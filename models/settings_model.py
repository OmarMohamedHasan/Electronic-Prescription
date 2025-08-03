import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "app.db")

class SettingsModel:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.cursor = self.conn.cursor()

    # User Management
    def get_all_users(self):
        self.cursor.execute("SELECT id, username, name FROM users")
        return self.cursor.fetchall()

    def add_user(self, username, password, name):
        hashed_password = generate_password_hash(password)
        try:
            self.cursor.execute("INSERT INTO users (username, password, name) VALUES (?, ?, ?)",
                                (username, hashed_password, name))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # Username already exists

    def update_user(self, user_id, username, name, password=None):
        if password:
            hashed_password = generate_password_hash(password)
            self.cursor.execute("UPDATE users SET username = ?, name = ?, password = ? WHERE id = ?",
                                (username, name, hashed_password, user_id))
        else:
            self.cursor.execute("UPDATE users SET username = ?, name = ? WHERE id = ?",
                                (username, name, user_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_user(self, user_id):
        self.cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    # Clinic Settings
    def save_clinic_settings(self, doctor_name, clinic_address, phone_numbers, logo_path, signature_path):
        self.cursor.execute("DELETE FROM clinic_settings") # Clear existing settings
        self.cursor.execute("INSERT INTO clinic_settings (doctor_name, clinic_address, phone_numbers, logo_path, signature_path) VALUES (?, ?, ?, ?, ?)",
                            (doctor_name, clinic_address, phone_numbers, logo_path, signature_path))
        self.conn.commit()
        return True

    def get_clinic_settings(self):
        self.cursor.execute("SELECT doctor_name, clinic_address, phone_numbers, logo_path, signature_path FROM clinic_settings LIMIT 1")
        return self.cursor.fetchone()

    # Print Settings (Placeholder for now, will be expanded)
    def save_print_settings(self, logo_position, print_template_style):
        self.cursor.execute("DELETE FROM print_settings")
        self.cursor.execute("INSERT INTO print_settings (logo_position, print_template_style) VALUES (?, ?)",
                            (logo_position, print_template_style))
        self.conn.commit()
        return True

    def get_print_settings(self):
        self.cursor.execute("SELECT logo_position, print_template_style FROM print_settings LIMIT 1")
        return self.cursor.fetchone()

    def __del__(self):
        self.conn.close()


