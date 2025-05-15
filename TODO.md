# Features to mention in writeup
[] - Would you get extra points for using book object instead of dictionary takes tuple of SQL as a constructor and changes into book YES
[] - ADD WISHLIST TABLE THAT TIES TO THE USER TABLE
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
[] - why u chose isbn db api

## New Goals to add in writeup
[] - And read or unread toggle boolean
[] - Barcode reader remember to add as input method on writeup
[] - Liked unlike boolean adds
[] - enable to save the location of the book
[] - Results display using cover art
[] - Enable multiple users to use the app therefore setup a secure login register system
[] - Secure storage of login credentials (I used hashing :)
[] - Allow the user to edit book entries and update the book details in the database
[] - have a wishlist tab to allow to add books to buy in the future
[] - display books to read that havent been read and read books to revisit
[] - allow users to borrow books
[] - Custom apology pages rendered on wrong input?

### Identification Of New User Needs: 
1. The program should allow the user to easily add new books to his existing book catalogue (by scanning the barcode).
2. The program should have a way for the user to search up whether a book is in the catalogue using its title/author and view information about the book.
3. The program should have a way for the user to edit book entries which are already in their catalogue
4. The program should keep track of the location of a book within a house i.e. which room was it in when it was added to the catalogue.
5. The program should have a section for books that have been borrowed to other people with information of who those books were lent to.
6. The program should be able to suggest unread books from within the users catalogue
7. The program should have a second suggestions tab which suggests old books for the user to revisit based on if they liked them or not
8. The program should be easy to use using the book cover arts as the main UI element
9. The program should securely support multiple users
10. The program should have an option to wishlist books to buy in the future

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
user_id INT NOT NULL UNIQUE,
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

```mermaidjs
flowchart TD
subgraph Homepage After Login:
    A([Start]) --> B[/Display Options/]
    A --> C[/Display Book Suggestions/]
end

B -->|Add Book| D[/Input ISBN/]
D -->|Automatic| G[[Fetch Data From ISBN API]]
G --> H[(Save fetched data into SQL database)]
D -->|Manual| I[/Display UI for manual input of data/]
I --> H


B -->|Search Book| E[/Input Title/Author/]
E --> F[(Fetch data from the database)]
F --> J[/Display books or error/]

B -->|Borrowed Books| K[(Fetch data from the database)]
K --> L[/Display books or error/]

B -->|Wishlisted Books| M[(Fetch data from the database)]
M --> N[/Display books or error/]
```
