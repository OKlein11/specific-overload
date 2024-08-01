import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from overload.db import get_db

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register",methods=("GET","POST"))
def register():
    if request.method == "POST": # If this is a request to register a user, get username and password from request
        username = request.form["username"]
        password = request.form["password"] 
        db = get_db()
        error = None

        if not username: # If either value is not included, throw an error
            error = "Username is required."
        elif not password:
            error = "Password is required."

        if error is None: #If there's no error
            try:
                db.execute(
                    "INSERT INTO user (username,password) VALUES (?,?)",
                    (username,generate_password_hash(password),)
                )
                db.commit()
            
            except db.IntegrityError:
                error = f"User {username} is already registered."

            else:
                return redirect(url_for("auth.login"))
            
        flash(error)
    
    return render_template("auth/register.html")


@bp.route("/login",methods=("GET","POST")) # Method used to login
def login():
    if request.method == "POST": # if you are attempting to send a login request
        username = request.form["username"]
        password = request.form["password"] 
        db = get_db()
        error = None

        user = db.execute("SELECT * FROM user WHERE username = ?",(username,)).fetchone() # find the user with the entered username

        if user is None: # check for errors
            error = "Incorrect username."
        
        elif not check_password_hash(user["password"], password):
            error = "Incorrect password."
        
        if error is None:
            session.clear() # If your are somehow already logged in, log out
            session["user_id"] = user["id"] # save teh userid
            return redirect(url_for("index")) #redirect to home page

        flash(error)

    return render_template("auth/login.html") # if not sending a login request, render the login page

@bp.before_app_request # Load the logged in user before pages load
def load_logged_in_user():
    user_id = session.get("user_id") #Get the id

    if user_id is None: # If not logged in, pass basically
        g.user = None
    
    else: # If you're logged in, get your user data
        g.user = get_db().execute(
            "SELECT * FROM user WHERE id = ?", (user_id,)
        ).fetchone()

@bp.route("/logout")
def logout(): # Simple method to logout and redirect home
    session.clear()
    return redirect(url_for("index"))

def login_required(view): # This is a wrapper function that I only partially get, but basically if you give something this decorator
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))
        
        return view(**kwargs)
    
    return wrapped_view