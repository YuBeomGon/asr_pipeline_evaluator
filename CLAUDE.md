# Claude Code Instructions: ASR Framework Bakeoff

You are operating inside an ASR framework bakeoff workspace.

## Mission

Help compare Spec Kit, OpenSpec, GSD, and BMAD by using each framework to generate an ASR serving pipeline candidate, then evaluate the four outputs using the same objective evaluator.

The target system is an ASR serving pipeline with CER evaluation, not a generic web app.


The target implementation scope is a **production-oriented v1 scaffold**, not a full production ASR platform. Require local runnable code, mock ASR backend, backend abstraction, CER evaluation, tests, docs, and run commands. Do not require real GPU inference, model training, diarization, auth, billing, or full autoscaling in v1.

## Non-negotiable fairness rules

1. Use the same requirements for all four frameworks.
2. Keep each framework isolated in its own workspace.
3. Do not let one framework's generated files, commands, or context leak into another framework's workspace.
4. Record framework version, model, prompt, date, and manual interventions in `versions.md`.
5. Copy final candidates only into `outputs/<framework>/`.
6. Run the same evaluator command for all candidates.
7. Separate automated scores from human judgment.

## Target requirements

Use this baseline requirement source:

```text
.claude/skills/asr-pipeline-evaluator/assets/baseline/ASR_PIPELINE_REQUIREMENTS.md
```

Use this implementation scope source:

```text
.claude/skills/asr-pipeline-evaluator/assets/baseline/IMPLEMENTATION_SCOPE.md
docs/07-implementation-scope.md
```

Use this API contract:

```text
.claude/skills/asr-pipeline-evaluator/assets/baseline/API_CONTRACT.md
```

Use this CER protocol:

```text
.claude/skills/asr-pipeline-evaluator/assets/baseline/EVAL_PROTOCOL.md
```

## Workspace layout

```text
workspaces/spec-kit/   # install and run Spec Kit here only
workspaces/openspec/   # install and run OpenSpec here only
workspaces/gsd/        # install and run GSD here only
workspaces/bmad/       # install and run BMAD here only
outputs/spec-kit/      # frozen final candidate from Spec Kit
outputs/openspec/      # frozen final candidate from OpenSpec
outputs/gsd/           # frozen final candidate from GSD
outputs/bmad/          # frozen final candidate from BMAD
reports/               # evaluator output
```

## How to behave

- Prefer reproducible shell commands over vague instructions.
- Ask before installing network dependencies if the environment is restricted.
- When generating candidate code, preserve the framework's native workflow rather than overriding it with your own process.
- When evaluating candidate code, be strict and consistent.
- Do not reward a candidate for merely mentioning a feature; check whether files, tests, code, and docs support it.
- Mark uncertain findings as uncertain.
- Keep a clear audit trail.

## Useful local commands

Run static evaluation:

```bash
python .claude/skills/asr-pipeline-evaluator/scripts/run_all.py \
  --targets outputs/spec-kit outputs/openspec outputs/gsd outputs/bmad \
  --labels spec-kit openspec gsd bmad \
  --manifest .claude/skills/asr-pipeline-evaluator/assets/baseline/test_fixtures/manifest.jsonl \
  --rubric .claude/skills/asr-pipeline-evaluator/assets/baseline/rubric.yaml \
  --out reports
```

Run evaluation with pytest:

```bash
python .claude/skills/asr-pipeline-evaluator/scripts/run_all.py \
  --targets outputs/spec-kit outputs/openspec outputs/gsd outputs/bmad \
  --labels spec-kit openspec gsd bmad \
  --manifest .claude/skills/asr-pipeline-evaluator/assets/baseline/test_fixtures/manifest.jsonl \
  --rubric .claude/skills/asr-pipeline-evaluator/assets/baseline/rubric.yaml \
  --out reports \
  --run-pytest
```

## Preferred review sequence

1. Use `.claude/commands/asr-bakeoff-setup.md`.
2. Use `.claude/commands/asr-generate-candidate.md` once per framework.
3. Freeze outputs.
4. Use `.claude/commands/asr-evaluate.md`.
5. Use `.claude/commands/asr-human-review.md`.
6. Use `.claude/commands/asr-summarize-results.md`.

## Key evaluation priorities

Rank candidates by fitness for a real ASR serving pipeline:

1. Correct and explicit CER evaluation.
2. Clean ASR backend abstraction.
3. Proper audio preprocessing and transcript normalization boundaries.
4. Production-aware API design.
5. Health, metrics, logging, request IDs, and failure handling.
6. Tests and local reproducibility.
7. Extensibility for real ASR backends.
8. Clear architecture and runbook documentation.
