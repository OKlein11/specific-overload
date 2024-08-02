import sqlite3

import click
from flask import current_app,g
from werkzeug.security import generate_password_hash

def get_db():
    if "db" not in g: # g is a object unique to each request, this basically means that for each request, the function only fetches the db once, after taht it uses the existing connection
        g.db= sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None): # This function is a cleanup function that will be called while flask is cleaning up after a request
    db = g.pop("db",None)

    if db is not None:
        db.close()

def init_db(): # This function will be called once during deployment to initialize the db
    db = get_db()

    with current_app.open_resource("schema.sql") as f: # Using the schema file, create the db
        db.executescript(f.read().decode("utf8"))

@click.command("init-db") # This creates a CLI command for initializing the db
def init_db_command():
    init_db()
    click.echo("Initialized the Db")

def init_app(app): # This is a function run as the app is created to perform some helping functions
    app.teardown_appcontext(close_db) # This makes close_db run after requests during cleanup
    app.cli.add_command(init_db_command) # This makes it so you can call a new coomand within the flask command
    app.cli.add_command(generate_superuser_command)


def create_user(username, password, authority):
    db = get_db()
    error = None
    try:
        db.execute(
            "INSERT INTO user (username,password,authority) VALUES (?,?,?)",
            (username,generate_password_hash(password),authority,)
                )
        db.commit()
            
    except db.IntegrityError:
        error = f"User {username} is already registered."
    
    return error

def generate_superuser(username,password):
    if not username:
        return "Username required."
    if not password:
        return "Password required."
    error = create_user(username,password,10)
    if not error is None:
        return error
    return f"User {username} created."

@click.command("generate-superuser")
@click.argument("username")
@click.argument("password")
def generate_superuser_command(username, password):
    result = generate_superuser(username,password)
    click.echo(result)