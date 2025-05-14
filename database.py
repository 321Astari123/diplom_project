from datetime import datetime
from app import db

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    cover_filename = db.Column(db.String(200))
    format = db.Column(db.String(10), nullable=False)
    genre = db.Column(db.String(100))
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 