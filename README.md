# ASR Claude Code Bakeoff Kit

이 저장소는 동일한 ASR 서빙 파이프라인 과제를 4개의 AI 개발 프레임워크에 동일하게 던져 비교하기 위한 **Claude Code 워크스페이스 템플릿**입니다.

비교 대상:

- Spec Kit
- OpenSpec
- GSD
- BMAD

목표는 각 프레임워크의 마케팅 문구를 비교하는 것이 아니라, 통제된 베이크오프(bakeoff)를 돌리는 것입니다.

1. 각 프레임워크에 동일한 ASR 서빙 파이프라인 요구사항을 줍니다.
2. 각 프레임워크는 자기 격리 workspace에서만 동작합니다.
3. 프레임워크당 후보 구현물 1개를 생성합니다.
4. 각 후보를 `outputs/<framework>/`로 복사합니다.
5. 동일한 evaluator로 4개 산출물을 모두 채점합니다.
6. leaderboard, scorecard, failure analysis를 사람이 검토합니다.

## 대상 시스템 (Target system)

각 후보가 만들 시스템은 production 지향의 음성인식 서빙 파이프라인입니다.

```text
audio input
  -> preprocessing
  -> ASR backend adapter
  -> inference
  -> transcript postprocessing
  -> API response
  -> CER evaluation
  -> observability and runbook
```

필수 API:

- `POST /transcribe`
- `GET /healthz`
- `GET /metrics`
- `POST /eval/cer` 또는 동등한 로컬 CER evaluator

GPU 없이 mock ASR backend로 로컬 실행 가능해야 하며, 실제 backend(Whisper, Triton, 원격 모델 서버, 매니지드 ASR API 등)는 `ASRBackend` 인터페이스 뒤로 교체 가능해야 합니다.

## 구현 범위 (Implementation scope)

구현 범위는 명시되어 있습니다. 후보 생성 전 반드시 다음 두 문서를 읽으세요.

```text
docs/07-implementation-scope.md
.claude/skills/asr-pipeline-evaluator/assets/baseline/IMPLEMENTATION_SCOPE.md
```

요약하면, 각 후보는 **v1 ASR 서빙 파이프라인 scaffold**를 만들면 됩니다: 로컬 실행 가능한 API 서비스, mock backend, backend abstraction, preprocessing 경계, postprocessing 경계, CER evaluator, 테스트, 로컬 실행 명령, 문서.

이번 1차 베이크오프에서는 **다음 항목을 요구하지 않습니다**: 실제 GPU 추론, 모델 학습, diarization, 인증, 과금, production Kubernetes autoscaling. 추후 명시적으로 추가하기 전까지는 모두 v1 out-of-scope입니다.

## 저장소 레이아웃 (Repository layout)

```text
asr-claude-code-bakeoff-kit/
  README.md
  CLAUDE.md

  .claude/
    commands/
      asr-bakeoff-setup.md
      asr-generate-candidate.md
      asr-evaluate.md
      asr-human-review.md
      asr-summarize-results.md
    agents/
      asr-architect.md
      asr-evaluator.md
      asr-ops-reviewer.md
      asr-qa-reviewer.md
    skills/
      asr-pipeline-evaluator/
        SKILL.md
        scripts/
        assets/
        references/

  docs/
    README.md
    01-claude-code-concepts.md
    02-framework-isolation.md
    03-bakeoff-workflow.md
    04-evaluation-playbook.md
    05-faq.md
    06-what-this-kit-does.md
    07-implementation-scope.md

  workspaces/
    spec-kit/
    openspec/
    gsd/
    bmad/

  outputs/
    spec-kit/
    openspec/
    gsd/
    bmad/

  reports/
```

## 중요한 구분

이 패키지는 **ChatGPT Skill 업로드용 패키지가 아닙니다**.

의도된 결정입니다. 이전 `agents/openai.yaml` 파일은 ChatGPT Skill 패키징 전용이었습니다. Claude Code에서는 다음이 핵심 자산입니다.

- `CLAUDE.md` — 프로젝트 지침
- `.claude/commands/` — 재사용 가능한 슬래시 커맨드 프롬프트
- `.claude/agents/` — 리뷰어/아키텍트 전문 에이전트
- `.claude/skills/` — 재사용 가능한 task-specific 절차와 스크립트

## Claude Code에서 사용하는 법

이 폴더를 Claude Code에서 열고, 먼저 다음 문서들을 읽습니다.

```text
README.md
CLAUDE.md
docs/06-what-this-kit-does.md
```

그리고 setup 커맨드를 호출합니다.

```text
Use .claude/commands/asr-bakeoff-setup.md and prepare the bakeoff workspace.
```

각 비교 프레임워크는 자기 workspace 안에서만 설치/초기화합니다.

```text
workspaces/spec-kit/
workspaces/openspec/
workspaces/gsd/
workspaces/bmad/
```

같은 workspace에 4개를 모두 설치하지 마세요. 지침, 커맨드, 컨텍스트 파일이 서로 충돌합니다.

## 후보 생성 (Generate candidates)

각 프레임워크에 동일한 후보 생성 프롬프트를 입력합니다. 예:

```text
Use .claude/commands/asr-generate-candidate.md for the spec-kit workspace.
```

`spec-kit`, `openspec`, `gsd`, `bmad` 각각 반복합니다.

각 프레임워크가 끝나면 결과 구현물을 다음 위치로 복사합니다.

```text
outputs/spec-kit/
outputs/openspec/
outputs/gsd/
outputs/bmad/
```

## 후보 채점 (Evaluate candidates)

```bash
python .claude/skills/asr-pipeline-evaluator/scripts/run_all.py \
  --targets outputs/spec-kit outputs/openspec outputs/gsd outputs/bmad \
  --labels spec-kit openspec gsd bmad \
  --manifest .claude/skills/asr-pipeline-evaluator/assets/baseline/test_fixtures/manifest.jsonl \
  --rubric .claude/skills/asr-pipeline-evaluator/assets/baseline/rubric.yaml \
  --out reports
```

후보들이 의존성 설치 없이 테스트 가능한 상태라면 `--run-pytest`를 추가합니다.

## 산출물 (Outputs)

evaluator가 작성하는 파일:

```text
reports/leaderboard.md
reports/scorecard-spec-kit.md
reports/scorecard-openspec.md
reports/scorecard-gsd.md
reports/scorecard-bmad.md
reports/failure-analysis.md
reports/all-scores.json
reports/reference-cer.json
```

## 권장 워크플로

1. Target 요구사항을 읽는다.
2. 각 workspace에 프레임워크 1개씩만 설치한다.
3. 같은 task 프롬프트로 4개 후보를 모두 생성한다.
4. outputs를 freeze한다.
5. evaluator를 실행한다.
6. `.claude/agents/asr-evaluator.md`와 `.claude/commands/asr-human-review.md`로 사람 리뷰.
7. `.claude/commands/asr-summarize-results.md`로 결과 요약.

## 포함된 것과 포함되지 않은 것

포함:

- Claude Code 프로젝트 지침
- Claude 슬래시 커맨드 프롬프트
- Claude 리뷰어/아키텍트 에이전트 프롬프트
- ASR evaluator 스크립트
- CER 레퍼런스 구현
- 정적 채점 rubric
- baseline ASR 요구사항, 구현 범위, API 계약
- evaluation playbook

미포함:

- Spec Kit, OpenSpec, GSD, BMAD 자체 (서드파티 프레임워크)
- production ASR 모델
- 오디오 데이터셋
- GPU 벤치마크 인프라

4개 프레임워크는 비교하려는 정확한 버전을 직접 격리된 workspace에 설치하세요.
