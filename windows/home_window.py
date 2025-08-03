from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QGridLayout
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from models.prescription_model import PrescriptionModel

class HomePage(QWidget):
    def __init__(self):
        super().__init__()
        self.prescription_model = PrescriptionModel()
        self.init_ui()
        self.load_statistics()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        title = QLabel("لوحة التحكم")
        title.setFont(QFont("Arial", 24, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)

        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)

        # Today's Prescriptions Card
        self.today_rx_label = QLabel("0")
        self.today_rx_label.setFont(QFont("Arial", 36, QFont.Bold))
        self.today_rx_label.setAlignment(Qt.AlignCenter)
        self.today_rx_label.setStyleSheet("color: #27ae60;")

        today_rx_title = QLabel("روشتات اليوم")
        today_rx_title.setFont(QFont("Arial", 16))
        today_rx_title.setAlignment(Qt.AlignCenter)
        today_rx_title.setStyleSheet("color: #34495e;")

        today_rx_card = QVBoxLayout()
        today_rx_card.addWidget(self.today_rx_label)
        today_rx_card.addWidget(today_rx_title)
        today_rx_card_widget = QWidget()
        today_rx_card_widget.setLayout(today_rx_card)
        today_rx_card_widget.setStyleSheet("""
            QWidget {
                background-color: #ecf0f1;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        stats_grid.addWidget(today_rx_card_widget, 0, 0)

        # Add more stats cards here if needed

        layout.addLayout(stats_grid)
        layout.addStretch(1)
        self.setLayout(layout)

    def load_statistics(self):
        today = QDate.currentDate().toString("yyyy-MM-dd")
        start_of_day = f"{today} 00:00:00"
        end_of_day = f"{today} 23:59:59"
        
        prescriptions_today = self.prescription_model.search_prescriptions(
            start_date=start_of_day, end_date=end_of_day
        )
        self.today_rx_label.setText(str(len(prescriptions_today)))


