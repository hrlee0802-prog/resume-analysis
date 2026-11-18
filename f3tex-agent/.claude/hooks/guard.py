#!/usr/bin/env python3
"""PreToolUse 훅 — 부탁이 아니라 통제.

1) data/ 아래 파일을 쓰거나 고치려 하면 차단합니다 (파일 도구 + 셸 명령).
2) out/offer-review*.md 를 쓸 때 첫머리에 '판정:' 줄이 없으면 차단하고 다시 쓰게 합니다.
종료 코드 2 = 차단 (stderr 메시지가 모델에게 전달됩니다).

셸 검사는 '읽기는 통과, 쓰기는 차단' 을 목표로 합니다.
  - 통과 예: cat data/x 2>&1 · grep … data/ · python3 scripts/margin.py data/04-costing.csv · cp data/x out/
  - 차단 예: echo > data/x · sed -i'' … data/x · mv data/x … · python3 -c "open('data/x','w')"
"""
import json
import os
import re
import shlex
import sys

# 'data' 경로 토큰: data/…, ./data/…, "data/…", 단독 data (cd data 등)
DATA_PATH = re.compile(r"""(?:^|[\s"'=(:,])(?:\./)?data(?:/|$|[\s"');,])""")
# data/ 를 가리키는 출력 리다이렉션: > data/x, >> ./data/x, >| "data/x", 1> data/x
REDIRECT_TO_DATA = re.compile(r"""\d?>{1,2}\|?\s*["']?(?:\./)?data(?:/|\b)""")
# 대상(마지막 인자)이 무엇이든 data/ 를 건드리면 쓰기인 명령
ALWAYS_WRITE = {"rm", "rmdir", "unlink", "shred", "truncate", "touch", "chmod", "chown",
                "mv", "dd", "tee", "patch"}
# 마지막 인자(목적지)가 data/ 일 때만 쓰기인 명령
DEST_WRITE = {"cp", "install", "rsync", "ln", "scp"}
# 제자리 수정 플래그를 가진 명령
INPLACE = {"sed", "perl", "gsed", "ruby"}
INTERPRETERS = {"python", "python3", "perl", "ruby", "node", "bash", "sh", "zsh"}
WRITE_MARKERS = re.compile(r"""['"](?:w|a|wb|ab|w\+|a\+|r\+)['"]|\.write|write_text|write_bytes|"""
                           r"""unlink|remove|rename|replace\(|rmtree|truncate|writeFile|appendFile""")


def is_data(tok: str) -> bool:
    return bool(DATA_PATH.search(" " + tok + " "))


def segments(cmd: str):
    """; && || | 줄바꿈으로 나눈 단순 명령들을 토큰 목록으로 돌려줍니다."""
    lex = shlex.shlex(cmd.replace("\n", " ; "), posix=True, punctuation_chars=";&|<>()")
    lex.whitespace_split = True
    try:
        all_toks = list(lex)
    except ValueError:  # 따옴표가 닫히지 않음 → 단순 분리
        all_toks = cmd.split()
    cur = []
    for t in all_toks + [";"]:
        if t and set(t) <= set(";&|()"):  # 연산자 토큰에서 명령을 끊음
            # sudo, env, VAR=… 같은 앞머리를 건너뜀
            while cur and (cur[0] in ("sudo", "env", "command", "exec", "nohup") or re.match(r"^\w+=", cur[0])):
                cur = cur[1:]
            if cur:
                yield cur
            cur = []
        else:
            cur.append(t)


def bash_writes_data(cmd: str) -> bool:
    if not DATA_PATH.search(" " + cmd + " "):
        return False
    if REDIRECT_TO_DATA.search(cmd):
        return True
    cwd_is_data = False
    for toks in segments(cmd):
        prog = os.path.basename(toks[0])
        args = toks[1:]
        if prog == "cd":
            cwd_is_data = bool(args) and is_data(args[0])
            continue
        touches = cwd_is_data or any(is_data(a) for a in args)
        if not touches:
            continue
        if prog in ALWAYS_WRITE:
            return True
        if prog in DEST_WRITE:
            paths = [a for a in args if not a.startswith("-")]
            if cwd_is_data or (paths and is_data(paths[-1])):
                return True
        if prog in INPLACE and any(a == "--in-place" or re.match(r"^-[a-zA-Z]*i", a) for a in args):
            return True
        if prog == "git" and args and args[0] in ("checkout", "restore", "rm", "mv", "stash", "reset", "clean"):
            return True
        if prog in INTERPRETERS and WRITE_MARKERS.search(" ".join(args)):
            return True
    return False


def main() -> None:
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    inp = data.get("tool_input", {}) or {}
    path = inp.get("file_path") or inp.get("notebook_path") or ""
    root = os.path.realpath(os.environ.get("CLAUDE_PROJECT_DIR", os.getcwd()))
    rel = os.path.relpath(os.path.realpath(path), root) if path else ""

    if tool in ("Write", "Edit", "MultiEdit", "NotebookEdit") and (rel == "data" or rel.startswith("data" + os.sep)):
        print(f"[차단] {rel} 은 원본입니다 (SR-02 제9조 2항). 수정안은 out/ 에 검토 결과로만 쓰십시오.", file=sys.stderr)
        sys.exit(2)

    if tool == "Bash" and bash_writes_data(inp.get("command", "")):
        print("[차단] 셸 명령으로 data/ 원본을 바꾸려 했습니다. 원본은 읽기 전용입니다 (SR-02 제9조 2항).", file=sys.stderr)
        sys.exit(2)

    if tool == "Write" and rel.startswith("out" + os.sep) and os.path.basename(rel).startswith("offer-review"):
        head = "\n".join((inp.get("content") or "").splitlines()[:8])
        if not re.search(r"판정\**\s*[:：—-]", head):
            print("[차단] 검토 결과 첫머리에 '판정: 발송 가능 / 수정 후 재검토 / 발송 불가' 줄이 없습니다. 형식대로 다시 쓰십시오.", file=sys.stderr)
            sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
