import random
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


def custom_merge_sort(tuple_list, index):
    # check whether there is more than one value in list to be sorted
    if len(tuple_list) > 1:
        # integer division discarding remainder
        midpoint = len(tuple_list) // 2
        # create two sub arrays around the midpoint
        left = tuple_list[:midpoint]
        right = tuple_list[midpoint:]
        # Call the sort on the right and left halves recursively
        custom_merge_sort(left, index)
        custom_merge_sort(right, index)
        # Set up indexes for left, right and main lists
        l, r, i = 0, 0, 0
        # Loop to iterate through all values in both split lists
        while l < len(left) and r < len(right):
            if left[l][index] >= right[r][index]:
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

# Function for picking three random books out of a book tuple list
def pick_three(rows):
    # Check if less than 3 books in list
    if len(rows) < 3:
        return []
    # Creates a list with 3 book tuples randomly selected
    new_rows = random.sample(rows, 3)
    # Creates a list to pass to the jinja template and formats the book data fetched from the database to display it on bootstrap cards
    book_info1 = []
    for book in new_rows:
        book_temp = {
            "date_published" : book[5],
            "cover_art" : book[8],
        }
        book_temp["title"] = book[1]
        # Shortens the title to a maximum of 35 characters and adds ... to the end
        if len(book_temp["title"]) > 35:
            book_temp["title"] = book_temp["title"][0:36].rstrip() + "..."
        book_temp["synopsis"] = book[7]
        # Shortens the synopsis to a maximum of 199 characters and adds ... to the end
        if len(book_temp["synopsis"]) > 153:
            book_temp["synopsis"] = book_temp["synopsis"][0:154] + "..."
        elif len(book_temp["synopsis"]) <= 0:
            book_temp["synopsis"] = "No book description available :("
        book_info1.append(book_temp)
    return book_info1

class Book:
    def __init__(self, rows):
        self.title = rows[1]
        self.author_id = rows[2]
        self.publisher_id = rows[3]
        self.isbn = rows[0]
        self.pages = rows[4]
        self.date_published = rows[5]
        self.language = rows[6]
        self.synopsis = rows[7]
        self.cover_art = rows[8]
        self.location = rows[11]
        self.book_id = rows[14]
        # Check checkboxes separately for input
        liked = rows[10]
        if liked == 0:
            self.liked = 0
        else:
            self.liked = 1
        finished_reading = rows[9]
        if finished_reading == 0:
            self.finished_reading = 0
        else:
            self.finished_reading = 1
    
    def SetAuthor(self, author):
        self.author = author
        
    def SetPublisher(self, publisher):
        self.publisher = publisher

    def SetLocation(self, location):
        self.location = location
