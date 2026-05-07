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

## 🚧 Pending — v1.1 · Bean Model editorial redesign

> Work order for Cursor. The bean-model page (`bean-model/index.html`) shipped
> in v1.0 is **functionally complete but visually a step below** the hub
> (`index.html`) and the USD/CNY tracker. It reads as a "data dashboard"
> rather than a "research artifact". This patch brings it up to the same
> editorial tier.

### Diagnosis (what's wrong with the v1.0 bean-model page)

| Element | Tracker / Hub level | Current bean-model | Action |
|---|---|---|---|
| Chapter numbers | 88px italic Source Serif 4 | 28px regular | **Upgrade to 88px italic** |
| Hero title | 48–72px display serif | clamp(32, 4.5vw, 44) | **Bump to clamp(44, 6vw, 64)** |
| Hero lead paragraph | FT-style drop cap | Plain `<p>` | **Add `.drop-cap` first-letter** |
| Pull quote | Big italic serif callout | Absent | **Add one between §2 and §3** |
| Method box | Bordered box with JetBrains-Mono formula | `<ul>` inside a tinted box | **Reformat as proper `.method-box` w/ formula block** |
| Headline stats | Single hero number + supporting stats | 6 generic stat cards | **Re-do as ONE huge headline number + 4 supporting cards** |
| Charts | Tufte minimal, paper-bg, custom tick fonts | Plotly defaults | **Apply tracker's chart styling tokens** |
| §1 Methodology | Flowing serif prose + numbered list | Bullet list only | **Rewrite as 2 paragraphs of serif prose, list as supplement** |
| §3 Probe panel | (n/a — bespoke) | Dense table rows | **Redesign as 5 large cards w/ inline sparkline** |
| Disclaimer | Footnote style w/ `†` mark | Plain italic block | **Reformat as proper research-footnote block** |
| Section spacing | 96px between major chapters | 56px | **Increase to 96px** |
| Plotly chart figures | Figure 1 label + source line | None | **Add figure caption + source attribution** |

### Specific edits — `bean-model/index.html`

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
