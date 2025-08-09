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
        layout.setContentsMargins(20, 20, 20, 20) # Reduced margins
        layout.setSpacing(10) # Reduced spacing

        self.title_label = QLabel("تسجيل الدخول")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        self.title_label.setStyleSheet("color: #2E86DE;")

        # Clinic Logo
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedSize(100, 100) # Adjusted size
        self.logo_label.setScaledContents(True)
        
        settings_model = SettingsModel()
        clinic_settings = settings_model.get_clinic_settings()
        # Check if clinic_settings is a dictionary and contains 'logo_path'
        if isinstance(clinic_settings, dict) and clinic_settings.get("logo_path"):
            pixmap = QPixmap(clinic_settings["logo_path"])
            if not pixmap.isNull():
                self.logo_label.setPixmap(pixmap)
            else:
                self.logo_label.setText("لا يوجد شعار")
        else:
            self.logo_label.setText("لا يوجد شعار")

        layout.addWidget(self.logo_label)
        layout.addSpacing(5) # Reduced spacing


        username_label = QLabel("اسم المستخدم")
        username_label.setAlignment(Qt.AlignCenter)
        username_label.setStyleSheet("font-size: 14px; color: #555;")

        self.user_combo = QComboBox()
        self.user_combo.setEditable(True)
        self.user_combo.lineEdit().setReadOnly(True)
        self.user_combo.lineEdit().setAlignment(Qt.AlignCenter)
        self.user_combo.setMinimumHeight(35) # Adjusted height
        self.user_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 8px;
                font-size: 14px;
                color: #333;
                background-color: white;
            }
            QComboBox QAbstractItemView {
                font-size: 13px;
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
        self.password_input.setMinimumHeight(35) # Adjusted height
        self.password_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 8px;
                font-size: 14px;
                color: #333;
            }
        """)

        self.login_button = QPushButton("تسجيل الدخول")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setMinimumHeight(40) # Adjusted height
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #2E86DE;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 8px;
                font-size: 15px;
            }
            QPushButton:hover {
                background-color: #1B4F72;
            }
        """)

        # Re-initialize layout to apply new margins/spacing
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20) # Reduced margins
        layout.setSpacing(10) # Reduced spacing
        layout.addWidget(self.title_label)
        layout.addSpacing(5) # Reduced spacing
        layout.addWidget(self.logo_label)
        layout.addSpacing(5) # Reduced spacing
        layout.addWidget(username_label)
        layout.addWidget(self.user_combo)
        layout.addWidget(password_label)
        layout.addWidget(self.password_input)
        layout.addSpacing(10) # Reduced spacing
        layout.addWidget(self.login_button)
        
        # Contact info
        contact_label = QLabel("للتواصل معنا: 01550788744")
        contact_label.setAlignment(Qt.AlignCenter)
        contact_label.setStyleSheet("font-size: 11px; color: #7f8c8d; margin-top: 5px;") # Adjusted font size and margin
        layout.addWidget(contact_label)
        
        # Copyright
        copyright_label = QLabel("جميع الحقوق محفوظة لدى د.أحمد جمال")
        copyright_label.setAlignment(Qt.AlignCenter)
        copyright_label.setStyleSheet("font-size: 9px; color: #95a5a6; margin-top: 2px;") # Adjusted font size and margin
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




