# Bookagement
A flask web app for domestic book management
📕📗📘📙

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

```bash
C:.
├───flask_session
├───templates
├───venv
│   ├───Lib
│   │   └───site-packages
│   │       ├───blinker
│   │       │   └───__pycache__
│   │       ├───blinker-1.7.0.dist-info
│   │       ├───cachelib
│   │       │   └───__pycache__
│   │       ├───cachelib-0.12.0.dist-info
│   │       ├───certifi
│   │       │   └───__pycache__
│   │       ├───certifi-2024.2.2.dist-info
│   │       ├───charset_normalizer
│   │       │   ├───cli
│   │       │   │   └───__pycache__
│   │       │   └───__pycache__
│   │       ├───charset_normalizer-3.3.2.dist-info
│   │       ├───click
│   │       │   └───__pycache__
│   │       ├───click-8.1.7.dist-info
│   │       ├───colorama
│   │       │   ├───tests
│   │       │   │   └───__pycache__
│   │       │   └───__pycache__
│   │       ├───colorama-0.4.6.dist-info
│   │       │   └───licenses
│   │       ├───flask
│   │       │   ├───json
│   │       │   │   └───__pycache__
│   │       │   ├───sansio
│   │       │   │   └───__pycache__
│   │       │   └───__pycache__
│   │       ├───flask-3.0.2.dist-info
│   │       ├───flask_session
│   │       │   └───__pycache__
│   │       ├───flask_session-0.6.0.dist-info
│   │       ├───idna
│   │       │   └───__pycache__
│   │       ├───idna-3.6.dist-info
│   │       ├───itsdangerous
│   │       │   └───__pycache__
│   │       ├───itsdangerous-2.1.2.dist-info
│   │       ├───jinja2
│   │       │   └───__pycache__
│   │       ├───Jinja2-3.1.3.dist-info
│   │       ├───markupsafe
│   │       │   └───__pycache__
│   │       ├───MarkupSafe-2.1.5.dist-info
│   │       ├───pip
│   │       │   ├───_internal
│   │       │   │   ├───cli
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───commands
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───distributions
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───index
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───locations
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───metadata
│   │       │   │   │   ├───importlib
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───models
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───network
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───operations
│   │       │   │   │   ├───build
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   ├───install
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───req
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───resolution
│   │       │   │   │   ├───legacy
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   ├───resolvelib
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───utils
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───vcs
│   │       │   │   │   └───__pycache__
│   │       │   │   └───__pycache__
│   │       │   ├───_vendor
│   │       │   │   ├───cachecontrol
│   │       │   │   │   ├───caches
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───certifi
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───chardet
│   │       │   │   │   ├───cli
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   ├───metadata
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───colorama
│   │       │   │   │   ├───tests
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───distlib
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───distro
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───idna
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───msgpack
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───packaging
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───pkg_resources
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───platformdirs
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───pygments
│   │       │   │   │   ├───filters
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   ├───formatters
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   ├───lexers
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   ├───styles
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───pyparsing
│   │       │   │   │   ├───diagram
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───pyproject_hooks
│   │       │   │   │   ├───_in_process
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───requests
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───resolvelib
│   │       │   │   │   ├───compat
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───rich
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───tenacity
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───tomli
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───truststore
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───urllib3
│   │       │   │   │   ├───contrib
│   │       │   │   │   │   ├───_securetransport
│   │       │   │   │   │   │   └───__pycache__
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   ├───packages
│   │       │   │   │   │   ├───backports
│   │       │   │   │   │   │   └───__pycache__
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   ├───util
│   │       │   │   │   │   └───__pycache__
│   │       │   │   │   └───__pycache__
│   │       │   │   ├───webencodings
│   │       │   │   │   └───__pycache__
│   │       │   │   └───__pycache__
│   │       │   └───__pycache__
│   │       ├───pip-24.0.dist-info
│   │       ├───requests
│   │       │   └───__pycache__
│   │       ├───requests-2.31.0.dist-info
│   │       ├───urllib3
│   │       │   ├───contrib
│   │       │   │   ├───emscripten
│   │       │   │   │   └───__pycache__
│   │       │   │   └───__pycache__
│   │       │   ├───util
│   │       │   │   └───__pycache__
│   │       │   └───__pycache__
│   │       ├───urllib3-2.2.0.dist-info
│   │       │   └───licenses
│   │       ├───werkzeug
│   │       │   ├───datastructures
│   │       │   │   └───__pycache__
│   │       │   ├───debug
│   │       │   │   ├───shared
│   │       │   │   └───__pycache__
│   │       │   ├───middleware
│   │       │   │   └───__pycache__
│   │       │   ├───routing
│   │       │   │   └───__pycache__
│   │       │   ├───sansio
│   │       │   │   └───__pycache__
│   │       │   ├───wrappers
│   │       │   │   └───__pycache__
│   │       │   └───__pycache__
│   │       ├───werkzeug-3.0.1.dist-info
│   │       └───__pycache__
│   └───Scripts
└───__pycache__
```
