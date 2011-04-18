'''Optional SQLAlchemy integration for Roots.'''

import argparse

from roots.app import RootsApp, RootsConfigError


def _engine(app):
    try:
        return app.config['engine']
    except KeyError:
        name = app.name or "the root app"
        raise RootsConfigError(
            "No SQL engine has been configured for %s." % name)


class SQLRootsApp(RootsApp):
    '''
    App that provides management commands to create and reset SQLAlchemy
    tables.
    '''

    def __init__(self, metadata, *args, **kwargs):
        super(SQLRootsApp, self).__init__(*args, **kwargs)
        self._metadata = metadata

    def action_sql_create(self, root, prog, args):
        '''Create SQLAlchemy tables.'''
        parser = argparse.ArgumentParser(prog=prog)
        args = parser.parse_args(args)

        engine = _engine(root)
        if self._metadata:
            self._metadata.create_all(engine)

    def action_sql_reset(self, root, prog, args):
        '''Drop and re-create SQLAlchemy tables.'''
        parser = argparse.ArgumentParser(prog=prog)
        args = parser.parse_args(args)

        engine = _engine(root)
        if self._metadata:
            self._metadata.drop_all(engine)
            self._metadata.create_all(engine)
