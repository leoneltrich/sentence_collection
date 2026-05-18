import os
from flask import Flask
from flasgger import Swagger
from .models import db

def create_app(test_config=None):
    app = Flask(__name__)
    
    # Configuration
    if test_config is None:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///local.db')
    else:
        app.config.update(test_config)
        
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Initialize extensions
    db.init_app(app)
    Swagger(app)
    
    # Register blueprints
    from .routes import api
    app.register_blueprint(api, url_prefix='/')
    
    return app