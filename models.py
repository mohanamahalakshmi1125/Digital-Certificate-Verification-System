from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    course = db.Column(db.String(100), nullable=False)
    college = db.Column(db.String(150), nullable=True) # Added College Name
    year = db.Column(db.Integer, nullable=False)
    certificates = db.relationship('Certificate', backref='student', lazy=True)

class Certificate(db.Model):
    __tablename__ = 'certificates'
    certificate_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.student_id'), nullable=False)
    issue_date = db.Column(db.Date, default=datetime.utcnow().date)
    certificate_type = db.Column(db.String(50), nullable=False)
    unique_verification_id = db.Column(db.String(50), unique=True, nullable=False)
    qr_code_path = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='Active') # Active / Revoked
