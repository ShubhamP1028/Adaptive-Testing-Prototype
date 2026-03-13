"""UserSession data model and validation."""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime
import uuid


@dataclass
class QuestionHistoryItem:
    """History item for a single question response."""
    
    question_id: str = ""
    difficulty: float = 0.5
    is_correct: bool = False
    response_time_ms: int = 0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for MongoDB storage."""
        return {
            "question_id": self.question_id,
            "difficulty": self.difficulty,
            "is_correct": self.is_correct,
            "response_time_ms": self.response_time_ms,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "QuestionHistoryItem":
        """Create from dictionary."""
        return cls(
            question_id=data.get("question_id", ""),
            difficulty=data.get("difficulty", 0.5),
            is_correct=data.get("is_correct", False),
            response_time_ms=data.get("response_time_ms", 0),
            timestamp=datetime.fromisoformat(data.get("timestamp")) if data.get("timestamp") else None
        )


@dataclass
class StudyPlanStep:
    """Single step in a study plan."""
    
    title: str = ""
    description: str = ""
    action_items: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "title": self.title,
            "description": self.description,
            "action_items": self.action_items
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "StudyPlanStep":
        """Create from dictionary."""
        return cls(
            title=data.get("title", ""),
            description=data.get("description", ""),
            action_items=data.get("action_items", [])
        )


@dataclass
class StudyPlan:
    """Personalized study plan generated after 10 questions."""
    
    steps: List[StudyPlanStep] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "steps": [step.to_dict() for step in self.steps],
            "generated_at": self.generated_at.isoformat() if self.generated_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "StudyPlan":
        """Create from dictionary."""
        return cls(
            steps=[StudyPlanStep.from_dict(step) for step in data.get("steps", [])],
            generated_at=datetime.fromisoformat(data.get("generated_at")) if data.get("generated_at") else None
        )


@dataclass
class UserSession:
    """User session tracking progress through the adaptive test."""
    
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    start_time: datetime = field(default_factory=datetime.utcnow)
    current_ability: float = 0.5
    question_history: List[QuestionHistoryItem] = field(default_factory=list)
    correct_count: int = 0
    incorrect_count: int = 0
    questions_asked: int = 0
    study_plan: Optional[StudyPlan] = None
    end_time: Optional[datetime] = None
    
    def __post_init__(self):
        """Validate session data after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate session fields."""
        # Validate ability bounds
        if not (0.0 <= self.current_ability <= 1.0):
            raise ValueError(f"current_ability must be between 0.0 and 1.0, got {self.current_ability}")
        
        # Validate consistency
        if self.correct_count + self.incorrect_count != self.questions_asked:
            raise ValueError(
                f"correct_count + incorrect_count ({self.correct_count + self.incorrect_count}) "
                f"must equal questions_asked ({self.questions_asked})"
            )
        
        if len(self.question_history) != self.questions_asked:
            raise ValueError(
                f"question_history length ({len(self.question_history)}) "
                f"must equal questions_asked ({self.questions_asked})"
            )
        
        # Validate study_plan is null if questions_asked < 10
        if self.questions_asked < 10 and self.study_plan is not None:
            raise ValueError("study_plan must be null when questions_asked < 10")
    
    def to_dict(self) -> dict:
        """Convert session to dictionary for MongoDB storage."""
        return {
            "_id": self.session_id,
            "session_id": self.session_id,
            "user_id": self.user_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "current_ability": self.current_ability,
            "question_history": [item.to_dict() for item in self.question_history],
            "correct_count": self.correct_count,
            "incorrect_count": self.incorrect_count,
            "questions_asked": self.questions_asked,
            "study_plan": self.study_plan.to_dict() if self.study_plan else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "UserSession":
        """Create session from dictionary (MongoDB document)."""
        return cls(
            session_id=data.get("_id", data.get("session_id")),
            user_id=data.get("user_id"),
            start_time=datetime.fromisoformat(data.get("start_time")) if data.get("start_time") else None,
            current_ability=data.get("current_ability", 0.5),
            question_history=[QuestionHistoryItem.from_dict(item) for item in data.get("question_history", [])],
            correct_count=data.get("correct_count", 0),
            incorrect_count=data.get("incorrect_count", 0),
            questions_asked=data.get("questions_asked", 0),
            study_plan=StudyPlan.from_dict(data["study_plan"]) if data.get("study_plan") else None,
            end_time=datetime.fromisoformat(data.get("end_time")) if data.get("end_time") else None
        )
    
    def add_question_response(
        self,
        question_id: str,
        difficulty: float,
        is_correct: bool,
        response_time_ms: int = 0
    ):
        """Add a question response to the session history."""
        history_item = QuestionHistoryItem(
            question_id=question_id,
            difficulty=difficulty,
            is_correct=is_correct,
            response_time_ms=response_time_ms
        )
        self.question_history.append(history_item)
        self.questions_asked += 1
        
        if is_correct:
            self.correct_count += 1
        else:
            self.incorrect_count += 1
        
        # Validate after update
        self._validate()
    
    def update_ability(self, new_ability: float):
        """Update the ability score with validation."""
        if not (0.0 <= new_ability <= 1.0):
            raise ValueError(f"new_ability must be between 0.0 and 1.0, got {new_ability}")
        self.current_ability = new_ability
    
    def is_complete(self) -> bool:
        """Check if the session is complete (10 questions asked)."""
        return self.questions_asked >= 10
