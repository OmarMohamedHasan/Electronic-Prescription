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
    def save_clinic_settings(self, doctor_name, clinic_address, phone_numbers, logo_path, signature_path, clinic_email, clinic_website):
        self.cursor.execute("DELETE FROM clinic_settings") # Clear existing settings
        self.cursor.execute("INSERT INTO clinic_settings (doctor_name, clinic_address, phone_numbers, logo_path, signature_path, clinic_email, clinic_website) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (doctor_name, clinic_address, phone_numbers, logo_path, signature_path, clinic_email, clinic_website))
        self.conn.commit()
        return True

    def get_clinic_settings(self):
        self.cursor.execute("SELECT doctor_name, clinic_address, phone_numbers, logo_path, signature_path, clinic_email, clinic_website FROM clinic_settings LIMIT 1")
        result = self.cursor.fetchone()
        if result:
            return {
                "doctor_name": result[0],
                "clinic_address": result[1],
                "phone_numbers": result[2],
                "logo_path": result[3],
                "signature_path": result[4],
                "clinic_email": result[5],
                "clinic_website": result[6]
            }
        return None

    # Print Settings
    def save_print_settings(self, logo_position, print_template_style, selected_template_id):
        self.cursor.execute("DELETE FROM print_settings")
        self.cursor.execute("INSERT INTO print_settings (logo_position, print_template_style, selected_template_id) VALUES (?, ?, ?)",
                            (logo_position, print_template_style, selected_template_id))
        self.conn.commit()
        return True

    def get_print_settings(self):
        self.cursor.execute("SELECT logo_position, print_template_style, selected_template_id FROM print_settings LIMIT 1")
        result = self.cursor.fetchone()
        if result:
            return {
                "logo_position": result[0],
                "print_template_style": result[1],
                "selected_template_id": result[2]
            }
        return None

    # Print Templates Management
    def add_print_template(self, name, file_path):
        try:
            self.cursor.execute("INSERT INTO print_templates (name, file_path) VALUES (?, ?)",
                                (name, file_path))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # Template name already exists

    def get_all_print_templates(self):
        self.cursor.execute("SELECT id, name, file_path FROM print_templates")
        return [{
            "id": row[0],
            "name": row[1],
            "file_path": row[2]
        } for row in self.cursor.fetchall()]

    def get_print_template_by_id(self, template_id):
        self.cursor.execute("SELECT id, name, file_path FROM print_templates WHERE id = ?", (template_id,))
        result = self.cursor.fetchone()
        if result:
            return {
                "id": result[0],
                "name": result[1],
                "file_path": result[2]
            }
        return None

    def delete_print_template(self, template_id):
        self.cursor.execute("DELETE FROM print_templates WHERE id = ?", (template_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def __del__(self):
        self.conn.close()


