# Cloudflare Workers

Two Workers back the Tracker. Both deploy to `*.tianshu-tan.workers.dev`.

| Worker | Purpose | Status |
|---|---|---|
| [`coffee-trigger/`](coffee-trigger/) | Update button → dispatches the GitHub Action | live since 2026-03-31 |
| [`coffee-favs/`](coffee-favs/) | Cross-device sync for ♥ saved coffees | **not deployed yet** |

`wrangler` is not installed globally — use `npx wrangler`.

---

## coffee-trigger

Takes a POST from the site's Update button and dispatches `update.yml` in
`TIANSHUUU/coffee-tracker`, so the GitHub token stays off the client.

**The source in this directory was recovered on 2026-07-24** by pulling the
deployed script back out of the Cloudflare API. It had been written in the
dashboard quick editor and never existed locally — the repo only ever held the
`WORKER_URL` constant in `docs/index.html`. It is committed here verbatim so it
can be edited and redeployed like normal code.

### Known weaknesses

Neither is causing a problem today, but both are worth knowing about:

1. **No origin check.** It answers `Access-Control-Allow-Origin: *` and accepts a
   POST from anywhere. The URL is published in `docs/index.html` on a public
   site, so anyone who finds it can trigger a scrape run — burning Actions
   minutes and hammering the roaster sites.
2. **No throttle.** Nothing stops repeated triggers.

The sibling worker at `~/Documents/code/infoaggre/worker/trigger-refresh.js`
solves both (an `ALLOWED_ORIGIN` check plus a 60-second edge-cache throttle) and
is the natural model to copy from. Redeploying is what makes any fix take
effect — editing this file alone changes nothing.

### Deploy

```bash
cd worker/coffee-trigger
npx wrangler deploy
```

The `GITHUB_TOKEN` secret is already set on the live Worker and cannot be read
back out. A redeploy of the script keeps it. Only a from-scratch rebuild needs
`npx wrangler secret put GITHUB_TOKEN`.

---

## coffee-favs

Stores saved coffees so they follow you between phone and desktop. Kept separate
from `coffee-trigger` on purpose: that one holds a GitHub token and this one
should not be anywhere near it.

### How it works

The site keeps saved coffees in `localStorage` and works fully offline. If sync
is on, the device also holds a **sync code** — 128 random bits generated in the
browser. The worker stores one JSON blob per code in KV:

```
GET  /favs/<code>  -> { items, tombstones, updated_at }
PUT  /favs/<code>  <- { items, tombstones }
```

The worker never merges. Clients pull, merge locally (last-write-wins per
coffee, with tombstones so a deletion isn't undone by another device's stale
copy), then push. That merge is convergent, so if two devices race, the loser
re-pushes its own entries next sync and nothing is lost.

**The sync code is the only credential.** Anyone holding it can read and change
that saved list. No accounts, no personal data — it's a coffee wishlist — but
don't paste the code anywhere public.

Unlike `coffee-trigger`, this one **does** check `Origin` against an allowlist
(`ALLOWED_ORIGINS`, which includes a few localhost ports for development).

### Deploy

```bash
cd worker/coffee-favs

# 1. Create the KV namespace (once). Copy the id it prints.
npx wrangler kv namespace create FAVS

# 2. Paste that id into wrangler.toml, replacing PASTE_KV_NAMESPACE_ID_HERE

# 3. Ship it
npx wrangler deploy
```

The deployed URL must match `SYNC_URL` in
[`../../docs/index.html`](../../docs/index.html), currently
`https://coffee-favs.tianshu-tan.workers.dev` (subdomain confirmed against the
account on 2026-07-24). If it doesn't match, sync fails silently — the page
still works, it just stays local-only and the Saved view shows "Sync failed".

### Cost

KV's free tier is 100k reads and 1k writes per day. A page load is one read plus
at most one write. Nothing to run or maintain; KV is managed by Cloudflare.

### Testing

Plain ESM with an `env.FAVS` KV binding, so it runs under Node with a `Map`
stub — no account or network needed. The client's sync logic is tested by
stubbing this host with Playwright request interception and driving two browser
contexts as two devices.
