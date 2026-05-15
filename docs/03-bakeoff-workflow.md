# 03. Claude Code 기준 ASR Pipeline Bakeoff Workflow

이 문서는 실제 비교 실험 절차입니다.

## Step 0. 실험 목적 고정

이번 실험의 목적은 다음입니다.

> Spec Kit, OpenSpec, GSD, BMAD 중 어떤 프레임워크가 Claude Code에서 더 좋은 ASR serving pipeline 산출물을 만들도록 유도하는가?

좋은 산출물의 기준:

- ASR backend가 교체 가능하다.
- `/transcribe`, `/healthz`, `/metrics`, CER eval 경로가 있다.
- CER normalization policy가 명확하다.
- 테스트와 Docker/local run 경로가 있다.
- 운영 지표, request id, runbook이 있다.

## Step 1. baseline 확인

baseline 파일은 이미 `.claude/skills/asr-pipeline-evaluator/assets/baseline/` 아래에 있습니다.

```text
.claude/skills/asr-pipeline-evaluator/assets/baseline/
  ASR_PIPELINE_REQUIREMENTS.md
  API_CONTRACT.md
  EVAL_PROTOCOL.md
  rubric.yaml
  test_fixtures/
```

자체 baseline으로 덮어쓰고 싶으면 해당 파일만 교체합니다.

## Step 2. workspace/outputs/reports 확인

`workspaces/{spec-kit,openspec,gsd,bmad}/`, `outputs/{spec-kit,openspec,gsd,bmad}/`, `reports/`는 이 킷에 이미 비어있는 스켈레톤으로 포함되어 있습니다. 추가로 만들 필요는 없습니다.

## Step 3. Claude Code instruction 적용

루트 `CLAUDE.md`는 Claude Code가 이 프로젝트 어디서 세션을 열든 자동 로드합니다. 단, 각 framework가 자기 workspace를 독립 프로젝트로 init하는 경우(예: BMAD/OpenSpec의 `init`이 그 폴더에 `CLAUDE.md`나 `.claude/`를 새로 만드는 경우) 루트 지침이 가려질 수 있으니 다음 중 하나를 권장합니다.

```bash
# 옵션 A: 루트에서 Claude Code를 열고 cd 또는 파일 지정으로 workspace 작업
# (루트 CLAUDE.md가 그대로 작동)

# 옵션 B: 루트 CLAUDE.md를 각 workspace에도 복사
for w in workspaces/spec-kit workspaces/openspec workspaces/gsd workspaces/bmad; do
  cp CLAUDE.md "$w/CLAUDE.md"
done
```

## Step 4. 각 프레임워크 설치/초기화

각 workspace 안에서 해당 프레임워크만 설치/초기화합니다. 구체 명령과 사전 요구사항은 `docs/02-framework-isolation.md`의 "설치 전략" 섹션을 따르세요. 요약:

```bash
# Spec Kit
cd workspaces/spec-kit && uvx --from git+https://github.com/github/spec-kit.git specify init . --ai claude

# OpenSpec  (npm i -g @fission-ai/openspec@latest 선행)
cd workspaces/openspec && openspec init        # Claude Code 선택

# GSD  (반드시 LOCAL scope 선택)
cd workspaces/gsd && npx get-shit-done-cc@latest

# BMAD
cd workspaces/bmad && npx bmad-method install --yes --tools claude-code
```

설치 직후 각 도구 버전을 `versions.md`에 박제합니다.

## Step 5. 동일 prompt 입력

4개 프레임워크 모두에게 동일한 prompt를 입력합니다.

사용할 prompt:

```text
.claude/skills/asr-pipeline-evaluator/assets/prompts/common_asr_pipeline_prompt.md
```

프롬프트를 복사해 Claude Code에 붙여넣거나, 프레임워크별 command에 전달합니다.

## Step 6. 결과물을 outputs로 정리

각 workspace의 최종 구현물을 다음 위치로 복사합니다.

```text
outputs/spec-kit/
outputs/openspec/
outputs/gsd/
outputs/bmad/
```

작업 중간 파일이 아니라 최종 후보 repo만 들어가야 합니다.

## Step 7. evaluator 실행

```bash
python .claude/skills/asr-pipeline-evaluator/scripts/run_all.py \
  --targets outputs/spec-kit outputs/openspec outputs/gsd outputs/bmad \
  --labels spec-kit openspec gsd bmad \
  --manifest .claude/skills/asr-pipeline-evaluator/assets/baseline/test_fixtures/manifest.jsonl \
  --rubric .claude/skills/asr-pipeline-evaluator/assets/baseline/rubric.yaml \
  --out reports
```

Claude Code 안에서는 동등하게 슬래시 커맨드 `/asr-evaluate`를 호출해도 됩니다.

### Step 7b. 한국어 실 데이터로 평가하기

`assets/baseline/test_fixtures/manifest.jsonl`은 evaluator 자체 검증용 sample 3개입니다. 실제 한국어 데이터(`data/audio/`, `data/labels/`)로 평가하려면 manifest 빌더로 한 번에 생성합니다.

```bash
python .claude/skills/asr-pipeline-evaluator/scripts/build_manifest.py \
  --audio-dir data/audio \
  --labels-dir data/labels \
  --out data/manifest.jsonl
```

빌더는 wav와 txt를 베이스네임으로 페어링하고, 각 라벨 파일 내용을 `reference`로 채웁니다. `hypothesis`는 빈 문자열로 남으며, 후보가 `/transcribe`로 처리한 결과를 그 자리에 채워서 다시 evaluator에 넘기는 흐름입니다.

생성된 manifest로 평가:

```bash
python .claude/skills/asr-pipeline-evaluator/scripts/run_all.py \
  --targets outputs/spec-kit outputs/openspec outputs/gsd outputs/bmad \
  --labels spec-kit openspec gsd bmad \
  --manifest data/manifest.jsonl \
  --rubric .claude/skills/asr-pipeline-evaluator/assets/baseline/rubric.yaml \
  --out reports
```

## Step 8. pytest 옵션

후보 repo들이 의존성 설치 없이 테스트 가능한 상태라면 `--run-pytest`를 추가합니다.

```bash
python .claude/skills/asr-pipeline-evaluator/scripts/run_all.py \
  --targets outputs/spec-kit outputs/openspec outputs/gsd outputs/bmad \
  --labels spec-kit openspec gsd bmad \
  --manifest .claude/skills/asr-pipeline-evaluator/assets/baseline/test_fixtures/manifest.jsonl \
  --rubric .claude/skills/asr-pipeline-evaluator/assets/baseline/rubric.yaml \
  --out reports \
  --run-pytest
```

## Step 9. 사람 리뷰

자동 점수만으로 끝내지 않습니다.

`reports/leaderboard.md`와 `reports/scorecard-*.md`를 읽고, 다음 항목은 사람이 다시 봅니다.

- backend abstraction이 실제로 의미 있는가?
- CER normalization이 한국어/영어/공백 정책에 맞는가?
- streaming ASR로 확장 가능한가?
- GPU worker, queue, timeout, retry 설계가 있는가?
- 운영 장애 상황에서 runbook이 도움이 되는가?

## Step 10. 최종 판단

최종 결과는 한 줄 순위보다 다음 형태가 좋습니다.

```text
Best for greenfield architecture: ...
Best for iterative changes: ...
Best for implementation velocity: ...
Best for team planning: ...
Best overall for this ASR serving pipeline: ...
```
