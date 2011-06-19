'''
Optional SQLAlchemy integration for Roots.

'''
from roots.app import App, RootsEnvironment
from roots.command import command


class SQLEnvironment(RootsEnvironment):
    '''Environment with some SQLAlchemy helpers.'''

    @property
    def engine(self):
        return self.config.engine

    def execute(self, *args, **kwargs):
        return self.engine.execute(*args, **kwargs)


class SQLApp(App):
    '''
    App that provides management commands to create and reset SQLAlchemy
    tables. SQLApp provides a :class:`SQLEnvironment` to its views.

    '''
    def __init__(self, metadata, *args, **kwargs):
        super(SQLApp, self).__init__(*args, **kwargs)
        self._metadata = metadata

    def make_environment(self, *args, **kwargs):
        return SQLEnvironment(*args, **kwargs)


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
