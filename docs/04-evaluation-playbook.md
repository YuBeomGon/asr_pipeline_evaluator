# 04. Evaluation Playbook

이 문서는 evaluator 결과를 어떻게 해석할지 설명합니다.

## evaluator가 하는 일

`scripts/run_all.py`는 다음을 수행합니다.

1. 각 후보 repo를 정적 검사합니다.
2. 필수 API/파일/문서/테스트 흔적을 찾습니다.
3. CER reference implementation으로 sample manifest를 계산합니다.
4. 옵션이 켜져 있으면 pytest를 실행합니다.
5. 옵션이 주어지면 `/healthz`, `/metrics` API smoke test를 합니다.
6. leaderboard와 scorecard를 생성합니다.

## 생성되는 report

```text
reports/
  leaderboard.md
  scorecard-spec-kit.md
  scorecard-openspec.md
  scorecard-gsd.md
  scorecard-bmad.md
  failure-analysis.md
  all-scores.json
  reference-cer.json
```

## leaderboard.md

전체 순위를 봅니다. 단, 점수만 보지 말고 notes와 failure summary도 같이 봐야 합니다.

## scorecard-*.md

후보별 상세 결과입니다.

확인할 것:

- 어떤 항목에서 감점됐는가?
- pytest가 실행됐는가, 실패했는가, 아니면 감지되지 않았는가?
- API smoke test가 수행됐는가?
- 문서/테스트/운영 항목이 빠졌는가?

## failure-analysis.md

4개 후보에서 반복적으로 빠진 항목을 확인합니다.

예:

- 모두 CER normalization policy를 애매하게 작성했다.
- 모두 `/metrics`는 만들었지만 실제 latency histogram이 없다.
- 모두 MockASRBackend는 있지만 remote backend 교체 경계가 약하다.

이런 반복 실패는 특정 프레임워크의 문제가 아니라 **공통 prompt가 부족했다는 신호**일 수 있습니다.

## 자동 점수의 한계

자동 점수는 heuristic입니다. 다음은 사람이 꼭 봐야 합니다.

- 코드 구조가 실제로 유지보수 가능한가?
- ASRBackend 추상화가 이름만 있는 것은 아닌가?
- CER 계산이 언어별 normalization 요구에 맞는가?
- queue/backpressure/timeout이 실제 운영에서 의미 있게 설계됐는가?
- Dockerfile이 존재하지만 실제로 실행 가능한가?

## 좋은 결과물의 특징

ASR serving pipeline 기준 좋은 결과물은 다음을 만족합니다.

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
  architecture.md
  api.md
  eval_protocol.md
  runbook.md
```

또한 다음 명령이 명확해야 합니다.

```bash
make test
make run
make eval
make docker-build
```

또는 이에 준하는 실행 경로가 있어야 합니다.

## CER 관련 체크

CER는 다음을 명확히 해야 합니다.

- reference와 hypothesis normalization 순서
- 공백 제거 여부
- 대소문자 처리
- punctuation 처리
- 한국어/영어/숫자 혼합 처리
- per-sample CER와 aggregate CER 계산 방식

## runtime 평가 확장 아이디어

나중에 evaluator를 강화하려면 다음을 추가할 수 있습니다.

- 실제 wav 파일 fixture
- `/transcribe` multipart upload smoke test
- latency percentile 측정
- concurrent request load test
- Docker build/run 자동화
- Whisper mock 또는 tiny model backend fixture
- streaming response contract test
