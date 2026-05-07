# -*- coding: utf-8 -*-
"""
Export bean-model data for the portfolio website.

Reads:
    C:\\Users\\魏来\\Desktop\\山顶资本\\量化\\全部数据\\bobo1号模型\\semi_backtest_signals.csv

Writes:
    portfolio-hub/bean-model/data.json

Privacy filters applied:
    - Only 2024-2025 signal records (excludes 2026+ to keep current period private)
    - Per-stock aggregate stats only (no specific trigger dates with indicator values)
    - No RSI / MACD / vol_ratio values per signal
    - Universe + total signal count visible (semi sector leaders are public domain)
"""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

SRC = Path(r"C:/Users/魏来/Desktop/山顶资本/量化/全部数据/bobo1号模型/semi_backtest_signals.csv")
DST = Path(__file__).parent / "data.json"

# 25-stock semiconductor universe — extracted from量化/semi_backtest.py
UNIVERSE = [
    ("688981", "中芯国际"),  ("002371", "北方华创"),  ("603501", "韦尔股份"),
    ("300661", "圣邦股份"),  ("688008", "澜起科技"),  ("300782", "卓胜微"),
    ("688385", "复旦微电"),  ("688012", "中微公司"),  ("688396", "华润微"),
    ("600460", "士兰微"),    ("600584", "长电科技"),  ("002156", "通富微电"),
    ("300316", "晶盛机电"),  ("300223", "北京君正"),  ("300672", "国科微"),
    ("603290", "斯达半导"),  ("688187", "时代电气"),  ("300373", "扬杰科技"),
    ("688082", "盛美上海"),  ("605111", "新洁能"),    ("002129", "TCL中环"),
    ("002049", "紫光国微"),  ("002230", "科大讯飞"),  ("000725", "京东方A"),
    ("688256", "寒武纪"),
]
UNIVERSE_DICT = {code.lstrip('0').zfill(6): name for code, name in UNIVERSE}

def main():
    sig = pd.read_csv(SRC)

    # Period filter: 2024-2025 only (2026+ stays private)
    sig = sig[sig['year'].isin([2024, 2025])].copy()
    sig['code'] = sig['code'].astype(str).str.lstrip('0').str.zfill(6)

    # Aggregate proof — headline stats
    n_signals = len(sig)
    win10 = (sig['ret10f'] > 0).mean() * 100
    avg10 = sig['ret10f'].mean()
    win5  = (sig['ret5f']  > 0).mean() * 100
    avg5  = sig['ret5f'].mean()
    win20 = (sig['ret20f'] > 0).mean() * 100
    avg20 = sig['ret20f'].mean()

    # Year breakdown
    by_year = []
    for year in [2024, 2025]:
        sub = sig[sig['year'] == year]
        if len(sub) == 0:
            by_year.append({"year": year, "signals": 0,
                            "win10": None, "avg10": None})
        else:
            by_year.append({
                "year": year,
                "signals": len(sub),
                "win10": round((sub['ret10f'] > 0).mean() * 100, 1),
                "avg10": round(sub['ret10f'].mean(), 2),
            })

    # Per-stock aggregate
    per_stock = {}
    for code, name in UNIVERSE:
        c = code.lstrip('0').zfill(6)
        sub = sig[sig['code'] == c]
        if len(sub) == 0:
            per_stock[c] = {
                "code": c, "name": name,
                "signals": 0, "win10": None, "avg10": None,
                "first_signal": None, "last_signal": None,
            }
        else:
            per_stock[c] = {
                "code": c, "name": name,
                "signals": int(len(sub)),
                "win10": round((sub['ret10f'] > 0).mean() * 100, 1),
                "avg10": round(sub['ret10f'].mean(), 2),
                "first_signal": str(sub['date'].min()),
                "last_signal": str(sub['date'].max()),
            }

    # Cumulative equity curve — naive: each signal earns ret10f / 10 over 10 days
    # (simplistic, illustrative; not a tradeable strategy spec)
    sig_sorted = sig.sort_values('date')
    sig_sorted['equity_step'] = sig_sorted['ret10f'] / 100.0  # decimal
    cum = (1 + sig_sorted['equity_step']).cumprod()
    equity_curve = [
        {"date": d, "equity": round(float(e), 4)}
        for d, e in zip(sig_sorted['date'].astype(str), cum)
    ]

    payload = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "period": "2024-01-01 to 2025-12-31",
        "universe_size": len(UNIVERSE),
        "universe_label_en": "Semiconductor sector leaders (A-share)",
        "universe_label_zh": "半导体板块龙头（A 股）",
        "criterion_en": "bean_score >= 5 (of 6 rules) AND anti_chase_score >= 2 (of 3 filters)",
        "criterion_zh": "豆模型 6 条核心条件至少满足 5 条，且 3 条追高过滤至少通过 2 条",
        "headline": {
            "n_signals":   int(n_signals),
            "n_stocks":    int(sig['code'].nunique()),
            "win5":  round(win5, 1),  "avg5":  round(avg5, 2),
            "win10": round(win10, 1), "avg10": round(avg10, 2),
            "win20": round(win20, 1), "avg20": round(avg20, 2),
        },
        "by_year": by_year,
        "per_stock": list(per_stock.values()),
        "equity_curve": equity_curve,
    }

    DST.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Wrote {DST} ({DST.stat().st_size // 1024} KB)")
    print(f"  Period: 2024-2025 · {n_signals} signals across {sig['code'].nunique()} stocks (of {len(UNIVERSE)} universe)")
    print(f"  10d win rate: {win10:.1f}% · avg return: {avg10:+.2f}%")
    print(f"  20d win rate: {win20:.1f}% · avg return: {avg20:+.2f}%")
    print(f"  Equity curve: {len(equity_curve)} points")

if __name__ == "__main__":
    main()
