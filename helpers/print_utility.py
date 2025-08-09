from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_RIGHT, TA_CENTER
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from datetime import datetime
from reportlab.pdfgen import canvas
from models.settings_model import SettingsModel # Import SettingsModel here

# Register Arabic font
pdfmetrics.registerFont(TTFont("ArabicFont", os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "NotoSansArabic-Regular.ttf")))
pdfmetrics.registerFont(TTFont("ArabicFont-Bold", os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "NotoSansArabic-Regular.ttf")))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name='ArabicNormal', fontName='ArabicFont', fontSize=12, leading=14, alignment=TA_RIGHT))
styles.add(ParagraphStyle(name='ArabicHeading', fontName='ArabicFont-Bold', fontSize=16, leading=18, alignment=TA_CENTER))
styles.add(ParagraphStyle(name='ArabicSubHeading', fontName='ArabicFont-Bold', fontSize=14, leading=16, alignment=TA_RIGHT))

def draw_background(canvas, doc):
    # This function is called on every page. We use it to draw the background image.
    if hasattr(doc, 'background_image_path') and doc.background_image_path:
        if os.path.exists(doc.background_image_path):
            canvas.saveState()
            canvas.drawImage(doc.background_image_path, 0, 0, width=A4[0], height=A4[1], preserveAspectRatio=True, anchor='c')
            canvas.restoreState()

def generate_prescription_pdf(file_path, prescription_data, clinic_settings, print_settings):
    doc = SimpleDocTemplate(file_path, pagesize=A4)
    story = []

    # Get selected template path
    template_path = None
    if print_settings and print_settings.get("selected_template_id"):
        settings_model = SettingsModel() # Re-initialize to avoid circular import issues
        template = settings_model.get_print_template_by_id(print_settings["selected_template_id"])
        if template:
            template_path = template["file_path"]

    # Set background image path on the document object if a template is used
    if template_path and os.path.exists(template_path):
        doc.background_image_path = template_path
        # Build the document with the background drawing function
        # Content will be added later, after the background is drawn
        # For now, we just build an empty story to trigger the page drawing
        doc.build(story, onFirstPage=draw_background, onLaterPages=draw_background)
        # Clear story to add actual content
        story = []

    # Clinic Header (only if not using a template, or if content needs to be overlaid)
    # For now, we will always add content, and assume template is just background
    if clinic_settings:
        logo_path = clinic_settings["logo_path"]
        doctor_name = clinic_settings["doctor_name"]
        clinic_address = clinic_settings["clinic_address"]
        phone_numbers = clinic_settings["phone_numbers"]
        clinic_email = clinic_settings["clinic_email"]
        clinic_website = clinic_settings["clinic_website"]

        header_elements = []
        if logo_path and os.path.exists(logo_path):
            img = Image(logo_path, width=3*cm, height=3*cm)
            # Position logo based on print_settings
            if print_settings and print_settings.get("logo_position") == "أعلى الوسط":
                img.hAlign = 'CENTER'
            elif print_settings and print_settings.get("logo_position") == "أعلى اليسار":
                img.hAlign = 'LEFT'
            else: # Default to top right
                img.hAlign = 'RIGHT'
            header_elements.append(img)

        if doctor_name:
            header_elements.append(Paragraph(f"دكتور: {doctor_name}", styles['ArabicHeading']))
        if clinic_address:
            header_elements.append(Paragraph(f"العنوان: {clinic_address}", styles['ArabicNormal']))
        if phone_numbers:
            header_elements.append(Paragraph(f"للتواصل: {phone_numbers}", styles['ArabicNormal']))
        if clinic_email:
            header_elements.append(Paragraph(f"البريد الإلكتروني: {clinic_email}", styles['ArabicNormal']))
        if clinic_website:
            header_elements.append(Paragraph(f"الموقع الإلكتروني: {clinic_website}", styles['ArabicNormal']))
        
        for elem in header_elements:
            story.append(elem)
        story.append(Spacer(1, 0.5*cm))

    # Prescription Details
    story.append(Paragraph(f"اسم المريض: {prescription_data['patient_name']}", styles['ArabicNormal']))
    story.append(Paragraph(f"التاريخ: {prescription_data['date']}", styles['ArabicNormal']))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(f"التشخيص: {prescription_data['diagnosis']}", styles['ArabicNormal']))
    story.append(Spacer(1, 0.5*cm))

    # Medicines Table
    data = [["الدواء", "الجرعة", "الشكل", "التعليمات"]]
    for item in prescription_data['medicines']:
        data.append([item['medicine_name'], item['dosage'], item['form'], item['instructions']])

    table = Table(data, colWidths=[4*cm, 3*cm, 3*cm, 6*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'ArabicFont-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'ArabicFont'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(table)
    story.append(Spacer(1, 1*cm))

    # Doctor Signature (Optional)
    if clinic_settings and clinic_settings.get("signature_path") and os.path.exists(clinic_settings["signature_path"]):
        if print_settings and print_settings.get("print_template_style") != "النموذج 2 (بدون توقيع)":
            signature_img = Image(clinic_settings["signature_path"], width=4*cm, height=2*cm)
            signature_img.hAlign = 'RIGHT'
            story.append(signature_img)
            story.append(Paragraph("توقيع الطبيب", styles['ArabicNormal']))

    doc.build(story)


