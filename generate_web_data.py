"""
Generate docs/data.json for the GitHub Pages site.

Finds the two most recent output JSON files, compares them to identify
new items, and writes the result to docs/data.json.
"""

import json
import os
import glob
import re
import sys
from datetime import datetime


def strip_html(text: str) -> str:
    """Remove HTML tags and collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "output")
WEB_DATA_PATH = os.path.join(os.path.dirname(__file__), "docs", "data.json")


def find_output_files():
    pattern = os.path.join(OUTPUT_DIR, "coffee_list_*.json")
    files = sorted(glob.glob(pattern))
    return files


def load_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def item_key(item):
    """Stable identity key for a coffee product."""
    return (item.get("roaster", "").strip(), item.get("bean_name", "").strip())


def main():
    files = find_output_files()
    if not files:
        print("No output files found in output/", file=sys.stderr)
        sys.exit(1)

    latest_path = files[-1]
    previous_path = files[-2] if len(files) >= 2 else None

    print(f"Latest:   {os.path.basename(latest_path)}")
    if previous_path:
        print(f"Previous: {os.path.basename(previous_path)}")
    else:
        print("Previous: (none — all items will be marked as new)")

    latest = load_json(latest_path)
    previous = load_json(previous_path) if previous_path else None

    # Build set of keys from previous run
    previous_keys = set()
    if previous:
        for item in previous.get("items", []):
            previous_keys.add(item_key(item))

    # Process items
    items = []
    for item in latest.get("items", []):
        if item.get("status") == "error":
            continue
        key = item_key(item)
        entry = {
            "roaster": strip_html(item.get("roaster", "")),
            "bean_name": strip_html(item.get("bean_name", "")),
            "url": item.get("source_url") or item.get("product_url", ""),
            "roast_profile": item.get("roast_profile", ""),
            "origin": strip_html(item.get("origin", "")),
            "price_aud": item.get("price_aud", ""),
            "process": strip_html(item.get("process", "")),
            "varietal": strip_html(item.get("varietal", "")),
            "flavour_profile": strip_html(item.get("flavour_profile", "")),
            "is_new": key not in previous_keys,
        }
        items.append(entry)

    # Sort: new first, then by roaster, then by bean name
    items.sort(key=lambda x: (not x["is_new"], x["roaster"], x["bean_name"]))

    roasters = sorted({i["roaster"] for i in items if i["roaster"]})
    new_count = sum(1 for i in items if i["is_new"])

    # Parse generated_at timestamp
    raw_ts = latest.get("generated_at", "")
    try:
        dt = datetime.strptime(raw_ts, "%Y-%m-%d_%H%M%S")
        generated_at = dt.strftime("%Y-%m-%d %H:%M")
    except ValueError:
        generated_at = raw_ts

    web_data = {
        "generated_at": generated_at,
        "stats": {
            "total": len(items),
            "new": new_count,
            "roasters": len(roasters),
        },
        "roasters": roasters,
        "items": items,
    }

    os.makedirs(os.path.dirname(WEB_DATA_PATH), exist_ok=True)
    with open(WEB_DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(web_data, f, ensure_ascii=False, indent=2)

    print(f"Written: {WEB_DATA_PATH}")
    print(f"Total items: {len(items)}, New: {new_count}, Roasters: {len(roasters)}")


if __name__ == "__main__":
    main()
