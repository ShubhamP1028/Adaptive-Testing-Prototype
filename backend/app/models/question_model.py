"""Question data model and validation."""
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import uuid


@dataclass
class Question:
    """Question data model for GRE-style test questions."""
    
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""
    options: List[str] = field(default_factory=list)
    correct_answer: int = 0
    difficulty: float = 0.5
    topic: str = ""
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate question data after initialization."""
        self._validate()
    
    def _validate(self):
        """Validate question fields."""
        # Validate difficulty
        if not (0.1 <= self.difficulty <= 1.0):
            raise ValueError(f"Difficulty must be between 0.1 and 1.0, got {self.difficulty}")
        
        # Validate options
        if len(self.options) < 2:
            raise ValueError(f"Options must have at least 2 items, got {len(self.options)}")
        
        # Validate correct_answer index
        if not (0 <= self.correct_answer < len(self.options)):
            raise ValueError(f"correct_answer must be between 0 and {len(self.options)-1}, got {self.correct_answer}")
        
        # Validate text and topic
        if not self.text or not self.text.strip():
            raise ValueError("Text cannot be empty")
        
        if not self.topic or not self.topic.strip():
            raise ValueError("Topic cannot be empty")
    
    def to_dict(self) -> dict:
        """Convert question to dictionary for MongoDB storage."""
        return {
            "_id": self.id,
            "question_id": self.id,
            "text": self.text,
            "options": self.options,
            "correct_answer": self.correct_answer,
            "difficulty": self.difficulty,
            "topic": self.topic,
            "tags": self.tags,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Question":
        """Create question from dictionary (MongoDB document)."""
        return cls(
            id=data.get("_id", data.get("question_id")),
            text=data.get("text", ""),
            options=data.get("options", []),
            correct_answer=data.get("correct_answer", 0),
            difficulty=data.get("difficulty", 0.5),
            topic=data.get("topic", ""),
            tags=data.get("tags", []),
            created_at=datetime.fromisoformat(data.get("created_at")) if data.get("created_at") else None
        )
    
    def is_correct(self, answer_index: int) -> bool:
        """Check if the given answer index is correct."""
        return answer_index == self.correct_answer
