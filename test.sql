-- database: :memory:
-- Create a new SQLite database and connect to it
ATTACH DATABASE 'team1.db' AS testdb;

-- Use the database
drop table if exists includes;
drop table if exists lists;
drop table if exists retweets;
drop table if exists mentions;
drop table if exists hashtags;
drop table if exists tweets;
drop table if exists follows;
drop table if exists users;

create table users (
  usr         int,
  pwd        text,
  name        text,
  email       text,
  city        text,
  timezone    float,
  primary key (usr)
);
create table follows (
  flwer       int,
  flwee       int,
  start_date  date,
  primary key (flwer,flwee),
  foreign key (flwer) references users,
  foreign key (flwee) references users
);
create table tweets (
  tid        int,
  writer      int,
  tdate       date,
  text        text,
  replyto     int,
  primary key (tid),
  foreign key (writer) references users,
  foreign key (replyto) references tweets
);
create table hashtags (
  term        text,
  primary key (term)
);
create table mentions (
  tid         int,
  term        text,
  primary key (tid,term),
  foreign key (tid) references tweets,
  foreign key (term) references hashtags
);
create table retweets (
  usr         int,
  tid         int,
  rdate       date,
  primary key (usr,tid),
  foreign key (usr) references users,
  foreign key (tid) references tweets
);
create table lists (
  lname        text,
  owner        int,
  primary key (lname),
  foreign key (owner) references users
);
create table includes (
  lname       text,
  member      int,
  primary key (lname,member),
  foreign key (lname) references lists,
  foreign key (member) references users
);
-- Insert test data into the 'users' table
INSERT INTO users (usr, pwd, name, email, city, timezone)
VALUES (1, 'password1', 'User1', 'user1@example.com', 'City1', 0.0),
       (2, 'password2', 'User2', 'user2@example.com', 'City2', 1.0),
       (3, 'password3', 'User3', 'user3@example.com', 'City3', 2.0),
       (4, 'password4', 'User4', 'user4@example.com', 'City4', 3.0),
       (5, 'password5', 'User5', 'user5@example.com', 'City5', 4.0),
       (6, 'password6', 'User6', 'user6@example.com', 'City6', -5.0),
       (7, 'password7', 'User7', 'user7@example.com', 'City7', 3.5),
       (8, 'password8', 'User8', 'user8@example.com', 'City8', 7.0),
       (9, 'password9', 'User9', 'user9@example.com', 'City9', 4.5);

-- Insert test data into the 'follows' table
INSERT INTO follows (flwer, flwee, start_date)
VALUES (1, 2, '2023-10-30'),
       (2, 3, '2023-10-30'),
       (3, 1, '2023-10-30'),
       (4, 2, '2023-10-30'),
       (5, 1, '2023-10-30'),
       (1, 4, '2023-10-30'),
       (5, 2, '2023-10-30'),
       (6, 7, '2023-10-30'),
       (8, 9, '2023-10-30');

-- Insert test data into the 'tweets' table
INSERT INTO tweets (tid, writer, tdate, text, replyto)
VALUES (1, 1, '2023-10-30', 'Tweet 1 by User 1', NULL),
       (2, 2, '2023-10-30', 'Tweet 2 by User 2', NULL),
       (3, 1, '2023-10-30', 'Reply to Tweet 1 by User 1', 1),
       (4, 3, '2023-10-30', 'Tweet 3 by User 3', NULL),
       (5, 2, '2023-10-30', 'Tweet 4 by User 2', NULL),
       (6, 3, '2023-10-30', 'Tweet 5 by User 3', NULL),
       (7, 4, '2023-10-30', 'Tweet 6 by User 4', NULL),
       (8, 1, '2023-10-30', 'Reply to Tweet 3 by User 1', 3),
       (9, 5, '2023-10-30', 'Tweet 7 by User 5', NULL);

-- Insert test data into the 'hashtags' table
INSERT INTO hashtags (term)
VALUES ('#tag1'), ('#tag2'), ('#tag3'), ('#tag4'), ('#tag5');

-- Insert test data into the 'mentions' table
INSERT INTO mentions (tid, term)
VALUES (1, '#tag1'), (2, '#tag2'), (3, '#tag1'), (4, '#tag3'), (5, '#tag4'), (6, '#tag5'), (7, '#tag6'), (8, '#tag7'), (9, '#tag8');

-- Insert test data into the 'retweets' table
INSERT INTO retweets (usr, tid, rdate)
VALUES (2, 1, '2023-10-30'),
       (3, 2, '2023-10-30'),
       (1, 3, '2023-10-30'),
       (4, 4, '2023-10-30'),
       (5, 5, '2023-10-30'),
       (6, 5, '2023-10-30'),
       (7, 7, '2023-10-30'),
       (8, 1, '2023-10-30'),
       (9, 4, '2023-10-30');

-- Insert test data into the 'lists' table
INSERT INTO lists (lname, owner)
VALUES ('List1', 1),
       ('List2', 2),
       ('List3', 3),
       ('List4', 4),
       ('List5', 5),
       ('List7', 8),
       ('List8', 9),
       ('List9', 6);

-- Insert test data into the 'includes' table
INSERT INTO includes (lname, member)
VALUES ('List1', 2),
       ('List2', 3),
       ('List3', 1),
       ('List4', 5),
       ('List5', 4),
       ('List6', 6),
       ('List7', 7),
       ('List8', 8),
       ('List9', 9);

-- Commit the changes and close the database

DETACH DATABASE testdb;
