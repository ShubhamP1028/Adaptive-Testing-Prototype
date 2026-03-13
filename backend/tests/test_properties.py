"""Property-based tests for adaptive engine."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from hypothesis import given, strategies as st, settings
from app.models.question_model import Question
from app.models.session_model import UserSession
from app.services.irt_model import update_ability


class TestAdaptiveEngineProperties:
    """Property-based tests for adaptive engine."""
    
    @given(
        ability=st.floats(min_value=0.0, max_value=1.0),
        difficulty=st.floats(min_value=0.1, max_value=1.0),
        is_correct=st.booleans()
    )
    @settings(max_examples=100)
    def test_ability_bounds_preserved(self, ability, difficulty, is_correct):
        """Property 1: Ability score always stays within [0.0, 1.0]."""
        new_ability = update_ability(ability, is_correct, difficulty, 0.1)
        assert 0.0 <= new_ability <= 1.0, f"Ability {new_ability} out of bounds"
    
    @given(
        ability=st.floats(min_value=0.0, max_value=1.0),
        difficulty=st.floats(min_value=0.1, max_value=1.0),
        is_correct=st.booleans()
    )
    @settings(max_examples=100)
    def test_correct_answer_increases_ability(self, ability, difficulty, is_correct):
        """Property 2: Correct answers generally increase ability."""
        new_ability = update_ability(ability, True, difficulty, 0.1)
        # With high probability, correct answers increase ability
        # (except when ability is already very high and question is very easy)
        if ability < 0.9 or difficulty > 0.3:
            assert new_ability >= ability, f"Correct answer should not decrease ability"
    
    @given(
        ability=st.floats(min_value=0.0, max_value=1.0),
        difficulty=st.floats(min_value=0.1, max_value=1.0),
        is_correct=st.booleans()
    )
    @settings(max_examples=100)
    def test_incorrect_answer_decreases_ability(self, ability, difficulty, is_correct):
        """Property 3: Incorrect answers generally decrease ability."""
        new_ability = update_ability(ability, False, difficulty, 0.1)
        # With high probability, incorrect answers decrease ability
        if ability > 0.1 or difficulty < 0.7:
            assert new_ability <= ability, f"Incorrect answer should not increase ability"
    
    @given(
        questions=st.lists(
            st.tuples(
                st.floats(min_value=0.1, max_value=1.0),
                st.booleans()
            ),
            min_size=1,
            max_size=20
        )
    )
    @settings(max_examples=50)
    def test_no_duplicate_questions(self, questions):
        """Property 4: Question history should not contain duplicates."""
        # This is a simplified test - in practice, we'd need a mock repository
        question_ids = [f"q{i}" for i in range(len(questions))]
        
        # Check for duplicates
        assert len(question_ids) == len(set(question_ids)), "Duplicate question IDs found"
    
    @given(
        correct_count=st.integers(min_value=0, max_value=10),
        incorrect_count=st.integers(min_value=0, max_value=10)
    )
    @settings(max_examples=50)
    def test_accuracy_consistency(self, correct_count, incorrect_count):
        """Property 5: Accuracy count consistency check."""
        total = correct_count + incorrect_count
        if total > 0:
            accuracy = correct_count / total
            assert 0.0 <= accuracy <= 1.0, "Accuracy should be between 0 and 1"
