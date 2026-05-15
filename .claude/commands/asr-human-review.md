# Human Review of ASR Candidates

Perform a qualitative review after automated scoring.

## Inputs

Read:

```text
reports/leaderboard.md
reports/failure-analysis.md
reports/scorecard-spec-kit.md
reports/scorecard-openspec.md
reports/scorecard-gsd.md
reports/scorecard-bmad.md
```

Then inspect the candidate folders under `outputs/`.

## Review dimensions

Score each candidate from 1 to 5 on:

1. ASR architecture clarity
2. Backend replaceability
3. CER correctness and reproducibility
4. Audio preprocessing boundaries
5. API contract quality
6. Test realism
7. Operational readiness
8. Simplicity and maintainability
9. Extensibility to real ASR backends
10. Documentation usefulness

## Required output

Write:

```text
reports/human-review.md
```

Use this structure:

```markdown
# Human Review

## Summary

## Candidate ranking

## Per-candidate review

### Spec Kit

### OpenSpec

### GSD

### BMAD

## Disagreements with automated score

## Final recommendation
```
