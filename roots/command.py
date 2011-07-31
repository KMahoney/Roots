import argparse
import inspect
from operator import attrgetter
from functools import wraps

from roots.utils.ansi import para_to_col, colour


def _function_arg_parser(fn, ignore=[], arguments={}):
    '''
    Inspect a function's arguments and create an :mod:`argparse` parser.

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
    Create a new :class:`Manager` command.

    The function should take an argument named `manager`, which is the
    :class:`Manager` used to invoke the command. Remaining arguments
    will be automatically converted to a :mod:`argparse` parser.

    :param name:
        The name of the command. Default: function name.
    :param help:
        Help to display in usage information. Default: function docstring.
    :param arguments:
        A dictionary mapping function arguments to parameters used in
        :meth:`ArgumentParser.add_argument`.

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


def _find_object_commands(obj):
    '''Find valid commands in `obj`.'''
    return dict((value.command_name or name, value)
                for name, value in obj.__dict__.items()
                if _valid_command(name, value))


class Commands(dict):
    '''A dictionary of command-line commands.'''

    def use_object(self, obj):
        '''Add all valid commands found in `obj`.'''
        self.update(_find_object_commands(obj))

    def as_list(self):
        ''':returns: A list of commands in alphabetical order.'''
        return sorted(self.values(), key=attrgetter('command_name'))

    def print_usage(self):
        '''Print a list of commands to standard output.'''
        for command in self.as_list():
            doc = para_to_col(30, command.command_help or "-")
            print colour("1;32") + command.command_name + colour() + doc

    def add(self, command):
        '''Add a new command.'''
        assert _valid_command(command.command_name, command)
        self[command.command_name] = command
