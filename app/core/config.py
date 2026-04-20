import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from langchain_openai import ChatOpenAI


class Settings(BaseSettings):
    PROJECT_NAME: str = "LingXi Agent"
    VERSION: str = "1.0.0"
    # 大模型 API 配置
    DASHSCOPE_API_KEY: str
    DASHSCOPE_API_BASE: str | None = None
    DEFAULT_MODEL: str

    NEO4J_URI: str = "bolt://localhost:7687"
    NEO4J_USER: str = "neo4j"
    NEO4J_PASSWORD: str = "password"
    model_config = SettingsConfigDict(env_file="../../.env", env_ignore_empty=True)


@lru_cache()
def get_settings() -> Settings:
    """使用 lru_cache 保证全局只加载一次配置，提升性能"""
    return Settings()


def get_llm(temperature: float = 0.7) -> ChatOpenAI:
    """获取配置好的 LLM 实例"""
    settings = get_settings()
    return ChatOpenAI(
        model=settings.DEFAULT_MODEL,
        temperature=temperature,
        api_key=settings.DASHSCOPE_API_KEY,
        base_url=settings.DASHSCOPE_API_BASE
    )
