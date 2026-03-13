"""Rate limiting utilities using Flask-Limiter."""
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import request

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per hour", "50 per minute"],
    storage_uri="memory://"
)


def get_api_key_limit_key():
    """Get rate limit key based on API key."""
    api_key = request.headers.get("X-API-KEY", "anonymous")
    return api_key


def init_rate_limiter(app):
    """Initialize rate limiter with Flask app."""
    limiter.init_app(app)
    return limiter
