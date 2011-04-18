import sys
from functools import partial

from utils import para_to_col, colour, pad


def _global_commands(root):
    return sorted(set(cmd
                      for cls in set(app.__class__ for app in root.iter_apps())
                      for cmd in cls.commands
                      if cmd.scope in ['global', 'all']))


def _local_commands(app):
    return sorted(cmd
                  for cmd in app.commands
                  if cmd.scope in ['local', 'all'])


def _local_name(app, cmd):
    return "%s:%s" % (app.name, cmd.name)


def _local_commands_lookup(app, root):
    return dict((_local_name(app, cmd), partial(cmd, app, root))
                for cmd in _local_commands(app))


def _command_lookup(root):
    lookup = dict((cmd.name, partial(cmd, root, root))
                  for cmd in _global_commands(root))

    for app in root.iter_apps():
        if app.name:
            lookup.update(_local_commands_lookup(app, root))

    return lookup


def _print_cmd(cmd, name=None):
    doc = para_to_col(30, cmd.__doc__ or "-")
    print colour("1;32") + (name or cmd.name) + colour() + doc


def _list_local_commands(app):
    print colour("1") + pad(70, app.name + " ", "=") + colour()
    for cmd in _local_commands(app):
        _print_cmd(cmd, name=_local_name(app, cmd))


def _list_global_commands(root):
    print colour("1") + pad(70, "Global ", "=") + colour()
    for cmd in _global_commands(root):
        _print_cmd(cmd)


def _usage(root):
    print "Usage: %s <command> <arguments...>" % sys.argv[0]
    print

    _list_global_commands(root)

    for app in root.iter_apps():
        if app.name:
            _list_local_commands(app)


def manage(app):
    if len(sys.argv) > 1:
        commands = _command_lookup(app)
        name = sys.argv[1]
        prog = " ".join(sys.argv[:2])

        try:
            command = commands[name]
        except KeyError:
            print "Invalid command: %s" % name
            return

        command(prog, sys.argv[2:])
    else:
        _usage(app)
