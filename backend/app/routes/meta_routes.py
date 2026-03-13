"""Meta routes for health, metrics, and other utilities."""
from flask import Blueprint, jsonify
import logging

from app.security.auth import require_api_key
from app.security.rate_limiter import limiter
from app.monitoring.metrics import metrics_collector

logger = logging.getLogger(__name__)
meta_bp = Blueprint("meta", __name__)


@meta_bp.route("/health", methods=["GET"])
def health_check():
    """
    Health check endpoint.
    
    Response:
        {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z"
        }
    """
    return jsonify({
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z"
    })


@meta_bp.route("/metrics", methods=["GET"])
@require_api_key
@limiter.limit("100 per minute")
def get_metrics():
    """
    Get Prometheus metrics.
    
    Response:
        Metrics in Prometheus text format
    """
    return metrics_collector.get_metrics(), 200, {"Content-Type": "text/plain; charset=utf-8"}


@meta_bp.route("/stats", methods=["GET"])
@require_api_key
@limiter.limit("100 per minute")
def get_stats():
    """
    Get system statistics.
    
    Response:
        {
            "total_questions": 100,
            "total_sessions": 50,
            "active_sessions": 5
        }
    """
    from app.db import get_db
    db = get_db()
    
    total_questions = db.questions.count_documents({})
    total_sessions = db.user_sessions.count_documents({})
    active_sessions = db.user_sessions.count_documents({"ended": {"$ne": True}})
    
    return jsonify({
        "total_questions": total_questions,
        "total_sessions": total_sessions,
        "active_sessions": active_sessions
    })
