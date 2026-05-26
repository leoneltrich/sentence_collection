import os
from flask import Flask
from flasgger import Swagger
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from .models import db

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://",
)

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Security: Limit request size to 1MB to prevent memory exhaustion
    app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024
    
    # Configuration
    if test_config is None:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
    else:
        app.config.update(test_config)
        
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    Swagger(app)
    limiter.init_app(app)
    
    # Register blueprints
    from .routes import api
    app.register_blueprint(api, url_prefix='/')

    @app.route('/')
    def index():
        from flask import render_template
        return render_template('landing.html')

    @app.route('/admin')
    def admin_page():
        from flask import render_template
        return render_template('index.html')

    @app.route('/submit')
    def submit_page():
        from flask import render_template
        return render_template('submit.html')

    @app.route('/quiz')
    def quiz_page():
        from flask import render_template
        return render_template('quiz.html')
    
    return app