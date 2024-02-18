from flask import Flask, render_template, redirect, request, session, g, flash
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
import requests as req
import hashlib
from helpers import apology, login_required

h = {'Authorization': '51841_15f8a1a6b75e8c37b224c61dca5164e7'}

# Start application
app = Flask(__name__)

# Set session to use filesystem (instead of cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Database global variable path
DATABASE = "C:\\Users\\Spacks\\Documents\\Bookagement\\tutorial.db"

# Get the global database variable if available
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/')
@login_required
def index():
    return render_template("index.html")

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
        # Ensure username doesnt exist
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
    #FIXME: actually make a search routine that searches using authors and publishers and aggregate sql
    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Get user input
        search_query = request.form.get("inputsearch").title()
        # Connect to database in this context
        db = get_db().cursor()
        # Query database for matching books
        fetched = db.execute(f"SELECT * FROM testbooks WHERE title LIKE ?", (f"{search_query}%",))
        rows = fetched.fetchall()
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
    fetched = db.execute("SELECT * FROM testbooks WHERE isbn = ?", (current_book,))
    rows = fetched.fetchall()
    if len(rows) > 1:
        return apology("Your search query was not specific enough")
    book_info = {
        "title" : rows[0][1],
        "author" : rows[0][2],
        "publisher": rows[0][3],
        "isbn" : rows[0][0],
        "pages" : rows[0][4],
        "date_published" : rows[0][5],
        "language" : rows[0][6],
        "synopsis": rows[0][7],
        "cover_art" : rows[0][8]
    }
    return render_template("view.html", book_info=book_info)

@app.route('/edit', methods=['POST'])
@login_required
def edit():
    # Connect to database in this context
    con = get_db()
    db = con.cursor()
    # Gets the book details from database using the ISBN number passed in form
    fetched = db.execute("SELECT * FROM testbooks WHERE isbn = ?", (request.form.get("isbn"),))
    rows = fetched.fetchall()[0]
    book_info = {}
    book_info["title"] = rows[1]
    book_info["author"] = rows[2]
    book_info["publisher"] = rows[3]
    book_info["isbn"] = rows[0]
    book_info["pages"] = rows[4]
    book_info["date_published"] = rows[5]
    book_info["language"] = rows[6]
    book_info["synopsis"] = rows[7]
    book_info["cover_art"] = rows[8]
    return render_template("edit.html", book_info=book_info)

@app.route('/save', methods=['POST'])
@login_required
def save():
    # Connect to database in this context
    con = get_db()
    db = con.cursor()
    # Update the book entry in the database
    with con:
        db.execute("DELETE FROM testbooks WHERE isbn = ?", (request.form.get("isbn"),))
        db.execute("INSERT INTO testbooks (title, author, publisher, isbn, pages, date_published, language, synopsis, cover_art) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (request.form.get("title"), request.form.get("author"), request.form.get("publisher"), request.form.get("isbn"), request.form.get("pages"), request.form.get("date_published"), request.form.get("language"), request.form.get("synopsis"), request.form.get("cover_art")))
    # Empty the flash message session variable
    session.pop('_flashes', None)
    # Inform user about successfully updating the book using a flash popup on home page
    flash("Succesfully edited the book details")
    return redirect("/")

@app.route('/remove', methods=['POST'])
@login_required
def remove():
    # Connect to database in this context
    con = get_db()
    db = con.cursor()
    # Removes the book with matching isbn number from the database
    with con:
        db.execute("DELETE FROM testbooks WHERE isbn = ?", (request.form.get("isbn"),))
    # Empty the flash message session variable
    session.pop('_flashes', None)
    # Inform user about successfully removing the book using a flash popup on home page
    flash("Succesfully removed the book from your library")
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
        fetched = db.execute("SELECT * FROM testbooks WHERE isbn = ?", (request.form.get("isbn"),))
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
        "liked" : request.form.get("rating"),
        "finished_reading" : request.form.get("finished_reading"),
        "user_id" : session.get("user_id")
        }
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
        fetched = db.execute("SELECT * FROM publishers WHERE author_id = ?", (hashed_publisher_name.hexdigest(),))
        publisher_rows = fetched.fetchall()
        if len(publisher_rows) == 0:
            with con:
                db.execute("INSERT INTO publishers (publisher_id, name) VALUES(?, ?)", (hashed_publisher_name.hexdigest(), book_info["publisher"]))
        # Insert book to database with appropriate foreign keys
        # TODO: organize insert statement properly add user_id field from session variable and make tables in tutorial.db or try final.db
        # TODO: Then work on other endpoints to add the additional select statements and information
        with con:
            db.execute("INSERT INTO testbooks (title, author, publisher, isbn, pages, date_published, language, synopsis, cover_art) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)")
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
            book_info["publisher"] = book_results["book"]["publisher"].replace('-', ' ').title()
            book_info["isbn"] = book_results["book"]["isbn"]
            book_info["pages"] = book_results["book"]["pages"]
            book_info["date_published"] = book_results["book"]["date_published"]
            book_info["language"] = book_results["book"]["language"].title()
            if "synopsis" in book_results:
                book_info["synopsis"] = book_results["book"]["synopsis"]
            else:
                book_info["synopsis"] = ""
            book_info["cover_art"] = book_results["book"]["image"]
        else:
            flash(f"Sorry we could not automatically find the book under this ISBN number.")
    return render_template("addconfirmation.html", book_info=book_info)

if __name__ == "__main__":
    app.run(debug=True)