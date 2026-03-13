"""Session management routes."""
from flask import Blueprint, request, jsonify
import logging

from app.security.auth import require_api_key, get_api_key_from_request
from app.security.rate_limiter import limiter
from app.services.adaptive_engine import adaptive_engine
from app.services.ai_service import ai_service

logger = logging.getLogger(__name__)
session_bp = Blueprint("session", __name__)


@session_bp.route("/start-session", methods=["POST"])
@require_api_key
@limiter.limit("100 per minute")
def start_session():
    """
    Start a new assessment session.
    
    Request Body:
        {
            "user_id": "optional-user-id"
        }
    
    Response:
        {
            "session_id": "uuid",
            "next_question": {
                "id": "uuid",
                "text": "Question text",
                "options": ["A", "B", "C", "D"],
                "difficulty": 0.5,
                "topic": "Algebra",
                "tags": ["quadratic"]
            }
        }
    """
    data = request.get_json() or {}
    user_id = data.get("user_id")
    
    # Create new session
    session = adaptive_engine.create_new_session(user_id=user_id)
    
    # Get first question
    next_question = adaptive_engine.get_next_question(session)
    
    if not next_question:
        return jsonify({
            "error": "No questions available in the database"
        }), 404
    
    logger.info(f"Session started: {session.session_id}")
    
    return jsonify({
        "session_id": session.session_id,
        "next_question": {
            "id": next_question.id,
            "text": next_question.text,
            "options": next_question.options,
            "difficulty": next_question.difficulty,
            "topic": next_question.topic,
            "tags": next_question.tags
        }
    })


@session_bp.route("/next-question", methods=["GET"])
@require_api_key
@limiter.limit("100 per minute")
def next_question():
    """
    Get the next question for a session.
    
    Query Parameters:
        session_id: The session ID
    
    Response:
        {
            "id": "uuid",
            "text": "Question text",
            "options": ["A", "B", "C", "D"],
            "difficulty": 0.5,
            "topic": "Algebra",
            "tags": ["quadratic"]
        }
    """
    session_id = request.args.get("session_id")
    
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400
    
    # Get session
    session = adaptive_engine.get_user_session(session_id)
    
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    # Check if session is complete
    if session.is_complete():
        return jsonify({"error": "Session is complete"}), 400
    
    # Get next question
    next_question = adaptive_engine.get_next_question(session)
    
    if not next_question:
        return jsonify({"error": "No more questions available"}), 404
    
    return jsonify({
        "id": next_question.id,
        "text": next_question.text,
        "options": next_question.options,
        "difficulty": next_question.difficulty,
        "topic": next_question.topic,
        "tags": next_question.tags
    })


@session_bp.route("/submit-answer", methods=["POST"])
@require_api_key
@limiter.limit("100 per minute")
def submit_answer():
    """
    Submit an answer to a question.
    
    Request Body:
        {
            "session_id": "uuid",
            "question_id": "uuid",
            "answer_index": 0
        }
    
    Response:
        {
            "is_correct": true,
            "current_ability": 0.55,
            "next_question": {...} or null if session complete
        }
    """
    data = request.get_json()
    
    if not data:
        return jsonify({"error": "Request body is required"}), 400
    
    session_id = data.get("session_id")
    question_id = data.get("question_id")
    answer_index = data.get("answer_index")
    
    # Validate required fields
    if not all([session_id, question_id, answer_index is not None]):
        return jsonify({"error": "session_id, question_id, and answer_index are required"}), 400
    
    # Validate answer_index is an integer
    try:
        answer_index = int(answer_index)
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid answer index"}), 400
    
    # Get session
    session = adaptive_engine.get_user_session(session_id)
    
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    # Get question
    question = adaptive_engine.get_question_by_id(question_id)
    
    if not question:
        return jsonify({"error": "Question not found"}), 404
    
    # Validate answer_index
    if not (0 <= answer_index < len(question.options)):
        return jsonify({"error": "Invalid answer index"}), 400
    
    # Submit answer
    is_correct, updated_session, next_question = adaptive_engine.submit_answer(
        session, question, answer_index
    )
    
    response = {
        "is_correct": is_correct,
        "current_ability": updated_session.current_ability,
        "questions_asked": updated_session.questions_asked
    }
    
    if next_question:
        response["next_question"] = {
            "id": next_question.id,
            "text": next_question.text,
            "options": next_question.options,
            "difficulty": next_question.difficulty,
            "topic": next_question.topic,
            "tags": next_question.tags
        }
    
    return jsonify(response)


@session_bp.route("/result", methods=["GET"])
@require_api_key
@limiter.limit("100 per minute")
def get_result():
    """
    Get the session result and study plan.
    
    Query Parameters:
        session_id: The session ID
    
    Response:
        {
            "session_id": "uuid",
            "current_ability": 0.65,
            "accuracy": 0.7,
            "correct_count": 7,
            "incorrect_count": 3,
            "questions_asked": 10,
            "study_plan": {...} or null if not complete
        }
    """
    session_id = request.args.get("session_id")
    
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400
    
    # Get session
    session = adaptive_engine.get_user_session(session_id)
    
    if not session:
        return jsonify({"error": "Session not found"}), 404
    
    # Generate study plan if not already done
    if session.is_complete() and not session.study_plan:
        session = ai_service.generate_study_plan_for_session(session)
    
    # Set end time if not set
    if session.is_complete() and not session.end_time:
        from datetime import datetime
        session.end_time = datetime.utcnow()
        adaptive_engine.update_user_session(session)
    
    # Get summary
    summary = adaptive_engine.get_session_summary(session)
    
    response = {
        "session_id": session.session_id,
        "current_ability": session.current_ability,
        "accuracy": summary["accuracy"],
        "correct_count": session.correct_count,
        "incorrect_count": session.incorrect_count,
        "questions_asked": session.questions_asked,
        "topic_stats": summary["topic_stats"]
    }
    
    if session.study_plan:
        response["study_plan"] = {
            "steps": [
                {
                    "title": step.title,
                    "description": step.description,
                    "action_items": step.action_items
                }
                for step in session.study_plan.steps
            ]
        }
    
    return jsonify(response)
