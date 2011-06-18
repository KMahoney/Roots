import sys
from operator import attrgetter

from roots.utils.ansi import para_to_col, colour
from roots.command import _valid_command
from roots import default_commands


class Manager(object):
    '''
    A Manager object holds configuration options and handles the command line.

    :param root: Root :py:class:`App`.

    '''
    def __init__(self, root, commands=None, config=None):
        self._commands = commands or {}

        self.root = root
        self.config = config or {}

        self.use_object_commands(default_commands)

    def add_command(self, command):
        '''Add a command to the manager.'''
        assert _valid_command(command.__name__, command)
        self._commands[command.command_name] = command

    def use_object_commands(self, obj):
        '''Scan `obj` for commands and add them to the manager.'''
        for name, value in obj.__dict__.items():
            if _valid_command(name, value):
                self._commands[value.command_name] = value

    def use_object_as_config(self, obj):
        '''Use `obj` top level definitions as configuration.'''
        for name, value in obj.__dict__.items():
            if (not name.startswith("_")):
                self.config[name] = value

    @property
    def command_list(self):
        '''List of commands in alphabetical order.'''
        return sorted(self._commands.values(), key=attrgetter('command_name'))

    def usage(self):
        '''List commands.'''
        for command in self.command_list:
            doc = para_to_col(30, command.command_help or "-")
            print colour("1;32") + command.command_name + colour() + doc

    def main(self):
        '''Handle command line input and run commands.'''
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
