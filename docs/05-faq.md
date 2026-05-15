# 05. FAQ

## Q1. docs 폴더가 꼭 필요한가?

네. 특히 이번 패키지는 단순 라이브러리가 아니라 **실험 운영 도구**입니다. 따라서 docs에는 다음이 있어야 합니다.

- 이 패키지의 목적
- 어떤 산출물을 비교하는지
- Claude Code에서 어떻게 실행하는지
- 4개 프레임워크를 어떻게 격리하는지
- 평가 결과를 어떻게 해석하는지

기존 버전은 evaluator code와 baseline은 있었지만, "사용자가 실제 실험을 어떻게 운영해야 하는가"에 대한 문서가 부족했습니다.

## Q2. Spec Kit, OpenSpec, GSD, BMAD를 모두 설치해야 하나?

비교 실험을 하려면 네, 설치하거나 사용할 수 있는 상태여야 합니다.

다만 같은 repo에 모두 설치하지 말고, 프레임워크별 workspace를 따로 둡니다.

```text
workspaces/spec-kit
workspaces/openspec
workspaces/gsd
workspaces/bmad
```

각 workspace에서 해당 프레임워크만 사용하고, 결과물을 `outputs/<name>`으로 복사해 평가합니다.

## Q3. 이 evaluator skill도 Claude Code에 설치하는가?

두 가지 방식이 가능합니다.

1. ChatGPT Skill로 업로드해서 ChatGPT 안에서 평가 지침과 스크립트를 사용한다.
2. Claude Code 프로젝트 안에 압축 해제해서 `scripts/run_all.py`를 직접 실행한다.

Claude Code bakeoff에서는 2번 방식이 더 직접적입니다.

## Q4. 4개 프레임워크가 만든 결과물을 바로 비교해도 되나?

가능하지만, 다음 조건이 맞아야 공정합니다.

- 같은 baseline prompt
- 같은 skeleton
- 같은 모델/권한/시간 제한
- 같은 dependency 제약
- 같은 평가 manifest
- 같은 rubric

## Q5. 자동 점수만 믿어도 되나?

아니요. 자동 점수는 1차 필터입니다.

ASR serving pipeline에서는 다음 판단이 중요해서 사람 리뷰가 필요합니다.

- backend abstraction이 실제로 좋은지
- CER normalization이 언어 특성에 맞는지
- 운영 장애에 대한 설계가 있는지
- latency/throughput 설계가 현실적인지

## Q6. 왜 CER sample fixture가 text만 있나?

이 패키지의 기본 fixture는 evaluator 자체의 CER 계산을 검증하기 위한 최소 fixture입니다. 실제 ASR 품질 평가를 하려면 wav/flac 파일과 reference transcript를 추가해야 합니다.

권장 확장:

```text
test_fixtures/
  audio/
    sample_001.wav
    sample_002.wav
  references/
    sample_001.txt
    sample_002.txt
  manifest.jsonl
```

## Q7. Claude Code command template은 어디에 있나?

`.claude/commands/`에 이미 설치되어 있습니다.

- `asr-bakeoff-setup.md`
- `asr-generate-candidate.md`
- `asr-evaluate.md`
- `asr-human-review.md`
- `asr-summarize-results.md`

Claude Code 세션에서 `/asr-bakeoff-setup`, `/asr-generate-candidate`, `/asr-evaluate`, `/asr-human-review`, `/asr-summarize-results`로 바로 호출할 수 있습니다.
