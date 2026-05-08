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

Portfolio simulation (v1.2):
    - Principal : ¥1,000,000
    - Position  : ¥100,000 per signal (10% fixed notional)
    - Holding   : 10 trading days
    - P&L       : position × ret10f/100  (realised at exit, not compounded)
    - Curve     : portfolio_value[i] = principal + cumsum(pnl[i])
      This replaces the v1.0/v1.1 cumprod equity_curve which was illustrative only.
"""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

SRC = Path(r"C:/Users/魏来/Desktop/山顶资本/量化/全部数据/bobo1号模型/semi_backtest_signals.csv")
DST = Path(__file__).parent / "data.json"

PRINCIPAL = 1_000_000     # ¥1,000,000 starting capital
POSITION  =   100_000     # ¥100,000 per signal (fixed notional)

# 25-stock semiconductor universe — extracted from 量化/semi_backtest.py
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


def compute_max_drawdown(values):
    """Peak-to-trough max drawdown as a fraction (0–1)."""
    peak = values[0]
    max_dd = 0.0
    for v in values:
        if v > peak:
            peak = v
        dd = (peak - v) / peak if peak > 0 else 0.0
        if dd > max_dd:
            max_dd = dd
    return max_dd


def main():
    sig = pd.read_csv(SRC)

    # Period filter: 2024-2025 only (2026+ stays private)
    sig = sig[sig['year'].isin([2024, 2025])].copy()
    sig['code'] = sig['code'].astype(str).str.lstrip('0').str.zfill(6)

    # ── Aggregate proof — headline stats ──────────────────────────────────────
    n_signals = len(sig)
    win10 = (sig['ret10f'] > 0).mean() * 100
    avg10 = sig['ret10f'].mean()
    win5  = (sig['ret5f']  > 0).mean() * 100
    avg5  = sig['ret5f'].mean()
    win20 = (sig['ret20f'] > 0).mean() * 100
    avg20 = sig['ret20f'].mean()

    # ── Year breakdown ────────────────────────────────────────────────────────
    by_year = []
    for year in [2024, 2025]:
        sub = sig[sig['year'] == year]
        if len(sub) == 0:
            by_year.append({"year": year, "signals": 0,
                            "win10": None, "avg10": None})
        else:
            by_year.append({
                "year":    year,
                "signals": len(sub),
                "win10":   round((sub['ret10f'] > 0).mean() * 100, 1),
                "avg10":   round(sub['ret10f'].mean(), 2),
            })

    # ── Per-stock aggregate ───────────────────────────────────────────────────
    per_stock = {}
    for code, name in UNIVERSE:
        c   = code.lstrip('0').zfill(6)
        sub = sig[sig['code'] == c]
        if len(sub) == 0:
            per_stock[c] = {
                "code": c, "name": name,
                "signals": 0, "win10": None, "avg10": None,
                "first_signal": None, "last_signal": None,
            }
        else:
            per_stock[c] = {
                "code":         c, "name": name,
                "signals":      int(len(sub)),
                "win10":        round((sub['ret10f'] > 0).mean() * 100, 1),
                "avg10":        round(sub['ret10f'].mean(), 2),
                "first_signal": str(sub['date'].min()),
                "last_signal":  str(sub['date'].max()),
            }

    # ── Portfolio simulation (v1.2) ───────────────────────────────────────────
    # Sort chronologically — P&L realised at exit date (approx. = signal date)
    sig_sorted = sig.sort_values('date').reset_index(drop=True)
    sig_sorted['pnl'] = sig_sorted['ret10f'] / 100.0 * POSITION

    portfolio_value = float(PRINCIPAL)
    peak_value      = float(PRINCIPAL)
    max_dd_abs      = 0.0
    max_dd_pct      = 0.0
    n_wins          = 0
    n_losses        = 0
    best_pnl        = float('-inf')
    worst_pnl       = float('inf')
    portfolio_curve = []

    for _, row in sig_sorted.iterrows():
        pnl = float(row['pnl'])
        portfolio_value += pnl

        if portfolio_value > peak_value:
            peak_value = portfolio_value

        dd_abs = peak_value - portfolio_value
        dd_pct = dd_abs / peak_value if peak_value > 0 else 0.0
        if dd_abs > max_dd_abs:
            max_dd_abs = dd_abs
        if dd_pct > max_dd_pct:
            max_dd_pct = dd_pct

        if pnl > 0:
            n_wins += 1
        else:
            n_losses += 1

        if pnl > best_pnl:
            best_pnl = pnl
        if pnl < worst_pnl:
            worst_pnl = pnl

        portfolio_curve.append({
            "date":  str(row['date']),
            "value": round(portfolio_value, 2),
        })

    total_pnl       = portfolio_value - PRINCIPAL
    total_return_pct = total_pnl / PRINCIPAL * 100.0

    portfolio_summary = {
        "principal":        PRINCIPAL,
        "position_size":    POSITION,
        "final_value":      round(portfolio_value, 2),
        "total_pnl":        round(total_pnl, 2),
        "total_return_pct": round(total_return_pct, 2),
        "n_wins":           n_wins,
        "n_losses":         n_losses,
        "best_trade_pnl":   round(best_pnl, 2),
        "worst_trade_pnl":  round(worst_pnl, 2),
        "max_drawdown_pct": round(max_dd_pct * 100, 2),
        "max_drawdown_cny": round(max_dd_abs),
    }

    # ── Canonical headline (from v3 research log, NOT derived from semi CSV) ─
    # Source of truth: 豆模型/bobo豆模型v3日志.md  ·  数据库3号 large-scale validation
    canonical = {
        "source_en":         "Research log v3.0 — 数据库3号 large-scale validation",
        "source_zh":         "研究日志 v3.0 — 数据库 3 号大规模验证",
        "universe_size":     240,
        "n_signals":         390,
        "win_5d":            69.8,
        "avg_5d":            3.18,
        "win_10d":           68.1,
        "avg_10d":           3.53,
        "win_20d":           57.0,
        "optimal_hold":      5,
        "training_window":   "2023-2024",
        "validation_window": "2025+",
        "best_year":         {"year": 2022, "win": 88.3, "note_en": "bull market", "note_zh": "牛市"},
        "weak_year":         {"year": 2023, "win": 52.8, "note_en": "choppy bottom — technical signals lost edge", "note_zh": "震荡磨底，技术信号失效"},
    }

    # ── Key research findings (from v3 log; copyable bullets for §1.5) ────────
    findings = [
        {
            "label_en": "Stop-loss is harmful",
            "label_zh": "止损反而砍胜率",
            "body_en":  "Adding −5% / MA10 stop-losses cut win rate from 69% to 54% across 390 signals. The losses being avoided were future winners. Lesson: do not interfere with positions once entered.",
            "body_zh":  "在 390 笔信号上加 -5% / 跌破 MA10 止损，胜率从 69% 直接砍到 54%。被止损切掉的大多是后来的赢家。结论：进场后不要主动干预。",
        },
        {
            "label_en": "5-day hold optimal, not 10–20",
            "label_zh": "5 日持仓最优，非 10-20 日",
            "body_en":  "Win-rate decay across hold periods: 5d 69.8% → 10d 68.1% → 20d 57.0%. The original v2 spec of \"10-20 trading days\" was empirically wrong; v3 locks 5-day hold as the canonical exit.",
            "body_zh":  "持仓期胜率衰减明显：5 日 69.8% → 10 日 68.1% → 20 日 57.0%。v2 原定的 10-20 日持仓被数据证伪；v3 锁定 5 日为标准出场。",
        },
        {
            "label_en": "Alpha is in entry timing, not exit",
            "label_zh": "Alpha 来自进场，不来自出场",
            "body_en":  "Soft-exit scoring, profit locks, and trailing stops all tested on the 390-signal panel — every active management overlay reduced win rate. The model's edge sits entirely in selecting WHEN to enter; staying in is passive.",
            "body_zh":  "软性卖点评分、浮盈锁定、跟踪止损 —— 在 390 笔信号上全部测过，每一种主动管理都让胜率下降。模型的 alpha 完全在\"何时进场\"，进场后就该被动持有。",
        },
        {
            "label_en": "v3 adds market-regime gate",
            "label_zh": "v3 新增大盘门控",
            "body_en":  "v2 fired regardless of market regime — 2023's choppy bottom dragged win rate to 52.8%. v3 only fires when (i) HS300 trades above its 20-day MA AND (ii) ChiNext is not down >8% over 20 days. Predicted win-rate lift to 72-76% (pending verification on 数据库3号).",
            "body_zh":  "v2 不管大盘环境硬开仓，2023 震荡磨底拖到 52.8%。v3 只在 (i) 沪深 300 站上 20 日均线 且 (ii) 创业板 20 日跌幅不超过 8% 时才允许开仓。预计胜率提升至 72-76%（待数据库 3 号回测验证）。",
        },
    ]

    # ── Build payload ─────────────────────────────────────────────────────────
    payload = {
        "generated_at":      datetime.now().strftime("%Y-%m-%d %H:%M"),
        "period":            "2024-01-01 to 2025-12-31",
        "canonical":         canonical,
        "findings":          findings,
        "universe_size":     len(UNIVERSE),
        "universe_label_en": "Semiconductor sector leaders (A-share)",
        "universe_label_zh": "半导体板块龙头（A 股）",
        "criterion_en":      "bean_score >= 5 (of 6 rules) AND anti_chase_score >= 2 (of 3 filters)",
        "criterion_zh":      "豆模型 6 条核心条件至少满足 5 条，且 3 条追高过滤至少通过 2 条",
        "headline": {
            "n_signals":   int(n_signals),
            "n_stocks":    int(sig['code'].nunique()),
            "win5":  round(win5, 1),  "avg5":  round(avg5, 2),
            "win10": round(win10, 1), "avg10": round(avg10, 2),
            "win20": round(win20, 1), "avg20": round(avg20, 2),
        },
        "by_year":         by_year,
        "per_stock":       list(per_stock.values()),
        "portfolio":       portfolio_summary,
        "portfolio_curve": portfolio_curve,
    }

    DST.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"Wrote {DST} ({DST.stat().st_size // 1024} KB)")
    print(f"  Period: 2024-2025 · {n_signals} signals · {sig['code'].nunique()} stocks (of {len(UNIVERSE)} universe)")
    print(f"  10d win rate: {win10:.1f}% · avg return: {avg10:+.2f}%")
    print(f"  Portfolio: ¥{PRINCIPAL:,} → ¥{portfolio_value:,.0f}  ({total_return_pct:+.2f}%)")
    print(f"  Wins: {n_wins} / Losses: {n_losses}")
    print(f"  Best: ¥{best_pnl:,.2f} / Worst: ¥{worst_pnl:,.2f}")
    print(f"  Max drawdown: {max_dd_pct*100:.2f}% / ¥{max_dd_abs:,.0f}")


if __name__ == "__main__":
    main()
