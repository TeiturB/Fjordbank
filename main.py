import json

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
)
import requests
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import main

from helpers import login_required, dkk

# Configure application
main = Flask(__name__)

# Ensure templates are auto-reloaded
main.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
main.jinja_env.filters["dkk"] = dkk

# Configure session to use filesystem (instead of signed cookies)
main.config["SESSION_PERMANENT"] = False
main.config["SESSION_TYPE"] = "filesystem"
Session(main)

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


@main.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Handle welcome page"""
    if request.method == "GET":
        # Get and declare variables
        p_number = session["p_number"]

        print()
        print(f"Session p_number: {p_number}")

        # Get account data from database
        url = f"https://apex.oracle.com/pls/apex/databasur/user/index/?p_number={p_number}"
        response = requests.get(url, headers=headers)

        print(json.loads(response.content))

        if response.status_code == 200:

            response_data = json.loads(
                json.loads(response.content)["items"][0]["json_data"]
            )

            first_name = response_data["first_name"]
            try:
                middle_name = response_data["middle_name"]
            except:
                middle_name = False
            last_name = response_data["last_name"]
            full_name = (
                f"{first_name} {middle_name + ' ' if middle_name else ''}{last_name}"
            )
            print(f"Name: {full_name}")

            if response_data["customer_id"]:

                customer_id = response_data["customer_id"]
                session["customer_id"] = customer_id
                print(f"Customer_id: {customer_id}")

                account_list = response_data["accounts"]

                related_customers = response_data["related_customers"]

                total_balance = sum([account["balance"] for account in account_list])
                print(f"Total balance: {total_balance}")
                print()

                print(f"List of user accounts: {account_list}")
                print()

                # Declare lists for displaying tables of related customers
                r_full_name_list = []
                r_account_list_list = []
                r_total_balance_list = []

                # For each customer, append to the lists
                for i, related_customer in enumerate(related_customers):

                    l_first_name = related_customer["first_name"]
                    try:
                        l_middle_name = related_customer["middle_name"]
                    except:
                        l_middle_name = False
                    l_last_name = related_customer["last_name"]
                    l_full_name = f"{l_first_name} {l_middle_name + ' ' if l_middle_name else ''}{l_last_name}"
                    print(f"Related Customer #{i + 1}'s name: {l_full_name}")
                    print()

                    r_full_name_list.append(l_full_name)

                    l_account_list = related_customer["accounts"]

                    r_account_list_list.append(l_account_list)

                    total = 0
                    for account in l_account_list:
                        total += account["balance"]
                    print(f"{l_full_name}'s total balance: {total}")
                    print()

                    r_total_balance_list.append(total)

                    print(f"{l_full_name}'s accounts: {l_account_list}")
                    print()

                # Make a dictionary of all related customers' lists
                related_customers_dict = {
                    "full_names": r_full_name_list,
                    "account_lists": r_account_list_list,
                    "total_balances": r_total_balance_list,
                }

                if len(account_list) > 0:

                    print(f"{full_name} holds accounts!")
                    print()

                    return render_template(
                        "index.html",
                        full_name=full_name,
                        customer_id=customer_id,
                        account_list=account_list,
                        total_balance=total_balance,
                        related_customers=related_customers,
                        related_customers_dict=related_customers_dict,
                    )

                else:

                    print(f"{full_name} does not hold accounts!")
                    print()

                    return render_template(
                        "index.html",
                        full_name=full_name,
                        customer_id=customer_id,
                        total_balance=total_balance,
                        related_customers=related_customers,
                        related_customers_dict=related_customers_dict,
                    )

            else:
                flash(f"{first_name} is not a customer")
                return render_template("login.html")

    # If POST
    else:
        session["accountnum"] = request.form.get("accountnum")
        session["accountname"] = request.form.get("accountname")
        session["registration_number"] = request.form.get("registration_number")

        return redirect("/transactions")


@main.route("/accounts_and_loans", methods=["GET", "POST"])
def accounts_and_loans():
    if request.method == "POST":

        # Get p_number from session
        p_number = session["p_number"]

        # Get the account type and account name from the HTML form
        account_type = request.form["account_type"]
        account_name = request.form["accountname"]

        # Define the payload for the RESTful Service call
        payload = {
            "p_number": p_number,
            "account_type": account_type,
            "accountname": account_name,
        }

        # Make the RESTful Service call to the open_account procedure
        response = requests.post(
            "https://apex.oracle.com/pls/apex/databasur/user/accounts_and_loans/",
            json=payload,
            headers=headers,
        )

        # Check the response status code
        if response.status_code == 200:
            flash("Account created successfully")
            return render_template("accounts-and-loans.html")
        else:
            flash("Error creating account: {}".format(response.text))
            return render_template("accounts-and-loans.html")
    else:
        return render_template("accounts-and-loans.html")


@main.route("/account_settings", methods=["GET", "POST"])
def account_settings():
    """Show user account_settings"""
    # Get p_number from session
    p_number = session["p_number"]

    if request.method == "POST":

        first_name = request.form["first_name"]
        middle_name = request.form["middle_name"]
        last_name = request.form["last_name"]
        hash = generate_password_hash(request.form["hash"])
        email = request.form["email"]
        phone_number = request.form["phone_number"]
        street_name = request.form["street_name"]
        street_number = request.form["street_number"]
        postal_code = request.form["postal_code"]

        personinfo = {
            "p_number": p_number,
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "hash": hash,
            "email": email,
            "phone_number": phone_number,
            "street_name": street_name,
            "street_number": street_number,
            "postal_code": postal_code,
        }

        print()
        print(f"User account info changed: {personinfo}")
        print()

        response = requests.post(
            "https://apex.oracle.com/pls/apex/databasur/user/account_settings/",
            json=personinfo,
            headers=headers,
        )

        # Check the response status code
        if response.status_code == 200:
            flash("Account settings changed successfully")
            return render_template("account-settings.html")
        else:
            flash("Error changing settings: {}".format(response.text))
            return render_template("account-settings.html")

    else:
        response = requests.get(
            f"https://apex.oracle.com/pls/apex/databasur/user/account_settings/?p_number={p_number}",
            headers=headers,
        )

        # Extract the values of the fields you want to show in the input boxes
        response_data = json.loads(response.content)

        if "items" in response_data and len(response_data["items"]) > 0:
            response_data = response_data["items"][0]

            first_name = response_data["first_name"]
            try:
                middle_name = response_data["middle_name"]
            except:
                middle_name = False
            last_name = response_data["last_name"]
            email = response_data["email"]
            phone_number = response_data["phone_number"]
            street_name = response_data["street_name"]
            street_number = response_data["street_number"]
            postal_code = response_data["postal_code"]
            return render_template(
                "account-settings.html",
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                street_name=street_name,
                street_number=street_number,
                postal_code=postal_code,
            )

        return render_template("account-settings.html")


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


@main.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # GET country codes
    response = requests.get(
        f"https://apex.oracle.com/pls/apex/databasur/user/register/",
        headers=headers,
    )

    country_codes = response.json()["items"]

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
            return render_template(
                "register.html", form_data=form_data, country_codes=country_codes
            )

        # Ensure password is provided
        if not password:
            flash("Password required")
            return render_template(
                "register.html", form_data=form_data, country_codes=country_codes
            )

        # Ensure confirmation is provided
        if not confirmation:
            flash("Confirm password")
            return render_template(
                "register.html", form_data=form_data, country_codes=country_codes
            )

        # Ensure confirmation matches password
        if password != confirmation:
            flash("Passwords must match")
            return render_template(
                "register.html", form_data=form_data, country_codes=country_codes
            )

        # Ensure first name is provided
        if not first_name:
            flash("First name required")
            return render_template(
                "register.html", form_data=form_data, country_codes=country_codes
            )

        # Ensure last name is provided
        if not last_name:
            flash("Last name required")
            return render_template(
                "register.html", form_data=form_data, country_codes=country_codes
            )

        # Ensure postal code is provided
        if not postal_code:
            flash("Postal code required")
            return render_template(
                "register.html", form_data=form_data, country_codes=country_codes
            )

        # Ensure street name is provided
        if not street_name:
            flash("Street name required")
            return render_template(
                "register.html", form_data=form_data, country_codes=country_codes
            )

        # Ensure street number is provided
        if not street_number:
            flash("Street number required")
            return render_template(
                "register.html", form_data=form_data, country_codes=country_codes
            )

        # Ensure phone number is provided
        if not country_code:
            flash("Country code required")
            return render_template(
                "register.html", form_data=form_data, country_codes=country_codes
            )

        # Ensure phone number is provided
        if not phone_number:
            flash("Phone number required")
            return render_template(
                "register.html", form_data=form_data, country_codes=country_codes
            )

        # Ensure e-mail is provided
        if not email:
            flash("E-mail required")
            return render_template(
                "register.html", form_data=form_data, country_codes=country_codes
            )

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
            "address_id": None,
        }
        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 201:
            session["p_number"] = p_number
            flash(f"Welcome, {first_name}!")

            return redirect("/")

        else:
            flash(response.reason)

            print()
            print("Error: ", response.reason)
            print()

            return render_template(
                "register.html", form_data=form_data, country_codes=country_codes
            )

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        return render_template("register.html", country_codes=country_codes)


@main.route("/transactions", methods=["GET"])
def transactions():
    """Display account transactions"""
    accountnum = session["accountnum"]
    accountname = session["accountname"]
    registration_number = session["registration_number"]

    print()
    print(f"Account name: {accountname}")
    print(f"Account number: {accountnum}")
    print()

    # HTTP GET transactions
    response_transactions = requests.get(
        f"https://apex.oracle.com/pls/apex/databasur/user/transactions/?account={accountnum}",
        headers=headers,
    )

    # HTTP GET future transactions
    response_f_transactions = requests.get(
        f"https://apex.oracle.com/pls/apex/databasur/user/future_transactions/?account={accountnum}",
        headers=headers,
    )

    if (
        response_transactions.status_code == 200
        and response_f_transactions.status_code == 200
    ):

        transaction_list = json.loads(response_transactions.content)["items"]

        f_transaction_list = json.loads(response_f_transactions.content)["items"]

        return render_template(
            "transactions.html",
            accountnum=accountnum,
            accountname=accountname,
            registration_number=registration_number,
            transaction_list=transaction_list,
            f_transaction_list=f_transaction_list,
        )

    else:
        flash(
            "Error while fetching transaction list: {}".format(
                response_transactions.reason
            )
        )


@main.route("/payments", methods=["GET", "POST"])
def payments():

    customer_id = session["customer_id"]

    url = f"https://apex.oracle.com/pls/apex/databasur/user/payments/?customer_id={customer_id}"
    response = requests.get(url, headers=headers)

    account_list = json.loads(response.content)["items"]

    if request.method == "POST":

        payment_method = request.form.get("payment_method")

        if payment_method == "deposit":

            to_account = request.form.get("to_account")
            amount = request.form.get("amount")
            message_text = request.form.get("message_text")
            own_text = request.form.get("own_text")
            cashier_id = request.form.get("cashier_id")
            due_date = request.form.get("due_date")

            payload = {
                "to_account": to_account,
                "amount": amount,
                "message_text": message_text,
                "own_text": own_text,
                "cashier_id": cashier_id,
                "due_date": due_date,
            }

        elif payment_method == "transfer":

            from_account = request.form.get("from_account")
            to_account = request.form.get("to_account")
            amount = request.form.get("amount")
            message_text = request.form.get("message_text")
            own_text = request.form.get("own_text")
            due_date = request.form.get("due_date")

            payload = {
                "from_account": from_account,
                "to_account": to_account,
                "amount": amount,
                "message_text": message_text,
                "own_text": own_text,
                "due_date": due_date,
            }

        elif payment_method == "withdrawal":

            from_account = request.form.get("from_account")
            amount = request.form.get("amount")
            message_text = request.form.get("message_text")
            own_text = request.form.get("own_text")
            cashier_id = request.form.get("cashier_id")
            due_date = request.form.get("due_date")

            payload = {
                "from_account": from_account,
                "amount": amount,
                "message_text": message_text,
                "own_text": own_text,
                "cashier_id": cashier_id,
                "due_date": due_date,
            }

        # Make the RESTful Service call to the appropriate procedure
        response = requests.post(
            f"https://apex.oracle.com/pls/apex/databasur/user/{payment_method}/",
            json=payload,
            headers=headers,
        )

        print()
        print(f"Status: {response.status_code}")
        print()

        # Check the response status code
        if response.status_code != 200:
            flash(f"Error occurred while performing {payment_method}")
            return render_template("payments.html", account_list=account_list)

        flash(f"Your {payment_method} was successful")
        return render_template("payments.html", account_list=account_list)

    # If GET method
    else:

        return render_template("payments.html", account_list=account_list)


@main.route("/portal", methods=["GET", "POST"])
def portal():
    """Endpoint to retrieve and display employee information"""
    if request.method == "GET":
        p_number = session["p_number"]
        employee_id = session["employee_id"]
        
        print("TODO")

        return render_template("portal.html")


    else: #POST
        print("TODO")


@main.route("/portal_account_management")
def portal_account_management():
    if request.method == "GET":

        return render_template("portal_account_management.html")

    else: # if POST
        print("TODO")


@main.route("/portal_customer_relations")
def portal_customer_relations():
    if request.method == "GET":
        
        return render_template("portal_customer_relations.html")

    else: # if POST
        print("TODO")


@main.route("/portal_customer_search")
def portal_customer_search():
    if request.method == "GET":
        
        return render_template("portal_customer_search.html")

    else: # if POST
        print("TODO")


@main.route("/portal-login", methods=["GET", "POST"])
def portal_login():
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
            return render_template("portal-login.html", form_data=form_data)

        # Ensure password is provided
        if not password:
            flash("Password required")
            return render_template("portal-login.html", form_data=form_data)

        # Query database for p_number and hash
        response = requests.get(
            f"https://apex.oracle.com/pls/apex/databasur/portal/login/?p_number={p_number}",
            headers=headers
        )

        print(f"YOOOOOOOOO: {json.loads(response.content)}")

        if response.status_code == 200:

            try:
                # Unpack person dict from json object
                data = response.json()["items"][0]
            except:
                flash("User does not exist")
                return render_template("portal-login.html", form_data=form_data)

            # Ensure p_number exists and password is correct
            if not check_password_hash(data["hash"], request.form.get("password")):
                flash("Incorrect password")
                return render_template("portal-login.html", form_data=form_data)

            try:
                employee_id = data["employee_id"]
                session["employee_id"] = employee_id
            except:
                flash("User is not an employee at FjordBank")
                return render_template("portal-login.html", form_data=form_data)

            print()
            print(f"P-number: {p_number}")
            print(f"Employee ID: {employee_id}")
            print()

            session["p_number"] = p_number
            flash(f"Get to work, {data['first_name']}!")

            return redirect("/portal")

        else:
            flash(response.reason)
            return render_template("portal-login.html", form_data=form_data)

    # User reached route via GET (as by clicking a link or via redirect)
    else:

        return render_template("portal-login.html")
    

@main.route("/portal_logout")
def portal_logout():
    """Log employee out"""
    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/portal-login")


if __name__ == "__main__":
    main.run(host="127.0.0.1", port=8080, debug=True)
