-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.
CREATE DATABASE tournament;
\c tournament;
CREATE TABLE players ( user_id serial PRIMARY KEY, name VARCHAR (50) NOT NULL, wins integer NOT NULL, matches integer NOT NULL );
CREATE TABLE matches ( player_1 serial references players(user_id), player_2 serial references players(user_id), winner serial references players(user_id));
