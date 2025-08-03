import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "app.db")

class PatientModel:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def add_patient(self, name, age, gender, phone, conditions):
        last_visit = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.cursor.execute("INSERT INTO patients (name, age, gender, phone, conditions, last_visit) VALUES (?, ?, ?, ?, ?, ?)",
                                (name, age, gender, phone, conditions, last_visit))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def get_all_patients(self):
        self.cursor.execute("SELECT * FROM patients")
        return self.cursor.fetchall()

    def get_patient_by_id(self, patient_id):
        self.cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        return self.cursor.fetchone()

    def update_patient(self, patient_id, name, age, gender, phone, conditions):
        self.cursor.execute("UPDATE patients SET name = ?, age = ?, gender = ?, phone = ?, conditions = ? WHERE id = ?",
                            (name, age, gender, phone, conditions, patient_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def update_last_visit(self, patient_id):
        last_visit = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("UPDATE patients SET last_visit = ? WHERE id = ?",
                            (last_visit, patient_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def __del__(self):
        self.conn.close()


