import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit,
    QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QDialogButtonBox, QFormLayout, QFileDialog
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from models.patient_model import PatientModel
from models.drug_model import DrugModel
from models.prescription_model import PrescriptionModel
from models.template_model import TemplateModel
from windows.patients_window import AddPatientDialog # Re-use patient dialog
from helpers.print_utility import generate_prescription_pdf
from models.settings_model import SettingsModel
from datetime import datetime
import os

class NewPrescriptionWindow(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id # Doctor ID
        self.patient_model = PatientModel()
        self.drug_model = DrugModel()
        self.prescription_model = PrescriptionModel()
        self.template_model = TemplateModel()
        self.selected_patient_id = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 280) # Reduced margins
        layout.setSpacing(-5) # Reduced spacing

        # Title
        title = QLabel("إنشاء روشتة جديدة")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 5px;") # Reduced margin-bottom
        layout.addWidget(title)

        # Patient Selection/Creation
        patient_layout = QHBoxLayout()
        patient_layout.addWidget(QLabel("المريض:"))
        
        self.patient_combo = QComboBox()
        self.patient_combo.setPlaceholderText("اختر مريضًا موجودًا")
        self.patient_combo.currentIndexChanged.connect(self.on_patient_selected)
        patient_layout.addWidget(self.patient_combo)

        self.add_new_patient_btn = QPushButton("➕ مريض جديد")
        self.add_new_patient_btn.clicked.connect(self.add_new_patient)
        patient_layout.addWidget(self.add_new_patient_btn)

        self.template_combo = QComboBox()
        self.template_combo.setPlaceholderText("اختر أسطمبة")
        self.template_combo.currentIndexChanged.connect(self.on_template_combo_selected)
        patient_layout.addWidget(self.template_combo)
        self.load_template_btn = QPushButton("إضافة من أسطمبة")
        self.load_template_btn.clicked.connect(self.load_template_medicines)
        patient_layout.addWidget(self.load_template_btn)
        layout.addLayout(patient_layout)
        # Patient Info Display (Optional, for selected patient)
        self.patient_info_label = QLabel("")
        self.patient_info_label.setStyleSheet("font-style: italic; color: #555;")
        layout.addWidget(self.patient_info_label)

        # Diagnosis
        layout.addWidget(QLabel("التشخيص (اختياري):"))
        self.diagnosis_input = QTextEdit()
        self.diagnosis_input.setPlaceholderText("اكتب تشخيص المريض هنا...")
        self.diagnosis_input.setFixedHeight(60)
        layout.addWidget(self.diagnosis_input)

        # Medicines Section
        medicine_section_layout = QVBoxLayout()
        medicine_section_layout.addWidget(QLabel("الأدوية:"))

        # Medicine input fields
        medicine_input_layout = QHBoxLayout()
        self.medicine_combo = QComboBox()
        self.medicine_combo.setMinimumWidth(250) # Enlarge medicine combo box
        self.medicine_combo.setPlaceholderText("اختر دواء")
        self.medicine_combo.currentIndexChanged.connect(self.on_medicine_selected)
        medicine_input_layout.addWidget(self.medicine_combo, 3) # Give it more stretch

        self.dosage_input = QLineEdit()
        self.dosage_input.setPlaceholderText("الجرعة")
        medicine_input_layout.addWidget(self.dosage_input, 1)

        self.form_input = QLineEdit()
        self.form_input.setPlaceholderText("الشكل")
        medicine_input_layout.addWidget(self.form_input, 1)

        self.instructions_input = QLineEdit()
        self.instructions_input.setPlaceholderText("تعليمات")
        medicine_input_layout.addWidget(self.instructions_input, 1)

        self.add_medicine_btn = QPushButton("➕ إضافة دواء")
        self.add_medicine_btn.clicked.connect(self.add_medicine_to_list)
        medicine_input_layout.addWidget(self.add_medicine_btn)
        medicine_section_layout.addLayout(medicine_input_layout)

        # Medicines Table
        self.medicines_table = QTableWidget()
        self.medicines_table.setColumnCount(5)
        self.medicines_table.setHorizontalHeaderLabels(["الدواء", "الجرعة", "الشكل", "التعليمات", "حذف"])
        self.medicines_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.medicines_table.setFixedHeight(150) # Reduced fixed height for the table
        medicine_section_layout.addWidget(self.medicines_table)
        layout.addLayout(medicine_section_layout)

        # Save and Print Button (Combined)
        save_print_layout = QHBoxLayout()
        save_print_layout.addStretch(1) # Add stretch to push button to center
        self.save_prescription_btn = QPushButton("حفظ الروشتة وطباعتها")
        self.save_prescription_btn.clicked.connect(self.save_and_print_prescription)
        self.save_prescription_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2271b3;
            }
        """)
        save_print_layout.addWidget(self.save_prescription_btn)
        save_print_layout.addStretch(1) # Add stretch to push button to center
        layout.addLayout(save_print_layout)
        self.setLayout(layout)
        self.load_patients_to_combo()
        self.load_medicines_to_combo()
        self.load_templates_to_combo()

    def load_patients_to_combo(self):
        self.patient_combo.clear()
        self.patient_combo.addItem("اختر مريضًا موجودًا", None) # Placeholder
        patients = self.patient_model.get_all_patients()
        for patient in patients:
            self.patient_combo.addItem(f"{patient[1]} (ID: {patient[0]})", patient[0])

    def load_medicines_to_combo(self):
        self.medicine_combo.clear()
        self.medicine_combo.addItem("اختر دواء", None) # Placeholder
        medicines = self.drug_model.get_all_medicines()
        for medicine in medicines:
            self.medicine_combo.addItem(f"{medicine[1]} ({medicine[2]})", medicine[0])

    def on_patient_selected(self, index):
        self.selected_patient_id = self.patient_combo.itemData(index)
        if self.selected_patient_id:
            patient = self.patient_model.get_patient_by_id(self.selected_patient_id)
            if patient:
                self.patient_info_label.setText(
                    f"الاسم: {patient[1]}, السن: {patient[2]}, الجنس: {patient[3] or ''}, الهاتف: {patient[4] or ''}"
                )
            else:
                self.patient_info_label.setText("")
        else:
            self.patient_info_label.setText("")

    def on_medicine_selected(self, index):
        medicine_id = self.medicine_combo.itemData(index)
        if medicine_id:
            medicine = self.drug_model.get_medicine_by_id(medicine_id)
            if medicine:
                self.dosage_input.setText(medicine[2] or '')
                self.form_input.setText(medicine[3] or '')
                self.instructions_input.setText(medicine[4] or '')
            else:
                self.dosage_input.clear()
                self.form_input.clear()
                self.instructions_input.clear()
        else:
            self.dosage_input.clear()
            self.form_input.clear()
            self.instructions_input.clear()

    def add_new_patient(self):
        dialog = AddPatientDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            data = dialog.get_data()
            if not data["name"] or not data["age"]:
                QMessageBox.warning(self, "خطأ", "الاسم والسن مطلوبان!")
                return
            try:
                age = int(data["age"])
                if age <= 0 or age > 150:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "خطأ", "يرجى إدخال سن صحيح!")
                return
            
            success = self.patient_model.add_patient(
                data["name"], age, data["gender"], data["phone"], data["conditions"]
            )
            if success:
                QMessageBox.information(self, "نجح", "تم إضافة المريض بنجاح!")
                self.load_patients_to_combo()
                self.patient_combo.setCurrentIndex(self.patient_combo.findData(self.patient_model.get_all_patients()[0][0]))
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء إضافة المريض!")

    def add_medicine_to_list(self):
        medicine_id = self.medicine_combo.itemData(self.medicine_combo.currentIndex())
        medicine_name = self.medicine_combo.currentText()
        dosage = self.dosage_input.text().strip()
        form = self.form_input.text().strip()
        instructions = self.instructions_input.text().strip()

        if not medicine_id or not dosage:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار دواء وتحديد الجرعة.")
            return

        row_position = self.medicines_table.rowCount()
        self.medicines_table.insertRow(row_position)
        self.medicines_table.setItem(row_position, 0, QTableWidgetItem(medicine_name))
        self.medicines_table.setItem(row_position, 1, QTableWidgetItem(dosage))
        self.medicines_table.setItem(row_position, 2, QTableWidgetItem(form))
        self.medicines_table.setItem(row_position, 3, QTableWidgetItem(instructions))

        delete_btn = QPushButton("حذف")
        delete_btn.clicked.connect(lambda _, r=row_position: self.remove_medicine_from_list(r))
        self.medicines_table.setCellWidget(row_position, 4, delete_btn)

        # Store medicine ID with the item for later retrieval
        self.medicines_table.item(row_position, 0).setData(Qt.UserRole, medicine_id)

        # Clear medicine input fields
        self.medicine_combo.setCurrentIndex(0)
        self.dosage_input.clear()
        self.form_input.clear()
        self.instructions_input.clear()

    def remove_medicine_from_list(self, row):
        self.medicines_table.removeRow(row)

    def save_and_print_prescription(self):
        if not self.selected_patient_id:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار مريض لحفظ الروشتة.")
            return

        diagnosis = self.diagnosis_input.toPlainText().strip()
        # Diagnosis is now optional, no warning if empty

        if self.medicines_table.rowCount() == 0:
            QMessageBox.warning(self, "خطأ", "يرجى إضافة دواء واحد على الأقل للروشتة لحفظها.")
            return

        # Gather prescription data
        patient = self.patient_model.get_patient_by_id(self.selected_patient_id)
        if not patient:
            QMessageBox.warning(self, "خطأ", "بيانات المريض غير موجودة.")
            return

        medicines_data = []
        for row in range(self.medicines_table.rowCount()):
            medicine_id = self.medicines_table.item(row, 0).data(Qt.UserRole)
            medicine_name = self.medicines_table.item(row, 0).text()
            dosage = self.medicines_table.item(row, 1).text()
            form = self.medicines_table.item(row, 2).text()
            instructions = self.medicines_table.item(row, 3).text()
            medicines_data.append({
                "medicine_id": medicine_id,
                "medicine_name": medicine_name,
                "dosage": dosage,
                "form": form,
                "instructions": instructions
            })

        # Save to database
        success = self.prescription_model.add_prescription(
            self.selected_patient_id, self.user_id, diagnosis, medicines_data
        )

        if success:
            QMessageBox.information(self, "نجح", "تم حفظ الروشتة بنجاح!")
            # Now generate and save PDF
            prescription_data = {
                "patient_name": patient[1],
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "diagnosis": diagnosis,
                "medicines": medicines_data
            }

            settings_model = SettingsModel()
            clinic_settings = settings_model.get_clinic_settings()
            print_settings = settings_model.get_print_settings()

            default_file_name = f"prescription_{patient[1].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            file_path, _ = QFileDialog.getSaveFileName(self, "حفظ الروشتة كـ PDF", default_file_name, "PDF Files (*.pdf)")

            if file_path:
                try:
                    generate_prescription_pdf(file_path, prescription_data, clinic_settings, print_settings)
                    QMessageBox.information(self, "نجح", f"تم حفظ الروشتة بنجاح في: {file_path}")
                    # os.startfile(file_path) # This might not work in all environments (e.g., Linux without specific desktop environment setup)
                except Exception as e:
                    QMessageBox.critical(self, "خطأ", f"حدث خطأ أثناء حفظ الروشتة كـ PDF: {e}")
            
            # Clear form after saving
            self.selected_patient_id = None
            self.patient_combo.setCurrentIndex(0)
            self.patient_info_label.clear()
            self.diagnosis_input.clear()
            self.medicines_table.setRowCount(0)
        else:
            QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء حفظ الروشتة في قاعدة البيانات!")

    def load_templates_to_combo(self):
        self.template_combo.clear()
        self.template_combo.addItem("اختر أسطمبة", None) # Placeholder
        templates = self.template_model.get_all_templates()
        for template in templates:
            self.template_combo.addItem(template["name"], template["id"])

    def on_template_combo_selected(self, index):
        pass # No direct action on selection, only when 'Load from Template' button is clicked

    def load_template_medicines(self):
        template_id = self.template_combo.itemData(self.template_combo.currentIndex())
        if not template_id:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار أسطمبة لتحميل الأدوية.")
            return

        reply = QMessageBox.question(self, "تأكيد", "هل أنت متأكد من تحميل الأدوية من هذه الأسطمبة؟ سيؤدي هذا إلى مسح الأدوية الحالية في الروشتة.",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return

        # Use get_template_by_id and access 'items' key
        template_data = self.template_model.get_template_by_id(template_id)
        if not template_data or not template_data.get('items'):
            QMessageBox.information(self, "معلومة", "لا توجد أدوية في هذه الأسطمبة.")
            return

        template_items = template_data['items']

        self.medicines_table.setRowCount(0) # Clear existing medicines
        for item in template_items:
            medicine = self.drug_model.get_medicine_by_id(item["medicine_id"])
            if medicine:
                row_position = self.medicines_table.rowCount()
                self.medicines_table.insertRow(row_position)
                self.medicines_table.setItem(row_position, 0, QTableWidgetItem(medicine[1])) # medicine name
                self.medicines_table.setItem(row_position, 1, QTableWidgetItem(item["dosage"])) # dosage from template
                self.medicines_table.setItem(row_position, 2, QTableWidgetItem(medicine[3])) # form from medicine
                self.medicines_table.setItem(row_position, 3, QTableWidgetItem(item["instructions"])) # instructions from template

                delete_btn = QPushButton("حذف")
                delete_btn.clicked.connect(lambda _, r=row_position: self.remove_medicine_from_list(r))
                self.medicines_table.setCellWidget(row_position, 4, delete_btn)

                self.medicines_table.item(row_position, 0).setData(Qt.UserRole, medicine[0])


