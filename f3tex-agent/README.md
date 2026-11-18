# f3tex-agent — F3TEX 오퍼 시트 검토 에이전트 (최종 프로젝트)

실습 my-agent(제안서 검토)의 구조를 섬유 수출 무역의 **오퍼 시트 발송 전 검토**로 옮긴 하네스입니다.
`data/` 는 모두 가공 자료입니다(가상 바이어·가상 수치).

| 부품 | 위치 | 하는 일 |
|---|---|---|
| 원칙·판단 기준 | `CLAUDE.md` | 페르소나, 근거 문서 4종, 판정 정의, 출력 형식(태그 7종) |
| 스킬 | `.claude/skills/offer-review/SKILL.md` | 단가 → 스펙 → 바이어 조건 → 거래조건 → 문구·미결 → 지시문 → 검증 순서 |
| 계산 도구 | `scripts/margin.py` | 원가·마진·최저 단가 재계산 (기준환율 1,380, 마진 12%) |
| 검증자 | `.claude/agents/validator.md` | 검토 결과의 숫자·인용을 원본에서 독립 재확인 |
| 훅 | `.claude/hooks/guard.py` | `data/` 쓰기(셸 포함) 차단, 판정 줄 없는 결과 차단 |
| 권한 | `.claude/settings.json` | `Edit(data/**)`, rm·curl·mail 거부 |
| 평가 | `evals/cases.md`, `scripts/run_evals.sh`, `scripts/score_evals.py`, `/eval` | 8개 케이스를 새 세션으로 실행·문자열 채점 |

시연 순서는 `DEMO.md`.

훅은 `python3` 로 실행됩니다. macOS에서 처음 실행할 때 개발자 도구 설치 창이 뜨면 설치해 두십시오.
