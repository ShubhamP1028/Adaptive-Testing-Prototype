"""Item Response Theory (IRT) model for ability estimation."""
import math
from typing import Tuple
import logging

logger = logging.getLogger(__name__)


def calculate_probability(ability: float, difficulty: float) -> float:
    """
    Calculate the probability of a correct response using the logistic model.
    
    P(correct | ability, difficulty) = 1 / (1 + exp(-(ability - difficulty)))
    
    Args:
        ability: User's current ability score (0.0 to 1.0)
        difficulty: Question's difficulty score (0.1 to 1.0)
    
    Returns:
        Probability of correct response (0.0 to 1.0)
    """
    difference = ability - difficulty
    # Use exp(-difference) directly for numerical stability
    exponent = -difference
    
    # Clamp exponent to avoid overflow
    exponent = max(-500, min(500, exponent))
    
    probability = 1.0 / (1.0 + math.exp(exponent))
    return probability


def update_ability(
    current_ability: float,
    is_correct: bool,
    difficulty: float,
    learning_rate: float = 0.1
) -> float:
    """
    Update the ability score using IRT-based online learning.
    
    θ_new = θ_old + α * (score - P)
    
    where:
    - θ is the ability score
    - α is the learning rate
    - score is 1 for correct, 0 for incorrect
    - P is the probability of correct response
    
    Args:
        current_ability: Current ability score (0.0 to 1.0)
        is_correct: Whether the answer was correct
        difficulty: Question difficulty (0.1 to 1.0)
        learning_rate: Learning rate (default 0.1)
    
    Returns:
        Updated ability score (clamped to 0.0 to 1.0)
    """
    # Calculate probability of correct response
    probability = calculate_probability(current_ability, difficulty)
    
    # Calculate adjustment
    score = 1.0 if is_correct else 0.0
    adjustment = learning_rate * (score - probability)
    
    # Update ability
    new_ability = current_ability + adjustment
    
    # Clamp to valid range
    new_ability = max(0.0, min(1.0, new_ability))
    
    logger.debug(
        f"Ability update: {current_ability:.3f} -> {new_ability:.3f} "
        f"(correct={is_correct}, difficulty={difficulty:.3f}, prob={probability:.3f})"
    )
    
    return new_ability


def calculate_difficulty_for_ability(
    target_ability: float,
    current_difficulty: float,
    is_correct: bool
) -> float:
    """
    Calculate the optimal difficulty for the next question.
    
    If correct, increase difficulty slightly.
    If incorrect, decrease difficulty slightly.
    
    Args:
        target_ability: Target ability level for next question
        current_difficulty: Current question difficulty
        is_correct: Whether the answer was correct
    
    Returns:
        New difficulty score (0.1 to 1.0)
    """
    # If correct, increase difficulty; if incorrect, decrease
    if is_correct:
        new_difficulty = current_difficulty + 0.05
    else:
        new_difficulty = current_difficulty - 0.05
    
    # Clamp to valid range
    new_difficulty = max(0.1, min(1.0, new_difficulty))
    
    return new_difficulty


def estimate_ability_from_history(
    question_history: list,
    learning_rate: float = 0.1
) -> float:
    """
    Estimate ability from question history using cumulative updates.
    
    Args:
        question_history: List of (difficulty, is_correct) tuples
        learning_rate: Learning rate for each update
    
    Returns:
        Estimated ability score
    """
    # Start with baseline ability
    ability = 0.5
    
    # Update ability for each question in history
    for item in question_history:
        difficulty = item.get("difficulty", 0.5)
        is_correct = item.get("is_correct", False)
        ability = update_ability(ability, is_correct, difficulty, learning_rate)
    
    return ability


def calculate_confidence(ability: float, difficulty: float) -> float:
    """
    Calculate the confidence in the ability estimate.
    
    Higher confidence when ability and difficulty are well-matched.
    
    Args:
        ability: Current ability score
        difficulty: Question difficulty
    
    Returns:
        Confidence score (0.0 to 1.0)
    """
    # Maximum confidence when ability matches difficulty
    difference = abs(ability - difficulty)
    
    # Convert to confidence (0.5 difference = 50% confidence)
    confidence = 1.0 - (difference * 2.0)
    
    return max(0.0, min(1.0, confidence))
