import locale

from flask import redirect, session
from functools import wraps


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("p_number") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# def dkk(value):
#     """Format value as DKK."""
#     locale.setlocale(locale.LC_ALL, 'da_DK.UTF-8')
#     return f"{locale.format_string('%.2f', value, grouping=True):>10}"


# Another way to achieve similar results
def dkk(value):
    return f"{value:,.2f}".replace(",", ";").replace(".", ",").replace(";", ".")


# Deprecated. Saved as a potential 404 screen in the future
# def apology(message, code=400):
#     """Render message as an apology to user."""
#     def escape(s):
#         """
#         Escape special characters.

#         https://github.com/jacebrowning/memegen#special-characters
#         """
#         for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
#                          ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
#             s = s.replace(old, new)
#         return s
#     return render_template("apology.html", top=code, bottom=escape(message)), code