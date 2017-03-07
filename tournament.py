#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2


def connect():
    # Connect to the PostgreSQL database.  Returns a database connection.
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    # Remove all the match records from the database.
    conn = connect()
    c = conn.cursor()
    # Delete all rows in matches and set matches+wins to 0 in players table
    c.execute("DELETE FROM matches;")
    c.execute("UPDATE players SET wins = 0")
    c.execute("UPDATE players SET matches = 0")
    conn.commit()
    conn.close()


def deletePlayers():
    # Remove all the player records from the database.
    conn = connect()
    c = conn.cursor()
    # Delete all rows in players and reset the sequence
    c.execute("DELETE FROM players;")
    c.execute("ALTER SEQUENCE players_user_id_seq RESTART WITH 1;")
    c.execute("UPDATE players SET user_id=nextval('players_user_id_seq');")
    conn.commit()
    conn.close()


"""Question for instructor: Is last_value a more efficient method for finding
the # of users? My thought process is that if I make the code check the
last_value from the sequence it won't have to cycle through every row in
the players table. However, as far as I can tell there's no way to have the
last_value column in the sequence differentiate between no users and one user.
If I set the minimum of the sequence to 0 but the start value to 1 it still
creates a initial user with the id 0. Therefor, I have the code only check the
players table when a value of 1 is returned."""


def countPlayers():
    # Returns the number of players currently registered.
    conn = connect()
    c = conn.cursor()
    # Select last value from the player ID sequence
    c.execute("SELECT last_value FROM players_user_id_seq")
    totalPlayers = c.fetchone()
    totalPlayers = totalPlayers[0]
    # Sequence won't return 0 so check via players table
    if totalPlayers == 1:
        c.execute("SELECT COUNT(*) FROM players")
        totalPlayers = c.fetchone()
        totalPlayers = totalPlayers[0]

    conn.commit()
    conn.close()
    return totalPlayers


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
     """

    conn = connect()
    c = conn.cursor()
    c.execute("INSERT INTO players (name, wins, matches) VALUES (%s, %s, %s)",
              (name, 0, 0))
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a
    player tied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """

    conn = connect()
    c = conn.cursor()
    # Select all from players table and order by most wins
    c.execute("SELECT * FROM players ORDER BY wins DESC;")
    rankings = c.fetchall()
    conn.commit()
    conn.close()
    return rankings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()
    # Add a new match in matches table
    c.execute(
        "INSERT INTO matches (player_1, player_2, winner) VALUES (%s, %s, %s)",
        (winner, loser, winner))
    # Add 1 point to the winner's win column in players table
    c.execute(
        "UPDATE players SET wins = wins + 1 WHERE user_id = %s", ([winner]))
    # Add 1 point to the match column of both players
    c.execute(
        "UPDATE players SET matches = matches + 1 WHERE user_id = %s",
        ([winner]))
    c.execute(
        "UPDATE players SET matches = matches + 1 WHERE user_id = %s",
        ([loser]))
    conn.commit()
    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each player
    appears exactly once in the pairings.  Each player is paired with another
    player with an equal or nearly-equal win record, that is, a player adjacent
    to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """

    # Get all players and count them
    allPlayers = playerStandings()
    totalPlayers = len(allPlayers)
    # Initialize the list of tuples
    pairs = []
    # Example: 8 players would have 4 pairs
    for number in xrange(0, totalPlayers, 2):
            # Create tuple with ID1, Name1, ID2, Name2
            pair = (allPlayers[number][0], allPlayers[number][1],
                    allPlayers[number+1][0], allPlayers[number+1][1])
            # Add pair tuple to list
            pairs.append(pair)
    return pairs
