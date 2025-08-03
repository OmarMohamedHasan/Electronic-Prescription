from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt5.QtCore import pyqtSignal, Qt

class TopHeader(QWidget):
    navigate = pyqtSignal(str)
    logout = pyqtSignal()

    def __init__(self, active="home"):
        super().__init__()
        self.setFixedHeight(80)
        self.setStyleSheet("""
            QPushButton {
                border: none;
                font-size: 16px;
                color: #444;
                background-color: transparent;
            }
            QPushButton:hover {
                color: #007acc;
            }
            QPushButton:checked {
                color: #007acc;
                font-weight: bold;
                text-decoration: underline;
            }
        """)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 10, 20, 0)
        layout.setSpacing(40)

        self.buttons = {}

        items = {
            "new_rx": "📝 روشتة جديدة",
            "view_rx": "📄 عرض الروشتات",
            "meds": "💊 الأدوية",
            "patients": "👥 المرضى",
            "templates": "🖨️ أسطمبة الأدوية",
            "settings": "⚙️ الإعدادات",
            "logout": "🚪 تسجيل الخروج"
        }

        for key, label in items.items():
            btn = QPushButton(label)
            btn.setCheckable(True)
            if key == active:
                btn.setChecked(True)

            if key == "logout":
                btn.clicked.connect(self.logout.emit)
            else:
                btn.clicked.connect(lambda _, k=key: self.navigate.emit(k))

            self.buttons[key] = btn
            layout.addWidget(btn, alignment=Qt.AlignTop)