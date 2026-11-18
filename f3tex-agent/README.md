# f3tex-agent — F3TEX 오퍼 시트 검토 에이전트 (최종 프로젝트)

실습 my-agent(제안서 검토)의 구조를 섬유 수출 무역의 **오퍼 시트 발송 전 검토**로 옮긴 하네스입니다.
`data/` 는 모두 가공 자료입니다(가상 바이어·가상 수치).

| 부품 | 위치 | 하는 일 |
|---|---|---|
| 원칙·판단 기준 | `CLAUDE.md` | 페르소나, 근거 문서 4종, 판정 정의, 출력 형식(태그 7종) |
| 스킬 | `.claude/skills/offer-review/SKILL.md` | 단가 → 스펙 → 바이어 조건 → 거래조건 → 문구·미결 → 지시문 → 검증 순서 |
| 계산 도구 | `scripts/margin.py` | 원가·마진·최저 단가 재계산 (기준환율 1,380, 마진 12%) |
| 검증자 | `.claude/agents/validator.md` | 검토 결과의 숫자·인용을 원본에서 독립 재확인 |
| 훅 | `.claude/hooks/guard.py` | `data/` 쓰기 차단 — 파일 도구·리다이렉션·`sed -i`·`mv/cp/rm`·`python -c` 쓰기 포함, 읽기는 통과. 판정 줄 없는 결과 차단 |
| 훅 테스트 | `scripts/test_guard.py` | 읽기 9건 통과·쓰기 15건 차단 등 31개 회귀 케이스 |
| 권한 | `.claude/settings.json` | `Edit/Write(data/**)`, rm·curl·wget·mail·scp·nc 거부 |
| 평가 | `evals/cases.md`, `scripts/run_evals.sh`, `scripts/score_evals.py`, `/eval` | 8개 케이스를 새 세션으로 실행·문자열 채점 |

## 실행

```bash
# 1) 단가 재계산만 (오퍼 단가를 넣으면 마진율·판정까지)
python3 scripts/margin.py data/04-costing.csv "FT-2801=2.95,SJ-1602=2.40,RB-2203=2.10"

# 2) 훅이 제대로 막는지 (31/31 이어야 함)
python3 scripts/test_guard.py

# 3) 평가 8케이스 — 케이스마다 새 claude -p 세션, Sonnet (수 분 소요, API 사용량 발생)
bash scripts/run_evals.sh . evals/results/run.md
```

검토 자체는 Claude Code 세션에서 한 줄로 시킵니다: `data/01-offer-sheet.md 를 검토해서 out/offer-review.md 에 저장해 주십시오.`

## 평가 기록

| 실행 | 대상 | 통과 |
|---|---|---|
| `run-before.md` | 하네스 없음 (CLAUDE.md·스킬·훅 없이) | 2 / 8 |
| `run-after-1.md` | 하네스 1차 | 8 / 8 |
| `run-after-2.md` | 하네스 2차 | 8 / 8 |

## 알려진 한계
- 채점은 문자열 포함 여부만 봅니다. 예: O-03의 `60` 은 다른 숫자(예: 2026, 160)에도 걸릴 수 있어 느슨합니다.
- 훅의 셸 검사는 정적 패턴 검사입니다. 변수 치환(`f=data/x; echo > $f`)이나 스크립트 파일을 거친 쓰기는 잡지 못합니다. 최종 방어선은 `run_evals.sh` 의 `data/` 해시 비교입니다.

시연 순서는 `DEMO.md`.

훅은 `python3` 로 실행됩니다. macOS에서 처음 실행할 때 개발자 도구 설치 창이 뜨면 설치해 두십시오.
