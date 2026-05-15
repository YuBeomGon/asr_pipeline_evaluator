# ASR Bakeoff — 통합 점수 비교표

리뷰 날짜: 2026-05-15  
평가자: asr-architect · asr-evaluator · asr-ops-reviewer · asr-qa-reviewer (병렬 전문 에이전트)

> 자동 루브릭은 4개 전원 100/100으로 의미 있는 차이를 보여주지 못했습니다.
> 아래는 코드를 직접 읽은 전문 에이전트의 정성 평가 결과입니다.

---

## 최종 순위

| 순위 | 후보 | 총점 (85) | 핵심 강점 | 핵심 약점 |
|:---:|---|:---:|---|---|
| 🥇 1 | **OpenSpec** | **75** | 비동기 안전 ContextVar 로깅, 5종 메트릭, 백엔드 인식 헬스체크, 413 제한 | CER 집계가 macro (비표준) |
| 🥈 2 | **Spec-Kit** | **65** | 유일하게 올바른 micro-CER + empty-ref 제외, 리샘플링 통합 테스트 | `bytes` 백엔드 인터페이스 (불필요한 직렬화) |
| 🥉 3 | **BMAD** | **61** | 데코레이터 기반 백엔드 레지스트리, CLI 서브프로세스 스모크 테스트 | empty-ref + non-empty hyp → CER=0.0 버그 |
| 4 | **GSD** | **56** | macro+micro CER 모두 노출, 전용 normalizer 모듈, librosa 리샘플러 | 전역 가변 `_BACKEND` 조용한 mock fallback |

---

## 세부 점수 (17개 항목 × 4개 후보)

### 아키텍처 (20점 만점)

| 항목 | Spec-Kit | OpenSpec | GSD | BMAD |
|---|:---:|:---:|:---:|:---:|
| ASR 아키텍처 명확성 | 3 | **5** | 3 | 4 |
| 백엔드 교체 가능성 | 3 | **5** | 3 | 4 |
| 오디오 전처리 경계 | 4 | 4 | 3 | 4 |
| 실제 백엔드 확장성 | 3 | **5** | 3 | 4 |
| **소계** | **13** | **19** | **12** | **16** |

### CER 평가 (20점 만점)

| 항목 | Spec-Kit | OpenSpec | GSD | BMAD |
|---|:---:|:---:|:---:|:---:|
| CER 수식 정확성 | **5** | **5** | **5** | 4 |
| 정규화 정책 명확성 | **5** | **5** | 4 | **5** |
| 집계 방식 정확성 | **5** | 2 | **5** | 2 |
| 엣지 케이스 처리 | **5** | 3 | 3 | 2 |
| **소계** | **20** | **15** | **17** | **13** |

### 운영 준비 (25점 만점)

| 항목 | Spec-Kit | OpenSpec | GSD | BMAD |
|---|:---:|:---:|:---:|:---:|
| 헬스체크 품질 | 2 | **5** | 2 | 2 |
| 메트릭 완성도 | 3 | **5** | 3 | 3 |
| 로깅 품질 | 4 | **5** | 3 | 3 |
| 에러 핸들링 | 3 | 4 | 4 | 3 |
| 운영 문서 | 4 | **5** | 3 | 4 |
| **소계** | **16** | **24** | **15** | **15** |

### 테스트 품질 (20점 만점)

| 항목 | Spec-Kit | OpenSpec | GSD | BMAD |
|---|:---:|:---:|:---:|:---:|
| 테스트 현실성 | 4 | 4 | 3 | 4 |
| API 계약 커버리지 | 4 | 4 | 3 | 3 |
| CER 평가 테스트 품질 | 4 | 4 | 3 | **5** |
| CI 실행 가능성 | 4 | 4 | 3 | 4 |
| **소계** | **16** | **16** | **12** | **16** |

### 총점

| 후보 | 아키텍처 | CER 평가 | 운영 준비 | 테스트 | **합계** |
|---|:---:|:---:|:---:|:---:|:---:|
| OpenSpec | 19/20 | 15/20 | **24/25** | 16/20 | **74** |
| Spec-Kit | 13/20 | **20/20** | 16/25 | 16/20 | **65** |
| BMAD | 16/20 | 13/20 | 15/25 | 16/20 | **60** |
| GSD | 12/20 | 17/20 | 15/25 | 12/20 | **56** |

---

## 자동 루브릭 vs 정성 평가 비교

| 후보 | 자동 루브릭 | 정성 평가 | 차이 원인 |
|---|:---:|:---:|---|
| OpenSpec | 100 | **74** | 자동 루브릭이 CER 집계 방식(macro vs micro)을 구분하지 못함 |
| Spec-Kit | 100 | **65** | `bytes` 인터페이스 문제, 헬스체크 backend-blind를 파일 존재로 통과 |
| BMAD | 100 | **60** | empty-ref CER 버그가 pytest 통과 (잘못된 동작을 assert) |
| GSD | 100 | **56** | global mutable `_BACKEND` silent fallback은 정적 체크로 잡히지 않음 |

---

## 항목별 1위

| 평가 항목 | 1위 후보 | 근거 |
|---|---|---|
| ASR 아키텍처 | **OpenSpec** | `np.ndarray` 인터페이스, `health_check()` ABC, 타입 `ASRBackendError` |
| 백엔드 교체 용이성 | **OpenSpec** | `lru_cache` 레지스트리, env 변수 하나로 교체 |
| CER 수식 정확성 | **공동 1위** (spec-kit·openspec·gsd) | 모두 올바른 Levenshtein CER |
| CER 집계 방식 | **Spec-Kit / GSD** | micro-CER 사용 (ASR 표준), GSD는 macro도 함께 노출 |
| empty-ref 처리 | **Spec-Kit** | `cer=None` 반환 후 집계 제외 — EVAL_PROTOCOL 완전 준수 |
| 헬스체크 | **OpenSpec** | 백엔드 `health_check()` 호출, tri-state 반환 |
| 메트릭 완성도 | **OpenSpec** | 5종 (`requests`, `errors`, `duration`, `audio_duration`, `inference_duration`) |
| 로깅 | **OpenSpec** | `ContextVar` 기반 — 유일한 async 안전 request ID 전파 |
| CER 테스트 품질 | **BMAD** | 실제 CLI 서브프로세스 테스트 + on-disk fixture manifest |
| 운영 문서 | **BMAD** | `.env.example` 제공, 메트릭 테이블, 백엔드 교체 가이드 |
| 정규화 모듈 분리 | **GSD** | 전용 `normalizer.py` — CER과 후처리가 공통 모듈 공유 |

---

## 수정이 필요한 핵심 버그

| 우선순위 | 후보 | 버그 | 파일:줄 |
|:---:|---|---|---|
| P0 | BMAD | empty ref + non-empty hyp → CER=0.0 (환각 완벽 점수) | `src/eval/cer.py:160` |
| P0 | GSD | `_BACKEND = MockASRBackend()` silent fallback (프로덕션 안전 위협) | `src/api/routes/transcribe.py:20` |
| P1 | OpenSpec | macro CER을 primary 집계로 사용 (표준은 micro) | `src/eval/cer.py:232` |
| P1 | Spec-Kit | `transcribe(audio_bytes: bytes)` — ndarray가 올바른 인터페이스 | `src/backends/base.py:62` |
| P2 | GSD | Compose healthcheck에서 curl 사용 (이미지에 curl 없음) | `docker-compose.yml` |
| P2 | GSD/BMAD | `env_prefix` 없어 `HOST`, `PORT` 쉘 변수 충돌 위험 | `src/config/settings.py` |
| P2 | spec-kit/gsd/bmad | `/healthz`가 백엔드 상태 무시 | `src/api/routes/health.py` |
| P2 | 전체 (openspec 제외) | 파일 크기 제한 없음 (무제한 업로드 허용) | — |

---

## 추천

**단일 후보 선택 기준:**
- CER 정확성이 가장 중요하다면 → **Spec-Kit** (유일한 완전한 micro-CER)
- 프로덕션 운영 준비도가 중요하다면 → **OpenSpec** (헬스체크·메트릭·로깅 모두 우수)
- 전반적 균형 → **OpenSpec** (총점 1위)

**최선의 구성:** OpenSpec 기반 + Spec-Kit의 CER 설계 채택
(macro→micro 집계 수정, empty-ref `cer=None` 처리 적용)
