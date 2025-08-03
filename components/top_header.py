from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QCursor

class TopHeader(QWidget):
    navigate = pyqtSignal(str)
    logout = pyqtSignal()

    def __init__(self, active="home"):
        super().__init__()
        self.active = active
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(30)
        self.setStyleSheet("background-color: #f0f0f0; padding: 10px;")

        self.buttons = {}

        items = [
            ("home", "🏠", "الرئيسية"),
            ("new_rx", "📝", "روشتة جديدة"),
            ("view_rx", "📄", "عرض الروشتات"),
            ("meds", "💊", "الأدوية"),
            ("patients", "🧑‍⚕️", "المرضى"),
            ("settings", "⚙️", "الإعدادات"),
            ("logout", "🚪", "خروج")
        ]

        for key, icon, label in items:
            btn = QPushButton(f"{icon}\n{label}")
            btn.setCursor(QCursor(Qt.PointingHandCursor))
            btn.setFixedSize(90, 55)
            btn.setStyleSheet(self.get_button_style(key == self.active))
            if key == "logout":
                btn.clicked.connect(self.logout.emit)
            else:
                btn.clicked.connect(lambda _, k=key: self.navigate.emit(k))
            layout.addWidget(btn)
            self.buttons[key] = btn

        self.setLayout(layout)

    def get_button_style(self, active=False):
        if active:
            return """
                QPushButton {
                    background-color: #d0e7ff;
                    border: 1px solid #007acc;
                    border-radius: 10px;
                    font-weight: bold;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: #ffffff;
                    border: 1px solid #ccc;
                    border-radius: 10px;
                }
                QPushButton:hover {
                    background-color: #e6f2ff;
                }
            """