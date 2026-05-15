# 08. 평가 파이프라인 동작 원리 — Commands · Agents · Skills

이 문서는 이번 ASR bakeoff에서 `.claude/` 안의 세 컴포넌트(commands, agents, skills)가
어떻게 연결되어 4개 후보를 평가했는지를 **학습 목적**으로 상세히 설명합니다.

---

## 1. `.claude/` 디렉토리 전체 구조

```
.claude/
├── commands/                        ← 슬래시 커맨드 정의 (절차 지시서)
│   ├── asr-bakeoff-setup.md
│   ├── asr-generate-candidate.md
│   ├── asr-evaluate.md
│   ├── asr-human-review.md
│   └── asr-summarize-results.md
│
├── agents/                          ← 전문 서브에이전트 정의 (전문가 정체성)
│   ├── asr-architect.md
│   ├── asr-evaluator.md
│   ├── asr-ops-reviewer.md
│   └── asr-qa-reviewer.md
│
└── skills/
    └── asr-pipeline-evaluator/      ← 평가 도구 묶음 (기준 자료 + 실행 코드)
        ├── SKILL.md                 ← 스킬 진입점
        ├── scripts/
        │   ├── run_all.py
        │   ├── asr_eval/cer.py
        │   ├── asr_eval/score_artifact.py
        │   ├── asr_eval/test_runner.py
        │   └── asr_eval/report.py
        ├── assets/baseline/
        │   ├── rubric.yaml          ← 자동 채점 기준
        │   ├── test_fixtures/manifest.jsonl
        │   ├── ASR_PIPELINE_REQUIREMENTS.md
        │   ├── API_CONTRACT.md
        │   ├── EVAL_PROTOCOL.md
        │   └── IMPLEMENTATION_SCOPE.md
        └── references/
            ├── rubric.md
            ├── experiment-design.md
            └── target-contract.md
```

---

## 2. 세 컴포넌트의 역할 구분

| 컴포넌트 | 호출 방법 | 역할 한 줄 요약 | 실행 주체 |
|---------|---------|--------------|---------|
| **commands** | `/asr-human-review` 슬래시 커맨드 입력 | **무엇을 할지** — 절차 지시서 | Claude Code 본체 |
| **agents** | 본체가 `Agent(subagent_type=...)` 툴 호출 | **어떤 관점으로 볼지** — 전문가 정체성 | 독립 서브에이전트 |
| **skills** | `/asr-pipeline-evaluator` 또는 본체가 `Skill(...)` 호출 | **어떤 도구·기준으로** — 스크립트 + 기준 데이터 | Claude Code 본체 |

> **핵심**: 이 세 파일은 모두 Python 코드가 아니라 **마크다운 텍스트**입니다.
> Claude Code(모델)가 텍스트를 읽고 의미를 추론해서 어떤 툴을 어떤 순서로 호출할지
> **스스로 결정**합니다. 명시적인 함수 호출 체인이 아닙니다.

---

## 3. 각 컴포넌트 파일 상세

### 3-1. Commands — `commands/asr-human-review.md`

```markdown
# Human Review of ASR Candidates

## Inputs
Read:
  reports/leaderboard.md
  reports/scorecard-spec-kit.md  ...

Then inspect the candidate folders under `outputs/`.

## Review dimensions
Score each candidate from 1 to 5 on:
1. ASR architecture clarity
2. Backend replaceability
...

## Required output
Write: reports/human-review.md
```

- **역할**: "무엇을 하라"는 절차 명세. 입력 파일, 평가 기준, 출력 파일을 지정.
- **모델이 이 파일을 읽으면**: "outputs/ 폴더를 보고, 10개 관점으로 채점하고,
  human-review.md를 써야 한다"고 이해한다.
- 에이전트를 몇 개 병렬로 쓸지는 **모델이 판단** — 커맨드 파일에는 명시되지 않음.

### 3-2. Agents — `agents/asr-architect.md`

```markdown
---
name: asr-architect
description: Reviews ASR serving pipeline architecture...
tools: Read, Grep, Glob, Bash
---

You are an ASR serving pipeline architect.

Review candidate implementations for:
- clear ASRBackend adapter boundary
- replaceability with Whisper, Triton, remote ASR
- separation of audio preprocessing from transcript postprocessing
...
```

- **frontmatter**: 에이전트 이름, 설명, 사용 가능한 툴을 선언.
  `tools: Read, Grep, Glob, Bash` — 이 에이전트는 파일 읽기/검색/실행만 가능.
  Write, Edit 툴은 없어 코드 수정 불가.
- **본문**: 이 에이전트의 system prompt가 됨. 서브에이전트가 "나는 ASR 아키텍트"로 동작.
- **독립 컨텍스트**: 부모 대화 히스토리를 전혀 모르는 상태에서 시작.

4개 에이전트 정의:

| 파일 | 전문 영역 | 주요 체크 항목 |
|------|---------|------------|
| `asr-architect.md` | 아키텍처 | ASRBackend 인터페이스, bytes vs ndarray, 전처리/후처리 경계 |
| `asr-evaluator.md` | CER 평가 | (S+D+I)/N 수식, 집계 방식(micro/macro), empty ref 처리 |
| `asr-ops-reviewer.md` | 운영 준비 | /healthz 백엔드 인식 여부, 메트릭 5종, 파일 크기 제한, Docker 보안 |
| `asr-qa-reviewer.md` | 테스트 품질 | 실제 WAV 바이트 사용 여부, CER 정확한 산술 검증, CLI 서브프로세스 테스트 |

### 3-3. Skills — `skills/asr-pipeline-evaluator/SKILL.md`

```markdown
---
name: asr-pipeline-evaluator
description: Evaluate and compare ASR serving pipeline candidates...
---

## Core evaluation command
python .claude/skills/asr-pipeline-evaluator/scripts/run_all.py \
  --targets outputs/spec-kit ... \
  --rubric .../rubric.yaml \
  --out reports
```

- **역할**: 자동 평가 스크립트 경로, 기준 파일 위치, 출력 형식을 알려줌.
- `rubric.yaml` — 자동 채점 기준 (파일 존재 여부, 엔드포인트 유무 등 정적 체크)
- `manifest.jsonl` — 미리 정의된 (reference, hypothesis) 텍스트 쌍
  (실제 음성 전사 없이 CER 계산 API가 동작하는지만 확인)

---

## 4. 컨텍스트 창이 어떻게 구성되는가

Claude Code는 하나의 **컨텍스트 창(context window)** 에 여러 소스를 층층이 쌓아 동작합니다.

```
┌─────────────────────────────────────────────────────────────┐
│              Claude Code 본체 컨텍스트 창                     │
│                                                             │
│  ① System Prompt                                            │
│     "당신은 Claude Code입니다. Bash, Read, Edit,            │
│      Agent, Skill 등 툴을 사용할 수 있습니다..."              │
│                                                             │
│  ② CLAUDE.md (프로젝트 루트, 자동 로드)                       │
│     "ASR bakeoff 진행 중. 공정성 규칙: 동일한 요구사항         │
│      사용, 워크스페이스 격리, 동일 평가기 실행..."              │
│                                                             │
│  ③ MEMORY.md (자동 메모리 인덱스)                             │
│     "- Project Goal → project_goal.md                      │
│      - Tool Targets → tool_targets.md"                     │
│                                                             │
│  ④ 슬래시 커맨드 실행 시 추가                                  │
│     commands/asr-human-review.md 전체 내용 주입              │
│                                                             │
│  ⑤ 대화 히스토리 (누적)                                       │
│     사용자 메시지, 툴 호출 결과, 이전 답변들...                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

서브에이전트는 **완전히 별개의 컨텍스트 창**을 가집니다:

```
부모 Claude Code                     asr-architect 서브에이전트
─────────────────                    ───────────────────────────
[대화 히스토리 전체]                   [새 컨텍스트, 부모 모름]
[CLAUDE.md]                           │
[MEMORY.md]           →  spawn        ├─ ① System: agents/asr-architect.md
[command 내용]                        │   "당신은 ASR 아키텍트입니다..."
[이전 리뷰 결과]                       │
                                      ├─ ② 부모가 작성한 prompt
                                      │   "outputs/spec-kit/ 읽고
                                      │    backend interface 분석하라"
                                      │
                                      └─ ③ 에이전트가 Read/Grep 툴로
                                           파일 직접 읽으며 컨텍스트 축적
```

---

## 5. 전체 평가 파이프라인 흐름

이번 bakeoff에서 실제로 실행된 순서입니다.

```
단계 1 — 자동 루브릭 평가  (/asr-evaluate)
─────────────────────────────────────────
사용자: "/asr-evaluate"
  │
  ├─ commands/asr-evaluate.md 로드
  │   "run_all.py를 이 인수로 실행하라"
  │
  └─ Bash 툴 실행
      python .claude/skills/.../run_all.py
        --targets outputs/spec-kit outputs/openspec outputs/gsd outputs/bmad
        --rubric  .../rubric.yaml
        --manifest .../manifest.jsonl
        --run-pytest

      결과: 전원 100/100 (정적 체크 기반 — 파일 존재 여부, API 엔드포인트 유무)
      → reports/leaderboard.md, scorecard-*.md 생성


단계 2 — 정성 리뷰  (/asr-human-review)
──────────────────────────────────────
사용자: "/asr-human-review"
  │
  ├─ commands/asr-human-review.md 로드
  │   "outputs/ 보고, 10개 관점 1~5점, human-review.md 써라"
  │
  ├─ 모델 판단: "4개 전문 에이전트 병렬로 실행하자"
  │
  ├─ Agent(subagent_type="asr-architect")  ──┐
  ├─ Agent(subagent_type="asr-evaluator")  ──┤  병렬 실행
  ├─ Agent(subagent_type="asr-ops-reviewer")─┤  각자 독립 컨텍스트
  └─ Agent(subagent_type="asr-qa-reviewer") ─┘
       │
       │  각 에이전트: outputs/{spec-kit,openspec,gsd,bmad}/ 직접 읽음
       │  → 점수 + 근거 + 파일:줄번호 인용
       │
       ▼
  4개 리포트 반환 → 본체가 종합
       │
       └─ reports/human-review.md 작성
           (17개 세부 항목 × 4개 후보 = 68개 점수)
```

---

## 6. spec-kit 평가 세부 — asr-architect 에이전트 예시

spec-kit 아키텍처 리뷰에서 에이전트가 실제로 수행한 과정:

```
① agents/asr-architect.md 로드 (system prompt)
   "나는 ASR 아키텍트. bytes vs ndarray 같은 것을 본다."

② 부모가 준 prompt
   "outputs/spec-kit/ 읽고, ASRBackend 인터페이스,
    backend replaceability, 전처리 경계 분석하라"

③ 에이전트가 Read 툴로 파일 순차 탐색
   outputs/spec-kit/src/backends/base.py
     → "transcribe(audio_bytes: bytes, ...) 발견"
     → "bytes 인터페이스 — 모든 실제 백엔드가 numpy 쓰는데 불일치!"

   outputs/spec-kit/src/api/routes.py:132
     → "chunk.samples.tobytes() 호출"
     → "ndarray → bytes 변환 후 mock.py에서 다시 frombuffer로 복원"
     → "불필요한 왕복 직렬화 확인"

   outputs/spec-kit/src/audio/postprocessing.py
     → "NFC(표시용) vs NFKC(CER용) 명시적 문서화 — 강점"

④ 점수 산정
   - ASR architecture clarity:   3/5  (bytes 인터페이스 결함)
   - Backend replaceability:     3/5  (Whisper 교체 시 직렬화 재구현 필요)
   - Audio preprocessing bounds: 4/5  (AudioChunk 타입 명확)
   - Extensibility:              3/5  (인터페이스 수정 없인 교체 어려움)
```

---

## 7. 자동 평가 vs 정성 평가 비교

| 항목 | 자동 루브릭 (`run_all.py`) | 정성 리뷰 (specialist agents) |
|------|--------------------------|------------------------------|
| 방식 | 정적 파일 체크 + pytest | 코드 직접 읽기 + 추론 |
| 속도 | 빠름 (수 분) | 느림 (에이전트당 4~8분) |
| 결과 | spec-kit 100, openspec 100, gsd 100, bmad 100 | spec-kit 65, openspec 75, gsd 56, bmad 61 |
| 발견 못한 것 | bytes 인터페이스, macro CER, empty-ref 버그, global mutable backend | — |
| 용도 | 1차 필터링 (뭔가 아예 없는지) | 실제 품질 판단 |

자동 루브릭이 전원 100점을 준 이유: 파일 존재 여부, 엔드포인트 유무,
pytest 통과 여부만 체크했기 때문. **CER 수식이 맞는지, 집계가 표준인지,
백엔드 인터페이스 타입이 적합한지** 같은 의미론적 품질은 코드를 읽는
에이전트만 발견할 수 있습니다.

---

## 8. 각 에이전트가 발견한 핵심 결함 요약

### asr-architect 발견
| 후보 | 결함 | 파일:줄 |
|------|------|--------|
| spec-kit | `transcribe(audio_bytes: bytes)` — ndarray 아닌 bytes 인터페이스 | `src/backends/base.py:62` |
| gsd | `_BACKEND = MockASRBackend()` 조용한 fallback (프로덕션 안전 위협) | `src/api/routes/transcribe.py:20` |
| bmad | 후처리가 route에 인라인 (`unicodedata.normalize("NFC", result.text)`) | `src/api/routes/transcribe.py:70` |

### asr-evaluator 발견
| 후보 | 결함 | 파일:줄 |
|------|------|--------|
| openspec | macro CER을 primary 집계로 사용 (ASR 표준은 micro) | `src/eval/cer.py:232` |
| bmad | empty ref + non-empty hyp → CER=0.0 (환각 완벽 점수 버그) | `src/eval/cer.py:160` |
| gsd | 중복된 NFC 적용 (NFKC 이후 NFC — 무해하지만 문서 노이즈) | `src/eval/normalizer.py:19` |

### asr-ops-reviewer 발견
| 후보 | 결함 | 파일 |
|------|------|------|
| spec-kit/gsd/bmad | `/healthz`가 백엔드 상태 무시 (항상 ok 반환) | `src/api/routes/health.py` |
| gsd | Compose healthcheck에서 curl 사용 — 이미지에 curl 없음 | `docker-compose.yml` |
| gsd/bmad | env_prefix 없어 `HOST`, `PORT` 등 쉘 변수와 충돌 | `src/config/settings.py` |
| 전체 | 파일 크기 제한 없음 (openspec 제외) | — |

### asr-qa-reviewer 발견
| 후보 | 강점 | 약점 |
|------|------|------|
| spec-kit | 44kHz 스테레오 리샘플링 통합 테스트 | 백엔드 단위 테스트 없음 |
| openspec | 83개 테스트, 엔드포인트별 파일 분리 | 리샘플링 통합 테스트 없음 |
| bmad | 서브프로세스 CLI 스모크 테스트, on-disk fixture | 빈 파일 통합 테스트 없음 |
| gsd | macro vs micro CER 구분 단위 테스트 | 42개 테스트로 가장 적음 |

---

## 9. 핵심 요약

```
Commands  = 절차 지시서     "무엇을 해라" (What)
Agents    = 전문가 정체성   "어떤 관점으로" (How / Who)
Skills    = 도구 + 기준     "어떤 도구로" (With What)

모든 파일은 마크다운 텍스트 → 모델이 읽고 의미 추론 → 툴 호출 결정
명시적 함수 호출 체인이 아닌, 텍스트 해석 기반 자율 오케스트레이션
```

서브에이전트의 독립 컨텍스트가 핵심입니다. 4개 에이전트가 서로의 결과를 모르는 상태에서
각자 코드를 읽기 때문에 편향 없는 독립적 리뷰가 가능합니다.
