from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Category(db.Model):
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    description = db.Column(db.String(255), nullable=True)
    
    sentences = db.relationship('Sentence', backref='category', lazy=True)

class Sentence(db.Model):
    __tablename__ = 'sentences'
    
    id = db.Column(db.Integer, primary_key=True)
    original_text = db.Column(db.Text, nullable=False)
    normalized_text = db.Column(db.Text, nullable=False, unique=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)