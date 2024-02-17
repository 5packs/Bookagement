import csv
import datetime
import subprocess
import urllib
import uuid
# import requests

from flask import redirect, render_template, session
from functools import wraps


def apology(message, code=400):
    return render_template("apology.html", top=code, bottom=message), code


def login_required(f):
    # Decorator function for requiring login
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function