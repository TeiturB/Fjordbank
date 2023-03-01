import json
import requests
from flask import Flask, render_template, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import main

# Configure application
app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Declare header for Oracle APEX database
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
    "content-type": "application/json"
}

@app.route("/")
def index():
    return "Welcome to my app!"

@app.route("/register/", methods=["GET", "POST"])
def register():
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
            return render_template("register.html", error="P-number required")

        # Ensure password was provided
        if not password:
            return render_template("register.html", error="Password required")

        # Ensure confirmation was provided
        if not confirmation:
            return render_template("register.html", error="Confirm password")

        # Ensure confirmation matches password
        if password != confirmation:
            return render_template("register.html", error="Passwords must match")

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
            "email": email,
        }

        # Make a POST request to insert data into Oracle APEX database
        response = requests.post(
            "https://apex.oracle.com/pls/apex/databasur/user/register/",
            json=data,
            headers=headers
        )

        # Print the response status code
        print(response.status_code)

        # Check if the POST request was successful
        if response.status_code == 201:
            return render_template("success.html")
        else:
            # Print the response content
            print(response.content)
            return render_template("register.html", error="An error occurred while registering user.")
    else:
        return render_template("register.html")

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080, debug=True)
