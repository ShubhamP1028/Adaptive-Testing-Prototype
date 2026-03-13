"""OpenAI service for study plan generation."""
import logging
import json
from typing import Optional
from datetime import datetime

from openai import OpenAI
from flask import current_app

from app.models.session_model import UserSession, StudyPlan, StudyPlanStep
from app.services.mongodb_repository import repository

logger = logging.getLogger(__name__)


class AIService:
    """Service for OpenAI integration and study plan generation."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        """
        Initialize the OpenAI service.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (gpt-4, gpt-3.5-turbo, etc.)
        """
        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for study plan generation."""
        return """You are an expert GRE tutor. Generate a concise, practical 3-step study plan 
based on the student's performance data. Each step should have a title, description, 
and 1-2 action items. End with a short motivational note."""
    
    def format_performance_data(self, session: UserSession) -> dict:
        """
        Format session data for OpenAI prompt.
        
        Args:
            session: User session
        
        Returns:
            Dictionary with performance data
        """
        # Calculate accuracy
        accuracy = (
            session.correct_count / session.questions_asked
            if session.questions_asked > 0 else 0
        )
        
        # Get topic statistics
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
        
        # Calculate topics missed
        topics_missed = {
            topic: stats["total"] - stats["correct"]
            for topic, stats in topic_stats.items()
        }
        
        # Find weakest topic
        weakest_topic = None
        weakest_accuracy = 1.0
        for topic, stats in topic_stats.items():
            if stats["total"] > 0:
                topic_accuracy = stats["correct"] / stats["total"]
                if topic_accuracy < weakest_accuracy:
                    weakest_accuracy = topic_accuracy
                    weakest_topic = topic
        
        return {
            "overall_accuracy": accuracy,
            "final_ability_score": session.current_ability,
            "topics_missed": topics_missed,
            "topic_stats": topic_stats,
            "weakest_topic": weakest_topic,
            "weakest_accuracy": weakest_accuracy,
            "max_difficulty": max(
                (item.difficulty for item in session.question_history),
                default=0.5
            )
        }
    
    def generate_study_plan_prompt(self, performance_data: dict) -> str:
        """
        Generate the prompt for OpenAI.
        
        Args:
            performance_data: Formatted performance data
        
        Returns:
            Prompt string
        """
        data = performance_data
        
        prompt = f"""Generate a 3-step personalized study plan based on the following performance data:

Student performance summary:
- overall_accuracy: {data['overall_accuracy'] * 100:.0f}%
- final_ability_score: {data['final_ability_score']:.2f}
- topics_missed: {data['topics_missed']}
- topic_stats: {data['topic_stats']}
- weakest_topic: {data['weakest_topic']}
- max_difficulty_reached: {data['max_difficulty']:.2f}

Produce:
1. Three numbered steps, each with a short title and 1-2 practical actions/resources
2. One optional targeted practice question for the weakest topic
3. A short motivational note (1 sentence)

Format as JSON with steps array containing title, description, and action_items."""

        return prompt
    
    def generate_study_plan(self, performance_data: dict) -> Optional[StudyPlan]:
        """
        Generate a study plan using OpenAI.
        
        Args:
            performance_data: Formatted performance data
        
        Returns:
            StudyPlan or None if generation failed
        """
        try:
            prompt = self.generate_study_plan_prompt(performance_data)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Try to parse as JSON
            try:
                data = json.loads(content)
                steps = [
                    StudyPlanStep(
                        title=step["title"],
                        description=step["description"],
                        action_items=step.get("action_items", [])
                    )
                    for step in data.get("steps", [])
                ]
                
                return StudyPlan(steps=steps)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse OpenAI response as JSON: {content}")
                return None
                
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    
    def generate_study_plan_for_session(self, session: UserSession) -> UserSession:
        """
        Generate a study plan for a completed session.
        
        Args:
            session: User session
        
        Returns:
            Updated session with study plan
        """
        if not session.is_complete():
            logger.warning(f"Session {session.session_id} is not complete yet")
            return session
        
        # Format performance data
        performance_data = self.format_performance_data(session)
        
        # Generate study plan
        study_plan = self.generate_study_plan(performance_data)
        
        if study_plan:
            session.study_plan = study_plan
            logger.info(f"Generated study plan for session {session.session_id}")
        else:
            logger.warning(f"Failed to generate study plan for session {session.session_id}")
        
        # Update session in database
        repository.update_user_session(session)
        
        return session


# Global service instance
ai_service = None


def init_ai_service(api_key: str, model: str = "gpt-4"):
    """Initialize the AI service with API key."""
    global ai_service
    ai_service = AIService(api_key=api_key, model=model)
    return ai_service
