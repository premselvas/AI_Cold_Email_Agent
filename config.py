import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the application."""
    
    # Groq API
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
    
    # Gmail API - Direct credentials
    GMAIL_CLIENT_ID = os.getenv('GMAIL_CLIENT_ID')
    GMAIL_CLIENT_SECRET = os.getenv('GMAIL_CLIENT_SECRET')
    GMAIL_REFRESH_TOKEN = os.getenv('GMAIL_REFRESH_TOKEN')
    GMAIL_ACCESS_TOKEN = os.getenv('GMAIL_ACCESS_TOKEN')
    GMAIL_TOKEN_URI = 'https://oauth2.googleapis.com/token'
    
    # Database
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'data/email_agent.db')
    
    # File paths
    UPLOAD_DIR = 'uploads'
    OUTPUT_DIR = 'outputs'
    LOG_DIR = 'logs'
    DATA_DIR = 'data'
    PROMPT_DIR = 'prompts'
    
    # Email settings
    MAX_ATTACHMENT_SIZE = 10 * 1024 * 1024  # 10MB
    MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5MB
    
    # Application settings
    APP_NAME = "AI Cold Email Agent"
    APP_VERSION = "1.0.0"
    
    # Logging
    LOG_FILE = 'logs/app.log'
    LOG_ROTATION = '10MB'
    LOG_RETENTION = 5

    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they do not exist."""
        for d in [cls.UPLOAD_DIR, cls.OUTPUT_DIR, cls.LOG_DIR, cls.DATA_DIR, cls.PROMPT_DIR]:
            os.makedirs(d, exist_ok=True)
    
    @classmethod
    def get_prompt_file(cls):
        """Get the path to the cold email prompt file."""
        return os.path.join(cls.PROMPT_DIR, 'email_prompt.txt')
    
    @classmethod
    def validate_config(cls):
        """Validate that all required configuration is present."""
        errors = []
        if not cls.GROQ_API_KEY or cls.GROQ_API_KEY == 'your_groq_api_key_here':
            errors.append("GROQ_API_KEY is not configured in .env file")
        return errors

Config.ensure_directories()