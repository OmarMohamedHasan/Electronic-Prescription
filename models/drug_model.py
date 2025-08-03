import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "app.db")

class DrugModel:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()

    def add_medicine(self, name, dosage, form, instructions):
        try:
            self.cursor.execute("INSERT INTO medicines (name, dosage, form, instructions) VALUES (?, ?, ?, ?)",
                                (name, dosage, form, instructions))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False # Medicine with this name might already exist (if name was UNIQUE)

    def get_all_medicines(self):
        self.cursor.execute("SELECT * FROM medicines")
        return self.cursor.fetchall()

    def get_medicine_by_id(self, medicine_id):
        self.cursor.execute("SELECT * FROM medicines WHERE id = ?", (medicine_id,))
        return self.cursor.fetchone()

    def update_medicine(self, medicine_id, name, dosage, form, instructions):
        self.cursor.execute("UPDATE medicines SET name = ?, dosage = ?, form = ?, instructions = ? WHERE id = ?",
                            (name, dosage, form, instructions, medicine_id))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def delete_medicine(self, medicine_id):
        self.cursor.execute("DELETE FROM medicines WHERE id = ?", (medicine_id,))
        self.conn.commit()
        return self.cursor.rowcount > 0

    def __del__(self):
        self.conn.close()


