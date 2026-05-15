"""
Application settings.

Spec ref: .specify/asr-pipeline-spec.md § Assumptions
  - v1 uses MockASRBackend exclusively
  - Docker image python:3.11-slim
  - No auth for v1
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the ASR serving pipeline."""

    model_config = SettingsConfigDict(env_prefix="ASR_", env_file=".env", extra="ignore")

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    log_level: str = "INFO"

    # ASR Backend
    backend: str = "mock"          # "mock" is the only v1 backend
    mock_transcript: str = "안녕하세요 테스트 음성입니다"
    mock_confidence: float = 0.98
    mock_backend_name: str = "mock-asr"
    mock_backend_version: str = "0.1.0"

    # Audio
    target_sample_rate: int = 16000

    # Request ID prefix (FR-008)
    request_id_prefix: str = "req_"


settings = Settings()
