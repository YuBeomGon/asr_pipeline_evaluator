# 01. Claude Code에서 Skill, Tool, Plugin, Command 이해하기

이 문서는 이번 실험에서 자주 나오는 용어를 Claude Code 관점으로 정리합니다.

## 1. Skill

Skill은 특정 작업을 반복적으로 잘 수행하기 위한 **설명서 + 코드 + 참고자료 묶음**입니다.

이 패키지의 skill은 다음을 알려줍니다.

- ASR pipeline 비교를 언제 해야 하는지
- 어떤 rubric으로 점수화할지
- 어떤 evaluator script를 실행할지
- 결과를 어떻게 해석할지

즉, skill은 "모델에게 주는 업무 매뉴얼"에 가깝습니다.

## 2. Tool

Tool은 실제로 무언가를 실행하는 기능입니다.

예:

- shell command 실행
- 파일 읽기/쓰기
- Python script 실행
- 웹 검색
- connector 검색

이번 패키지에서 핵심 tool은 `scripts/run_all.py`입니다. 이 파일은 여러 후보 repo를 실제로 검사하고 report를 만듭니다.

## 3. Plugin / Framework

이번 대화에서 말한 Spec Kit, OpenSpec, GSD, BMAD는 여기서 **비교 대상 프레임워크**입니다.

역할은 evaluator와 다릅니다.

```text
Spec Kit / OpenSpec / GSD / BMAD
  -> ASR pipeline 후보 산출물을 만든다

ASR Pipeline Evaluator
  -> 그 후보 산출물들을 같은 기준으로 비교한다
```

따라서 이 evaluator skill은 4개 프레임워크를 대체하지 않습니다. 4개 프레임워크가 만든 결과물을 채점합니다.

## 4. Claude Code command

Claude Code에서는 slash command나 project instruction을 통해 반복 작업을 쉽게 호출할 수 있습니다. 이 킷은 다음 슬래시 커맨드를 `.claude/commands/`에 미리 넣어 두었습니다.

- `/asr-bakeoff-setup`
- `/asr-generate-candidate`
- `/asr-evaluate`
- `/asr-human-review`
- `/asr-summarize-results`

예상 사용 흐름:

```text
1. 루트 CLAUDE.md가 자동 적용되어 프로젝트 지침이 로드된다.
2. .claude/commands/ 의 슬래시 커맨드로 단계별 작업을 호출한다.
3. 같은 baseline prompt로 각 프레임워크를 실행한다.
4. /asr-evaluate 로 결과를 비교한다.
```

## 5. 이번 실험의 역할 분리

```text
사용자
  -> 비교하고 싶은 목적과 제약을 정한다

Claude Code
  -> 각 프레임워크를 사용해 후보 구현을 생성한다

Spec Kit / OpenSpec / GSD / BMAD
  -> 서로 다른 방식으로 ASR pipeline 산출물을 만든다

ASR Pipeline Evaluator
  -> 결과물을 같은 기준으로 검사하고 점수화한다

사람 리뷰어
  -> 자동 점수로 판단하기 어려운 아키텍처 판단을 최종 검토한다
```

## 6. 왜 evaluator가 별도로 필요한가

4개 프레임워크는 철학이 다릅니다.

- Spec Kit은 명세와 phase gate에 강합니다.
- OpenSpec은 변경 단위 spec에 강합니다.
- GSD는 phase 실행과 검증 루프에 강합니다.
- BMAD는 역할 기반 planning과 architecture review에 강합니다.

그냥 산출물만 보면 문서가 많은 쪽이 좋아 보일 수 있습니다. 하지만 ASR serving pipeline에서는 실제로 다음이 더 중요합니다.

- 로컬에서 실행 가능한가?
- CER 계산이 맞는가?
- backend 교체가 쉬운가?
- 테스트가 있는가?
- 운영 지표가 있는가?

그래서 동일 evaluator가 필요합니다.
