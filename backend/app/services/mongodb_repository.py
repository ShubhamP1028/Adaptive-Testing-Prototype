"""MongoDB repository for data persistence."""
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from app.db import get_db
from app.models.question_model import Question
from app.models.session_model import UserSession, QuestionHistoryItem, StudyPlan, StudyPlanStep

logger = logging.getLogger(__name__)


class MongoDBRepository:
    """Repository for MongoDB data operations."""
    
    def __init__(self):
        """Initialize the repository with database connection."""
        self.db = get_db()
        self.questions_collection = self.db.questions
        self.sessions_collection = self.db.user_sessions
        self.api_keys_collection = self.db.api_keys
    
    def get_questions_by_difficulty_range(
        self,
        min_difficulty: float,
        max_difficulty: float
    ) -> List[Question]:
        """Get questions within a difficulty range."""
        cursor = self.questions_collection.find({
            "difficulty": {"$gte": min_difficulty, "$lte": max_difficulty}
        })
        return [Question.from_dict(doc) for doc in cursor]
    
    def get_all_questions(self) -> List[Question]:
        """Get all questions from the database."""
        cursor = self.questions_collection.find()
        return [Question.from_dict(doc) for doc in cursor]
    
    def get_question_by_id(self, question_id: str) -> Optional[Question]:
        """Get a question by its ID."""
        doc = self.questions_collection.find_one({"_id": question_id})
        return Question.from_dict(doc) if doc else None
    
    def get_question_by_difficulty(self, difficulty: float) -> Optional[Question]:
        """Get a question with exact difficulty (for fallback)."""
        doc = self.questions_collection.find_one({"difficulty": difficulty})
        return Question.from_dict(doc) if doc else None
    
    def create_user_session(self, session_data: Dict[str, Any]) -> UserSession:
        """Create a new user session."""
        session = UserSession(
            session_id=session_data.get("session_id"),
            user_id=session_data.get("user_id")
        )
        
        doc = session.to_dict()
        self.sessions_collection.insert_one(doc)
        
        logger.info(f"Created new session: {session.session_id}")
        return session
    
    def get_user_session(self, session_id: str) -> Optional[UserSession]:
        """Get a user session by ID."""
        doc = self.sessions_collection.find_one({"_id": session_id})
        return UserSession.from_dict(doc) if doc else None
    
    def update_user_session(self, session: UserSession) -> UserSession:
        """Update an existing user session."""
        doc = session.to_dict()
        self.sessions_collection.update_one(
            {"_id": session.session_id},
            {"$set": doc}
        )
        
        logger.debug(f"Updated session: {session.session_id}")
        return session
    
    def delete_user_session(self, session_id: str) -> bool:
        """Delete a user session."""
        result = self.sessions_collection.delete_one({"_id": session_id})
        return result.deleted_count > 0
    
    def seed_questions(self, questions: List[Question]) -> int:
        """Seed questions into the database."""
        inserted_count = 0
        
        for question in questions:
            try:
                # Check if question already exists
                existing = self.questions_collection.find_one({"_id": question.id})
                if existing:
                    logger.info(f"Skipping duplicate question: {question.id}")
                    continue
                
                doc = question.to_dict()
                self.questions_collection.insert_one(doc)
                inserted_count += 1
                logger.debug(f"Inserted question: {question.id}")
            except Exception as e:
                logger.error(f"Error inserting question {question.id}: {e}")
        
        logger.info(f"Seeded {inserted_count} questions")
        return inserted_count
    
    def get_all_api_keys(self) -> List[Dict[str, Any]]:
        """Get all API keys from the database."""
        cursor = self.api_keys_collection.find()
        return list(cursor)
    
    def create_api_key(self, hashed_key: str, name: str, permissions: List[str]) -> bool:
        """Create a new API key."""
        try:
            self.api_keys_collection.insert_one({
                "key": hashed_key,
                "name": name,
                "permissions": permissions,
                "created_at": datetime.utcnow(),
                "active": True
            })
            return True
        except Exception as e:
            logger.error(f"Error creating API key: {e}")
            return False
    
    def deactivate_api_key(self, hashed_key: str) -> bool:
        """Deactivate an API key."""
        result = self.api_keys_collection.update_one(
            {"key": hashed_key},
            {"$set": {"active": False}}
        )
        return result.modified_count > 0


# Global repository instance
repository = MongoDBRepository()
