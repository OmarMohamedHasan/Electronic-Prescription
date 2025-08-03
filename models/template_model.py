import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "database", "app.db")

class TemplateModel:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = sqlite3.connect(DB_PATH)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
        except sqlite3.Error as e:
            print(f"Database connection error: {e}")

    def disconnect(self):
        if self.conn:
            self.conn.close()

    def add_template(self, name, description, items):
        try:
            self.connect()
            self.cursor.execute("INSERT INTO templates (name, description) VALUES (?, ?)", (name, description))
            template_id = self.cursor.lastrowid
            for item in items:
                self.cursor.execute("INSERT INTO template_items (template_id, medicine_id, dosage, form, instructions) VALUES (?, ?, ?, ?, ?)",
                                    (template_id, item['medicine_id'], item['dosage'], item['form'], item['instructions']))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error adding template: {e}")
            return False
        finally:
            self.disconnect()

    def get_all_templates(self):
        try:
            self.connect()
            self.cursor.execute("SELECT id, name, description FROM templates")
            templates = self.cursor.fetchall()
            return templates
        except sqlite3.Error as e:
            print(f"Error getting all templates: {e}")
            return []
        finally:
            self.disconnect()

    def get_template_by_id(self, template_id):
        try:
            self.connect()
            self.cursor.execute("SELECT id, name, description FROM templates WHERE id = ?", (template_id,))
            template = self.cursor.fetchone()
            if template:
                self.cursor.execute("SELECT medicine_id, dosage, form, instructions FROM template_items WHERE template_id = ?", (template_id,))
                items = self.cursor.fetchall()
                return {"id": template[0], "name": template[1], "description": template[2], "items": items}
            return None
        except sqlite3.Error as e:
            print(f"Error getting template by id: {e}")
            return None
        finally:
            self.disconnect()

    def delete_template(self, template_id):
        try:
            self.connect()
            self.cursor.execute("DELETE FROM template_items WHERE template_id = ?", (template_id,))
            self.cursor.execute("DELETE FROM templates WHERE id = ?", (template_id,))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error deleting template: {e}")
            return False
        finally:
            self.disconnect()

    def update_template(self, template_id, name, description, items):
        try:
            self.connect()
            self.cursor.execute("UPDATE templates SET name = ?, description = ? WHERE id = ?", (name, description, template_id))
            self.cursor.execute("DELETE FROM template_items WHERE template_id = ?", (template_id,))
            for item in items:
                self.cursor.execute("INSERT INTO template_items (template_id, medicine_id, dosage, form, instructions) VALUES (?, ?, ?, ?, ?)",
                                    (template_id, item['medicine_id'], item['dosage'], item['form'], item['instructions']))
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error updating template: {e}")
            return False
        finally:
            self.disconnect()


