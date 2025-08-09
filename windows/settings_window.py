from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QMessageBox,
    QFormLayout, QDialog, QDialogButtonBox, QFileDialog, QComboBox, QGroupBox
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
        layout.setContentsMargins(10, 10, 10, 10) # Reduced margins
        layout.setSpacing(10) # Reduced spacing

        title = QLabel("إدارة المستخدمين")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;") # Reduced margin-bottom
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
        layout.setContentsMargins(10, 10, 10, 10) # Reduced margins
        layout.setSpacing(10) # Reduced spacing

        title = QLabel("بيانات العيادة")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;") # Reduced margin-bottom
        layout.addWidget(title)

        form_layout = QFormLayout()

        self.doctor_name_input = QLineEdit()
        self.clinic_address_input = QLineEdit()
        self.phone_numbers_input = QLineEdit()
        self.clinic_email_input = QLineEdit()
        self.clinic_website_input = QLineEdit()
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
        form_layout.addRow("البريد الإلكتروني:", self.clinic_email_input)
        form_layout.addRow("الموقع الإلكتروني:", self.clinic_website_input)
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
            self.doctor_name_input.setText(settings.get("doctor_name", "") or "")
            self.clinic_address_input.setText(settings.get("clinic_address", "") or "")
            self.phone_numbers_input.setText(settings.get("phone_numbers", "") or "")
            self.clinic_email_input.setText(settings.get("clinic_email", "") or "")
            self.clinic_website_input.setText(settings.get("clinic_website", "") or "")
            self.logo_path_input.setText(settings.get("logo_path", "") or "")
            self.signature_path_input.setText(settings.get("signature_path", "") or "")

    def save_settings(self):
        doctor_name = self.doctor_name_input.text().strip()
        clinic_address = self.clinic_address_input.text().strip()
        phone_numbers = self.phone_numbers_input.text().strip()
        clinic_email = self.clinic_email_input.text().strip()
        clinic_website = self.clinic_website_input.text().strip()
        logo_path = self.logo_path_input.text().strip()
        signature_path = self.signature_path_input.text().strip()

        if self.settings_model.save_clinic_settings(doctor_name, clinic_address, phone_numbers, logo_path, signature_path, clinic_email, clinic_website):
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
        layout.setContentsMargins(10, 10, 10, 10) # Reduced margins
        layout.setSpacing(10) # Reduced spacing

        title = QLabel("إعدادات الطباعة")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;") # Reduced margin-bottom
        layout.addWidget(title)

        form_layout = QFormLayout()

        self.logo_position_combo = QComboBox()
        self.logo_position_combo.addItems(["أعلى اليمين", "أعلى الوسط", "أعلى اليسار"])

        self.print_template_combo = QComboBox()
        # This combo box will be populated dynamically with print templates
        self.print_template_combo.currentIndexChanged.connect(self.on_template_selected)

        form_layout.addRow("موضع الشعار:", self.logo_position_combo)
        form_layout.addRow("نموذج الطباعة:", self.print_template_combo)

        layout.addLayout(form_layout)

        # Template Management Section
        template_group_box = QGroupBox("إدارة قوالب الطباعة")
        template_layout = QVBoxLayout()

        add_template_layout = QHBoxLayout()
        self.template_name_input = QLineEdit()
        self.template_name_input.setPlaceholderText("اسم القالب")
        self.template_path_input = QLineEdit()
        self.template_path_input.setReadOnly(True)
        template_browse_btn = QPushButton("استعراض...")
        template_browse_btn.clicked.connect(lambda: self.browse_file(self.template_path_input, "Image Files (*.jpg *.jpeg *.png)"))
        add_template_btn = QPushButton("➕ إضافة قالب")
        add_template_btn.clicked.connect(self.add_print_template)

        add_template_layout.addWidget(self.template_name_input)
        add_template_layout.addWidget(self.template_path_input)
        add_template_layout.addWidget(template_browse_btn)
        add_template_layout.addWidget(add_template_btn)
        template_layout.addLayout(add_template_layout)

        self.templates_table = QTableWidget()
        self.templates_table.setColumnCount(3)
        self.templates_table.setHorizontalHeaderLabels(["الرقم", "الاسم", "الإجراءات"])
        self.templates_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.templates_table.setSelectionBehavior(QTableWidget.SelectRows)
        template_layout.addWidget(self.templates_table)

        self.template_preview_label = QLabel("معاينة القالب")
        self.template_preview_label.setAlignment(Qt.AlignCenter)
        self.template_preview_label.setFixedSize(300, 400) # Fixed size for preview
        self.template_preview_label.setStyleSheet("border: 1px solid #ccc; background-color: #f0f0f0;")
        template_layout.addWidget(self.template_preview_label)

        template_group_box.setLayout(template_layout)
        layout.addWidget(template_group_box)

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
        self.load_print_templates()

    def browse_file(self, line_edit, file_filter):
        file_path, _ = QFileDialog.getOpenFileName(self, "اختر ملف", "", file_filter)
        if file_path:
            line_edit.setText(file_path)

    def load_settings(self):
        settings = self.settings_model.get_print_settings()
        if settings:
            self.logo_position_combo.setCurrentText(settings.get("logo_position", "أعلى اليمين") or "أعلى اليمين")
            # Set selected template in combo box
            selected_template_id = settings.get("selected_template_id")
            if selected_template_id:
                index = self.print_template_combo.findData(selected_template_id)
                if index != -1:
                    self.print_template_combo.setCurrentIndex(index)
            self.on_template_selected(self.print_template_combo.currentIndex()) # Load preview for current template

    def save_settings(self):
        logo_position = self.logo_position_combo.currentText()
        selected_template_id = self.print_template_combo.currentData()

        if self.settings_model.save_print_settings(logo_position, selected_template_id):
            QMessageBox.information(self, "نجح", "تم حفظ إعدادات الطباعة بنجاح!")
        else:
            QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء حفظ البيانات.")

    def load_print_templates(self):
        self.print_template_combo.clear()
        self.print_template_combo.addItem("لا يوجد قالب", None)
        self.templates_table.setRowCount(0)
        templates = self.settings_model.get_all_print_templates()
        for template in templates:
            # Populate combo box
            self.print_template_combo.addItem(template["name"], template["id"])

            # Populate table
            row_position = self.templates_table.rowCount()
            self.templates_table.insertRow(row_position)
            self.templates_table.setItem(row_position, 0, QTableWidgetItem(str(template["id"])))
            self.templates_table.setItem(row_position, 1, QTableWidgetItem(template["name"]))

            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)

            delete_btn = QPushButton("حذف")
            delete_btn.clicked.connect(lambda _, t_id=template["id"]: self.delete_print_template(t_id))
            actions_layout.addWidget(delete_btn)

            actions_widget.setLayout(actions_layout)
            self.templates_table.setCellWidget(row_position, 2, actions_widget)

    def add_print_template(self):
        name = self.template_name_input.text().strip()
        path = self.template_path_input.text().strip()

        if not name or not path:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم ومسار القالب.")
            return
        
        if not os.path.exists(path):
            QMessageBox.warning(self, "خطأ", "مسار القالب غير صحيح.")
            return

        if self.settings_model.add_print_template(name, path):
            QMessageBox.information(self, "نجح", "تم إضافة القالب بنجاح!")
            self.template_name_input.clear()
            self.template_path_input.clear()
            self.load_print_templates()
        else:
            QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء إضافة القالب.")

    def delete_print_template(self, template_id):
        reply = QMessageBox.question(self, "تأكيد الحذف", "هل أنت متأكد من حذف هذا القالب؟",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.settings_model.delete_print_template(template_id):
                QMessageBox.information(self, "نجح", "تم حذف القالب بنجاح!")
                self.load_print_templates()
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء حذف القالب.")

    def on_template_selected(self, index):
        template_id = self.print_template_combo.itemData(index)
        if template_id:
            template = self.settings_model.get_print_template_by_id(template_id)
            if template and os.path.exists(template["path"]):
                pixmap = QPixmap(template["path"])
                if not pixmap.isNull():
                    self.template_preview_label.setPixmap(pixmap.scaled(self.template_preview_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
                else:
                    self.template_preview_label.setText("فشل تحميل الصورة")
            else:
                self.template_preview_label.setText("مسار القالب غير صحيح أو غير موجود")
        else:
            self.template_preview_label.setText("معاينة القالب")


class SettingsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10) # Reduced margins
        main_layout.setSpacing(10) # Reduced spacing

        # Left Panel (Navigation)
        left_panel = QVBoxLayout()
        left_panel.setContentsMargins(0, 0, 5, 0) # Reduced right margin

        self.user_management_btn = QPushButton("إدارة المستخدمين")
        self.clinic_settings_btn = QPushButton("بيانات العيادة")
        self.print_settings_btn = QPushButton("إعدادات الطباعة")

        self.user_management_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        self.clinic_settings_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        self.print_settings_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))

        left_panel.addWidget(self.user_management_btn)
        left_panel.addWidget(self.clinic_settings_btn)
        left_panel.addWidget(self.print_settings_btn)
        left_panel.addStretch(1)

        main_layout.addLayout(left_panel)

        # Right Panel (Content)
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setContentsMargins(5, 0, 0, 0) # Reduced left margin

        self.user_management_page = UserManagementPage()
        self.clinic_settings_page = ClinicSettingsPage()
        self.print_settings_page = PrintSettingsPage()

        self.stacked_widget.addWidget(self.user_management_page)
        self.stacked_widget.addWidget(self.clinic_settings_page)
        self.stacked_widget.addWidget(self.print_settings_page)

        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)

        # Set initial page
        self.stacked_widget.setCurrentIndex(0)




