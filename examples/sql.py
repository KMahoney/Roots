from werkzeug.wrappers import Response
from sqlalchemy import create_engine, MetaData, Table, Column, Integer

from roots.manager import Manager
from roots.integration import sqlalchemy as roots_alchemy

metadata = MetaData()

test = Table('access',
             metadata,
             Column('id', Integer, primary_key=True))

sqlapp = roots_alchemy.SQLApp(metadata, 'sqlapp')


def _execute(env, *args, **kwargs):
    return env.config['engine'].execute(*args, **kwargs)


@sqlapp.route("/")
def add(env):
    _execute(env, test.insert())
    ul = "<ul>"
    for n in _execute(env, test.select()):
        ul += "<li>%s</li>" % n.id
    ul += "</ul>"
    return Response(ul, mimetype='text/html')


if __name__ == '__main__':
    manager = Manager(root=sqlapp)
    manager.config['engine'] = create_engine('sqlite:///test.db', echo=True)
    manager.use_object_commands(roots_alchemy)
    manager.main()

# To run:

# python2 example2.py sql.create
# python2 example2.py run
