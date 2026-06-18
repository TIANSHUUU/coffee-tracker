# Coffee Diary — 设计文档

- 日期：2026-06-18
- 项目：嵌入现有 `coffee-tracker` 静态站点（GitHub Pages，根目录 `docs/`）
- 灵感来源：Good Pair Days 葡萄酒详情页的"编辑杂志风"版式
- 在线地址：https://tianshuuu.github.io/coffee-tracker/

## 1. 目标

在现有 coffee-tracker 站点中新增一个个人**咖啡品鉴日记**板块，模仿葡萄酒详情页的版式骨架（大色块分区、风味图标行、风味滑条、高亮总评、产区块），内容围绕：豆名、烘焙商、产地、品种/处理、突出风味、冲煮搭配、品鉴笔记。

现有主页导航的 `Blog` 按钮当前指向空的 `blog.html`（`blog-posts.json` 为空，故"点击没反应"）。本项目用 Diary 取代它。

## 2. 范围与决策

| 项 | 决定 |
|---|---|
| 视觉风格 | **混合**：沿用现有 header/导航与配色变量保证站点统一；详情页内部采用葡萄酒页版式骨架 |
| 技术栈 | **纯静态 HTML/CSS/JS**，不引入框架（与现有站点一致） |
| 数据存储 | 单个 `diary.json`（结构化数组） |
| 录入工作流 | 用户在对话中口述信息，由 Claude 整理写入 `diary.json`；用户不手动编辑 |
| 入口 | 主页 `Blog` 按钮改为 `Diary`，指向 `diary.html` |
| 旧脚手架 | **删除** `docs/blog.html` 与 `docs/blog-posts.json` |
| 图标 | 风味/搭配先用 **emoji**（零依赖），日后可换 SVG |
| 产区 | **不做地图**，用 国旗 + 产区 + 海拔 文字块 |
| 列表页 | 卡片网格 + **关键词搜索框** + 烘焙度筛选 pill（filter/espresso/omni），纯前端即时过滤 |

## 3. 文件结构（均在 `docs/` 下）

| 文件 | 作用 |
|---|---|
| `docs/diary.html` | 日记列表/画廊页（含搜索 + 筛选），主页 Diary 按钮指向此 |
| `docs/diary-detail.html` | 葡萄酒风详情页，读 URL 参数 `?slug=xxx` 渲染 |
| `docs/diary.json` | 所有品鉴记录的结构化数组 |
| `docs/diary/images/` | 豆袋图（可选；缺图时用色块占位） |
| `docs/index.html` | 修改导航：`Blog`→`Diary`，链接 `diary.html` |

删除：`docs/blog.html`、`docs/blog-posts.json`。
（`docs/blog/posts/.gitkeep` 一并清理。）

## 4. 数据模型（`diary.json`）

顶层：`{ "entries": [ <entry>, ... ] }`

每个 entry：

```jsonc
{
  "slug": "ethiopia-guji-natural",      // URL 唯一标识，kebab-case
  "date": "2026-06-18",                 // ISO 日期
  "bean_name": "Guji Natural",
  "roaster": "Market Lane",
  "image": "diary/images/guji.jpg",     // 可空；空则用色块占位
  "color": "pink",                      // hero 左侧色块主题: pink/peach/blue/green
  "roast_profile": "filter",            // filter/espresso/omni —— 用于列表筛选
  "price_aud": "24.00",                 // 字符串，可空
  "tags": ["Ethiopia","Natural","Filter","1900–2100m","Heirloom"],
  "flavours": [                         // 风味图标行
    {"icon":"🫐","label":"Blueberry"},
    {"icon":"🌸","label":"Floral"}
  ],
  "story": "品鉴笔记 + 豆子背景，支持多段(以\\n\\n分段)",
  "brew": {
    "method": "V60 · 1:16 · 92°C",      // 冲煮参数，自由文本
    "food":  [{"icon":"🥐","label":"Croissant"}],
    "moods": [{"icon":"😌","label":"Calm"}],
    "time":  [{"icon":"🌅","label":"Morning"}]
  },
  "profile": {                          // 杯测滑条，整数 1–5
    "acidity":4, "sweetness":3, "body":2,
    "bitterness":1, "aftertaste":3, "balance":4
  },
  "summary": "明亮莓果酸、花香突出、轻盈干净。",
  "rating": 4.5,                        // 可选，0–5，半星粒度
  "origin": {
    "country":"Ethiopia", "region":"Guji", "flag":"🇪🇹",
    "altitude":"1900–2100m", "notes":"产区介绍…"
  }
}
```

字段约定：
- 除 `slug`/`bean_name` 外字段均可缺省；渲染时缺省区块整体隐藏（如无 `brew` 则不渲染 BREW & PAIRING）。
- `profile` 滑条为 1–5 整数；渲染为横条 + 圆点位置 `(value-1)/4`。
- `color` 仅控制 hero 左侧色块主题，取自一组预设。

## 5. 详情页版式（`diary-detail.html`）

复用现有站点 header（logo + 导航，Diary 高亮）。主体自上而下：

1. **Hero（左右分栏）**
   - 左（sticky，色块底由 `color` 决定）：豆袋图（缺图→大号 ☕ 占位）；底部一排 pill `tags`；左下黑底白字 `price_aud`。
   - 右（白底）：大粗体 `bean_name`；下方小字 `roaster` + 日期；分享按钮；**FLAVOUR NOTES** emoji 图标行；**NOTES** 故事正文（`story`，按段渲染）。
2. **BREW & PAIRING（杏色块）**：`brew.method` 文本 + 分类图标组 FOOD / MOOD / TIME（各一行 emoji+label）。
3. **TASTE PROFILE（杏色块）**：6 条横向滑条（酸 / 甜 / 醇厚 / 苦 / 余韵 / 平衡），圆点标档位。
4. **SUMMARY（奶油黄高亮条）**：`summary` 一句话 + `rating` 星级（满分 5，支持半星）。
5. **ORIGIN（淡蓝色块）**：`origin.flag` + `country/region` + `altitude` + `notes`。

缺失数据的区块整体不渲染。`slug` 不存在时显示友好的"未找到"占位并提供返回列表链接。

## 6. 列表页（`diary.html`）

- 页眉：标题 + 一句简介。
- 控件区：关键词搜索框 + 烘焙度筛选 pill（All / filter / espresso / omni）。
- 卡片网格（响应式）：每张卡 = 豆袋缩略图（色块底）+ `bean_name` + `roaster` + 风味 chips + `rating`，点击进 `diary-detail.html?slug=...`。
- **搜索**：纯前端，对 `bean_name`、`roaster`、`origin.country/region`、`tags`、`flavours.label` 做大小写不敏感包含匹配。
- **筛选**：按 `roast_profile` 过滤；与搜索叠加（AND）。
- 空数据/无匹配：显示友好占位文案。

## 7. 样式

- 复用 `blog.html`/`index.html` 既有 CSS 变量（Inter 字体、粉橙色系、圆角、淡紫底）。
- 新增柔和大色块变量：`--hero-pink`、`--hero-peach`、`--hero-blue`、`--hero-green`、`--panel-peach`、`--panel-blue`、`--highlight-yellow`。
- 标题字重 800–900 营造编辑感；不引入新字体。
- 移动端：Hero 分栏在窄屏堆叠为上下；列表网格降为单列。

## 8. 录入工作流

用户在对话中口述某支咖啡的信息与品鉴感受（可零散口语）；Claude 整理为一个 entry 对象，追加进 `docs/diary.json`（生成 `slug`、补全可选字段、必要时留空）。图片由用户另行放入 `docs/diary/images/` 或暂留空用占位。

## 9. 测试 / 验收

纯静态站点，手动验收：
- `diary.html` 本地打开能列出种子数据卡片；搜索框与筛选 pill 正常过滤。
- 点击卡片进入 `diary-detail.html?slug=...`，各区块按数据渲染、缺省区块隐藏。
- 主页导航 Diary 按钮跳转正确，旧 blog 文件已删除且无残留引用。
- 移动端窄屏布局正常堆叠。
- 至少 1 条种子 entry，确保页面非空、可视觉验证。

## 10. 非目标（YAGNI）

- 不做后端、登录、评论。
- 不做手绘图标与产区地图（后续可选升级）。
- 不做分页（数据量小，一次性渲染 + 前端过滤足够）。
- 不与 `data.json`（自动抓取的在售豆列表）打通——日记是独立的个人记录。
