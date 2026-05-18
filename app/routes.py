from flask import Blueprint, request, jsonify, render_template, Response
import io
import csv
from sqlalchemy.exc import IntegrityError
from .models import db, Sentence, Category
from .utils import normalize_sentence

api = Blueprint('api', __name__)

@api.route('/')
def index():
    return render_template('index.html')

@api.route('/download/all')
def download_all():
    sentences = Sentence.query.all()
    
    def generate():
        data = io.StringIO()
        writer = csv.writer(data)
        writer.writerow(['ID', 'Original Text', 'Normalized Text', 'Category'])
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        for s in sentences:
            writer.writerow([s.id, s.original_text, s.normalized_text, s.category.name])
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
    categories = Category.query.all()
    return jsonify([{
        'id': c.id,
        'name': c.name,
        'description': c.description
    } for c in categories])

@api.route('/categories', methods=['POST'])
def add_category():
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
def add_sentence():
    data = request.get_json()
    if not data or 'text' not in data or 'category_id' not in data:
        return jsonify({'error': 'Sentence text and category_id are required'}), 400
    
    original_text = data['text']
    normalized_text = normalize_sentence(original_text)
    category_id = data['category_id']
    
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
        db.session.commit()
        return jsonify({'message': 'Sentence added successfully', 'id': new_sentence.id}), 201
    except IntegrityError:
        # This handles concurrent submissions of the same normalized sentence
        db.session.rollback()
        return jsonify({'error': 'Sentence already existed and was not added'}), 409

@api.route('/stats', methods=['GET'])
def get_stats():
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
