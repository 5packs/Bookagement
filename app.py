from flask import Flask, render_template, redirect, request, session, g, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import requests as req
import hashlib
from helpers import apology, login_required, custom_merge_sort, pick_three, Book

h = {'Authorization': 'ISBN_API_KEY'}

# Start application
app = Flask(__name__)

# Set up static folder allowing for stylesheets
app.static_folder = 'static'

# Set session to use filesystem (instead of cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database global variable path
DATABASE = "C:\\Users\\User\\Documents\\Bookagement\\bookagement.db"

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
    # Sets up connection to the databases
    db = get_db().cursor()
    # Query the database for the most recent added or edited unread books
    fetched = db.execute("SELECT * FROM books WHERE finished_reading = ? AND borrowed_id = ? AND user_id = ?", ("0", "0", session.get("user_id")))
    rows1 = fetched.fetchall()
    # Function for picking three random books out of a book tuple list
    book_info1 = pick_three(rows1)
    # Query the database for the most recent added or edited unread books
    fetched = db.execute("SELECT * FROM books WHERE finished_reading = ? AND borrowed_id = ? AND liked = ? AND user_id = ?", ("1", "0", "1", session.get("user_id")))
    rows2 = fetched.fetchall()
    # Function for picking three random books out of a book tuple list
    book_info2 = pick_three(rows2)
    # Render the homepage
    return render_template("index.html", book_info1=book_info1, book_info2=book_info2)

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
            username = request.form.get("username")
            password = generate_password_hash(request.form.get("password"))
            user_id = hashlib.sha1(f"{username}{password}".encode()).hexdigest()
            db.execute("INSERT INTO users (username, hash, user_id) VALUES(?, ?, ?)", (username, password, user_id))
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
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get user input
        search_query = request.form.get("inputsearch").title()
        # Connect to database in this context
        db = get_db().cursor()
        # Query database for matching books using title or author using aggregate SQL and SQL JOIN
        fetched = db.execute(f"SELECT * FROM books JOIN authors ON books.author_id=authors.author_id WHERE (title LIKE ? OR name LIKE ?) AND user_id = ?", (f"{search_query}%", f"{search_query}%", session.get("user_id")))
        rows = fetched.fetchall()
        # Sorts all the books to be displayed using a custom written merge sort
        # Get sort input from form
        sort_by = int(request.form.get("sort_by"))
        # Sorts by parameter in the form of column within tuple of book in books
        custom_merge_sort(rows, sort_by)
        return render_template("results.html", books=rows, search_query=search_query)
    return render_template("search.html")

@app.route('/view', methods=['POST'])
@login_required
def view():
    # Checks which book was clicked on the search page
    current_book = request.form.get("bookid")
    # Sets up connection to the database
    db = get_db().cursor()
    # Query the database for the book
    fetched = db.execute("SELECT * FROM books WHERE book_id = ?", (current_book,))
    rows = fetched.fetchall()
    # Fetch author publisher borrower and location name using the hashed id
    author_query = db.execute("SELECT * FROM authors WHERE author_id = ?", (rows[0][2],))
    author_name = author_query.fetchall()[0][1]
    publisher_query = db.execute("SELECT * FROM publishers WHERE publisher_id = ?", (rows[0][3],))
    publisher_name = publisher_query.fetchall()[0][1]
    location_query = db.execute("SELECT * FROM locations WHERE location_id = ?", (rows[0][11],))
    location_name = location_query.fetchall()[0][1]
    borrow_id = rows[0][13]
    borrow_name = "No"
    if borrow_id != '0':
        borrow_query = db.execute("SELECT * FROM borrowed WHERE borrowed_id = ?", (borrow_id,))
        borrow_name = borrow_query.fetchall()[0][1]
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
        "book_id": rows[0][14],
        "location" : location_name,
        "borrowed_id": borrow_id,
        "borrowed_name": borrow_name
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
    fetched = db.execute("SELECT * FROM books WHERE book_id = ?", (request.form.get("book_id"),))
    rows = fetched.fetchall()[0]
    # ---
    book_info = Book(rows)
    # ---
    # Fetch author and publisher name using the hashed id and add them to the dictionary
    author_query = db.execute("SELECT * FROM authors WHERE author_id = ?", (book_info.author_id,))
    author_name = author_query.fetchall()[0][1]
    publisher_query = db.execute("SELECT * FROM publishers WHERE publisher_id = ?", (book_info.publisher_id,))
    publisher_name = publisher_query.fetchall()[0][1]
    location_query = db.execute("SELECT * FROM locations WHERE location_id = ?", (book_info.location,))
    location_name = location_query.fetchall()[0][1]
    book_info.SetAuthor(author_name)
    book_info.SetPublisher(publisher_name)
    book_info.SetLocation(location_name)
    return render_template("edit.html", book_info=book_info)

@app.route('/save', methods=['POST'])
@login_required
def save():
    # Connect to database in this context
    con = get_db()
    db = con.cursor()
    # Hash the author name string using SHA1 to generate the author_id which is the primary key in the authors table
    hashed_author_name = hashlib.sha1(request.form.get("author").encode())
    # Check if author already in database if not insert into authors table
    fetched = db.execute("SELECT * FROM authors WHERE author_id = ?", (hashed_author_name.hexdigest(),))
    author_rows = fetched.fetchall()
    if len(author_rows) == 0:
        with con:
            db.execute("INSERT INTO authors (author_id, name) VALUES(?, ?)", (hashed_author_name.hexdigest(), request.form.get("author")))
    # Hash the publisher name string using SHA1 to generate the publisher_id which is the primary key in the publishers table
    hashed_publisher_name = hashlib.sha1(request.form.get("publisher").encode())
    # Check if publisher already in database if not insert into publishers table
    fetched = db.execute("SELECT * FROM publishers WHERE publisher_id = ?", (hashed_publisher_name.hexdigest(),))
    publisher_rows = fetched.fetchall()
    if len(publisher_rows) == 0:
        with con:
            db.execute("INSERT INTO publishers (publisher_id, name) VALUES(?, ?)", (hashed_publisher_name.hexdigest(), request.form.get("publisher")))

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
    book_id = request.form.get("book_id")
    with con:
        db.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
        db.execute("INSERT INTO books (title, author_id, publisher_id, isbn, pages, date_published, language, synopsis, cover_art, finished_reading, liked, location_id, user_id, book_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (request.form.get("title"), hashed_author_name.hexdigest(), hashed_publisher_name.hexdigest(), request.form.get("isbn"), request.form.get("pages"), request.form.get("date_published"), request.form.get("language"), request.form.get("synopsis"), request.form.get("cover_art"), finished_reading, liked, location, session.get("user_id"), book_id))
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
        rows = db.execute("SELECT * FROM books WHERE book_id = ?", (request.form.get("book_id"),)).fetchall()
        db.execute("DELETE FROM books WHERE book_id = ?", (request.form.get("book_id"),))
        if rows[0][13] != '0':
            db.execute("DELETE FROM borrowed WHERE borrowed_id = ?", (rows[0][13],))
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
    return render_template("add.html", isbn="")

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
        # TODO: use an object instead of a dictionary here and figure out if you can pass a list of objects instead of tuples to the other templates html
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
        # Hash the isbn + user_id string using SHA1 to generate the book_id which is the primary key in the books table
        hashed_book_id = hashlib.sha1(f"{book_info["isbn"]}{session.get("user_id")}".encode()).hexdigest()
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
            db.execute("INSERT INTO books (title, author_id, publisher_id, isbn, pages, date_published, language, synopsis, cover_art, finished_reading, liked, location_id, user_id, book_id) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (book_info["title"], hashed_author_name.hexdigest(), hashed_publisher_name.hexdigest(), book_info["isbn"], book_info["pages"], book_info["date_published"], book_info["language"], book_info["synopsis"], book_info["cover_art"], book_info["finished_reading"], book_info["liked"], book_info["location"], session.get("user_id"), hashed_book_id))
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

@app.route('/returningto', methods=['POST', 'GET'])
@login_required
def returningto():
    # Connect to database in this context
    con = get_db()
    db = con.cursor()
    # Get book and borrow id from forms
    book_id = request.form.get("book_id")
    borrowed_id = request.form.get("borrowed_id")
    # Update the book entry in the database with new borrow id
    with con:
        db.execute("DELETE FROM borrowed WHERE borrowed_id = ?", (borrowed_id,))
        db.execute("UPDATE books SET borrowed_id = ? WHERE book_id = ?", ('0', book_id))
    # Empty the flash message session variable
    session.pop('_flashes', None)
    # Inform user about successfully updating the book using a flash popup on home page
    flash("Successfully returned the book")
    return redirect("/")

@app.route('/borrowingto', methods=['POST', 'GET'])
@login_required
def borrowingto():
    book_id = request.form.get("book_id")
    return render_template("borrowingto.html", book_id=book_id)

@app.route('/borrow', methods=['POST', 'GET'])
@login_required
def borrow():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Connect to database in this context
        con = get_db()
        db = con.cursor()
        # Get book id and borrower from forms
        book_id = request.form.get("book_id")
        borrower = request.form.get("borrower")
        # Generates a borrow id by hashing the book_id and borrower name
        borrow_id = hashlib.sha1(f"{book_id}{borrower}".encode()).hexdigest()
        # Update the book entry in the database with new borrow id
        with con:
            db.execute("INSERT OR REPLACE INTO borrowed (borrowed_id, person) VALUES(?, ?)", (borrow_id, borrower))
            db.execute("UPDATE books SET borrowed_id = ? WHERE book_id = ?", (borrow_id, book_id))
        # Empty the flash message session variable
        session.pop('_flashes', None)
        # Inform user about successfully updating the book using a flash popup on home page
        flash("Successfully borrowed the book")
        return redirect("/")

@app.route('/borrowed', methods=['POST', 'GET'])
@login_required
def borrowed():
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Connect to database in this context
        con = get_db()
        db = con.cursor()
        # Access form input of search for person name
        borrowed_person = request.form.get("borrower")
        # Select from books where borrowed =! 0 and user current and borrowed person matches searched name
        fetched = db.execute("SELECT * FROM books JOIN borrowed ON books.borrowed_id = borrowed.borrowed_id WHERE books.borrowed_id != ? AND books.user_id = ? AND borrowed.person LIKE ?", ("0", session.get("user_id"), f"{borrowed_person}%"))
        rows = fetched.fetchall()
        return render_template("borrowed.html", books=rows)
    # Connect to database in this context
    con = get_db()
    db = con.cursor()
    # Select from books where borrowed =! 0 and user current
    fetched = db.execute("SELECT * FROM books WHERE borrowed_id != ? AND user_id = ?", ("0", session.get("user_id")))
    rows = fetched.fetchall()
    return render_template("borrowed.html", books=rows)

@app.route('/wishlist', methods=['POST', 'GET'])
@login_required
def wishlist():
    books = []
     # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Connect to database in this context
        con = get_db()
        db = con.cursor()
        # Fetch information about the book
        wish_id = request.form.get("wishid")
        # Check if tick clicked or cross
        action = request.form.get("action")
        if action == 'add':
            fetched = db.execute("SELECT * FROM wishlist WHERE wish_id = ?", (wish_id,))
            rows = fetched.fetchall()
            # Removes the entry from the wishlist
            with con:
                db.execute("DELETE FROM wishlist WHERE wish_id == ?", (wish_id,))
            return render_template("add.html", isbn=rows[0][1])
        # Removes the entry from the wishlist
        with con:
            db.execute("DELETE FROM wishlist WHERE wish_id == ?", (wish_id,))
        redirect("/wishlist")
    # Connect to database in this context
    con = get_db()
    db = con.cursor()
    # Select from books where borrowed =! 0 and user current
    fetched = db.execute("SELECT * FROM wishlist WHERE user_id = ?", (session.get("user_id"),))
    rows = fetched.fetchall()
    return render_template("wishlist.html", books=rows)

@app.route('/wished', methods=['POST', 'GET'])
@login_required
def wished():
    # Empty the flash message session variable
    session.pop('_flashes', None)
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Connect to database in this context
        con = get_db()
        db = con.cursor()
        # Check if book already in database to prevent double entries
        fetched = db.execute("SELECT * FROM wishlist WHERE isbn = ? AND user_id = ?", (request.form.get("isbn"), session.get("user_id")))
        rows = fetched.fetchall()
        if len(rows) != 0:
            return apology("This book is already in your database! If you want to change it please edit it instead")
        # Fetch book data into dictionary from form for easier formatting
        book_info = {
        "title" : request.form.get("title"),
        "isbn" : request.form.get("isbn"),
        "cover_art" : request.form.get("cover_art"),
        "user_id" : session.get("user_id")
        }
        # Generates a borrow id by hashing the book_id and borrower name
        wish_id = hashlib.sha1(f"{book_info['user_id']}{book_info["isbn"]}".encode()).hexdigest()
        # Adds book to the wishlist database
        with con:
            db.execute("INSERT INTO wishlist (title, isbn, cover_art, user_id, wish_id) VALUES(?, ?, ?, ?, ?)", (book_info["title"], book_info["isbn"], book_info["cover_art"], book_info["user_id"], wish_id))
        # Inform user about successfully adding the book using a flash popup on home page
        flash("Successfully added the book to your wishlist")
        # Redirect user to homepage for wishlist
        return redirect("/wishlist")
    return redirect("/")

@app.route('/wishfor', methods=['POST', 'GET'])
@login_required
def wishfor():
    # Empty the flash message session variable
    session.pop('_flashes', None)
    # Set up empty dictionary with book details
    book_info = {
        "title" : "",
        "isbn" : "",
        "cover_art" : "",
    }
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        if request.form.get("isbn") != "":
            book_info["isbn"] = request.form.get("isbn")
            # Fetch information about the book with that ISBN from the ISBNdb API
            resp = req.get(f"https://api2.isbndb.com/book/{book_info['isbn']}", headers=h)
            # Parse the results from the API response into json
            book_results = resp.json()
            # Check the API response for whether the book was fetched successfully
            if 'book' in book_results:
                flash(f"We have automatically filled some of the book details for you.")
                # Update the dictionary with the fetched book information
                book_info["title"] = book_results["book"]["title"].replace('-', ' ').title()
                book_info["cover_art"] = book_results["book"]["image"]
            else:
                # Show a message to the user regarding incorrect input
                flash(f"Sorry we could not automatically find the book under this ISBN number.")
    return render_template("wishfor.html", book_info=book_info)

if __name__ == "__main__":
    app.run(debug=True)
