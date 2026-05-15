# Fair Bakeoff Design

Use the same baseline prompt, same allowed tools, same model if possible, same time budget, and same output directory contract for every workflow tool.

## Recommended layout

```text
asr-pipeline-bakeoff/
  baseline/
    ASR_PIPELINE_REQUIREMENTS.md
    API_CONTRACT.md
    EVAL_PROTOCOL.md
    rubric.yaml
    test_fixtures/
      manifest.jsonl
  outputs/
    spec-kit/
    openspec/
    gsd/
    bmad/
  reports/
```

## Procedure

1. Start from an empty or identical skeleton repository.
2. Give each tool the exact same prompt.
3. Forbid manual fixes before first scoring, or record them separately.
4. Run `scripts/run_all.py` across all outputs.
5. Perform human review only after reading automated results.
6. Report both overall winner and category winner.

## Bias controls

- Do not let one tool see another tool's output before generation.
- Do not tune the rubric after seeing results unless you rerun all candidates.
- Keep runtime checks optional but apply them consistently.
- Separate generated quality from operator intervention quality.
