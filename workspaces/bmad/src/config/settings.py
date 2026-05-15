from __future__ import annotations
"""Application settings using Pydantic BaseSettings.

All configuration is read from environment variables.
No secrets are hardcoded.
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Server
    host: str = Field(default="0.0.0.0", description="Bind host")
    port: int = Field(default=8000, description="Bind port")

    # ASR Backend
    asr_backend: str = Field(default="mock", description="Backend name: mock | whisper | azure | google")
    mock_transcript: str = Field(
        default="안녕하세요 이것은 모의 음성 인식 결과입니다",
        description="Fixed transcript text for MockASRBackend",
    )
    mock_confidence: float = Field(default=0.98, ge=0.0, le=1.0)

    # Observability
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO"
    )

    # Audio
    target_sample_rate: int = Field(default=16000)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
