# Roots

A lightweight abstraction around Werkzeug for creating modular, reusable pieces
of web application code. Similar in concept to Django apps.


## Why?! Hasn't this been done a million times already?

Mostly for fun. If somebody actually finds it useful, that's a bonus.

Check out Bottle and Flask too.

### Some differences between Roots and Bottle/Flask

- Roots is in an early stage of development and has unstable interfaces.
- Roots has explicit semantics where practical.
  Flask, for example, uses context locals where Roots passes through an 'environment' parameter explicitly.
- Roots provides command line management for your projects.
- Roots separates out the configuration (Manager) from the collections of routes (App).
- Roots has an emphasis on mounting sub-apps for modularity, although this is certainly possible in Bottle and Flask too. Flask has 'Module' objects.


## Project Goals

- Hot explicit Python action.
- Modular.
- Configurable.
- Flexible.
- Well documented code.
- Batteries: completely optional extended functionality included.
  - Optional integration with Jinja2, SQLAlchemy, and more.
- Small and comprehensible.


## Features

### Apps

- Add views to an app

        from roots.app import App
        from werkzeug.wrappers import Response

        demoapp = App('demoapp')

        @app.route("/<name>")
        def hello(env, name):
            return Response("Hello %s" % name)

- Reverse view names to URLs

        @app.route("/other/")
        def other(env):
            example_url = env.reverse("demoapp:hello", name="Joe")
            ...

- Mount child apps

        parent = App('parentapp')
        parent.mount(demoapp, "/child/")

### Managers

- Command line invocation

        from roots.manager import Manager

        if __name__ == '__main__':
            Manager(root=demoapp).main()

    Run a server with:

        $ python2 app.py run --host <host> --port <port> --reloader

- Extend command line functionality

        from roots.manager import Manager
        from roots.integration import sqlalchemy

        if __name__ == '__main__':
            manager = Manager(root=demoapp)
            manager.commands.use_object(sqlalchemy)
            manager.main()

- Define new commands

        from roots.manager import Manager
        from roots.command import command

        @command()
        def hello(manager, name="Joe"):
            '''Say hello!'''
            print "Hello %s!" % name

        if __name__ == '__main__':
            manager = Manager(root=demoapp)
            manager.commands.add(hello)
            manager.main()

    Results in:

        $ python2 app.py hello --name you
        Hello you!


## TODO

- SQLAlchemy helpers.
  - Associate metadata with apps.
  - Table creation/deletion management commands.
- Jinja2 helpers.
- Tutorials and API documentation.
- User authentication app, using SQLAlchemy.


## License

Copyright 2011 Kevin Mahoney.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
