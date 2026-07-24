/**
 * coffee-trigger — the site's Update button.
 *
 * Takes a POST from the Tracker and dispatches the update.yml workflow, so the
 * GitHub token never reaches the browser.
 *
 * Originally written in the Cloudflare dashboard quick editor (2026-03-31) and
 * recovered into this repo on 2026-07-24. Hardened at the same time: it used to
 * answer `Access-Control-Allow-Origin: *` with no Origin check and no throttle,
 * which let anyone who read the worker URL out of the public page spam scrape
 * runs.
 */

const ALLOWED_ORIGINS = [
  'https://tianshuuu.github.io',
  'http://localhost:8000',
  'http://localhost:8765',
  'http://127.0.0.1:8000',
  'http://127.0.0.1:8765',
]

const DISPATCH_URL =
  'https://api.github.com/repos/TIANSHUUU/coffee-tracker/actions/workflows/update.yml/dispatches'

const THROTTLE_SECONDS = 60

function corsHeaders(origin) {
  return {
    'Access-Control-Allow-Origin': ALLOWED_ORIGINS.includes(origin) ? origin : '',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Vary': 'Origin',
  }
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || ''

    if (request.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders(origin) })
    }

    if (request.method !== 'POST') {
      return new Response('Method not allowed', { status: 405, headers: corsHeaders(origin) })
    }

    if (!ALLOWED_ORIGINS.includes(origin)) {
      return new Response('forbidden', { status: 403, headers: corsHeaders(origin) })
    }

    // Edge-level throttle. Per-colo rather than global, which is plenty for one
    // person clicking a button — it exists to stop a loop, not to be exact.
    const cache = caches.default
    const throttleKey = new Request('https://throttle.local/coffee-trigger')
    if (await cache.match(throttleKey)) {
      return new Response('too_soon', { status: 429, headers: corsHeaders(origin) })
    }

    const res = await fetch(DISPATCH_URL, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${env.GITHUB_TOKEN}`,
        Accept: 'application/vnd.github+json',
        'Content-Type': 'application/json',
        'User-Agent': 'coffee-tracker-worker',
      },
      body: JSON.stringify({ ref: 'main' }),
    })

    if (res.status !== 204) {
      return new Response('error', { status: 500, headers: corsHeaders(origin) })
    }

    await cache.put(
      throttleKey,
      new Response('1', { headers: { 'Cache-Control': `max-age=${THROTTLE_SECONDS}` } })
    )
    return new Response('ok', { status: 200, headers: corsHeaders(origin) })
  },
}
