# Login UI generated from Qt Designer
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

class LoginUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - ePrescription")
        self.setFixedSize(350, 200)
        self.init_ui()

    def init_ui(self):
        # Title Label
        self.title_label = QLabel("Electronic Prescription Login")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold;")

        # Username Field
        self.username_label = QLabel("Username:")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter your username")

        # Password Field
        self.password_label = QLabel("Password:")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText("Enter your password")

        # Login Button
        self.login_button = QPushButton("Login")

        # Layouts
        form_layout = QVBoxLayout()
        form_layout.addWidget(self.title_label)
        form_layout.addSpacing(10)

        form_layout.addWidget(self.username_label)
        form_layout.addWidget(self.username_input)

        form_layout.addWidget(self.password_label)
        form_layout.addWidget(self.password_input)

        form_layout.addSpacing(10)
        form_layout.addWidget(self.login_button)

        self.setLayout(form_layout)
