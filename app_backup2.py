from heapq import heapify
import json
import os
import re
from symtable import Symbol

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
import requests
import json
from flask_session import Session
from tempfile import mkdtemp
import hashlib
from werkzeug.security import check_password_hash, generate_password_hash
import datetime

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Declare header for Oracle APEX database
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "content-type": "application/json"
}

# Make sure API key is set
# if not os.environ.get("API_KEY"):
#     raise RuntimeError("API_KEY not set")


@app.route("/accounts", methods=["GET", "POST"])
def accounts():
    """Show portfolio of accounts"""
    if request.method == "POST":
        boom = 123

    else:
        return render_template("accounts.html")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # Get and declare variables
    user_id = session["user_id"]

    # p_number = session["p_number"]

    print(user_id)

    transactions_db = db.execute(
        "SELECT symbol, SUM(shares) AS shares, price FROM transactions WHERE user_id = ? GROUP BY symbol",
        user_id,
    )
    cash_db = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    cash = cash_db[0]["cash"]

    # Get name from database
    username_list = db.execute("SELECT username FROM users WHERE id = ?", user_id)
    username_dict = username_list[0]

    # Calculate total portfolio value
    total = cash
    for i in range(0, len(transactions_db)):
        total = total + (transactions_db[i]["shares"] * transactions_db[i]["price"])

    return render_template(
        "index.html",
        database=transactions_db,
        cash=cash,
        total=total,
        username=username_dict["username"],
    )


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any p_number
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get variables from form
        p_number = request.form.get("p_number")
        password = request.form.get("password")

        print(p_number)
        print(password)

        # Ensure p_number was submitted
        if not p_number:
            return apology("P-number required", 403)

        # Ensure password was submitted
        elif not password:
            return apology("Password required", 403)

        # Query database for p_number and hash
        response = requests.get(
            f"https://apex.oracle.com/pls/apex/databasur/user/login?p_number={p_number}",
            headers=headers,
        )

        # Ensure p_number exists and password is correct
        # if len(rows) != 1 or not check_password_hash(
        #     rows[0]["hash"], request.form.get("password")
        # ):
        #     return apology("ógyldugt brúkaranavn og/ella loyniorð", 403)

        # Remember which user has logged in
        # session["p_number"] =

        # rows = db.execute(
        #     "SELECT * FROM users WHERE username = ?", request.form.get("p_number")
        # )

        if response.status_code == 200:

            # Unpack person dict from json object
            db_person = response.json()["items"][0]

            # Ensure p_number exists and password is correct
            if len(db_person) != 1 or not check_password_hash(
                db_person["hash"], request.form.get("password")
            ):
                return apology("Invalid p-number and/or password", 403)

            session["p_number"] = db_person["p_number"]

            # Redirect user to home page
            return redirect("/")

        else:

            # return an error message if the request failed
            return f"Something went wrong: {response.text}"

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


@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    """Show user dashboard"""
    if request.method == "POST":

        print("POST")

    else:

        # get the query parameter from the request URL
        # query = request.args.get("bloop")

        # namee = ":bloop"

        # print(f"Query: {query}")

        p_number = "010188121"

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }

        # make an HTTP GET request to the RESTful web service URL with the query parameter
        response = requests.get(
            f"https://apex.oracle.com/pls/apex/databasur/user/dashboard?p_number={p_number}",
            headers=headers,
        )

        print(f"Response: {response}")
        # print(f"JSON response: {response.json()}")

        # check if the request was successful
        if response.status_code == 200:

            # get the JSON data from the response
            data = response.json()

            print(data)

            # return a formatted string with some data fields
            return f"The result for query is: {data}"
        # return render_template("dashboard.html")

        else:

            # return an error message if the request failed
            return f"Something went wrong: {response.text}"


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Assign variables
        p_number = request.form.get("p_number")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        first_name = request.form.get("first_name")
        middle_name = request.form.get("middle_name")
        last_name = request.form.get("last_name")
        postal_code = request.form.get("postal_code")
        street_name = request.form.get("street_name")
        street_number = request.form.get("street_number")
        phone_number = request.form.get("phone_number")
        email = request.form.get("email")

        # Ensure p_number was provided
        if not p_number:
            return apology("P-number required", 403)

        # Ensure password was provided
        if not password:
            return apology("Password required", 403)

        # Ensure confirmation was provided
        if not confirmation:
            return apology("Confirm password", 403)

        # Ensure confirmation matches password
        if password != confirmation:
            return apology("Passwords must be the same", 403)

        # Encrypt and store hash of provided password
        hash = generate_password_hash(password)

        data = {
            "p_number": p_number,
            "hash": hash,
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "postal_code": postal_code,
            "street_name": street_name,
            "street_number": street_number,
            "phone_number": phone_number,
            "email": email
        }

        print(data)

        test = {
            "ID": "5",
            "word": "hey"
        }
        
        response = requests.post(f"https://apex.oracle.com/pls/apex/databasur/user/test/", json=json.dumps(test))

        # try:

        # Insert into database
        # response = requests.post(
        #     "https://apex.oracle.com/pls/apex/databasur/user/register/", json=json.dumps(data), timeout=60
        # )
        # print(response.status_code)
        # print(response.content)

        # requests.post(
        #     "https://apex.oracle.com/pls/apex/databasur/user/register/", json=query
        # )

        if response.status_code == 200:
            flash("OH YEAH!")
            print("yo")
        else:
            print("fokk")
            flash("åh neeeii")

        # new_user = db.execute(
        #     "INSERT INTO users (username, hash) VALUES (?, ?)", p_number, hash
        # )
        # except:
            # return apology("brúkaranavn er tikið", 403)

        session["user_id"] = p_number

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

    return apology("TODO")


# @app.route("/buy", methods=["GET", "POST"])
# @login_required
# def buy():
#     """Buy shares of stock"""

#     if request.method == "POST":

#         # Declare variables
#         symbol = request.form.get("symbol")
#         shares = int(request.form.get("shares"))

#         # Error handling
#         if not symbol:
#             return apology("symbol manglar", 403) # The 403 (Forbidden) status code indicates that the server understood the request but refuses to authorize it

#         # Lookup quote
#         stock = lookup(symbol.upper())
#         # return jsonify(stock)

#         # Error handling
#         if stock == None:
#             return apology("symbol er ikki til", 403)
#         if shares < 0:
#             return apology("nøgd má verða positiv", 403)
#         if shares > 1000000000000000: # Defense against integer overflow
#             return apology("tú sleppur ikki at bróta síðuna", 403)
#         if not shares:
#             return apology("vel nøgd", 403)

#         # Store price of selected stocks
#         transaction_value = shares * stock["price"]

#         # Get user's cash amount from db and store in variable
#         user_id = session["user_id"]
#         user_cash_db = db.execute("SELECT cash FROM users WHERE id = :id", id=user_id)
#         user_cash = user_cash_db[0]["cash"]
#         # return jsonify(user_cash_db)

#         # Check if user can afford transaction
#         if user_cash < transaction_value:
#             return apology("tú ert ov fátækur", 403)

#         # Calculate new user cash total and update databases
#         updt_cash = user_cash - transaction_value
#         db.execute("UPDATE users SET cash = ? WHERE id = ?", updt_cash, user_id)

#         date = datetime.datetime.now()
#         # return jsonify(date)
#         db.execute("INSERT INTO transactions (user_id, symbol, shares, price, date) VALUES (?, ?, ?, ?, ?)", user_id, stock["symbol"], shares, stock["price"], date)

#         flash("Keypt!")

#         return redirect("/")

#     else:
#         return render_template("/buy.html")


# @app.route("/history")
# @login_required
# def history():
#     """Show history of transactions"""
#     user_id = session["user_id"]
#     transactions_db = db.execute("SELECT * FROM transactions WHERE user_id = :id", id=user_id)
#     return render_template("history.html", transactions = transactions_db)


# @app.route("/quote", methods=["GET", "POST"])
# @login_required
# def quote():
#     """Get stock quote."""

#     if request.method == "POST":

#         # Define variables
#         symbol = request.form.get("symbol")

#         # Error handling
#         if not symbol:
#             return apology("Symbol manglar", 403)

#         # Lookup quote
#         stock = lookup(symbol.upper())

#         # Error handling
#         if stock == None:
#             return apology("Symbol er ikki til", 403)

#         # Render quoted
#         return render_template("/quoted.html", name = stock["name"], price = stock["price"], symbol = stock["symbol"])

#     else:
#         return render_template("/quote.html")


# @app.route("/sell", methods=["GET", "POST"])
# @login_required
# def sell():
#     """Sell shares of stock"""

#     if request.method == "POST":

#         # Declare variables
#         symbol = request.form.get("symbol")
#         shares = int(request.form.get("shares"))

#         # Error handling
#         if not symbol:
#             return apology("symbol manglar", 403)

#         # Lookup quote
#         stock = lookup(symbol.upper())

#         # Error handling
#         if stock == None:
#             return apology("symbol er ikki til", 403)

#         # Error handling
#         if shares < 0:
#             return apology("nøgd má verða positiv", 403)
#         if shares > 1000000000000000:
#             return apology("Tú sleppur ikki at bróta síðuna", 403)
#         if not shares:
#             return apology("vel nøgd", 403)

#         # Store price of selected stocks
#         transaction_value = shares * stock["price"]

#         # Get user's cash amount from db and store in variable
#         user_id = session["user_id"]
#         user_cash_db = db.execute("SELECT cash FROM users WHERE id = :id", id=user_id)
#         user_cash = user_cash_db[0]["cash"]

#         # Error handling
#         user_shares_db = db.execute("SELECT SUM(shares) AS shares FROM transactions WHERE user_id=:id AND symbol = :symbol", id=user_id, symbol=symbol)
#         user_shares = user_shares_db[0]["shares"]
#         if shares > user_shares:
#             return apology("tú hevur ikki so nógv virðisbrøv av hasum slagnum", 403)

#         # Calculate new user cash total and update databases
#         updt_cash = user_cash + transaction_value
#         db.execute("UPDATE users SET cash = ? WHERE id = ?", updt_cash, user_id)

#         date = datetime.datetime.now()
#         # return jsonify(date)
#         db.execute("INSERT INTO transactions (user_id, symbol, shares, price, date) VALUES (?, ?, ?, ?, ?)", user_id, stock["symbol"], (-1) * shares, stock["price"], date)

#         flash("Selt!")

#         return redirect("/")

#     else:
#         user_id = session["user_id"]

#         # Get the user's shares only
#         user_symbols = db.execute("SELECT symbol FROM transactions WHERE user_id = :id GROUP BY symbol HAVING SUM(shares) > 0", id=user_id)
#         return render_template("sell.html", symbols = [row["symbol"] for row in user_symbols])
