import csv
import datetime
import subprocess
import urllib
import uuid
# import requests

from flask import redirect, render_template, session
from functools import wraps

# Renders simple apology message to the user
def apology(message, code=400):
    return render_template("apology.html", top=code, bottom=message), code


def login_required(f):
    # Decorator function for requiring login
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Checks whether the session variable that stores user information is empty if yes redirects to login page
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def custom_merge_sort(tuple_list):
    # sort by column no [5] date published
    # check whether there is more than one value in list to be sorted
    if len(tuple_list) > 1:
        # integer division discarding remainder
        midpoint = len(tuple_list) // 2
        # create two sub arrays around the midpoint
        left = tuple_list[:midpoint]
        right = tuple_list[midpoint:]
        # Call the sort on the right and left halves recursively
        custom_merge_sort(left)
        custom_merge_sort(right)
        # Set up indexes for left, right and main lists
        l, r, i = 0, 0, 0
        # Loop to iterate through all values in both split lists
        while l < len(left) and r < len(right):
            if left[l][5] >= right[r][5]:
                tuple_list[i] = left[l]
                l+=1
            else:
                tuple_list[i] = right[r]
                r+=1
            i+=1
        # Fill in all remaining values from left or right arrays
        while l < len(left):
            tuple_list[i] = left[l]
            l+=1
            i+=1
        while r < len(right):
            tuple_list[i] = right[r]
            r+=1
            i+=1