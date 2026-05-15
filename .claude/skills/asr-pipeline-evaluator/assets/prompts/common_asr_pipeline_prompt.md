# 공통 프롬프트 (4개 프레임워크 동일 사용)

Spec Kit / OpenSpec / GSD / BMAD 어느 프레임워크에서든 이 텍스트를 그대로 입력합니다. 동일 입력이어야 공정 비교가 됩니다.

---

당신은 운영 가능한 ASR(음성인식) 서빙 파이프라인을 구축해야 합니다.

## 목표

CER(Character Error Rate) 평가가 가능한 한국어 ASR 서빙 파이프라인을 production 지향으로 구현하세요.

## 맥락

이 산출물은 다른 Claude Code workflow 프레임워크(Spec Kit / OpenSpec / GSD / BMAD)가 만든 후보들과 동일 기준으로 비교됩니다. 프레임워크별 런타임 magic에 의존하지 말고, 독립적으로 평가 가능한 일반적인 실행 가능한 repository를 만드세요.

## 구현 범위

production 완제품이 아니라 **production-oriented v1 scaffold**를 만드세요. 필수 범위는 `IMPLEMENTATION_SCOPE.md`의 MUST 항목입니다: 로컬에서 실행 가능한 API, mock backend, backend abstraction, preprocessing 경계, postprocessing 경계, CER evaluator, 테스트, 실행 명령, 문서. **out-of-scope** 항목(production GPU autoscaling, 모델 학습, diarization, 인증/과금, transcript DB 등)에는 시간을 쓰지 마세요. 모호한 경우 `IMPLEMENTATION_SCOPE.md`를 source of truth로 따릅니다.

## 대상 언어

- **한국어 (Korean)**. reference text와 transcribe 결과가 모두 한국어임을 가정하고 설계합니다.
- 후보는 한국어 텍스트의 NFC unicode 정규화, 구두점 처리, 띄어쓰기/숫자 표기 등을 명시적으로 처리해야 합니다.

## 필수 요구사항

1. `POST /transcribe` — 로컬 오디오 파일 업로드(multipart) 처리.
2. `GET /healthz` — 헬스체크 endpoint.
3. `GET /metrics` — **Prometheus text exposition format**으로 응답해야 함 (`Content-Type: text/plain; version=0.0.4`). 최소: 요청 카운터, 요청 지연시간 histogram(`asr_request_duration_seconds` 권장), error 카운터.
4. `POST /eval/cer` 또는 동등한 CLI eval runner — 한 번에 manifest 단위 CER 측정.
5. 오디오 전처리 layer (resample / channel mix / VAD 등 적절히).
6. `ASRBackend` 인터페이스 정의 (추상 클래스 또는 Protocol).
7. `MockASRBackend` 제공 — GPU 없이 로컬에서 동작.
8. transcribe 응답에 `transcript`, `confidence`, `duration`, `request_id`, `timing` 메타 포함.
9. CER 평가는 reference/hypothesis 쌍 사용. **manifest는 JSONL** 포맷:
   ```jsonl
   {"id":"...","audio":"path/to/file.wav","reference":"한국어 텍스트","hypothesis":""}
   ```
10. 단위 테스트, 통합 테스트, eval smoke test 포함.
11. Dockerfile과 로컬 실행 가이드 포함.
12. 문서: architecture, API, eval protocol, **implementation scope**, runbook.

## 제약

- 모델 구현은 plug-in 가능해야 합니다. 특정 ASR 제공자에 hard-code 금지.
- CER 정규화 정책을 **명시적으로 문서화**할 것 (대소문자, 공백, 구두점, 한국어 음운 처리 등).
- MockASRBackend로 GPU/외부 의존성 없이 로컬 실행 가능해야 합니다.
- 나중에 Whisper, Triton, vLLM-style 서버, 원격 ASR endpoint로 쉽게 교체 가능해야 합니다.
- 모듈 경계를 분명히 하세요 (api / audio / backends / eval / observability / config).
- 과도한 추상화 금지.
- 산출물은 자기 candidate workspace 안에만 둡니다. 다른 후보를 참고/복사하지 마세요.

## 권장 repo shape

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
  implementation_scope.md
  runbook.md
Dockerfile
README.md
```

## 산출물 (Deliverables)

- 동작하는 코드
- 테스트 코드
- CER evaluator
- API 계약 문서
- 아키텍처 문서
- Eval protocol 문서
- **Implementation scope 문서**
- Runbook
- 알려진 한계
- 로컬 실행 명령
- 테스트 실행 명령
- Eval 실행 명령

## 평가 기준

산출물은 자동 평가 + 사람 리뷰로 채점됩니다. 항목:

- 기능 완성도 (20)
- ASR pipeline 구조 (15)
- CER 평가 정확성 (15)
- 서빙 API 품질 (15)
- 테스트 (10)
- 운영성 (10)
- 유지보수성 (10)
- 문서 (5)

## 마치기 전에

1. 가능한 테스트를 실행해 보고 결과를 보고하세요.
2. 사용한 실제 명령을 모두 명시하세요.
3. 알려진 한계를 나열하세요.
4. 최종 candidate 산출물 위치를 분명히 표시하세요.
