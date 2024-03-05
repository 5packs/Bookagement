from flask import Flask, render_template, redirect, request, session, g, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import requests as req
import hashlib
from helpers import apology, login_required, custom_merge_sort

h = {'Authorization': '51841_15f8a1a6b75e8c37b224c61dca5164e7'}

# Start application
app = Flask(__name__)

# Set session to use filesystem (instead of cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database global variable path
DATABASE = "C:\\Users\\Spacks\\Documents\\Bookagement\\test.db"

# Get the global database variable if available
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# Function for closing a database connection
# TODO: add close connection to all the places where it opens the database???
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
@login_required
def index():
    #TODO: add the ability to display recent books and other homepage things
    # Sets up connection to the database
    db = get_db().cursor()
    # Query the database for the most recent added or edited unread books
    fetched = db.execute("SELECT * FROM books WHERE finished_reading = (?)", ("0",))
    rows = fetched.fetchall()
    # If there is less than 3 unread books in the library instead redirect user to the add book page
    # TODO: Maybe make the whole div disappear instead from the main page and instead show a big text add more books to get started
    if len(rows) < 3:
        return redirect("/add")
    # Creates a list to pass to the jinja template and formats the book data fetched from the database to display it on bootstrap cards
    book_info = []
    for book in rows:
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
        if len(book_temp["synopsis"]) > 159:
            book_temp["synopsis"] = book_temp["synopsis"][0:160] + "..."
        elif len(book_temp["synopsis"]) <= 0:
            book_temp["synopsis"] = "No book description available :("
        book_info.append(book_temp)
        if len(book_info) >= 3:
            break;
    return render_template("index.html", book_info=book_info)

@app.route('/register', methods=['GET', 'POST'])
def register():
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Connect to database in this context
        con = get_db()
        db = con.cursor()
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)
        # Ensure passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must be the same", 400)
        # Query database for username
        fetched = db.execute("SELECT * FROM users WHERE username = (?)", (request.form.get("username"),))
        taken = fetched.fetchall()
        # Ensure username doesn't exist
        if len(taken) == 1:
            return apology("username taken", 400)
        # Add user to database
        with con:
            db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", (request.form.get("username"), generate_password_hash(request.form.get("password"))))
        # Redirect user to home page
        return redirect("/login")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

@app.route('/login', methods=["GET", "POST"])
def login():
    # Forget any user_id
    session.clear()
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Connect to database in this context
        db = get_db().cursor()
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        # Query database for username
        fetched = db.execute("SELECT * FROM users WHERE username = ?", (request.form.get("username"),))
        rows = fetched.fetchall()
        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0][2], request.form.get("password")):
            return apology("invalid username and/or password", 403)
        # Remember which user has logged in
        session["user_id"] = rows[0][0]
        # Redirect user to home page
        return redirect("/")
    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route('/search', methods=['POST', 'GET'])
@login_required
def search():
    #TODO: actually make a search routine that searches using authors and publishers and aggregate sql
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get user input
        search_query = request.form.get("inputsearch").title()
        # Connect to database in this context
        db = get_db().cursor()
        # Query database for matching books
        fetched = db.execute(f"SELECT * FROM books WHERE title LIKE ? AND user_id = ?", (f"{search_query}%", session.get("user_id")))
        rows = fetched.fetchall()
        # Sorts all the books to be displayed using a custom written merge sort based on release date [5] period in tuple of book results
        custom_merge_sort(rows)
        return render_template("results.html", books=rows)
    return render_template("search.html")

@app.route('/view', methods=['POST'])
@login_required
def view():
    # Checks which book was clicked on the search page
    current_book = request.form.get("bookisbn")
    # Sets up connection to the database
    db = get_db().cursor()
    # Query the database for the book
    fetched = db.execute("SELECT * FROM books WHERE isbn = ?", (current_book,))
    rows = fetched.fetchall()
    if len(rows) > 1:
        return apology("Your search query was not specific enough")
    # Fetch author publisher and location name using the hashed id
    author_query = db.execute("SELECT * FROM authors WHERE author_id = ?", (rows[0][2],))
    author_name = author_query.fetchall()[0][1]
    publisher_query = db.execute("SELECT * FROM publishers WHERE publisher_id = ?", (rows[0][3],))
    publisher_name = publisher_query.fetchall()[0][1]
    location_query = db.execute("SELECT * FROM locations WHERE location_id = ?", (rows[0][11],))
    location_name = location_query.fetchall()[0][1]
    # Create a book value dictionary out of the values returned from the search query in the database
    book_info = {
        "title" : rows[0][1],
        "author" : author_name,
        "publisher": publisher_name,
        "isbn" : rows[0][0],
        "pages" : rows[0][4],
        "date_published" : rows[0][5],
        "language" : rows[0][6],
        "synopsis": rows[0][7],
        "cover_art" : rows[0][8],
        "location" : location_name
    }
    # Check checkboxes separately for input
    liked = rows[0][10]
    if liked == 0:
        book_info["liked"] = "No"
    else:
        book_info["liked"] = "Yes"
    finished_reading = rows[0][9]
    if finished_reading == 0:
        book_info["finished_reading"] = "No"
    else:
        book_info["finished_reading"] = "Yes"
    return render_template("view.html", book_info=book_info)

@app.route('/edit', methods=['POST'])
@login_required
def edit():
    # Connect to database in this context
    con = get_db()
    db = con.cursor()
    # Gets the book details from database using the ISBN number passed in form
    fetched = db.execute("SELECT * FROM books WHERE isbn = ?", (request.form.get("isbn"),))
    rows = fetched.fetchall()[0]
    # Create a book value dictionary out of the values returned from the search query in the database
    book_info = {}
    book_info["title"] = rows[1]
    book_info["author_id"] = rows[2]
    book_info["publisher_id"] = rows[3]
    book_info["isbn"] = rows[0]
    book_info["pages"] = rows[4]
    book_info["date_published"] = rows[5]
    book_info["language"] = rows[6]
    book_info["synopsis"] = rows[7]
    book_info["cover_art"] = rows[8]
    book_info["location"] = rows[11]
    # Check checkboxes separately for input
    liked = rows[10]
    if liked == 0:
        book_info["liked"] = 0
    else:
        book_info["liked"] = 1
    finished_reading = rows[9]
    if finished_reading == 0:
        book_info["finished_reading"] = 0
    else:
        book_info["finished_reading"] = 1
    # Fetch author and publisher name using the hashed id and add them to the dictionary
    author_query = db.execute("SELECT * FROM authors WHERE author_id = ?", (book_info["author_id"],))
    author_name = author_query.fetchall()[0][1]
    publisher_query = db.execute("SELECT * FROM publishers WHERE publisher_id = ?", (book_info["publisher_id"],))
    publisher_name = publisher_query.fetchall()[0][1]
    location_query = db.execute("SELECT * FROM locations WHERE location_id = ?", (book_info["location"],))
    location_name = location_query.fetchall()[0][1]
    book_info["author"] = author_name
    book_info["publisher"] = publisher_name
    book_info["location"] = location_name
    return render_template("edit.html", book_info=book_info)

@app.route('/save', methods=['POST'])
@login_required
def save():
    # Connect to database in this context
    con = get_db()
    db = con.cursor()
    # Hash the author name string using SHA1 to generate the author_id which is the primary key in the authors table
    hashed_author_name = hashlib.sha1(request.form.get("author").encode())
    # Hash the publisher name string using SHA1 to generate the publisher_id which is the primary key in the publishers table
    hashed_publisher_name = hashlib.sha1(request.form.get("publisher").encode())
    # Check checkboxes separately for input
    liked = request.form.get("liked")
    if liked == None:
        liked = 0
    else:
        liked = 1
    finished_reading = request.form.get("finished_reading")
    if finished_reading == None:
        finished_reading = 0
    else:
        finished_reading = 1
    # Check if location form field empty and if yes set to id 0 of name "Unspecified"
    location = request.form.get("location")
    if location == "" or location == None:
        location = "0"
        # Checks if location unspecified of id 0 is in the database if not adds an unspecified location of id 0
        location_query = db.execute("SELECT * FROM locations WHERE location_id = ?", (location,))
        location_name = location_query.fetchall()
        if len(location_name) < 1:
            db.execute("INSERT INTO locations (location_id, location_name) VALUES(?, ?)", (location, "Unspecified"))
    else:
        # Hash the location name string using SHA1 to generate the location_id which is the primary key in the authors table unless set to 0 then unspecified
        hashed_location_name = hashlib.sha1(location.encode()).hexdigest()
        # Check if location already in database if not insert into locations table
        fetched = db.execute("SELECT * FROM locations WHERE location_id = ?", (hashed_location_name,))
        location_rows = fetched.fetchall()
        if len(location_rows) == 0:
            with con:
                db.execute("INSERT INTO locations (location_id, location_name) VALUES(?, ?)", (hashed_location_name, location))
        location = hashed_location_name
    # Update the book entry in the database
    with con:
        db.execute("DELETE FROM books WHERE isbn = ?", (request.form.get("isbn"),))
        db.execute("INSERT INTO books (title, author_id, publisher_id, isbn, pages, date_published, language, synopsis, cover_art, finished_reading, liked, location_id, user_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (request.form.get("title"), hashed_author_name.hexdigest(), hashed_publisher_name.hexdigest(), request.form.get("isbn"), request.form.get("pages"), request.form.get("date_published"), request.form.get("language"), request.form.get("synopsis"), request.form.get("cover_art"), finished_reading, liked, location, session.get("user_id")))
    # Empty the flash message session variable
    session.pop('_flashes', None)
    # Inform user about successfully updating the book using a flash popup on home page
    flash("Successfully edited the book details")
    return redirect("/")

@app.route('/remove', methods=['POST'])
@login_required
def remove():
    # Connect to database in this context
    con = get_db()
    db = con.cursor()
    # Removes the book with matching isbn number from the database
    with con:
        db.execute("DELETE FROM books WHERE isbn = ?", (request.form.get("isbn"),))
    # Empty the flash message session variable
    session.pop('_flashes', None)
    # Inform user about successfully removing the book using a flash popup on home page
    flash("Successfully removed the book from your library")
    return redirect("/")

@app.route('/add', methods=['POST', 'GET'])
@login_required
def add():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Adds the isbn number to the current flask session to pass it through
        session["currentisbn"] = request.form.get("isbn")
        return redirect("/addconfirmation")
    return render_template("add.html")

@app.route('/addconfirmation', methods=['POST', 'GET'])
@login_required
def addconfirmation():
    # Empty the flash message session variable
    session.pop('_flashes', None)
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Connect to database in this context
        con = get_db()
        db = con.cursor()
        # Check if book already in database to prevent double entries
        fetched = db.execute("SELECT * FROM books WHERE isbn = ? AND user_id = ?", (request.form.get("isbn"), session.get("user_id")))
        rows = fetched.fetchall()
        if len(rows) != 0:
            return apology("This book is already in your database! If you want to change it please edit it instead")
        # Fetch book data into dictionary from form for easier formatting
        book_info = {
        "title" : request.form.get("title"),
        "author" : request.form.get("author"),
        "publisher": request.form.get("publisher"),
        "isbn" : request.form.get("isbn"),
        "pages" : request.form.get("pages"),
        "date_published" : request.form.get("date_published"),
        "language" : request.form.get("language"),
        "synopsis": request.form.get("synopsis"),
        "cover_art" : request.form.get("cover_art"),
        "location" : request.form.get("location"),
        }
        # Check checkboxes separately for input
        liked = request.form.get("liked")
        if liked == None:
            book_info["liked"] = 0
        else:
            book_info["liked"] = 1
        finished_reading = request.form.get("finished_reading")
        if finished_reading == None:
            book_info["finished_reading"] = 0
        else:
            book_info["finished_reading"] = 1
        # Check if location form field empty and if yes set to "Unspecified"
        if book_info["location"] == "" or book_info["location"] == None:
            book_info["location"] = "0"
            # Checks if location unspecified of id 0 is in the database if not adds an unspecified location of id 0
            location_query = db.execute("SELECT * FROM locations WHERE location_id = ?", (book_info["location"],))
            location_name = location_query.fetchall()
            if len(location_name) < 1:
                db.execute("INSERT INTO locations (location_id, location_name) VALUES(?, ?)", (book_info["location"], "Unspecified"))
        else:
            # Hash the location name string using SHA1 to generate the location_id which is the primary key in the authors table unless set to 0 then unspecified
            hashed_location_name = hashlib.sha1(book_info["location"].encode())
            # Check if location already in database if not insert into locations table
            fetched = db.execute("SELECT * FROM locations WHERE location_id = ?", (hashed_location_name.hexdigest(),))
            location_rows = fetched.fetchall()
            if len(location_rows) == 0:
                with con:
                    db.execute("INSERT INTO locations (location_id, location_name) VALUES(?, ?)", (hashed_location_name.hexdigest(), book_info["location"]))
            book_info["location"] = hashed_location_name.hexdigest()

        # Hash the author name string using SHA1 to generate the author_id which is the primary key in the authors table
        hashed_author_name = hashlib.sha1(book_info["author"].encode())
        # Check if author already in database if not insert into authors table
        fetched = db.execute("SELECT * FROM authors WHERE author_id = ?", (hashed_author_name.hexdigest(),))
        authors_rows = fetched.fetchall()
        if len(authors_rows) == 0:
            with con:
                db.execute("INSERT INTO authors (author_id, name) VALUES(?, ?)", (hashed_author_name.hexdigest(), book_info["author"]))
        # Hash the publisher name string using SHA1 to generate the publisher_id which is the primary key in the publishers table
        hashed_publisher_name = hashlib.sha1(book_info["publisher"].encode())
        # Check if publisher already in database if not insert into publishers table
        fetched = db.execute("SELECT * FROM publishers WHERE publisher_id = ?", (hashed_publisher_name.hexdigest(),))
        publisher_rows = fetched.fetchall()
        if len(publisher_rows) == 0:
            with con:
                db.execute("INSERT INTO publishers (publisher_id, name) VALUES(?, ?)", (hashed_publisher_name.hexdigest(), book_info["publisher"]))
        # Insert book to database with appropriate foreign keys
        with con:
            db.execute("INSERT INTO books (title, author_id, publisher_id, isbn, pages, date_published, language, synopsis, cover_art, finished_reading, liked, location_id, user_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (book_info["title"], hashed_author_name.hexdigest(), hashed_publisher_name.hexdigest(), book_info["isbn"], book_info["pages"], book_info["date_published"], book_info["language"], book_info["synopsis"], book_info["cover_art"], book_info["finished_reading"], book_info["liked"], book_info["location"], session.get("user_id")))
        # Inform user about successfully adding the book using a flash popup on home page
        flash("Successfully added the book to your library")
        # Redirect user to homepage
        return redirect("/")
    book_info = {
        "title" : "",
        "author" : "",
        "publisher": "",
        "isbn" : "",
        "pages" : "",
        "date_published" : "",
        "language" : "",
        "synopsis": "",
        "cover_art" : ""
    }
    if "currentisbn" in session:
        # Fetch information about the book with that ISBN from the ISBNdb API
        resp = req.get(f"https://api2.isbndb.com/book/{session["currentisbn"]}", headers=h)
        # Remove the ISBN session variable from flask
        session.pop("currentisbn")
        # Parse the results from the API response into json
        book_results = resp.json()
        # Check the API response for whether the book was fetched successfully
        if 'book' in book_results:
            flash(f"We have automatically filled some of the book details for you.")
            # Update the dictionary with the fetched book information
            book_info["title"] = book_results["book"]["title"].replace('-', ' ').title()
            if len(book_results["book"]["authors"]) > 0:
                book_info["author"] = book_results["book"]["authors"][0].replace('-', ' ').title()
            else:
                book_info["author"] = "Unknown Author"
            if "publisher" in book_results:
                book_info["publisher"] = book_results["book"]["publisher"].replace('-', ' ').title()
            else:
                book_info["publisher"] = "Unknown Publisher"
            book_info["isbn"] = book_results["book"]["isbn"]
            if "pages" in book_results:
                book_info["pages"] = book_results["book"]["pages"]
            if "date_published" in book_results:
                book_info["date_published"] = book_results["book"]["date_published"]
            if "language" in book_results:
                book_info["language"] = book_results["book"]["language"].title()
            if "synopsis" in book_results:
                book_info["synopsis"] = book_results["book"]["synopsis"]
            else:
                book_info["synopsis"] = ""
            book_info["cover_art"] = book_results["book"]["image"]
        else:
            # Show a message to the user regarding incorrect input
            flash(f"Sorry we could not automatically find the book under this ISBN number.")
    return render_template("addconfirmation.html", book_info=book_info)

if __name__ == "__main__":
    app.run(debug=True)