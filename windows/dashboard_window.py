from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QStackedWidget, QLabel, QPushButton, QDialog, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont
from windows.top_header import TopHeader
from windows.settings_window import SettingsWindow # Corrected import
from windows.patients_window import PatientsWindow
from windows.medicines_window import MedicinesWindow
from windows.new_prescription_window import NewPrescriptionWindow
from windows.prescriptions_window import PrescriptionsWindow
from windows.home_window import HomePage
from windows.templates_window import TemplatesWindow

class LogoutDialog(QDialog):
    confirmed = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("تأكيد الخروج")
        self.setModal(True)
        self.setFixedSize(300, 160)

        self.layout = QVBoxLayout()
        self.label = QLabel("هل أنت متأكد من تسجيل الخروج؟\nسيتم تسجيل الخروج تلقائيًا خلال 10 ثوانٍ")
        self.label.setFont(QFont("Noto Sans Arabic", 10))
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        self.timer_label = QLabel("10")
        self.timer_label.setFont(QFont("Noto Sans Arabic", 14, QFont.Bold))
        self.timer_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.timer_label)

        btn_layout = QHBoxLayout()
        self.yes_btn = QPushButton("نعم")
        self.no_btn = QPushButton("لا")
        self.yes_btn.setFont(QFont("Noto Sans Arabic", 10))
        self.no_btn.setFont(QFont("Noto Sans Arabic", 10))
        btn_layout.addWidget(self.yes_btn)
        btn_layout.addWidget(self.no_btn)
        self.layout.addLayout(btn_layout)

        self.setLayout(self.layout)

        self.counter = 10
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

        self.yes_btn.clicked.connect(self.accept)
        self.no_btn.clicked.connect(self.reject)

    def update_timer(self):
        self.counter -= 1
        self.timer_label.setText(str(self.counter))
        if self.counter == 0:
            self.accept()

class DashboardWindow(QMainWindow):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id

        self.setWindowTitle("Electronic Prescription")
        self.setGeometry(100, 100, 1200, 700)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        self.layout = QVBoxLayout(central_widget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0) # Reduce spacing between header and content

        self.header = TopHeader(active="new_rx")
        self.header.setFixedHeight(60) # Reduce header height
        self.layout.addWidget(self.header)

        self.pages = QStackedWidget()
        self.layout.addWidget(self.pages)

        self.settings_page = SettingsWindow() # Removed current_user_id

        # self.pages.addWidget(QWidget())  # home
        self.new_prescription_page = NewPrescriptionWindow(self.user_id)
        self.templates_page = TemplatesWindow()
        self.pages.addWidget(self.new_prescription_page)  # new_rx
        self.pages.addWidget(PrescriptionsWindow())  # view_rx
        self.medicines_page = MedicinesWindow()
        self.pages.addWidget(self.medicines_page)  # meds
        self.pages.addWidget(PatientsWindow())  # patients
        self.pages.addWidget(self.settings_page)  # settings
        self.pages.addWidget(self.templates_page) # templates

        # Connect template_changed signal to new_prescription_page
        self.templates_page.template_changed.connect(self.new_prescription_page.load_templates_to_combo)
        # Connect medicine_changed signal to templates_page
        self.medicines_page.medicine_changed.connect(self.templates_page.load_medicines_to_combo)

        self.page_map = {
            # "home": 0,
            "new_rx": 0, # new_rx is now index 0
            "view_rx": 1,
            "meds": 2,
            "patients": 3,
            "settings": 4,
            "templates": 5
        }

        self.header.navigate.connect(self.switch_page)
        self.header.logout.connect(self.confirm_logout)

        # Set initial page to new_rx
        self.pages.setCurrentIndex(self.page_map["new_rx"])

    def confirm_logout(self):
        dialog = LogoutDialog()
        result = dialog.exec_()
        if result == QDialog.Accepted:
            self.handle_logout()

    def handle_logout(self):
        from windows.login_window import LoginWindow
        self.close()
        self.login_window = LoginWindow()
        self.login_window.show()


    def switch_page(self, page_key):
        if page_key in self.page_map:
            # Update header
            self.header.setParent(None)
            self.header = TopHeader(active=page_key)
            self.header.navigate.connect(self.switch_page)
            self.header.logout.connect(self.confirm_logout)
            self.layout.insertWidget(0, self.header)

            # If switching to new_rx page, reload its data
            if page_key == "new_rx":
                new_rx_page = self.pages.widget(self.page_map["new_rx"])
                new_rx_page.load_patients_to_combo()
                new_rx_page.load_medicines_to_combo()

            self.pages.setCurrentIndex(self.page_map[page_key])






