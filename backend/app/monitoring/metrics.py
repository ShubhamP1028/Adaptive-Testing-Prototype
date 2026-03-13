"""Metrics collection for Prometheus."""
import time
import logging
from functools import wraps
from flask import request, g

from prometheus_client import (
    Counter, Histogram, Gauge, generate_latest,
    CONTENT_TYPE_LATEST, CollectorRegistry
)

logger = logging.getLogger(__name__)

# Create custom registry
registry = CollectorRegistry()

# Define metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"],
    registry=registry
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["endpoint"],
    registry=registry
)

sessions_active = Gauge(
    "sessions_active",
    "Number of active sessions",
    registry=registry
)

session_question_count = Gauge(
    "session_question_count",
    "Number of questions asked in session",
    ["session_id"],
    registry=registry
)

ability_estimate = Gauge(
    "ability_estimate",
    "Current ability estimate",
    ["session_id"],
    registry=registry
)

questions_answered_total = Counter(
    "questions_answered_total",
    "Total questions answered",
    ["correct"],
    registry=registry
)

openai_api_calls_total = Counter(
    "openai_api_calls_total",
    "Total OpenAI API calls",
    ["success"],
    registry=registry
)

openai_api_duration_seconds = Histogram(
    "openai_api_duration_seconds",
    "OpenAI API call duration in seconds",
    registry=registry
)


class MetricsCollector:
    """Collector for application metrics."""
    
    def __init__(self):
        """Initialize the metrics collector."""
        self.registry = registry
    
    def before_request(self):
        """Record start time for request."""
        g.start_time = time.time()
    
    def after_request(self, response):
        """Record request metrics after response."""
        if hasattr(g, "start_time"):
            duration = time.time() - g.start_time
            
            # Record HTTP request metrics
            http_requests_total.labels(
                method=request.method,
                endpoint=request.path,
                status=response.status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                endpoint=request.path
            ).observe(duration)
        
        return response
    
    def record_question_response(self, is_correct: bool, difficulty: float):
        """Record a question response."""
        questions_answered_total.labels(correct=str(is_correct)).inc()
    
    def record_openai_api_call(self, duration: float, success: bool):
        """Record an OpenAI API call."""
        openai_api_calls_total.labels(success=str(success)).inc()
        openai_api_duration_seconds.observe(duration)
    
    def update_session_metrics(self, session_id: str, questions_count: int, ability: float):
        """Update session-specific metrics."""
        session_question_count.labels(session_id=session_id).set(questions_count)
        ability_estimate.labels(session_id=session_id).set(ability)
    
    def get_metrics(self) -> str:
        """Get metrics in Prometheus format."""
        return generate_latest(self.registry).decode("utf-8")


# Global metrics collector instance
metrics_collector = MetricsCollector()


def setup_metrics(app):
    """Setup metrics collection for Flask app."""
    # Register before_request and after_request hooks
    app.before_request(metrics_collector.before_request)
    app.after_request(metrics_collector.after_request)
    
    # Expose metrics endpoint
    @app.route("/metrics")
    def metrics():
        return metrics_collector.get_metrics(), 200, {"Content-Type": CONTENT_TYPE_LATEST}
    
    logger.info("Metrics collection initialized")
