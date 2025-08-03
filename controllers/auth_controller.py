import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "app.db")

class AuthController:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    def create_user(self, username, password, name):
        hashed_password = generate_password_hash(password)
        try:
            self.cursor.execute("INSERT INTO users (username, password, name) VALUES (?, ?, ?)",
                                (username, hashed_password, name))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # Username already exists

    def verify_user(self, username, password):
        self.cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
        user = self.cursor.fetchone()
        if user and check_password_hash(user[0], password):
            return True
        return False

    def get_user_id(self, username):
        self.cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = self.cursor.fetchone()
        return user_id[0] if user_id else None

    def __del__(self):
        self.conn.close()


