from roots.command import command
from roots.utils.ansi import to_col, colour


@command()
def run(manager, host="localhost", port=8000, reloader=False):
    '''Run a webserver.'''
    manager.run(host, port, reloader)


@command()
def routes(manager):
    '''List all routes for this app.'''
    for rule in manager.root._map.iter_rules():
        print (colour("1;32") + rule.endpoint + colour() +
               to_col(40) + rule.rule)
