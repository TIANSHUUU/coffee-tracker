# Field Extraction Improvement — Design

**Date:** 2026-06-24
**Status:** Approved direction, pending spec review
**Scope:** `update_coffee_list.py` field extraction (origin / process / varietal / flavour). Additive — does **not** rewrite the existing scraper or its `parse_*` functions.

## Goal & priorities

Make the structured card fields (origin / process / varietal, plus the flavour note beside the blue rule) reliable.

Priority order, agreed:

1. **Eliminate contamination** — stop stuffing unrelated text into a field (e.g. `process = "Fully Washed ALTITUDE"`, `"Natural Producer"`, `"WASHED & NATURAL REGION"`).
2. **Fill gaps** — read the structured data we currently ignore so fewer fields are empty.
3. **Never fabricate** — a field is emitted only when a recognised source provides it. Empty is acceptable; wrong is not.

## Problem diagnosis (evidence)

Measured on the latest snapshot (180 ok items): origin 22% empty, process 42% empty, varietal 78% empty, flavour 80% empty, plus 11 visibly contaminated `process` values.

The data is **mostly structured**, just not read. Each store uses a consistent convention; the current parser only recognises a fraction of them and falls back to greedy free-text parsing:

| Store | Where structured data lives | Example | Current failure |
|---|---|---|---|
| Code Black | tags, `_`-namespaced | `ORIGIN_Brazil`, `PROCESSING_Washed`, `FLAVOUR_Chocolate` | namespace not recognised → falls back to body → `WASHED & NATURAL REGION` |
| ONA | tags, `.`-namespaced | `Origin.South America`, `Taste Notes.Floral`, `Coffee Type.Filter` | `Origin.`/`Taste Notes.` not recognised → origin + flavour lost |
| Proud Mary | tags, custom `:` keys | `From: Nicaragua`, `Process: Washed` | `From:` (= origin) not recognised |
| Commonfolk | tags, `:` uppercase | `COUNTRY: X`, `PROCESS: X`, `ROAST: X` | already handled |
| Market Lane, Seven Seeds, Wide Open Road, Vacation, Commonfolk | body `Label: value` text | `Origin: … Variety: … Processing Method: … Producers: …` | label parser's stop-words incomplete → bleeds into next label |
| Stitch, Padre (blends), Standing Room | little/no structure | — | genuinely absent on page → must stay empty |

**Two root causes:** (1) tag namespaces not recognised; (2) body `Label:` boundaries incomplete.

**Conclusion:** deterministic, no LLM needed.

## Approach

**A (generic multi-convention extractor) + a minimal per-store override hook.** Layered above the existing parsers, which are kept as the final fallback.

## Architecture

- New module **`field_extraction.py`** — pure, network-free, unit-testable functions. Existing `parse_*` in `update_coffee_list.py` are **unchanged**.
- A resolver `resolve_fields(...)` tries sources in priority order and returns the final field set:
  1. **Structured tags** (`extract_from_tags`)
  2. **Body `Label: value`** (`extract_from_body_labels`)
  3. **Existing heuristics** (`parse_origin` / `parse_process` / `parse_varietal` / `parse_flavour_profile`) — fallback only.
- Wired in at the ~5 `CoffeeItem`-construction sites (`scrape_shopify_collection_json`, `scrape_shopify_all_products_json`, `scrape_woocommerce_store_api`, `scrape_wordpress_product_api`, `parse_product_page`): replace the direct `parse_*` calls with one `resolve_fields(...)` call. No other scraper logic changes.

## Components

### 1. `extract_from_tags(tags) -> dict`
Split each tag on the first of `:` `_` `.` into `(key, value)`; map normalised key → field. Key map:

- **origin** ← origin, country, from
- **process** ← process, processing
- **varietal** ← variety, varietal, varieties, cultivar
- **flavour** ← flavour, flavor, taste notes, tasting notes, notes
- **roast** ← coffee type, brew method, for, roast (→ profile, reuses existing roast logic)
- **region** ← region (used to refine origin; see field rules)

Multiple values per field are joined (`ORIGIN_Brazil` + `ORIGIN_Ethiopia` → `"Brazil, Ethiopia"`). Only tags whose key matches a known field are accepted; bare tags (`coffee`, `All Products`) are ignored. Template-label guard (`_is_template_label`) reused.

### 2. `extract_from_body_labels(text) -> dict`
Find every `Label:` in the body and slice each value up to the **next** known label — the full vocabulary acts as mutual boundaries: origin, country, region, variety/varietal/varieties, cultivar, process/processing/processing method, producer(s), altitude, relationship length, notes/tasting notes/flavour/flavor, roast. Producer / altitude / relationship-length are boundaries even though they are not emitted. This is the core de-contamination fix.

### 3. Process whitelist normalisation
`process` is emitted only as recognised process terms (Washed, Natural, Honey, Anaerobic, Pulped Natural, Wet Hulled, Carbonic Maceration, Double Fermentation, Co-ferment, Experimental, with modifiers Fully / Semi / Double). Detection is by matching known terms, not by grabbing text after `Process:`. This structurally prevents `ALTITUDE` / `REGION` / `PRODUCER` from ever entering `process`.

### 4. Per-store hook (minimal, YAGNI)
Optional `"field_rules"` per roaster in `config/roasters.json`. Initial support:

- `"skip_sources": ["body"]` — disable a source that produces garbage for that store.
- `"tag_aliases": {"origin": ["custom_key"]}` — extra key→field mappings for a store's bespoke tag key.

Shape is extended only when a concrete oddball needs more. No rules added speculatively.

## Field rules (honesty)

- **origin** — prefer the most specific available: an `Origin:`/`Origin.`/`From:`/`COUNTRY:` value, else compose `Region + Country`. Free-text fallback still requires a known country keyword.
- **process** — whitelist only (above). Never free prose.
- **varietal** — from a varietal source; the new layer applies its own prose-rejection guard (length / word-count / "contains a sentence" checks) so values like `"Caturra In the hills of Cauca…"` are dropped. The existing `parse_varietal` is unchanged and used only as fallback.
- **flavour** — from `Taste Notes`/`Flavour`/`Notes` tags or a flavour label; the existing `looks_like_flavour` guard is reused to avoid grabbing marketing copy.
- Any field with no recognised source stays empty.

## Error handling

Extractors are defensive over empty/`None`/malformed input and do no I/O. `field_rules` is shape-validated; malformed rules are ignored with the generic path used instead.

## Testing

1. **Offline golden fixtures** — capture raw product data (tags + body) for ~8–12 representative stores (Code Black, ONA, Proud Mary, Market Lane, Seven Seeds, Commonfolk, Wide Open Road, Vacation, …) into `tests/fixtures/`. `tests/test_field_extraction.py` asserts expected origin/process/varietal/flavour per fixture, and explicitly asserts the known contamination cases (`Natural Producer`, `Washed ALTITUDE`, `WASHED & NATURAL REGION`) come out clean.
2. **Offline before/after report** — a script runs the new resolver over the fixtures (and, optionally, a one-time live pass) and diffs field-by-field against current output, quantifying contamination removed and gaps filled, so the improvement is verified on real data before deploying.

## Non-goals

- No LLM extraction now (revisit only for residual stubborn stores).
- No changes to the existing `parse_*` internals, the scrape-strategy selection, or the output schema.
- No speculative per-store rules.

## Incremental rollout

1. Add `field_extraction.py` + tests (no wiring yet) — verify against fixtures.
2. Wire `resolve_fields` into the 5 construction sites.
3. Run the before/after report on real data; confirm contamination down and no regressions.
4. Add `field_rules` only for stores the report flags as still wrong.
