# Changelog

A human-readable record of notable changes. Newest first.
(For machine context across AI sessions, see the project memory — separate from the repo.)

## 2026-06 — Tracker redesign, data-quality overhaul, hardening

### Frontend — "The Classifieds" redesign
- Rebuilt `docs/index.html` from the minimal candy-card layout into a **Riso two-colour zine / newspaper-classifieds** look (via the Hallmark design skill).
  - Warm newsprint paper, deep blue-black ink, two spot inks: riso **orange** + riso **blue**; halftone grain; offset/misregistered masthead title "FRESH THIS WEEK"; knockout blue roaster tabs; coffees as boxed classified ads grouped by roaster; hard-offset shadow on card hover.
  - All existing behaviour preserved: `data.json` fetch, search, roaster/profile filters, New-only toggle, click-through, and the Update→Worker→poll button.
- **Palette dial-back** (too much orange): orange now reserved for *new this week* only (NEW tag + new-card border) plus the title accent and dateline star. Price is plain ink with an ink underline; the "N NEW THIS WK" badge is a low-key hollow blue postmark; the flavour-note rule is blue.
- **Wordmark**: "COFFEE TRACKER" set in **Cinzel Decorative** (engraved vintage caps), its own face distinct from the body display.
- **Logo / mascot**: new **two-colour hand-drawn pineapple** (orange+blue, no beach scenery) — crisp header icon (`docs/pineapple-icon.png`) + faint 8% bottom-right page watermark (`docs/pineapple-riso.png`). Original beach-photo logo kept only as the favicon.

### Scraper — field-extraction overhaul
- New module **`field_extraction.py`** layered above the existing `parse_*` heuristics (kept as fallback) to fix empty / cross-contaminated fields (e.g. `process = "Fully Washed ALTITUDE"`, flavour text stuffed into varietal).
  - Reads each store's structured data: namespaced Shopify tags (`ORIGIN_x` / `Origin.x` / `From: x` / `COUNTRY: x` …) and body `Label: value` text with the full label set as mutual boundaries.
  - Guards every value regardless of source: process whitelist, varietal prose/cup/country cleanup, origin place-validation, flavour recipe/marketing-prose rejection. Honesty rule: unknown fields stay empty, never fabricated.
  - Wired into all 5 product-construction sites; roast-profile logic unchanged. Optional per-store `field_rules` hook (unused so far).
- **Validated on live data**: process contamination 10 → 0; +88 fields newly filled. 30 offline unit tests (`tests/test_field_extraction.py`). Design + plan in `specs/2026-06-24-field-extraction-*.md`; diagnostic in `tools/extraction_report.py`.

### Maintenance / CI hardening (code review)
- `.github/workflows/update.yml`: added a `concurrency` guard + rebase-retry on push (so the weekly cron and the site's Update button can't collide), a scrape-health `::warning::` when ≥3 roasters fail, and an auto-prune step.
- `requirements.txt`: added upper version bounds for stable unattended CI.
- `update_coffee_list.py`: `previous_item_identities()` now selects the previous snapshot by filename (deterministic after a CI checkout), not mtime.
- **Output retention**: `output/` keeps only the newest two `coffee_list_*.json` snapshots (latest + the one needed for next week's "new" diff). One-time cleanup removed ~141 old snapshots, and the git history was rewritten to drop them (`.git` ~11 MB → ~4.6 MB).

### Diary — portrait photos + mobile polish
- List thumbnails switched from landscape (5:4 / 16:9) to **portrait 4:5** to match the source photos (all ~3:4 portrait), which were being awkwardly cropped; desktop image column narrowed 220→180px.
- Fixed the mobile list controls: the borderless search box was rendering **300px tall** (its `flex-basis: 300px` became a height in the column layout) with the filter pills shoved to the bottom — big empty gap. Search is now content-height and the controls stack tightly.
- Kept the header wordmark on one line at ≤320px (was wrapping).
- **Mobile list is now a 2-column magazine grid** (full-bleed, hairline grid lines, portrait photo + bean name + roaster; flavour line hidden on mobile) so several entries fit per screen. Desktop keeps the horizontal image-left cards.
- The rich detail page (`diary-detail.html`) was verified clean on mobile (no horizontal overflow; hero, taste sliders, spec list, origin all adapt).

## Earlier (baseline)
- Coffee **Diary** page (`docs/diary.html` / `docs/diary.css`): editorial "broadsheet index" design (coffee-crema palette, Fraunces / Newsreader / Geist Mono). Not yet visually unified with the Tracker — the Tracker's riso style is the lead going forward.
- Python scraper with multi-strategy fallback (Shopify JSON → handle discovery → HTML → all-products JSON → shop-slug → sitemap → Woo/WP API), published to GitHub Pages, refreshed by a weekly GitHub Action and a manual Update button (cron-job.org → Cloudflare Worker → `workflow_dispatch`).
