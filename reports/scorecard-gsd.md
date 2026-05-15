# Scorecard: gsd

Target: `/home/beomgon/side/asr-pipeline-evaluator/outputs/gsd`

Total score: **100.00 / 100**

## Category scores

| Category | Score |
|---|---:|
| functionality | 20.00 |
| asr_pipeline_structure | 15.00 |
| cer_evaluation | 15.00 |
| serving_api_quality | 15.00 |
| tests | 10.00 |
| operations | 10.00 |
| maintainability | 10.00 |
| documentation | 5.00 |

## Evidence

| Category | Points | Finding | Files |
|---|---:|---|---|
| functionality | 5/5 | transcription endpoint or handler | README.md, TASKS.md, docs/api.md |
| functionality | 3/3 | audio upload/input handling | .claude/agents/gsd-executor.md, .claude/agents/gsd-phase-researcher.md, .claude/agents/gsd-plan-checker.md |
| functionality | 4/4 | ASR backend abstraction | README.md, TASKS.md, docs/architecture.md |
| functionality | 3/3 | response schema includes transcript/confidence/request/timing fields | .claude/agents/gsd-ai-researcher.md, .claude/agents/gsd-assumptions-analyzer.md, .claude/agents/gsd-debugger.md |
| functionality | 3/3 | error handling paths | .claude/agents/gsd-code-fixer.md, .claude/agents/gsd-code-reviewer.md, .claude/agents/gsd-codebase-mapper.md |
| functionality | 2/2 | configuration/env management | .claude/agents/gsd-advisor-researcher.md, .claude/agents/gsd-ai-researcher.md, .claude/agents/gsd-code-fixer.md |
| asr_pipeline_structure | 3/3 | preprocessing layer | README.md, TASKS.md, docs/api.md |
| asr_pipeline_structure | 3/3 | chunking/batching/VAD consideration | .claude/agents/gsd-ai-researcher.md, .claude/agents/gsd-debugger.md, .claude/agents/gsd-doc-writer.md |
| asr_pipeline_structure | 3/3 | model adapter boundary | README.md, TASKS.md, docs/architecture.md |
| asr_pipeline_structure | 3/3 | postprocessing/transcript normalization | .claude/agents/gsd-verifier.md, .claude/get-shit-done/references/verification-overrides.md, .claude/get-shit-done/templates/research.md |
| asr_pipeline_structure | 3/3 | async/queue/streaming extensibility | .claude/agents/gsd-advisor-researcher.md, .claude/agents/gsd-ai-researcher.md, .claude/agents/gsd-code-fixer.md |
| cer_evaluation | 5/5 | CER calculation implementation/reference | README.md, TASKS.md, docs/api.md |
| cer_evaluation | 3/3 | manifest/reference/hypothesis support | .claude/agents/gsd-ai-researcher.md, .claude/agents/gsd-code-fixer.md, .claude/agents/gsd-code-reviewer.md |
| cer_evaluation | 3/3 | explicit CER normalization policy | .claude/agents/gsd-code-fixer.md, .claude/agents/gsd-debugger.md, .claude/agents/gsd-doc-synthesizer.md |
| cer_evaluation | 2/2 | per-sample and aggregate metrics | .claude/agents/gsd-assumptions-analyzer.md, .claude/agents/gsd-code-fixer.md, .claude/agents/gsd-code-reviewer.md |
| cer_evaluation | 2/2 | CER failure/edge-case handling | .claude/agents/gsd-ai-researcher.md, .claude/agents/gsd-assumptions-analyzer.md, .claude/agents/gsd-code-fixer.md |
| serving_api_quality | 3/3 | API schema/OpenAPI clarity | .claude/agents/gsd-ai-researcher.md, .claude/agents/gsd-codebase-mapper.md, .claude/agents/gsd-doc-classifier.md |
| serving_api_quality | 3/3 | latency measurement | .claude/agents/gsd-ai-researcher.md, .claude/agents/gsd-debugger.md, .claude/agents/gsd-eval-planner.md |
| serving_api_quality | 3/3 | concurrency consideration | .claude/agents/gsd-ai-researcher.md, .claude/agents/gsd-code-fixer.md, .claude/agents/gsd-code-reviewer.md |
| serving_api_quality | 2/2 | timeout/retry/backoff | .claude/agents/gsd-ai-researcher.md, .claude/agents/gsd-debug-session-manager.md, .claude/agents/gsd-debugger.md |
| serving_api_quality | 2/2 | streaming extension path | .claude/agents/gsd-advisor-researcher.md, .claude/agents/gsd-ai-researcher.md, .claude/agents/gsd-assumptions-analyzer.md |
| serving_api_quality | 2/2 | health and metrics endpoints | .claude/commands/gsd/health.md, .claude/get-shit-done/workflows/health.md, .claude/gsd-file-manifest.json |
| tests | 3/3 | unit tests | tests/unit/test_cer.py, tests/__init__.py, tests/unit/test_normalizer.py |
| tests | 3/3 | integration/API tests | tests/unit/test_cer.py, tests/__init__.py, tests/unit/test_normalizer.py |
| tests | 2/2 | eval smoke tests | .claude/agents/gsd-debugger.md, .claude/get-shit-done/references/thinking-models-execution.md, .claude/get-shit-done/workflows/help.md |
| tests | 2/2 | CI-ready test command | .claude/agents/gsd-advisor-researcher.md, .claude/agents/gsd-ai-researcher.md, .claude/agents/gsd-assumptions-analyzer.md |
| operations | 3/3 | Docker or compose support | .claude/agents/gsd-codebase-mapper.md, .claude/agents/gsd-debugger.md, .claude/agents/gsd-doc-writer.md |
| operations | 2/2 | structured logging/request tracing | .claude/agents/gsd-code-reviewer.md, .claude/agents/gsd-codebase-mapper.md, .claude/agents/gsd-debugger.md |
| operations | 2/2 | metrics | .claude/agents/gsd-code-fixer.md, .claude/agents/gsd-code-reviewer.md, .claude/agents/gsd-codebase-mapper.md |
| operations | 2/2 | deployment/runbook | .claude/agents/gsd-codebase-mapper.md, .claude/agents/gsd-debugger.md, .claude/agents/gsd-doc-classifier.md |
| operations | 1/1 | rollback/fallback consideration | .claude/agents/gsd-advisor-researcher.md, .claude/agents/gsd-ai-researcher.md, .claude/agents/gsd-code-fixer.md |
| maintainability | 3/3 | module boundaries | src/eval/cer.py, src/backends/base.py, src/api/routes/metrics_route.py |
| maintainability | 2/2 | configuration separation | .claude/agents/gsd-advisor-researcher.md, .claude/agents/gsd-ai-researcher.md, .claude/agents/gsd-code-fixer.md |
| maintainability | 2/2 | dependency management | requirements.txt |
| maintainability | 2/2 | basic code organization/simplicity | src/eval/cer.py, tests/unit/test_cer.py, tests/__init__.py |
| maintainability | 1/1 | model/vendor replacement path | .claude/agents/gsd-codebase-mapper.md, .claude/agents/gsd-executor.md, .claude/agents/gsd-phase-researcher.md |
| documentation | 1/1 | architecture documentation | .claude/get-shit-done/templates/codebase/architecture.md, docs/runbook.md, docs/architecture.md |
| documentation | 1/1 | eval protocol | .claude/agents/gsd-ai-researcher.md, .claude/agents/gsd-code-fixer.md, .claude/agents/gsd-code-reviewer.md |
| documentation | 1/1 | API usage examples | .claude/agents/gsd-codebase-mapper.md, .claude/agents/gsd-debugger.md, .claude/agents/gsd-doc-classifier.md |
| documentation | 1/1 | implementation scope documentation | .claude/agents/gsd-code-reviewer.md, .claude/agents/gsd-doc-writer.md, .claude/agents/gsd-executor.md |
| documentation | 1/1 | known limitations | .claude/agents/gsd-code-reviewer.md, .claude/agents/gsd-codebase-mapper.md, .claude/agents/gsd-executor.md |

## Pytest

```json
{
  "available": true,
  "passed": true,
  "returncode": 0,
  "command": "/home/beomgon/side/asr-pipeline-evaluator/outputs/gsd/.venv/bin/python -m pytest -q",
  "stdout_tail": "..........................................                               [100%]\n42 passed in 1.25s\n",
  "stderr_tail": ""
}
```
