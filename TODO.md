# Questions for Mr Lane
[] - Would you get extra points for using book object instead of dictionary takes tuple of SQL as a constructor and changes into book YES

# TODO For Project
[] - Change the title names on all of your html files
[] - Display current bestsellers to add to wishlist on main page??? no according to lane
[] - Look at the scoring table on drive
[] - Add a bunch of books to your database to showcase how it works
[] - Generate UML diagram for class relationship from the sql schema
[] - Make it pretty using background images and colors and fonts?

# Features to add in the future
[] - better visuals and design using flex box

# Features to mention in writeup
[] - should i implement pages on book searches ADD WISHLIST TABLE THAT TIES TO THE USER TABLE
[] - Add a wishlist? in a separate table and single page for adding simple information about the book and then adding book to library
[] - main page add books that you have read and liked to maybe revisit at some point
[] - Additional borrowed category which is already displayed remember
[] - end user feedback in analysis and at the ending 
[] - Custom apology pages rendered on wrong input
[] - Are there extra points for multiple complex algorithms if i already have merge sort do i need sha1 NO BUT CHANGE MERGE SOIRT TO SORT BY COLUMN
[] - Make the home page be a recently added books thingy work with random unread books just random index the rows and pick 3 unread books
[] - Should i implement the different ways to sort searched books YESSS cus it makes merge sort more complex so add dropdown form
[] - Multiple users
[] - Paramaterised sql
[] - Use of jinja to generate dynamic html
[] - Used aggregate SQL and Join command to query for books by both title and author
[] - Reformat the app to use a bookid not isbn as primary key because multiple users cant add the same book otherwise then add borrowed
[] - Results display using cover art
[] - Mark which fields are compulsory with a star in their description on both add and edit pages
[] - Add larger text box for synopsis on both add and edit pages
[] - And read or unread toggle boolean
[] - Liked unlike boolean add
[] - Used figma to design the web interface with my client??
[] - Use sorting merge sort to sort books by release date once fetched as a tuple list
[] - When viewing make sure to set userid=curentuserid to only show single users books
[] - fix users table and add rooms table into all the app functions edit addconf and view
[] - ask lane whether this database system is complex enough? if not (Set up the user login user specific tables???)
[] - Add hashing algorithm to generate author and publisher id
[] - Complex database add authors and publishers and users tying in to it not only for passwords with author and publisher id and information (where from name etc)
[] - Make a directory diagram as in github showing the nesting of folders with images and templates as children
[] - Sorry we didn't find any books notification
[] - Mention hashing password in sql table
[] - Write about flash messages popup
[] - Connect github to add onto writeup
[] - Barcode reader remember to add as input method on writeup
[] - Explain why u used flask over react
[] - Add custom page icon and check if names of pages change at heading
[] - Explain why use Jinja CSS bootstrap flask etc
[] - Use sqlite3 how it works with app

## New Goals to add in writeup
[] - Enable multiple users to use the app
[] - Secure storage of login credentials (I used hashing :)
[] - Allow the user to edit book entries and update the book details in the database

## Original Goals
### Identification Of User Needs:		
1. The program should allow the user to easily add new books to his existing book catalogue (by scanning the barcode).
2. The program should have a way for the user to search up whether a book is in the catalogue using its title/author and view information about the book.
3. The program should keep track of the location of a book within a house i.e. which shelf was it on when it was added to the catalogue.
4. The program should have a section for books that have been lent to other people with information of who those books were lent to.
5. The program should be able to suggest unread books from within the users catalogue based on the previously read books and the user rating of those books.
6. The program should have a second suggestions tab which suggests new books for the user to buy based on the previously read books and the user rating of those books.

# SQL Commands?
Generate UML diagram for class relationship from this schema
```sql
CREATE TABLE books (
isbn INT NOT NULL,
title TEXT NOT NULL,
author_id INT NOT NULL,
publisher_id INT NOT NULL,
pages INT NOT NULL,
date_published TEXT NOT NULL,
language TEXT NOT NULL,
synopsis TEXT,
cover_art TEXT,
finished_reading BOOLEAN NOT NULL DEFAULT 'FALSE',
liked BOOLEAN NOT NULL DEFAULT 'FALSE',
location_id TEXT NOT NULL DEFAULT '0',
user_id INT NOT NULL,
borrowed_id TEXT NOT NULL DEFAULT '0',
book_id INT NOT NULL UNIQUE,
PRIMARY KEY(book_id)
FOREIGN KEY(author_id) REFERENCES authors(author_id)
FOREIGN KEY(publisher_id) REFERENCES publishers(publisher_id)
FOREIGN KEY(user_id) REFERENCES users(user_id)
FOREIGN KEY(location_id) REFERENCES locations(location_id)
FOREIGN KEY(borrowed_id) REFERENCES borrowed(borrowed_id)
);

CREATE TABLE authors (
author_id INT NOT NULL UNIQUE,
name TEXT NOT NULL,
PRIMARY KEY (author_id)
);

CREATE TABLE publishers (
publisher_id INT NOT NULL UNIQUE,
name TEXT NOT NULL,
PRIMARY KEY (publisher_id)
);

CREATE TABLE users (
user_id INT NOT NULL UNIQUE AUTOINCREMENT,
username TEXT UNIQUE NOT NULL,
hash TEXT NOT NULL,
PRIMARY KEY (user_id)
);

CREATE TABLE locations (
location_id INT NOT NULL,
location_name TEXT NOT NULL,
PRIMARY KEY (location_id)
);

CREATE TABLE borrowed (
borrowed_id INT NOT NULL,
person TEXT NOT NULL,
PRIMARY KEY (borrowed_id)
);

CREATE TABLE wishlist (
wish_id TEXT NOT NULL UNIQUE,
isbn INT NOT NULL,
title TEXT NOT NULL,
user_id TEXT NOT NULL,
cover_art TEXT NOT NULL,
PRIMARY KEY (wish_id)
FOREIGN KEY(user_id) REFERENCES users(user_id)
);
```
