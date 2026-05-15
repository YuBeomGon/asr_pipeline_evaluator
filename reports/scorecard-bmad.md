# Scorecard: bmad

Target: `/home/beomgon/side/asr-pipeline-evaluator/outputs/bmad`

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
| functionality | 3/3 | audio upload/input handling | .claude/skills/bmad-prfaq/references/internal-faq.md, .claude/skills/bmad-product-brief/prompts/draft-and-review.md, docs/api.md |
| functionality | 4/4 | ASR backend abstraction | README.md, docs/architecture.md, docs/implementation_scope.md |
| functionality | 3/3 | response schema includes transcript/confidence/request/timing fields | .claude/skills/bmad-brainstorming/steps/step-02a-user-selected.md, .claude/skills/bmad-brainstorming/steps/step-02b-ai-recommended.md, .claude/skills/bmad-brainstorming/steps/step-02c-random-selection.md |
| functionality | 3/3 | error handling paths | .claude/skills/bmad-check-implementation-readiness/SKILL.md, .claude/skills/bmad-check-implementation-readiness/steps/step-02-prd-analysis.md, .claude/skills/bmad-check-implementation-readiness/steps/step-05-epic-quality-review.md |
| functionality | 2/2 | configuration/env management | .claude/skills/bmad-advanced-elicitation/SKILL.md, .claude/skills/bmad-agent-analyst/SKILL.md, .claude/skills/bmad-agent-analyst/customize.toml |
| asr_pipeline_structure | 3/3 | preprocessing layer | docs/api.md, docs/architecture.md, docs/implementation_scope.md |
| asr_pipeline_structure | 3/3 | chunking/batching/VAD consideration | .claude/skills/bmad-code-review/steps/step-01-gather-context.md, .claude/skills/bmad-code-review/steps/step-04-present.md, .claude/skills/bmad-correct-course/SKILL.md |
| asr_pipeline_structure | 3/3 | model adapter boundary | README.md, docs/architecture.md, docs/implementation_scope.md |
| asr_pipeline_structure | 3/3 | postprocessing/transcript normalization | README.md, docs/api.md, docs/architecture.md |
| asr_pipeline_structure | 3/3 | async/queue/streaming extensibility | .claude/skills/bmad-check-implementation-readiness/steps/step-02-prd-analysis.md, .claude/skills/bmad-checkpoint-preview/generate-trail.md, .claude/skills/bmad-create-architecture/steps/step-03-starter.md |
| cer_evaluation | 5/5 | CER calculation implementation/reference | README.md, docs/api.md, docs/architecture.md |
| cer_evaluation | 3/3 | manifest/reference/hypothesis support | .claude/skills/bmad-agent-analyst/SKILL.md, .claude/skills/bmad-agent-analyst/customize.toml, .claude/skills/bmad-agent-architect/SKILL.md |
| cer_evaluation | 3/3 | explicit CER normalization policy | .claude/skills/bmad-checkpoint-preview/generate-trail.md, .claude/skills/bmad-create-prd/steps-c/step-10-nonfunctional.md, .claude/skills/bmad-create-ux-design/steps/step-13-responsive-accessibility.md |
| cer_evaluation | 2/2 | per-sample and aggregate metrics | .claude/skills/bmad-brainstorming/steps/step-01b-continue.md, .claude/skills/bmad-brainstorming/steps/step-03-technique-execution.md, .claude/skills/bmad-brainstorming/steps/step-04-idea-organization.md |
| cer_evaluation | 2/2 | CER failure/edge-case handling | .claude/skills/bmad-agent-analyst/SKILL.md, .claude/skills/bmad-agent-architect/SKILL.md, .claude/skills/bmad-agent-dev/SKILL.md |
| serving_api_quality | 3/3 | API schema/OpenAPI clarity | .claude/skills/bmad-agent-tech-writer/SKILL.md, .claude/skills/bmad-checkpoint-preview/step-02-walkthrough.md, .claude/skills/bmad-checkpoint-preview/step-03-detail-pass.md |
| serving_api_quality | 3/3 | latency measurement | .claude/skills/bmad-brainstorming/steps/step-02a-user-selected.md, .claude/skills/bmad-brainstorming/steps/step-02b-ai-recommended.md, .claude/skills/bmad-brainstorming/steps/step-02c-random-selection.md |
| serving_api_quality | 3/3 | concurrency consideration | .claude/skills/bmad-check-implementation-readiness/steps/step-02-prd-analysis.md, .claude/skills/bmad-create-architecture/steps/step-03-starter.md, .claude/skills/bmad-create-architecture/steps/step-05-patterns.md |
| serving_api_quality | 2/2 | timeout/retry/backoff | .claude/skills/bmad-create-architecture/steps/step-05-patterns.md, .claude/skills/bmad-party-mode/SKILL.md, .claude/skills/bmad-quick-dev/SKILL.md |
| serving_api_quality | 2/2 | streaming extension path | .claude/skills/bmad-advanced-elicitation/SKILL.md, .claude/skills/bmad-agent-analyst/SKILL.md, .claude/skills/bmad-agent-architect/SKILL.md |
| serving_api_quality | 2/2 | health and metrics endpoints | Dockerfile, README.md, docker-compose.yml |
| tests | 3/3 | unit tests | tests/unit/test_cer.py, tests/__init__.py, .claude/skills/bmad-customize/scripts/tests/test_list_customizable_skills.py |
| tests | 3/3 | integration/API tests | tests/unit/test_cer.py, tests/__init__.py, .claude/skills/bmad-customize/scripts/tests/test_list_customizable_skills.py |
| tests | 2/2 | eval smoke tests | .claude/skills/bmad-checkpoint-preview/generate-trail.md, .claude/skills/bmad-retrospective/SKILL.md, README.md |
| tests | 2/2 | CI-ready test command | .claude/skills/bmad-advanced-elicitation/SKILL.md, .claude/skills/bmad-agent-analyst/SKILL.md, .claude/skills/bmad-agent-analyst/customize.toml |
| operations | 3/3 | Docker or compose support | .claude/skills/bmad-create-architecture/steps/step-03-starter.md, .claude/skills/bmad-create-architecture/steps/step-06-structure.md, .claude/skills/bmad-customize/SKILL.md |
| operations | 2/2 | structured logging/request tracing | .claude/skills/bmad-check-implementation-readiness/SKILL.md, .claude/skills/bmad-check-implementation-readiness/steps/step-02-prd-analysis.md, .claude/skills/bmad-check-implementation-readiness/steps/step-03-epic-coverage-validation.md |
| operations | 2/2 | metrics | .claude/skills/bmad-brainstorming/steps/step-01-session-setup.md, .claude/skills/bmad-brainstorming/steps/step-01b-continue.md, .claude/skills/bmad-brainstorming/steps/step-02a-user-selected.md |
| operations | 2/2 | deployment/runbook | .claude/skills/bmad-brainstorming/steps/step-02a-user-selected.md, .claude/skills/bmad-checkpoint-preview/step-03-detail-pass.md, .claude/skills/bmad-correct-course/SKILL.md |
| operations | 1/1 | rollback/fallback consideration | .claude/skills/bmad-checkpoint-preview/step-01-orientation.md, .claude/skills/bmad-checkpoint-preview/step-02-walkthrough.md, .claude/skills/bmad-correct-course/SKILL.md |
| maintainability | 3/3 | module boundaries | src/eval/cer.py, src/backends/registry.py, src/backends/base.py |
| maintainability | 2/2 | configuration separation | .claude/skills/bmad-advanced-elicitation/SKILL.md, .claude/skills/bmad-agent-analyst/SKILL.md, .claude/skills/bmad-agent-analyst/customize.toml |
| maintainability | 2/2 | dependency management | requirements.txt |
| maintainability | 2/2 | basic code organization/simplicity | src/eval/cer.py, tests/unit/test_cer.py, src/backends/registry.py |
| maintainability | 1/1 | model/vendor replacement path | .claude/skills/bmad-create-architecture/steps/step-02-context.md, .claude/skills/bmad-create-architecture/steps/step-03-starter.md, .claude/skills/bmad-create-architecture/steps/step-06-structure.md |
| documentation | 1/1 | architecture documentation | docs/runbook.md, docs/architecture.md, README.md |
| documentation | 1/1 | eval protocol | .claude/skills/bmad-agent-analyst/SKILL.md, .claude/skills/bmad-agent-analyst/customize.toml, .claude/skills/bmad-agent-architect/SKILL.md |
| documentation | 1/1 | API usage examples | .claude/skills/bmad-agent-analyst/SKILL.md, .claude/skills/bmad-agent-architect/SKILL.md, .claude/skills/bmad-agent-dev/SKILL.md |
| documentation | 1/1 | implementation scope documentation | .claude/skills/bmad-create-epics-and-stories/steps/step-01-validate-prerequisites.md, .claude/skills/bmad-create-prd/steps-c/step-08-scoping.md, .claude/skills/bmad-customize/SKILL.md |
| documentation | 1/1 | known limitations | .claude/skills/bmad-check-implementation-readiness/SKILL.md, .claude/skills/bmad-check-implementation-readiness/steps/step-05-epic-quality-review.md, .claude/skills/bmad-create-architecture/steps/step-01b-continue.md |

## Pytest

```json
{
  "available": true,
  "passed": true,
  "returncode": 0,
  "command": "/home/beomgon/side/asr-pipeline-evaluator/outputs/bmad/.venv/bin/python -m pytest -q",
  "stdout_tail": "......................................................................   [100%]\n70 passed in 0.49s\n",
  "stderr_tail": "/home/beomgon/side/asr-pipeline-evaluator/outputs/bmad/.venv/lib/python3.8/site-packages/pytest_asyncio/plugin.py:208: PytestDeprecationWarning: The configuration option \"asyncio_default_fixture_loop_scope\" is unset.\nThe event loop scope for asynchronous fixtures will default to the fixture caching scope. Future versions of pytest-asyncio will default the loop scope for asynchronous fixtures to function scope. Set the default fixture loop scope explicitly in order to avoid unexpected behavior in the future. Valid fixture loop scopes are: \"function\", \"class\", \"module\", \"package\", \"session\"\n\n  warnings.warn(PytestDeprecationWarning(_DEFAULT_FIXTURE_LOOP_SCOPE_UNSET))\n"
}
```
