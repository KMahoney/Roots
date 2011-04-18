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


def _empty_parser(prog, args):
    parser = argparse.ArgumentParser(prog=prog)
    return parser.parse_args(args)


def _all_metadata(root):
    return (app._metadata
            for app in root.iter_apps()
            if hasattr(app, '_metadata') and app._metadata)


@SQLRootsApp.command(scope='global')
def sql_create_all(app, root, prog, args):
    '''Create SQLAlchemy tables.'''
    _empty_parser(prog, args)
    engine = _engine(root)
    for metadata in _all_metadata(root):
        metadata.create_all(engine)


@SQLRootsApp.command(scope='local')
def sql_create(app, root, prog, args):
    '''Create SQLAlchemy tables.'''
    _empty_parser(prog, args)
    engine = _engine(root)
    app._metadata.create_all(engine)


@SQLRootsApp.command(scope='global')
def sql_reset_all(app, root, prog, args):
    '''Drop and re-create SQLAlchemy tables for this app.'''
    _empty_parser(prog, args)
    engine = _engine(root)
    for metadata in _all_metadata(root):
        metadata.drop_all(engine)
        metadata.create_all(engine)


@SQLRootsApp.command(scope='local')
def sql_reset(app, root, prog, args):
    '''Drop and re-create SQLAlchemy tables for this app.'''
    _empty_parser(prog, args)
    engine = _engine(root)
    app._metadata.drop_all(engine)
    app._metadata.create_all(engine)
