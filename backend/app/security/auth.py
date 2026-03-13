"""API key authentication utilities."""
import bcrypt
import logging
from functools import wraps
from flask import request, jsonify
from app.db import get_db

logger = logging.getLogger(__name__)


def hash_api_key(api_key):
    """Hash an API key using bcrypt."""
    return bcrypt.hashpw(api_key.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_api_key(api_key, hashed_key):
    """Verify an API key against its hash."""
    return bcrypt.checkpw(api_key.encode("utf-8"), hashed_key.encode("utf-8"))


def get_api_key_from_request():
    """Extract API key from request headers."""
    return request.headers.get("X-API-KEY")


def validate_api_key(api_key):
    """Validate an API key against the database."""
    if not api_key:
        return False
    
    db = get_db()
    api_key_doc = db.api_keys.find_one({"key": api_key, "active": True})
    
    if api_key_doc:
        logger.debug(f"API key validated for key: {api_key[:8]}...")
        return True
    
    logger.warning(f"Invalid or inactive API key: {api_key}")
    return False


def require_api_key(f):
    """Decorator to require API key authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = get_api_key_from_request()
        
        if not api_key:
            return jsonify({"error": "Invalid API key"}), 401
        
        if not validate_api_key(api_key):
            return jsonify({"error": "Invalid API key"}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


def init_api_keys(api_keys_list):
    """Initialize API keys in the database."""
    db = get_db()
    
    for api_key in api_keys_list:
        hashed_key = hash_api_key(api_key)
        
        # Check if key already exists
        existing = db.api_keys.find_one({"key": hashed_key})
        if not existing:
            db.api_keys.insert_one({
                "key": hashed_key,
                "name": f"key-{len(api_keys_list)}",
                "permissions": ["read", "write"],
                "created_at": db.api_keys.count_documents({}),
                "active": True
            })
            logger.info(f"API key initialized: {api_key[:8]}...")
    
    logger.info(f"Initialized {len(api_keys_list)} API keys")
