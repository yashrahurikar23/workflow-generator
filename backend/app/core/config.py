from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Workflow Generator"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "workflow_generator"
    
    # LLM settings (optional, can be configured later)
    OPENAI_API_KEY: Optional[str] = None
    LLM_PROVIDER: str = "openai"  # openai, anthropic, local, etc.
    
    class Config:
        env_file = ".env"

settings = Settings()
