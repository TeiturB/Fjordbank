from heapq import heapify
import json
from symtable import Symbol

from cs50 import SQL
from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
)
import requests
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import main

from helpers import apology, login_required, lookup, dkk

# Configure application
main = Flask(__name__)

# Ensure templates are auto-reloaded
main.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
main.jinja_env.filters["dkk"] = dkk

# app.jinja_env.filters["dkk"] = dkk

# Configure session to use filesystem (instead of signed cookies)
main.config["SESSION_PERMANENT"] = False
main.config["SESSION_TYPE"] = "filesystem"
Session(main)

# Configure Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Declare header for Oracle APEX database
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "content-type": "application/json",
}


@main.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@main.route("/")
@login_required
def index():
    """Show welcome page"""
    # Get and declare variables
    p_number = session["p_number"]

    # customer_id = session["customer_id"]

    print(f"Session p_number: {p_number}")

    # Get account data from database
    url = f"https://apex.oracle.com/pls/apex/databasur/user/index/?p_number={p_number}"
    response = requests.get(url, headers=headers)

    print(response.status_code)

    if response.status_code == 200:

        json_content = json.loads(response.content)

        print(f"JSON content: {json_content['items']}")

        try:
            account_list = json.loads(json_content["items"][0]["json_data"])["accounts"]

            print(json.loads(json_content["items"][0]["json_data"])["customer_id"])

            print(f"List of user accounts: {account_list}")

            # If user has accounts
            if len(account_list) > 0:
                print("User has accounts!")

                first_name = json.loads(json_content["items"][0]["json_data"])["first_name"]

                return render_template(
                    "index.html", first_name=first_name, account_list=account_list
                )
        except:
            # If user does not have accounts
            print("User does not have accounts!")

            data = response.json()["items"][0]["json_data"]

            parsed_data = json.loads(data)
            first_name = parsed_data["first_name"]

            return render_template("index.html", first_name=first_name)

    else:
        flash("Database error!")
        return render_template("login.html")


@main.route("/accounts", methods=["GET", "POST"])
def accounts():
    """Show portfolio of accounts"""
    if request.method == "POST":
        print("TODO")

    else:
        return render_template("accounts.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    # Forget any p_number
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Retain form data to reduce UX irretability
        session["login_form_data"] = request.form
        form_data = session.pop("login_form_data")

        # Get variables from form
        p_number = request.form.get("p_number")
        password = request.form.get("password")

        # Ensure p_number is provided
        if not p_number:
            flash("P-number required")
            return render_template("login.html", form_data=form_data)

        # Ensure password is provided
        if not password:
            flash("Password required")
            return render_template("login.html", form_data=form_data)

        # Query database for p_number and hash
        response = requests.get(
            f"https://apex.oracle.com/pls/apex/databasur/user/login/?p_number={p_number}",
            headers=headers,
        )

        if response.status_code == 200:

            try:
                # Unpack person dict from json object
                data = response.json()["items"][0]
            except:
                flash("User does not exist")
                return render_template("login.html", form_data=form_data)

            print(f"Login GET data: {data}")
            print(f"len of login data: {len(data)}")

            # Ensure p_number exists and password is correct
            if not check_password_hash(data["hash"], request.form.get("password")):
                flash("Incorrect password")
                return render_template("login.html", form_data=form_data)

            session["p_number"] = p_number
            flash(f"Welcome back, {data['first_name']}!")

            return redirect("/")

        else:
            flash(response.reason)
            return render_template("login.html", form_data=form_data)

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        return render_template("login.html")


@main.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@main.route("/dashboard", methods=["GET", "POST"])
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
            f"https://apex.oracle.com/pls/apex/databasur/user/dashboard/?p_number={p_number}",
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


@main.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # GET country codes
    response = requests.get(
        f"https://apex.oracle.com/pls/apex/databasur/user/register/",
        headers=headers,
    )

    country_codes = response.json()['items']

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
        country_code = request.form.get("country_code")
        phone_number = request.form.get("phone_number")
        email = request.form.get("email")

        # Retain form data to reduce UX irretability
        session["register_form_data"] = request.form
        form_data = session.pop("register_form_data")

        # Ensure p_number is provided
        if not p_number:
            flash("P-number required")
            return render_template("register.html", form_data=form_data, country_codes=country_codes)

        # Ensure password is provided
        if not password:
            flash("Password required")
            return render_template("register.html", form_data=form_data, country_codes=country_codes)

        # Ensure confirmation is provided
        if not confirmation:
            flash("Confirm password")
            return render_template("register.html", form_data=form_data, country_codes=country_codes)

        # Ensure confirmation matches password
        if password != confirmation:
            flash("Passwords must match")
            return render_template("register.html", form_data=form_data, country_codes=country_codes)

        # Ensure first name is provided
        if not first_name:
            flash("First name required")
            return render_template("register.html", form_data=form_data, country_codes=country_codes)

        # Ensure last name is provided
        if not last_name:
            flash("Last name required")
            return render_template("register.html", form_data=form_data, country_codes=country_codes)

        # Ensure postal code is provided
        if not postal_code:
            flash("Postal code required")
            return render_template("register.html", form_data=form_data, country_codes=country_codes)

        # Ensure street name is provided
        if not street_name:
            flash("Street name required")
            return render_template("register.html", form_data=form_data, country_codes=country_codes)

        # Ensure street number is provided
        if not street_number:
            flash("Street number required")
            return render_template("register.html", form_data=form_data, country_codes=country_codes)
        
        # Ensure phone number is provided
        if not country_code:
            flash("Country code required")
            return render_template("register.html", form_data=form_data, country_codes=country_codes)

        # Ensure phone number is provided
        if not phone_number:
            flash("Phone number required")
            return render_template("register.html", form_data=form_data, country_codes=country_codes)

        # Ensure e-mail is provided
        if not email:
            flash("E-mail required")
            return render_template("register.html", form_data=form_data, country_codes=country_codes)

        # Encrypt and store hash of provided password
        hash = generate_password_hash(password)

        # Concatenate country code and phone number
        full_phone_number = f"+{country_code}{phone_number}"

        # Insert data into database
        url = "https://apex.oracle.com/pls/apex/databasur/user/register/"
        data = {
            "p_number": p_number,
            "hash": hash,
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "postal_code": postal_code,
            "street_name": street_name,
            "street_number": street_number,
            "phone_number": full_phone_number,
            "email": email,
            "address_id": None
        }
        response = requests.post(url, json=data, headers=headers)

        print(data)
        print(f"Response: {response}")

        if response.status_code == 201:
            session["p_number"] = p_number
            flash(f"Welcome, {first_name}!")

            return redirect("/")

        else:
            flash(response.reason)
            print("Error: ", response.reason)

            return render_template("register.html", form_data=form_data, country_codes=country_codes)

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        print(f"country_codes: {country_codes}")
        return render_template("register.html", country_codes=country_codes)


if __name__ == "__main__":
    main.run(host="127.0.0.1", port=8080, debug=True)
