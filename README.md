# Coffee Tracker

One page to browse what's currently roasting across Australian specialty coffee roasters, refreshed weekly — so you don't have to check ~15 websites by hand.

**Live site:** https://tianshuuu.github.io/coffee-tracker/

## What it does

A Python scraper visits each roaster in [`config/roasters.json`](config/roasters.json), collects the coffees currently in stock (name, roast profile, origin, price, process, varietal, flavour notes), and publishes them to a static site hosted on GitHub Pages. New arrivals since the previous run are flagged.

The site has two sections:

- **Tracker** ([`docs/index.html`](docs/index.html)) — the weekly classifieds: every in-stock coffee, grouped by roaster, filterable by roaster / roast profile / search, with this week's new beans highlighted.
- **Diary** ([`docs/diary.html`](docs/diary.html)) — hand-curated tasting notes for individual coffees.

## How it works

```
update_coffee_list.py      scrape each roaster → output/coffee_list_<timestamp>.{json,csv,xlsx}
        │                   (multi-strategy: Shopify JSON → HTML → WooCommerce/WP API → sitemap)
        ▼
generate_web_data.py       diff latest vs previous snapshot, mark new items → docs/data.json
        ▼
docs/index.html            vanilla JS fetches data.json and renders the page
```

- **Automation:** [`.github/workflows/update.yml`](.github/workflows/update.yml) runs every Monday (and on manual dispatch), scrapes, regenerates `docs/data.json`, and commits the result.
- **Update button:** the site's *Update* button calls a Cloudflare Worker, which triggers the same workflow via the GitHub API (keeps the token off the client), then polls `data.json` for the new timestamp.
- **Snapshot retention:** only the newest two `output/coffee_list_*.json` snapshots are kept (the latest plus the one needed to compute "new this week"); the workflow prunes the rest automatically.

## Run it locally

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python update_coffee_list.py    # scrape → output/
python generate_web_data.py     # build docs/data.json

# preview the site (data.json is fetched over HTTP, so file:// won't work)
python3 -m http.server -d docs 8000   # then open http://localhost:8000
```

Optional arguments:

```bash
python update_coffee_list.py --config config/roasters.json --output-dir output
```

## Adding or changing a roaster

Edit [`config/roasters.json`](config/roasters.json). Each entry needs a `name` and `url`; optional fields handle awkward sites:

| field | purpose |
|---|---|
| `collection_url_override` | scrape a different URL than the public listing |
| `shopify_collection_handle` | force a specific Shopify collection |
| `price_variant_filter` | pick a bag size for the displayed price (e.g. `"250g"`) |
| `force_html_listing` / `force_woo_api` | skip auto-detection and use a specific strategy |

Products that aren't whole-bean coffee (drip bags, subscriptions, merch, equipment, etc.) are filtered out by keyword. If a roaster can't be scraped, it's recorded with `status: error` rather than silently dropped, and the workflow warns when several roasters fail in one run.
