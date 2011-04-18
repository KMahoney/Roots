import sys
import re

from utils import para_to_col, colour, pad

ACTION_REGEXP = r"^action_(.*)$"


# Actions

def _app_actions(app, qualified=False):
    '''
    Retreive a list of bound methods matching ACTION_REGEXP in `app`.
    Prepend app name if `qualified`.
    '''
    actions = []
    cls = app.__class__

    while cls != object:
        for key, value in cls.__dict__.items():
            match = re.match(ACTION_REGEXP, key)
            if match:
                if qualified and app.name:
                    action_name = "%s:%s" % (app.name, match.group(1))
                else:
                    action_name = match.group(1)
                action_fn = value.__get__(app)
                actions.append((action_name, action_fn))
        cls = cls.__base__

    return actions


def _sub_apps(app):
    '''Flatten app children into a single list'''
    apps = []

    def _rec_find(app):
        for child in app.children:
            apps.append(child)
            _rec_find(child)

    _rec_find(app)
    return apps


def _action_lookup(app):
    '''A dictionary mapping command names to functions.'''
    actions = dict(_app_actions(app))
    actions.update(dict(_app_actions(app, qualified=True)))
    for sub in _sub_apps(app):
        actions.update(dict(_app_actions(sub, qualified=True)))
    return actions


# Script

def _list_all():
    return len(sys.argv) > 1 and sys.argv[1] == 'all'


def _action_info(action, fn):
    doc = para_to_col(30, fn.__doc__ or "-")
    print colour("1;32") + action + colour() + doc


def _list_actions(app, qualified=False):
    name = app.name or "Actions"
    print colour("1") + pad(70, name + " ", "=") + colour()
    print
    for action, fn in _app_actions(app, qualified=qualified):
        _action_info(action, fn)
    print


def _usage(app):
    print "Usage: %s <action> <arguments...>" % sys.argv[0]
    print "Give -h as an argument to an action to show its usage."
    print "Use 'all' as an action to show all child app actions."
    print

    _list_actions(app, qualified=False)

    if _list_all():
        for sub in _sub_apps(app):
            _list_actions(sub, qualified=True)


def manage(app):
    if len(sys.argv) > 1 and not _list_all():
        actions = _action_lookup(app)
        name = sys.argv[1]
        prog = " ".join(sys.argv[:2])

        try:
            action = actions[name]
        except KeyError:
            print "Invalid action: %s" % name
            return

        action(app, prog, sys.argv[2:])
    else:
        _usage(app)
