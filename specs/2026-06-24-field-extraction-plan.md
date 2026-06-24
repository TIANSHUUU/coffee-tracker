# Field Extraction Improvement — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Read each store's structured coffee metadata correctly (origin / process / varietal / flavour) and stop cross-field contamination, without rewriting the existing scraper.

**Architecture:** A new pure module `field_extraction.py` parses structured Shopify tags and body `Label: value` text. The 5 `CoffeeItem`-construction sites in `update_coffee_list.py` call it first and fall back to the existing `parse_*` heuristics (unchanged). A whitelist normaliser cleans `process`; a prose guard cleans `varietal` — applied to every source, so contamination is impossible regardless of where the value came from.

**Tech Stack:** Python 3.11, stdlib `re` + `unittest` (no new runtime deps), BeautifulSoup (already used).

Reference spec: `specs/2026-06-24-field-extraction-design.md`.

---

### Task 1: Tag extractor (`extract_from_tags`)

**Files:**
- Create: `field_extraction.py`
- Create: `tests/__init__.py` (empty)
- Test: `tests/test_field_extraction.py`

- [ ] **Step 1: Write the failing test**

```python
# tests/test_field_extraction.py
import unittest
from field_extraction import extract_from_tags


class TestTags(unittest.TestCase):
    def test_code_black_underscore(self):
        tags = ["COFFEE_Espresso", "FLAVOUR_Chocolate", "FLAVOUR_Nutty",
                "ORIGIN_Brazil", "ORIGIN_Ethiopia", "PROCESSING_Natural", "PROCESSING_Washed"]
        out = extract_from_tags(tags)
        self.assertEqual(out["origin"], "Brazil, Ethiopia")
        self.assertEqual(out["process"], "Natural, Washed")
        self.assertEqual(out["flavour"], "Chocolate, Nutty")
        self.assertEqual(out["varietal"], "")

    def test_ona_dot(self):
        tags = ["Brew Method.Pour over", "Coffee Type.Filter",
                "Origin.South America", "Taste Notes.Floral", "Taste Notes.Nutty", "Rare Coffee"]
        out = extract_from_tags(tags)
        self.assertEqual(out["origin"], "South America")
        self.assertEqual(out["flavour"], "Floral, Nutty")

    def test_proud_mary_colon_custom_key(self):
        tags = ["Feeling: Mild", "For: Espresso", "From: Nicaragua", "Process: Washed", "Type: Single Origin"]
        out = extract_from_tags(tags)
        self.assertEqual(out["origin"], "Nicaragua")
        self.assertEqual(out["process"], "Washed")

    def test_ignores_bare_tags(self):
        out = extract_from_tags(["coffee", "All Products", "SINGLE ORIGIN"])
        self.assertEqual(out, {"origin": "", "process": "", "varietal": "", "flavour": ""})


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd /Users/tantianshu/Documents/code/coffee-tracker && touch tests/__init__.py && python3 -m unittest tests.test_field_extraction -v`
Expected: FAIL — `ModuleNotFoundError: No module named 'field_extraction'`

- [ ] **Step 3: Write minimal implementation**

```python
# field_extraction.py
"""Structured field extraction for coffee product metadata.

Pure, network-free helpers used by update_coffee_list.py as a higher-priority
layer above the existing parse_* heuristics. See
specs/2026-06-24-field-extraction-design.md.
"""
import re

# normalised tag key -> canonical field
_TAG_KEY_FIELD = {
    "origin": "origin", "country": "origin", "from": "origin",
    "process": "process", "processing": "process",
    "variety": "varietal", "varietal": "varietal", "varieties": "varietal", "cultivar": "varietal",
    "flavour": "flavour", "flavor": "flavour",
    "taste notes": "flavour", "taste note": "flavour",
    "tasting notes": "flavour", "tasting note": "flavour",
    "notes": "flavour", "note": "flavour",
}

_FIELDS = ("origin", "process", "varietal", "flavour")


def _looks_like_placeholder(s: str) -> bool:
    """All-caps template label captured by accident, e.g. 'PROCESSING', 'REGION'."""
    return bool(re.match(r"^[A-Z][A-Z0-9 /]+$", s.strip()))


def extract_from_tags(tags, rules=None):
    """Parse 'KEY: val' / 'KEY_val' / 'Key.val' namespaced tags into fields."""
    out = {f: [] for f in _FIELDS}
    keymap = dict(_TAG_KEY_FIELD)
    for field, keys in (rules or {}).get("tag_aliases", {}).items():
        for k in keys:
            keymap[k.strip().lower()] = field
    for tag in tags or []:
        m = re.match(r"^\s*([A-Za-z][A-Za-z /]*?)\s*[:._]\s*(.+)$", str(tag).strip())
        if not m:
            continue
        key = re.sub(r"\s+", " ", m.group(1).strip().lower())
        val = m.group(2).strip()
        field = keymap.get(key)
        if field in out and val and not _looks_like_placeholder(val) and val not in out[field]:
            out[field].append(val)
    return {f: ", ".join(out[f]) for f in _FIELDS}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_field_extraction -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add field_extraction.py tests/__init__.py tests/test_field_extraction.py
git commit -m "feat(extract): namespaced tag extractor for coffee fields"
```

---

### Task 2: Process whitelist normaliser (`normalize_process`)

**Files:**
- Modify: `field_extraction.py`
- Test: `tests/test_field_extraction.py`

- [ ] **Step 1: Write the failing test**

```python
# add to tests/test_field_extraction.py
from field_extraction import normalize_process


class TestProcess(unittest.TestCase):
    def test_strips_trailing_label(self):
        self.assertEqual(normalize_process("Fully Washed ALTITUDE"), "Fully Washed")
        self.assertEqual(normalize_process("Pulped Natural Producers"), "Pulped Natural")

    def test_multi_process(self):
        self.assertEqual(normalize_process("WASHED & NATURAL REGION"), "Washed, Natural")

    def test_keeps_specific_over_generic(self):
        self.assertEqual(normalize_process("Carbonic Maceration"), "Carbonic Maceration")
        self.assertEqual(normalize_process("pulped natural"), "Pulped Natural")

    def test_empty_when_no_known_term(self):
        self.assertEqual(normalize_process("Single Origin Goodness"), "")
        self.assertEqual(normalize_process(""), "")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_field_extraction.TestProcess -v`
Expected: FAIL — `ImportError: cannot import name 'normalize_process'`

- [ ] **Step 3: Write minimal implementation**

```python
# add to field_extraction.py

# Ordered most-specific-first so "Pulped Natural" wins over "Natural", etc.
_PROCESS_PHRASES = [
    "Carbonic Maceration", "Double Fermentation", "Wet Hulled", "Pulped Natural",
    "Fully Washed", "Semi Washed", "Fully Natural",
    "Anaerobic", "Honey", "Co-Ferment", "Co Ferment",
    "Washed", "Natural", "Experimental",
]


def normalize_process(text: str) -> str:
    """Return only recognised process terms, so unrelated trailing words
    (ALTITUDE / REGION / PRODUCER ...) can never enter the process field."""
    low = (text or "").lower()
    found = []
    for phrase in _PROCESS_PHRASES:
        if re.search(r"\b" + re.escape(phrase.lower()) + r"\b", low):
            # skip if already covered by a more specific term already added
            if any(phrase.lower() in f.lower() for f in found):
                continue
            # drop any previously added term that this phrase subsumes
            found = [f for f in found if f.lower() not in phrase.lower()]
            found.append(phrase)
    # de-dupe preserving order
    return ", ".join(dict.fromkeys(found))
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_field_extraction.TestProcess -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add field_extraction.py tests/test_field_extraction.py
git commit -m "feat(extract): process whitelist normaliser"
```

---

### Task 3: Varietal prose guard (`clean_varietal`)

**Files:**
- Modify: `field_extraction.py`
- Test: `tests/test_field_extraction.py`

- [ ] **Step 1: Write the failing test**

```python
# add to tests/test_field_extraction.py
from field_extraction import clean_varietal


class TestVarietal(unittest.TestCase):
    def test_salvages_list_before_prose(self):
        self.assertEqual(clean_varietal("Caturra In the hills of Cauca, Colombia"), "Caturra")

    def test_rejects_prose_leading(self):
        self.assertEqual(clean_varietal("his farm has pink bourbon, bourbon aji, caturra"), "")

    def test_keeps_clean_lists(self):
        self.assertEqual(clean_varietal("Caturra & Catuaí"), "Caturra & Catuaí")
        self.assertEqual(clean_varietal("Catuaí"), "Catuaí")

    def test_empty(self):
        self.assertEqual(clean_varietal(""), "")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_field_extraction.TestVarietal -v`
Expected: FAIL — `ImportError: cannot import name 'clean_varietal'`

- [ ] **Step 3: Write minimal implementation**

```python
# add to field_extraction.py

_VARIETAL_PROSE = re.compile(
    r"\b(in|from|is|are|was|were|with|the|his|her|their|its|grown|located|"
    r"hills?|farm|farms|region|valley|estate|family|producer|redefining|known)\b",
    re.I,
)


def clean_varietal(s: str) -> str:
    """Keep a short varietal/cultivar list; drop prose that leaked in."""
    s = (s or "").strip(" ,;:-")
    if not s:
        return ""
    m = _VARIETAL_PROSE.search(s)
    if m and m.start() == 0:
        return ""              # starts with prose -> not a varietal
    if m and m.start() > 0:
        s = s[:m.start()].strip(" ,")
    if not s or len(s) > 80 or len(s.split()) > 12:
        return ""
    return s
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_field_extraction.TestVarietal -v`
Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add field_extraction.py tests/test_field_extraction.py
git commit -m "feat(extract): varietal prose guard"
```

---

### Task 4: Body `Label: value` extractor (`extract_from_body_labels`)

**Files:**
- Modify: `field_extraction.py`
- Test: `tests/test_field_extraction.py`

- [ ] **Step 1: Write the failing test**

```python
# add to tests/test_field_extraction.py
from field_extraction import extract_from_body_labels

MARKET_LANE = ("80% São Benedito Origin: Piatã, Bahia, Brazil Variety: Catuaí "
               "Processing Method: Pulped Natural Producers: Silvio Leite "
               "Relationship Length: Since 2020 20% San Antonio Origin: Inzá, "
               "Cauca, Colombia Varieties: Caturra Processing Method: Washed")

SEVEN_SEEDS = ("Origin: Chirinos, Cajamarca, Peru Producer: Various Process: "
               "Fully Washed Altitude: 1700-1900 masl Varietal: Caturra, Bourbon, Catimor")


class TestBodyLabels(unittest.TestCase):
    def test_market_lane_first_component(self):
        out = extract_from_body_labels(MARKET_LANE)
        self.assertEqual(out["origin"], "Piatã, Bahia, Brazil")
        self.assertEqual(out["varietal"], "Catuaí")
        self.assertEqual(out["process"], "Pulped Natural")

    def test_seven_seeds_no_bleed(self):
        out = extract_from_body_labels(SEVEN_SEEDS)
        self.assertEqual(out["origin"], "Chirinos, Cajamarca, Peru")
        self.assertEqual(out["process"], "Fully Washed")          # stops at 'Altitude:'
        self.assertEqual(out["varietal"], "Caturra, Bourbon, Catimor")

    def test_no_labels(self):
        out = extract_from_body_labels("A delicious everyday espresso blend.")
        self.assertEqual(out, {"origin": "", "process": "", "varietal": "", "flavour": ""})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_field_extraction.TestBodyLabels -v`
Expected: FAIL — `ImportError: cannot import name 'extract_from_body_labels'`

- [ ] **Step 3: Write minimal implementation**

```python
# add to field_extraction.py

# (label regex, field-or-None). None = boundary only (used to stop a previous value).
_BODY_LABELS = [
    (r"origins?", "origin"),
    (r"countr(?:y|ies)", "origin"),
    (r"region", None),
    (r"variet(?:y|ies|al)", "varietal"),
    (r"cultivar", "varietal"),
    (r"process(?:ing)?(?:\s+method)?", "process"),
    (r"producers?", None),
    (r"altitude", None),
    (r"elevation", None),
    (r"relationship\s+length", None),
    (r"farm", None),
    (r"importer", None),
    (r"roast(?:\s+(?:level|profile))?", None),
    (r"tasting\s+notes?", "flavour"),
    (r"flavou?r(?:\s+notes?)?", "flavour"),
    (r"notes?", "flavour"),
]

_LABEL_ALT = "|".join(p for p, _ in _BODY_LABELS)
_LABEL_RE = re.compile(rf"\b({_LABEL_ALT})\b\s*[:\-]\s*", re.I)


def _label_field(label: str):
    label = label.strip().lower()
    for pat, field in _BODY_LABELS:
        if re.fullmatch(pat, label, re.I):
            return field
    return None


def extract_from_body_labels(text: str, rules=None):
    """Slice each 'Label: value' up to the next known label (mutual boundaries)."""
    t = re.sub(r"\s+", " ", text or "")
    out = {f: "" for f in _FIELDS}
    matches = list(_LABEL_RE.finditer(t))
    for i, m in enumerate(matches):
        field = _label_field(m.group(1))
        if field is None or out.get(field):     # boundary-only, or field already filled
            continue
        end = matches[i + 1].start() if i + 1 < len(matches) else len(t)
        value = t[m.end():end].strip(" ,;:-")
        value = re.split(r"[.;]", value)[0].strip()   # stop at sentence end
        if value:
            out[field] = value[:120]
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_field_extraction.TestBodyLabels -v`
Expected: PASS (3 tests)

- [ ] **Step 5: Commit**

```bash
git add field_extraction.py tests/test_field_extraction.py
git commit -m "feat(extract): body Label:value extractor with mutual boundaries"
```

---

### Task 5: Orchestrator (`extract_structured`) + per-store `field_rules`

**Files:**
- Modify: `field_extraction.py`
- Test: `tests/test_field_extraction.py`

- [ ] **Step 1: Write the failing test**

```python
# add to tests/test_field_extraction.py
from field_extraction import extract_structured


class TestOrchestrator(unittest.TestCase):
    def test_tags_win_over_body(self):
        out = extract_structured(
            tags=["ORIGIN_Brazil", "PROCESSING_Washed"],
            body_text="Origin: Somewhere Else Process: Natural",
        )
        self.assertEqual(out["origin"], "Brazil")
        self.assertEqual(out["process"], "Washed")

    def test_body_fills_when_no_tags(self):
        out = extract_structured(tags=[], body_text=SEVEN_SEEDS)
        self.assertEqual(out["process"], "Fully Washed")
        self.assertEqual(out["varietal"], "Caturra, Bourbon, Catimor")

    def test_process_always_whitelisted(self):
        out = extract_structured(tags=["PROCESS: Fully Washed ALTITUDE"], body_text="")
        self.assertEqual(out["process"], "Fully Washed")

    def test_skip_sources_body(self):
        out = extract_structured(tags=[], body_text=SEVEN_SEEDS, rules={"skip_sources": ["body"]})
        self.assertEqual(out, {"origin": "", "process": "", "varietal": "", "flavour": ""})
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_field_extraction.TestOrchestrator -v`
Expected: FAIL — `ImportError: cannot import name 'extract_structured'`

- [ ] **Step 3: Write minimal implementation**

```python
# add to field_extraction.py

def extract_structured(tags=None, body_text="", rules=None):
    """Combine tag + body sources (tags win), then whitelist/guard the values.
    Returns {origin, process, varietal, flavour}; any field may be ''. """
    rules = rules or {}
    skip = set(rules.get("skip_sources", []))
    tag_out = extract_from_tags(tags, rules) if "tags" not in skip else {f: "" for f in _FIELDS}
    body_out = extract_from_body_labels(body_text, rules) if "body" not in skip else {f: "" for f in _FIELDS}

    out = {}
    for f in _FIELDS:
        out[f] = tag_out.get(f) or body_out.get(f) or ""
    out["process"] = normalize_process(out["process"])
    out["varietal"] = clean_varietal(out["varietal"])
    return out
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python3 -m unittest tests.test_field_extraction -v`
Expected: PASS (all suites — Tags, Process, Varietal, BodyLabels, Orchestrator)

- [ ] **Step 5: Commit**

```bash
git add field_extraction.py tests/test_field_extraction.py
git commit -m "feat(extract): orchestrator with source priority + field_rules"
```

---

### Task 6: Wire into the scraper (fallback preserved)

**Files:**
- Modify: `update_coffee_list.py` (import; 5 `CoffeeItem` build sites)

The pattern at every site: compute `sx = extract_structured(<tags>, <body_text>, rules=field_rules)` then use `sx[field] or <existing parse_* call>`, applying `normalize_process` / `clean_varietal` to the fallback too.

- [ ] **Step 1: Add the import and a roaster-rules accessor**

Add near the top imports of `update_coffee_list.py`:

```python
from field_extraction import extract_structured, normalize_process, clean_varietal
```

In `scrape_one_roaster`, read the optional rules (near the other `roaster.get(...)` reads):

```python
    field_rules = roaster.get("field_rules") if isinstance(roaster.get("field_rules"), dict) else None
```

Pass `field_rules` down to each scrape strategy that builds items. Add a keyword arg `field_rules=None` to: `scrape_shopify_collection_json`, `scrape_shopify_all_products_json`, `scrape_woocommerce_store_api`, `scrape_wordpress_product_api`, and `parse_product_page`. `parse_product_page` is called by three listing strategies — `scrape_via_html_listing`, `scrape_via_shop_slug_listing`, `scrape_via_sitemap` — so add `field_rules=None` to those three too and forward it into each `parse_product_page(...)` call. Thread `field_rules` from `scrape_one_roaster` into every one of these calls.

- [ ] **Step 2: Replace the field computation in `scrape_shopify_collection_json`**

Find the block that sets `process`, `origin`, `varietal` via `_tag_or_parse(...)` and the `flavour_profile=parse_flavour_profile(combined)` in the `CoffeeItem(...)`. Replace the three `_tag_or_parse` assignments and the flavour arg with:

```python
        sx = extract_structured(raw_tags, text_blob, rules=field_rules)
        origin   = sx["origin"]   or parse_origin(combined)
        process  = sx["process"]  or normalize_process(parse_process(combined, title=title, product_url=product_url))
        varietal = sx["varietal"] or clean_varietal(parse_varietal(combined))
        flavour  = sx["flavour"]  or parse_flavour_profile(combined)
```

and set `flavour_profile=flavour` in the `CoffeeItem(...)`. Leave the existing `roast_profile_label` logic untouched.

- [ ] **Step 3: Apply the same pattern to the other 4 sites**

Replace the inline `parse_origin/parse_process/parse_varietal/parse_flavour_profile` arguments with the same 4-line `sx = extract_structured(<tags>, <body>, rules=field_rules)` block + `sx[field] or <fallback>`. Use these exact `<tags>` / `<body>` arguments per site (tags must be a **list**):

| Function | `<tags>` arg | `<body>` arg |
|---|---|---|
| `scrape_shopify_all_products_json` | `product.get("tags") or []` | `text_blob` |
| `scrape_woocommerce_store_api` | `[c.get("name","") for p in products for c in (p.get("categories") or []) if isinstance(c, dict)] + [t.get("name","") for t in (product.get("tags") or []) if isinstance(t, dict)]` | `combined` |
| `scrape_wordpress_product_api` | `[]` | `combined` |
| `parse_product_page` | `[]` | `text_blob` |

Keep each site's `roast_profile` logic unchanged. (Woo/WP/HTML have no Shopify-style namespaced tags, so the tag source is empty/`[]` and the body extractor does the work there.)

- [ ] **Step 4: Smoke-verify it imports and runs on saved raw data**

Run:
```bash
python3 -c "import update_coffee_list, field_extraction; print('import OK')"
python3 -m unittest tests.test_field_extraction -v
```
Expected: `import OK` and all unit tests PASS.

- [ ] **Step 5: Commit**

```bash
git add update_coffee_list.py
git commit -m "feat(extract): route 5 build sites through extract_structured (parse_* kept as fallback)"
```

---

### Task 7: Before/after validation on real data

**Files:**
- Create: `tools/extraction_report.py` (one-off diagnostic; not run in CI)

- [ ] **Step 1: Write the report script**

```python
# tools/extraction_report.py
"""Run the live scraper once and compare field health vs the latest committed
snapshot. Diagnostic only — prints contamination + emptiness deltas."""
import json, glob, subprocess, sys

BAD = ["altitude", "producer", "region", "varieties", "masl", "notes", "tasting"]

def health(items):
    n = len(items) or 1
    empt = {f: sum(1 for i in items if not (i.get(f) or "").strip())
            for f in ["origin", "process", "varietal", "flavour_profile"]}
    contam = sum(1 for i in items
                 if any(w in (i.get("process") or "").lower() for w in BAD))
    return empt, contam, len(items)

def load_latest():
    f = sorted(glob.glob("output/coffee_list_*.json"))[-1]
    return [i for i in json.load(open(f))["items"] if i.get("status") == "ok"]

if __name__ == "__main__":
    before = load_latest()
    print("BEFORE:", health(before))
    print("Now run: python update_coffee_list.py   then re-run this script for AFTER.")
```

- [ ] **Step 2: Capture BEFORE numbers**

Run: `python3 tools/extraction_report.py`
Record the printed empties + contamination count.

- [ ] **Step 3: Run the live scraper and capture AFTER**

Run:
```bash
python3 update_coffee_list.py
python3 tools/extraction_report.py
```
Expected: `process` contamination count drops toward 0; `varietal`/`flavour` empties drop. Eyeball 10 random items for any new wrong values.

- [ ] **Step 4: Add `field_rules` only for stores still flagged wrong**

For any store the eyeball pass shows still polluting a field, add a minimal `field_rules` entry in `config/roasters.json` (e.g. `"field_rules": {"skip_sources": ["body"]}`), re-run, re-check. Do not add rules speculatively.

- [ ] **Step 5: Commit**

```bash
git add tools/extraction_report.py config/roasters.json
git commit -m "chore(extract): validation report + per-store field_rules where needed"
```

---

## Notes for the implementer

- Run all unit tests from the repo root: `python3 -m unittest tests.test_field_extraction -v`.
- `roast_profile` quality is **out of scope** — do not change roast logic at any site.
- Honesty rule: never emit a field without a recognised source. Empty is correct; wrong is a bug.
- The existing `parse_*` functions and `extract_shopify_tag_metadata` stay defined and used (as fallback / for roast). Do not delete them.
