from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
import hashlib
import re
from .models import db, QuizResult
from . import limiter

api = Blueprint('api', __name__)

@api.route('/quiz/submit', methods=['POST'])
@limiter.limit("10 per minute")
def submit_quiz():
    """
    Submit quiz results
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            email:
              type: string
            score:
              type: integer
            total:
              type: integer
            level:
              type: string
    responses:
      201:
        description: Quiz result stored
      400:
        description: Invalid input or email already used
    """
    data = request.get_json()
    if not data or 'email' not in data or 'score' not in data or 'level' not in data:
        return jsonify({'error': 'Missing required quiz data'}), 400
    
    email_raw = data['email']
    # 1. Converted to lowercase
    email_lower = email_raw.lower()
    # 2. Stripped of any leading/trailing whitespace
    email_stripped = email_lower.strip()
    
    # Simple email validation
    if not email_stripped or not re.match(r"[^@]+@[^@]+\.[^@]+", email_stripped):
        return jsonify({'error': 'Invalid email address'}), 400
    
    # 3. Encoded as UTF-8 bytes
    email_bytes = email_stripped.encode('utf-8')
    # 4. Hashed using standard SHA-256 to produce a 64-character hexadecimal representation
    hashed_email = hashlib.sha256(email_bytes).hexdigest()
    
    # Check if this email hash already exists in DB
    existing = QuizResult.query.filter_by(email=hashed_email).first()
    if existing:
        return jsonify({'error': 'This email has already been used to take the quiz.'}), 400
        
    try:
        new_result = QuizResult(
            email=hashed_email,
            score=data['score'],
            total_questions=data.get('total', 10),
            level=data['level']
        )
        db.session.add(new_result)
        db.session.commit()
        return jsonify({'message': 'Quiz results saved. Thank you for participating!'}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'This email has already been used to take the quiz.'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
