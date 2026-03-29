"""
이력서 100개 분석 스크립트
대상: 이력서_001.docx ~ 이력서_100.docx
"""

import zipfile
import re
import sys
from collections import Counter

RESUME_DIR = "../이력서"


def extract_docx_text(docx_path):
    try:
        with zipfile.ZipFile(docx_path) as z:
            with z.open("word/document.xml") as f:
                content = f.read().decode("utf-8")
        texts = re.findall(r"<w:t[^>]*>([^<]*)</w:t>", content)
        return " ".join(t for t in texts if t.strip())
    except Exception as e:
        return f"ERROR: {e}"


def parse_resume(text):
    data = {}
    m = re.search(r"성명\s+([^\s]+)\s+성별", text)
    data["name"] = m.group(1) if m else ""

    m = re.search(r"성별\s+(남|여)", text)
    data["gender"] = m.group(1) if m else ""

    m = re.search(r"생년월일\s+(\d{4})\.(\d{2})\.(\d{2})\s+\((\d+)세\)", text)
    if m:
        data["birth_year"] = int(m.group(1))
        data["age"] = int(m.group(4))

    m = re.search(r"총 경력\s+(\d+)년", text)
    data["total_exp"] = int(m.group(1)) if m else 0

    m = re.search(r"학점[:\s]+(\d+\.\d+)/(\d+\.\d+)", text)
    if m:
        data["gpa"] = float(m.group(1))
        data["gpa_max"] = float(m.group(2))
        data["gpa_normalized"] = round(data["gpa"] / data["gpa_max"] * 4.5, 2)

    m = re.search(r"자격증\s+([^\s▪]+?)(?:\s+학력|\s*$)", text)
    data["cert"] = m.group(1).strip() if m else "없음"

    m = re.search(r"경력 사항\s+([^\(]+)\(([^\)]+)\)", text)
    if m:
        data["current_company"] = m.group(1).strip()
        data["industry"] = m.group(2).strip()

    m = re.search(r"\(([^\)]+)\)\s+\|\s+([^\|]+)\|", text)
    if m:
        data["current_position"] = m.group(2).strip()

    m = re.search(r"보유 역량 및 기술\s+(.+?)\s+자기소개", text)
    if m:
        skills = re.split(r"\s*/\s*", m.group(1))
        data["skills"] = [s.strip() for s in skills if s.strip()]
    else:
        data["skills"] = []

    major_pattern = (
        r"(경영학과|경영학부|컴퓨터공학|전자공학|기계공학|화학공학|산업공학"
        r"|통계학|수학과|물리학|심리학|경제학|회계학|무역학|금융학)"
    )
    m = re.search(major_pattern, text)
    data["major"] = m.group(1) if m else "기타"

    companies = re.findall(r"([^\s]+)\s+\([^\)]+\)\s+\|\s+[^\|]+\|", text)
    data["num_companies"] = len(companies)

    return data


def analyze(resumes):
    print(f"총 파싱 완료: {len(resumes)}개\n")

    # 성별
    gender = Counter(r["gender"] for r in resumes)
    print(f"[성별] 남: {gender['남']}명 / 여: {gender['여']}명")

    # 평균 나이
    ages = [r["age"] for r in resumes if "age" in r]
    print(f"[나이] 평균: {sum(ages)/len(ages):.1f}세")

    # 평균 경력
    exps = [r["total_exp"] for r in resumes]
    print(f"[경력] 평균: {sum(exps)/len(exps):.1f}년")

    # 업종 Top 5
    print("\n[업종 Top 5]")
    for ind, cnt in Counter(r.get("industry", "") for r in resumes).most_common(5):
        print(f"  {ind}: {cnt}명")

    # 스킬 Top 10
    all_skills = []
    for r in resumes:
        all_skills.extend(r.get("skills", []))
    print("\n[스킬 Top 10]")
    for skill, cnt in Counter(all_skills).most_common(10):
        print(f"  {skill}: {cnt}명")


if __name__ == "__main__":
    import os

    resumes = []
    for i in range(1, 101):
        path = os.path.join(RESUME_DIR, f"이력서_{i:03d}.docx")
        text = extract_docx_text(path)
        if text.startswith("ERROR"):
            continue
        d = parse_resume(text)
        d["file"] = f"이력서_{i:03d}"
        resumes.append(d)

    analyze(resumes)
