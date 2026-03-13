"""MongoDB connection and initialization."""
from flask_pymongo import PyMongo
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import logging

logger = logging.getLogger(__name__)
mongo = PyMongo()


def init_db(app):
    """Initialize MongoDB connection with Flask app."""
    mongo.init_app(app)
    
    # Test connection
    try:
        client = MongoClient(app.config["MONGODB_URI"])
        client.admin.command("ping")
        logger.info("MongoDB connection established successfully")
    except ConnectionFailure as e:
        logger.error(f"Could not connect to MongoDB: {e}")
        raise


def get_db():
    """Get the current database connection."""
    return mongo.db


def create_indexes():
    """Create database indexes for better query performance."""
    db = get_db()
    
    # Create index on session_id for UserSessions
    db.user_sessions.create_index("session_id", unique=True)
    
    # Create index on difficulty for Questions
    db.questions.create_index("difficulty")
    
    # Create index on question_id for Questions
    db.questions.create_index("question_id", unique=True)
    
    # Create index on topic for Questions
    db.questions.create_index("topic")
    
    logger.info("Database indexes created successfully")
