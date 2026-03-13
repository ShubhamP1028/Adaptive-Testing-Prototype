"""Flask application factory and main entry point."""
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from app.config import config
from app.db import init_db
from app.security.rate_limiter import rate_limiter
from app.routes.session_routes import session_bp
from app.routes.question_routes import question_bp
from app.routes.meta_routes import meta_bp
from app.monitoring.metrics import setup_metrics


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    
    # Load configuration
    app.config.from_object(config)
    
    # Initialize database
    init_db(app)
    
    # Setup metrics
    setup_metrics(app)
    
    # Register blueprints
    app.register_blueprint(session_bp, url_prefix="/api")
    app.register_blueprint(question_bp, url_prefix="/api")
    app.register_blueprint(meta_bp, url_prefix="/api")
    
    # Register error handlers
    @app.errorhandler(401)
    def unauthorized(error):
        return {"error": "Invalid API key"}, 401
    
    @app.errorhandler(429)
    def rate_limit_exceeded(error):
        return {"error": "Rate limit exceeded"}, 429
    
    @app.errorhandler(404)
    def not_found(error):
        return {"error": str(error)}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {"error": "Internal server error"}, 500
    
    return app


app = create_app()


if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
