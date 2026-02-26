import qrcode
import os
import uuid
import string
import random
from reportlab.lib.pagesizes import letter, landscape
from reportlab.pdfgen import canvas
from reportlab.lib import colors

def generate_unique_id():
    """Generates a secure random verification ID like CERT2026-8X9A3K"""
    year = 2026
    chars = string.ascii_uppercase + string.digits
    suffix = ''.join(random.choices(chars, k=6))
    return f"CERT{year}-{suffix}"

def generate_qr_code(verification_id, base_url="http://127.0.0.1:5000"):
    """Generates a QR code linked to the verification page"""
    verify_url = f"{base_url}/verify/{verification_id}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(verify_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save the QR code
    qr_filename = f"{verification_id}.png"
    qr_dir = os.path.join('static', 'qrcodes')
    if not os.path.exists(qr_dir):
        os.makedirs(qr_dir)
    
    qr_path = os.path.join(qr_dir, qr_filename)
    img.save(qr_path)
    return qr_path

def generate_certificate_pdf(student_name, course, college_name, issue_date, verification_id, qr_path):
    """Generates a premium PDF certificate"""
    pdf_filename = f"{verification_id}.pdf"
    pdf_dir = os.path.join('static', 'certificates')
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
    
    pdf_path = os.path.join(pdf_dir, pdf_filename)
    
    c = canvas.Canvas(pdf_path, pagesize=landscape(letter))
    width, height = landscape(letter)
    
    # Background color and border
    c.setStrokeColor(colors.gold)
    c.setLineWidth(5)
    c.rect(20, 20, width-40, height-40)
    
    # Header
    c.setFont("Helvetica-Bold", 40)
    c.drawCentredString(width/2, height-80, "CERTIFICATE OF ACHIEVEMENT")
    
    c.setFont("Helvetica", 18)
    c.drawCentredString(width/2, height-120, "This is to certify that")
    
    # Student Name
    c.setFont("Helvetica-Bold", 35)
    c.drawCentredString(width/2, height-180, student_name)
    
    c.setFont("Helvetica", 18)
    c.drawCentredString(width/2, height-230, "from")
    
    # College Name
    c.setFont("Helvetica-Bold", 25)
    c.drawCentredString(width/2, height-270, college_name)
    
    c.setFont("Helvetica", 18)
    c.drawCentredString(width/2, height-320, "has successfully completed the course")
    
    # Course
    c.setFont("Helvetica-Bold", 25)
    c.drawCentredString(width/2, height-370, course)
    
    # Details
    c.setFont("Helvetica", 15)
    c.drawString(100, 100, f"Issue Date: {issue_date}")
    c.drawString(100, 80, f"Verification ID: {verification_id}")
    
    # QR Code
    if os.path.exists(qr_path):
        c.drawImage(qr_path, width-200, 50, width=150, height=150)
    
    c.showPage()
    c.save()
    
    return pdf_path
