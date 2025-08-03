from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from models.settings_model import SettingsModel
import sqlite3
import os

from windows.dashboard_window import DashboardWindow

DB_PATH = os.path.join(os.path.dirname(__file__), "../database/app.db")
MASTER_PASSWORD = "Zccz93!@#"  # كلمة السر العامة


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("تسجيل الدخول - برنامج الروشتة")
        self.setFixedSize(400, 350)
        self.setStyleSheet("background-color: #ffffff;")
        self.setup_ui()
        self.load_users()

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 30, 50, 30)
        layout.setSpacing(15)

        self.title_label = QLabel("تسجيل الدخول")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.title_label.setStyleSheet("color: #2E86DE;")

        # Clinic Logo
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedSize(150, 150) # Adjust size as needed
        self.logo_label.setScaledContents(True)
        
        settings_model = SettingsModel()
        clinic_settings = settings_model.get_clinic_settings()
        if clinic_settings and clinic_settings[3]: # clinic_settings[3] is logo_path
            pixmap = QPixmap(clinic_settings[3])
            if not pixmap.isNull():
                self.logo_label.setPixmap(pixmap)
            else:
                self.logo_label.setText("لا يوجد شعار")
        else:
            self.logo_label.setText("لا يوجد شعار")

        layout.addWidget(self.logo_label)
        layout.addSpacing(10)


        username_label = QLabel("اسم المستخدم")
        username_label.setAlignment(Qt.AlignCenter)
        username_label.setStyleSheet("font-size: 14px; color: #555;")

        self.user_combo = QComboBox()
        self.user_combo.setEditable(True)
        self.user_combo.lineEdit().setReadOnly(True)
        self.user_combo.lineEdit().setAlignment(Qt.AlignCenter)
        self.user_combo.setMinimumHeight(40)
        self.user_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 8px;
                font-size: 15px;
                color: #333;
                background-color: white;
            }
            QComboBox QAbstractItemView {
                font-size: 14px;
                selection-background-color: #2E86DE;
                selection-color: white;
            }
        """)

        password_label = QLabel("كلمة السر")
        password_label.setAlignment(Qt.AlignCenter)
        password_label.setStyleSheet("font-size: 14px; color: #555;")

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("كلمة السر")
        self.password_input.setAlignment(Qt.AlignCenter)
        self.password_input.returnPressed.connect(self.handle_login)
        self.password_input.setMinimumHeight(40)
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 1px solid #ccc;
                border-radius: 8px;
                font-size: 15px;
                color: #333;
            }
        """)

        self.login_button = QPushButton("تسجيل الدخول")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setMinimumHeight(45)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #2E86DE;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 8px;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #1B4F72;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(50, 30, 50, 30)
        layout.setSpacing(15)
        layout.addWidget(self.title_label)
        layout.addSpacing(10)
        layout.addWidget(username_label)
        layout.addWidget(self.user_combo)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addSpacing(15)
        layout.addWidget(self.login_button)
        
        # Contact info
        contact_label = QLabel("للتواصل معنا: 01550788744")
        contact_label.setAlignment(Qt.AlignCenter)
        contact_label.setStyleSheet("font-size: 12px; color: #7f8c8d; margin-top: 10px;")
        layout.addWidget(contact_label)
        
        # Copyright
        copyright_label = QLabel("جميع الحقوق محفوظة لدى د.أحمد جمال")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("font-size: 10px; color: #95a5a6; margin-top: 5px;")
        layout.addWidget(copyright_label)

        self.setLayout(layout)

    def load_users(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT username FROM users")
        users = [row[0] for row in c.fetchall()]
        conn.close()

        self.user_combo.clear()
        self.user_combo.addItems(users)

        if users:
            self.user_combo.setCurrentIndex(0)
            self.user_combo.lineEdit().setText(users[0])
            self.user_combo.lineEdit().setAlignment(Qt.AlignCenter)

    def handle_login(self):
        username = self.user_combo.currentText()
        password = self.password_input.text()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=?", (username,))
        user = c.fetchone()
        conn.close()

        if user and (user[2] == password or password == MASTER_PASSWORD):
            user_id = user[0]
            self.dashboard = DashboardWindow(user_id=user_id)
            self.dashboard.show()
            self.close()
        else:
            QMessageBox.warning(self, "خطأ", "اسم المستخدم أو كلمة المرور غير صحيحة.")
            self.password_input.clear()
            self.password_input.setFocus()


if __name__ == "__main__":
    app = QApplication([])
    window = LoginWindow()
    window.show()
    app.exec_()
