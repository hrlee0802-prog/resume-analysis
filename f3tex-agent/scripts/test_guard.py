"""guard.py 훅 회귀 테스트. 사용: python3 scripts/test_guard.py"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HOOK = os.path.join(ROOT, ".claude", "hooks", "guard.py")


def run(tool, **inp):
    r = subprocess.run([sys.executable, HOOK], input=json.dumps({"tool_name": tool, "tool_input": inp}),
                       capture_output=True, text=True, cwd=ROOT, env={**os.environ, "CLAUDE_PROJECT_DIR": ROOT})
    return r.returncode


BLOCK, ALLOW = 2, 0
bash_cases = [
    # 읽기 — 통과해야 함
    (ALLOW, "cat data/01-offer-sheet.md"),
    (ALLOW, "cat data/01-offer-sheet.md 2>&1 | head"),
    (ALLOW, "grep -n FT-2801 data/*.md > out/grep.txt"),
    (ALLOW, 'python3 scripts/margin.py data/04-costing.csv "FT-2801=2.95,SJ-1602=2.40"'),
    (ALLOW, "cp data/01-offer-sheet.md out/offer-copy.md"),
    (ALLOW, "sha256sum data/*"),
    (ALLOW, "sed -n 1,20p data/02-offer-rules.md"),
    (ALLOW, "ls data && wc -l data/*"),
    (ALLOW, "echo hello > out/x.md"),
    # 쓰기 — 차단해야 함
    (BLOCK, "echo x > data/01-offer-sheet.md"),
    (BLOCK, "echo x >> ./data/01-offer-sheet.md"),
    (BLOCK, "sed -i 's/TBD/2026-12-16/' data/01-offer-sheet.md"),
    (BLOCK, "sed -i'' 's/TBD/2026-12-16/' data/01-offer-sheet.md"),
    (BLOCK, "sed -i.bak 's/TBD/x/' data/01-offer-sheet.md"),
    (BLOCK, "perl -pi -e 's/TBD/x/' data/01-offer-sheet.md"),
    (BLOCK, "mv data/01-offer-sheet.md /tmp/"),
    (BLOCK, "cp out/new.md data/01-offer-sheet.md"),
    (BLOCK, "echo x | tee data/01-offer-sheet.md"),
    (BLOCK, "rm data/01-offer-sheet.md"),
    (BLOCK, "touch data/new.md"),
    (BLOCK, "cd data && sed -i 's/TBD/x/' 01-offer-sheet.md"),
    (BLOCK, """python3 -c "open('data/01-offer-sheet.md','w').write('x')" """),
    (BLOCK, """python3 -c "import pathlib; pathlib.Path('data/01-offer-sheet.md').write_text('x')" """),
    (BLOCK, "git checkout data/01-offer-sheet.md"),
]

fails = 0
for want, cmd in bash_cases:
    got = run("Bash", command=cmd)
    if got != want:
        fails += 1
        print(f"FAIL  want={'BLOCK' if want else 'ALLOW'}  {cmd}")

file_cases = [
    (BLOCK, "Write", dict(file_path=os.path.join(ROOT, "data/01-offer-sheet.md"), content="x")),
    (BLOCK, "Edit", dict(file_path="data/01-offer-sheet.md", old_string="a", new_string="b")),
    (BLOCK, "Edit", dict(file_path=os.path.join(ROOT, "out/../data/01-offer-sheet.md"), old_string="a", new_string="b")),
    (BLOCK, "Write", dict(file_path=os.path.join(ROOT, "out/offer-review.md"), content="# 검토\n표만 있음")),
    (ALLOW, "Write", dict(file_path=os.path.join(ROOT, "out/offer-review.md"), content="판정: 발송 불가\n...")),
    (ALLOW, "Write", dict(file_path=os.path.join(ROOT, "out/offer-review.md"), content="# 검토\n**판정**: 발송 불가")),
    (ALLOW, "Write", dict(file_path=os.path.join(ROOT, "out/notes.md"), content="메모")),
]
for want, tool, inp in file_cases:
    got = run(tool, **inp)
    if got != want:
        fails += 1
        print(f"FAIL  want={'BLOCK' if want else 'ALLOW'}  {tool} {inp.get('file_path')}")

total = len(bash_cases) + len(file_cases)
print(f"guard.py: {total - fails} / {total} 통과")
sys.exit(1 if fails else 0)
