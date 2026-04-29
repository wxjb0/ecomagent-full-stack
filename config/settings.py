import os
from typing import Optional
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """应用配置管理"""
    
    # 应用基础配置
    APP_NAME: str = "EcommerceMultiAgent"
    APP_ENV: str = "development"
    DEBUG: bool = True
    
    # OpenAI配置
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000
    
    # Anthropic配置
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./ecommerce_agent.db"
    
    # API配置
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Agent配置
    USE_MOCK_DATA: bool = True  # 默认使用模拟数据
    ENABLE_AGENT_MEMORY: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings():
    """获取配置单例"""
    return Settings()
