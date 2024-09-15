import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # OpenAI API configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Milvus database configuration
    MILVUS_COLLECTION_NAME = os.getenv("MILVUS_COLLECTION_NAME", "default_collection")
    MILVUS_URI = os.getenv("MILVUS_URI", "localhost:19530")
    MILVUS_EMBEDDING_SIZE = int(os.getenv("MILVUS_EMBEDDING_SIZE", "1536"))

    # Model configuration
    ASSISTANT_MODEL = os.getenv("ASSISTANT_MODEL", "gpt-4")

    # Add any other configuration variables here
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:8000").split(",")

    @classmethod
    def validate(cls):
        """Validate that all required configuration variables are set."""
        required_vars = ["OPENAI_API_KEY", "MILVUS_COLLECTION_NAME", "MILVUS_URI"]
        for var in required_vars:
            if not getattr(cls, var):
                raise ValueError(f"Missing required environment variable: {var}")

# Validate the configuration on import
Config.validate()

# Create a config instance for easy import in other modules
config = Config()
