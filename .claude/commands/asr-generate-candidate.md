# Generate ASR Candidate

Generate one ASR serving pipeline candidate using exactly one framework workspace.

## Required input from user

Ask for or infer exactly one framework label:

```text
spec-kit | openspec | gsd | bmad
```

## Process

1. Work only inside `workspaces/<framework>/`.
2. Read the common prompt:

```text
.claude/skills/asr-pipeline-evaluator/assets/prompts/common_asr_pipeline_prompt.md
```

3. Read the baseline sources:

```text
.claude/skills/asr-pipeline-evaluator/assets/baseline/ASR_PIPELINE_REQUIREMENTS.md
.claude/skills/asr-pipeline-evaluator/assets/baseline/IMPLEMENTATION_SCOPE.md
.claude/skills/asr-pipeline-evaluator/assets/baseline/API_CONTRACT.md
.claude/skills/asr-pipeline-evaluator/assets/baseline/EVAL_PROTOCOL.md
```

4. Use the selected framework's native workflow as much as possible.
5. Produce a runnable candidate implementation.
6. Ensure the candidate explicitly documents implementation scope, out-of-scope items, and known limitations.
7. Run whatever local tests the candidate provides.
8. Copy the final frozen candidate to:

```text
outputs/<framework>/
```

9. Update `versions.md` with framework version, model, date, and any interventions.

## Candidate implementation scope summary

The candidate must implement a production-oriented v1 ASR serving scaffold:

- local runnable API service
- `/transcribe`, `/healthz`, `/metrics`
- local audio upload path
- mock ASR backend requiring no GPU or network
- replaceable ASR backend interface
- audio preprocessing boundary
- transcript postprocessing boundary
- CER evaluator with explicit normalization policy
- tests and documented commands
- architecture, API, eval protocol, implementation scope, runbook, and known limitations docs

Do not spend implementation time on out-of-scope v1 items such as production GPU autoscaling, model training, diarization, auth, billing, transcript database, or full real-time streaming.

## Fairness rules

- Do not inspect other framework outputs while generating this candidate.
- Do not reuse code from another candidate.
- Do not improve the prompt for one framework unless the same prompt update is applied to all four.
- Record every manual fix.
