# Roots

A thin wrapper around Werkzeug routing for creating reusable, composable apps.

## Features

### Add views to an app

    app = RootsApp('demoapp')

    @app.route("/<name>", name="example")
    def view(env, name):
        ...

### Reverse view names to URLs

    def otherview(env):
        example_url = env.reverse("example")
   
### Mount child apps

    from childapp import childapp
    parent = RootsApp('parentapp')
    parent.mount(childapp, "/child/")

### Management commands

    if __name__ == '__main__':
        manage(app)

Run a server with:

    python2 <app>.py run --host <host> --port <port> --reloader


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
