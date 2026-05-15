"""
Pydantic request/response schemas for the ASR API.

Spec ref: .specify/asr-pipeline-spec.md § API Contract
"""

from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


# ── /transcribe ──────────────────────────────────────────────────────────────

class TimingInfoSchema(BaseModel):
    """Timing breakdown in milliseconds."""
    preprocess_ms: float
    inference_ms: float
    postprocess_ms: float
    total_ms: float


class ModelInfoSchema(BaseModel):
    """ASR model/backend metadata."""
    backend: str
    name: str
    version: str


class TranscribeResponse(BaseModel):
    """
    Response schema for POST /transcribe.

    Spec ref: .specify/asr-pipeline-spec.md § Endpoint: POST /transcribe
    """
    request_id: str = Field(..., description="Unique request identifier (req_<uuid4>)")
    transcript: str = Field(..., description="ASR transcription output")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score")
    audio_duration_seconds: float = Field(..., ge=0.0, description="Duration of the audio clip")
    timing: TimingInfoSchema
    model: ModelInfoSchema


# ── /eval/cer ────────────────────────────────────────────────────────────────

class CERPair(BaseModel):
    """A single reference/hypothesis pair for CER evaluation."""
    id: str
    reference: str
    hypothesis: str


class CERRequest(BaseModel):
    """
    Request body for POST /eval/cer.

    Spec ref: .specify/asr-pipeline-spec.md § Endpoint: POST /eval/cer
    """
    pairs: list[CERPair] = Field(..., min_length=1)


class CERSampleResponse(BaseModel):
    """CER result for a single pair."""
    id: str
    cer: Optional[float] = None   # None when reference is empty (undefined)
    reference_chars: int
    edits: int


class CERResponse(BaseModel):
    """
    Response schema for POST /eval/cer.

    Spec ref: .specify/asr-pipeline-spec.md § Endpoint: POST /eval/cer
    """
    pairs: list[CERSampleResponse]
    overall_cer: float
    total_reference_chars: int
    total_edits: int


# ── /healthz ─────────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    """Response schema for GET /healthz."""
    status: str = "ok"
