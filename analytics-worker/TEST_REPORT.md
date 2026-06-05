# Analytics Test Report

Date: 2026-06-04

## Local Structural Tests

Portfolio hub:

- PASS `assets/site-analytics.js` exposes `window.siteTrack`.
- PASS `privacy/index.html` discloses visitor IP address collection.
- PASS `analytics-worker/worker.js` includes `/collect`, `/dashboard`, and
  `/summary` routes.
- PASS Worker supports `STORE_RAW_IP`.
- PASS Worker reads `CF-Connecting-IP`.
- PASS Worker dashboard auto-refreshes every 20 seconds.
- PASS `index.html` includes `SITE_ANALYTICS_CONFIG`.
- PASS homepage footer includes quiet `Privacy` link.
- PASS `bean-model/index.html` includes `SITE_ANALYTICS_CONFIG`.
- PASS Bean Model random draw records `bean_draw_cases`.
- PASS Bean Model footer includes quiet `Privacy` link.
- PASS README documents the private dashboard URL format.

USD/CNY tracker:

- PASS `docs/site-analytics.js` exposes `window.siteTrack`.
- PASS `docs/index.html` includes `SITE_ANALYTICS_CONFIG`.
- PASS tracker footer links to the portfolio privacy notice.
- PASS CSV / JSON / Excel / notebook download buttons have named tracking.
- PASS language switch tracking only fires on user click.

## Runtime Tests

Blocked in the current local environment:

- `node --check` cannot run because `node.exe` returns `Access is denied`.
- `wrangler`, `npm`, `npx`, `deno`, `bun`, `python`, and `py` are unavailable.
- No Cloudflare credentials or local Wrangler login state were found.

## Deployment State

Analytics backend is live.

Cloudflare Worker:

```text
https://erick-site-analytics.erickviann1.workers.dev
```

Collect endpoint:

```text
https://erick-site-analytics.erickviann1.workers.dev/collect
```

Owner dashboard:

```text
https://erick-site-analytics.erickviann1.workers.dev/dashboard?token=<ADMIN_TOKEN>
```

The real `ADMIN_TOKEN` is stored only in `.env.deploy.local`, which is ignored
by git.

## Live Smoke Test

PASS:

- Dashboard returned HTTP 200.
- `/collect` accepted a synthetic `deployment-test` page view.
- `/summary` returned `unique_sessions >= 1`.
- `/summary.top_pages` included `/codex-test`.
- Recent event was `page_view`.
