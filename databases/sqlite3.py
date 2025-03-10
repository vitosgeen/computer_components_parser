# connect to sqlite3 database
import sqlite3

# class to connect to sqlite3 database
class SQLite3:
    DB_NAME = 'database.db'
    
    # constructor
    def __init__(self, db_name=DB_NAME):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
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
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS motherboard_overviews (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mb_item_id INTEGER,
                type TEXT,
                text TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
        self.cursor.execute(''' CREATE TABLE IF NOT EXISTS motherboard_techspecs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mb_item_id INTEGER,
                type TEXT,
                text TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
        self.cursor.execute(''' CREATE TABLE IF NOT EXISTS motherboard_supports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mb_item_id INTEGER,
                type TEXT,
                data TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
        self.conn.commit()

    # close connection
    def close(self):
        self.conn.close()