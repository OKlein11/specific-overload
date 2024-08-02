import os

from flask import Flask

def create_app(test_config=None):
    # This Function creates and configures the agg
    app = Flask(__name__,instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=os.path.join(app.instance_path,"specific_overload.sqlite")
    ) # always load the dev config

    if test_config is None:
        # load the config from the config file for production
        app.config.from_pyfile("config.py", silent=True) # Load config from config.py, will pass if file DNE

    else:
        app.config.from_mapping(test_config) # If there is a test config, load it

    try:
        os.makedirs(app.instance_path) # makes sure the instance folder for the app exists

    except OSError:
        pass # pass if the path aleady exists

    @app.route("/hello")
    def hello(): # A simple routing to a hello world, note to self, add exlosions and sound effects to this page
        return "Hello World"

    from . import db
    db.init_app(app)
    
    from . import auth
    app.register_blueprint(auth.bp)

    from . import blog
    app.register_blueprint(blog.bp)
    app.add_url_rule("/",endpoint="index")

    return app

