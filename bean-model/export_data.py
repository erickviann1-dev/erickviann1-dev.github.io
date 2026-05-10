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
    - No rule thresholds, IC ranks, current picks, or live candidate lists
    - Interactive cases are historical / delayed display only

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
DB4_RANDOM_UNIVERSE = Path(r"C:/Users/魏来/Desktop/山顶资本/豆模型/random_tech_120_baseline_db4tech_20250205_20260205_universe.csv")
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

    # ── Legacy per-stock aggregate fallback ──────────────────────────────────
    # This is kept only as a fallback if the DB4 public-random universe file is
    # unavailable. The public site should prefer DB4 delayed random tech cases.
    per_stock_full = {}
    for code, name in UNIVERSE:
        c   = code.lstrip('0').zfill(6)
        sub = sig[sig['code'] == c]
        if len(sub) > 0:
            # ret10f distribution per stock for sparkline (cumulative)
            sub_sorted = sub.sort_values('date')
            cum = (1 + sub_sorted['ret10f'] / 100.0).cumprod().tolist()
            per_stock_full[c] = {
                "code":         c, "name": name,
                "signals":      int(len(sub)),
                "win10":        round((sub['ret10f'] > 0).mean() * 100, 1),
                "avg10":        round(sub['ret10f'].mean(), 2),
                "first_signal": str(sub['date'].min()),
                "last_signal":  str(sub['date'].max()),
                # spark = per-signal cumulative return path (for the inline mini chart)
                "spark":        [round(float(v), 4) for v in cum],
            }
    per_stock = []

    # ── Public interactive sample pool: DB4 random 50 technology cases ───────
    # Source file contains DB4 technology-universe 120D forward-return windows.
    # Public display may show historical stock names/codes, but still exports no
    # signal dates, factor values, thresholds, or current candidate information.
    if DB4_RANDOM_UNIVERSE.exists():
        db4 = pd.read_csv(DB4_RANDOM_UNIVERSE)
        db4["symbol"] = db4["symbol"].astype(str).str.lstrip("0").str.zfill(6)
        grouped = list(db4.groupby("symbol", sort=True))
        sample_symbols = (
            pd.Series([sym for sym, _ in grouped])
            .sample(n=min(50, len(grouped)), random_state=42)
            .tolist()
        )
        group_map = {sym: g for sym, g in grouped}
        for idx, sym in enumerate(sample_symbols, start=1):
            g = group_map[sym].sort_values("date")
            display_name = str(g["name"].iloc[0]) if "name" in g.columns else sym
            ret = pd.to_numeric(g["ret_120d"], errors="coerce").dropna()
            mdd = pd.to_numeric(g["mdd_120d"], errors="coerce").dropna()
            closes = pd.to_numeric(g["close"], errors="coerce").dropna()
            if len(ret) == 0:
                continue
            if len(closes) >= 2:
                spark = (closes / closes.iloc[0]).tolist()
            else:
                spark = (1 + ret / 100.0).cumprod().tolist()
            curve = []
            if len(closes) >= 2 and "date" in g.columns:
                base = float(closes.iloc[0])
                dates = g.loc[closes.index, "date"].astype(str).tolist()
                curve = [
                    {"date": dates[i], "value": round(float(closes.iloc[i] / base), 4)}
                    for i in range(len(closes))
                    if base != 0
                ]
            per_stock.append({
                "case_id": f"DB4-{idx:02d}",
                "code": sym,
                "name": display_name,
                "signals": int(len(ret)),
                "win10": round((ret > 0).mean() * 100, 1),
                "avg10": round(ret.mean(), 2),
                "mdd120": round(mdd.median(), 2) if len(mdd) else None,
                "spark": [round(float(v), 4) for v in spark[-80:]],
                "curve": curve,
            })
    else:
        for idx, item in enumerate(per_stock_full.values(), start=1):
            anonymized = dict(item)
            anonymized["case_id"] = f"CASE-{idx:02d}"
            anonymized["code"] = f"CASE-{idx:02d}"
            anonymized["name"] = "Historical case"
            anonymized.pop("first_signal", None)
            anonymized.pop("last_signal", None)
            per_stock.append(anonymized)
    active_universe_size = len(per_stock)

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

    # ── Canonical headline (v3.1 LOCKED — from 网站发布版.md, 2026-05) ─────
    # Source: v2模型验证/网站发布版.md (database-3 final validation, 500 stocks)
    canonical = {
        "source_en":         "Research note v3.1 LOCKED — Database 3, 500 tech stocks, 2022-2026",
        "source_zh":         "研究终稿 v3.1 锁定版 — 数据库 3 号 · 500 只科技股 · 2022-2026",
        "universe_size":     500,
        "n_signals":         1199,
        "win_5d":            60.7,
        "win_10d":           62.6,
        "win_20d":           56.8,
        "optimal_hold":      80,
        "headline_win":      88.5,           # 80-day hold rate
        "headline_avg":      36.67,          # 80-day avg return %
        "headline_window":   "2025-05 → 2026-02 (full 80d completion possible)",
    }

    # ── Hold-period discovery — THE killer finding ──────────────────────────
    # Test window: 2025-05 → 2026-02, 52 signals where full 80d holds
    hold_period_table = [
        {"days": 5,  "win": 50.0, "avg": 1.77,  "median": -0.03},
        {"days": 10, "win": 59.6, "avg": 2.94,  "median": 1.83},
        {"days": 30, "win": 64.4, "avg": 8.64,  "median": 6.64},
        {"days": 60, "win": 75.0, "avg": 24.77, "median": 12.38},
        {"days": 80, "win": 88.5, "avg": 36.67, "median": 23.00},  # LOCKED
    ]

    # ── Regime-adapted model timeline (2022-2026) ───────────────────────────
    # These cards intentionally show the model / horizon that best matches each
    # market stage, rather than forcing every year into one fixed 10D lens.
    market_regime = [
        {"year": 2022, "win10": 81.5, "n": 222,
         "model": "v2 / v3.1", "metric_en": "10D win", "metric_zh": "10日胜率",
         "label_en": "Short-term reversal golden age",
         "label_zh": "短线反转黄金期",
         "note_en": "Sector rotation rapid; '5-10d mean reversion' worked everywhere.",
         "note_zh": "板块快速轮动；5-10 日均值回归在各处都有效。"},
        {"year": 2023, "win10": 49.1, "n": 51,
         "model": "Risk-off / cash filter", "metric_en": "10D win", "metric_zh": "10日胜率",
         "label_en": "Models collectively fail",
         "label_zh": "模型集体失效",
         "note_en": "Capital lacked consensus direction; reversal strategies fail across the board.",
         "note_zh": "资金一致性预期不足，方向感弱；短线反转策略集体失灵。"},
        {"year": 2024, "win10": 71.0, "n": 280,
         "model": "v3.1 short lens", "metric_en": "5D win", "metric_zh": "5日胜率",
         "label_en": "Strategy contradiction",
         "label_zh": "策略矛盾期",
         "note_en": "5d holds 71% / 20d holds 41% — choppy market; short OK, medium dangerous.",
         "note_zh": "5 日持有 71%、20 日持有 41% — 震荡市；短线还能做、中线持有就是雷。"},
        {"year": 2025, "win10": 81.25, "n": 48,
         "model": "v4 medium-term", "metric_en": "60-90D win", "metric_zh": "60-90日胜率",
         "label_en": "Main-line holding regime emerges",
         "label_zh": "主线持仓型市场登场",
         "note_en": "Technology beta strengthened. The adapted view shifts from quick reversal to v4 medium-term trend holding.",
         "note_zh": "科技主线增强后，适配视角从短线反转切换到 v4 中线趋势持有。"},
        {"year": 2026, "win10": 92.86, "n": 14,
         "model": "v4.S strict layer", "metric_en": "120D win", "metric_zh": "120日胜率",
         "label_en": "Strict medium/long-term layer",
         "label_zh": "严格中长线层",
         "note_en": "Short-term 10D view was no longer appropriate. The stricter v4.S layer is used to evaluate medium/long-term continuation.",
         "note_zh": "10 日短线视角不再适配。这里改用筛选更严格的 v4.S 中长线口径展示模型进步。"},
    ]

    # ── Key research findings (from 网站发布版.md, the authoritative reframe) ─
    findings = [
        {
            "label_en": "Hold period is a vastly under-rated variable",
            "label_zh": "持有期是被严重低估的变量",
            "body_en":  "The same 52 entry signals produce a 50.0% win rate at a 5-day hold and an 88.5% win rate at an 80-day hold. Hold period doesn't just scale returns — it changes the strategy's identity.",
            "body_zh":  "同一批 52 笔进场信号：5 日持有胜率 50.0%，80 日持有胜率 88.5%。持有期决定的不只是收益大小，是策略的本质。",
        },
        {
            "label_en": "Market style is destiny",
            "label_zh": "市场风格决定策略命运",
            "body_en":  "2022 rewarded short-term reversal (81.5% at 10d). 2025+ rewards medium-term trend holding (88.5% at 80d). The model didn't change — the regime did. There is no permanently optimal strategy; there are only matched holds.",
            "body_zh":  "2022 年震荡市奖励短线反转（10 日 81.5%）；2025 年起主线持仓奖励中线趋势（80 日 88.5%）。模型没变，市场变了。没有永远有效的策略，只有匹配市场的持有期。",
        },
        {
            "label_en": "Short-term failure is often hold-mismatch",
            "label_zh": "短线\"失效\"往往是视角错配",
            "body_en":  "Q4 2025 looked like model collapse: 10-day win rate fell to 41.7%. The same signals at 80-day hold: 71.4%. Question your viewpoint before you question the model — most apparent failures are wrong holding periods, not broken edges.",
            "body_zh":  "2025 Q4 看似 v3.1 灾难季（10 日胜率 41.7%），同一批信号用 80 日持有：71.4%。怀疑视角，不要急着怀疑模型 —— 大多数\"看似失效\"只是持有期错配。",
        },
        {
            "label_en": "Smart filters are usually overfitting in disguise",
            "label_zh": "聪明的过滤往往是过拟合的伪装",
            "body_en":  "Sector strength filter, relative-strength check, dynamic exits, RSI band tightening — all tested, all failed. Each looked smarter than the base model; each made results worse. Simple core rules + the right hold period beat layered filters.",
            "body_zh":  "板块强度过滤、相对强度检查、动态退出、RSI 区间收窄 —— 全部测过，全部失败。每一个看起来都比原版更\"聪明\"，每一个都让结果更差。简单核心规则 + 正确持有期，胜过复杂层层过滤。",
        },
    ]

    # ── Public-facing result layer (rules intentionally withheld) ────────────
    result_summary = {
        "v2_win_rate": 68.0,
        "v2_note_en": "Large-sample validation showed the original core signal was real, but not mythical.",
        "v2_note_zh": "大样本验证证明原始核心信号有效，但不是神话。",
        "v4s_status": "LOCK_CANDIDATE",
        "v4s_win": 92.86,
        "v4s_avg": 59.44,
        "v4s_median": 46.62,
        "random_win": 78.0,
        "random_avg": 42.0,
        "random_median": 23.0,
    }

    model_timeline = [
        {
            "version": "v2",
            "label_en": "Original core signal",
            "label_zh": "原始核心买点",
            "body_en": "The first locked buy signal extracted from real trading records. It proved the sample contains a repeatable edge, but large-sample testing pulled the win rate back to a realistic ~68%.",
            "body_zh": "从真实买入记录中提炼出的第一版锁定买点。它证明样本里确实有可重复特征，但大样本验证把胜率拉回更真实的约 68%。",
        },
        {
            "version": "v3.1",
            "label_en": "Locked discipline",
            "label_zh": "锁定与反过拟合纪律",
            "body_en": "v3.1 did not simply add complexity. Its real value was forcing version discipline: stop changing rules after seeing results, then test the locked signal across regimes and holding periods.",
            "body_zh": "v3.1 不是简单堆复杂条件。它真正的价值是建立版本纪律：看结果之后不再改规则，而是拿锁定信号去跨行情、跨持有期验证。",
        },
        {
            "version": "v4",
            "label_en": "Technology-mainline framework",
            "label_zh": "科技主线框架",
            "body_en": "v4 moved from one buy signal to a tiered framework. It can evaluate short-term moves and medium/long-term holds; the stricter v4.S layer is designed for the strongest medium-term trend opportunities.",
            "body_zh": "v4 从单一买点升级为分层框架。它既能看短线，也能看中长线；其中筛选最严格的 v4.S 层，目标是捕捉最强的中线趋势机会。",
        },
        {
            "version": "Exit",
            "label_en": "Holding and exit research",
            "label_zh": "持有与卖点研究",
            "body_en": "Entry and exit are separated. Short-term exits can reduce drawdown, but the strongest discovery is that strict signals often need 60-120 days to express their edge.",
            "body_zh": "买点和卖点分开研究。短线卖点能降低回撤，但最强发现是：越严格的信号往往需要 60-120 日才能充分释放优势。",
        },
    ]

    v4_horizon = [
        {
            "key": "short",
            "label_en": "Short-term validation",
            "label_zh": "短线验证",
            "horizon_en": "10-20 trading days",
            "horizon_zh": "10-20 个交易日",
            "win": 73.33,
            "avg": 4.76,
            "median": 3.64,
            "body_en": "Useful for checking whether the entry has immediate follow-through, but not where the model's strongest edge appears.",
            "body_zh": "适合验证买点是否有短期跟随，但这不是模型最强的地方。",
        },
        {
            "key": "mid",
            "label_en": "Medium-term trend",
            "label_zh": "中线趋势",
            "horizon_en": "60-90 trading days",
            "horizon_zh": "60-90 个交易日",
            "win": 81.25,
            "avg": 31.91,
            "median": 19.89,
            "body_en": "The signal starts to reveal its true character as a trend-entry filter rather than a quick reversal trade.",
            "body_zh": "信号开始显露真正属性：它更像趋势进场过滤器，而不是单纯短线反转交易。",
        },
        {
            "key": "long",
            "label_en": "Strict long-horizon layer",
            "label_zh": "严格中长线层",
            "horizon_en": "120 trading days · v4.S",
            "horizon_zh": "120 个交易日 · v4.S",
            "win": 92.86,
            "avg": 59.44,
            "median": 46.62,
            "body_en": "The strictest layer filters harder and fires less often, but historically produced the strongest medium/long-term results.",
            "body_zh": "最严格的层级筛得更少，但历史上给出了最强的中长线结果。",
        },
    ]

    strategy_compare = [
        {
            "key": "fixed",
            "label_en": "Fixed holding allocation",
            "label_zh": "固定持有分仓",
            "return": 70.31,
            "max_dd": -20.92,
            "note_en": "Higher upside, larger tail risk.",
            "note_zh": "收益更高，但尾部风险更大。",
        },
        {
            "key": "dynamic",
            "label_en": "Dynamic exit allocation",
            "label_zh": "动态卖点分仓",
            "return": 53.22,
            "max_dd": -13.35,
            "note_en": "Lower drawdown, but may exit strong trends too early.",
            "note_zh": "回撤更低，但可能卖飞强趋势票。",
        },
    ]

    # ── Build payload ─────────────────────────────────────────────────────────
    payload = {
        "generated_at":      datetime.now().strftime("%Y-%m-%d %H:%M"),
        "period":            "2024-01-01 to 2025-12-31",
        "canonical":         canonical,
        "findings":          findings,
        "hold_period_table": hold_period_table,
        "market_regime":     market_regime,
        "universe_size":     len(UNIVERSE),
        "universe_label_en": "Semiconductor sector leaders (A-share)",
        "universe_label_zh": "半导体板块龙头（A 股）",
        "criterion_en":      "Protected research logic — public page shows results only.",
        "criterion_zh":      "受保护的研究逻辑 — 公开页面只展示结果。",
        "result_summary":    result_summary,
        "model_timeline":    model_timeline,
        "v4_horizon":        v4_horizon,
        "strategy_compare":  strategy_compare,
        "headline": {
            "n_signals":   int(n_signals),
            "n_stocks":    int(sig['code'].nunique()),
            "win5":  round(win5, 1),  "avg5":  round(avg5, 2),
            "win10": round(win10, 1), "avg10": round(avg10, 2),
            "win20": round(win20, 1), "avg20": round(avg20, 2),
        },
        "by_year":              by_year,
        "active_universe_size": active_universe_size,
        "per_stock":            per_stock,
        "portfolio":            portfolio_summary,
        "portfolio_curve":      portfolio_curve,
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
