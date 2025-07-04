from flask import redirect, session, g
from functools import wraps
import logging
import os
import re
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

logging.basicConfig(
    filename="error.log",  # Log file name
    level=logging.ERROR,  # Only log errors and higher (ERROR, CRITICAL)
    format="%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]",
)

def account_change(username, email, password, confirm):
    """Check if the email and password are valid."""
    db = get_db()
    cursor = db.cursor()

    if email is None:
        pass
    elif "@" not in email or "." not in email:
        return 0.5
    elif not re.match(r"[^@]+@[A-Za-z]+\.[a-z]+", email):
        return 0.5

    # Same Email & Password change but not matching
    if not email and password != confirm:
        return 1

    # Same email & Password change and matching
    elif not email and password == confirm:
        hash = generate_password_hash(password)
        try:
            cursor.execute(
                "UPDATE users SET hash = ? WHERE Username = ?", (hash, username)
            )
            db.commit()
            return 2

        except sqlite3.Error as e:
            logging.error(
                f"Error: could not update the password in database for user {username}"
            )
        return 5

    # Email change && Password not change
    elif email and not password and not confirm:
        try:
            cursor.execute(
                "UPDATE users SET email = ? WHERE Username = ?", (email, username)
            )
            db.commit()
            return 3

        except sqlite3.Error as e:
            logging.error(
                f"Error: could not update the email in database for user {username}"
            )
            return 5

    # Email & password change
    elif email and password == confirm:
        hash = generate_password_hash(password)
        try:
            cursor.execute(
                "UPDATE users SET email = ?, hash = ? WHERE Username = ?",
                (
                    email, 
                    hash, 
                    username
                    ),
            )
            db.commit()
            return 4
        except sqlite3.Error as e:
            logging.error(
                f"Error: could not update the email and password in database for user {username}"
            )
            return 5

    else:
        return 5

def account_create(username, email, password, confirm):
    """Check if username, email and password are valid."""

    # Account input verfication
    # Empty username
    if username is None:
        return 1
    # Username length between 3 and 20
    elif len(username) < 3 or len(username) > 20:
        return 2
    # Email is empty
    elif email is None:
        return 3
    # Email has no @ or .
    elif "@" not in email or "." not in email:
        return 4
    # Email not in the right format
    elif not re.match(r"[^@]+@[A-Za-z]+\.[a-z]+", email):
        return 5
    # Password empty
    elif password is None:
        return 6
    # Password must be between 8 and 20 chars
    elif len(password) < 8 or len(password) > 20:
        return 7
    # Password and confirm password not matching
    elif password != confirm:
        return 8
    # Username cannot be the same as password
    elif username == password:
        return 9
    # Username cannot be same as email
    elif username == email:
        return 10
    # Confirm is empty
    elif confirm is None:
        return 11
    # Email same as password
    elif email == password:
        return 12

    # Hash the password for security
    hash = generate_password_hash(password)

    # Open the database
    db = get_db()
    cursor = db.cursor()

    # Insert user data into database
    try:
        cursor.execute(
            "INSERT INTO users (username, email, hash) VALUES (?, ?, ?)",
            (
                username, 
                email, 
                hash
                ),
        )
        db.commit()
    except sqlite3.IntegrityError as e:
        logging.error(f"Integrity Error: {str(e)} while inserting user {username}")
        return 13
    except sqlite3.DatabaseError as e:
        logging.error(f"Database Error: {str(e)}")
        return 14
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")
        return 15

    return 0

def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def get_db():
    if "db" not in g:
        # Get the database path locally on device
        basedir = os.path.abspath(os.path.dirname(__file__))
        db_path = os.path.join(basedir, "database.db")
        g.db = sqlite3.connect(db_path)
        g.db.row_factory = sqlite3.Row
    return g.db

def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/latest/patterns/viewdecorators/
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decorated_function

def profile_history(username):
    """Get the profile history of the user."""
    db = get_db()
    cursor = db.cursor()
    record = []

    try:
        cursor.execute(
            "SELECT GameSelect, Letter, WinLossTie1, WinLossTie2, Username1, Username2, WordList1, WordList2, Score1, Score2, DateTime FROM game_records WHERE Username1 = ? or Username2 = ?",
            (username, username),
        )
        record = cursor.fetchall()
    except sqlite3.Error as e:
        logging.error(
            f"Error: could not pull profile history for user {username} or data does not exist"
        )

    if not record:
        record = []

    all_data = []
    for row in record:
        data = {
            "GameType": row[0],
            "Letter": row[1],
            "WinLossTie1": row[2],
            "WinLossTie2": row[3],
            "Username1": row[4],
            "Username2": row[5],
            "WordList1": (
                ", ".join(
                    [x if x.strip() else "/ " for x in re.findall(r"'(.*?)'", row[6])]
                )
                if row[6]
                else []
            ),
            "WordList2": (
                ", ".join(
                    [x if x.strip() else "/ " for x in re.findall(r"'(.*?)'", row[7])]
                )
                if row[7]
                else []
            ),
            "Score1": row[8],
            "Score2": row[9],
            "DateTime": row[10],
        }
        all_data.append(data)

    return all_data

def scoring(p1_score, p2_score, p1_list, p2_list, letter):
    """Calculate the score for each player."""
    # Check if player 1 word starts with the letter and not empty
    for word in p1_list:
        if not word:
            p1_score = p1_score - 10
        elif word.startswith(letter.lower()) == False:
            p1_score = p1_score - 10

    # Check if player 2 word starts with the letter and not empty
    for word in p2_list:
        if not word:
            p2_score = p2_score - 10
        elif word.startswith(letter.lower()) == False:
            p2_score = p2_score - 10

    # Check for duplicate words between players
    for p1_word, p2_word in zip(p1_list, p2_list):
        if p1_word and p2_word and p1_word == p2_word:
            p1_score = p1_score - 5
            p2_score = p2_score - 5

    # List of files to check versus words
    filenames = ["name.txt", "animal.txt", "object.txt", "movie.txt", "country.txt"]

    # Check for words in the files
    for p1_word, p2_word, filename in zip(p1_list, p2_list, filenames):
        try:
            with open(f"data/{filename}", "r", encoding="utf-8") as file:
                # Read the contents of the file and split into lines
                contents = file.read().splitlines()
                if not p1_word or p1_score == 0:
                    continue
                elif p1_word == p2_word and p1_word not in contents:
                    p1_score -= 5
                elif p1_word not in contents:
                    p1_score -= 10

                if not p2_word or p2_score == 0:
                    continue
                elif p2_word == p1_word and p2_word not in contents:
                    p2_score -= 5
                elif p2_word not in contents:
                    p2_score -= 10

        except FileNotFoundError:
            print(f"Warning: {filename} not found. Skipping.")
            continue

    # Check if p1 score < 0 or > 50 and set min (0) or max(50)

    if p1_score < 0:
        p1_score = 0
    elif p1_score > 50:
        p1_score = 50

    # Check if p2 score < 0 or > 50 and set min (0) or max(50)
    if p2_score < 0:
        p2_score = 0
    elif p2_score > 50:
        p2_score = 50

    return p1_score, p2_score

def search_db(user, password):
    db = get_db()
    cursor = db.cursor()

    if user is None:
        return 1
    elif password is None:
        return 2

    try:
        cursor.execute("SELECT * FROM users WHERE username = ?", (user,))
        row = cursor.fetchone()
    except sqlite3.Error as e:
        logging.error(f"Error: could not get user signin data for user {user}")
        return 3
    if row is None or not check_password_hash(row["hash"], password):
        return 4

    return 0