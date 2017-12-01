from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
# TODO
db = SQL("sqlite:///bergbuddies.db")


@app.route("/")
def index():
    """Show home page"""
    return render_template("layout.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # check that all fields are filled
        if not request.form.get("name"):
            return apology("must provide name")
        if not request.form.get("username"):
            return apology("must provide username")

        if not request.form.get("password"):
            return apology("must provide password")
        # check that confirmation is entered
        if not request.form.get("confirmation"):
            return apology("must provide confirmation")
        # check that password matches confirmation
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("confirmation must match password")

        # remember hashed form of password
        hashPass = generate_password_hash(request.form.get("password"))

        # input new user info into table users
        result = db.execute("INSERT INTO users (name, username, hash) VALUES (:name, :username, :hashPass)",
                            name=request.form.get("name"), username=request.form.get("username"), hashPass=hashPass)

        # usernames are a unique field in users, return error if username already exists (execute will fail)
        if not result:
            return apology("username already taken")

        # store user_id in session (to keep user logged in)
        session["user_id"] = result

        return redirect("/")
    else: # if get method
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


def errorhandler(e):
    """Handle error"""
    # dunno how to do this or what this is for
    return None


# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)