import os
import secrets
from typing import List, Optional, Dict, Any, Union
from pydantic import PostgresDsn, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "Learning Platform"
    API_V1_STR: str = "/api/v1"
    
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "app")
    
    DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}/{POSTGRES_DB}"
    
    UPLOAD_DIRECTORY: str = os.getenv("UPLOAD_DIRECTORY", os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads"))
    
    # JWT settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # CORS settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    # LLM configuration
    LLM_MODEL_PATH: str = os.getenv("LLM_MODEL_PATH", "./models/llama")
    LLM_CONTEXT_SIZE: int = 2048
    LLM_MAX_TOKENS: int = 512

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        
        values = info.data
        postgres_user = values.get("POSTGRES_USER")
        postgres_password = values.get("POSTGRES_PASSWORD")
        postgres_server = values.get("POSTGRES_SERVER")
        postgres_db = values.get("POSTGRES_DB")
        
        return f"postgresql://{postgres_user}:{postgres_password}@{postgres_server}/{postgres_db}"

    model_config = {
        "case_sensitive": True,
        "env_file": ".env",
        "extra": "allow"
    }


settings = Settings() 