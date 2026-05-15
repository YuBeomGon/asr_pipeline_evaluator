# 07. 구현 범위 (Implementation Scope)

이 문서는 Spec Kit / OpenSpec / GSD / BMAD 가 생성하는 각 후보의 **정확한 구현 범위**를 정의합니다.

베이크오프의 목적은 풀세트 production ASR 플랫폼을 만드는 것이 **아닙니다**. 동일한 제약 아래에서 어느 workflow 프레임워크가 가장 좋은 **production 지향 v1 ASR 서빙 파이프라인 scaffold**를 만드는지 비교하는 것입니다.

## 범위 레벨

프롬프트, 리뷰, 스코어카드에서 일관되게 다음 레이블을 사용합니다.

| 레벨 | 의미 |
|---|---|
| MUST | 유효한 v1 후보의 필수 조건. 빠지면 감점. |
| SHOULD | 강력히 권장. 빠지면 운영 신뢰도 감소. |
| MAY | 선택 사항. 없어도 감점하지 않음. |
| OUT OF SCOPE | 이번 베이크오프에서는 구현하지 않음 (추후 명시적으로 추가하지 않는 한). |

## v1 후보가 MUST 구현해야 하는 것

각 프레임워크 후보는 다음을 포함한 **실행 가능한** repository를 만들어야 합니다.

### 1. 로컬 실행 가능 API 서비스

다음 endpoint를 가진 로컬 서비스를 제공해야 합니다.

- `POST /transcribe`
- `GET /healthz`
- `GET /metrics`

선호 스택은 Python + FastAPI지만, 명확히 실행 가능하고 테스트 가능한 다른 스택도 허용합니다.

### 2. Mock ASR backend

다음 없이도 repository가 동작하도록 `MockASRBackend` 또는 동등한 가짜 backend를 포함해야 합니다.

- GPU
- 실제 ASR 모델 가중치
- 네트워크 접근
- 유료 ASR provider 자격증명

Mock backend의 목적은 서빙 파이프라인 **구조**를 테스트하는 것이지 음성 정확도를 테스트하는 것이 아닙니다.

### 3. ASR backend 인터페이스

다음과 같은 후속 교체가 가능한 backend 인터페이스 또는 protocol을 정의해야 합니다.

- Whisper 또는 faster-whisper
- Triton 또는 다른 모델 서버
- 원격 ASR HTTP/gRPC 서비스
- 매니지드 클라우드 ASR 제공자

API 라우트가 특정 모델 구현에 직접 의존하면 안 됩니다.

### 4. 오디오 입력과 preprocessing 경계

`/transcribe` 를 통해 로컬 오디오 업로드를 받아야 합니다.

다음과 같은 관심사를 다루는 **별도의 preprocessing 경계 또는 모듈**이 있어야 합니다.

- 파일 검증
- sample rate 처리
- 지속시간 추출
- 정규화 hook
- 청킹 hook

v1에서는 실제 오디오 디코딩이 가볍거나 mock이어도 무방하지만, **경계 자체는 반드시 존재해야** 합니다.

### 5. Transcript postprocessing 경계

raw backend 출력과 transcript postprocessing을 **분리**해야 합니다.

텍스트 정규화, 구두점 정책, 대소문자 정책, 언어별 cleanup이 어디에서 일어나는지 코드 상 분명히 드러나야 합니다.

### 6. CER 평가

reference/hypothesis 쌍을 사용한 CER 평가를 제공해야 합니다.

JSONL manifest 입력 또는 동등한 문서화된 포맷을 지원해야 합니다.

CER 계산 이전 단계의 **정규화 정책을 문서화**해야 합니다.

다음을 보고해야 합니다.

- per-sample CER 또는 per-sample edit count
- aggregate CER
- 총 substitution / deletion / insertion 또는 동등한 edit-distance 근거

### 7. 테스트

다음에 대한 테스트가 있어야 합니다.

- CER 계산
- mock backend 또는 transcribe 흐름
- API health 또는 transcribe endpoint

테스트 명령은 문서화되어야 합니다.

### 8. 로컬 실행 가이드

다음이 모두 문서화되어 있어야 합니다.

- 의존성 설치 명령
- 로컬 서버 실행 명령
- 테스트 명령
- 평가(eval) 명령

### 9. 문서

다음을 문서화해야 합니다.

- 아키텍처
- API 사용법
- eval protocol
- 구현 범위 (implementation scope)
- 알려진 한계 (known limitations)

후보는 자기 `docs/implementation_scope.md`를 두거나, `README.md` 안에 명확한 제목으로 동등한 섹션을 두어야 합니다.

## v1 후보가 SHOULD 구현하는 것

절대 필수는 아니지만, 채점과 사람 리뷰에서 중요합니다.

- Dockerfile
- request ID 생성 및 전달
- 구조화된 logging
- preprocess / inference / postprocess / 전체 요청 시간의 latency timing
- Prometheus 스타일 metrics 또는 구조화된 metrics 요약
- 환경 변수 또는 설정 파일 기반 configuration
- timeout 처리
- 잘못된 오디오 입력에 대한 명확한 error 응답
- 다음과 유사한 **깔끔한 모듈 레이아웃**:

```text
src/
  api/
  audio/
  backends/
  eval/
  observability/
  config/
tests/
  unit/
  integration/
  eval/
docs/
```

## v1 후보가 MAY 구현하는 것

선택 항목입니다. 사람 리뷰에 좋게 작용할 수 있지만 비교의 핵심을 결정해서는 안 됩니다.

- 실제 Whisper/faster-whisper backend stub 또는 옵션 구현
- streaming API 형태
- 배치 transcription endpoint
- queue 또는 worker 추상화
- 간단한 로드 테스트 스크립트
- OpenAPI 예시
- Docker Compose
- CI workflow
- 언어별 텍스트 정규화
- pluggable storage layer

## v1에서 명시적으로 OUT OF SCOPE

이번 1차 비교 라운드에서는 후보에게 다음을 요구하지 않습니다.

- production GPU autoscaling
- 간단한 예시 이상의 Kubernetes manifest
- 실제 모델 다운로드 또는 모델 학습
- diarization
- speaker identification
- forced alignment 기반 단어 단위 timestamp
- 완전히 동작하는 real-time websocket streaming
- 인증/인가
- 과금 및 quota
- 멀티 테넌트 격리
- 장기 transcript 데이터베이스
- 풀세트 observability stack 배포
- 대용량 오디오 데이터셋 번들링
- 사람 라벨링 UI

## evaluator 범위와 후보 범위의 구분

이 베이크오프 킷 자체는 **evaluator + 실험 하네스**입니다. ASR 서비스를 구현할 필요가 없습니다.

평가 대상은 `outputs/<framework>/` 의 4개 후보입니다. 이 후보들이 위의 v1 구현 범위를 만족해야 합니다.

```text
this kit
  -> prompts, docs, commands, agents, evaluator scripts 보관
  -> 후보 repository 채점
  -> 리포트 생성

candidate repositories
  -> ASR 서비스 구현
  -> CER 평가 구현
  -> 테스트와 실행 가이드 제공
```

## 합격선 (Acceptance threshold)

다음을 모두 보여야 후보는 최소 합격선을 만족합니다.

1. 로컬 `/healthz` endpoint 또는 동등한 health check
2. mock backend를 사용하는 로컬 `/transcribe` 경로
3. 샘플 reference/hypothesis 데이터로 동작하는 CER evaluator
4. 문서화된 테스트 명령
5. 문서화된 로컬 실행 명령
6. 문서화된 구현 범위와 한계

높은 점수를 받으려면 위에 더해 깔끔한 모듈 경계, 운영 준비도, 실제 ASR backend 교체 경로까지 함께 보여야 합니다.
