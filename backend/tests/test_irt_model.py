"""Tests for IRT model."""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.irt_model import (
    calculate_probability,
    update_ability,
    calculate_difficulty_for_next,
    estimate_ability_from_history,
    calculate_confidence
)


class TestIRTModel:
    """Test IRT model functions."""
    
    def test_probability_at_equal_ability_difficulty(self):
        """When ability equals difficulty, probability should be 0.5."""
        prob = calculate_probability(0.5, 0.5)
        assert abs(prob - 0.5) < 0.001
    
    def test_probability_high_ability_low_difficulty(self):
        """High ability, low difficulty should give high probability."""
        prob = calculate_probability(0.9, 0.1)
        assert prob > 0.9
    
    def test_probability_low_ability_high_difficulty(self):
        """Low ability, high difficulty should give low probability."""
        prob = calculate_probability(0.1, 0.9)
        assert prob < 0.1
    
    def test_update_ability_correct_answer(self):
        """Correct answer should increase ability."""
        new_ability = update_ability(0.5, True, 0.5, 0.1)
        assert new_ability > 0.5
    
    def test_update_ability_incorrect_answer(self):
        """Incorrect answer should decrease ability."""
        new_ability = update_ability(0.5, False, 0.5, 0.1)
        assert new_ability < 0.5
    
    def test_update_ability_bounds(self):
        """Ability should stay within [0.0, 1.0]."""
        # Test with extreme values
        for ability in [0.0, 0.1, 0.5, 0.9, 1.0]:
            for is_correct in [True, False]:
                for difficulty in [0.1, 0.5, 1.0]:
                    new_ability = update_ability(ability, is_correct, difficulty, 0.1)
                    assert 0.0 <= new_ability <= 1.0
    
    def test_update_ability_clamping(self):
        """Ability should be clamped at boundaries."""
        # High ability with correct answer should stay at 1.0
        new_ability = update_ability(0.99, True, 0.1, 0.3)
        assert new_ability <= 1.0
        
        # Low ability with incorrect answer should stay at 0.0
        new_ability = update_ability(0.01, False, 0.9, 0.3)
        assert new_ability >= 0.0
    
    def test_difficulty_adjustment_correct(self):
        """Correct answer should increase difficulty for next question."""
        new_diff = calculate_difficulty_for_next(0.5, 0.5, True)
        assert new_diff > 0.5
    
    def test_difficulty_adjustment_incorrect(self):
        """Incorrect answer should decrease difficulty for next question."""
        new_diff = calculate_difficulty_for_next(0.5, 0.5, False)
        assert new_diff < 0.5
    
    def test_confidence_at_equal_values(self):
        """Maximum confidence when ability matches difficulty."""
        confidence = calculate_confidence(0.5, 0.5)
        assert confidence == 1.0
    
    def test_confidence_with_difference(self):
        """Confidence decreases with ability-difficulty difference."""
        conf1 = calculate_confidence(0.5, 0.5)
        conf2 = calculate_confidence(0.5, 0.7)
        assert conf2 < conf1
