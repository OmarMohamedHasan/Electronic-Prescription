import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QMessageBox,
    QDateEdit, QComboBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
from models.prescription_model import PrescriptionModel
from datetime import datetime
from helpers.print_utility import generate_prescription_pdf
from models.settings_model import SettingsModel

class PrescriptionsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.prescription_model = PrescriptionModel()
        self.init_ui()
        self.load_prescriptions()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("عرض الروشتات")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)

        # Search and Filter section
        search_filter_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث باسم المريض أو رقم الهاتف...")
        self.search_input.returnPressed.connect(self.search_prescriptions)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        search_filter_layout.addWidget(self.search_input)

        self.date_filter_combo = QComboBox()
        self.date_filter_combo.addItems(["كل الروشتات", "روشتات اليوم", "روشتات الأسبوع", "روشتات الشهر", "تاريخ مخصص"])
        self.date_filter_combo.currentIndexChanged.connect(self.on_date_filter_changed)
        search_filter_layout.addWidget(self.date_filter_combo)

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())
        self.start_date_edit.hide() # Hidden by default
        search_filter_layout.addWidget(self.start_date_edit)

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.hide() # Hidden by default
        search_filter_layout.addWidget(self.end_date_edit)

        self.search_button = QPushButton("بحث")
        self.search_button.clicked.connect(self.search_prescriptions)
        self.search_button.setStyleSheet("""
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
        search_filter_layout.addWidget(self.search_button)

        layout.addLayout(search_filter_layout)

        # Prescriptions table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "الرقم", "التاريخ", "اسم المريض", "اسم الطبيب", "الإجراءات"
        ])
        
        # Set table style
        self.table.setStyleSheet("""
            QTableWidget {
                gridline-color: #bdc3c7;
                background-color: white;
                alternate-background-color: #f8f9fa;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        
        layout.addWidget(self.table)
        self.setLayout(layout)

    def on_date_filter_changed(self, index):
        if self.date_filter_combo.currentText() == "تاريخ مخصص":
            self.start_date_edit.show()
            self.end_date_edit.show()
        else:
            self.start_date_edit.hide()
            self.end_date_edit.hide()
        self.search_prescriptions()

    def load_prescriptions(self):
        prescriptions = self.prescription_model.get_all_prescriptions()
        self.populate_table(prescriptions)

    def populate_table(self, prescriptions):
        self.table.setRowCount(len(prescriptions))
        
        for row, prescription in enumerate(prescriptions):
            # Prescription data: id, date, patient_name, doctor_name
            self.table.setItem(row, 0, QTableWidgetItem(str(prescription[0])))
            
            # Format date
            try:
                date_obj = datetime.strptime(prescription[1], "%Y-%m-%d %H:%M:%S")
                formatted_date = date_obj.strftime("%Y/%m/%d %H:%M")
            except:
                formatted_date = prescription[1] # Fallback
            self.table.setItem(row, 1, QTableWidgetItem(formatted_date))
            
            self.table.setItem(row, 2, QTableWidgetItem(prescription[2]))
            self.table.setItem(row, 3, QTableWidgetItem(prescription[3]))

            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            actions_layout.setSpacing(5)

            print_btn = QPushButton("طباعة")
            # Pass the full prescription data row (which contains the ID) to print_prescription
            print_btn.clicked.connect(lambda _, p=prescription: self.print_prescription(p))
            actions_layout.addWidget(print_btn)

            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 4, actions_widget)

    def search_prescriptions(self):
        patient_search_text = self.search_input.text().strip()
        start_date = None
        end_date = None

        filter_type = self.date_filter_combo.currentText()
        current_date = QDate.currentDate()

        if filter_type == "روشتات اليوم":
            start_date = current_date.toString("yyyy-MM-dd 00:00:00")
            end_date = current_date.toString("yyyy-MM-dd 23:59:59")
        elif filter_type == "روشتات الأسبوع":
            start_date = current_date.addDays(-current_date.dayOfWeek() + 1).toString("yyyy-MM-dd 00:00:00")
            end_date = current_date.addDays(7 - current_date.dayOfWeek()).toString("yyyy-MM-dd 23:59:59")
        elif filter_type == "روشتات الشهر":
            start_date = QDate(current_date.year(), current_date.month(), 1).toString("yyyy-MM-dd 00:00:00")
            end_date = QDate(current_date.year(), current_date.month(), current_date.daysInMonth()).toString("yyyy-MM-dd 23:59:59")
        elif filter_type == "تاريخ مخصص":
            start_date = self.start_date_edit.date().toString("yyyy-MM-dd 00:00:00")
            end_date = self.end_date_edit.date().toString("yyyy-MM-dd 23:59:59")

        # Split patient search text into name and phone if possible
        patient_name = None
        patient_phone = None
        if patient_search_text:
            if patient_search_text.isdigit(): # Assume it\`s a phone number if all digits
                patient_phone = patient_search_text
            else:
                patient_name = patient_search_text
        
        prescriptions = self.prescription_model.search_prescriptions(
            start_date=start_date, end_date=end_date,
            patient_name=patient_name, patient_phone=patient_phone
        )
        self.populate_table(prescriptions)

    def print_prescription(self, prescription_data_row):
        # prescription_data_row: id, date, patient_name, doctor_name (from populate_table)
        prescription_id = prescription_data_row[0] # Get the ID from the passed row data
        
        # Get full prescription details including items
        prescription_details = self.prescription_model.get_prescription_details(prescription_id)
        if not prescription_details or not prescription_details["prescription"]:
            QMessageBox.warning(self, "خطأ", "لا يمكن العثور على تفاصيل الروشتة.")
            return

        # Prepare data for PDF
        # Access 'prescription' and 'items' keys from the dictionary
        prescription_info = prescription_details["prescription"]
        prescription_items = prescription_details["items"]

        patient_name = prescription_info["patient_name"]
        diagnosis = prescription_info["notes"]
        prescription_date = prescription_info["date"]

        medicines_data = []
        for item in prescription_items:
            medicines_data.append({
                "medicine_name": item["name"], # Assuming 'name' is the key for medicine name in items
                "dosage": item["dosage"],
                "duration": item["duration"],
                "instructions": item["instructions"]
            })

        prescription_data = {
            "patient_name": patient_name,
            "date": prescription_date,
            "diagnosis": diagnosis,
            "medicines": medicines_data
        }

        # Get clinic and print settings
        settings_model = SettingsModel()
        clinic_settings = settings_model.get_clinic_settings()
        print_settings = settings_model.get_print_settings()

        try:
            file_name = "prescription_" + patient_name.replace(" ", "_") + "_" + datetime.now().strftime("%Y%m%d%H%M%S") + ".pdf"
            output_dir = os.path.join(os.path.expanduser("~"), "Desktop") # Save to Desktop
            os.makedirs(output_dir, exist_ok=True)
            file_path = os.path.join(output_dir, file_name)
            
            generate_prescription_pdf(file_path, prescription_data, clinic_settings, print_settings)
            QMessageBox.information(self, "نجح", f"تم إنشاء الروشتة بنجاح في: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء طباعة الروشتة: {e}")


