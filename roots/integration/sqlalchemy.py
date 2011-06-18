'''
Optional SQLAlchemy integration for Roots.

'''
from roots.app import App
from roots.command import command


class SQLApp(App):
    '''
    App that provides management commands to create and reset SQLAlchemy
    tables.

    '''
    def __init__(self, metadata, *args, **kwargs):
        super(SQLApp, self).__init__(*args, **kwargs)
        self._metadata = metadata


def _all_metadata(root):
    return (app._metadata
            for app in root.app_iterator()
            if hasattr(app, '_metadata') and app._metadata)


@command(name="sql.create")
def sql_create(manager):
    '''Create SQLAlchemy tables.'''
    engine = manager.config['engine']
    for metadata in _all_metadata(manager.root):
        metadata.create_all(engine)


@command(name="sql.reset")
def sql_reset(manager):
    '''Drop and re-create SQLAlchemy tables.'''
    engine = manager.config['engine']
    for metadata in _all_metadata(manager.root):
        metadata.drop_all(engine)
        metadata.create_all(engine)
