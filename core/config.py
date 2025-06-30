from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_username: str = "neo4j"
    neo4j_password: str = ""
    
    openai_api_key: str = ""
    
    redis_url: str = "redis://localhost:6379"

    app_name: str = "Music Search System"
    debug: bool = False
    max_search_results: int = 20
    session_timeout: int = 3600 
    
    rag_top_k: int = 50
    embedding_model: str = "text-embedding-ada-002"
    
    class Config:
        env_file = ".env"

settings = Settings()
