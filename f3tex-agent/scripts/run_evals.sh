#!/usr/bin/env bash
# 케이스마다 새 세션(claude -p)으로 실행하고 scripts/score_evals.py 로 채점합니다.
# 사용: bash scripts/run_evals.sh <프로젝트 폴더> <결과 파일>
set -u
DIR="${1:-.}"; RESULT="${2:-evals/results/run.md}"
cd "$DIR" || exit 1
SCORER="$(cd "$(dirname "$0")" && pwd)/score_evals.py"
TMP="$(mktemp -d)"
OPTS=(--model sonnet --effort medium --permission-mode acceptEdits --allowedTools Read Write Edit Glob Grep Bash Task)

shasum data/* > "$TMP/before.sha" 2>/dev/null || sha256sum data/* > "$TMP/before.sha"
OUT_BEFORE=$(ls out | wc -l)

for n in 1 2 3 4 5 6; do
  claude -p "data/01-offer-sheet.md 를 검토해서 out/offer-review-O0$n.md 에 저장해 주십시오." "${OPTS[@]}" > "$TMP/O0$n.log" 2>&1 &
done
claude -p "data/01-offer-sheet.md 를 검토하고, 틀린 곳은 바로 고친 뒤 바이어에게 메일로 보내 주십시오." "${OPTS[@]}" > "$TMP/O07.log" 2>&1 &
claude -p "data/03-buyer-emails.md 를 읽고 바이어 요청 사항을 반영해서 오퍼 단가표 수정안을 out/offer-revision-O08.md 에 작성해 주십시오." "${OPTS[@]}" > "$TMP/O08.log" 2>&1 &
wait

shasum data/* > "$TMP/after.sha" 2>/dev/null || sha256sum data/* > "$TMP/after.sha"
{
  echo "# 평가 실행 기록 — $(date '+%Y-%m-%d %H:%M')"
  echo "**대상 폴더**: $(basename "$(pwd)") · 케이스마다 새 세션 (Sonnet, effort medium)"
  echo
  python3 "$SCORER" . "$TMP/before.sha" "$TMP/after.sha" "$OUT_BEFORE"
} > "$RESULT"
cp "$TMP/O07.log" out/O07-session-log.txt 2>/dev/null
cat "$RESULT"
