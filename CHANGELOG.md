# Portfolio Hub — Changelog

Personal research portfolio of **Erick Wei** (Columbia SIPA · International
Finance & Capital Markets). Hosted at **https://erickviann1-dev.github.io**.

> **For Cursor:** before any visual / design edit, read the design language
> in `../usdcny-tracker/docs/dashboard.js` header comment + the
> `REFERENCE_STUDY.md` in that repo. The portfolio sites must share the same
> editorial DNA: Source Serif 4 / Inter / JetBrains Mono · paper palette
> (`#faf8f5` bg, `#a16207` ochre, `#1e3a5f` navy, `#0c0a09` ink) · BIS
> Quarterly Review / FT longform aesthetic, NOT corporate dashboard.

---

## 🚧 Pending — v1.2 · "¥1,000,000 portfolio" — concrete-money UX

> Work order for Cursor. v1.1 fixed visual polish but the page still
> communicates in **abstract quant language** (win rate %, avg return %).
> Real visitors (recruiters, professors, friends) want a **landed, visceral
> story**: "if you started with ¥1,000,000 in Jan 2024 following this model,
> here's what your account looks like in Dec 2025." This is the standard
> Vanguard / Morningstar / Bridgewater public-facing pattern. v1.2 turns
> the abstract curve into a concrete-money equity story.

### Two distinct problems being fixed

#### A — The current equity curve is mathematically wrong
`bean-model/data.json:equity_curve` uses `cumprod(1 + ret10f/100)`. This
implicitly assumes **every signal uses the entire account balance**. Across
195 signals at +2.76% avg return, that compounds to ~210× —— absurd. Real
trading has overlapping positions; you cannot full-bet every signal.

**Fix:** rewrite as a proper portfolio simulation in `export_data.py`.

#### B — The communication layer is too abstract
"63.1% win rate" doesn't move anyone outside finance. "¥1,000,000 → ¥1.X M"
does. Headline + chart need to speak in concrete CNY.

### Specific edits

#### (1) `bean-model/export_data.py` — portfolio simulation rewrite

Replace the current `equity_curve` block with:

```python
INITIAL_CAPITAL = 1_000_000      # ¥1M starting balance
ALLOC_PER_SIGNAL = 100_000       # ¥100k per signal (10% notional)
HOLD_DAYS = 10                   # exit at signal_date + 10 trading days

# Build daily account-value series
sig_sorted = sig.sort_values('date').copy()
sig_sorted['date'] = pd.to_datetime(sig_sorted['date'])
sig_sorted['exit_date'] = sig_sorted['date'] + pd.tseries.offsets.BDay(HOLD_DAYS)
sig_sorted['pnl'] = ALLOC_PER_SIGNAL * sig_sorted['ret10f'] / 100.0

# Daily timeline from first signal to last exit
all_dates = pd.date_range(
    start=sig_sorted['date'].min(),
    end=sig_sorted['exit_date'].max(),
    freq='B'
)
account = pd.Series(INITIAL_CAPITAL, index=all_dates)

# Apply realized P&L on each exit date
exit_pnls = sig_sorted.groupby('exit_date')['pnl'].sum()
realized_cum = exit_pnls.reindex(all_dates, fill_value=0).cumsum()
account = INITIAL_CAPITAL + realized_cum

# Open positions count per day (for chart annotation, optional)
open_count = pd.Series(0, index=all_dates)
for _, row in sig_sorted.iterrows():
    open_count.loc[row['date']:row['exit_date']] += 1

portfolio_curve = [
    {"date": str(d.date()),
     "account": round(float(v), 2),
     "open_positions": int(open_count.loc[d])}
    for d, v in account.items()
]
```

Add to JSON payload:
```python
"portfolio": {
    "initial_capital": INITIAL_CAPITAL,
    "alloc_per_signal": ALLOC_PER_SIGNAL,
    "hold_days": HOLD_DAYS,
    "final_value": round(float(account.iloc[-1]), 2),
    "total_return_pct": round((account.iloc[-1] / INITIAL_CAPITAL - 1) * 100, 2),
    "peak_value": round(float(account.max()), 2),
    "trough_value": round(float(account.min()), 2),
    "max_drawdown_pct": round(((account / account.cummax() - 1).min()) * 100, 2),
    "max_drawdown_cny": round(float((account - account.cummax()).min()), 2),
    "n_winning_trades": int((sig_sorted['pnl'] > 0).sum()),
    "n_losing_trades":  int((sig_sorted['pnl'] <= 0).sum()),
    "best_trade_cny":   round(float(sig_sorted['pnl'].max()), 2),
    "worst_trade_cny":  round(float(sig_sorted['pnl'].min()), 2),
},
"portfolio_curve": portfolio_curve,
```

The legacy `equity_curve` field can stay (used by per-stock sparklines)
or be removed if nothing else references it.

#### (2) `bean-model/index.html` §2 — Concrete-money headline

**Replace** the v1.1 single-headline `63.1%` block with a "money story" hero:

```
┌──────────────────────────────────────────────────────────────┐
│                                                                │
│  ¥1,000,000          ──→          ¥1,540,000                  │
│  Jan 2024                          Dec 2025                   │
│                                                                │
│  +54.0% total · ¥540,000 P&L · max drawdown −¥83,000          │
│                                                                │
└──────────────────────────────────────────────────────────────┘
```

CSS: two giant ¥ numbers (96-112px JetBrains Mono 700-weight, color
`var(--ink)`) flanking a 32px ochre arrow. Below: 14px Inter caption with
the three secondary numbers (total return %, P&L in CNY, max DD in CNY).

i18n keys (EN + ZH):
- `portfolio.story_label` → "Portfolio simulation: ¥100k allocated per signal, 10-day hold" / "组合仿真：每笔信号分配 ¥10 万，持有 10 个交易日"
- `portfolio.from` → "Jan 2024" / "2024 年 1 月"
- `portfolio.to`   → "Dec 2025" / "2025 年 12 月"
- `portfolio.summary` → templated "+{X}% total · ¥{Y} P&L · max drawdown −¥{Z}"

The numbers come from `data.json:portfolio.{final_value, total_return_pct, max_drawdown_cny}`.

#### (3) `bean-model/index.html` Equity chart — relabel in CNY

The existing `Figure 2 · Cumulative equity` chart:

- **Data source change**: read `data.portfolio_curve` (not `equity_curve`)
- Y-axis tickformat: render values as `¥1.0M`, `¥1.2M`, `¥1.5M` style (use
  Plotly `tickformat: "~s"` with prefix `¥` via `tickprefix: "¥"`, or
  custom `text` array if `~s` doesn't render the M suffix correctly)
- Hover label: `¥1,234,567` formatted with thousand separators
- Title: "Figure 2 · ¥1,000,000 Portfolio Path" / "图二 · 100 万本金账户走势"
- Caption below:  "¥100k allocated per signal · 10-day hold · realized P&L
  applied at position close"
- ADD a thin horizontal reference line at `¥1,000,000` (initial capital,
  break-even) — `var(--rule)` 1px dashed
- ADD optional drawdown shading (filled area below cummax) in
  `rgba(185,28,28,0.05)` if you can do it in Plotly without complexity
  (skip if it's painful)

#### (4) Per-stock probe cards (§3) — optional CNY framing

If trivial: in each `.probe-card`, replace `+X.XX%` (avg10) with the
CNY-equivalent: `¥10,000 → ¥10,XXX` per signal-trade. Same data, different
framing. **Skip this if it requires adding new fields to per_stock JSON.**

If skipping: keep the % framing on cards but make sure the §2 headline
is the dominant visual element — that one carries the concrete-money story.

#### (5) Stat cards — reframe as "trade outcomes"

Replace v1.1's `[avg10 / win20 / avg20 / stocks-fired]` quartet with:

```
WINS               LOSSES             BEST TRADE         WORST TRADE
123 / 195          72 / 195           +¥18,400          −¥15,200
63%                37%                14 May 2025        02 Mar 2024
```

Where the dollar figures come from `data.json:portfolio.{best_trade_cny,
worst_trade_cny, n_winning_trades, n_losing_trades}`.

i18n keys: `stat.wins / stat.losses / stat.best / stat.worst` (replacing
the current `avg10 / win20 / avg20 / stocks fired`).

### Acceptance criteria

- [ ] `data.json` has top-level `portfolio` dict + `portfolio_curve` array
- [ ] §2 headline shows `¥1,000,000 → ¥X,XXX,XXX` story
- [ ] Equity chart Y-axis shows CNY values, not abstract `1.05` decimals
- [ ] Equity chart has horizontal break-even line at ¥1M
- [ ] 4 supporting stat cards reframed as trade outcomes (wins / losses / best / worst)
- [ ] EN/ZH symmetric (any new keys present in both dictionaries)
- [ ] Random-draw probe still works
- [ ] Sparklines still render
- [ ] No regression vs v1.1: chapter format / pull quote / disclaimer / footnote unchanged

### What NOT to change

- Per-stock JSON shape (`per_stock` array) — leave as-is
- Universe (25 semiconductor stocks) — fixed
- Sample period (2024-2025) — fixed
- Privacy contract — rule thresholds / IC / current-period signals stay hidden
- Hub `index.html` — out of scope
- Probe panel UX (random-draw button + cards + sparklines) — keep as v1.1

### Why this delivers what v1.1 didn't

v1.1 made the page **prettier**. v1.2 makes it **comprehensible to non-quants**.
Three failure modes v1.1 still has that v1.2 fixes:

1. **"63% win rate"** is a percentage. Recruiter doesn't know if that's
   good. **"¥1M → ¥1.54M in 24 months"** is unambiguously interesting.
2. The current cumprod equity curve is **mathematically dishonest** —
   reads as 200× total return. v1.2 portfolio sim is **realistic**.
3. **No drawdown felt**. Win rate hides the path. ¥1M dropping to ¥920k
   then climbing to ¥1.54M tells the *truth* about what holding the
   strategy felt like.

### Snapshot before edit

```bash
cp bean-model/index.html bean-model/index.v1.1.html.preserved
cp bean-model/data.json  bean-model/data.v1.1.json.preserved
cp bean-model/export_data.py bean-model/export_data.v1.1.py.preserved
```

### Commit + push when done

```bash
cd C:\Users\魏来\Desktop\山顶资本\portfolio-hub
python bean-model/export_data.py        # regenerate data.json
git add -A
git commit -m "feat: v1.2 — ¥1M portfolio simulation (concrete money story)"
git push
git tag v1.2 && git push --tags
```

Then update this CHANGELOG: replace the "🚧 Pending" header with
`[v1.2] — 2026-05-XX · ¥1,000,000 portfolio` followed by a Shipped table.

---

## [v1.1] — 2026-05-07 · Bean Model editorial redesign

> Delivered. `bean-model/index.html` upgraded to match tracker / hub editorial tier.
> All 8 items from the work order shipped; EN/ZH i18n symmetric (54 keys each);
> random-draw and sparkline functionality preserved. Tagged `v1.1`.

### Shipped

| # | Item | Result |
|---|---|---|
| 1 | Hero title | `clamp(44px, 6vw, 64px)` Source Serif 4 600, lh 1.08; `.hero-lead` + CSS `::first-letter` drop cap (64px ochre) |
| 2 | Chapter headings | `.chapter-head` 110px/1fr grid; `.chapter-num` 88px italic Source Serif 4 ochre; applied to §01/02/03 |
| 3 | §1 Methodology | 2 paragraphs flowing serif prose + JetBrains Mono method-box formula block + steps supplement + `⊘` privacy-note |
| 4 | §2 headline stat | Single 96–112px JetBrains Mono `63.1%` bull number + 4 supporting stats (avg10, win20, avg20, stocks fired) |
| 5 | Figure captions | Figure 1 · Annual breakdown + Figure 2 · Cumulative equity; source lines below each |
| 6 | Plotly styling | `plot_bgcolor / paper_bgcolor: #faf8f5`, gridcolor `#e8e4dc`, navy line `#1e3a5f`, mono hover |
| 7 | Pull quote | 22px Source Serif italic blockquote between §2 equity chart and §3; EN/ZH i18n (`quote.body` / `quote.cite`) |
| 8 | §3 probe cards | 5 × `.probe-card` with 28px mono stats + inline 60px Plotly sparkline (always rendered, no click-to-expand) |
| 9 | Draw button | Ochre outline style (was dark filled) |
| 10 | Disclaimer | `.research-footnote` with `†` dagger + centred `独立思考 · 明辨是非` italic closer; moved below §3 |
| 11 | Section spacing | 96px margin-top on each `.chapter-head` (was 56px) |

### Files touched

- `bean-model/index.html` — full editorial redesign (1,315 insertions / 404 deletions vs v1.0)
- `bean-model/index.v1.0.html.preserved` — v1.0 snapshot kept for diff / revert reference

---

### (archived) Specific edits — `bean-model/index.html`

#### (1) Hero block
- Title font: `clamp(44px, 6vw, 64px)` Source Serif 4 600-weight, line-height 1.08, letter-spacing -0.02em
- Add `.hero-overline` ABOVE title: small uppercase ochre eyebrow text (already partially there as `.eyebrow`, just enlarge contrast)
- Replace `.subtitle` with proper `.hero-lead` — first character gets `.drop-cap`:
  ```css
  .hero-lead .drop-cap {
      font-family: 'Source Serif 4', Georgia, serif;
      float: left;
      font-size: 64px;
      line-height: 0.9;
      font-weight: 600;
      color: var(--ochre);
      padding: 6px 10px 0 0;
      margin-top: 2px;
  }
  ```
- Lead text bilingual content (EN/ZH already in i18n; just expand to 3-4 lines instead of 1-2)

#### (2) Chapter heading upgrade
Replace existing `.section-head` styling with a tracker-equivalent:
```css
.chapter-head {
    display: grid;
    grid-template-columns: 110px 1fr;
    gap: 24px;
    align-items: baseline;
    margin: 96px 0 32px;
    border-bottom: 1px solid var(--rule);
    padding-bottom: 18px;
}
.chapter-num {
    font-family: 'Source Serif 4', serif;
    font-style: italic;
    font-size: 88px;
    font-weight: 400;
    color: var(--ochre);
    line-height: 0.85;
    letter-spacing: -0.04em;
}
.chapter-title-block .eyebrow { /* small ochre uppercase tag */ }
.chapter-title-block h2 {
    font-family: 'Source Serif 4', serif;
    font-size: 32px;
    font-weight: 600;
    letter-spacing: -0.01em;
    line-height: 1.15;
}
```
Apply to all three sections (§01, §02, §03).

#### (3) §1 Methodology — prose-first rewrite
Current: 1 short sentence + 5 bullets.

Target structure:
- 2 paragraphs of flowing serif prose (~120 words total) describing the IC discovery framework
- Then a `.method-box` with bordered formula block:
  ```
  ┌─ METHOD ─────────────────────────────────────┐
  │ DISCOVERY                                     │
  │                                               │
  │ For each indicator i:                         │
  │   IC_i  =  corr( indicator_i,  ret_{t→t+10} )│
  │                                               │
  │ Rank by |IC|, derive thresholds on 2023–24    │
  │ training set, validate on 2025+ test set.    │
  └───────────────────────────────────────────────┘
  ```
  Use JetBrains Mono inside the formula. Box: `.method-box` with ochre left border + ochre uppercase "METHOD" label.
- Then the 5-step list as a supplement, not the headline content
- "What's withheld" becomes a separate `.privacy-note` block at the end of §1 — same styling but with subtle warning tint and a `⊘` icon

#### (4) §2 Performance Proof — single-headline redesign
**Replace** the 6-card grid with this layout:

```
┌───────────────────────────────────────────────────┐
│                                                    │
│           63.1%                                    │
│           ────────                                 │
│           10-DAY WIN RATE                          │
│           195 trades · 2024–2025                   │
│                                                    │
│           +2.76%   59.0%   +4.89%   11/25         │
│           AVG 10D  WIN 20D  AVG 20D  STOCKS FIRED │
│                                                    │
└───────────────────────────────────────────────────┘
```
- Headline number: 96-120px JetBrains Mono 700-weight, color `var(--bull)` (`#15803d`)
- Underline: 60px ochre rule
- 4 supporting stats below in a clean horizontal row, each ~36px mono with small uppercase label

Replace year-by-year `<table>` with a "figure"-style block:
```
Figure 1 · Annual breakdown
  YEAR    SIGNALS    10D WIN    10D AVG
  2024       89        56.2%    +1.8%
  2025      106        68.9%    +3.5%
Source: bean_model.py backtest, semi-conductor universe (n=25), 2024–2025
```
Smaller figure caption above, source line below in 11px italic muted.

Equity curve gets `Figure 2 · Cumulative equity` framing + Plotly styling matching tracker:
- `plot_bgcolor: #faf8f5`, `paper_bgcolor: #faf8f5`
- gridcolor `#e8e4dc`, linecolor `#d4cec1`
- font family Inter 11px color `#57534e`
- line color `#1e3a5f` (navy), 2px stroke, low-opacity navy fill
- hover label dark ink with mono font

#### (5) NEW — Pull quote between §2 and §3
Insert after equity chart:
```html
<blockquote class="pullquote">
    <p>Test-set performance (2025: 68.9%) <em>exceeded</em> training-set performance (2024: 56.2%) — strong evidence the rules generalise rather than overfit.</p>
    <cite>— from the bean-model research log</cite>
</blockquote>
```
Style: 32px Source Serif italic, max-width 640px, centered, ochre vertical rule on left, `<cite>` in 12px uppercase tracking.

i18n keys `quote.body` / `quote.cite` (EN + ZH).

ZH version of the quote: "测试集表现（2025 · 68.9%）<em>超过</em>训练集表现（2024 · 56.2%）—— 这是规则可泛化、非过拟合的有力证据。"

#### (6) §3 Probe panel — card-based redesign
**Replace** the dense `.probe-row` table with 5 stacked **`.probe-card`** elements:
```
┌───────────────────────────────────────────────────┐
│  晶盛机电   300316             ↗                  │
│                                                    │
│   22 signals   86%   +6.26%                       │
│   ─────────  WIN     AVG 10D                      │
│                                                    │
│   ▁▁▂▃▅▆▇▆▅▄▃▂▁▁▂▃▄▅▇  ←  inline sparkline       │
│                                                    │
└───────────────────────────────────────────────────┘
```
- Card: white bg, hairline border, shadow-card, 24px padding
- Stock name in 18px Inter 600
- Code in 12px JetBrains Mono muted
- Three big stats inline: 32px mono numbers with small uppercase labels
- **Inline sparkline always rendered** (no click-to-expand) — small Plotly chart 60px tall, no axes, just the line
- Hover: lift 1px + shadow-lift
- Zero-signal stocks render as muted card with "NO SIGNAL FIRED" in 14px uppercase ochre

Draw button: ochre outline, 14px Inter 600, "Draw 5 random ↻" / "随机抽 5 只 ↻"

#### (7) Disclaimer — footnote treatment
Move to bottom of `<main>` (below §3, before footer). Styling:
```css
.research-footnote {
    margin-top: 64px;
    padding-top: 24px;
    border-top: 1px solid var(--rule);
    font-size: 12px;
    color: var(--muted);
    line-height: 1.7;
    font-family: 'Source Serif 4', Georgia, serif;
}
.research-footnote .dagger {
    color: var(--ochre);
    font-weight: 600;
    margin-right: 6px;
}
.research-footnote .closing {
    display: block;
    margin-top: 12px;
    font-style: italic;
    font-size: 14px;
    color: var(--ink-soft);
    text-align: center;
}
```
HTML:
```html
<aside class="research-footnote">
    <span class="dagger">†</span>
    [existing disclaimer text — sample-period limitation, withheld
    items, not investment advice]
    <span class="closing">独立思考 · 明辨是非</span>
</aside>
```
The "独立思考 · 明辨是非" closing line gets 14px Source Serif italic centred, slightly above muted color, with a 12px ochre `·` separator that's visually distinct.

#### (8) Section spacing
Find every `margin: 56px 0` or similar tight spacing — bump to 96px between major sections (`§01 → §02 → §03`). Keep tight spacing (24-32px) within sections.

### Acceptance criteria

- [ ] All chapter numbers render at 88px italic Source Serif (visually match tracker)
- [ ] Hero title is clearly larger than v1.0; drop cap visible on lead paragraph
- [ ] §2 has ONE huge headline number (`63.1%`), not 6 equal-weight cards
- [ ] Pull quote inserted between §2 equity curve and §3 probe
- [ ] §3 probe shows 5 large cards with inline sparklines, no click-to-expand needed
- [ ] Plotly charts use paper-bg + custom tick styling (no Plotly default white-bg)
- [ ] Disclaimer is footnote-style with `†` and centred 独立思考·明辨是非 closer
- [ ] Section spacing 96px between §01/§02/§03
- [ ] EN/ZH i18n still symmetric (no asymmetric keys)
- [ ] All v1.0 functionality preserved: random draw button works, sparklines render, language toggle works, data.json bindings unchanged
- [ ] Cache-bust if any: `<script src="...?v=1.1">` if the JS gets touched

### What NOT to change

- `bean-model/data.json` schema — JS bindings in `index.html` rely on it
- `bean-model/export_data.py` — the data pipeline is correct
- The 25-stock universe / 2024-2025 sample period / 195-signal headline numbers
- `assets/headshot.png`
- The hub `index.html` — only the bean-model page is in scope for v1.1
- The "What's withheld" privacy contract — rule thresholds, IC values, current-period signals stay hidden

### Snapshot before edit
```bash
cp bean-model/index.html bean-model/index.v1.0.html.preserved
```
(Keep around for diff / revert reference.)

### Commit + push when done
```bash
git add -A
git commit -m "design: v1.1 bean-model editorial upgrade (chapter format, headline number, pull quote, probe cards, footnote disclaimer)"
git push
```
Tag if you want: `git tag v1.1 && git push --tags`

---

## [v1.0] — 2026-05-07 · Initial deployment

### Shipped
- **Hub** (`index.html`) at `https://erickviann1-dev.github.io`
  - Headshot avatar (assets/headshot.png)
  - Bilingual bio (Erick Wei · Columbia SIPA · International Finance)
  - 2 tools cards: USD/CNY Tracker (live), Bobo Bean Model
  - 1 paper card: Warsh QT & RMB Opportunity (SSRN abstract=6645380)
  - Contact cards: Email (lw3170@columbia.edu), LinkedIn (in/laiwei)
  - EN/ZH language toggle, localStorage persistence
- **Bean Model page** (`bean-model/index.html`)
  - Methodology section (high-level only — rule thresholds withheld)
  - Performance Proof: 195 signals, 63.1% 10d win rate, +2.76% avg, 2024-2025
  - Annual breakdown table
  - Cumulative equity curve (Plotly)
  - Random-sample probe (draw 5 from 25-stock semi universe)
  - Click-to-expand mini equity charts per stock
  - Disclaimer with "独立思考 · 明辨是非" closing
- **Bean Model data pipeline** (`bean-model/export_data.py`)
  - Reads from `量化/全部数据/bobo1号模型/semi_backtest_signals.csv`
  - Filters to 2024-2025 only (current period stays private)
  - Outputs aggregated per-stock + headline + equity curve to `data.json`
  - 25-stock universe extracted from `量化/semi_backtest.py`
- **Privacy contract**:
  - 6 rule thresholds NOT public
  - 20-indicator IC values NOT public
  - 2026+ signals NOT public
  - Indicator readings on individual trigger dates NOT public
  - Public: universe membership, aggregate per-stock stats (signals, win rate, avg return), period boundaries

### Files Touched
- `index.html` — full hub page
- `assets/headshot.png` — author photo (1.7 MB)
- `bean-model/index.html` — bean-model demo page
- `bean-model/data.json` — backtest aggregate JSON (~19 KB)
- `bean-model/export_data.py` — data export script

### Cross-links
- Hub → USD/CNY tracker: `https://erickviann1-dev.github.io/usdcny-tracker/`
- Hub → Bean Model: `bean-model/` (subdirectory)
- Bean Model → Hub: "← Back to portfolio" link in topbar

### Known limitations (carrying into v1.1+)
- Bean Model page visual quality below tracker / hub tier (addressed in v1.1)
- No proper paper PDF for bean-model methodology yet (separate v2 task)
- Disclaimer line "独立思考 · 明辨是非" is a footnote-style closing, intentional

---

## Design language reference

The portfolio sites are designed as a single editorial system. All three
sites (hub, USD/CNY tracker, bean-model) share these tokens:

```
COLORS
  bg:        #faf8f5  (paper)
  bg-tint:   #f5f2ec  (recessed)
  card:      #ffffff
  hairline:  #e8e4dc
  rule:      #d4cec1  (heavier hairline)
  ink:       #0c0a09
  ink-soft:  #292524
  muted:     #57534e
  navy:      #1e3a5f  (data lines, links)
  ochre:     #a16207  (eyebrow tags, accents)
  bull:      #15803d
  bear:      #b91c1c

TYPOGRAPHY
  Display:  Source Serif 4 (chapter numbers, titles, pull quotes)
  Body:     Inter (paragraphs, UI)
  Numbers:  JetBrains Mono (stats, formulas, codes)

SPACING
  Section gap:   96px between major chapters
  Card gap:      20-24px in grids
  Reading width: max 720px for body prose

REFERENCE LOOK
  → BIS Quarterly Review (overall layout)
  → Financial Times longform (drop cap, pull quote)
  → AQR / Two Sigma research papers (formula blocks, figure captions)
  → NOT: Streamlit demo, Bloomberg Terminal, generic SaaS dashboard
```

If a proposed edit makes the site look more like a "Streamlit demo" and
less like a "BIS Quarterly Review article", **don't do it**.
