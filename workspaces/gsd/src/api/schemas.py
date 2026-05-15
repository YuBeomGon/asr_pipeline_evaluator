"""Pydantic request/response schemas."""
from __future__ import annotations

from pydantic import BaseModel, Field


# --- /transcribe ---

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
    request_id: str
    transcript: str
    confidence: float
    audio_duration_seconds: float
    timing: TimingInfo
    model: ModelInfo


# --- /eval/cer ---

class CERPair(BaseModel):
    id: str = Field(default="")
    reference: str
    hypothesis: str


class CERRequest(BaseModel):
    pairs: list[CERPair]


class CERSampleResult(BaseModel):
    id: str
    reference_normalized: str
    hypothesis_normalized: str
    edit_distance: int
    reference_length: int
    cer: float


class CERAggregate(BaseModel):
    num_samples: int
    total_edit_distance: int
    total_reference_length: int
    macro_cer: float
    micro_cer: float


class CERResponse(BaseModel):
    aggregate: CERAggregate
    samples: list[CERSampleResult]


# --- /healthz ---

class HealthResponse(BaseModel):
    status: str = "ok"
