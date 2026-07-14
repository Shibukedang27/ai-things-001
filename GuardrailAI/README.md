# GuardRail
**Turns production into a safe place to fail.**

GuardRail is a deployment safety engine that stops the exact class of bug that caused
the biggest outages of 2024–2026 (CrowdStrike, Cloudflare, AWS DynamoDB): configs that
weren't validated, rollouts with no blast-radius control, and no automatic rollback.

## What it actually does

1. **Config validation gate** — checks every config against hard schema limits *before*
   it can deploy. This is the exact check that was missing when a Cloudflare config file
   exceeded a hard-coded downstream limit and took down a huge slice of the internet
   in November 2025.

2. **Canary rollout engine** — ships to 1% → 10% → 50% → 100% of traffic, in stages,
   instead of all at once. A bad build only ever reaches a small slice before it's caught.

3. **Automatic rollback** — if the error rate crosses 2% at any stage, the deployment
   halts and rolls back immediately. No engineer has to notice first — this is what
   CrowdStrike's Windows sensor update didn't have, which is why fixing it required
   manually touching every crashed machine.

4. **Feature flags** — toggle a feature on or off instantly without a new deploy, so a
   bad feature can be killed in one click instead of waiting on a build pipeline.

## Run it

```bash
npm install
npm start
```

Then open **http://localhost:3000**.

- Fill in a service name, version, and config JSON, and hit **Validate & Deploy**.
- Slide the "chaos level" up to simulate a buggy build and watch it get caught and
  auto-rolled-back mid-rollout, in real time.
- Try breaking the config on purpose (e.g. add more entries to `rules` than `maxRules`
  allows) to see the pre-deploy validation gate block it before it ever reaches
  the canary stage.
- Toggle feature flags on the left panel — no deploy required.

## Architecture

- `server.js` — the whole safety engine: config validator (Ajv-based schema + limit
  checks), canary rollout state machine, rollback logic, feature flag store, and a
  WebSocket broadcaster for live dashboard updates.
- `public/index.html` — single-page ops console (vanilla JS + Chart.js, no build step).

Everything is in-memory right now, which is fine for a demo. To make this
production-real, swap:
- in-memory `deployments` / `featureFlags` → Postgres or Redis
- `simulateTrafficErrorRate()` → real metrics from your APM/observability tool
  (Datadog, Prometheus, New Relic — pull actual error rate from the new version's pods)
- the manual `/api/deploy` call → a webhook triggered by your real CI/CD
  (GitHub Actions, GitLab CI, Jenkins) after it builds a new image

## Where this becomes a real product

The target buyer is exactly the segment called out in industry outage reports:
**mid-size companies and SMBs without a dedicated SRE/platform team**, who currently
either deploy straight to 100% with no safety net, or pay a large SRE hire to build
this by hand. Packaging this as a lightweight SaaS or a self-hosted plugin that
plugs into existing CI/CD (rather than replacing it) is the wedge — you're not asking
anyone to rip out Jenkins or GitHub Actions, just to route the "go live" step through
this gate first.

Natural pricing model: per-service, per-month (like Datadog/PagerDuty), with a free
tier capped at 1–2 services to drive adoption before the upgrade.
