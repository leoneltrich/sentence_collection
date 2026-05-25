from flask import Blueprint, request, jsonify, render_template, Response
import io
import csv
from sqlalchemy.exc import IntegrityError
from .models import db, Sentence, Category
from .utils import normalize_sentence
from . import limiter

api = Blueprint('api', __name__)

@api.route('/')
def index():
    return render_template('index.html')

@api.route('/submit')
def submit_page():
    return render_template('submit.html')

@api.route('/download/all')
def download_all():
    """
    Download all sentences as CSV
    ---
    responses:
      200:
        description: A CSV file containing all sentences
    """
    from sqlalchemy.orm import joinedload
    sentences = Sentence.query.options(joinedload(Sentence.giveaway_entry), joinedload(Sentence.category)).all()
    
    def generate():
        data = io.StringIO()
        writer = csv.writer(data)
        writer.writerow(['ID', 'Original Text', 'Normalized Text', 'Category', 'Giveaway Email'])
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        for s in sentences:
            email = s.giveaway_entry.email if s.giveaway_entry else ''
            writer.writerow([s.id, s.original_text, s.normalized_text, s.category.name, email])
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    return Response(
        generate(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=all_sentences.csv'}
    )

@api.route('/download/category/<int:category_id>')
def download_category(category_id):
    """
    Download sentences from a specific category as CSV
    ---
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: A CSV file containing sentences from the category
      404:
        description: Category not found
    """
    category = Category.query.get_or_404(category_id)
    sentences = Sentence.query.filter_by(category_id=category_id).all()
    
    def generate():
        data = io.StringIO()
        writer = csv.writer(data)
        writer.writerow(['ID', 'Original Text', 'Normalized Text'])
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        for s in sentences:
            writer.writerow([s.id, s.original_text, s.normalized_text])
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    filename = f"category_{category.name.lower().replace(' ', '_')}_sentences.csv"
    return Response(
        generate(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )

@api.route('/categories', methods=['GET'])
def get_categories():
    """
    List all categories
    ---
    responses:
      200:
        description: A list of categories
    """
    categories = Category.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description
    } for c in categories])

@api.route('/categories', methods=['POST'])
@limiter.limit("10 per minute")
def add_category():
    """
    Create a new category
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            description:
              type: string
    responses:
      201:
        description: Category created
      400:
        description: Invalid input
      409:
        description: Category already exists
    """
    data = request.get_json()
    if not data or 'name' not in data:
        return jsonify({'error': 'Category name is required'}), 400
    
    try:
        new_category = Category(
            name=data['name'],
            description=data.get('description', '')
        )
        db.session.add(new_category)
        db.session.commit()
        return jsonify({'message': 'Category added successfully', 'id': new_category.id}), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Category already exists'}), 409

@api.route('/sentences', methods=['POST'])
@limiter.limit("20 per minute")
def add_sentence():
    """
    Add a new sentence
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            text:
              type: string
            category_id:
              type: integer
            email:
              type: string
    responses:
      201:
        description: Sentence added
      400:
        description: Invalid input
      404:
        description: Category not found
      409:
        description: Sentence already exists (normalized check)
    """
    data = request.get_json()
    if not data or 'text' not in data or 'category_id' not in data:
        return jsonify({'error': 'Sentence text and category_id are required'}), 400
    
    original_text = data['text']
    normalized_text = normalize_sentence(original_text)
    category_id = data['category_id']
    email = data.get('email')
    
    # Verify category exists
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Category not found'}), 404

    try:
        new_sentence = Sentence(
            original_text=original_text,
            normalized_text=normalized_text,
            category_id=category_id
        )
        db.session.add(new_sentence)
        db.session.flush() # Get the ID before committing

        if email:
            from .models import GiveawayEntry
            entry = GiveawayEntry(email=email, sentence_id=new_sentence.id)
            db.session.add(entry)

        db.session.commit()
        return jsonify({'message': 'Sentence added successfully', 'id': new_sentence.id}), 201
    except IntegrityError:
        # This handles concurrent submissions of the same normalized sentence
        db.session.rollback()
        return jsonify({'error': 'Sentence already existed and was not added'}), 409

@api.route('/stats', methods=['GET'])
@limiter.limit("60 per minute")
def get_stats():
    """
    Get sentence statistics
    ---
    responses:
      200:
        description: Statistics including total count and per-category breakdown
    """
    total_count = Sentence.query.count()
    
    # Sentence count per category
    categories = Category.query.all()
    category_stats = []
    for cat in categories:
        count = Sentence.query.filter_by(category_id=cat.id).count()
        category_stats.append({
            'category_id': cat.id,
            'category_name': cat.name,
            'count': count
        })
        
    return jsonify({
        'total_sentences': total_count,
        'category_stats': category_stats
    })
