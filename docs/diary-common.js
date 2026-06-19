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
      flavours: '风味', notes: '笔记', brew: '冲煮', tasteProfile: '风味曲线',
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
      flavours: 'Flavour Notes', notes: 'Notes', brew: 'Brew', tasteProfile: 'Taste Profile',
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
    pink: 'var(--wash-pink)', peach: 'var(--wash-peach)',
    blue: 'var(--wash-blue)', green: 'var(--wash-green)'
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
      <a href="index.html" class="wordmark">Coffee <span class="wm-accent">Diary</span></a>
      <div class="header-right">
        <nav class="nav-links">
          <a href="index.html" class="nav-link${active === 'tracker' ? ' active' : ''}">${esc(ui('navTracker'))}</a>
          <a href="diary.html" class="nav-link${active === 'diary' ? ' active' : ''}">${esc(ui('navDiary'))}</a>
        </nav>
        <button class="lang-toggle" id="langToggle" type="button" aria-label="language">${nextLabel}</button>
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
