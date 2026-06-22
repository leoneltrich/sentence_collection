from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class QuizResult(db.Model):
    __tablename__ = 'quiz_results'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), nullable=False, unique=True)
    score = db.Column(db.Integer, nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    level = db.Column(db.String(50), nullable=False) # beginner, intermediate, expert
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())