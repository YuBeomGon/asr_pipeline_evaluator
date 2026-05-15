# 02. 4개 프레임워크 설치/실행을 분리하는 방법

질문: "비교할 4개 스킬은 설치해야 하는 거지?"

답: **네. 단, 같은 프로젝트에 전부 섞어 설치하지 않는 것을 권장합니다.**

정확히는 4개가 모두 ChatGPT Skill이라는 뜻은 아닙니다. 이번 실험에서는 Spec Kit, OpenSpec, GSD, BMAD를 Claude Code에서 사용할 수 있는 **workflow framework / command pack / agent workflow**로 보고, 각자 독립된 workspace에 설치하거나 초기화합니다.

## 왜 분리해야 하나

같은 repo에 모두 설치하면 다음 문제가 생깁니다.

- `.claude/commands` 충돌
- `CLAUDE.md` instruction 충돌
- framework별 metadata가 서로 섞임
- 어떤 도구가 만든 산출물인지 구분이 어려움
- 비교 결과가 특정 도구의 성능이 아니라 혼합 설정의 결과가 됨

공정 비교에서는 **격리**가 핵심입니다.

## 권장 디렉터리 구조

```text
asr-pipeline-bakeoff/
  baseline/
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
  evaluator/
    asr-pipeline-evaluator/
  reports/
  versions.md
```

## 각 workspace의 원칙

각 workspace는 같은 조건에서 시작해야 합니다.

- 같은 baseline prompt
- 같은 API contract
- 같은 CER protocol
- 같은 skeleton 또는 빈 repo
- 같은 Claude Code 모델/권한 모드
- 같은 시간 제한
- 같은 외부 dependency 제한

## 설치 기록 남기기

각 프레임워크는 시간이 지나면서 설치 방법이 바뀔 수 있습니다. 그래서 실험할 때는 `versions.md`를 만들어 기록합니다.

예시:

```markdown
# Bakeoff Versions

Date: YYYY-MM-DD
Claude Code version: ...
Model: ...
Permission mode: ...

## Spec Kit
- Source URL:
- Commit/tag/version:
- Install command used:
- Notes:

## OpenSpec
- Source URL:
- Commit/tag/version:
- Install command used:
- Notes:

## GSD
- Source URL:
- Commit/tag/version:
- Install command used:
- Notes:

## BMAD
- Source URL:
- Commit/tag/version:
- Install command used:
- Notes:
```

## 설치 전략

각 workspace 안에서 해당 프레임워크만 설치/초기화합니다. 아래 명령은 2026-05 기준 공식 저장소를 따른 것이며, 실험 시점에 변경되었을 수 있으므로 반드시 각 프로젝트 공식 문서를 한 번 확인하고 `versions.md`에 박제하세요.

### 사전 요구사항

- Claude Code CLI 설치 및 로그인 완료
- Node.js ≥ 20.19 (OpenSpec, GSD, BMAD 공통)
- uv 또는 uvx (Spec Kit) - `curl -LsSf https://astral.sh/uv/install.sh | sh`

### 1. Spec Kit (`github/spec-kit`)

```bash
cd workspaces/spec-kit
uvx --from git+https://github.com/github/spec-kit.git specify init . --ai claude
```

영구 설치를 선호하면:

```bash
uv tool install specify-cli --from git+https://github.com/github/spec-kit.git
specify init . --ai claude
```

설치 후 Claude Code 슬래시 커맨드: `/speckit.constitution`, `/speckit.specify`, `/speckit.plan`, `/speckit.tasks`, `/speckit.implement`.

### 2. OpenSpec (`@fission-ai/openspec`)

```bash
npm install -g @fission-ai/openspec@latest    # 전역 1회
cd workspaces/openspec
openspec init                                  # 프롬프트에서 "Claude Code" 선택
```

`.claude/skills/`, `.claude/commands/`가 workspace 안에 생성되어 자연스럽게 격리됩니다.

### 3. GSD (`gsd-build/get-shit-done`) - 격리 주의

```bash
cd workspaces/gsd
npx get-shit-done-cc@latest
# 프롬프트:
#   runtime: Claude Code
#   scope:   LOCAL (전역 설치를 선택하면 다른 workspace까지 영향)
```

기본값이 `~/.claude/skills/gsd-*/` 전역 설치이므로 베이크오프 격리를 위해 반드시 local/project 옵션을 선택해야 합니다. 설치 후 Claude Code 세션에서 `/gsd-help`로 시작.

### 4. BMAD-METHOD (`bmad-method`)

```bash
cd workspaces/bmad
npx bmad-method install --yes --tools claude-code
```

비대화형으로 옵션을 박고 싶으면:

```bash
npx bmad-method install --yes --modules bmm --tools claude-code \
  --set bmm.user_skill_level=expert
```

Claude Code 슬래시 커맨드: `/pm`, `/sm`, `/dev`, `/qa`.

### 버전 박제 (`versions.md`)

설치 직후 각 도구의 버전을 확인해 `asr-pipeline-bakeoff/versions.md`에 기록합니다.

```bash
# Spec Kit
specify --version

# OpenSpec
openspec --version
npm view @fission-ai/openspec version

# GSD
npm view get-shit-done-cc version

# BMAD
npm view bmad-method version
```

기록 양식:

```markdown
## <Framework name>
- Source URL:
- Commit/tag/version:
- Install command used:
- Claude Code model:        # e.g., Sonnet 4.6 / Opus 4.7
- Permission mode:          # default | accept-edits | plan
- Date:                     # YYYY-MM-DD
- Notes:
```

이후 같은 prompt(`assets/prompts/common_asr_pipeline_prompt.md`)를 사용해 후보 구현을 생성합니다.

## outputs로 복사할 때 주의할 점

평가 대상에는 실제 ASR serving pipeline 산출물만 넣는 것을 권장합니다.

포함:

- source code
- tests
- Dockerfile/compose
- docs/runbook
- eval scripts
- API schema

제외 권장:

- framework 설치 캐시
- Claude Code session log
- 불필요한 임시 파일
- tool-specific lock/log 파일

단, 어떤 프레임워크가 만든 spec이나 task 문서가 실제 구현 이해에 필요하다면 포함해도 됩니다.
