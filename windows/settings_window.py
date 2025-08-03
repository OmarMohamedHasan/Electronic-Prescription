from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QMessageBox,
    QFormLayout, QDialog, QDialogButtonBox, QFileDialog, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap
from models.settings_model import SettingsModel
from werkzeug.security import generate_password_hash, check_password_hash
import os

class AddUserDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة مستخدم جديد" if not user_data else "تعديل مستخدم")
        self.setFixedSize(400, 250)
        self.user_data = user_data
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("اسم المستخدم")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("الاسم الكامل")
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("كلمة المرور")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setPlaceholderText("تأكيد كلمة المرور")
        self.confirm_password_input.setEchoMode(QLineEdit.Password)

        if self.user_data:
            self.username_input.setText(self.user_data[1])
            self.name_input.setText(self.user_data[2])
            self.password_input.setPlaceholderText("اترك فارغًا لعدم التغيير")
            self.confirm_password_input.setPlaceholderText("اترك فارغًا لعدم التغيير")

        layout.addRow("اسم المستخدم:", self.username_input)
        layout.addRow("الاسم:", self.name_input)
        layout.addRow("كلمة المرور:", self.password_input)
        layout.addRow("تأكيد كلمة المرور:", self.confirm_password_input)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def get_data(self):
        return {
            "username": self.username_input.text().strip(),
            "name": self.name_input.text().strip(),
            "password": self.password_input.text().strip(),
            "confirm_password": self.confirm_password_input.text().strip()
        }

class UserManagementPage(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_model = SettingsModel()
        self.init_ui()
        self.load_users()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("إدارة المستخدمين")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)

        add_user_btn = QPushButton("➕ إضافة مستخدم جديد")
        add_user_btn.clicked.connect(self.add_user)
        add_user_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
            QPushButton:pressed {
                background-color: #229954;
            }
        """)
        layout.addWidget(add_user_btn, alignment=Qt.AlignRight)

        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["الرقم", "اسم المستخدم", "الاسم", "الإجراءات"])
        self.users_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.users_table)

        self.setLayout(layout)

    def load_users(self):
        users = self.settings_model.get_all_users()
        self.users_table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.users_table.setItem(row, 0, QTableWidgetItem(str(user[0])))
            self.users_table.setItem(row, 1, QTableWidgetItem(user[1]))
            self.users_table.setItem(row, 2, QTableWidgetItem(user[2] or ""))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)

            edit_btn = QPushButton("تعديل")
            edit_btn.clicked.connect(lambda _, u=user: self.edit_user(u))
            actions_layout.addWidget(edit_btn)

            delete_btn = QPushButton("حذف")
            delete_btn.clicked.connect(lambda _, uid=user[0]: self.delete_user(uid))
            actions_layout.addWidget(delete_btn)

            actions_widget.setLayout(actions_layout)
            self.users_table.setCellWidget(row, 3, actions_widget)

    def add_user(self):
        dialog = AddUserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["username"] or not data["name"] or not data["password"]:
                QMessageBox.warning(self, "خطأ", "جميع الحقول مطلوبة.")
                return
            if data["password"] != data["confirm_password"]:
                QMessageBox.warning(self, "خطأ", "كلمتا المرور غير متطابقتين.")
                return
            
            if self.settings_model.add_user(data["username"], data["password"], data["name"]):
                QMessageBox.information(self, "نجح", "تم إضافة المستخدم بنجاح!")
                self.load_users()
            else:
                QMessageBox.warning(self, "خطأ", "اسم المستخدم موجود بالفعل.")

    def edit_user(self, user_data):
        dialog = AddUserDialog(self, user_data=user_data)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["username"] or not data["name"]:
                QMessageBox.warning(self, "خطأ", "اسم المستخدم والاسم الكامل مطلوبان.")
                return
            
            password_to_update = None
            if data["password"]:
                if data["password"] != data["confirm_password"]:
                    QMessageBox.warning(self, "خطأ", "كلمتا المرور غير متطابقتين.")
                    return
                password_to_update = data["password"]

            if self.settings_model.update_user(user_data[0], data["username"], data["name"], password_to_update):
                QMessageBox.information(self, "نجح", "تم تحديث المستخدم بنجاح!")
                self.load_users()
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء تحديث المستخدم.")

    def delete_user(self, user_id):
        reply = QMessageBox.question(self, "تأكيد الحذف", "هل أنت متأكد من حذف هذا المستخدم؟",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.settings_model.delete_user(user_id):
                QMessageBox.information(self, "نجح", "تم حذف المستخدم بنجاح!")
                self.load_users()
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء حذف المستخدم.")

class ClinicSettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_model = SettingsModel()
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("بيانات العيادة")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)

        form_layout = QFormLayout()

        self.doctor_name_input = QLineEdit()
        self.clinic_address_input = QLineEdit()
        self.phone_numbers_input = QLineEdit()
        self.logo_path_input = QLineEdit()
        self.logo_path_input.setReadOnly(True)
        self.signature_path_input = QLineEdit()
        self.signature_path_input.setReadOnly(True)

        logo_browse_btn = QPushButton("استعراض...")
        logo_browse_btn.clicked.connect(lambda: self.browse_file(self.logo_path_input, "Image Files (*.png *.jpg *.jpeg)"))
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.logo_path_input)
        logo_layout.addWidget(logo_browse_btn)

        signature_browse_btn = QPushButton("استعراض...")
        signature_browse_btn.clicked.connect(lambda: self.browse_file(self.signature_path_input, "Image Files (*.png *.jpg *.jpeg)"))
        signature_layout = QHBoxLayout()
        signature_layout.addWidget(self.signature_path_input)
        signature_layout.addWidget(signature_browse_btn)

        form_layout.addRow("اسم الطبيب:", self.doctor_name_input)
        form_layout.addRow("عنوان العيادة:", self.clinic_address_input)
        form_layout.addRow("أرقام التواصل:", self.phone_numbers_input)
        form_layout.addRow("شعار العيادة:", logo_layout)
        form_layout.addRow("التوقيع الإلكتروني:", signature_layout)

        layout.addLayout(form_layout)

        save_btn = QPushButton("حفظ بيانات العيادة")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2271b3;
            }
        """)
        layout.addWidget(save_btn, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def browse_file(self, line_edit, file_filter):
        file_path, _ = QFileDialog.getOpenFileName(self, "اختر ملف", "", file_filter)
        if file_path:
            line_edit.setText(file_path)

    def load_settings(self):
        settings = self.settings_model.get_clinic_settings()
        if settings:
            self.doctor_name_input.setText(settings[0] or "")
            self.clinic_address_input.setText(settings[1] or "")
            self.phone_numbers_input.setText(settings[2] or "")
            self.logo_path_input.setText(settings[3] or "")
            self.signature_path_input.setText(settings[4] or "")

    def save_settings(self):
        doctor_name = self.doctor_name_input.text().strip()
        clinic_address = self.clinic_address_input.text().strip()
        phone_numbers = self.phone_numbers_input.text().strip()
        logo_path = self.logo_path_input.text().strip()
        signature_path = self.signature_path_input.text().strip()

        if self.settings_model.save_clinic_settings(doctor_name, clinic_address, phone_numbers, logo_path, signature_path):
            QMessageBox.information(self, "نجح", "تم حفظ بيانات العيادة بنجاح!")
        else:
            QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء حفظ البيانات.")

class PrintSettingsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.settings_model = SettingsModel()
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel("إعدادات الطباعة")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)

        form_layout = QFormLayout()

        self.logo_position_combo = QComboBox()
        self.logo_position_combo.addItems(["أعلى اليمين", "أعلى الوسط", "أعلى اليسار"])

        self.print_template_combo = QComboBox()
        self.print_template_combo.addItems(["النموذج الافتراضي 1", "النموذج 2 (بدون توقيع)"])

        form_layout.addRow("موضع الشعار:", self.logo_position_combo)
        form_layout.addRow("نموذج الطباعة:", self.print_template_combo)

        layout.addLayout(form_layout)

        save_btn = QPushButton("حفظ إعدادات الطباعة")
        save_btn.clicked.connect(self.save_settings)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2271b3;
            }
        """)
        layout.addWidget(save_btn, alignment=Qt.AlignRight)

        self.setLayout(layout)

    def load_settings(self):
        settings = self.settings_model.get_print_settings()
        if settings:
            self.logo_position_combo.setCurrentText(settings[0] or "أعلى اليمين")
            self.print_template_combo.setCurrentText(settings[1] or "النموذج الافتراضي 1")

    def save_settings(self):
        logo_position = self.logo_position_combo.currentText()
        print_template_style = self.print_template_combo.currentText()

        if self.settings_model.save_print_settings(logo_position, print_template_style):
            QMessageBox.information(self, "نجح", "تم حفظ إعدادات الطباعة بنجاح!")
        else:
            QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء حفظ البيانات.")

class SettingsPage(QWidget):
    def __init__(self, current_user_id=None):
        super().__init__()
        self.current_user_id = current_user_id
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header for navigation within settings
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(20, 10, 20, 10)
        header_layout.setSpacing(10)

        self.user_management_btn = QPushButton("إدارة المستخدمين")
        self.user_management_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.user_management_page))
        self.user_management_btn.setStyleSheet("font-size: 16px; padding: 10px; border-radius: 5px;")
        header_layout.addWidget(self.user_management_btn)

        self.clinic_settings_btn = QPushButton("بيانات العيادة")
        self.clinic_settings_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.clinic_settings_page))
        self.clinic_settings_btn.setStyleSheet("font-size: 16px; padding: 10px; border-radius: 5px;")
        header_layout.addWidget(self.clinic_settings_btn)

        self.print_settings_btn = QPushButton("إعدادات الطباعة")
        self.print_settings_btn.clicked.connect(lambda: self.pages.setCurrentWidget(self.print_settings_page))
        self.print_settings_btn.setStyleSheet("font-size: 16px; padding: 10px; border-radius: 5px;")
        header_layout.addWidget(self.print_settings_btn)

        header_layout.addStretch(1)
        main_layout.addLayout(header_layout)

        # Stacked widget for different settings pages
        self.pages = QStackedWidget()

        self.user_management_page = UserManagementPage()
        self.clinic_settings_page = ClinicSettingsPage()
        self.print_settings_page = PrintSettingsPage()

        self.pages.addWidget(self.user_management_page)
        self.pages.addWidget(self.clinic_settings_page)
        self.pages.addWidget(self.print_settings_page)

        main_layout.addWidget(self.pages)
        self.setLayout(main_layout)

        # Set initial page
        self.pages.setCurrentWidget(self.user_management_page)


