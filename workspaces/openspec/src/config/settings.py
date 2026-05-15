from __future__ import annotations
"""
Application settings and configuration.
All settings can be overridden via environment variables.
"""
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    # Server settings
    host: str = Field(default="0.0.0.0", description="Server bind host")
    port: int = Field(default=8000, description="Server bind port")
    debug: bool = Field(default=False, description="Enable debug mode")

    # ASR backend settings
    backend: Literal["mock"] = Field(
        default="mock",
        description="ASR backend to use (currently only 'mock' is supported)",
    )
    mock_transcript: str = Field(
        default="안녕하세요 반갑습니다",
        description="Default mock transcript returned by MockASRBackend",
    )
    mock_confidence: float = Field(
        default=0.95,
        description="Mock confidence score [0, 1]",
    )
    mock_inference_delay_ms: float = Field(
        default=10.0,
        description="Simulated inference latency in milliseconds",
    )

    # Audio preprocessing settings
    target_sample_rate: int = Field(
        default=16000,
        description="Target sample rate (Hz) for audio preprocessing",
    )
    max_audio_bytes: int = Field(
        default=50 * 1024 * 1024,  # 50 MB
        description="Maximum allowed audio file size in bytes",
    )

    # Logging settings
    log_level: str = Field(default="INFO", description="Log level")
    log_format: Literal["json", "text"] = Field(
        default="json",
        description="Log format: 'json' for structured logging or 'text' for human-readable",
    )

    # Metrics settings
    metrics_enabled: bool = Field(default=True, description="Enable Prometheus metrics")

    model_config = {
        "env_prefix": "ASR_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached application settings."""
    return Settings()
