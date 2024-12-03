# connect to sqlite3 database
import sqlite3

# class to connect to sqlite3 database
class SQLite3:
    DB_NAME = 'database.db'
    
    # constructor
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()

    # install tables
    def install(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS motherboard_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orig_id text,
                title TEXT,
                price REAL,
                link TEXT,
                description TEXT,
                category TEXT,
                manufacturer TEXT
            )
        ''')
        self.conn.commit()

    # close connection
    def close(self):
        self.conn.close()