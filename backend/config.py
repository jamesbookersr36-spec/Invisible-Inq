import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "")

    BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
    BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))

    CORS_ORIGINS = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173").split(",")]

    GROK_API_KEY = os.getenv("GROK_API_KEY", "")
    GROK_API_URL = os.getenv("GROK_API_URL", "https://api.x.ai/v1/chat/completions")
    GROK_MODEL = os.getenv("GROK_MODEL", "grok-3")

    @classmethod
    def validate(cls):
        if not cls.NEO4J_PASSWORD:
            raise ValueError("NEO4J_PASSWORD environment variable is required")
        return True
