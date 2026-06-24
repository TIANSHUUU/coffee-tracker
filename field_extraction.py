"""Structured field extraction for coffee product metadata.

Pure, network-free helpers used by update_coffee_list.py as a higher-priority
layer above the existing parse_* heuristics. The existing parsers stay as the
final fallback. See specs/2026-06-24-field-extraction-design.md.

Design goals, in order: (1) never let unrelated text contaminate a field,
(2) read the structured data each store actually exposes, (3) never fabricate —
an unknown field stays empty.
"""
import re

_FIELDS = ("origin", "process", "varietal", "flavour")

# normalised tag key -> canonical field. Roast is intentionally absent: roast
# profile is handled by the existing scraper logic and is out of scope here.
_TAG_KEY_FIELD = {
    "origin": "origin", "country": "origin", "from": "origin",
    "process": "process", "processing": "process",
    "variety": "varietal", "varietal": "varietal", "varieties": "varietal", "cultivar": "varietal",
    "flavour": "flavour", "flavor": "flavour",
    "taste notes": "flavour", "taste note": "flavour",
    "tasting notes": "flavour", "tasting note": "flavour",
    "notes": "flavour", "note": "flavour",
}


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
            if any(phrase.lower() in f.lower() for f in found):
                continue
            found = [f for f in found if f.lower() not in phrase.lower()]
            found.append(phrase)
    return ", ".join(dict.fromkeys(found))


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


# (label regex, field-or-None). None = boundary only (stops a previous value).
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


def extract_structured(tags=None, body_text="", rules=None):
    """Combine tag + body sources (tags win), then whitelist/guard the values.

    Returns {origin, process, varietal, flavour}; any field may be ''.
    """
    rules = rules or {}
    skip = set(rules.get("skip_sources", []))
    empty = {f: "" for f in _FIELDS}
    tag_out = empty if "tags" in skip else extract_from_tags(tags, rules)
    body_out = empty if "body" in skip else extract_from_body_labels(body_text, rules)

    out = {}
    for f in _FIELDS:
        out[f] = tag_out.get(f) or body_out.get(f) or ""
    out["process"] = normalize_process(out["process"])
    out["varietal"] = clean_varietal(out["varietal"])
    return out
