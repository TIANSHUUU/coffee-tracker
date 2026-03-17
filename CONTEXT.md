# Coffee Tracker Context

## Project Goal

Build a manual-update local tool to fetch currently available coffee beans from selected Australian roasters and export results to local files.

User does **not** want scheduled auto-updates. Updates are triggered manually when needed.

## Project Location

- Root: `/Users/tantianshu/Documents/code/coffee-tracker`
- Main script: `/Users/tantianshu/Documents/code/coffee-tracker/update_coffee_list.py`
- Config: `/Users/tantianshu/Documents/code/coffee-tracker/config/roasters.json`
- Output: `/Users/tantianshu/Documents/code/coffee-tracker/output`

## Current Roaster Links

1. `https://marketlane.com.au/pages/coffee`
2. `https://www.smallbatch.com.au/shop/`
3. `https://www.proudmarycoffee.com.au/collections/coffee`
4. `https://sevenseeds.com.au/collections/coffee`
5. `https://www.commonfolkcoffee.com.au/collections/single-origin`
6. `https://onacoffee.com.au/collections/all`
7. `https://www.padrecoffee.com.au/collections/coffee?page=1#3ccf7147c4b179b7949fa6999e6ab2a2`
8. `https://codeblackcoffee.com.au/collections/coffee`
9. `https://somospuchero.com/en/categoria-producto/cafe/`

## Required Output Formats

- CSV
- JSON

## Required Fields

- `bean_name`
- `roast_profile` (`filter` / `espresso` / `omni`)
- `origin`
- `price_aud`
- `process`
- `flavour_profile`
- `source_url` (must be the specific product purchase URL, not generic listing URL)
- `product_url`
- `status`
- `error`

## Roast Profile Color Mapping

- `filter` -> `pink`
- `espresso` -> `green`
- `omni` -> `blue`

Implemented as field: `roast_profile_color`.

## Product Filtering Rules

Only coffee beans should remain in the final dataset. Exclude products if title/metadata matches:

- `drip bag`, `drip bags`
- `bundle`, `bundles`
- `subscription`, `subsrcription`
- `equipment`
- `merchandise`, `merch`
- `cup`
- `cascara tea`
- `decaf`
- `tote`

## Error Handling Requirement

If a site cannot be scraped, include an `error` record for that roaster instead of silently skipping.

## Implementation Notes (Current)

- Uses `requests` + `BeautifulSoup`.
- First tries Shopify collection JSON (`/collections/{handle}/products.json?limit=250`) where possible.
- Falls back to HTML listing + product-page parsing.
- Extracts roast profile, origin, process, flavour profile using heuristic keyword/pattern parsing.
- Writes timestamped files:
  - `output/coffee_list_YYYY-MM-DD_HHMMSS.csv`
  - `output/coffee_list_YYYY-MM-DD_HHMMSS.json`

## Latest Verified Run (in this session)

- Output files:
  - `/Users/tantianshu/Documents/code/coffee-tracker/output/coffee_list_2026-02-27_200110.csv`
  - `/Users/tantianshu/Documents/code/coffee-tracker/output/coffee_list_2026-02-27_200110.json`
- Reported:
  - `Total rows: 89`
  - `Error rows: 2`

## Run Instructions

```bash
cd /Users/tantianshu/Documents/code/coffee-tracker
python3 update_coffee_list.py
```

Optional:

```bash
python3 update_coffee_list.py --config config/roasters.json --output-dir output
```

## Latest Updates

- Added Puchero Coffee: https://somospuchero.com/en/categoria-producto/cafe/
- Puchero filter rule: exclude products whose name/metadata contains "chocolate" or "té"
- Latest output: /Users/tantianshu/Documents/code/coffee-tracker/output/coffee_list_2026-03-17_155641.*

