# TODO For Project
[] - Complex database add authors and publishers and users tying in to it not only for passwords with author and publisher id and information (where from name etc)
[] - Add hashing algorithm to generate author and publisher id
[] - Make the home page be a recently added books thingy
[] - Additional borrowed category
[] - And read or unread toggle boolean
[] - Liked unlike boolean add
[] - Set up the user login user specific tables???
[] - Look at the scoring table on drive
[] - Add a wishlist
[] - Add a bunch of books to your database to showcase how it works
[] - Generate UML diagram for class relationship from the sql schema

# Features to mention in writeup
[] - Make a directory diagram as in github showing the nesting of folders with images and templates as children
[] - Sorry we didn't find any books notification
[] - Mention hashing password in sql table
[] - Write about flash messages popup
[] - Connect github to add onto writeup
[] - Barcode reader remember to add as input method on writeup
[] - Explain why u used flask over react
[] - Add custom page icon and check if names of pages change at heading

# SQL Commands?
Generate UML diagram for class relationship from this schema
```sql
CREATE TABLE `books` (
	`isbn` INT NOT NULL UNIQUE,
	`title` TEXT NOT NULL,
	`author_id` INT NOT NULL,
	`publisher_id` INT NOT NULL,
	`pages` INT NOT NULL,
	`date_published` TEXT NOT NULL,
	`language` TEXT NOT NULL,
	`synopsis` TEXT,
	`cover_art` TEXT,
	`finished_reading` BOOLEAN NOT NULL DEFAULT 'FALSE',
	`liked` BOOLEAN NOT NULL DEFAULT 'FALSE',
    `user_id` INT NOT NULL,
	PRIMARY KEY (`isbn`)
    FOREIGN KEY(author_id) REFERENCES authors(author_id)
    FOREIGN KEY(publisher_id) REFERENCES publishers(publisher_id)
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

CREATE TABLE `authors` (
	`author_id` INT NOT NULL UNIQUE,
	`name` TEXT NOT NULL,
	PRIMARY KEY (`author_id`)
);

CREATE TABLE `publishers` (
	`publisher_id` INT NOT NULL UNIQUE,
	`name` TEXT NOT NULL,
	PRIMARY KEY (`publisher_id`)
);

CREATE TABLE `users` (
	`user_id` INT NOT NULL UNIQUE AUTO_INCREMENT,
	`username` TEXT UNIQUE NOT NULL,
	`hash` TEXT NOT NULL,
	PRIMARY KEY (`user_id`)
);
```
