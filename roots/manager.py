import sys

from werkzeug.serving import run_simple

from roots.command import Commands
from roots import default_commands


class Config(dict):
    '''A dictionary of configuration options. Allows access with attributes.'''

    def __setattr__(self, key, value):
        self[key] = value

    def __getattr__(self, key):
        return self[key]

    def use_object(self, obj):
        '''Use `obj` top level definitions as configuration.'''
        for name, value in obj.__dict__.items():
            if (not name.startswith("_")):
                self[name] = value


class Manager(object):
    '''
    A Manager object holds configuration options and handles the command line.
    It is a valid WSGI application, and can be wrapped with WSGI middleware.

    Typically, you would create an :py:class:`App` to use as a 'root' like so::

        from roots.app import App
        from roots.manager import Manager

        app = App('example')

        # <Define views here>

        if __name__ == '__main__':
            Manager(app).main()

    For more complicated projects, it is more likely you would be importing
    your :py:class:`App` from somewhere, and adding configuration::

        from roots.manager import Manager
        from example.project import app, config

        if __name__ == '__main__':
            manager = Manager(app)
            manager.config['example'] = ...
            manager.use_object_as_config(config)
            manger.main()

    :param root: Root :py:class:`App`.
    :param commands: Initial dictionary of commands.
    :param config: Initial configuration dictionary.

    '''
    def __init__(self, root, commands=None, config=None):
        self.root = root
        self.commands = Commands(commands or {})
        self.config = Config(config or {})

        self.commands.use_object(default_commands)

    def main(self):
        '''
        Handle command line input and run commands. If no command is specified,
        list them.

        Additional commands can be added to the :py:attr:`commands` dictionary
        and with :py:meth:`use_object`. Commands are typically defined with the
        :py:func:`command` decorator, but any object that has `command_name`
        and `command_help` attributes and is callable with a manager and a list
        of command line arguments can be a valid command.

        Commands defined with the :py:func:`command` decorator use
        :py:module:`argparse` and accept '-h' as a parameter to list their
        options.

        Commands defined in :py:module:`roots.default_commands` are added by
        default, which includes commands to run a webserver and list routes.

        '''
        # Print usage if no command specified
        if len(sys.argv) <= 1:
            self.commands.print_usage()
            return

        name = sys.argv[1]
        args = sys.argv[2:]

        try:
            command = self.commands[name]
        except KeyError:
            print "Invalid command: %s" % name
            self.commands.print_usage()
            return

        return command(self, args)

    def run(self, host="localhost", port=8000, reloader=False):
        '''Serve this :py:class:`Manager` using the Werkzeug server.'''
        run_simple(host, port, application=self, use_reloader=reloader)

    def __call__(self, environ, start_response):
        '''Make this Manager object behave like a WSGI application.'''
        return self.root.handle_wsgi_request(
            self.config, environ, start_response)
