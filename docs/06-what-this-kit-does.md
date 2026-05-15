# 06. 이 킷이 하는 일

이 킷은 모호한 비교 질문을 **통제된 Claude Code 실험**으로 바꿔주는 도구입니다.

비교 질문:

> ASR 서빙 파이프라인과 CER 측정을 만들 때, Spec Kit / OpenSpec / GSD / BMAD 중 어느 프레임워크가 가장 좋은 결과를 만드는가?

## 무엇을 비교하는가

4개 프레임워크는 **자기 README의 주장**으로 평가하지 않습니다. 각 프레임워크가 **실제로 생성한 산출물**로 평가합니다.

각 프레임워크는 동일한 task를 받습니다.

```text
Build a production-oriented ASR serving pipeline with CER evaluation.
```

각 프레임워크는 다음을 포함하는 후보 repository를 만들어야 합니다.

- ASR API 서비스
- audio preprocessing
- ASR backend abstraction
- 로컬 실행을 위한 mock backend
- CER evaluation
- 테스트
- Docker/로컬 실행 가이드
- 아키텍처 문서
- runbook

## 이 킷이 제공하는 것

이 킷은 실험을 둘러싸는 **control layer**입니다.

1. 공통 task 프롬프트
2. 공통 baseline 요구사항
3. 공통 API 계약
4. 공통 CER protocol
5. 베이크오프 실행용 Claude Code 슬래시 커맨드
6. Claude Code 리뷰어 에이전트
7. 로컬 evaluator 스크립트
8. 채점 rubric
9. 리포트 생성

## 이 킷이 제공하지 않는 것

이 킷은 Spec Kit / OpenSpec / GSD / BMAD 자체를 포함하지 **않습니다**.

그 4개 프레임워크는 각각 다음 위치에 별도 설치하세요.

```text
workspaces/spec-kit/
workspaces/openspec/
workspaces/gsd/
workspaces/bmad/
```

분리는 의도적입니다. 같은 디렉터리에 모두 설치하면 컨텍스트 파일, 커맨드, 생성 산출물이 서로 오염시킵니다.

## agents/openai.yaml 을 제거한 이유

`agents/openai.yaml`은 ChatGPT Skill 업로드 패키지에 쓰는 메타데이터였습니다.

이 킷은 이제 **Claude Code 워크스페이스 패키지**로 방향을 잡았습니다. Claude Code 친화 자산은 다음에 위치합니다.

```text
CLAUDE.md
.claude/commands/
.claude/agents/
.claude/skills/
```

## evaluator 동작 방식

evaluator는 freeze된 후보 산출물 폴더들을 대상으로 동작합니다.

```text
outputs/spec-kit/
outputs/openspec/
outputs/gsd/
outputs/bmad/
```

검사 항목:

- 기대 파일·모듈 존재 여부
- ASR 서빙 구조
- CER 구현 시그널
- API 서빙 품질
- 테스트
- Docker/로컬 실행 준비도
- 운영 지표 및 운영 문서
- 유지보수성

리포트 저장 위치:

```text
reports/
```

evaluator는 의도적으로 **보수적**입니다. 1차 점수일 뿐, 사람 리뷰를 대체하지 않습니다.

## 결과 해석 (3계층)

최종 결과는 3개 층으로 해석하세요.

1. **자동 점수** — 빠르고 일관됨. 스크리닝 용도.
2. **사람 리뷰** — 아키텍처 판단과 구현 품질 판단에 필수.
3. **런타임 벤치마크** — production 성능을 주장하려면 별도로 수행 필요.
