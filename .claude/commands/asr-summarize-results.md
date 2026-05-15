# Summarize ASR Bakeoff Results

Create the final decision memo from automated and human evaluation results.

## Inputs

Read:

```text
reports/leaderboard.md
reports/failure-analysis.md
reports/all-scores.json
reports/human-review.md
versions.md
```

If `reports/human-review.md` is missing, clearly state that the summary is based only on automated scoring.

## Output

Write:

```text
reports/final-recommendation.md
```

Use this structure:

```markdown
# ASR Framework Bakeoff Final Recommendation

## Executive summary

## Experimental setup

## Results table

## Winner and why

## Where the automated score may be misleading

## Best use case by framework

## Recommended next experiment

## Appendix: versions and prompts
```
