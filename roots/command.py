import argparse
import inspect
from functools import wraps


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
