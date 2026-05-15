# Evaluate ASR Candidates

Run the local ASR pipeline evaluator against all frozen candidates.

## First check

Verify these candidate folders exist and are non-empty:

```text
outputs/spec-kit/
outputs/openspec/
outputs/gsd/
outputs/bmad/
```

## Static evaluation command

```bash
python .claude/skills/asr-pipeline-evaluator/scripts/run_all.py \
  --targets outputs/spec-kit outputs/openspec outputs/gsd outputs/bmad \
  --labels spec-kit openspec gsd bmad \
  --manifest .claude/skills/asr-pipeline-evaluator/assets/baseline/test_fixtures/manifest.jsonl \
  --rubric .claude/skills/asr-pipeline-evaluator/assets/baseline/rubric.yaml \
  --out reports
```

## Optional pytest evaluation

Only run this if all candidates have installable Python test environments:

```bash
python .claude/skills/asr-pipeline-evaluator/scripts/run_all.py \
  --targets outputs/spec-kit outputs/openspec outputs/gsd outputs/bmad \
  --labels spec-kit openspec gsd bmad \
  --manifest .claude/skills/asr-pipeline-evaluator/assets/baseline/test_fixtures/manifest.jsonl \
  --rubric .claude/skills/asr-pipeline-evaluator/assets/baseline/rubric.yaml \
  --out reports \
  --run-pytest
```

## Report back

After execution, summarize:

- ranking from `reports/leaderboard.md`
- each candidate's biggest strength
- each candidate's biggest gap
- whether human review is required before trusting the result
