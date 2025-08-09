from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QMessageBox,
    QInputDialog, QComboBox, QFormLayout, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from models.patient_model import PatientModel
from datetime import datetime


class AddPatientDialog(QDialog):
    def __init__(self, parent=None, patient_data=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة مريض جديد" if not patient_data else "تعديل بيانات المريض")
        self.setFixedSize(400, 300)
        self.patient_data = patient_data
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("اسم المريض")
        
        self.age_input = QLineEdit()
        self.age_input.setPlaceholderText("السن")
        
        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["ذكر", "أنثى"])
        
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("رقم الهاتف")
        
        self.conditions_input = QLineEdit()
        self.conditions_input.setPlaceholderText("الأمراض المزمنة أو الحساسية")

        # Fill data if editing
        if self.patient_data:
            self.name_input.setText(self.patient_data[1])
            self.age_input.setText(str(self.patient_data[2]))
            if self.patient_data[3]:
                self.gender_combo.setCurrentText(self.patient_data[3])
            if self.patient_data[4]:
                self.phone_input.setText(self.patient_data[4])
            if self.patient_data[5]:
                self.conditions_input.setText(self.patient_data[5])

        layout.addRow("الاسم:", self.name_input)
        layout.addRow("السن:", self.age_input)
        layout.addRow("الجنس:", self.gender_combo)
        layout.addRow("رقم الهاتف:", self.phone_input)
        layout.addRow("الأمراض/الحساسية:", self.conditions_input)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'age': self.age_input.text().strip(),
            'gender': self.gender_combo.currentText(),
            'phone': self.phone_input.text().strip(),
            'conditions': self.conditions_input.text().strip()
        }


class PatientsWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.patient_model = PatientModel()
        self.init_ui()
        self.load_patients()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10) # Reduced margins
        layout.setSpacing(10) # Reduced spacing

        # Title
        title = QLabel("إدارة المرضى")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;") # Reduced margin-bottom
        layout.addWidget(title)

        # Search and Add section
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث بالاسم أو رقم الهاتف...")
        self.search_input.textChanged.connect(self.search_patients)
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
        
        self.add_button = QPushButton("➕ إضافة مريض جديد")
        self.add_button.clicked.connect(self.add_patient)
        self.add_button.setStyleSheet("""
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

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.add_button)
        layout.addLayout(search_layout)

        # Patients table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "الرقم", "الاسم", "السن", "الجنس", "رقم الهاتف", "آخر زيارة", "الإجراءات"
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

    def load_patients(self):
        patients = self.patient_model.get_all_patients()
        self.populate_table(patients)

    def populate_table(self, patients):
        self.table.setRowCount(len(patients))
        
        for row, patient in enumerate(patients):
            # Patient data: id, name, age, gender, phone, conditions, last_visit
            self.table.setItem(row, 0, QTableWidgetItem(str(patient[0])))
            self.table.setItem(row, 1, QTableWidgetItem(patient[1]))
            self.table.setItem(row, 2, QTableWidgetItem(str(patient[2])))
            self.table.setItem(row, 3, QTableWidgetItem(patient[3] or ""))
            self.table.setItem(row, 4, QTableWidgetItem(patient[4] or ""))
            
            # Format last visit date
            last_visit = patient[6] if patient[6] else "لم يحدد"
            if last_visit != "لم يحدد":
                try:
                    # Parse and format the date
                    date_obj = datetime.strptime(last_visit, "%Y-%m-%d %H:%M:%S")
                    formatted_date = date_obj.strftime("%Y/%m/%d %H:%M")
                    last_visit = formatted_date
                except:
                    pass
            
            self.table.setItem(row, 5, QTableWidgetItem(last_visit))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            edit_btn = QPushButton("تعديل")
            edit_btn.clicked.connect(lambda _, p=patient: self.edit_patient(p))
            
            actions_layout.addWidget(edit_btn)
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 6, actions_widget)

    def search_patients(self):
        search_text = self.search_input.text().strip()
        if not search_text:
            self.load_patients()
            return
        
        # Simple search implementation
        all_patients = self.patient_model.get_all_patients()
        filtered_patients = []
        
        for patient in all_patients:
            # Search in name and phone
            if (search_text.lower() in patient[1].lower() or 
                (patient[4] and search_text in patient[4])):
                filtered_patients.append(patient)
        
        self.populate_table(filtered_patients)

    def add_patient(self):
        dialog = AddPatientDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            # Validate required fields
            if not data['name'] or not data['age']:
                QMessageBox.warning(self, "خطأ", "الاسم والسن مطلوبان!")
                return
            
            try:
                age = int(data['age'])
                if age <= 0 or age > 150:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال سن صحيح!")
                return
            
            # Add patient
            success = self.patient_model.add_patient(
                data['name'], age, data['gender'], 
                data['phone'], data['conditions']
            )
            
            if success:
                QMessageBox.information(self, "نجح", "تم إضافة المريض بنجاح!")
                self.load_patients()
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء إضافة المريض!")

    def edit_patient(self, patient_data):
        dialog = AddPatientDialog(self, patient_data)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            # Validate required fields
            if not data['name'] or not data['age']:
                QMessageBox.warning(self, "خطأ", "الاسم والسن مطلوبان!")
                return
            
            try:
                age = int(data['age'])
                if age <= 0 or age > 150:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال سن صحيح!")
                return
            
            # Update patient
            success = self.patient_model.update_patient(
                patient_data[0], data['name'], age, data['gender'], 
                data['phone'], data['conditions']
            )
            
            if success:
                QMessageBox.information(self, "نجح", "تم تحديث بيانات المريض بنجاح!")
                self.load_patients()
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء تحديث بيانات المريض!")



