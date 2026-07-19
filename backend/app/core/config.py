from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # App General Settings
    APP_NAME: str = "Internet Memory Layer Backend"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "iml_default_local_secret_key_change_me_in_production"
    
    # SQLite / PostgreSQL Relational DB Settings
    DATABASE_URL: str = "sqlite:///./iml_metadata.db"
    
    # Redis Cache & Queue Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Neo4j Graph DB Settings
    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    
    # Vector DB (ChromaDB) Settings
    CHROMADB_PATH: str = "./iml_chroma_db"
    
    # Local LLM (Ollama) Settings
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:1.5b"
    EMBEDDING_MODEL: str = "bge-large-en-v1.5"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
