CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
DROP TABLE IF EXISTS pictures CASCADE;
DROP TABLE IF EXISTS Users CASCADE;

CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    last_name    CHAR(20),
    email varchar(255) UNIQUE,
    password varchar(255),
    first_name CHAR(20),
    dob DATE,
    gender CHAR(1),
    friends LONGTEXT, 
   CONSTRAINT users_pk PRIMARY KEY (user_id)
);

CREATE TABLE Comments 
(
date Date,
user_id int4,
text varchar(300),
comment_id int4 AUTO_INCREMENT,
PRIMARY KEY (comment_id),
FOREIGN KEY (user_id) REFERENCES Users(user_id)
); 

CREATE TABLE Tag
(
	word_desc varchar(300),
    primary key (word_desc)
);

CREATE TABLE Pictures
(
  picture_id int4  AUTO_INCREMENT,
  user_id int4,
  imgdata longblob ,
  caption VARCHAR(255),
  INDEX upid_idx (user_id),
  CONSTRAINT pictures_pk PRIMARY KEY (picture_id)
);







CREATE TABLE Album
(
	dates DATE,
	album_id int4  AUTO_INCREMENT,
	album_name varchar(300), 
	Primary Key(album_id)
);


CREATE TABLE Contain(
	picture_id int4,
	album_id int4,
Primary Key(picture_id, album_id),
FOREIGN KEY(picture_id)
	REFERENCES pictures(picture_id),
FOREIGN KEY(album_id)
	REFERENCES album(album_id)
);

CREATE TABLE Writes(
	User_id int4,
Comment_id int4,
Primary Key(User_id, comment_id),
FOREIGN KEY(User_id)
	REFERENCES Users(User_id),
FOREIGN KEY(comment_id)
	REFERENCES comments(comment_id)
    );

CREATE TABLE Describes(
	Word_desc CHAR(20),
picture_id int4,
Primary Key(word_desc, picture_id),
FOREIGN KEY(picture_id)
	REFERENCES pictures(picture_id),
FOREIGN KEY(word_desc)
	REFERENCES Tag(word_desc)
);







CREATE TABLE Creates(
	User_id int4,
album_id int4,

Primary Key(User_id, album_id),
FOREIGN KEY(User_id)
	REFERENCES Users(User_id),
FOREIGN KEY(album_id)
	REFERENCES Album(album_id)
);








INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');



