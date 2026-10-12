import os
from typing import List, Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "The Lenny Growth Assistant"
    API_V1_STR: str = "/api"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    # Database
    # Standard PostgreSQL URL, or SQLite fallback for portable evaluations
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        "sqlite+aiosqlite:///./lenny_growth.db" if not os.getenv("POSTGRES_DB") else 
        f"postgresql+asyncpg://{os.getenv('POSTGRES_USER', 'postgres')}:{os.getenv('POSTGRES_PASSWORD', 'postgres')}@{os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')}/{os.getenv('POSTGRES_DB', 'lenny_growth')}"
    )

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # LLM Settings & Provider Selection
    DEFAULT_PROVIDER: str = os.getenv("DEFAULT_PROVIDER", "ollama")  # 'ollama', 'anthropic', 'openai', 'mock'
    DEFAULT_MODEL: str = os.getenv("DEFAULT_MODEL", "llama3.2")
    
    # Ollama Configuration
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2")

    # Cloud Providers
    ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY", None)
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")

    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o")

    # Knowledge & Retrieval Paths
    TRANSCRIPTS_DATA_DIR: str = os.getenv(
        "TRANSCRIPTS_DATA_DIR", 
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "transcripts-repo"))
    )
    RETRIEVAL_INDEX_FILE: str = os.getenv(
        "RETRIEVAL_INDEX_FILE", 
        os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "retrieval_index.json"))
    )

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"

settings = Settings()
