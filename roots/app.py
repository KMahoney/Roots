import argparse

from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Request
from werkzeug.routing import Rule, Map, Submount
from werkzeug.serving import run_simple

from roots.utils.ansi import to_col, colour


class ReversableNameConflictError(Exception):
    pass


class RootsConfigError(Exception):
    pass


class RootsEnvironment(object):
    '''
    An object constructed by the :py:class:`App` on each request and passed in
    to the view.

    :attribute root: Currently running root app.
    :attribute request: Current :py:class:`Request` object.

    '''
    def __init__(self, root, map_adapter, request):
        self._map_adapter = map_adapter

        self.root = root
        self.request = request

    def reverse(self, reversable, **kwargs):
        '''
        Construct a URL.

        :param reversable:
            A string, or an object with a `reversable_with` property.

        Additional keyword arugments will be passed into the URL builder to
        construct the URL.

        '''
        if hasattr(reversable, 'reversable_with'):
            return self._map_adapter.build(reversable.reversable_with, kwargs)

        return self._map_adapter.build(reversable, kwargs)

    @property
    def config(self):
        return self.root.config


class App(object):
    '''
    A thin wrapper around Werkzeug routing for creating reusable, modular
    apps. Views can be added to an app with the `route` decorator.

    :param name:
        Optional name of application.
    :param environment:
        Class to use to construct the object passed through to views on each
        request.

    '''
    commands = []

    def __init__(self, name=None, config=None, environment=RootsEnvironment):
        self._map = Map()
        self._view_lookup = {}
        self._environment = environment

        self.name = name
        self.children = []
        self.config = config or {}

    @classmethod
    def command(cls, scope='local', name=None):
        '''
        Add a command to this class. `scope` should be 'global' when applicable
        to all apps, and 'local' when applicable only to the current app.
        '''
        def _add_command(fn):
            fn.scope = scope
            fn.name = name or fn.__name__

            # create a copy of the superclass commands list if needed
            if 'commands' not in cls.__dict__:
                cls.commands = list(cls.commands)

            cls.commands.append(fn)
            return fn
        return _add_command

    def default_name(self, fn):
        ''':returns: default reverse name for `fn`.'''
        if self.name:
            return "%s:%s" % (self.name, fn.__name__)
        return fn.__name__

    def route(self, path, name=None, **kwargs):
        '''
        Decorator to add a view to this app. The view function should take an
        environment as its first paramter and any additional keyword parameters
        defined in the `path`.

        :param path: The URL for this view. All named parameters should be
            reflected as keyword parameters in the view function.
        :param name:
            A string used to reverse to this view. Default:
            'appname:functionname'.

        See :py:class:`werkzeug.routing.Rule` for additional arguments.

        '''
        def _add_rule(fn):
            fn.reversable_with = name or self.default_name(fn)

            if fn.reversable_with in self._view_lookup:
                raise ReversableNameConflictError(fn.reversable_with)

            rule = Rule(path, endpoint=fn.reversable_with, **kwargs)
            self._map.add(rule)
            self._view_lookup[fn.reversable_with] = fn
            return fn

        return _add_rule

    def mount(self, app, path):
        '''Mount a child app under `path`.'''
        # check for reversable name conflicts
        for key in app._view_lookup.keys():
            if key in self._view_lookup:
                raise ReversableNameConflictError(key)

        self._map.add(Submount(path, app._map._rules))
        self._view_lookup.update(app._view_lookup)
        self.children.append(app)

    def app_iterator(self):
        '''Iterate over all apps in tree order.'''
        yield self
        for child in self.children:
            for app in child.app_iterator():
                yield app

    def __call__(self, environ, start_response):
        map_adapter = self._map.bind_to_environ(environ)

        try:
            endpoint, kwargs = map_adapter.match()
        except HTTPException, e:
            return e(environ, start_response)

        view_fn = self._view_lookup[endpoint]
        request = Request(environ)
        env = self._environment(self, map_adapter, request)
        response = view_fn(env, **kwargs)
        return response(environ, start_response)


@App.command(scope='all')
def run(app, root, prog, args):
    '''Run a webserver with this app's routes.'''
    parser = argparse.ArgumentParser(prog=prog)
    parser.add_argument('--host', default='localhost')
    parser.add_argument('--port', type=int, default=8000)
    parser.add_argument('--reloader', action='store_true')
    args = parser.parse_args(args)
    run_simple(args.host,
               args.port,
               application=app,
               use_reloader=args.reloader)


@App.command(scope='all')
def routes(app, root, prog, args):
    '''List all routes for this app.'''
    parser = argparse.ArgumentParser(prog=prog)
    args = parser.parse_args(args)

    for rule in app._map.iter_rules():
        print (colour("1;32") + rule.endpoint + colour() +
               to_col(40) + rule.rule)
