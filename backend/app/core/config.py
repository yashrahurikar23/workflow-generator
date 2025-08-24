from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Workflow Generator"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "workflow_generator"
    USE_MOCK_DATABASE: bool = False  # Set to True to use mock database for development
    
    # Environment
    ENVIRONMENT: str = "development"
    
    # LLM settings (multiple provider support)
    LLM_PROVIDER: str = "template"  # template, openai, aiml, anthropic, local
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4"
    
    # AIML API Configuration (https://aimlapi.com)
    AIML_API_KEY: Optional[str] = None
    AIML_BASE_URL: str = "https://api.aimlapi.com/v1"
    AIML_MODEL: str = "gpt-4o"  # Latest GPT-4 Omni via AIML
    
    # Anthropic Configuration
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    
    class Config:
        env_file = ".env"

settings = Settings()
