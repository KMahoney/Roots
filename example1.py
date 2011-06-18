from roots.app import App
from roots.manager import Manager
from werkzeug.wrappers import Response


def html(content):
    return Response(content, mimetype='text/html')


# The app name is optional
child_app = App('childapp')

# `route` can be passed a name, but by default the view is called
# 'appname:functionname', or just the function name if the app
# hasn't been named.


# This view is called 'childapp:childview':
@child_app.route("/<test>")
def childview(env, test):
    parent_url = env.reverse('parentapp:parentview')
    text = env.config['text']
    return html("<h1>child view</h1>"
                "<p>argument %s</p>"
                "<p>config text: %s</p>"
                "<a href=\"%s\">parent_app</a>"
                % (test, text, parent_url))


# Normally this would be in a different Python module.
parent_app = App(
    'parentapp',
    config={'text': 'example config'})


# This view is called 'parentapp:parentview':
@parent_app.route("/")
def parentview(env):
    # You can also reverse using the function itself.
    child_url = env.reverse(childview, test=123)
    return html("<h1>parent view</h1>"
                "<a href=\"%s\">child_app</a>"
                % child_url)


# Mount the child app inside the parent app.
# Note that the parent_app is the app passed through to all the
# views, including child_app views.
parent_app.mount(child_app, "/child/")

# management script
if __name__ == '__main__':
    Manager(parent_app).main()
