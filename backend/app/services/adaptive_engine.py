"""Adaptive engine for question selection and ability estimation."""
import random
from typing import List, Optional, Tuple
import logging

from app.models.question_model import Question
from app.models.session_model import UserSession, QuestionHistoryItem
from app.services.irt_model import update_ability, calculate_probability
from app.services.mongodb_repository import repository

logger = logging.getLogger(__name__)


class AdaptiveEngine:
    """Adaptive testing engine using IRT-based question selection."""
    
    def __init__(
        self,
        initial_ability: float = 0.5,
        learning_rate: float = 0.1,
        difficulty_range: float = 0.15,
        expanded_difficulty_range: float = 0.3,
        min_difficulty: float = 0.1,
        max_difficulty: float = 1.0,
        questions_per_session: int = 10
    ):
        """
        Initialize the adaptive engine.
        
        Args:
            initial_ability: Starting ability score
            learning_rate: Learning rate for ability updates
            difficulty_range: Initial difficulty range (±)
            expanded_difficulty_range: Expanded range when few questions available
            min_difficulty: Minimum question difficulty
            max_difficulty: Maximum question difficulty
            questions_per_session: Number of questions per session
        """
        self.initial_ability = initial_ability
        self.learning_rate = learning_rate
        self.difficulty_range = difficulty_range
        self.expanded_difficulty_range = expanded_difficulty_range
        self.min_difficulty = min_difficulty
        self.max_difficulty = max_difficulty
        self.questions_per_session = questions_per_session
    
    def create_new_session(self, user_id: Optional[str] = None) -> UserSession:
        """Create a new user session with initial ability."""
        session = UserSession(
            user_id=user_id,
            current_ability=self.initial_ability
        )
        
        # Save to database
        repository.create_user_session(session.to_dict())
        
        logger.info(f"Created new session: {session.session_id} with ability {self.initial_ability}")
        return session
    
    def get_next_question(self, session: UserSession) -> Optional[Question]:
        """
        Get the next question based on current ability.
        
        Args:
            session: Current user session
        
        Returns:
            Next question or None if no questions available
        """
        # Get asked question IDs
        asked_ids = {item.question_id for item in session.question_history}
        
        # Calculate target difficulty based on current ability
        target_difficulty = session.current_ability
        
        # Try initial difficulty range
        min_diff = max(self.min_difficulty, target_difficulty - self.difficulty_range)
        max_diff = min(self.max_difficulty, target_difficulty + self.difficulty_range)
        
        available_questions = repository.get_questions_by_difficulty_range(min_diff, max_diff)
        
        # Filter out already asked questions
        new_questions = [q for q in available_questions if q.id not in asked_ids]
        
        # If not enough questions, expand difficulty range
        if len(new_questions) < 3:
            logger.debug(
                f"Expanding difficulty range for session {session.session_id}: "
                f"only {len(new_questions)} questions available"
            )
            
            min_diff = max(self.min_difficulty, target_difficulty - self.expanded_difficulty_range)
            max_diff = min(self.max_difficulty, target_difficulty + self.expanded_difficulty_range)
            
            available_questions = repository.get_questions_by_difficulty_range(min_diff, max_diff)
            new_questions = [q for q in available_questions if q.id not in asked_ids]
        
        # If still not enough, get any unasked question
        if len(new_questions) < 3:
            all_questions = repository.get_all_questions()
            unasked = [q for q in all_questions if q.id not in asked_ids]
            
            if unasked:
                new_questions = unasked
                logger.debug(
                    f"Using fallback questions for session {session.session_id}: "
                    f"{len(new_questions)} available"
                )
        
        # Select random question from available pool
        if new_questions:
            question = random.choice(new_questions)
            logger.debug(
                f"Selected question {question.id} (difficulty={question.difficulty:.3f}) "
                f"for session {session.session_id} (ability={session.current_ability:.3f})"
            )
            return question
        
        logger.warning(f"No questions available for session {session.session_id}")
        return None
    
    def submit_answer(
        self,
        session: UserSession,
        question: Question,
        answer_index: int
    ) -> Tuple[bool, UserSession, Optional[Question]]:
        """
        Process an answer submission and update session state.
        
        Args:
            session: Current user session
            question: The question that was answered
            answer_index: The index of the selected answer
        
        Returns:
            Tuple of (is_correct, updated_session, next_question)
        """
        # Check if answer is correct
        is_correct = question.is_correct(answer_index)
        
        # Update ability score
        new_ability = update_ability(
            session.current_ability,
            is_correct,
            question.difficulty,
            self.learning_rate
        )
        
        # Update session
        session.update_ability(new_ability)
        session.add_question_response(
            question_id=question.id,
            difficulty=question.difficulty,
            is_correct=is_correct
        )
        
        # Update database
        repository.update_user_session(session)
        
        logger.info(
            f"Answer submitted for session {session.session_id}: "
            f"correct={is_correct}, new_ability={new_ability:.3f}"
        )
        
        # Get next question
        next_question = None
        if not session.is_complete():
            next_question = self.get_next_question(session)
        
        return is_correct, session, next_question
    
    def calculate_difficulty_for_next(self, session: UserSession) -> float:
        """
        Calculate the target difficulty for the next question.
        
        Args:
            session: Current user session
        
        Returns:
            Target difficulty score
        """
        return session.current_ability
    
    def get_session_summary(self, session: UserSession) -> dict:
        """
        Get a summary of the session performance.
        
        Args:
            session: User session
        
        Returns:
            Dictionary with session summary
        """
        accuracy = (
            session.correct_count / session.questions_asked
            if session.questions_asked > 0 else 0
        )
        
        # Calculate topic breakdown
        topic_stats = {}
        for item in session.question_history:
            question = repository.get_question_by_id(item.question_id)
            if question:
                topic = question.topic
                if topic not in topic_stats:
                    topic_stats[topic] = {"correct": 0, "total": 0}
                topic_stats[topic]["total"] += 1
                if item.is_correct:
                    topic_stats[topic]["correct"] += 1
        
        return {
            "session_id": session.session_id,
            "user_id": session.user_id,
            "start_time": session.start_time.isoformat() if session.start_time else None,
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "questions_asked": session.questions_asked,
            "correct_count": session.correct_count,
            "incorrect_count": session.incorrect_count,
            "accuracy": accuracy,
            "current_ability": session.current_ability,
            "topic_stats": topic_stats
        }


# Global engine instance
adaptive_engine = AdaptiveEngine()
