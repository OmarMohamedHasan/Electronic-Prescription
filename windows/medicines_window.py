from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QHeaderView, QLineEdit, QMessageBox,
    QInputDialog, QComboBox, QFormLayout, QDialog, QDialogButtonBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from models.drug_model import DrugModel


class AddMedicineDialog(QDialog):
    def __init__(self, parent=None, medicine_data=None):
        super().__init__(parent)
        self.setWindowTitle("إضافة دواء جديد" if not medicine_data else "تعديل بيانات الدواء")
        self.setFixedSize(400, 300)
        self.medicine_data = medicine_data
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("اسم الدواء")
        
        self.dosage_input = QLineEdit()
        self.dosage_input.setPlaceholderText("الجرعة (مثال: 500mg)")
        
        self.form_input = QLineEdit()
        self.form_input.setPlaceholderText("الشكل (مثال: أقراص, شراب)")
        
        self.instructions_input = QLineEdit()
        self.instructions_input.setPlaceholderText("تعليمات الاستخدام (مثال: مرتين يومياً بعد الأكل)")

        # Fill data if editing
        if self.medicine_data:
            self.name_input.setText(self.medicine_data[1])
            self.dosage_input.setText(self.medicine_data[2] or "")
            self.form_input.setText(self.medicine_data[3] or "")
            self.instructions_input.setText(self.medicine_data[4] or "")

        layout.addRow("الاسم:", self.name_input)
        layout.addRow("الجرعة:", self.dosage_input)
        layout.addRow("الشكل:", self.form_input)
        layout.addRow("التعليمات:", self.instructions_input)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

        self.setLayout(layout)

    def get_data(self):
        return {
            "name": self.name_input.text().strip(),
            "dosage": self.dosage_input.text().strip(),
            "form": self.form_input.text().strip(),
            "instructions": self.instructions_input.text().strip()
        }


class MedicinesWindow(QWidget):
    medicine_changed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.drug_model = DrugModel()
        self.init_ui()
        self.load_medicines()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10) # Reduced margins
        layout.setSpacing(10) # Reduced spacing

        # Title
        title = QLabel("إدارة الأدوية")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;") # Reduced margin-bottom
        layout.addWidget(title)

        # Search and Add section
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث باسم الدواء...")
        self.search_input.textChanged.connect(self.search_medicines)
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
        
        self.add_button = QPushButton("➕ إضافة دواء جديد")
        self.add_button.clicked.connect(self.add_medicine)
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

        # Medicines table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "الرقم", "الاسم", "الجرعة", "الشكل", "الإجراءات"
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

    def load_medicines(self):
        medicines = self.drug_model.get_all_medicines()
        self.populate_table(medicines)

    def populate_table(self, medicines):
        self.table.setRowCount(len(medicines))
        
        for row, medicine in enumerate(medicines):
            # Medicine data: id, name, dosage, form, instructions
            self.table.setItem(row, 0, QTableWidgetItem(str(medicine[0])))
            self.table.setItem(row, 1, QTableWidgetItem(medicine[1]))
            self.table.setItem(row, 2, QTableWidgetItem(medicine[2] or ""))
            self.table.setItem(row, 3, QTableWidgetItem(medicine[3] or ""))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            edit_btn = QPushButton("تعديل")
            edit_btn.clicked.connect(lambda _, m=medicine: self.edit_medicine(m))
            
            actions_layout.addWidget(edit_btn)
            actions_widget.setLayout(actions_layout)
            self.table.setCellWidget(row, 4, actions_widget)

    def search_medicines(self):
        search_text = self.search_input.text().strip()
        if not search_text:
            self.load_medicines()
            return
        
        # Simple search implementation (by name)
        all_medicines = self.drug_model.get_all_medicines()
        filtered_medicines = []
        
        for medicine in all_medicines:
            if search_text.lower() in medicine[1].lower():
                filtered_medicines.append(medicine)
        
        self.populate_table(filtered_medicines)

    def add_medicine(self):
        dialog = AddMedicineDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            # Validate required fields
            if not data["name"]:
                QMessageBox.warning(self, "خطأ", "اسم الدواء مطلوب!")
                return
            
            # Add medicine
            success = self.drug_model.add_medicine(
                data["name"], data["dosage"], data["form"], data["instructions"]
            )
            
            if success:
                QMessageBox.information(self, "نجح", "تم إضافة الدواء بنجاح!")
                self.load_medicines()
                self.medicine_changed.emit()
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء إضافة الدواء!")

    def edit_medicine(self, medicine_data):
        dialog = AddMedicineDialog(self, medicine_data)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            
            # Validate required fields
            if not data["name"]:
                QMessageBox.warning(self, "خطأ", "اسم الدواء مطلوب!")
                return
            
            # Update medicine
            success = self.drug_model.update_medicine(
                medicine_data[0], data["name"], data["dosage"], data["form"], data["instructions"]
            )
            
            if success:
                QMessageBox.information(self, "نجح", "تم تحديث بيانات الدواء بنجاح!")
                self.load_medicines()
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء تحديث بيانات الدواء!")




