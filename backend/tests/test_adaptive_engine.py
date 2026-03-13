"""Tests for adaptive engine."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.models.question_model import Question
from app.models.session_model import UserSession
from app.services.adaptive_engine import AdaptiveEngine


class TestAdaptiveEngine:
    """Test adaptive engine functions."""
    
    def test_create_new_session(self):
        """Test creating a new session."""
        engine = AdaptiveEngine()
        session = engine.create_new_session(user_id="test_user")
        
        assert session.session_id is not None
        assert session.user_id == "test_user"
        assert session.current_ability == 0.5
        assert len(session.question_history) == 0
        assert session.correct_count == 0
        assert session.incorrect_count == 0
        assert session.questions_asked == 0
    
    def test_get_next_question_initial(self):
        """Test getting first question."""
        engine = AdaptiveEngine()
        session = engine.create_new_session()
        
        question = engine.get_next_question(session)
        
        assert question is not None
        assert question.difficulty >= 0.1
        assert question.difficulty <= 1.0
    
    def test_get_next_question_excludes_asked(self):
        """Test that asked questions are excluded."""
        engine = AdaptiveEngine()
        session = engine.create_new_session()
        
        # Get first question
        question1 = engine.get_next_question(session)
        assert question1 is not None
        
        # Add to history
        session.add_question_response(
            question_id=question1.id,
            difficulty=question1.difficulty,
            is_correct=True
        )
        
        # Get next question - should be different
        question2 = engine.get_next_question(session)
        assert question2 is not None
        assert question2.id != question1.id
    
    def test_submit_answer_increments_count(self):
        """Test that answer submission increments counters."""
        engine = AdaptiveEngine()
        session = engine.create_new_session()
        
        question = engine.get_next_question(session)
        assert question is not None
        
        # Submit correct answer
        is_correct, updated_session, next_question = engine.submit_answer(
            session, question, question.correct_answer
        )
        
        assert is_correct
        assert updated_session.correct_count == 1
        assert updated_session.incorrect_count == 0
        assert updated_session.questions_asked == 1
    
    def test_submit_answer_updates_ability(self):
        """Test that answer submission updates ability."""
        engine = AdaptiveEngine()
        session = engine.create_new_session()
        
        question = engine.get_next_question(session)
        
        # Submit correct answer
        is_correct, updated_session, _ = engine.submit_answer(
            session, question, question.correct_answer
        )
        
        assert is_correct
        assert updated_session.current_ability > 0.5
    
    def test_session_complete_after_10_questions(self):
        """Test that session is complete after 10 questions."""
        engine = AdaptiveEngine(questions_per_session=10)
        session = engine.create_new_session()
        
        # Simulate 10 questions
        for i in range(10):
            question = engine.get_next_question(session)
            if question:
                engine.submit_answer(session, question, question.correct_answer)
        
        assert session.is_complete()
        assert session.questions_asked == 10
    
    def test_ability_bounds_preserved(self):
        """Test that ability stays within bounds after multiple answers."""
        engine = AdaptiveEngine()
        session = engine.create_new_session()
        
        # Simulate many questions
        for _ in range(20):
            question = engine.get_next_question(session)
            if question:
                is_correct = session.current_ability > question.difficulty
                engine.submit_answer(session, question, question.correct_answer if is_correct else 0)
        
        assert 0.0 <= session.current_ability <= 1.0
