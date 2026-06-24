"""Diagnostic: compare field health between the two most recent output snapshots.

Run the live scraper first (`python update_coffee_list.py`), then run this to see
how origin/process/varietal/flavour completeness and `process` contamination
changed between the previous snapshot (old extraction) and the new one.

Not used in CI — purely a local before/after check.
"""
import glob
import json

# words that should never appear inside a clean `process` value
_CONTAM = ["altitude", "producer", "region", "varieties", "variety", "masl",
           "notes", "tasting", "elevation", "relationship"]
_FIELDS = ["origin", "process", "varietal", "flavour_profile"]


def load(path):
    data = json.load(open(path, encoding="utf-8"))
    return [i for i in data.get("items", []) if i.get("status") == "ok"]


def health(items):
    n = len(items) or 1
    empties = {f: sum(1 for i in items if not (i.get(f) or "").strip()) for f in _FIELDS}
    contam = [i for i in items
              if any(w in (i.get("process") or "").lower() for w in _CONTAM)]
    return empties, contam, len(items)


def main():
    snaps = sorted(glob.glob("output/coffee_list_*.json"))
    if len(snaps) < 2:
        print("Need at least 2 snapshots (run the scraper first).")
        return
    prev_items, new_items = load(snaps[-2]), load(snaps[-1])
    print(f"BEFORE: {snaps[-2].split('/')[-1]}")
    print(f"AFTER:  {snaps[-1].split('/')[-1]}\n")

    pe, pc, pn = health(prev_items)
    ne, nc, nn = health(new_items)

    print(f"{'field':18} {'empty BEFORE':>14} {'empty AFTER':>14}")
    for f in _FIELDS:
        print(f"{f:18} {pe[f]:>6}/{pn:<7} {ne[f]:>6}/{nn:<7}")
    print(f"\nprocess contamination:  BEFORE {len(pc)}   AFTER {len(nc)}")

    if pc:
        print("\n-- sample contaminated `process` BEFORE --")
        for i in pc[:8]:
            print(f"   [{i['roaster'][:12]:12}] {i.get('process')!r}")
    if nc:
        print("\n-- STILL contaminated AFTER (investigate / add field_rules) --")
        for i in nc[:8]:
            print(f"   [{i['roaster'][:12]:12}] {i.get('process')!r}")

    # what newly got filled (by roaster, varietal+flavour)
    def by_key(items):
        return {(i.get("roaster"), i.get("bean_name")): i for i in items}
    pmap, nmap = by_key(prev_items), by_key(new_items)
    newly = {f: 0 for f in _FIELDS}
    for k, i in nmap.items():
        p = pmap.get(k)
        if not p:
            continue
        for f in _FIELDS:
            if (i.get(f) or "").strip() and not (p.get(f) or "").strip():
                newly[f] += 1
    print("\nnewly-filled (same product, was empty -> now has value):")
    for f in _FIELDS:
        print(f"   {f:18} +{newly[f]}")


if __name__ == "__main__":
    main()
