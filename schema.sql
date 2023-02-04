drop table if exists reviews;
drop table if exists favorites;
drop table if exists uses;
drop table if exists belongsto;
drop table if exists contains;
drop table if exists users;
drop table if exists dish;
drop table if exists tool;
drop table if exists category;

CREATE TABLE users (
    userID serial primary key not null,
    email varchar(80) not null,
    firstname varchar(80) not null,
    lastname varchar(80) not null
);

CREATE TABLE dish (
    dishID varchar(80) primary key not null,
    title varchar(80),
    directions text,
    time_amt varchar(80)
);

CREATE TABLE tool (
    toolName varchar(80) primary key not null
);

CREATE TABLE category (
    categoryName varchar(80) primary key not null,
    categoryDescription varchar(500)
);

CREATE TABLE reviews (
    userID int REFERENCES users(userID),
    dishID varchar(80) REFERENCES dish(dishID),
    numStars int,
    reviewText varchar(500),
    numUpvote int
);

CREATE TABLE favorites (
    userID int REFERENCES users(userID),
    dishID varchar(80) REFERENCES dish(dishID)
);

CREATE TABLE uses (
    dishID varchar(80) REFERENCES dish(dishID),
    toolName varchar(80) REFERENCES tool(toolName)
);

CREATE TABLE contains (
    dishID varchar(80) REFERENCES dish(dishID),
    ingredientName varchar(500)
);

CREATE TABLE belongsto (
     dishID varchar(80) REFERENCES dish(dishID),
    categoryName varchar(80) REFERENCES category(categoryName)
);
