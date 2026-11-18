#!/usr/bin/env python3
"""PreToolUse 훅 — 부탁이 아니라 통제.

1) data/ 아래 파일을 쓰거나 고치려 하면 차단합니다.
2) out/offer-review*.md 를 쓸 때 첫머리에 '판정:' 줄이 없으면 차단하고 다시 쓰게 합니다.
종료 코드 2 = 차단 (stderr 메시지가 모델에게 전달됩니다).
"""
import json
import os
import sys

data = json.load(sys.stdin)
tool = data.get("tool_name", "")
inp = data.get("tool_input", {}) or {}
path = inp.get("file_path") or inp.get("notebook_path") or ""
root = os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd())
rel = os.path.relpath(os.path.abspath(path), root) if path else ""

if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit") and rel.startswith("data" + os.sep):
    print(f"[차단] {rel} 은 원본입니다 (SR-02 제9조 2항). 수정안은 out/ 에 검토 결과로만 쓰십시오.", file=sys.stderr)
    sys.exit(2)

if tool == "Bash":
    cmd = inp.get("command", "")
    writes = (" -i", ">", "tee ", "mv ", "cp ", "rm ", "truncate", "dd ")
    if "data/" in cmd and any(w in cmd for w in writes):
        print("[차단] 셸 명령으로 data/ 원본을 바꾸려 했습니다. 원본은 읽기 전용입니다 (SR-02 제9조 2항).", file=sys.stderr)
        sys.exit(2)

if tool == "Write" and rel.startswith("out" + os.sep) and os.path.basename(rel).startswith("offer-review"):
    head = "\n".join((inp.get("content") or "").splitlines()[:8])
    if "판정:" not in head and "판정**:" not in head and "판정** —" not in head:
        print("[차단] 검토 결과 첫머리에 '판정: 발송 가능 / 수정 후 재검토 / 발송 불가' 줄이 없습니다. 형식대로 다시 쓰십시오.", file=sys.stderr)
        sys.exit(2)

sys.exit(0)
