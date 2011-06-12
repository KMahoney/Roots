# Roots

A lightweight abstraction around Werkzeug for creating reusable pieces of web application code.
Similar in concept to Django apps.


## Why?! Hasn't this been done a million times already?

Mostly for fun. If somebody actually finds it useful, that's a bonus.

Check out Bottle and Flask too.


## Project Goals

- Hot explicit Python action.
- Flexible: does not mandate conventions.
- Layered abstractions: decide how much you want to use.
- Well documented code
- Batteries: completely optional extended functionality included with the source.
- Small and understandable: Werkzeug takes care of the hard parts.


## Features

### Apps

- Add views to an app

        from roots.app import RootsApp
        from werkzeug.wrappers import Response

        demoapp = RootsApp('demoapp')

        @app.route("/<name>")
        def hello(env, name):
            return Response("Hello %s" % name)

- Reverse view names to URLs

        @app.route("/other/")
        def other(env):
            example_url = env.reverse("demoapp:hello", name="Joe")
            ...

- Mount child apps

        parent = RootsApp('parentapp')
        parent.mount(demoapp, "/child/")

### Management

- Command line invocation

        from roots.manage import manage

        if __name__ == '__main__':
            manage(root=demoapp)

    Run a server with:

        $ python2 app.py run --host <host> --port <port> --reloader

- Define new commands

        from roots.manage import manage, command

        @command()
        def hello(name="Joe"):
            '''Say hello!'''
            print "Hello %s!" % name

        if __name__ == '__main__':
            manage(root=demoapp, commands=[hello])

    Results in:

        $ python2 app.py hello you
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
