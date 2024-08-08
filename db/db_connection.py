import sqlite3
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
db_file_path = os.path.join(script_dir, 'chat_backup.db')

def create_connection(db_file = db_file_path):
    connection = None
    try:
        connection = sqlite3.connect(db_file)
        print('Connection to SQLite DB successful')
    except sqlite3.Error as error:
        print('Error occurred - ', error)
    return connection

def initial_setup(connection):
    table_init_path = os.path.join(script_dir, 'table_init.sql')
    try:
        cursor = connection.cursor()
        with open(table_init_path, 'r') as file:
            queries = file.read()
            cursor.executescript(queries)

        connection.commit()
        cursor.close()
        print('Initial setup successful')
    except sqlite3.Error as error:
        print('Error occurred - ', error)

def add_user(connection, ip, name):
    try:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO users (ip, name) VALUES (?, ?)', (ip, name))
        connection.commit()
        cursor.close()
        print('User added successfully')
    except sqlite3.Error as error:
        print('Error occurred - ', error)

def add_message(connection, ip, message):
    try:
        cursor = connection.cursor()
        cursor.execute('INSERT INTO chats (ip, message) VALUES (?, ?)', (ip, message))
        connection.commit()
        cursor.close()
    except sqlite3.Error as error:
        print('Error occurred - ', error)

def terminate_connection(connection):
    if connection:
        connection.close()
        print('Connection to SQLite DB terminated')