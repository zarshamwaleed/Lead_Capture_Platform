from typing import List
from pydantic_settings import BaseSettings
import json

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "sqlite:///./lead_capture.db"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5500", "http://127.0.0.1:5500"]
    
    # Geo APIs
    GEO_PROVIDER_A_URL: str = "http://ip-api.com/json"
    GEO_PROVIDER_B_URL: str = "https://ipapi.co/json"
    GEO_CACHE_TTL: int = 3600
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10
    RATE_LIMIT_PER_WIDGET: int = 20
    
    # Email
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 1025
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    EMAIL_FROM: str = "noreply@leadcapture.com"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        
        @classmethod
        def parse_env_var(cls, field_name: str, raw_val: str):
            if field_name == "CORS_ORIGINS":
                try:
                    return json.loads(raw_val)
                except json.JSONDecodeError:
                    return [origin.strip() for origin in raw_val.split(",")]
            return raw_val

settings = Settings()
