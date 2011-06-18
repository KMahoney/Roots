import sys
import argparse
import inspect
from functools import wraps
from operator import attrgetter

from roots.utils.ansi import para_to_col, colour


def _function_arg_parser(fn, ignore=[], arguments={}):
    '''
    Inspect a function's arguments and create an :py:mod:`argparse` parser.

    '''
    parser = argparse.ArgumentParser(description=fn.__doc__)
    spec = inspect.getargspec(fn)
    defaults = dict(zip(reversed(spec.args or []),
                        reversed(spec.defaults or [])))
    args = (arg for arg in spec.args if arg not in ignore)

    # Construct an option for each function argument that hasn't been ignored
    for arg in args:
        default = defaults.get(arg)

        arg_params = {
            'default': default,
            'required': arg not in defaults,
            }

        # Try to determine option behaviour by looking at the argument's
        # default value.
        if type(default) == bool:
            arg_params.update({
                    'action': 'store_const',
                    'const': (not default),
                    })
        elif type(default) == list:
            arg_params.update({'action': 'append'})

        if arg in arguments:
            arg_params.update(arguments[arg])

        parser.add_argument("--" + arg, **arg_params)

    return parser


def command(name=None, help=None, arguments={}):
    '''
    Create a new :py:class:`Manager` command.

    The function should take an argument named `manager`, which is the
    :py:class:`Manager` used to invoke the command. Remaining arguments
    will be automatically converted to a :py:mod:`argparse` parser.

    :param name:
        The name of the command. Default: function name.
    :param help:
        Help to display in usage information. Default: function docstring.
    :param arguments:
        A dictionary mapping function arguments to parameters used in
        :py:meth:`ArgumentParser.add_argument`.

    '''
    def _decorator(fn):
        parser = _function_arg_parser(
            fn, ignore=["manager"], arguments=arguments)

        @wraps(fn)
        def _command(manager, cmd_args):
            namespace = parser.parse_args(cmd_args)
            return fn(manager, **vars(namespace))

        _command.command_name = name or fn.__name__
        _command.command_help = help or fn.__doc__
        parser.prog = _command.command_name
        return _command
    return _decorator


def _valid_command(name, value):
    return ((not name.startswith("_")) and
            callable(value) and
            hasattr(value, "command_name") and
            hasattr(value, "command_help"))


class Manager(object):
    '''
    A Manager object holds configuration options and handles the command line.

    :param root: Root :py:class:`App`.

    '''
    def __init__(self, root, commands=None, config=None):
        self._commands = commands or {}

        self.root = root
        self.config = config or {}

        # Avoid circular import for `command` decorator by importing here.
        from roots import default_commands
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
