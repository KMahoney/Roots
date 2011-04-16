from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Request
from werkzeug.routing import Rule, Map, Submount
from werkzeug.serving import run_simple


class RootsEnvironment(object):
    '''
    An object passed in to each view with the current request's
    environment. Contains the running RootsApp `app` and the current `request`.
    '''

    def __init__(self, app, map_adapter, request):
        self._map_adapter = map_adapter

        self.app = app
        self.request = request

    def reverse(self, reversable, **kwargs):
        '''Construct a URL for `name`.'''

        if hasattr(reversable, 'reversable_with'):
            return self._map_adapter.build(reversable.reversable_with, kwargs)

        return self._map_adapter.build(reversable, kwargs)

    @property
    def config(self):
        return self.app.config


class ReversableNameConflictError(Exception):
    pass


class RootsApp(object):
    '''
    A thin wrapper around Werkzeug routing for creating reusable, composable
    apps. Views can be added to an app with the `route` decorator.

    `name`
    Optional name of application.

    `config`
    Dictionary passed through to views.

    `env_class`
    Class to use to construct the object passed through to views on each
    request.
    '''

    def __init__(self, name=None, config=None, env_class=RootsEnvironment):
        self._map = Map()
        self._view_lookup = {}
        self._env_class = env_class

        self.name = name
        self.children = []
        self.config = config or {}

    def default_name(self, fn):
        if self.name:
            return "%s:%s" % (self.name, fn.__name__)
        return fn.__name__

    def route(self, path, name=None, **kwargs):
        '''
        Decorator to add a view to this app. Optionally pass in a view
        `name` the app can `reverse` on.  By default the name will be
        'app_name:function_name'.  The view should take at least one
        parameter as well as any parameters defined in the URL.
        See `werkzeug.routing.Rule` for additional arguments.
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

    def run(self, *args, **kwargs):
        '''
        Run a webserver with this app's routes.
        See `werkzeug.serving.run_simple` for additional arguments. The most
        useful is probably `use_reloader` which, when true, detects changes in
        your code and reloads.
        '''
        run_simple(*args, application=self, **kwargs)

    def __call__(self, environ, start_response):
        map_adapter = self._map.bind_to_environ(environ)

        try:
            endpoint, kwargs = map_adapter.match()
        except HTTPException, e:
            return e(environ, start_response)

        view_fn = self._view_lookup[endpoint]
        request = Request(environ)
        env = self._env_class(self, map_adapter, request)
        response = view_fn(env, **kwargs)
        return response(environ, start_response)
