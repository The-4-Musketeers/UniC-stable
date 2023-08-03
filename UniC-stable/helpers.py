import sqlite3
from flask import redirect, session, request
from functools import wraps
from colorama import Fore, init

init(autoreset=True)

# connect database with sqlite3
def connect_to_db(db):
    connection = sqlite3.connect(db, check_same_thread=False)
    return connection


# execute a write query into database
def write_to_db(connection, query, placeholders=()):
    cursor = connection.cursor()
    print(f"{Fore.GREEN} {query}, {placeholders}")
    cursor.execute(query, placeholders)
    connection.commit()
    return True


# execute a read query from database
def read_from_db(connection, query, placeholders=()):
    cursor = connection.cursor()
    print(f"{Fore.GREEN} {query}, {placeholders}")
    cursor.execute(query, placeholders)
    return cursor.fetchall()


# decorates routes to require login
def login_required(f):
    # http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function
