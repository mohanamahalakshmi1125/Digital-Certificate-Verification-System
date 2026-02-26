from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from models import db, Student, Certificate
from utils import generate_unique_id, generate_qr_code, generate_certificate_pdf
import os
from datetime import datetime, timezone
from functools import wraps

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///certificates.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'supersecretkey' # In production, use a secure key

db.init_app(app)

# Create database tables
with app.app_context():
    db.create_all()

# Auth Decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_logged_in' not in session:
            flash('Please log in first.')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/verify', methods=['POST'])
def verify_search():
    verification_id = request.form.get('verification_id')
    return redirect(url_for('verify_result', verification_id=verification_id))

@app.route('/verify/<verification_id>')
def verify_result(verification_id):
    certificate = Certificate.query.filter_by(unique_verification_id=verification_id).first()
    if certificate:
        student = Student.query.get(certificate.student_id)
        return render_template('verify.html', certificate=certificate, student=student)
    else:
        return render_template('verify.html', error="Invalid Verification ID")

# Admin Authentication
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == 'sakthi' and password == 'sakthi123':
            session['admin_logged_in'] = True
            flash('Logged in successfully!')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials!')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully!')
    return redirect(url_for('index'))

@app.route('/admin')
@login_required
def admin_dashboard():
    students = Student.query.all()
    certificates = Certificate.query.all()
    return render_template('admin_dashboard.html', students=students, certificates=certificates)

@app.route('/admin/add_student', methods=['GET', 'POST'])
@login_required
def add_student():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        course = request.form.get('course')
        college = request.form.get('college')
        year = request.form.get('year')
        
        new_student = Student(name=name, email=email, course=course, college=college, year=year)
        db.session.add(new_student)
        db.session.commit()
        flash('Student added successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('add_student.html')

@app.route('/admin/issue_certificate', methods=['GET', 'POST'])
@login_required
def issue_certificate():
    students = Student.query.all()
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        cert_type = request.form.get('certificate_type')
        
        student = Student.query.get(student_id)
        if not student:
            flash('Student not found!')
            return redirect(url_for('admin_dashboard'))
        
        # Generate ID, QR, and PDF
        verification_id = generate_unique_id()
        qr_path = generate_qr_code(verification_id)
        pdf_path = generate_certificate_pdf(student.name, student.course, student.college, datetime.now(timezone.utc).date(), verification_id, qr_path)
        
        new_cert = Certificate(
            student_id=student_id,
            certificate_type=cert_type,
            unique_verification_id=verification_id,
            qr_code_path=qr_path,
            status='Active'
        )
        db.session.add(new_cert)
        db.session.commit()
        
        flash(f'Certificate issued successfully! ID: {verification_id}')
        return redirect(url_for('admin_dashboard'))
        
    return render_template('issue_certificate.html', students=students)

@app.route('/admin/revoke/<int:cert_id>')
@login_required
def revoke_certificate(cert_id):
    cert = Certificate.query.get(cert_id)
    if cert:
        cert.status = 'Revoked'
        db.session.commit()
        flash('Certificate revoked!')
    return redirect(url_for('admin_dashboard'))

@app.route('/download/<verification_id>')
def download_certificate(verification_id):
    filename = f"{verification_id}.pdf"
    return send_from_directory(os.path.join('static', 'certificates'), filename)

if __name__ == '__main__':
    app.run(debug=True)
