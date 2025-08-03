from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QLineEdit,
    QTextEdit, QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QMessageBox, QDialog, QDialogButtonBox, QFormLayout, QSplitter
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from models.template_model import TemplateModel
from models.drug_model import DrugModel

class TemplatesWindow(QWidget):
    template_changed = pyqtSignal()
    def __init__(self):
        super().__init__()
        self.template_model = TemplateModel()
        self.drug_model = DrugModel()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("أسطمبة الأدوية")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)

        # Create splitter for templates list and template details
        splitter = QSplitter(Qt.Horizontal)

        # Left side - Templates list
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        left_layout.setContentsMargins(0, 0, 10, 0)

        left_layout.addWidget(QLabel("قائمة الأسطمبات:"))
        
        self.templates_table = QTableWidget()
        self.templates_table.setColumnCount(3)
        self.templates_table.setHorizontalHeaderLabels(["الاسم", "الوصف", "إجراءات"])
        self.templates_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.templates_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.templates_table.itemSelectionChanged.connect(self.on_template_selected)
        left_layout.addWidget(self.templates_table)

        # Add new template button
        self.add_template_btn = QPushButton("➕ إضافة أسطمبة جديدة")
        self.add_template_btn.clicked.connect(self.add_new_template)
        self.add_template_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        left_layout.addWidget(self.add_template_btn)

        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)

        # Right side - Template details
        right_widget = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(10, 0, 0, 0)

        right_layout.addWidget(QLabel("تفاصيل الأسطمبة:"))

        # Template name
        right_layout.addWidget(QLabel("اسم الأسطمبة:"))
        self.template_name_input = QLineEdit()
        self.template_name_input.setPlaceholderText("اكتب اسم الأسطمبة...")
        right_layout.addWidget(self.template_name_input)

        # Template description
        right_layout.addWidget(QLabel("وصف الأسطمبة:"))
        self.template_description_input = QTextEdit()
        self.template_description_input.setPlaceholderText("اكتب وصف الأسطمبة...")
        self.template_description_input.setFixedHeight(80)
        right_layout.addWidget(self.template_description_input)

        # Medicines section
        right_layout.addWidget(QLabel("الأدوية:"))

        # Medicine input fields
        medicine_input_layout = QHBoxLayout()
        self.medicine_combo = QComboBox()
        self.medicine_combo.setMinimumWidth(200)
        self.medicine_combo.setPlaceholderText("اختر دواء")
        self.medicine_combo.currentIndexChanged.connect(self.on_medicine_selected)
        medicine_input_layout.addWidget(self.medicine_combo, 2)
        self.dosage_input = QLineEdit()
        self.dosage_input.setPlaceholderText("الجرعة")
        medicine_input_layout.addWidget(self.dosage_input, 1)

        self.form_input = QLineEdit()
        self.form_input.setPlaceholderText("الشكل")
        medicine_input_layout.addWidget(self.form_input, 1)

        self.instructions_input = QLineEdit()
        self.instructions_input.setPlaceholderText("تعليمات")
        medicine_input_layout.addWidget(self.instructions_input, 1)

        self.add_medicine_btn = QPushButton("➕")
        self.add_medicine_btn.clicked.connect(self.add_medicine_to_template)
        medicine_input_layout.addWidget(self.add_medicine_btn)
        right_layout.addLayout(medicine_input_layout)

        # Medicines table
        self.template_medicines_table = QTableWidget()
        self.template_medicines_table.setColumnCount(5)
        self.template_medicines_table.setHorizontalHeaderLabels(["الدواء", "الجرعة", "الشكل", "التعليمات", "حذف"])
        self.template_medicines_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        right_layout.addWidget(self.template_medicines_table)

        # Save and cancel buttons
        buttons_layout = QHBoxLayout()
        self.save_template_btn = QPushButton("حفظ الأسطمبة")
        self.save_template_btn.clicked.connect(self.save_template)
        self.save_template_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        buttons_layout.addWidget(self.save_template_btn)

        self.cancel_btn = QPushButton("إلغاء")
        self.cancel_btn.clicked.connect(self.clear_template_form)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        buttons_layout.addWidget(self.cancel_btn)
        right_layout.addLayout(buttons_layout)

        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)

        # Set splitter proportions
        splitter.setSizes([400, 600])
        layout.addWidget(splitter)

        self.setLayout(layout)
        self.load_templates()
        self.load_medicines_to_combo()
        self.clear_template_form()

        # Track current template being edited
        self.current_template_id = None

    def load_templates(self):
        self.templates_table.setRowCount(0)
        templates = self.template_model.get_all_templates()
        for template in templates:
            row_position = self.templates_table.rowCount()
            self.templates_table.insertRow(row_position)
            self.templates_table.setItem(row_position, 0, QTableWidgetItem(template[1]))  # name
            self.templates_table.setItem(row_position, 1, QTableWidgetItem(template[2] or ''))  # description

            # Actions buttons
            actions_layout = QHBoxLayout()
            edit_btn = QPushButton("تعديل")
            edit_btn.clicked.connect(lambda _, t_id=template[0]: self.edit_template(t_id))
            edit_btn.setStyleSheet("QPushButton { background-color: #f39c12; color: white; border: none; padding: 5px 10px; border-radius: 3px; }")
            actions_layout.addWidget(edit_btn)

            delete_btn = QPushButton("حذف")
            delete_btn.clicked.connect(lambda _, t_id=template[0]: self.delete_template(t_id))
            delete_btn.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; border: none; padding: 5px 10px; border-radius: 3px; }")
            actions_layout.addWidget(delete_btn)

            actions_widget = QWidget()
            actions_widget.setLayout(actions_layout)
            self.templates_table.setCellWidget(row_position, 2, actions_widget)

            # Store template ID with the item
            self.templates_table.item(row_position, 0).setData(Qt.UserRole, template[0])

    def load_medicines_to_combo(self):
        self.medicine_combo.clear()
        self.medicine_combo.addItem("اختر دواء", None)
        medicines = self.drug_model.get_all_medicines()
        for medicine in medicines:
            self.medicine_combo.addItem(f"{medicine['name']} ({medicine['form']})", medicine['id'])

    def on_template_selected(self):
        selected_items = self.templates_table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            template_id = self.templates_table.item(row, 0).data(Qt.UserRole)
            self.load_template_details(template_id)

    def load_template_details(self, template_id):
        template = self.template_model.get_template_by_id(template_id)
        if template:
            self.current_template_id = template_id
            self.template_name_input.setText(template['name'])
            self.template_description_input.setPlainText(template['description'] or '')
            
            # Load template medicines
            self.template_medicines_table.setRowCount(0)
            for item in template["items"]:
                medicine = self.drug_model.get_medicine_by_id(item["medicine_id"])
                if medicine:
                    row_position = self.template_medicines_table.rowCount()
                    self.template_medicines_table.insertRow(row_position)
                    self.template_medicines_table.setItem(row_position, 0, QTableWidgetItem(medicine["name"]))
                    self.template_medicines_table.setItem(row_position, 1, QTableWidgetItem(item["dosage"] or ""))
                    self.template_medicines_table.setItem(row_position, 2, QTableWidgetItem(item["form"] or ""))
                    self.template_medicines_table.setItem(row_position, 3, QTableWidgetItem(item["instructions"] or ""))

                    delete_btn = QPushButton("حذف")
                    delete_btn.clicked.connect(lambda _, r=row_position: self.remove_medicine_from_template(r))
                    delete_btn.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; border: none; padding: 5px 10px; border-radius: 3px; }")
                    self.template_medicines_table.setCellWidget(row_position, 4, delete_btn)

                    # Store medicine ID with the item
                    self.template_medicines_table.item(row_position, 0).setData(Qt.UserRole, item["medicine_id"])

    def add_new_template(self):
        self.clear_template_form()
        self.current_template_id = None

    def clear_template_form(self):
        self.template_name_input.clear()
        self.template_description_input.clear()
        self.template_medicines_table.setRowCount(0)
        self.medicine_combo.setCurrentIndex(0)
        self.dosage_input.clear()
        self.form_input.clear()
        self.instructions_input.clear()
        self.current_template_id = None

    def add_medicine_to_template(self):
        medicine_id = self.medicine_combo.itemData(self.medicine_combo.currentIndex())
        medicine_name = self.medicine_combo.currentText()
        dosage = self.dosage_input.text().strip()
        form = self.form_input.text().strip()
        instructions = self.instructions_input.text().strip()

        if not medicine_id:
            QMessageBox.warning(self, "خطأ", "يرجى اختيار دواء.")
            return

        row_position = self.template_medicines_table.rowCount()
        self.template_medicines_table.insertRow(row_position)
        self.template_medicines_table.setItem(row_position, 0, QTableWidgetItem(medicine_name))
        self.template_medicines_table.setItem(row_position, 1, QTableWidgetItem(dosage))
        self.template_medicines_table.setItem(row_position, 2, QTableWidgetItem(form))
        self.template_medicines_table.setItem(row_position, 3, QTableWidgetItem(instructions))

        delete_btn = QPushButton("حذف")
        delete_btn.clicked.connect(lambda _, r=row_position: self.remove_medicine_from_template(r))
        delete_btn.setStyleSheet("QPushButton { background-color: #e74c3c; color: white; border: none; padding: 5px 10px; border-radius: 3px; }")
        self.template_medicines_table.setCellWidget(row_position, 4, delete_btn)

        # Store medicine ID with the item
        self.template_medicines_table.item(row_position, 0).setData(Qt.UserRole, medicine_id)

        # Clear input fields
        self.medicine_combo.setCurrentIndex(0)
        self.dosage_input.clear()
        self.form_input.clear()
        self.instructions_input.clear()

    def remove_medicine_from_template(self, row):
        self.template_medicines_table.removeRow(row)

    def save_template(self):
        name = self.template_name_input.text().strip()
        description = self.template_description_input.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم الأسطمبة.")
            return

        if self.template_medicines_table.rowCount() == 0:
            QMessageBox.warning(self, "خطأ", "يرجى إضافة دواء واحد على الأقل للأسطمبة.")
            return

        # Gather medicines data
        items = []
        for row in range(self.template_medicines_table.rowCount()):
            medicine_id = self.template_medicines_table.item(row, 0).data(Qt.UserRole)
            dosage = self.template_medicines_table.item(row, 1).text()
            form = self.template_medicines_table.item(row, 2).text()
            instructions = self.template_medicines_table.item(row, 3).text()
            items.append({
                "medicine_id": medicine_id,
                "dosage": dosage,
                "form": form,
                "instructions": instructions
            })

        # Save or update template
        if self.current_template_id:
            success = self.template_model.update_template(self.current_template_id, name, description, items)
            message = "تم تحديث الأسطمبة بنجاح!" if success else "حدث خطأ أثناء تحديث الأسطمبة!"
        else:
            success = self.template_model.add_template(name, description, items)
            message = "تم إضافة الأسطمبة بنجاح!" if success else "حدث خطأ أثناء إضافة الأسطمبة!"

        if success:
            QMessageBox.information(self, "نجح", message)
            self.load_templates()
            self.clear_template_form()
            self.template_changed.emit()
        else:
            QMessageBox.warning(self, "خطأ", message)

    def edit_template(self, template_id):
        self.load_template_details(template_id)

    def delete_template(self, template_id):
        reply = QMessageBox.question(self, "تأكيد الحذف", "هل أنت متأكد من حذف هذه الأسطمبة؟",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            success = self.template_model.delete_template(template_id)
            if success:
                QMessageBox.information(self, "نجح", "تم حذف الأسطمبة بنجاح!")
                self.load_templates()
                self.clear_template_form()
                self.template_changed.emit()
            else:
                QMessageBox.warning(self, "خطأ", "حدث خطأ أثناء حذف الأسطمبة!")



    def on_medicine_selected(self, index):
        medicine_id = self.medicine_combo.itemData(index)
        if medicine_id:
            medicine = self.drug_model.get_medicine_by_id(medicine_id)
            if medicine:
                self.dosage_input.setText(medicine["dosage"] or "")
                self.form_input.setText(medicine["form"] or "")
                self.instructions_input.setText(medicine["instructions"] or "")
            else:
                self.dosage_input.clear()
                self.form_input.clear()
                self.instructions_input.clear()
        else:
            self.dosage_input.clear()
            self.form_input.clear()
            self.instructions_input.clear()


