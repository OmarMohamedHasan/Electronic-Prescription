import sqlite3
import os
from werkzeug.security import generate_password_hash

# مسار قاعدة البيانات
DB_PATH = os.path.join(os.path.dirname(__file__), "app.db")

def update_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # حذف جدول المرضى وإعادة إنشائه بالتعديلات المطلوبة
    c.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT,
            phone TEXT,
            conditions TEXT,
            last_visit TEXT
        )
    ''')

    # جدول المستخدمين
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            name TEXT
        )
    ''')

    # إضافة Admin لو مش موجود
    c.execute("SELECT * FROM users WHERE id = 1000")
    if not c.fetchone():
        c.execute(
            "INSERT INTO users (id, username, password, name) VALUES (?, ?, ?, ?)",
            (1000, 'admin', '0000', 'Admin')
        )

    # إضافة مريض افتراضي لو جدول المرضى فارغ
    c.execute("SELECT COUNT(*) FROM patients")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO patients (name, age, gender, phone, conditions, last_visit) VALUES (?, ?, ?, ?, ?, ?)",
                  ("مريض تجريبي", 30, "ذكر", "0123456789", "لا يوجد", "2024-01-01"))

    # إضافة دواء افتراضي لو جدول الأدوية فارغ
    c.execute("SELECT COUNT(*) FROM medicines")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO medicines (name, dosage, form, instructions) VALUES (?, ?, ?, ?)",
                  ("دواء تجريبي", "500 مجم", "أقراص", "مرة واحدة يوميًا"))

    # جدول الأدوية
    c.execute('''
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            dosage TEXT,
            form TEXT,
            instructions TEXT
        )
    ''')

    # جدول الروشتات
    c.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            doctor_id INTEGER,
            date TEXT,
            notes TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients(id),
            FOREIGN KEY (doctor_id) REFERENCES users(id)
        )
    ''')

    # جدول تفاصيل الروشتة
    c.execute('''
        CREATE TABLE IF NOT EXISTS prescription_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prescription_id INTEGER,
            medicine_id INTEGER,
            dosage TEXT,
            duration TEXT,
            instructions TEXT,
            FOREIGN KEY (prescription_id) REFERENCES prescriptions(id),
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    ''')

    # جدول الاسطمبات (قوالب الأدوية لأمراض معينة)
    c.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT
        )
    """)

    # إضافة أسطمبة افتراضية لو جدول الاسطمبات فارغ
    c.execute("SELECT COUNT(*) FROM templates")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO templates (name, description) VALUES (?, ?)",
                  ("أسطمبة تجريبية", "وصف لأسطمبة تجريبية"))

    # جدول تفاصيل الأدوية داخل الاسطمبة
    c.execute("""
        CREATE TABLE IF NOT EXISTS template_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id INTEGER,
            medicine_id INTEGER,
            dosage TEXT,
            duration TEXT,
            instructions TEXT,
            FOREIGN KEY (template_id) REFERENCES templates(id),
            FOREIGN KEY (medicine_id) REFERENCES medicines(id)
        )
    """)

    # إضافة عنصر أسطمبة افتراضي لو جدول template_items فارغ
    c.execute("SELECT COUNT(*) FROM template_items")
    if c.fetchone()[0] == 0:
        # الحصول على ID الدواء الافتراضي والأسطمبة الافتراضية
        c.execute("SELECT id FROM medicines WHERE name = ?", ("دواء تجريبي",))
        medicine_id = c.fetchone()[0]
        c.execute("SELECT id FROM templates WHERE name = ?", ("أسطمبة تجريبية",))
        template_id = c.fetchone()[0]
        if medicine_id and template_id:
            c.execute("INSERT INTO template_items (template_id, medicine_id, dosage, duration, instructions) VALUES (?, ?, ?, ?, ?)",
                      (template_id, medicine_id, "1 قرص", "يومياً", "بعد الأكل"))

    # جدول إعدادات العيادة
    c.execute("""
        CREATE TABLE IF NOT EXISTS clinic_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_name TEXT,
            clinic_address TEXT,
            phone_numbers TEXT,
            logo_path TEXT,
            signature_path TEXT
        )
    """)

    # جدول إعدادات الطباعة
    c.execute("""
        CREATE TABLE IF NOT EXISTS print_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            logo_position TEXT,
            print_template_style TEXT
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    update_database()