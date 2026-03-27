import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from app.routes import register_blueprints
from .models.logs import parse_message


def create_app(config_name=None):
    """Application factory"""
    app = Flask(__name__)

    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'development')

    from app.config import config
    app.config.from_object(config[config_name])

    # Apply ProxyFix if configured
    proxy_level = app.config.get('PROXY_LEVEL', 0)
    if proxy_level > 0:
        app.wsgi_app = ProxyFix(
            app.wsgi_app,
            x_for=proxy_level,
            x_proto=proxy_level,
            x_host=proxy_level,
            x_prefix=proxy_level
        )

    @app.context_processor
    def add_parse_message():
        return {"parse_message": parse_message}

    # Register blueprints
    register_blueprints(app)

    return app
