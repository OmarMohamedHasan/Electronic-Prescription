import os
import sys
from datetime import datetime

# Add parent directory to path to import models and helpers
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.settings_model import SettingsModel
from helpers.print_utility import generate_prescription_pdf

# Ensure the database is initialized (if not already)
from database.db_init import update_database
update_database()

def run_test_print():
    settings_model = SettingsModel()

    # 1. Simulate Clinic Settings (including new email and website fields)
    #    Make sure to replace with actual paths if you want to test with real images
    test_doctor_name = "د. أحمد محمد"
    test_clinic_address = "شارع النيل، عمارة 5، الدور 3، القاهرة"
    test_phone_numbers = "+201001234567, +20234567890"
    test_logo_path = "" # Set to empty string to avoid dummy image creation
    test_signature_path = "" # Set to empty string to avoid dummy image creation
    test_clinic_email = "info@clinic.com"
    test_clinic_website = "www.clinic.com"

    # No need to create dummy files, as we are setting paths to empty strings

    settings_model.save_clinic_settings(
        test_doctor_name, test_clinic_address, test_phone_numbers,
        test_logo_path, test_signature_path, test_clinic_email, test_clinic_website
    )

    # 2. Simulate Print Settings
    test_logo_position = "أعلى الوسط" # Options: "أعلى اليمين", "أعلى الوسط", "أعلى اليسار"
    test_print_template_style = "النموذج الافتراضي 1" # Options: "النموذج الافتراضي 1", "النموذج 2 (بدون توقيع)"
    test_selected_template_id = None # No template selected for now
    settings_model.save_print_settings(test_logo_position, test_print_template_style, test_selected_template_id)

    # 3. Simulate Prescription Data
    prescription_data = {
        'patient_name': 'محمد علي',
        'date': datetime.now().strftime('%Y-%m-%d %H:%M'),
        'diagnosis': 'التهاب الحلق',
        'medicines': [
            {'medicine_name': 'دواء أ', 'dosage': '500 مجم', 'form': 'أقراص', 'instructions': 'مرتين يومياً بعد الأكل'},
            {'medicine_name': 'دواء ب', 'dosage': '100 مجم', 'form': 'كبسولات', 'instructions': 'مرة واحدة يومياً قبل النوم'},
            {'medicine_name': 'دواء ج', 'dosage': '250 مجم', 'form': 'شراب', 'instructions': '3 مرات يومياً'},
        ]
    }

    # 4. Get actual settings from DB
    clinic_settings = settings_model.get_clinic_settings()
    print_settings = settings_model.get_print_settings()

    # 5. Generate PDF
    output_pdf_path = "/home/ubuntu/ElectronicPrescription/test_prescription.pdf"
    try:
        generate_prescription_pdf(output_pdf_path, prescription_data, clinic_settings, print_settings)
        print(f"PDF generated successfully at: {output_pdf_path}")
    except Exception as e:
        print(f"Error generating PDF: {e}")

if __name__ == "__main__":
    run_test_print()


