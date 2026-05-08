// gen_portfolio.js
// From the cumprod equity_curve, back-derive individual trade returns,
// then compute a real ¥-denominated portfolio curve.
//
// Simulation spec:
//   Principal  : ¥1,000,000
//   Per signal : ¥100,000  (10% of principal, fixed notional)
//   Realize    : exit day P&L = position × ret10f/100
//   Curve      : portfolio_value[i] = principal + cumsum(pnl[i])
//
// equity_curve is sorted by signal date.
// equity[0]   = 1 + ret10f_0/100
// equity[i]   = equity[i-1] × (1 + ret10f_i/100)
// => ret10f_i/100 = equity[i] / equity[i-1] - 1  (i > 0)
//                 = equity[0] - 1                  (i = 0)

'use strict';
const fs   = require('fs');
const path = require('path');

const DST = path.join(__dirname, 'bean-model', 'data.json');
const data = JSON.parse(fs.readFileSync(DST, 'utf8'));

const PRINCIPAL = 1_000_000;
const POSITION  = 100_000;

const curve = data.equity_curve;
if (!curve || curve.length === 0) {
    console.error('No equity_curve found in data.json');
    process.exit(1);
}

// --- Back-derive per-signal returns ---
const signals = [];
for (let i = 0; i < curve.length; i++) {
    const eq  = curve[i].equity;
    const ret = i === 0 ? (eq - 1) : (eq / curve[i - 1].equity - 1);
    const pnl = POSITION * ret;
    signals.push({ date: curve[i].date, ret, pnl });
}

// --- Build portfolio curve ---
let portfolioValue = PRINCIPAL;
let maxValue       = PRINCIPAL;
let maxDrawdownAbs = 0;   // in ¥
let maxDrawdownPct = 0;   // as fraction
let nWins    = 0, nLosses = 0;
let bestPnl  = -Infinity;
let worstPnl =  Infinity;

const portfolioCurve = [];

for (const s of signals) {
    portfolioValue += s.pnl;

    if (portfolioValue > maxValue) maxValue = portfolioValue;
    const ddAbs = maxValue - portfolioValue;
    const ddPct = maxValue > 0 ? ddAbs / maxValue : 0;
    if (ddAbs > maxDrawdownAbs) maxDrawdownAbs = ddAbs;
    if (ddPct > maxDrawdownPct) maxDrawdownPct = ddPct;

    if (s.pnl > 0)  nWins++;
    else             nLosses++;

    if (s.pnl > bestPnl)  bestPnl  = s.pnl;
    if (s.pnl < worstPnl) worstPnl = s.pnl;

    portfolioCurve.push({
        date:  s.date,
        value: Math.round(portfolioValue * 100) / 100,
    });
}

const totalPnl       = portfolioValue - PRINCIPAL;
const totalReturnPct = totalPnl / PRINCIPAL * 100;

const portfolio = {
    principal:          PRINCIPAL,
    position_size:      POSITION,
    final_value:        Math.round(portfolioValue * 100) / 100,
    total_pnl:          Math.round(totalPnl       * 100) / 100,
    total_return_pct:   Math.round(totalReturnPct * 100) / 100,
    n_wins:             nWins,
    n_losses:           nLosses,
    best_trade_pnl:     Math.round(bestPnl  * 100) / 100,
    worst_trade_pnl:    Math.round(worstPnl * 100) / 100,
    max_drawdown_pct:   Math.round(maxDrawdownPct * 10000) / 100,   // e.g. 12.34
    max_drawdown_cny:   Math.round(maxDrawdownAbs),
};

data.portfolio       = portfolio;
data.portfolio_curve = portfolioCurve;

fs.writeFileSync(DST, JSON.stringify(data, null, 2), 'utf8');

// --- Report ---
const fmt = (n) => n.toLocaleString('en-US', { maximumFractionDigits: 0 });
const pct = (n) => n.toFixed(2) + '%';
console.log('=== Portfolio simulation ===');
console.log(`  Principal   : ¥${fmt(PRINCIPAL)}`);
console.log(`  Position    : ¥${fmt(POSITION)} per signal`);
console.log(`  Signals     : ${signals.length}`);
console.log(`  Wins/Losses : ${nWins} / ${nLosses}`);
console.log(`  Final value : ¥${fmt(portfolioValue)}`);
console.log(`  Total P&L   : ¥${fmt(totalPnl)}   (${pct(totalReturnPct)})`);
console.log(`  Best trade  : ¥${bestPnl .toFixed(2)}`);
console.log(`  Worst trade : ¥${worstPnl.toFixed(2)}`);
console.log(`  Max drawdown: ${pct(maxDrawdownPct * 100)} / ¥${fmt(maxDrawdownAbs)}`);
console.log(`  Written to  : ${DST}`);
