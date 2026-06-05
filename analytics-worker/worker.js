/*
 * Erick Wei research-site analytics worker.
 *
 * Deploy target: Cloudflare Workers + KV.
 *
 * Required bindings / vars:
 * - ANALYTICS_KV: KV namespace binding
 * - ADMIN_TOKEN: secret token for /dashboard and /summary
 * - STORE_RAW_IP: "true" to store raw IP strings; anything else stores a hash
 *
 * Routes:
 * - POST /collect
 * - GET  /dashboard?token=ADMIN_TOKEN
 * - GET  /summary?token=ADMIN_TOKEN
 */

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
};

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS });
    }

    if (url.pathname === "/collect" && request.method === "POST") {
      return collect(request, env);
    }

    if (url.pathname === "/summary" && request.method === "GET") {
      if (!authorized(url, env)) return json({ error: "unauthorized" }, 401, CORS);
      return json(await buildSummary(env), 200, CORS);
    }

    if (url.pathname === "/dashboard" && request.method === "GET") {
      if (!authorized(url, env)) return html(loginPage(url));
      return html(dashboardPage(url.searchParams.get("token") || ""));
    }

    return new Response("Not found", { status: 404 });
  },
};

async function collect(request, env) {
  let body;
  try {
    body = await request.json();
  } catch (_) {
    return json({ ok: false, error: "bad_json" }, 400, CORS);
  }

  const now = new Date();
  const day = now.toISOString().slice(0, 10);
  const hour = now.toISOString().slice(0, 13);
  const site = clean(body.site || "unknown", 60);
  const event = clean(body.event || "event", 80);
  const path = clean(body.path || "/", 180);
  const section = clean((body.props && body.props.section) || "", 80);
  const ref = clean(body.referrer_host || "direct", 120) || "direct";
  const lang = clean(body.lang || "", 24);
  const viewport = clean(body.viewport || "", 24);
  const session = clean(body.session_id || "no_session", 80);
  const ip = clientIp(request);
  const ipKey = await ipIdentity(ip, env);

  await Promise.all([
    inc(env, `count:${site}:day:${day}:event:${event}`),
    inc(env, `count:${site}:day:${day}:path:${path}`),
    inc(env, `count:${site}:day:${day}:ref:${ref}`),
    inc(env, `count:${site}:hour:${hour}:event:${event}`),
    section ? inc(env, `count:${site}:day:${day}:section:${section}`) : null,
    inc(env, `count:${site}:day:${day}:ip:${ipKey}`),
    env.ANALYTICS_KV.put(`visit:${site}:${day}:${session}`, "1", { expirationTtl: 60 * 60 * 24 * 45 }),
    env.ANALYTICS_KV.put(`last:${site}:${Date.now()}:${Math.random().toString(36).slice(2)}`, JSON.stringify({
      ts: now.toISOString(),
      site,
      event,
      path,
      section,
      referrer_host: ref,
      lang,
      viewport,
      ip: ipKey,
    }), { expirationTtl: 60 * 60 * 24 * 14 }),
  ].filter(Boolean));

  return json({ ok: true }, 200, CORS);
}

function authorized(url, env) {
  const token = url.searchParams.get("token") || "";
  return env.ADMIN_TOKEN && token === env.ADMIN_TOKEN;
}

function clientIp(request) {
  return request.headers.get("CF-Connecting-IP")
    || request.headers.get("X-Forwarded-For")
    || request.headers.get("X-Real-IP")
    || "unknown";
}

async function ipIdentity(ip, env) {
  if ((env.STORE_RAW_IP || "").toLowerCase() === "true") return ip;
  const enc = new TextEncoder();
  const digest = await crypto.subtle.digest("SHA-256", enc.encode(String(ip)));
  const bytes = Array.from(new Uint8Array(digest));
  return "sha256:" + bytes.map(b => b.toString(16).padStart(2, "0")).join("").slice(0, 24);
}

function clean(value, maxLen) {
  return String(value == null ? "" : value)
    .replace(/[\u0000-\u001f\u007f]/g, "")
    .slice(0, maxLen);
}

async function inc(env, key) {
  const current = parseInt(await env.ANALYTICS_KV.get(key) || "0", 10);
  await env.ANALYTICS_KV.put(key, String(current + 1), { expirationTtl: 60 * 60 * 24 * 90 });
}

async function scan(env, prefix, limit = 1000) {
  let cursor;
  const rows = [];
  do {
    const res = await env.ANALYTICS_KV.list({ prefix, cursor, limit: 1000 });
    for (const key of res.keys) {
      rows.push({ key: key.name, value: parseInt(await env.ANALYTICS_KV.get(key.name) || "0", 10) });
      if (rows.length >= limit) return rows;
    }
    cursor = res.cursor;
  } while (cursor);
  return rows;
}

async function scanRaw(env, prefix, limit = 1000) {
  let cursor;
  const rows = [];
  do {
    const res = await env.ANALYTICS_KV.list({ prefix, cursor, limit: 1000 });
    for (const key of res.keys) {
      rows.push({ key: key.name, value: await env.ANALYTICS_KV.get(key.name) });
      if (rows.length >= limit) return rows;
    }
    cursor = res.cursor;
  } while (cursor);
  return rows;
}

async function buildSummary(env) {
  const days = [...Array(14)].map((_, i) => {
    const d = new Date(Date.now() - i * 86400000);
    return d.toISOString().slice(0, 10);
  }).reverse();

  const all = await scan(env, "count:", 5000);
  const visitRows = await scanRaw(env, "visit:", 5000);
  const recentRows = await scanRaw(env, "last:", 120);

  return {
    generated_at: new Date().toISOString(),
    last_14_days: days,
    unique_sessions: visitRows.length,
    top_pages: topByType(all, "path", 20),
    top_events: topByType(all, "event", 30),
    top_sections: topByType(all, "section", 30),
    top_referrers: topByType(all, "ref", 20),
    top_ips: topByType(all, "ip", 30),
    recent: recentRows
      .map(row => {
        try { return JSON.parse(row.value); }
        catch (_) { return { ts: "", site: "", event: "bad_recent_row", path: row.key, ip: "" }; }
      })
      .sort((a, b) => String(b.ts || "").localeCompare(String(a.ts || "")))
      .slice(0, 40),
  };
}

function topByType(rows, type, limit) {
  const map = new Map();
  for (const row of rows) {
    const parts = row.key.split(":");
    const idx = parts.indexOf(type);
    if (idx < 0) continue;
    const name = parts.slice(idx + 1).join(":");
    map.set(name, (map.get(name) || 0) + row.value);
  }
  return [...map.entries()]
    .map(([name, count]) => ({ name, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, limit);
}

function json(obj, status = 200, headers = {}) {
  return new Response(JSON.stringify(obj, null, 2), {
    status,
    headers: { "Content-Type": "application/json; charset=utf-8", ...headers },
  });
}

function html(body) {
  return new Response(body, {
    headers: { "Content-Type": "text/html; charset=utf-8" },
  });
}

function loginPage(url) {
  return `<!doctype html><meta charset="utf-8"><title>Analytics Login</title>
  <body style="font-family:Inter,system-ui;padding:40px;background:#faf8f5;color:#0c0a09">
  <h1>Analytics Dashboard</h1>
  <p>Add <code>?token=ADMIN_TOKEN</code> to the URL.</p>
  <p>Current path: <code>${escapeHtml(url.pathname)}</code></p></body>`;
}

function dashboardPage(token) {
  return `<!doctype html>
<html lang="en">
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Erick Wei - Site Analytics</title>
<style>
body{margin:0;background:#faf8f5;color:#0c0a09;font-family:Inter,system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
main{max-width:1260px;margin:0 auto;padding:42px 24px 80px}
h1{font-family:Georgia,serif;font-size:44px;margin:0 0 8px}
.muted{color:#78716c}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin-top:28px}
.card{background:#fffdf9;border:1px solid #e7dfd3;border-radius:8px;padding:20px;box-shadow:0 10px 30px rgba(28,25,23,.06)}
table{width:100%;border-collapse:collapse;font-size:13px}td,th{padding:8px;border-bottom:1px solid #eee7dc;text-align:left;vertical-align:top}td:last-child,th:last-child{text-align:right;font-family:"JetBrains Mono",monospace}
.kpi{display:flex;gap:18px;margin:24px 0}.kpi div{background:#fffdf9;border:1px solid #e7dfd3;padding:16px 18px;border-radius:8px}.kpi strong{font-size:26px}
.wide{grid-column:1/-1}.toolbar{display:flex;justify-content:space-between;gap:12px;align-items:center;margin-top:14px}.pill{font-family:"JetBrains Mono",monospace;font-size:11px;color:#1e3a5f;border:1px solid #d4cec1;border-radius:999px;padding:5px 9px}
@media(max-width:760px){.grid{grid-template-columns:1fr}h1{font-size:34px}}
</style>
<main>
<h1>Site Analytics</h1>
<p class="muted">Private dashboard - page views, events, sections, referrers, and visitor IP identities.</p>
<div class="toolbar"><span class="pill">auto refresh - 20s</span><span class="muted" id="status">loading</span></div>
<div class="kpi"><div><span class="muted">Unique Sessions</span><br><strong id="sessions">-</strong></div><div><span class="muted">Updated</span><br><strong id="updated">-</strong></div></div>
<div class="grid">
  <div class="card"><h2>Top Pages</h2><table id="pages"></table></div>
  <div class="card"><h2>Top Events</h2><table id="events"></table></div>
  <div class="card"><h2>Top Sections</h2><table id="sections"></table></div>
  <div class="card"><h2>Top Referrers</h2><table id="refs"></table></div>
  <div class="card"><h2>Top IPs</h2><table id="ips"></table></div>
  <div class="card wide"><h2>Recent Events</h2><table id="recent"></table></div>
</div>
</main>
<script>
const token = ${JSON.stringify(token)};
function rows(id, data) {
  document.getElementById(id).innerHTML = '<tr><th>Name</th><th>Count</th></tr>' +
    (data || []).map(r => '<tr><td>' + escapeHtml(r.name) + '</td><td>' + r.count + '</td></tr>').join('');
}
function recentRows(data) {
  document.getElementById('recent').innerHTML = '<tr><th>Time</th><th>Site</th><th>Event</th><th>Path</th><th>Section</th><th>IP</th></tr>' +
    (data || []).map(r => '<tr><td>' + escapeHtml(r.ts ? new Date(r.ts).toLocaleString() : '') + '</td><td>' + escapeHtml(r.site) + '</td><td>' + escapeHtml(r.event) + '</td><td>' + escapeHtml(r.path) + '</td><td>' + escapeHtml(r.section || '') + '</td><td>' + escapeHtml(r.ip || '') + '</td></tr>').join('');
}
function escapeHtml(s){return String(s).replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[m]));}
async function load() {
  document.getElementById('status').textContent = 'refreshing';
  const d = await fetch('/summary?token=' + encodeURIComponent(token), { cache: 'no-store' }).then(r=>r.json());
  document.getElementById('sessions').textContent = d.unique_sessions || 0;
  document.getElementById('updated').textContent = new Date(d.generated_at).toLocaleString();
  rows('pages', d.top_pages); rows('events', d.top_events); rows('sections', d.top_sections);
  rows('refs', d.top_referrers); rows('ips', d.top_ips); recentRows(d.recent);
  document.getElementById('status').textContent = 'live';
}
load().catch(e => { document.getElementById('status').textContent = 'error: ' + e.message; });
setInterval(() => load().catch(()=>{}), 20000);
</script>
</html>`;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, m => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;",
  }[m]));
}
