# Scorecard: openspec

Target: `/home/beomgon/side/asr-pipeline-evaluator/outputs/openspec`

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
| functionality | 5/5 | transcription endpoint or handler | README.md, docs/api.md, docs/architecture.md |
| functionality | 3/3 | audio upload/input handling | docs/api.md, docs/architecture.md, docs/eval_protocol.md |
| functionality | 4/4 | ASR backend abstraction | docs/architecture.md, docs/implementation_scope.md, src/api/routes/transcribe.py |
| functionality | 3/3 | response schema includes transcript/confidence/request/timing fields | README.md, docker-compose.yml, docs/api.md |
| functionality | 3/3 | error handling paths | .claude/commands/opsx/apply.md, .claude/commands/opsx/archive.md, .claude/skills/openspec-apply-change/SKILL.md |
| functionality | 2/2 | configuration/env management | README.md, docs/architecture.md, docs/implementation_scope.md |
| asr_pipeline_structure | 3/3 | preprocessing layer | README.md, docker-compose.yml, docs/api.md |
| asr_pipeline_structure | 3/3 | chunking/batching/VAD consideration | README.md, docs/architecture.md, docs/runbook.md |
| asr_pipeline_structure | 3/3 | model adapter boundary | docs/architecture.md, docs/implementation_scope.md, openapi.yaml |
| asr_pipeline_structure | 3/3 | postprocessing/transcript normalization | docs/api.md, docs/architecture.md, docs/implementation_scope.md |
| asr_pipeline_structure | 3/3 | async/queue/streaming extensibility | docs/implementation_scope.md, requirements.txt, src/api/main.py |
| cer_evaluation | 5/5 | CER calculation implementation/reference | README.md, docker-compose.yml, docs/api.md |
| cer_evaluation | 3/3 | manifest/reference/hypothesis support | .claude/commands/opsx/explore.md, .claude/skills/openspec-explore/SKILL.md, README.md |
| cer_evaluation | 3/3 | explicit CER normalization policy | README.md, docs/api.md, docs/architecture.md |
| cer_evaluation | 2/2 | per-sample and aggregate metrics | .claude/commands/opsx/archive.md, .claude/commands/opsx/explore.md, .claude/skills/openspec-archive-change/SKILL.md |
| cer_evaluation | 2/2 | CER failure/edge-case handling | .claude/commands/opsx/apply.md, .claude/commands/opsx/explore.md, .claude/skills/openspec-apply-change/SKILL.md |
| serving_api_quality | 3/3 | API schema/OpenAPI clarity | .claude/commands/opsx/apply.md, .claude/commands/opsx/archive.md, .claude/commands/opsx/explore.md |
| serving_api_quality | 3/3 | latency measurement | docs/api.md, docs/architecture.md, docs/runbook.md |
| serving_api_quality | 3/3 | concurrency consideration | requirements.txt, src/api/main.py, src/api/routes/eval_cer.py |
| serving_api_quality | 2/2 | timeout/retry/backoff | Dockerfile, docker-compose.yml |
| serving_api_quality | 2/2 | streaming extension path | .claude/commands/opsx/archive.md, .claude/skills/openspec-archive-change/SKILL.md, docs/implementation_scope.md |
| serving_api_quality | 2/2 | health and metrics endpoints | Dockerfile, README.md, docker-compose.yml |
| tests | 3/3 | unit tests | tests/unit/test_backends.py, tests/__init__.py, tests/integration/test_eval_cer.py |
| tests | 3/3 | integration/API tests | tests/unit/test_backends.py, tests/__init__.py, tests/integration/test_eval_cer.py |
| tests | 2/2 | eval smoke tests | README.md, docs/architecture.md, docs/implementation_scope.md |
| tests | 2/2 | CI-ready test command | .claude/commands/opsx/apply.md, .claude/commands/opsx/archive.md, .claude/commands/opsx/explore.md |
| operations | 3/3 | Docker or compose support | Dockerfile, README.md, docker-compose.yml |
| operations | 2/2 | structured logging/request tracing | .claude/skills/openspec-explore/SKILL.md, README.md, docs/api.md |
| operations | 2/2 | metrics | .claude/commands/opsx/apply.md, .claude/skills/openspec-apply-change/SKILL.md, README.md |
| operations | 2/2 | deployment/runbook | .claude/skills/openspec-explore/SKILL.md, docs/architecture.md, docs/implementation_scope.md |
| operations | 1/1 | rollback/fallback consideration | docs/api.md, docs/architecture.md, docs/implementation_scope.md |
| maintainability | 3/3 | module boundaries | src/observability/logging.py, src/api/schemas.py, src/eval/cer.py |
| maintainability | 2/2 | configuration separation | .claude/commands/opsx/archive.md, .claude/commands/opsx/propose.md, .claude/skills/openspec-archive-change/SKILL.md |
| maintainability | 2/2 | dependency management | requirements.txt |
| maintainability | 2/2 | basic code organization/simplicity | tests/unit/test_backends.py, src/observability/logging.py, tests/__init__.py |
| maintainability | 1/1 | model/vendor replacement path | README.md, docker-compose.yml, docs/api.md |
| documentation | 1/1 | architecture documentation | docs/architecture.md, README.md, docs/runbook.md |
| documentation | 1/1 | eval protocol | .claude/commands/opsx/explore.md, .claude/skills/openspec-explore/SKILL.md, README.md |
| documentation | 1/1 | API usage examples | .claude/commands/opsx/archive.md, .claude/skills/openspec-archive-change/SKILL.md, .claude/skills/openspec-propose/SKILL.md |
| documentation | 1/1 | implementation scope documentation | docs/implementation_scope.md, src/backends/base.py |
| documentation | 1/1 | known limitations | .claude/commands/opsx/propose.md, .claude/skills/openspec-propose/SKILL.md |

## Pytest

```json
{
  "available": true,
  "passed": true,
  "returncode": 0,
  "command": "/home/beomgon/side/asr-pipeline-evaluator/outputs/openspec/.venv/bin/python -m pytest -q",
  "stdout_tail": "============================= test session starts ==============================\nplatform linux -- Python 3.8.10, pytest-8.3.4, pluggy-1.5.0\nrootdir: /home/beomgon/side/asr-pipeline-evaluator/outputs/openspec\nconfigfile: pytest.ini\ntestpaths: tests\nplugins: asyncio-0.24.0, anyio-4.5.2\nasyncio: mode=strict, default_loop_scope=None\ncollected 83 items\n\ntests/eval/test_cer_runner.py .......                                    [  8%]\ntests/integration/test_eval_cer.py ........                              [ 18%]\ntests/integration/test_health.py ....                                    [ 22%]\ntests/integration/test_metrics.py ......                                 [ 30%]\ntests/integration/test_transcribe.py ............                        [ 44%]\ntests/unit/test_audio.py .......                                         [ 53%]\ntests/unit/test_backends.py .........                                    [ 63%]\ntests/unit/test_cer.py ..............................                    [100%]\n\n============================== 83 passed in 1.33s ==============================\n",
  "stderr_tail": "/home/beomgon/side/asr-pipeline-evaluator/outputs/openspec/.venv/lib/python3.8/site-packages/pytest_asyncio/plugin.py:208: PytestDeprecationWarning: The configuration option \"asyncio_default_fixture_loop_scope\" is unset.\nThe event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: \"function\", \"class\", \"module\", \"package\", \"session\"\n\n  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))\n"
}
```
