# Private Analytics Backend

This folder contains the private visitor analytics backend for Erick Wei's
research site. It is designed for Cloudflare Workers + KV.

## What It Records

- Page views across the portfolio, Bean Model, and USD/CNY tracker pages.
- Named click events such as opening tools, downloads, language switches, and
  Bean Model random-case draws.
- Viewed sections via IntersectionObserver.
- Referrer host, viewport, browser language, anonymous browser session id.
- Visitor IP identity from Worker request headers.

If `STORE_RAW_IP=true`, the dashboard shows raw IP addresses. If it is false or
unset, the dashboard shows a short SHA-256 hash instead.

## Where The Owner Sees Data

After deployment, open:

```text
https://<your-worker-name>.<your-subdomain>.workers.dev/dashboard?token=<ADMIN_TOKEN>
```

The dashboard auto-refreshes every 20 seconds and shows:

- Unique sessions
- Top pages
- Top events
- Top viewed sections
- Top referrers
- Top IPs
- Recent events

The JSON API is:

```text
https://<your-worker-name>.<your-subdomain>.workers.dev/summary?token=<ADMIN_TOKEN>
```

## Deployment Checklist

1. Create a Cloudflare Worker.
2. Create a KV namespace and bind it as `ANALYTICS_KV`.
3. Add Worker environment variables:
   - `ADMIN_TOKEN`: a long private password/token.
   - `STORE_RAW_IP`: `true` if raw IP addresses should be stored.
4. Deploy `worker.js`.
5. Copy the collection endpoint:

```text
https://<your-worker-name>.<your-subdomain>.workers.dev/collect
```

6. Paste that endpoint into the `SITE_ANALYTICS_CONFIG.endpoint` value in:
   - `index.html`
   - `bean-model/index.html`
   - `privacy/index.html`
   - `../usdcny-tracker/docs/index.html`

Until the endpoint is filled, the frontend analytics scripts stay disabled and
do not send data.

## Frontend Disclosure

The public site includes a low-key footer `Privacy` link. Keep it small and
visually quiet, but do not remove it while collecting IP addresses.
