"""Configuration management for the Adaptive Diagnostic Engine."""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class."""
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/adaptive_test")
    MONGODB_DATABASE = os.getenv("MONGODB_DATABASE", "adaptive_test")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "1000"))
    
    # API Configuration
    API_KEY = os.getenv("API_KEY", "default-api-key-for-demo")
    API_RATE_LIMIT = int(os.getenv("API_RATE_LIMIT", "100"))  # requests per minute
    
    # Adaptive Engine Configuration
    INITIAL_ABILITY = float(os.getenv("INITIAL_ABILITY", "0.5"))
    LEARNING_RATE = float(os.getenv("LEARNING_RATE", "0.1"))
    DIFFICULTY_RANGE = float(os.getenv("DIFFICULTY_RANGE", "0.15"))
    EXPANDED_DIFFICULTY_RANGE = float(os.getenv("EXPANDED_DIFFICULTY_RANGE", "0.3"))
    MIN_DIFFICULTY = float(os.getenv("MIN_DIFFICULTY", "0.1"))
    MAX_DIFFICULTY = float(os.getenv("MAX_DIFFICULTY", "1.0"))
    QUESTIONS_PER_SESSION = int(os.getenv("QUESTIONS_PER_SESSION", "10"))
    
    # Application Configuration
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "5000"))


config = Config()
