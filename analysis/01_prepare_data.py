"""KOSIS 원자료(월별·원인별 발생건수)를 분석하기 쉬운 형태로 변환합니다.

입력: data/raw_kosis_monthly_cause.xlsx  (KOSIS TX_13625_A003, 헤더 2줄: 연도 / 원인)
출력: data/fire_long.csv   (월, 연도, 원인, 건수 — 한 줄에 값 하나)
      data/cube.json       (웹사이트용 [연도][월][원인] 3차원 배열)

처리 원칙
- 원본의 '-' 는 0건으로 처리합니다.
- 2022년에는 '어린이불장난' 항목이 원본에 없습니다. CSV에는 0으로 저장되지만,
  웹사이트에서는 결측(null)으로 취급해 평균의 분모에서 제외합니다.
실행: 저장소 최상위 폴더에서  python analysis/01_prepare_data.py
"""
import json, warnings
from pathlib import Path
import pandas as pd

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw_kosis_monthly_cause.xlsx"

df = pd.read_excel(RAW, sheet_name=0, header=[0, 1], index_col=0)
df = df.replace("-", 0).apply(pd.to_numeric, errors="coerce").fillna(0)
df.index.name = "m"
df.columns.names = ["y", "c"]
long = df.stack([0, 1]).reset_index()
long.columns = ["월", "연도", "원인", "건수"]
long["월"] = long["월"].str.replace("월", "").astype(int)
long["연도"] = long["연도"].astype(int)
long.to_csv(ROOT / "data" / "fire_long.csv", index=False)

# 원인은 20년 합계가 큰 순서로 정렬
order = long.groupby("원인")["건수"].sum().sort_values(ascending=False).index.tolist()
years = sorted(long["연도"].unique())
piv = long.pivot_table(index=["연도", "월"], columns="원인", values="건수", aggfunc="sum").reindex(columns=order).fillna(0)
v = [[[int(piv.loc[(y, m), c]) for c in order] for m in range(1, 13)] for y in years]
json.dump({"years": [int(y) for y in years], "causes": order, "v": v},
          open(ROOT / "data" / "cube.json", "w"), ensure_ascii=False)
print(f"완료: {len(long)}행, 총 {int(long['건수'].sum()):,}건")
