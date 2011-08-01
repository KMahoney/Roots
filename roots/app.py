from werkzeug.exceptions import HTTPException
from werkzeug.wrappers import Request
from werkzeug.routing import Rule, Map, Submount


class ReversableNameConflictError(Exception):
    pass


class RootsConfigError(Exception):
    pass


class ExtendableEnvironment(object):
    '''
    A composite, extendable environment.

    Constructed by the :class:`App` on each request and passed in to the view.
    This object defers to a chain of sub-environments; the sub environments
    included by default are the :class:`Request` object itself, a
    :class:`ConfigEnv` and a :class:`ReverseEnv`.

    '''
    def __init__(self):
        self._environments = []

    def extend_environment(self, env):
        '''
        Extend this environment with a sub-environment.

        The environment is appended to the end of the chain, and so has the
        least priority.

        '''
        self._environments.append(env)

    def __getattr__(self, key):
        for env in self._environments:
            try:
                return getattr(env, key)
            except AttributeError:
                pass
        raise AttributeError(key)

    def __repr__(self):
        chain = '->'.join(env.__class__.__name__ for env in self._environments)
        return 'Env(%s)' % chain


class ConfigEnv(object):
    '''
    Allow access to the configuration.
    This environment is included by default on every request.

    '''
    def __init__(self, config):
        self.config = config


class ReverseEnv(object):
    '''
    Provides the :meth:'reverse' method to construct URLs.
    This environment is included by default on every request.

    :param map_adapter: App routes bound to WSGI environment.

    '''
    def __init__(self, map_adapter):
        self._map_adapter = map_adapter

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


class App(object):
    '''
    A thin wrapper around Werkzeug routing for creating reusable, modular
    apps. Views can be added to an app with the `route` decorator.

    :param name:
        Optional name of application.

    '''
    def __init__(self, name=None):
        # `App` is a wrapper around `werkzeug.routing.Map`
        self._map = Map()

        # Keep a dictionary of name -> view lookups. This will be updated
        # whenever a new view is added or sub-app mounted.
        self._view_lookup = {}

        # The app name is used to give views a default lookup name.
        self.name = name

        # List of mounted sub apps.
        self.children = []

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

        See :class:`werkzeug.routing.Rule` for additional arguments.

        :note:
            The order in which you define your routes is important! The router
            will use the first match it finds.

        '''
        def _add_rule_decorator(fn):
            fn.reversable_with = name or self.default_name(fn)

            if fn.reversable_with in self._view_lookup:
                raise ReversableNameConflictError(fn.reversable_with)

            rule = Rule(path, endpoint=fn.reversable_with, **kwargs)
            self._map.add(rule)
            self._view_lookup[fn.reversable_with] = fn
            return fn

        return _add_rule_decorator

    def mount(self, app, path):
        '''Mount a child app under `path`.'''
        # Check for reversable name conflicts.
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

    def handle_wsgi_request(self, config, environ, start_response):
        # Bind the environment to the URL router.
        map_adapter = self._map.bind_to_environ(environ)

        # Lookup view.
        try:
            endpoint, kwargs = map_adapter.match()
        except HTTPException, e:
            return e(environ, start_response)

        view_fn = self._view_lookup[endpoint]

        # Create default environment.
        env = ExtendableEnvironment()
        env.extend_environment(Request(environ))
        env.extend_environment(ConfigEnv(config))
        env.extend_environment(ReverseEnv(map_adapter))

        # Call the view. This expects a valid WSGI app in response.
        response = view_fn(env, **kwargs)
        return response(environ, start_response)
