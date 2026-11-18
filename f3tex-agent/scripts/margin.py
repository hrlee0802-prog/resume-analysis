"""원가표에서 Article별 원가·최저 단가를 다시 계산합니다 (규정 SR-02 제3조).

사용: python3 scripts/margin.py data/04-costing.csv [단가표 예: FT-2801=2.95,SJ-1602=2.40]
원가표의 total_cost_usd 열은 쓰지 않고 항목별 값으로 다시 계산합니다.
"""
import csv
import math
import sys

RATE = 1380.0      # 기준환율 KRW/USD (SR-02 제3조 2항)
MIN_MARGIN = 0.12  # 최소 마진율 (SR-02 제3조 3항)


def main() -> None:
    path = sys.argv[1]
    offered = {}
    if len(sys.argv) > 2:
        for pair in sys.argv[2].split(","):
            k, v = pair.split("=")
            offered[k.strip()] = float(v)

    print("| Article | 원가 재계산(USD/yd) | 원가표 합계 열 | 최저 단가(12%) | 오퍼 단가 | 마진율 | 판정 |")
    print("|---|---|---|---|---|---|---|")
    with open(path, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            mill = float(r["mill_price_krw_per_yd"]) / RATE
            cost = mill + sum(float(r[c]) for c in (
                "finishing_usd", "inland_handling_usd", "packing_usd", "finance_insurance_usd"))
            floor_price = math.ceil(round(cost / (1 - MIN_MARGIN), 6) * 100) / 100
            sheet_total = float(r["total_cost_usd"])
            art = r["article"]
            note = "" if abs(sheet_total - cost) < 0.005 else " ⚠ 불일치"
            if art in offered:
                p = offered[art]
                m = (p - cost) / p
                verdict = "미달" if m < MIN_MARGIN else "충족"
                print(f"| {art} | {cost:.2f} | {sheet_total:.2f}{note} | {floor_price:.2f} | {p:.2f} | {m*100:.1f}% | {verdict} |")
            else:
                print(f"| {art} | {cost:.2f} | {sheet_total:.2f}{note} | {floor_price:.2f} | - | - | - |")


if __name__ == "__main__":
    main()
