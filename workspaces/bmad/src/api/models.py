"""Pydantic request/response models for the ASR API.

BMAD Developer: All API shapes are defined here. Routes import these models.
Keep models thin — business logic lives in service modules.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


# ─────────────────────────────── /healthz ──────────────────────────────────

class HealthResponse(BaseModel):
    status: str = "ok"


# ─────────────────────────────── /transcribe ───────────────────────────────

class TimingInfo(BaseModel):
    preprocess_ms: float
    inference_ms: float
    postprocess_ms: float
    total_ms: float


class ModelInfo(BaseModel):
    backend: str
    name: str
    version: str


class TranscribeResponse(BaseModel):
    request_id: str = Field(description="Unique request identifier with req_ prefix")
    transcript: str
    confidence: float = Field(ge=0.0, le=1.0)
    audio_duration_seconds: float = Field(ge=0.0)
    timing: TimingInfo
    model: ModelInfo


# ─────────────────────────────── /eval/cer ─────────────────────────────────

class CERPair(BaseModel):
    id: str
    reference: str
    hypothesis: str


class CERRequest(BaseModel):
    pairs: list[CERPair] = Field(min_length=1)


class CERSampleResponse(BaseModel):
    id: str
    reference: str
    hypothesis: str
    cer: float
    substitutions: int
    deletions: int
    insertions: int
    reference_length: int


class CERAggregate(BaseModel):
    mean_cer: float
    total_samples: int
    total_reference_chars: int
    total_errors: int


class CERResponse(BaseModel):
    results: list[CERSampleResponse]
    aggregate: CERAggregate


# ─────────────────────────────── Error ─────────────────────────────────────

class ErrorResponse(BaseModel):
    error: str
    request_id: str | None = None
    detail: str | None = None
