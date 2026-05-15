# ASR Pipeline Evaluator: Claude Code 기준 실험 가이드

이 패키지는 **Spec Kit, OpenSpec, GSD, BMAD**를 사용해 생성한 4개의 음성인식(ASR) 서빙 파이프라인 산출물을 같은 기준으로 비교하기 위한 평가 스킬/도구입니다.

목표는 "어느 프레임워크가 더 멋진 문서를 만들었나"가 아니라, **어느 프레임워크가 더 운영 가능한 ASR serving pipeline을 만들도록 유도하는가**를 확인하는 것입니다.

## 무엇을 만들려는가

비교 대상이 만들어야 하는 시스템은 다음과 같습니다.

```text
audio input
  -> preprocessing
  -> ASRBackend adapter
  -> inference
  -> postprocessing / normalization
  -> transcript response
  -> CER evaluation
  -> metrics / logs / runbook
```

필수 API는 다음입니다.

- `POST /transcribe`
- `GET /healthz`
- `GET /metrics`
- `POST /eval/cer` 또는 동등한 CLI/eval runner

핵심 품질 기준은 다음입니다.

- 모델 구현이 교체 가능한가? (`MockASRBackend`, Whisper, Triton, remote ASR 등)
- CER 계산 기준이 재현 가능한가?
- 전처리/후처리/평가/서빙 코드가 분리되어 있는가?
- 테스트와 로컬 실행 경로가 있는가?
- latency, request id, logging, metrics, runbook이 있는가?

## 구현 범위

각 후보가 만들어야 하는 것은 **production-ready 완제품**이 아니라 **production-oriented v1 scaffold**입니다.

필수 범위는 `docs/07-implementation-scope.md`와 `.claude/skills/asr-pipeline-evaluator/assets/baseline/IMPLEMENTATION_SCOPE.md`에 명시되어 있습니다. 요약:

- 로컬에서 실행 가능한 API 서비스 (`/transcribe`, `/healthz`, `/metrics`)
- GPU 없이 동작하는 `MockASRBackend`
- 교체 가능한 `ASRBackend` 경계
- audio preprocessing / transcript postprocessing 경계
- reference/hypothesis 기반 CER evaluator
- JSONL manifest 또는 동등한 평가 입력 포맷
- 테스트, 로컬 실행 명령, 평가 명령
- architecture, API, eval protocol, implementation scope, runbook 문서

v1 제외 항목: 실제 GPU serving 완성, 모델 학습, diarization, 인증/과금/멀티테넌시, production Kubernetes autoscaling, 대용량 오디오 데이터셋 번들링.

## Claude Code 기준 사용 방식

Claude Code에서는 4개 프레임워크를 **같은 repo에 섞어 설치하지 않는 것**을 권장합니다. 공정 비교를 위해 각 프레임워크를 별도의 workspace에 설치하고, 동일한 baseline prompt와 동일한 skeleton에서 시작해야 합니다.

권장 구조 (이 킷의 실제 레이아웃):

```text
asr-pipeline-evaluator/        # 이 킷의 루트
  CLAUDE.md
  README.md
  versions.md
  .claude/
    commands/                  # /asr-bakeoff-setup, /asr-generate-candidate, /asr-evaluate, ...
    agents/                    # asr-architect, asr-evaluator, asr-ops-reviewer, asr-qa-reviewer
    skills/asr-pipeline-evaluator/
      SKILL.md
      scripts/                 # run_all.py, asr_eval/
      assets/
        baseline/              # ASR_PIPELINE_REQUIREMENTS, API_CONTRACT, EVAL_PROTOCOL, rubric.yaml, test_fixtures/
        prompts/               # common_asr_pipeline_prompt.md, human_review_prompt.md
      references/
  docs/
  workspaces/{spec-kit,openspec,gsd,bmad}/
  outputs/{spec-kit,openspec,gsd,bmad}/
  reports/
```

`workspaces/`는 Claude Code가 각 도구를 사용해 작업하는 공간입니다. `outputs/`는 최종 비교 대상이 되는 산출물입니다. 둘을 분리하면 프레임워크별 임시 파일, 캐시, 설정이 평가 대상 코드와 섞이는 것을 줄일 수 있습니다.

## 문서 읽는 순서

1. `docs/01-claude-code-concepts.md` - Skill, tool, plugin, command 개념 정리
2. `docs/02-framework-isolation.md` - 4개 프레임워크를 어떻게 분리 설치/실행할지
3. `docs/03-bakeoff-workflow.md` - 실제 비교 실험 절차
4. `docs/04-evaluation-playbook.md` - evaluator 실행과 결과 해석
5. `docs/05-faq.md` - 자주 헷갈리는 질문

## 빠른 시작

1. 이 킷의 루트(`asr-pipeline-evaluator/`)에서 Claude Code 세션을 엽니다. 루트 `CLAUDE.md`가 자동 로드됩니다.
2. `docs/02-framework-isolation.md`의 "설치 전략" 섹션을 보고 4개 프레임워크를 각각 `workspaces/<framework>/` 안에 설치합니다 (자세한 명령은 02 문서 참조).
3. 각 workspace에서 `.claude/skills/asr-pipeline-evaluator/assets/prompts/common_asr_pipeline_prompt.md`를 동일하게 입력해 후보를 생성합니다 (또는 `/asr-generate-candidate` 슬래시 커맨드).
4. 각 프레임워크 최종 산출물을 `outputs/<framework>/`로 복사합니다.
5. evaluator를 실행합니다 (또는 `/asr-evaluate` 슬래시 커맨드).

```bash
python .claude/skills/asr-pipeline-evaluator/scripts/run_all.py \
  --targets outputs/spec-kit outputs/openspec outputs/gsd outputs/bmad \
  --labels spec-kit openspec gsd bmad \
  --manifest .claude/skills/asr-pipeline-evaluator/assets/baseline/test_fixtures/manifest.jsonl \
  --rubric .claude/skills/asr-pipeline-evaluator/assets/baseline/rubric.yaml \
  --out reports
```

pytest까지 실행하려면 다음 옵션을 추가합니다.

```bash
--run-pytest
```

이미 각 후보 서버를 띄워둔 상태에서 API smoke test를 하고 싶다면 다음 옵션을 사용합니다.

```bash
--api-base-url http://localhost:8000
```

단, 4개 후보를 동시에 띄우면 포트 충돌이 나기 쉬우므로 API smoke test는 후보별로 따로 실행하는 것을 권장합니다.
