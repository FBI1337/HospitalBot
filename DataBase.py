import sqlite3
from datetime import datetime

class BotDB:
    def __init__(self, db_file):
        self.db_file = db_file

    def add_user(self, user_id, name, middle_name, surname, address, phone_number):
        join_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO User (user_id, name, middle_name, surname, address, phone_number, join_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (user_id, name, middle_name, surname, address, phone_number, join_date))
        conn.commit()
        conn.close()

    def find_user_by_id(self, user_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id))
        user = cursor.fetchone()
        conn.close()
        return user
                                                
