import os
import sqlite3

def get_db_connection():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    db_path = os.path.join(parent_dir, "database.db")
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    return connection

def execute(sql, params=None):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        if params is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, params)
        connection.commit()
    finally:
        connection.close()

def query(sql, params=None):
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        if params is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, params)
        return cursor.fetchall()
    finally:
        connection.close()

def last_insert_id():
    connection = get_db_connection()
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT last_insert_rowid()")
        return cursor.fetchone()[0]
    finally:
        connection.close()
