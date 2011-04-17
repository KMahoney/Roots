import sys
import re

ACTION_REGEXP = r"^action_(.*)$"


# ANSI bling

def _to_col(n):
    return "\033[%sG\033[K" % n


def _colour(n=""):
    return "\033[%sm" % n


def _para_to_col(n, string):
    return _to_col(n) + string.replace("\n", "\n" + _to_col(n))


def _pad(n, string, fill):
    count = n - min(len(string), n)
    return string + (count * fill)


# Actions

def _app_actions(app):
    actions = []
    app_dict = app.__class__.__dict__

    for key, value in app_dict.items():
        match = re.match(ACTION_REGEXP, key)
        if match:
            actions.append((match.group(1), value.__get__(app)))

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


def _sub_actions(app):
    return [("%s:%s" % (app.name, action), fn)
            for (action, fn) in _app_actions(app)]


def _all_subapp_actions(app):
    return [(sub, _sub_actions(sub)) for sub in _sub_apps(app) if sub.name]


def _action_dict(app):
    actions = dict(_app_actions(app))
    for _, child_actions in _all_subapp_actions(app):
        actions.update(dict(child_actions))
    return actions


def _action_info(action, fn):
    doc = _para_to_col(30, fn.__doc__)
    print _colour("1;32") + action + _colour() + doc


# Script

def _list_all():
    return len(sys.argv) > 1 and sys.argv[1] == 'all'


def _usage(app):
    print
    print "Usage: %s <action> <arguments...>" % sys.argv[0]
    print "Give -h as an argument to an action to show its usage."
    print "Use 'all' as an action to show all child app actions."

    name = app.name or "Actions"
    print
    print _colour("1") + _pad(70, name + " ", "=") + _colour()
    print

    for action, fn in _app_actions(app):
        _action_info(action, fn)

    print

    if _list_all():
        for child, actions in _all_subapp_actions(app):
            print _colour("1") + _pad(70, child.name + " ", "=") + _colour()
            print
            for action, fn in actions:
                _action_info(action, fn)
            print


def manage(app):
    if len(sys.argv) > 1 and not _list_all():
        actions = _action_dict(app)
        name = sys.argv[1]
        prog = " ".join(sys.argv[:2])
        try:
            action = actions[name]
            action(prog, sys.argv[2:])
        except KeyError:
            print "Invalid action: %s" % name
    else:
        _usage(app)
