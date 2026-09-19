"""
Worked example: generate every chart PNG for the "이력서 100개 종합 분석
보고서" deck using chart_lib. This is the actual data/charts from that
session, kept as a pattern to copy from for the next report.

Run from the skill's scripts/ directory on the PYTHONPATH:
    PYTHONPATH=../scripts python3 gen_charts.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from chart_lib import Palette, hbar_chart, stat_bar_chart  # noqa: E402

OUT = Path(__file__).resolve().parent / "charts"
OUT.mkdir(exist_ok=True)

PAL = Palette(primary="#00806F", highlight="#ED7D31", text="#06231F", muted="#6E6E6E")

hbar_chart(str(OUT / "gender.png"), ["남성", "여성"], [67, 33], palette=PAL, pct_of=100)

hbar_chart(
    str(OUT / "age.png"),
    ["20대 후반 (25~29세)", "30대 초반 (30~34세)", "30대 후반 (35~39세)", "20대 초반 (~24세)"],
    [42, 35, 22, 1], palette=PAL, pct_of=100,
)

hbar_chart(
    str(OUT / "major.png"),
    ["경영학과", "경영학부", "경제학", "산업공학", "기타"],
    [69, 15, 8, 6, 2], palette=PAL, pct_of=100,
)

hbar_chart(
    str(OUT / "university.png"),
    ["고려대학교", "건국대학교", "아주대학교", "시립대학교", "이화여자대학교",
     "인하대학교", "성균관대학교", "한양대학교", "숭실대학교", "연세대학교", "서울대학교"],
    [10, 9, 8, 7, 7, 7, 6, 6, 5, 5, 5], palette=PAL, pct_of=100,
)

hbar_chart(
    str(OUT / "gpa.png"),
    ["4.3 이상 (최우수)", "4.0 ~ 4.29", "3.7 ~ 3.99", "3.3 ~ 3.69", "3.3 미만"],
    [17, 22, 28, 28, 5], palette=PAL, pct_of=100,
)

hbar_chart(
    str(OUT / "experience.png"),
    ["신입 (0년)", "1~2년", "3~5년", "6~8년", "9~12년"],
    [1, 10, 43, 34, 12], palette=PAL, pct_of=100,
)

hbar_chart(str(OUT / "position.png"), ["과장", "대리", "차장"], [45, 39, 16], palette=PAL, pct_of=100)

hbar_chart(
    str(OUT / "companies.png"),
    ["3개 회사 이상", "2개 회사", "1개 회사"],
    [38, 33, 29], palette=PAL, pct_of=100,
)

hbar_chart(
    str(OUT / "industry.png"),
    ["금융", "게임", "유통", "핀테크", "IT플랫폼", "통신", "에너지", "보험",
     "반도체", "환경가전", "이커머스", "IT서비스", "건설", "식품", "화장품"],
    [17, 8, 8, 7, 6, 6, 6, 6, 5, 5, 4, 3, 3, 3, 3], palette=PAL, pct_of=100,
)

hbar_chart(
    str(OUT / "skills.png"),
    ["SQL", "공급망관리", "원가관리", "투자분석", "예산관리", "영어(비즈니스)",
     "프로젝트관리", "교육훈련", "회계", "Python", "SAP", "인사평가", "데이터분석",
     "중어(비즈니스)", "CRM 운영", "Tableau", "마케팅기획", "일어(비즈니스)", "Excel", "PowerPoint"],
    [31, 30, 29, 28, 27, 26, 26, 25, 24, 24, 23, 22, 22, 22, 22, 22, 22, 22, 21, 21],
    palette=PAL, pct_of=100,
)

hbar_chart(
    str(OUT / "skill_category.png"),
    ["경영/기획 역량", "IT/데이터 스킬", "외국어", "인사 관련"],
    [95, 89, 58, 41], palette=PAL, pct_of=100,
)

hbar_chart(
    str(OUT / "certificates.png"),
    ["없음", "정보처리기사", "CFA(공인재무분석사)", "ERP정보관리사", "증권투자권유대행인",
     "PMP(프로젝트관리전문가)", "경영지도사", "ADsP(데이터분석준전문가)", "재경관리사", "공인회계사(CPA)"],
    [47, 8, 8, 8, 7, 6, 5, 4, 4, 3], palette=PAL, pct_of=100,
)

stat_bar_chart(
    str(OUT / "key_metrics.png"),
    ["경영학 계열\n전공", "과장·대리급\n(중간관리자)", "3개 이상 회사\n이직 경험", "학점 4.0 이상", "자격증\n없음"],
    [84, 84, 38, 39, 47],
    value_labels=["84%", "84%", "38%", "39%", "47%"],
    palette=PAL,
)

print(f"wrote {len(list(OUT.glob('*.png')))} charts to {OUT}")
