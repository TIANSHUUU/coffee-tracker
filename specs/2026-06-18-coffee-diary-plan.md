# Coffee Diary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a bilingual (中/EN) personal coffee tasting "diary" to the existing coffee-tracker static site, with a searchable/filterable list page and a wine-detail-style entry page.

**Architecture:** Pure static HTML/CSS/JS in `docs/` (GitHub Pages root). Two new pages (`diary.html` list, `diary-detail.html` detail) share one stylesheet (`diary.css`) and one JS module (`diary-common.js`: i18n, `t()` resolver, header + language toggle, shared render helpers). Data lives in `diary.json` (structured array, bilingual text fields as `{zh,en}` objects). The empty `blog.*` scaffold is removed and the homepage nav points to the diary.

**Tech Stack:** Vanilla HTML/CSS/JS, `fetch()` for JSON, `localStorage` for language preference. No build step, no framework, no test runner. Verification is manual via a local static server.

**Spec:** `specs/2026-06-18-coffee-diary-design.md`

**Note on TDD:** The existing site has no test harness and adding one for a small personal static page is out of scope (YAGNI). Each task therefore ends with a concrete manual verification step (JSON validation or browser check via `python3 -m http.server`).

---

## File Structure

| File | Responsibility |
|---|---|
| `docs/diary.json` | All diary entries (data). Seeded with 1 entry. |
| `docs/diary.css` | Shared styles: header/nav/lang-toggle, color blocks, pills, chips, sliders, panels, card grid, responsive. |
| `docs/diary-common.js` | Shared logic: language state, `t()` resolver, `ui()` label dictionary, header + lang-toggle render, slider/icon-group helpers, `esc`, `formatDate`, color map. |
| `docs/diary.html` | List/gallery page: search box + roast filter pills + card grid. |
| `docs/diary-detail.html` | Detail page: reads `?slug=`, renders hero + flavours + notes + brew + taste profile + summary + origin. |
| `docs/diary/images/` | Bean images (optional; `.gitkeep` placeholder). |
| `docs/index.html` | MODIFY: nav `Blog` → `Diary` linking `diary.html`. |
| `docs/blog.html`, `docs/blog-posts.json`, `docs/blog/` | DELETE (empty scaffold superseded by diary). |

**Local verification command (used throughout):**
```bash
cd /Users/tantianshu/Documents/code/coffee-tracker
python3 -m http.server 8000 --directory docs
# then open http://localhost:8000/diary.html
```

---

## Task 1: Data seed + remove old blog scaffold

**Files:**
- Create: `docs/diary.json`
- Create: `docs/diary/images/.gitkeep`
- Delete: `docs/blog.html`, `docs/blog-posts.json`, `docs/blog/posts/.gitkeep`

- [ ] **Step 1: Create `docs/diary.json` with one seed entry**

```json
{
  "entries": [
    {
      "slug": "ethiopia-guji-natural",
      "date": "2026-06-18",
      "bean_name": { "zh": "古吉 日晒", "en": "Guji Natural" },
      "roaster": { "zh": "Market Lane", "en": "Market Lane" },
      "image": "",
      "color": "pink",
      "roast_profile": "filter",
      "price_aud": "24.00",
      "tags": [
        { "zh": "埃塞俄比亚", "en": "Ethiopia" },
        { "zh": "日晒", "en": "Natural" },
        { "zh": "手冲", "en": "Filter" },
        { "zh": "1900–2100m", "en": "1900–2100m" }
      ],
      "flavours": [
        { "icon": "🫐", "label": { "zh": "蓝莓", "en": "Blueberry" } },
        { "icon": "🍓", "label": { "zh": "草莓", "en": "Strawberry" } },
        { "icon": "🌸", "label": { "zh": "花香", "en": "Floral" } }
      ],
      "story": {
        "zh": "干香是浓郁的莓果和花香，热水一冲整个房间都甜了。\n\n入口明亮多汁，蓝莓和草莓的酸甜很跳，尾段有淡淡的红茶感，干净利落。",
        "en": "Dry aroma bursts with berries and florals — the whole room sweetens on the pour.\n\nBright and juicy up front, vivid blueberry-strawberry acidity, finishing on a light black-tea note. Clean and crisp."
      },
      "brew": {
        "method": { "zh": "V60 · 1:16 · 92°C · 2:30", "en": "V60 · 1:16 · 92°C · 2:30" },
        "food": [
          { "icon": "🥐", "label": { "zh": "可颂", "en": "Croissant" } },
          { "icon": "🍋", "label": { "zh": "柠檬蛋糕", "en": "Lemon cake" } }
        ],
        "moods": [
          { "icon": "😌", "label": { "zh": "平静", "en": "Calm" } }
        ],
        "time": [
          { "icon": "🌅", "label": { "zh": "清晨", "en": "Morning" } }
        ]
      },
      "profile": {
        "acidity": "high",
        "sweetness": "medium",
        "body": "low",
        "aroma": "high",
        "aftertaste": "medium"
      },
      "summary": {
        "zh": "明亮莓果酸、花香突出、轻盈干净。",
        "en": "Bright berry acidity, floral, clean and light."
      },
      "origin": {
        "country": { "zh": "埃塞俄比亚", "en": "Ethiopia" },
        "region": { "zh": "古吉", "en": "Guji" },
        "flag": "🇪🇹",
        "altitude": "1900–2100m",
        "notes": {
          "zh": "古吉位于埃塞俄比亚南部，高海拔、昼夜温差大，盛产花香与莓果调性突出的水洗与日晒处理咖啡。",
          "en": "Guji, in southern Ethiopia, sits at high altitude with big diurnal swings — known for washed and natural coffees with pronounced floral and berry character."
        }
      }
    }
  ]
}
```

- [ ] **Step 2: Create the images placeholder**

```bash
mkdir -p docs/diary/images
touch docs/diary/images/.gitkeep
```

- [ ] **Step 3: Delete the old blog scaffold**

```bash
git rm docs/blog.html docs/blog-posts.json docs/blog/posts/.gitkeep
# remove now-empty blog dir if present
rmdir docs/blog/posts docs/blog 2>/dev/null || true
```

- [ ] **Step 4: Verify JSON is valid**

Run: `python3 -m json.tool docs/diary.json > /dev/null && echo OK`
Expected: prints `OK` (no JSON errors).

- [ ] **Step 5: Commit**

```bash
git add docs/diary.json docs/diary/images/.gitkeep
git commit -m "feat(diary): seed diary.json and remove empty blog scaffold"
```

---

## Task 2: Shared stylesheet `docs/diary.css`

**Files:**
- Create: `docs/diary.css`

- [ ] **Step 1: Write the full stylesheet**

```css
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:           #f5f4f8;
  --surface:      #ffffff;
  --border:       #ebe8f0;
  --text:         #1a1625;
  --muted:        #7c6e8a;
  --subtle:       #b8aec6;
  --pink:         #ff6b9d;
  --orange:       #ff8c42;
  --header-h:     64px;

  /* coffee-diary color blocks */
  --hero-pink:    #f7d4e0;
  --hero-peach:   #fbe3d4;
  --hero-blue:    #d9e6f5;
  --hero-green:   #dceadb;
  --panel-peach:  #fceede;
  --panel-blue:   #e6eef8;
  --highlight:    #fbf3cf;
}

body {
  font-family: 'Inter', -apple-system, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  font-size: 13px;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

/* ── Header (matches existing site) ── */
header {
  height: var(--header-h);
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 0 28px;
  display: flex; align-items: center; justify-content: space-between;
  position: sticky; top: 0; z-index: 200;
  box-shadow: 0 1px 0 var(--border), 0 4px 16px rgba(0,0,0,.04);
}
.logo { display: flex; align-items: center; gap: 10px; text-decoration: none; color: inherit; }
.logo-icon {
  width: 34px; height: 34px; border-radius: 10px;
  background: linear-gradient(135deg, var(--pink) 0%, var(--orange) 100%);
  display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0;
}
.logo-text { font-size: 17px; font-weight: 800; letter-spacing: -0.5px; }
.logo-text em {
  font-style: normal;
  background: linear-gradient(90deg, var(--pink), var(--orange));
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.header-right { display: flex; align-items: center; gap: 16px; }
.nav-links { display: flex; gap: 4px; }
.nav-link {
  padding: 5px 13px; border-radius: 20px; font-size: 12.5px; font-weight: 600;
  font-family: inherit; text-decoration: none; color: var(--muted);
  border: 1.5px solid transparent; transition: all .15s;
}
.nav-link:hover { color: var(--pink); }
.nav-link.active { background: var(--surface); border-color: var(--border); color: var(--text); }
.lang-toggle {
  padding: 5px 12px; border-radius: 20px; font-size: 12px; font-weight: 700;
  font-family: inherit; cursor: pointer; color: var(--text);
  background: var(--surface); border: 1.5px solid var(--border); transition: all .15s;
}
.lang-toggle:hover { border-color: var(--pink); color: var(--pink); }

/* ── Generic editorial headings ── */
.section-title {
  font-size: 22px; font-weight: 900; letter-spacing: -0.5px;
  text-transform: uppercase; margin-bottom: 18px;
}

/* ── List page ── */
.list-page { max-width: 1100px; margin: 0 auto; padding: 40px 28px 80px; }
.list-head { margin-bottom: 24px; }
.list-title { font-size: 30px; font-weight: 900; letter-spacing: -0.8px; }
.list-intro { color: var(--muted); margin-top: 6px; font-size: 14px; }

.controls { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin-bottom: 28px; }
.search-box {
  flex: 1 1 260px; min-width: 200px; padding: 10px 14px;
  border: 1.5px solid var(--border); border-radius: 24px; font-family: inherit;
  font-size: 13px; color: var(--text); background: var(--surface);
}
.search-box:focus { outline: none; border-color: var(--pink); }
.filter-pills { display: flex; gap: 6px; flex-wrap: wrap; }
.filter-pill {
  padding: 7px 14px; border-radius: 20px; font-size: 12px; font-weight: 600;
  font-family: inherit; cursor: pointer; color: var(--muted);
  background: var(--surface); border: 1.5px solid var(--border); transition: all .15s;
}
.filter-pill:hover { border-color: var(--pink); }
.filter-pill.active { background: var(--text); color: #fff; border-color: var(--text); }

.card-grid {
  display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 20px;
}
.card {
  display: flex; flex-direction: column; text-decoration: none; color: inherit;
  background: var(--surface); border: 1.5px solid var(--border); border-radius: 16px;
  overflow: hidden; transition: border-color .15s, box-shadow .15s, transform .15s;
}
.card:hover { border-color: var(--pink); box-shadow: 0 6px 20px rgba(0,0,0,.07); transform: translateY(-2px); }
.card-thumb {
  aspect-ratio: 4 / 3; display: flex; align-items: center; justify-content: center; overflow: hidden;
}
.card-thumb img { width: 100%; height: 100%; object-fit: cover; }
.card-thumb-fallback { font-size: 52px; opacity: .55; }
.card-body { padding: 14px 16px 18px; }
.card-name { font-size: 16px; font-weight: 800; letter-spacing: -0.3px; line-height: 1.25; }
.card-roaster { font-size: 12px; color: var(--muted); margin-top: 3px; }
.card-flavours { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 12px; }
.chip {
  font-size: 11px; font-weight: 600; padding: 4px 9px; border-radius: 14px;
  background: var(--bg); border: 1px solid var(--border); color: var(--muted);
}

/* ── Empty states ── */
.empty-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  min-height: 320px; color: var(--muted); text-align: center;
}
.empty-state-icon { font-size: 48px; margin-bottom: 14px; }
.empty-state p { font-size: 15px; font-weight: 600; }
.empty-state small { font-size: 12px; color: var(--subtle); margin-top: 6px; }

/* ── Detail page ── */
.detail { max-width: 1100px; margin: 0 auto; }
.back-link {
  display: inline-block; margin: 20px 28px 0; font-size: 13px; font-weight: 600;
  color: var(--muted); text-decoration: none;
}
.back-link:hover { color: var(--pink); }

.hero { display: grid; grid-template-columns: 1fr 1fr; min-height: 520px; }
.hero-left {
  position: relative; display: flex; align-items: center; justify-content: center;
  padding: 40px; min-height: 420px;
}
.hero-img { max-height: 420px; max-width: 80%; object-fit: contain; }
.hero-img-fallback { font-size: 120px; opacity: .5; }
.hero-tags {
  position: absolute; left: 24px; bottom: 56px; right: 24px;
  display: flex; flex-wrap: wrap; gap: 7px;
}
.hero-tag {
  font-size: 11px; font-weight: 600; padding: 5px 12px; border-radius: 16px;
  background: rgba(255,255,255,.75); border: 1px solid rgba(0,0,0,.08); color: var(--text);
}
.hero-price {
  position: absolute; left: 0; bottom: 0; background: #000; color: #fff;
  font-size: 20px; font-weight: 800; padding: 10px 22px;
}
.hero-right { padding: 44px 48px; background: var(--surface); }
.bean-name { font-size: 34px; font-weight: 900; letter-spacing: -1px; line-height: 1.1; }
.bean-meta { font-size: 13px; color: var(--muted); margin-top: 10px; font-weight: 600; }

.flavour-row { display: flex; flex-wrap: wrap; gap: 22px; margin-top: 8px; }
.icon-item { display: flex; flex-direction: column; align-items: center; width: 76px; text-align: center; }
.icon-emoji { font-size: 30px; line-height: 1.4; }
.icon-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .3px; margin-top: 2px; }

.story { margin-top: 8px; }
.story p { font-size: 14.5px; line-height: 1.8; color: #2d2540; margin-bottom: 14px; }

/* panels */
.panel { padding: 44px 48px; }
.panel-peach { background: var(--panel-peach); }
.panel-blue { background: var(--panel-blue); }

.brew-method { font-size: 14.5px; font-weight: 600; margin-bottom: 22px; }
.icon-group { margin-bottom: 18px; }
.icon-group-title { font-size: 11px; font-weight: 800; letter-spacing: .6px; color: var(--muted); margin-bottom: 10px; }
.icon-row { display: flex; flex-wrap: wrap; gap: 20px; }

/* sliders */
.slider-row { margin-bottom: 20px; }
.slider-label { font-size: 12px; font-weight: 800; letter-spacing: .4px; margin-bottom: 8px; }
.slider-track {
  position: relative; height: 14px; border-radius: 8px; background: var(--surface);
  border: 1.5px solid var(--border);
}
.slider-dot {
  position: absolute; top: 50%; width: 20px; height: 20px; border-radius: 50%;
  background: var(--orange); border: 3px solid var(--surface); transform: translate(-50%, -50%);
  box-shadow: 0 1px 4px rgba(0,0,0,.2);
}
.slider-scale { display: flex; justify-content: space-between; font-size: 11px; color: var(--muted); margin-top: 5px; }

/* summary highlight */
.summary-wrap { padding: 30px 48px; background: var(--surface); }
.summary-box {
  background: var(--highlight); border-radius: 10px; padding: 18px 22px;
  font-size: 15px; font-weight: 600; line-height: 1.6; display: flex; gap: 12px; align-items: flex-start;
}
.summary-box .cup { font-size: 22px; flex-shrink: 0; }

/* origin */
.origin-name { font-size: 17px; font-weight: 800; margin-bottom: 6px; }
.origin-alt { font-size: 13px; color: var(--muted); font-weight: 600; margin-bottom: 14px; }
.origin-notes { font-size: 14px; line-height: 1.8; color: #2d2540; }

/* ── Responsive ── */
@media (max-width: 760px) {
  header { padding: 0 16px; }
  .hero { grid-template-columns: 1fr; }
  .hero-left { min-height: 300px; }
  .hero-right, .panel, .summary-wrap { padding: 28px 20px; }
  .bean-name { font-size: 27px; }
  .list-page { padding: 24px 16px 60px; }
  .card-grid { grid-template-columns: 1fr; }
}
```

- [ ] **Step 2: Verify file exists and is non-empty**

Run: `test -s docs/diary.css && echo OK`
Expected: prints `OK`. (Visual verification happens in Tasks 4–5.)

- [ ] **Step 3: Commit**

```bash
git add docs/diary.css
git commit -m "feat(diary): add shared stylesheet"
```

---

## Task 3: Shared JS module `docs/diary-common.js`

**Files:**
- Create: `docs/diary-common.js`

- [ ] **Step 1: Write the shared module**

```js
/* Coffee Diary — shared i18n + render helpers (no module system; attaches globals) */
(function () {
  const LANG_KEY = 'diary_lang';

  function getLang() {
    return localStorage.getItem(LANG_KEY) === 'en' ? 'en' : 'zh';
  }
  function setLang(lang) {
    localStorage.setItem(LANG_KEY, lang === 'en' ? 'en' : 'zh');
  }

  // Resolve a LocalizedString ({zh,en}) or plain string for the current language.
  function t(field, lang) {
    lang = lang || getLang();
    if (field == null) return '';
    if (typeof field === 'string') return field;
    return field[lang] || field.en || field.zh || '';
  }

  const UI = {
    zh: {
      navTracker: '追踪', navDiary: '日记',
      flavours: '风味', brewPairing: '冲煮 & 搭配', tasteProfile: '风味曲线',
      summary: '总评', origin: '产区',
      food: '食物', mood: '心情', time: '时段',
      dims: { acidity: '酸度', sweetness: '甜度', body: '醇厚', aroma: '香气', aftertaste: '余韵' },
      levels: { low: '弱', medium: '中', high: '强' },
      searchPlaceholder: '搜索豆名 / 烘焙商 / 产地 / 风味…',
      filterAll: '全部', roast: { filter: '手冲', espresso: '意式', omni: '通用' },
      emptyList: '还没有记录', emptyHint: '喝到好咖啡了就来记一笔',
      noMatch: '没有匹配的咖啡', back: '← 返回日记', notFound: '未找到这条记录',
      altitude: '海拔',
      listTitle: '咖啡日记', listIntro: '我喝过、记下来的每一支咖啡。'
    },
    en: {
      navTracker: 'Tracker', navDiary: 'Diary',
      flavours: 'Flavour Notes', brewPairing: 'Brew & Pairing', tasteProfile: 'Taste Profile',
      summary: 'Summary', origin: 'Origin',
      food: 'Food', mood: 'Mood', time: 'Time',
      dims: { acidity: 'Acidity', sweetness: 'Sweetness', body: 'Body', aroma: 'Aroma', aftertaste: 'Aftertaste' },
      levels: { low: 'Low', medium: 'Medium', high: 'High' },
      searchPlaceholder: 'Search bean / roaster / origin / flavour…',
      filterAll: 'All', roast: { filter: 'Filter', espresso: 'Espresso', omni: 'Omni' },
      emptyList: 'No entries yet', emptyHint: 'Had a good cup? Jot it down.',
      noMatch: 'No matching coffee', back: '← Back to diary', notFound: 'Entry not found',
      altitude: 'Altitude',
      listTitle: 'Coffee Diary', listIntro: 'Every cup I’ve had — and written down.'
    }
  };

  // Dotted-key lookup into UI for current language, e.g. ui('dims.acidity').
  function ui(key) {
    return key.split('.').reduce((o, k) => (o && o[k] != null ? o[k] : null), UI[getLang()]) ?? '';
  }

  const PROFILE_DIMS = ['acidity', 'sweetness', 'body', 'aroma', 'aftertaste'];
  const LEVELS = ['low', 'medium', 'high'];
  const HERO_COLORS = {
    pink: 'var(--hero-pink)', peach: 'var(--hero-peach)',
    blue: 'var(--hero-blue)', green: 'var(--hero-green)'
  };

  function esc(s) {
    return (s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;').replace(/'/g, '&#39;');
  }

  function formatDate(s) {
    try {
      return new Date(s).toLocaleDateString(getLang() === 'en' ? 'en-AU' : 'zh-CN',
        { year: 'numeric', month: 'long', day: 'numeric' });
    } catch (e) { return s; }
  }

  function heroColor(name) { return HERO_COLORS[name] || HERO_COLORS.pink; }

  // Header markup. active: 'tracker' | 'diary'
  function renderHeader(active) {
    const nextLabel = getLang() === 'zh' ? 'EN' : '中';
    return `
      <a href="index.html" class="logo">
        <div class="logo-icon">☕</div>
        <span class="logo-text">Coffee <em>Tracker</em></span>
      </a>
      <div class="header-right">
        <nav class="nav-links">
          <a href="index.html" class="nav-link${active === 'tracker' ? ' active' : ''}">${esc(ui('navTracker'))}</a>
          <a href="diary.html" class="nav-link${active === 'diary' ? ' active' : ''}">${esc(ui('navDiary'))}</a>
        </nav>
        <button class="lang-toggle" id="langToggle" type="button">${nextLabel}</button>
      </div>`;
  }

  // Wire the toggle button created by renderHeader. onChange() should re-render the page.
  function initLangToggle(onChange) {
    const btn = document.getElementById('langToggle');
    if (!btn) return;
    btn.addEventListener('click', function () {
      setLang(getLang() === 'zh' ? 'en' : 'zh');
      onChange();
    });
  }

  // One 3-level slider row for a taste dimension.
  function sliderRow(dimKey, value) {
    const idx = Math.max(0, LEVELS.indexOf(value));   // 0 | 1 | 2
    const pct = (idx / 2) * 100;                       // 0 | 50 | 100
    return `
      <div class="slider-row">
        <div class="slider-label">${esc(ui('dims.' + dimKey))}</div>
        <div class="slider-track"><span class="slider-dot" style="left:${pct}%"></span></div>
        <div class="slider-scale">
          <span>${esc(ui('levels.low'))}</span>
          <span>${esc(ui('levels.medium'))}</span>
          <span>${esc(ui('levels.high'))}</span>
        </div>
      </div>`;
  }

  // An icon group (food/mood/time). titleKey is a ui() key. Returns '' if empty.
  function iconGroup(titleKey, arr) {
    if (!arr || !arr.length) return '';
    const items = arr.map(it =>
      `<div class="icon-item">
         <div class="icon-emoji">${esc(it.icon)}</div>
         <div class="icon-label">${esc(t(it.label))}</div>
       </div>`).join('');
    return `<div class="icon-group">
      <div class="icon-group-title">${esc(ui(titleKey))}</div>
      <div class="icon-row">${items}</div>
    </div>`;
  }

  // Concatenated lowercased zh+en text of an entry, for search matching.
  function searchHaystack(e) {
    const parts = [];
    const push = v => {
      if (v && typeof v === 'object') { if (v.zh) parts.push(v.zh); if (v.en) parts.push(v.en); }
      else if (v) parts.push(v);
    };
    push(e.bean_name); push(e.roaster);
    if (e.origin) { push(e.origin.country); push(e.origin.region); }
    (e.tags || []).forEach(push);
    (e.flavours || []).forEach(f => push(f.label));
    return parts.join(' ').toLowerCase();
  }

  // Expose as a global namespace.
  window.Diary = {
    getLang, setLang, t, ui, esc, formatDate, heroColor,
    renderHeader, initLangToggle, sliderRow, iconGroup, searchHaystack,
    PROFILE_DIMS, LEVELS
  };
})();
```

- [ ] **Step 2: Verify the script parses (syntax check via Node)**

Run: `node --check docs/diary-common.js && echo OK`
Expected: prints `OK` (no syntax errors). If `node` is unavailable, skip — syntax is verified in the browser in Task 4.

- [ ] **Step 3: Commit**

```bash
git add docs/diary-common.js
git commit -m "feat(diary): add shared i18n and render helpers"
```

---

## Task 4: List page `docs/diary.html`

**Files:**
- Create: `docs/diary.html`

- [ ] **Step 1: Write the list page**

```html
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Coffee Diary</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="diary.css" />
</head>
<body>
<header id="siteHeader"></header>

<main class="list-page">
  <div class="list-head">
    <h1 class="list-title" id="listTitle"></h1>
    <p class="list-intro" id="listIntro"></p>
  </div>
  <div class="controls">
    <input type="text" class="search-box" id="search" />
    <div class="filter-pills" id="filterPills"></div>
  </div>
  <div id="results"></div>
</main>

<script src="diary-common.js"></script>
<script>
(function () {
  const D = window.Diary;
  const ROASTS = ['all', 'filter', 'espresso', 'omni'];
  const state = { q: '', roast: 'all' };
  let ALL = [];

  fetch('diary.json')
    .then(r => r.ok ? r.json() : Promise.reject(r.status))
    .then(data => {
      ALL = (data.entries || []).slice().sort((a, b) => (b.date || '').localeCompare(a.date || ''));
      render();
    })
    .catch(() => { ALL = []; render(); });

  function render() {
    document.documentElement.lang = D.getLang() === 'en' ? 'en' : 'zh';
    document.getElementById('siteHeader').innerHTML = D.renderHeader('diary');
    D.initLangToggle(render);

    document.getElementById('listTitle').textContent = D.ui('listTitle');
    document.getElementById('listIntro').textContent = D.ui('listIntro');

    const search = document.getElementById('search');
    search.placeholder = D.ui('searchPlaceholder');
    search.value = state.q;
    search.oninput = function () { state.q = this.value; renderResults(); };

    renderFilters();
    renderResults();
  }

  function renderFilters() {
    const wrap = document.getElementById('filterPills');
    wrap.innerHTML = ROASTS.map(r => {
      const label = r === 'all' ? D.ui('filterAll') : D.ui('roast.' + r);
      return `<button class="filter-pill${state.roast === r ? ' active' : ''}" data-roast="${r}" type="button">${D.esc(label)}</button>`;
    }).join('');
    wrap.querySelectorAll('.filter-pill').forEach(btn => {
      btn.addEventListener('click', () => {
        state.roast = btn.dataset.roast;
        renderFilters();
        renderResults();
      });
    });
  }

  function renderResults() {
    const q = state.q.trim().toLowerCase();
    const items = ALL.filter(e => {
      if (state.roast !== 'all' && e.roast_profile !== state.roast) return false;
      if (q && D.searchHaystack(e).indexOf(q) === -1) return false;
      return true;
    });
    const results = document.getElementById('results');

    if (!ALL.length) {
      results.innerHTML = emptyState('☕', D.ui('emptyList'), D.ui('emptyHint'));
      return;
    }
    if (!items.length) {
      results.innerHTML = emptyState('🔍', D.ui('noMatch'), '');
      return;
    }
    results.innerHTML = '<div class="card-grid">' + items.map(card).join('') + '</div>';
  }

  function card(e) {
    const thumb = e.image
      ? `<img src="${D.esc(e.image)}" alt="" />`
      : `<span class="card-thumb-fallback">☕</span>`;
    const flavours = (e.flavours || []).slice(0, 3).map(f =>
      `<span class="chip">${D.esc(f.icon)} ${D.esc(D.t(f.label))}</span>`).join('');
    return `<a class="card" href="diary-detail.html?slug=${encodeURIComponent(e.slug)}">
      <div class="card-thumb" style="background:${D.heroColor(e.color)}">${thumb}</div>
      <div class="card-body">
        <div class="card-name">${D.esc(D.t(e.bean_name))}</div>
        <div class="card-roaster">${D.esc(D.t(e.roaster))}</div>
        <div class="card-flavours">${flavours}</div>
      </div>
    </a>`;
  }

  function emptyState(icon, title, hint) {
    return `<div class="empty-state">
      <div class="empty-state-icon">${icon}</div>
      <p>${D.esc(title)}</p>
      ${hint ? `<small>${D.esc(hint)}</small>` : ''}
    </div>`;
  }
})();
</script>
</body>
</html>
```

- [ ] **Step 2: Start a local server**

```bash
python3 -m http.server 8000 --directory docs
```

- [ ] **Step 3: Verify list page in browser**

Open `http://localhost:8000/diary.html`. Confirm:
- Header shows logo + Tracker/Diary nav (Diary active) + a `EN` toggle button.
- Title "咖啡日记", one card "古吉 日晒 / Market Lane" with flavour chips and a pink thumbnail (☕ fallback).
- Typing "blueberry" or "蓝莓" in the search box keeps the card; typing "xyz" shows the "no match" state.
- Clicking the `espresso` filter pill hides the card; `全部`/`All` shows it again.
- Clicking `EN` switches all labels to English and flips the button to `中`; reloading the page keeps English.

Expected: all checks pass.

- [ ] **Step 4: Commit**

```bash
git add docs/diary.html
git commit -m "feat(diary): add searchable/filterable list page"
```

---

## Task 5: Detail page `docs/diary-detail.html`

**Files:**
- Create: `docs/diary-detail.html`

- [ ] **Step 1: Write the detail page**

```html
<!DOCTYPE html>
<html lang="zh">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Coffee Diary</title>
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet" />
  <link rel="stylesheet" href="diary.css" />
</head>
<body>
<header id="siteHeader"></header>
<a class="back-link" href="diary.html" id="backLink"></a>
<div class="detail" id="content"></div>

<script src="diary-common.js"></script>
<script>
(function () {
  const D = window.Diary;
  const slug = new URLSearchParams(location.search).get('slug');
  let ENTRY = null;

  fetch('diary.json')
    .then(r => r.ok ? r.json() : Promise.reject(r.status))
    .then(data => {
      ENTRY = (data.entries || []).find(e => e.slug === slug) || null;
      render();
    })
    .catch(() => { ENTRY = null; render(); });

  function render() {
    document.documentElement.lang = D.getLang() === 'en' ? 'en' : 'zh';
    document.getElementById('siteHeader').innerHTML = D.renderHeader('diary');
    D.initLangToggle(render);
    document.getElementById('backLink').textContent = D.ui('back');

    const wrap = document.getElementById('content');
    if (!ENTRY) {
      wrap.innerHTML = `<div class="empty-state">
        <div class="empty-state-icon">🤷</div>
        <p>${D.esc(D.ui('notFound'))}</p>
      </div>`;
      return;
    }
    wrap.innerHTML = hero(ENTRY) + brew(ENTRY) + profile(ENTRY) + summary(ENTRY) + origin(ENTRY);
  }

  function hero(e) {
    const img = e.image
      ? `<img class="hero-img" src="${D.esc(e.image)}" alt="" />`
      : `<span class="hero-img-fallback">☕</span>`;
    const tags = (e.tags || []).map(tag =>
      `<span class="hero-tag">${D.esc(D.t(tag))}</span>`).join('');
    const price = e.price_aud ? `<div class="hero-price">$${D.esc(e.price_aud)}</div>` : '';
    const flavours = (e.flavours || []).map(f =>
      `<div class="icon-item">
         <div class="icon-emoji">${D.esc(f.icon)}</div>
         <div class="icon-label">${D.esc(D.t(f.label))}</div>
       </div>`).join('');
    const flavourBlock = flavours
      ? `<h2 class="section-title" style="font-size:14px;margin-top:28px;margin-bottom:14px;">${D.esc(D.ui('flavours'))}</h2>
         <div class="flavour-row">${flavours}</div>` : '';
    const storyText = D.t(e.story);
    const story = storyText
      ? `<h2 class="section-title" style="font-size:14px;margin-top:28px;margin-bottom:12px;">NOTES</h2>
         <div class="story">${storyText.split('\n\n').map(p => `<p>${D.esc(p)}</p>`).join('')}</div>` : '';
    const meta = [D.t(e.roaster), D.formatDate(e.date)].filter(Boolean).join(' · ');

    return `<section class="hero">
      <div class="hero-left" style="background:${D.heroColor(e.color)}">
        ${img}
        ${tags ? `<div class="hero-tags">${tags}</div>` : ''}
        ${price}
      </div>
      <div class="hero-right">
        <h1 class="bean-name">${D.esc(D.t(e.bean_name))}</h1>
        ${meta ? `<div class="bean-meta">${D.esc(meta)}</div>` : ''}
        ${flavourBlock}
        ${story}
      </div>
    </section>`;
  }

  function brew(e) {
    const b = e.brew;
    if (!b) return '';
    const method = D.t(b.method)
      ? `<div class="brew-method">${D.esc(D.t(b.method))}</div>` : '';
    const groups = D.iconGroup('food', b.food) + D.iconGroup('mood', b.moods) + D.iconGroup('time', b.time);
    if (!method && !groups) return '';
    return `<section class="panel panel-peach">
      <h2 class="section-title">${D.esc(D.ui('brewPairing'))}</h2>
      ${method}${groups}
    </section>`;
  }

  function profile(e) {
    if (!e.profile) return '';
    const rows = D.PROFILE_DIMS
      .filter(dim => e.profile[dim])
      .map(dim => D.sliderRow(dim, e.profile[dim])).join('');
    if (!rows) return '';
    return `<section class="panel panel-peach">
      <h2 class="section-title">${D.esc(D.ui('tasteProfile'))}</h2>
      ${rows}
    </section>`;
  }

  function summary(e) {
    const text = D.t(e.summary);
    if (!text) return '';
    return `<section class="summary-wrap">
      <div class="summary-box"><span class="cup">☕</span><span>${D.esc(text)}</span></div>
    </section>`;
  }

  function origin(e) {
    const o = e.origin;
    if (!o) return '';
    const place = [D.t(o.region), D.t(o.country)].filter(Boolean).join(', ');
    const head = `${o.flag ? D.esc(o.flag) + ' ' : ''}${D.esc(place)}`;
    const alt = o.altitude ? `<div class="origin-alt">${D.esc(D.ui('altitude'))}: ${D.esc(o.altitude)}</div>` : '';
    const notes = D.t(o.notes) ? `<div class="origin-notes">${D.esc(D.t(o.notes))}</div>` : '';
    if (!place && !alt && !notes) return '';
    return `<section class="panel panel-blue">
      <h2 class="section-title">${D.esc(D.ui('origin'))}</h2>
      ${place ? `<div class="origin-name">${head}</div>` : ''}
      ${alt}${notes}
    </section>`;
  }
})();
</script>
</body>
</html>
```

- [ ] **Step 2: Verify detail page in browser**

With the server running, open `http://localhost:8000/diary-detail.html?slug=ethiopia-guji-natural`. Confirm:
- Back link "← 返回日记" at top; clicking a card from `diary.html` lands here.
- Hero: pink left block with ☕ fallback, tag pills bottom-left, black `$24.00` price bottom-left corner; right side shows big "古吉 日晒", meta "Market Lane · 2026年6月18日", FLAVOUR row (🫐🍓🌸), NOTES paragraphs.
- Peach BREW & PAIRING panel with method line and FOOD/MOOD/TIME icon groups.
- Peach TASTE PROFILE panel with 5 slider rows; dots at right (acidity high), middle (sweetness/aftertaste), left (body).
- Yellow SUMMARY box with ☕.
- Blue ORIGIN panel: "🇪🇹 古吉, 埃塞俄比亚", altitude line, notes.
- `EN` toggle switches all section titles, dimension names, level scale (Low/Medium/High), and content to English and persists on reload.
- Visiting `?slug=nope` shows the "未找到" state.

Expected: all checks pass.

- [ ] **Step 3: Commit**

```bash
git add docs/diary-detail.html
git commit -m "feat(diary): add wine-style detail page"
```

---

## Task 6: Point homepage nav at the diary

**Files:**
- Modify: `docs/index.html` (the nav link currently at ~line 499)

- [ ] **Step 1: Update the nav link**

Find in `docs/index.html`:
```html
      <a href="blog.html" class="nav-link">Blog</a>
```
Replace with:
```html
      <a href="diary.html" class="nav-link">Diary</a>
```

- [ ] **Step 2: Verify no stale blog references remain**

Run: `grep -rn "blog" docs/ ; echo "exit:$?"`
Expected: no matches (grep exit `1` / "exit:1"). If any line references `blog.html` or `blog-posts.json`, fix it.

- [ ] **Step 3: Verify homepage nav in browser**

Open `http://localhost:8000/index.html`, click the `Diary` nav link → lands on `diary.html`. From the diary, click `Tracker` → returns to `index.html`.

Expected: navigation works both directions.

- [ ] **Step 4: Commit**

```bash
git add docs/index.html
git commit -m "feat(diary): replace homepage Blog nav with Diary"
```

---

## Task 7: Full acceptance pass (spec §9)

**Files:** none (verification only)

- [ ] **Step 1: Run the spec acceptance checklist**

With `python3 -m http.server 8000 --directory docs` running, verify against spec §9:
- `diary.html` lists the seed card; search box + roast filter pills filter correctly.
- Card → `diary-detail.html?slug=...` renders all sections; missing-data sections are hidden (temporarily blank a field like `brew` in `diary.json` to confirm the panel disappears, then restore it).
- Homepage `Diary` nav works; no `blog.*` files or references remain (`ls docs/blog* 2>/dev/null` shows nothing; `grep -rn blog docs/` is empty).
- 中/EN toggle works on both pages, persists across reload; both Chinese and English keywords match in search.
- Narrow the browser to ~375px: hero stacks vertically, card grid becomes single column.

- [ ] **Step 2: Stop the server**

Press Ctrl+C in the server terminal.

- [ ] **Step 3: Final confirmation**

Confirm all checks pass and the working tree is clean (`git status` shows nothing uncommitted for diary files).

---

## Self-Review

- **Spec coverage:** file structure (§3) → Tasks 1–6; data model (§4) → Task 1 seed + Task 3 `t()`/helpers; detail layout (§5) → Task 5; list page search/filter (§6) → Task 4; styling + lang toggle (§7) → Tasks 2–3; workflow (§8) is human+Claude, no code; acceptance (§9) → Task 7; non-goals (§10) respected (no backend/map/rating/pagination). ✅
- **Placeholder scan:** all steps contain real code/commands; no TBD/TODO. ✅
- **Type consistency:** `window.Diary` API (`t`, `ui`, `esc`, `formatDate`, `heroColor`, `renderHeader`, `initLangToggle`, `sliderRow`, `iconGroup`, `searchHaystack`, `PROFILE_DIMS`, `LEVELS`) defined in Task 3 and used with matching names in Tasks 4–5. `profile` values `"low"|"medium"|"high"` align with `LEVELS` and `sliderRow`. JSON field names in Task 1 match accessors in Tasks 4–5 (`bean_name`, `roaster`, `roast_profile`, `flavours[].label`, `brew.method/food/moods/time`, `origin.country/region/flag/altitude/notes`). ✅
