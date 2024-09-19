from flask import Flask
from config.database import init_db
from models import init_models
from app.routes import init_routes



def create_app():
    app = Flask(__name__)

    app.config['JSON_SORT_KEYS'] = False
    app.config['JSON_AS_ASCII'] = False

    # Initialize database
    init_db(app)
    
    # Initialize models
    init_models()

    # Register routes
    init_routes(app)
    
    return app
