"""
Worked example: fill the 30-slide draft (built by restructure.py from
template.pptx + outline.json) with the actual "이력서 100개 종합 분석
보고서" content, using deck_lib. This is the per-report driver script you
write fresh each time -- the content (sentences, keywords, table rows) is
specific to this dataset, but the mechanics (find_shape, set_rich,
fit_table, add_image_into_placeholder) come from deck_lib.

Usage:
    python3 fill_deck.py draft.pptx final.pptx
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from deck_lib import (  # noqa: E402
    add_image_into_placeholder, find_shape, set_footer, set_plain,
    set_source_footnote, set_text_with_keywords, fit_table,
)
from pptx import Presentation  # noqa: E402
from pptx.dml.color import RGBColor  # noqa: E402

ORANGE = RGBColor(0xED, 0x7D, 0x31)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARKTEXT = RGBColor(0x26, 0x26, 0x26)
CHART_DIR = Path(__file__).resolve().parent / "charts"

DECK_TITLE = "이력서 100개 종합 분석 보고서"
SUBTITLE = "인구통계 · 학력 · 경력 · 산업 · 역량 데이터 기반 분석"
SOURCE = "출처: 이력서 100개 종합 분석 보고서 (2026-03)"
TOTAL = 30

# below-shape names for the table layout's insight box + source footnote,
# in top-to-bottom order (see inspect_template.py output for a new template)
TABLE_BELOW_SHAPES = ["Rounded Rectangle 8", "TextBox 9"]

ROM = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}
SEC_TITLE = {
    1: "지원자 프로필 — 인구통계 & 학력",
    2: "경력 프로필 — 연차 및 이직 패턴",
    3: "산업 분포",
    4: "보유 역량 — 스킬 & 자격증",
    5: "종합 인사이트",
}

DIVIDERS = {
    2: ("01", "지원자 프로필 — 인구통계 & 학력", "성별 · 연령 · 학력 분포", "전공 · 출신대학 · 학점 현황"),
    11: ("02", "경력 프로필 — 연차 및 이직 패턴", "총 경력 및 직급 분포", "이직 패턴 (보유 회사 수)"),
    17: ("03", "산업 분포", "업종별 지원자 분포", "상위 업종 상세 현황"),
    20: ("04", "보유 역량 — 스킬 & 자격증", "보유 스킬 및 카테고리 분포", "자격증 보유 현황"),
    26: ("05", "종합 인사이트", "주요 인사이트 요약", "핵심 프로필 지표"),
}

CONTENT = [
    (3, 1, "chart", "성별 분포",
     "지원자 100명 중 남성은 67명(67%), 여성은 33명(33%)이다.",
     ["67명(67%)", "33명(33%)"], "gender.png"),
    (4, 1, "chart", "연령대 분포",
     "연령대는 20대 후반(25~29세) 42명(42%), 30대 초반(30~34세) 35명(35%) 순으로 많다.",
     ["42명(42%)", "35명(35%)"], "age.png"),
    (5, 1, "table", "연령대 분포 상세",
     "연령대별 인원은 20대 후반 42명, 30대 초반 35명, 30대 후반 22명, 20대 초반 1명이다.",
     ["42명", "35명", "22명", "1명"],
     dict(header=["연령대", "인원", "비율", "비고"],
          rows=[["20대 후반 (25~29세)", "42명", "42%", "최다 구간"],
                ["30대 초반 (30~34세)", "35명", "35%", ""],
                ["30대 후반 (35~39세)", "22명", "22%", ""],
                ["20대 초반 (~24세)", "1명", "1%", "최소 구간"]],
          insight="20대 후반과 30대 초반을 합하면 전체의 77%를 차지한다.",
          insight_kw=["77%"])),
    (6, 1, "chart", "전공 분포",
     "전공은 경영학과 69명(69%), 경영학부 15명(15%) 순으로 많다.",
     ["69명(69%)", "15명(15%)"], "major.png"),
    (7, 1, "table", "전공 분포 상세",
     "전공 분포는 경영학과 69명, 경영학부 15명, 경제학 8명, 산업공학 6명, 기타 2명이다.",
     ["69명", "15명", "8명", "6명", "2명"],
     dict(header=["전공", "인원", "비율", "비고"],
          rows=[["경영학과", "69명", "69%", ""],
                ["경영학부", "15명", "15%", ""],
                ["경제학", "8명", "8%", ""],
                ["산업공학", "6명", "6%", ""],
                ["기타", "2명", "2%", ""],
                ["경영학 계열 합계", "84명", "84%", "경영학과+경영학부"]],
          insight="경영학 계열(경영학과+경영학부) 전공자는 84명으로 전체의 84%이다.",
          insight_kw=["84명", "84%"])),
    (8, 1, "chart", "출신대학 TOP10",
     "출신대학은 고려대학교 10명, 건국대학교 9명, 아주대학교 8명 순으로 많다.",
     ["10명", "9명", "8명"], "university.png"),
    (9, 1, "chart", "학점 분포",
     "학점(4.5 기준)은 3.7~3.99 구간과 3.3~3.69 구간이 각각 28명(28%)으로 가장 많다.",
     ["28명(28%)"], "gpa.png"),
    (10, 1, "table", "학점 분포 상세",
     "학점 구간별 인원은 4.3 이상 17명, 4.0~4.29 22명, 3.7~3.99 28명, 3.3~3.69 28명, 3.3 미만 5명이다.",
     ["17명", "22명", "28명", "5명"],
     dict(header=["학점 구간", "인원", "비율", "비고"],
          rows=[["4.3 이상 (최우수)", "17명", "17%", ""],
                ["4.0 ~ 4.29", "22명", "22%", ""],
                ["3.7 ~ 3.99", "28명", "28%", "최다 구간"],
                ["3.3 ~ 3.69", "28명", "28%", "최다 구간"],
                ["3.3 미만", "5명", "5%", ""]],
          insight="평균 학점은 3.87/4.5이며, 4.0 이상 보유자는 39명(39%)이다.",
          insight_kw=["3.87/4.5", "39명(39%)"])),
    (12, 2, "chart", "총 경력 분포",
     "총 경력은 3~5년 43명(43%), 6~8년 34명(34%) 순으로 많다.",
     ["43명(43%)", "34명(34%)"], "experience.png"),
    (13, 2, "table", "총 경력 분포 상세",
     "경력 구간별 인원은 신입 1명, 1~2년 10명, 3~5년 43명, 6~8년 34명, 9~12년 12명이다.",
     ["1명", "10명", "43명", "34명", "12명"],
     dict(header=["경력 구간", "인원", "비율", "비고"],
          rows=[["신입 (0년)", "1명", "1%", ""],
                ["1~2년", "10명", "10%", ""],
                ["3~5년", "43명", "43%", "최다 구간"],
                ["6~8년", "34명", "34%", ""],
                ["9~12년", "12명", "12%", ""]],
          insight="평균 경력은 5.4년이며, 3년 이상 경력자는 89명(89%)이다.",
          insight_kw=["5.4년", "89명(89%)"])),
    (14, 2, "chart", "직급 분포",
     "직급은 과장 45명(45%), 대리 39명(39%), 차장 16명(16%) 순이다.",
     ["45명(45%)", "39명(39%)", "16명(16%)"], "position.png"),
    (15, 2, "chart", "이직 패턴 (보유 회사 수)",
     "보유 회사 수는 3개 이상 38명(38%), 2개 33명(33%), 1개 29명(29%) 순이다.",
     ["38명(38%)", "33명(33%)", "29명(29%)"], "companies.png"),
    (16, 2, "table", "경력 · 직급 · 이직 종합 수치",
     "평균 경력 5.4년, 최다 직급은 과장(45명), 3개 이상 회사 경험자는 38명이다.",
     ["5.4년", "45명", "38명"],
     dict(header=["구분", "수치", "비율", "비고"],
          rows=[["평균 총 경력", "5.4년", "-", "전체 100명 기준"],
                ["최다 직급", "과장", "45%", "45명"],
                ["3개 이상 회사 경험", "38명", "38%", "이직 활발 구간"],
                ["과장 + 대리 합계", "84명", "84%", "중간관리자 비중"]],
          insight="과장 · 대리급 중간관리자가 84명으로 전체 직급의 84%를 차지한다.",
          insight_kw=["84명", "84%"])),
    (18, 3, "chart", "업종 분포 TOP15",
     "업종은 금융 17명(17%)이 가장 많고, 게임 · 유통이 각 8명으로 뒤를 잇는다.",
     ["17명(17%)", "8명"], "industry.png"),
    (19, 3, "table", "업종 분포 상세 (TOP8)",
     "상위 업종은 금융 17명, 게임 8명, 유통 8명, 핀테크 7명 순이다.",
     ["17명", "8명", "7명"],
     dict(header=["업종", "인원", "비율", "비고"],
          rows=[["금융", "17명", "17%", "1위"],
                ["게임", "8명", "8%", ""],
                ["유통", "8명", "8%", ""],
                ["핀테크", "7명", "7%", ""],
                ["IT플랫폼", "6명", "6%", ""],
                ["통신", "6명", "6%", ""],
                ["에너지", "6명", "6%", ""],
                ["보험", "6명", "6%", ""]],
          insight="상위 8개 업종 종사자를 합하면 58명(58%)이다.",
          insight_kw=["58명(58%)"])),
    (21, 4, "chart", "보유 스킬 TOP20",
     "보유 스킬은 SQL 31명(31%), 공급망관리 30명(30%) 순으로 많다.",
     ["31명(31%)", "30명(30%)"], "skills.png"),
    (22, 4, "table", "보유 스킬 상세 (TOP10)",
     "상위 스킬은 SQL 31명, 공급망관리 30명, 원가관리 29명, 투자분석 28명 순이다.",
     ["31명", "30명", "29명", "28명"],
     dict(header=["스킬", "인원", "비율", "비고"],
          rows=[["SQL", "31명", "31%", "1위"],
                ["공급망관리", "30명", "30%", ""],
                ["원가관리", "29명", "29%", ""],
                ["투자분석", "28명", "28%", ""],
                ["예산관리", "27명", "27%", ""],
                ["영어(비즈니스)", "26명", "26%", ""],
                ["프로젝트관리", "26명", "26%", ""],
                ["교육훈련", "25명", "25%", ""],
                ["회계", "24명", "24%", ""],
                ["Python", "24명", "24%", ""]],
          insight="데이터 관련 스킬(SQL · Python)이 상위 10개 스킬 안에 포함된다.",
          insight_kw=["SQL", "Python"])),
    (23, 4, "chart", "스킬 카테고리별 분포",
     "카테고리별로는 경영/기획 역량 95명(95%), IT/데이터 스킬 89명(89%) 순이다.",
     ["95명(95%)", "89명(89%)"], "skill_category.png"),
    (24, 4, "chart", "자격증 보유 현황",
     "자격증 미보유자는 47명(47%)으로 가장 많고, 정보처리기사 · CFA · ERP정보관리사가 각 8명이다.",
     ["47명(47%)", "8명"], "certificates.png"),
    (25, 4, "table", "자격증 보유 현황 상세",
     "자격증 보유 현황은 없음 47명, 정보처리기사 8명, CFA 8명, ERP정보관리사 8명 순이다.",
     ["47명", "8명"],
     dict(header=["자격증", "인원", "비율", "비고"],
          rows=[["없음", "47명", "47%", ""],
                ["정보처리기사", "8명", "8%", ""],
                ["CFA (공인재무분석사)", "8명", "8%", ""],
                ["ERP정보관리사", "8명", "8%", ""],
                ["증권투자권유대행인", "7명", "7%", ""],
                ["PMP (프로젝트관리전문가)", "6명", "6%", ""],
                ["경영지도사", "5명", "5%", ""],
                ["ADsP (데이터분석준전문가)", "4명", "4%", ""],
                ["재경관리사", "4명", "4%", ""],
                ["공인회계사 (CPA)", "3명", "3%", ""]],
          insight="자격증 보유자는 53명(53%)으로, 보유자와 미보유자 비율이 비슷하다.",
          insight_kw=["53명(53%)"])),
    (27, 5, "table", "주요 인사이트 요약",
     "100명 데이터에서 확인된 핵심 인사이트는 6가지이다.",
     ["6가지"],
     dict(header=["번호", "인사이트", "핵심 수치", "관련 섹션"],
          rows=[["1", "경영학 전공 집중", "84명 (84%)", "I"],
                ["2", "중간관리자 중심", "84명 (84%)", "II"],
                ["3", "데이터 스킬 보편화", "SQL 31% · Python 24%", "IV"],
                ["4", "이직 경험 많음", "38명 (38%)", "II"],
                ["5", "자격증 보유율 낮음", "53명 (53%)", "IV"],
                ["6", "금융 업종 최다", "17명 (17%)", "III"]],
          insight="6개 인사이트 모두 100명 데이터의 실제 집계 수치에 근거한다.",
          insight_kw=["100명"])),
    (28, 5, "chart", "핵심 프로필 지표",
     "경영학 계열 전공과 과장 · 대리급 비율이 각각 84%로 가장 높고, 자격증 미보유율은 47%이다.",
     ["84%", "47%"], "key_metrics.png"),
]


def set_breadcrumb(slide, subtopic, roman, section_title):
    set_plain(find_shape(slide, text_exact="[발표 제목] — [부제]"), f"{DECK_TITLE} — {SUBTITLE}")
    set_plain(find_shape(slide, text_exact="[소주제]"), subtopic)
    set_plain(find_shape(slide, text_exact="[I. 섹션명]"), f"{roman}. {section_title}")


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    draft_path, out_path = sys.argv[1:3]

    prs = Presentation(draft_path)
    slides = list(prs.slides)

    # Title
    s = slides[0]
    set_plain(find_shape(s, text_exact="[발표 제목]"), DECK_TITLE)
    set_plain(find_shape(s, text_exact="[부제 — 세션 · 다루는 주제 요약]"), SUBTITLE)
    set_plain(find_shape(s, text_exact="[YYYY년 M월]"), "2026년 3월")
    set_plain(find_shape(s, text_exact="[발표자 이름]   [소속]"), "인사분석팀   Biyard")

    # TOC
    s = slides[1]
    for i, t in enumerate(list(SEC_TITLE.values()), 1):
        set_plain(find_shape(s, text_exact=f"[섹션 {i} 제목]"), t)
    set_plain(find_shape(s, text_exact="2 / 6"), f"2 / {TOTAL}")

    # Dividers
    for idx, (num, title, sub1, sub2) in DIVIDERS.items():
        s = slides[idx]
        set_plain(find_shape(s, text_exact="01"), num)
        set_plain(find_shape(s, text_exact="[섹션 제목]"), title)
        set_plain(find_shape(s, text_exact="[이 섹션에서 다룰 소주제 1]"), sub1)
        set_plain(find_shape(s, text_exact="[이 섹션에서 다룰 소주제 2]"), sub2)

    # Closing (reuses the title-layout clone at the end of the outline)
    s = slides[29]
    set_plain(find_shape(s, text_exact="[발표 제목]"), "감사합니다")
    set_plain(find_shape(s, text_exact="[부제 — 세션 · 다루는 주제 요약]"), "Thank You")
    set_plain(find_shape(s, text_exact="Date"), "Source")
    set_plain(find_shape(s, text_exact="[YYYY년 M월]"), SOURCE.replace("출처: ", ""))
    set_plain(find_shape(s, text_exact="Presenter"), "Prepared by")
    set_plain(find_shape(s, text_exact="[발표자 이름]   [소속]"), "인사분석팀   Biyard")

    # Content slides
    for idx, sec, kind, subtopic, headline, kws, payload in CONTENT:
        s = slides[idx]
        set_breadcrumb(s, subtopic, ROM[sec], SEC_TITLE[sec])
        set_text_with_keywords(
            find_shape(s, text_startswith="[핵심 메시지"), headline, kws,
            size_pt=19, bold=True, color=WHITE, kw_color=ORANGE,
        )
        set_source_footnote(s, SOURCE)
        set_footer(s, idx + 1, TOTAL, suffix_hint="/ 6")

        if kind == "chart":
            add_image_into_placeholder(s, "[이미지", str(CHART_DIR / payload))
        else:
            fit_table(s, payload["header"], payload["rows"], below_shape_names=TABLE_BELOW_SHAPES)
            set_text_with_keywords(
                find_shape(s, text_startswith="[표에서 읽어야"), payload["insight"], payload["insight_kw"],
                size_pt=10, bold=False, color=DARKTEXT, kw_color=ORANGE,
            )

    prs.save(out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    main()
