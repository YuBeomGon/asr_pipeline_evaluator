# ASR Serving Pipeline - Dockerfile
# Spec ref: .specify/asr-pipeline-spec.md § FR-014, NFR-001
# Spec ref: .specify/asr-pipeline-spec.md § Assumptions (python:3.11-slim)

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for soundfile / libsndfile
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose the API port
EXPOSE 8000

# Spec ref: NFR-001 — start command
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
