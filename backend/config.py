"""
Configuration management for InsightVault backend
"""

import os
from typing import Optional

class Config:
    """Application configuration"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./insightvault.db"
    
    # JWT Configuration
    SECRET_KEY: str = "supersecretkey"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    @classmethod
    def load_from_env(cls):
        """Load configuration from environment variables"""
        cls.OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
        cls.DATABASE_URL = os.getenv('DATABASE_URL', cls.DATABASE_URL)
        cls.SECRET_KEY = os.getenv('SECRET_KEY', cls.SECRET_KEY)
        cls.ALGORITHM = os.getenv('ALGORITHM', cls.ALGORITHM)
        cls.ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', str(cls.ACCESS_TOKEN_EXPIRE_MINUTES)))
    
    @classmethod
    def load_from_file(cls, config_file: str = "config.json"):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(config_file):
                import json
                with open(config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Update OpenAI API key if present
                if 'openai_api_key' in config_data and config_data['openai_api_key'] != "your_openai_api_key_here":
                    cls.OPENAI_API_KEY = config_data['openai_api_key']
                
                print(f"Configuration loaded from {config_file}")
                return True
        except Exception as e:
            print(f"Error loading config from {config_file}: {e}")
        
        return False

# Initialize configuration
Config.load_from_env()
Config.load_from_file() 