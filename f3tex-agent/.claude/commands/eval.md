# 평가 실행

케이스마다 새 세션으로 실행하고 결과를 채점합니다. 이 세션에서 직접 검토를 쓰지 않습니다(정답을 아는 맥락이 섞이지 않게).

1. 아래를 실행합니다. 결과 파일: $ARGUMENTS (없으면 `evals/results/run.md`)
   `bash scripts/run_evals.sh . <결과 파일>`
2. 출력된 통과 수와 FAIL 목록을 그대로 요약합니다.
3. 개선 제안은 한 건만 합니다.

## 금지
- 판정 기준(`evals/cases.md`, `scripts/score_evals.py`)을 고치지 않습니다.
- `data/` 를 고치지 않습니다.
