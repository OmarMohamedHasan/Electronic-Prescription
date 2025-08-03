from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QListWidget, QLineEdit,
    QHBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# قاعدة بيانات مؤقتة للتجربة
USERS = [
    {"id": 1000, "name": "Admin", "username": "admin", "password": "0000"},
    {"id": 1001, "name": "د. محمد", "username": "drmohamed", "password": "1234"}
]

class UserManagementPage(QWidget):
    def __init__(self, go_back_callback):
        super().__init__()
        self.go_back_callback = go_back_callback
        self.mode = "list"  # or "form"
        self.selected_user_id = None
        self.setup_ui()

    def setup_ui(self):
        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setSpacing(10)
        self.setLayout(self.layout)
        self.show_user_list()

    def clear_layout(self):
        while self.layout.count():
            child = self.layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def show_user_list(self):
        self.mode = "list"
        self.clear_layout()

        title = QLabel("مستخدمي البرنامج")
        title.setFont(QFont("Segoe UI", 14))
        title.setAlignment(Qt.AlignCenter)

        self.user_list = QListWidget()
        for user in USERS:
            self.user_list.addItem(f"{user['name']} ({user['username']})")

        self.user_list.itemDoubleClicked.connect(self.edit_selected_user)

        btn_layout = QHBoxLayout()

        add_user_btn = QPushButton("➕ إضافة مستخدم جديد")
        add_user_btn.clicked.connect(self.show_add_form)

        delete_user_btn = QPushButton("🗑️ حذف المستخدم المحدد")
        delete_user_btn.clicked.connect(self.delete_selected_user)

        back_btn = QPushButton("⬅ العودة")
        back_btn.clicked.connect(self.go_back_callback)

        btn_layout.addWidget(add_user_btn)
        btn_layout.addWidget(delete_user_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(back_btn)

        self.layout.addWidget(title)
        self.layout.addWidget(self.user_list)
        self.layout.addLayout(btn_layout)

    def show_add_form(self, user=None):
        self.mode = "form"
        self.clear_layout()

        is_edit = user is not None
        title = QLabel("تعديل مستخدم" if is_edit else "إنشاء مستخدم جديد")
        title.setFont(QFont("Segoe UI", 14))
        title.setAlignment(Qt.AlignCenter)

        self.name_input = QLineEdit(user['name'] if is_edit else "")
        self.name_input.setPlaceholderText("الاسم")

        self.username_input = QLineEdit(user['username'] if is_edit else "")
        self.username_input.setPlaceholderText("اسم المستخدم")

        self.password_input = QLineEdit(user['password'] if is_edit else "")
        self.password_input.setPlaceholderText("كلمة السر")
        self.password_input.setEchoMode(QLineEdit.Password)

        save_btn = QPushButton("💾 حفظ")
        save_btn.clicked.connect(lambda: self.save_user(user['id'] if is_edit else None))

        cancel_btn = QPushButton("إلغاء")
        cancel_btn.clicked.connect(self.show_user_list)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)

        self.layout.addWidget(title)
        self.layout.addWidget(self.name_input)
        self.layout.addWidget(self.username_input)
        self.layout.addWidget(self.password_input)
        self.layout.addLayout(btn_layout)

    def save_user(self, user_id=None):
        name = self.name_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not name or not username or not password:
            QMessageBox.warning(self, "تنبيه", "الرجاء تعبئة جميع الحقول.")
            return

        if user_id is None:
            new_id = max(u['id'] for u in USERS) + 1
            USERS.append({
                "id": new_id,
                "name": name,
                "username": username,
                "password": password
            })
        else:
            for u in USERS:
                if u["id"] == user_id:
                    u["name"] = name
                    u["username"] = username
                    u["password"] = password
                    break

        self.show_user_list()

    def delete_selected_user(self):
        current_row = self.user_list.currentRow()
        if current_row < 0:
            QMessageBox.information(self, "تنبيه", "يرجى اختيار مستخدم لحذفه.")
            return

        user = USERS[current_row]
        if user["id"] == 1000:
            QMessageBox.warning(self, "خطأ", "لا يمكن حذف حساب الأدمن.")
            return

        confirm = QMessageBox.question(self, "تأكيد", f"هل تريد حذف المستخدم {user['name']}؟")
        if confirm == QMessageBox.Yes:
            USERS.remove(user)
            self.show_user_list()

    def edit_selected_user(self):
        current_row = self.user_list.currentRow()
        if current_row < 0:
            return
        user = USERS[current_row]
        self.show_add_form(user)