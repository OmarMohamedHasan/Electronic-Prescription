import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "app.db")

class PrescriptionModel:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def add_prescription(self, patient_id, doctor_id, diagnosis, medicines_data):
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.cursor.execute("INSERT INTO prescriptions (patient_id, doctor_id, date, notes) VALUES (?, ?, ?, ?)",
                                (patient_id, doctor_id, date, diagnosis))
            prescription_id = self.cursor.lastrowid

            for item in medicines_data:
                self.add_prescription_item(prescription_id, item["medicine_id"], item["dosage"], item["form"], item["instructions"])
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"Error adding prescription: {e}")
            return False

    def add_prescription_item(self, prescription_id, medicine_id, dosage, form, instructions):
        self.cursor.execute("INSERT INTO prescription_items (prescription_id, medicine_id, dosage, form, instructions) VALUES (?, ?, ?, ?, ?)",
                            (prescription_id, medicine_id, dosage, form, instructions))
        return self.cursor.lastrowid

    def get_prescription_details(self, prescription_id):
        self.cursor.execute("""
            SELECT
                p.id, p.date, p.notes, pa.name as patient_name, pa.age, pa.gender, pa.phone, pa.conditions,
                u.name as doctor_name
            FROM prescriptions p
            JOIN patients pa ON p.patient_id = pa.id
            JOIN users u ON p.doctor_id = u.id
            WHERE p.id = ?
        """, (prescription_id,))
        prescription = self.cursor.fetchone()

        self.cursor.execute("""
            SELECT
                m.name, pi.dosage, pi.form, pi.instructions
            FROM prescription_items pi
            JOIN medicines m ON pi.medicine_id = m.id
            WHERE pi.prescription_id = ?
        """, (prescription_id,))
        items = self.cursor.fetchall()

        return {"prescription": prescription, "items": items}

    def get_all_prescriptions(self):
        self.cursor.execute("""
            SELECT
                p.id, p.date, pa.name as patient_name, u.name as doctor_name
            FROM prescriptions p
            JOIN patients pa ON p.patient_id = pa.id
            JOIN users u ON p.doctor_id = u.id
            ORDER BY p.date DESC
        """)
        return self.cursor.fetchall()

    def search_prescriptions(self, start_date=None, end_date=None, patient_name=None, patient_phone=None):
        query = """
            SELECT
                p.id, p.date, pa.name as patient_name, u.name as doctor_name
            FROM prescriptions p
            JOIN patients pa ON p.patient_id = pa.id
            JOIN users u ON p.doctor_id = u.id
            WHERE 1=1
        """
        params = []

        if start_date:
            query += " AND p.date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND p.date <= ?"
            params.append(end_date)
        if patient_name:
            query += " AND pa.name LIKE ?"
            params.append(f'%{patient_name}%')
        if patient_phone:
            query += " AND pa.phone LIKE ?"
            params.append(f'%{patient_phone}%')

        query += " ORDER BY p.date DESC"
        self.cursor.execute(query, tuple(params))
        return self.cursor.fetchall()

    def __del__(self):
        self.conn.close()

