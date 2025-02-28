from flask import Flask


def create_app() -> Flask:
    """
    Create and configure the Flask application.
    
    Returns:
        The configured Flask application
    """
    app = Flask(__name__)
    
    from app.routes import register_routes
    register_routes(app)
    
    return app 