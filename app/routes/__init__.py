from flask import Blueprint

# Import blueprints
from app.routes.main import bp as main_bp
from app.routes.chat import bp as chat_bp
from app.routes.search import bp as search_bp


def register_blueprints(app):
    """Register all blueprints with the Flask app"""
    # Register chat first (more specific routes before less specific)
    app.register_blueprint(chat_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(main_bp)
