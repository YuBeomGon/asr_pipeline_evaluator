from __future__ import annotations
"""
Pydantic schemas for API request and response bodies.
These schemas mirror the OpenAPI spec in openapi.yaml exactly.
See openapi.yaml at the project root for the authoritative specification.
"""
from typing import List, Optional

from pydantic import BaseModel, Field


# ─── Health ──────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str = Field(..., examples=["ok"])


# ─── Transcription ───────────────────────────────────────────────────────────

class TimingInfo(BaseModel):
    preprocess_ms: float = Field(..., ge=0)
    inference_ms: float = Field(..., ge=0)
    postprocess_ms: float = Field(..., ge=0)
    total_ms: float = Field(..., ge=0)


class ModelInfo(BaseModel):
    backend: str
    name: str
    version: str


class TranscribeResponse(BaseModel):
    request_id: str = Field(..., examples=["req_550e8400-e29b-41d4-a716-446655440000"])
    transcript: str
    confidence: float = Field(..., ge=0, le=1)
    audio_duration_seconds: float = Field(..., ge=0)
    timing: TimingInfo
    model: ModelInfo


# ─── CER Evaluation ──────────────────────────────────────────────────────────

class CERPair(BaseModel):
    id: str
    reference: str
    hypothesis: str


class CERRequest(BaseModel):
    pairs: List[CERPair] = Field(..., min_length=1)


class CERSampleResult(BaseModel):
    id: str
    reference: str
    hypothesis: str
    cer: float = Field(..., ge=0)
    substitutions: int = Field(..., ge=0)
    deletions: int = Field(..., ge=0)
    insertions: int = Field(..., ge=0)
    reference_length: int = Field(..., ge=0)


class CERAggregate(BaseModel):
    mean_cer: float = Field(..., ge=0)
    total_substitutions: int = Field(..., ge=0)
    total_deletions: int = Field(..., ge=0)
    total_insertions: int = Field(..., ge=0)
    total_reference_length: int = Field(..., ge=0)
    total_samples: int = Field(..., ge=0)


class CERResponse(BaseModel):
    results: List[CERSampleResult]
    aggregate: CERAggregate


# ─── Errors ──────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
    request_id: Optional[str] = None
