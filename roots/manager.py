import sys
from operator import attrgetter

from roots.utils.ansi import para_to_col, colour
from roots.command import find_object_commands
from roots import default_commands


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
        self._commands = commands or {}

        self.root = root
        self.config = config or {}

        self.use_object_commands(default_commands)

    def add_command(self, command):
        '''Add a command to the manager.'''
        self._commands[command.command_name] = command

    def use_object_commands(self, obj):
        '''Scan `obj` for commands and add them to the manager.'''
        self._commands.update(find_object_commands(obj))

    def use_object_as_config(self, obj):
        '''Use `obj` top level definitions as configuration.'''
        for name, value in obj.__dict__.items():
            if (not name.startswith("_")):
                self.config[name] = value

    @property
    def command_list(self):
        ''':returns: A list of commands in alphabetical order.'''
        return sorted(self._commands.values(), key=attrgetter('command_name'))

    def usage(self):
        '''Print a list of commands to standard output.'''
        for command in self.command_list:
            doc = para_to_col(30, command.command_help or "-")
            print colour("1;32") + command.command_name + colour() + doc

    def main(self):
        '''
        Handle command line input and run commands.

        Additional commands can be added with :py:meth:`add_command` and
        :py:meth:`use_object_commands`. Commands are typically defined with the
        :py:func:`command` decorator, but any object that has `command_name`
        and `command_help` attributes and is callable with a manager and a list
        of command line arguments can be a valid command.

        Commands defined with the :py:func:`command` decorator use
        :py:module:`argparse` and accept '-h' as a parameter to list their
        options.

        Commands defined in :py:module:`roots.default_commands` are added by
        default, which includes commands to run a webserver and list routes.

        '''
        if len(sys.argv) <= 1:
            self.usage()
            return

        name = sys.argv[1]
        args = sys.argv[2:]

        try:
            command = self._commands[name]
        except KeyError:
            print "Invalid command: %s" % name
            self.usage()
            return

        return command(self, args)

    def __call__(self, environ, start_response):
        '''Handle WSGI call.'''
        return self.root.wsgi_request(self.config, environ, start_response)
