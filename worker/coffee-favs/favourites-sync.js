/**
 * coffee-favs — cross-device storage for the Tracker's ♥ saved coffees.
 *
 * Deliberately dumb: it stores one JSON blob per sync code and never merges.
 * Clients GET, merge locally, then PUT. Because the client merge is last-write-
 * wins per key with tombstones, it converges even if two devices race — the
 * loser re-pushes its own keys on its next sync.
 *
 * The sync code IS the credential. 128 bits of randomness, generated on the
 * client, never written down anywhere server-side but the KV key itself.
 *
 *   GET  /favs/<code>  -> { items, tombstones, updated_at }
 *   PUT  /favs/<code>  <- { items, tombstones }
 *
 * Deploy: see worker/README.md
 */

const ALLOWED_ORIGINS = [
  'https://tianshuuu.github.io',
  'http://localhost:8000',
  'http://localhost:8765',
  'http://127.0.0.1:8000',
  'http://127.0.0.1:8765',
]

const CODE_RE = /^[0-9a-f]{32}$/
const MAX_BODY = 256 * 1024        // ~1000 saved coffees; far past any real use
const TTL_SECONDS = 60 * 60 * 24 * 365   // drop codes untouched for a year

function corsHeaders(origin) {
  return {
    'Access-Control-Allow-Origin': ALLOWED_ORIGINS.includes(origin) ? origin : '',
    'Access-Control-Allow-Methods': 'GET, PUT, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '86400',
    'Vary': 'Origin',
  }
}

const json = (obj, status, origin) =>
  new Response(JSON.stringify(obj), {
    status,
    headers: {
      'Content-Type': 'application/json',
      'Cache-Control': 'no-store',
      ...corsHeaders(origin),
    },
  })

// Reject anything that isn't the shape we wrote, so a malformed PUT can't
// poison a device that pulls it later.
function validDoc(doc) {
  if (!doc || typeof doc !== 'object' || Array.isArray(doc)) return false
  const { items, tombstones } = doc
  if (!items || typeof items !== 'object' || Array.isArray(items)) return false
  if (tombstones !== undefined &&
      (!tombstones || typeof tombstones !== 'object' || Array.isArray(tombstones))) return false
  for (const v of Object.values(items)) {
    if (!v || typeof v !== 'object' || Array.isArray(v)) return false
  }
  for (const v of Object.values(tombstones || {})) {
    if (typeof v !== 'number' || !Number.isFinite(v)) return false
  }
  return true
}

export default {
  async fetch(request, env) {
    const origin = request.headers.get('Origin') || ''

    if (request.method === 'OPTIONS')
      return new Response(null, { status: 204, headers: corsHeaders(origin) })

    if (!ALLOWED_ORIGINS.includes(origin))
      return json({ error: 'forbidden' }, 403, origin)

    const match = new URL(request.url).pathname.match(/^\/favs\/([^/]+)$/)
    if (!match) return json({ error: 'not_found' }, 404, origin)

    const code = match[1]
    if (!CODE_RE.test(code)) return json({ error: 'bad_code' }, 400, origin)

    const kvKey = `favs:${code}`

    if (request.method === 'GET') {
      const stored = await env.FAVS.get(kvKey, 'json')
      return json(stored || { items: {}, tombstones: {}, updated_at: 0 }, 200, origin)
    }

    if (request.method === 'PUT') {
      const raw = await request.text()
      if (raw.length > MAX_BODY) return json({ error: 'too_large' }, 413, origin)

      let doc
      try { doc = JSON.parse(raw) } catch { return json({ error: 'bad_json' }, 400, origin) }
      if (!validDoc(doc)) return json({ error: 'bad_shape' }, 400, origin)

      const updated_at = Date.now()
      await env.FAVS.put(
        kvKey,
        JSON.stringify({ items: doc.items, tombstones: doc.tombstones || {}, updated_at }),
        { expirationTtl: TTL_SECONDS }
      )
      return json({ ok: true, updated_at }, 200, origin)
    }

    return json({ error: 'method_not_allowed' }, 405, origin)
  },
}
