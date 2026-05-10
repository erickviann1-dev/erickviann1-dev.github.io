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

## [snapshot-web-v1.5.1] — 2026-05-10 · Stable online rollback point

> Current preserved web version. Use this as the rollback anchor if later Bean
> Model / portfolio hub edits break the page, weaken the design, or muddle the
> model narrative.

- Git commit: `17fda5a`
- Git tag: `web-v1.5.1-v4s-evidence`
- Live page: `https://erickviann1-dev.github.io/bean-model/`
- Key state preserved: v4 framework explanation, v4.S empirical evidence card,
  corrected v3.1 metric provenance, protected-method wording, DB4 random draw
  interaction, and portfolio hub navigation.
- Rollback command:

```bash
git checkout web-v1.5.1-v4s-evidence
```

- If restoring `main` to this version:

```bash
git checkout main
git reset --hard web-v1.5.1-v4s-evidence
git push --force-with-lease origin main
```

---

## [v1.5] — 2026-05-10 · Bean Model protected-results interactive page

> Delivered. Bean Model page reframed from a methodology explainer into a
> protected research-results showcase. Public page now emphasizes outcome
> evidence, account curves, random controls, and research discipline while
> withholding replicable stock-selection logic.

### Shipped

| # | Item | Result |
|---|---|---|
| 1 | Public positioning | Hero rewritten: not a public stock picker, not a miracle prediction engine; it is a validated technology-stock trading research system. |
| 2 | Privacy boundary | Added explicit research-boundary block: no rules, thresholds, IC ranks, live signals, current picks, trigger dates, or factor readings. |
| 3 | Result strip | First-screen evidence chips: v2 ~68% large-sample win rate, v4.S 92.86% historical win rate, fixed allocation +70.31%, rules protected. |
| 4 | Model arc | Added v2 → v3.1 → v4 → Exit timeline; only explains version purpose and public conclusions, not implementation. |
| 4.1 | Model distinction | Expanded model arc to explain v2 vs v3.1 vs v4: original buy signal, locked anti-overfitting discipline, then tiered technology-mainline framework. |
| 4.2 | v4 horizon progression | Added v4 short / medium / long-horizon cards showing improvement trend: 10-20D validation, 60-90D trend expression, 120D v4.S strict long-horizon layer. |
| 4.3 | Regime-adapted view | Figure B now shows the model/horizon adapted to each market regime; 2025 uses v4 medium-term and 2026 uses v4.S 120D instead of the old fixed v3.1 10D lens. |
| 4.4 | v4 spotlight | Added a dedicated public v4 explanation block before the empirical section: v4.A short-horizon validation, v4.B observation layer, v4.S strict long-horizon layer. Wording explains the framework without exposing rules, thresholds, factor values, or live candidates. |
| 4.5 | Metric provenance fix | Corrected the v3.1 headline card: 88.5% is from 52 completed 80D signals; 1,199 is the broader DB3-500 background scan, not the denominator for the 80D result. |
| 4.6 | v4 empirical card | Added a v4.S evidence card at the start of the empirical section: 120D win rate 92.86%, average return +59.44%, median return +46.62%, 14 strict historical cases. This makes v4 the current model evidence while v3.1 remains the foundation / hold-period discovery. |
| 5 | Alpha/Beta comparison | Added v4.S vs random technology basket comparison: win rate, average return, median return. |
| 6 | Holding-style interaction | Added interactive tabs for fixed holding allocation vs dynamic exit allocation: return, drawdown, interpretation. |
| 7 | Historical sample draw | Random historical probe displays delayed DB4 stock names/codes after owner approval, while keeping signal logic private. |
| 7.1 | Source-data privacy | `data.json` exports historical DB4 stock names/codes plus aggregate 120D outcomes and price curves, but no trigger dates, factor readings, thresholds, or live candidates. |
| 7.2 | DB4 random 50 upgrade | Interactive draw now uses 50 randomly sampled technology stocks from DB4 random universe, with historical stock names/codes allowed by owner approval. |
| 7.3 | Timeline comparison | Added a 5-stock normalized price timeline with range tabs: 2025-2026 full, 2025 H1, 2025 H2, 2026. |
| 8 | Data contract | `data.json` / `export_data.py` now include `result_summary`, `model_timeline`, and `strategy_compare`; `criterion_*` changed to protected-language placeholders. |

### Public numbers now used

| Metric | Public display |
|---|---:|
| v2 large-sample win rate | ~68% |
| v4.S historical win rate | 92.86% |
| v4.S average return | +59.44% |
| v4.S median return | +46.62% |
| v4 short-term layer | 10-20D · 73.33% win · +4.76% avg |
| v4 medium-term layer | 60-90D · 81.25% win · +31.91% avg |
| v4 strict long-horizon layer | 120D v4.S · 92.86% win · +59.44% avg |
| Figure B 2025 adapted view | v4 medium-term · 60-90D win 81.25% |
| Figure B 2026 adapted view | v4.S strict layer · 120D win 92.86% |
| Random tech basket win rate | ~78% |
| Random tech basket average return | ~42% |
| Random tech basket median return | ~23% |
| Fixed holding allocation | +70.31%, max drawdown -20.92% |
| Dynamic exit allocation | +53.22%, max drawdown -13.35% |

### Privacy contract

- Do not publish v2/v3.1/v4 rules or thresholds.
- Do not publish IC ranking, factor weights, factor values, or trigger logic.
- Do not publish current-year live signals, current candidates, or current holdings.
- Historical interactive cards must remain delayed and anonymized unless explicitly approved.
- Historical DB4 random stock names/codes may be shown in the public interaction by owner approval.
- Do not publish trigger dates, factor readings, model thresholds, current candidates, or live signal lists.
- The page may show aggregate result quality, account-level performance, drawdown, random comparison, and research limitations.

### Snapshot before edit

Saved before this change:

```text
history/v1.5-pre-results-interactive-20260510-112816/
```

### Verification

- `bean-model/data.json` parsed successfully with new public result fields.
- Embedded page script compiled successfully with Node `vm.Script`.
- EN/ZH i18n references checked: 66 references, 0 missing keys.
- Python was not available in this shell as `python` or `py`, so `export_data.py`
  was not executed here. `data.json` was patched directly and the export script
  was updated so Cursor can regenerate the same fields later.
- In-app browser preview could not be completed because the browser runtime hit a
  local Windows permission error; no page-code syntax errors were found in static checks.

### Files touched

- `bean-model/index.html`
- `bean-model/export_data.py`
- `bean-model/data.json`
- `CHANGELOG.md`

---

## [v1.2] — 2026-05-07 · Bean Model ¥1,000,000 portfolio simulation

> Delivered. Portfolio simulation replaces the v1.0/v1.1 cumprod equity curve with a
> real ¥-denominated account model. §2 hero reframed as a "¥1M → ¥1.54M" story.
> EN/ZH i18n symmetric (63 keys each). Tagged `v1.2`.

### Shipped

| # | Item | Result |
|---|---|---|
| 1 | `export_data.py` rewrite | `PRINCIPAL = ¥1,000,000`, `POSITION = ¥100,000` per signal · cumsum P&L · produces `portfolio` summary + `portfolio_curve` |
| 2 | `data.json` new fields | `portfolio` (final_value, total_pnl, total_return_pct, n_wins, n_losses, best/worst_trade_pnl, max_drawdown_pct/cny) + `portfolio_curve` [{date, value}] |
| 3 | §2 hero | `¥1,000,000 → ¥1.54M` story: two 52–96px JetBrains Mono numbers + 32px ochre arrow + caption (total return / P&L / max drawdown) |
| 4 | §2 supporting cards | WINS (123) / LOSSES (72) / BEST TRADE (+¥47,952) / WORST TRADE (−¥28,670) |
| 5 | Equity chart | Y-axis: `¥1.0M / ¥1.2M / ¥1.5M` dynamic ticks · dashed reference line at ¥1,000,000 with BREAKEVEN label · data source: `portfolio_curve` |
| 6 | Sparklines | Updated to use `portfolio_curve` + `p.value` field |
| 7 | i18n | 9 new keys added symmetrically (EN/ZH 54 → 63 each): `s2.sup_wins/losses/best/worst`, `s2.portfolio_return/pnl/dd_label`, `s2.breakeven_label`, updated `s2.figure2_caption` |

### Portfolio simulation output (2024–2025 · 195 signals)

| Metric | Value |
|---|---|
| Initial capital | ¥1,000,000 |
| Position size | ¥100,000 per signal |
| Final value | **¥1,537,416** |
| Total P&L | +¥537,416 (+53.74%) |
| Wins / Losses | 123 / 72 |
| Best single trade | +¥47,952 |
| Worst single trade | −¥28,670 |
| Max drawdown | 9.79% / ¥107,398 |

### Files touched

- `bean-model/export_data.py` — portfolio simulation rewrite
- `bean-model/data.json` — added `portfolio` + `portfolio_curve` fields
- `bean-model/index.html` — §2 hero, equity chart, sparklines, i18n (9 new keys)

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
