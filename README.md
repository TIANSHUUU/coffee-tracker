# Coffee Tracker (Manual Update)

This tool fetches current coffee beans from your selected roasters and writes local files in CSV and JSON formats.

## Output fields

- `bean_name` (coffee name)
- `roast_profile` (`filter` / `espresso` / `omni` / empty)
- `origin`
- `price_aud`
- `process`
- `varietal`
- `flavour_profile`
- plus status fields

If a roaster cannot be scraped, the output includes a row with `status=error` and an `error` message.
In CSV/XLSX output, `bean_name` is a hyperlink to the purchase URL.
`product_url` and `source_url` are not shown as output columns.

## Excluded product types

The scraper automatically excludes products with names/descriptions containing:

- drip bag(s)
- bundle(s)
- subscription / subsrcription
- equipment
- merchandise / merch
- cup
- cascara tea
- decaf
- tote
- coffee concentrate
- tshirt / t-shirt / tee shirt
- giftcard / gift card
- tea
- brewing scales
- candle
- jug / jugs
- matcha latte
- matcha
- vest
- jumper
- cap
- tamper
- Hario V60 Drip Assist Set
- instant coffee

## Setup

```bash
cd /Users/tantianshu/Documents/code/coffee-tracker
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run update manually

```bash
cd /Users/tantianshu/Documents/code/coffee-tracker
source .venv/bin/activate
python update_coffee_list.py
```

Optional arguments:

```bash
python update_coffee_list.py --config config/roasters.json --output-dir output
```

## Output files

Generated under `output/`:

- `coffee_list_YYYY-MM-DD_HHMMSS.csv`
- `coffee_list_YYYY-MM-DD_HHMMSS.xlsx` (new items vs previous run are highlighted yellow)
- `coffee_list_YYYY-MM-DD_HHMMSS.json`
