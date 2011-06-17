from roots.app import App
from roots.sqlalchemy import SQLApp
from roots.manage import manage
from werkzeug.wrappers import Response

from sqlalchemy import create_engine, MetaData, Table, Column, Integer

metadata = MetaData()

test = Table('access', metadata,
             Column('id', Integer, primary_key=True))

# SQL app

sqlapp = SQLApp(metadata, 'sqlapp')


# View

def execute(env, *args, **kwargs):
    return env.config['engine'].execute(*args, **kwargs)


@sqlapp.route("/")
def add(env):
    execute(env, test.insert())
    ul = "<ul>"
    for n in execute(env, test.select()):
        ul += "<li>%s</li>" % n.id
    ul += "</ul>"
    return Response(ul, mimetype='text/html')


# Root app
# Must contain engine configuration

engine = create_engine('sqlite:///test.db', echo=True)
root = App('root', config={'engine': engine})
root.mount(sqlapp, '/')


# management script
if __name__ == '__main__':
    manage(root)

# To run:

# python2 example2.py sql_create_all
# python2 example2.py run
