#!/usr/bin/env python3
"""Seed script for GRE-style questions."""
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.models.question_model import Question
from app.services.mongodb_repository import repository

# GRE-style questions with varying difficulty levels
QUESTIONS = [
    # Algebra (Difficulty 0.1 - 0.3)
    Question(
        text="If x + 3 = 7, what is the value of x?",
        options=["3", "4", "5", "10"],
        correct_answer=1,
        difficulty=0.1,
        topic="Algebra",
        tags=["linear-equations", "basic"]
    ),
    Question(
        text="Solve for y: 2y - 5 = 11",
        options=["3", "5", "7", "8"],
        correct_answer=2,
        difficulty=0.15,
        topic="Algebra",
        tags=["linear-equations"]
    ),
    Question(
        text="If 3x = 12, what is the value of x/2?",
        options=["1", "2", "3", "4"],
        correct_answer=2,
        difficulty=0.2,
        topic="Algebra",
        tags=["linear-equations"]
    ),
    Question(
        text="Simplify: 2(x + 3) - 4",
        options=["2x + 2", "2x + 6", "2x - 2", "2x + 10"],
        correct_answer=0,
        difficulty=0.25,
        topic="Algebra",
        tags=["simplification"]
    ),
    # Algebra (Difficulty 0.35 - 0.5)
    Question(
        text="If x^2 - 2x - 3 = 0, what is x?",
        options=["-1", "1", "3", "2"],
        correct_answer=2,
        difficulty=0.35,
        topic="Algebra",
        tags=["quadratic", "roots"]
    ),
    Question(
        text="Solve the system: x + y = 10, x - y = 2",
        options=["x=4, y=6", "x=6, y=4", "x=5, y=5", "x=3, y=7"],
        correct_answer=1,
        difficulty=0.4,
        topic="Algebra",
        tags=["system-of-equations"]
    ),
    Question(
        text="If x + y = 8 and xy = 15, what is x^2 + y^2?",
        options=["34", "38", "42", "46"],
        correct_answer=1,
        difficulty=0.45,
        topic="Algebra",
        tags=["algebraic-identities"]
    ),
    # Algebra (Difficulty 0.55 - 0.7)
    Question(
        text="If f(x) = 2x^2 - 3x + 1, what is f(2)?",
        options=["3", "5", "7", "9"],
        correct_answer=1,
        difficulty=0.55,
        topic="Algebra",
        tags=["functions"]
    ),
    Question(
        text="Solve for x: x^2 + 5x + 6 = 0",
        options=["-2, -3", "2, 3", "-1, -6", "1, 6"],
        correct_answer=0,
        difficulty=0.6,
        topic="Algebra",
        tags=["quadratic", "factoring"]
    ),
    Question(
        text="If x > 0 and x^2 = 16, what is x^3?",
        options=["4", "8", "16", "64"],
        correct_answer=3,
        difficulty=0.65,
        topic="Algebra",
        tags=["exponents"]
    ),
    # Algebra (Difficulty 0.75 - 0.9)
    Question(
        text="Solve: |2x - 3| = 7",
        options=["-2, 5", "-5, 2", "-2, -5", "2, 5"],
        correct_answer=0,
        difficulty=0.75,
        topic="Algebra",
        tags=["absolute-value"]
    ),
    Question(
        text="If x + 1/x = 3, what is x^2 + 1/x^2?",
        options=["7", "9", "11", "13"],
        correct_answer=0,
        difficulty=0.8,
        topic="Algebra",
        tags=["algebraic-identities"]
    ),
    Question(
        text="Solve: x^2 - 4x + 5 = 0",
        options=["2±i", "2±√5", "4±i", "No real solutions"],
        correct_answer=0,
        difficulty=0.85,
        topic="Algebra",
        tags=["quadratic", "complex-numbers"]
    ),
    # Vocabulary (Difficulty 0.1 - 0.3)
    Question(
        text="What is the synonym of 'happy'?",
        options=["sad", "joyful", "angry", "tired"],
        correct_answer=1,
        difficulty=0.1,
        topic="Vocabulary",
        tags=["synonyms", "basic"]
    ),
    Question(
        text="Choose the word that means 'very hungry'?",
        options=["starving", "full", "thirsty", "sleepy"],
        correct_answer=0,
        difficulty=0.15,
        topic="Vocabulary",
        tags=["synonyms"]
    ),
    Question(
        text="What is the antonym of 'begin'?",
        options=["start", "finish", "continue", "pause"],
        correct_answer=1,
        difficulty=0.2,
        topic="Vocabulary",
        tags=["antonyms"]
    ),
    # Vocabulary (Difficulty 0.35 - 0.5)
    Question(
        text="Which word means 'to make something better'?",
        options=["deteriorate", "improve", "worsen", "destroy"],
        correct_answer=1,
        difficulty=0.35,
        topic="Vocabulary",
        tags=["synonyms"]
    ),
    Question(
        text="Choose the best synonym for 'difficult'?",
        options=["easy", "challenging", "simple", "boring"],
        correct_answer=1,
        difficulty=0.4,
        topic="Vocabulary",
        tags=["synonyms"]
    ),
    Question(
        text="What does 'meticulous' mean?",
        options=["careless", "detailed", "hasty", "rude"],
        correct_answer=1,
        difficulty=0.45,
        topic="Vocabulary",
        tags=["advanced"]
    ),
    # Vocabulary (Difficulty 0.55 - 0.7)
    Question(
        text="Which word means 'to express approval'?",
        options=["condemn", "endorse", "criticize", "reject"],
        correct_answer=1,
        difficulty=0.55,
        topic="Vocabulary",
        tags=["synonyms"]
    ),
    Question(
        text="Choose the word that is closest in meaning to 'ambiguous'?",
        options=["clear", "vague", "definite", "exact"],
        correct_answer=1,
        difficulty=0.6,
        topic="Vocabulary",
        tags=["advanced"]
    ),
    Question(
        text="What is the synonym of 'benevolent'?",
        options=["kind", "cruel", "selfish", "evil"],
        correct_answer=0,
        difficulty=0.65,
        topic="Vocabulary",
        tags=["advanced"]
    ),
    # Vocabulary (Difficulty 0.75 - 0.9)
    Question(
        text="Which word means 'to make something less severe'?",
        options=["aggravate", "mitigate", "worsen", "intensify"],
        correct_answer=1,
        difficulty=0.75,
        topic="Vocabulary",
        tags=["advanced"]
    ),
    Question(
        text="Choose the best synonym for 'ephemeral'?",
        options=["permanent", "short-lived", "eternal", "enduring"],
        correct_answer=1,
        difficulty=0.8,
        topic="Vocabulary",
        tags=["advanced"]
    ),
    Question(
        text="What does 'ubiquitous' mean?",
        options=["rare", "everywhere", "hidden", "specific"],
        correct_answer=1,
        difficulty=0.85,
        topic="Vocabulary",
        tags=["advanced"]
    ),
]

def seed_questions():
    """Seed questions into the database."""
    print("Starting question seeding...")
    
    # Initialize repository
    repo = repository
    
    # Seed questions
    count = repo.seed_questions(QUESTIONS)
    
    print(f"Successfully seeded {count} questions")
    
    # Print summary
    all_questions = repo.get_all_questions()
    print(f"\nTotal questions in database: {len(all_questions)}")
    
    # Group by topic
    topics = {}
    for q in all_questions:
        topic = q.topic
        if topic not in topics:
            topics[topic] = []
        topics[topic].append(q)
    
    print("\nQuestions by topic:")
    for topic, questions in topics.items():
        print(f"  {topic}: {len(questions)} questions")
    
    return count

if __name__ == "__main__":
    seed_questions()
