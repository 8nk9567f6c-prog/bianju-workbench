"""
Generate clean v5.0 index.html from ground up.
Reads data.json, embeds it, produces single-file HTML.
"""
import json

# Read data.json
with open('data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data['version'] = '5.0'
data['updated'] = '2026-05-31'

# Build libraryContent directly from 素材库 files
# We embed the full content since data.json no longer has it
import os

# Read the library content from our earlier script's output
# Actually, let's rebuild it from data.json backup
# Since we removed libraryContent from data.json, let's rebuild it
# But wait - we need it. Let me add it back to the data dict.

# For now, let's read the library content from the git history
# Actually, let me just reconstruct it from the local 素材库 files

# Build simple libraryContent structure
libraryContent = {
    "memes": {
        "title": "热梗名梗",
        "icon": "🔥",
        "updated": "2026-05-31",
        "sections": [
            {
                "name": "2026年5月最新热梗",
                "items": [
                    {"name": "水果AI短剧（柠檬和芭乐生草莓）", "origin": "抖音网友用AI工具生成的水果拟人短剧，柠檬和芭乐谈恋爱生下草莓，因设定离谱+AI画面荒诞而全网爆火", "data": "单条播放破亿，引发AI短剧类型热议", "usage": "AI漫剧方向：离谱但合理的设定可以成为传播爆点。水果拟人→仙草拟人→器物拟人，万物可拟人化"},
                    {"name": "《Enemy》双强搭档", "origin": "无限流民国短剧《Enemy》爆火，双人搭档在循环中互相托付后背", "data": "全网二创霸榜，势均力敌的搭档要比恋人难得太多太多成为出圈金句", "usage": "双主角关系设计：写搭档比写恋人更有化学反应"},
                    {"name": "Dream还我10万美刀", "origin": "海外主播Dream被合作方拖欠10万美元，粉丝发起全球维权", "data": "全球热搜，跨国维权出圈", "usage": "被欠钱+维权=最普世的情绪钩子"},
                    {"name": "雪山救狐/酱板鸭", "origin": "抖音博主在雪山上救了一只狐狸，狐狸天天带酱板鸭来报恩", "data": "连续剧式更新，单条最高播放8000万+", "usage": "动物报恩=最原始的情感钩子"}
                ]
            },
            {
                "name": "化用指南",
                "items": [
                    {"name": "热梗三步化用法", "usage": "第一步：提取热梗的核心情绪。第二步：映射到你的世界观。第三步：用你的角色重新演一遍"},
                    {"name": "时效性原则", "usage": "热梗保质期通常2-4周，优先用正在上升期的梗"}
                ]
            }
        ]
    },
    "quotes": {
        "title": "爆款台词",
        "icon": "💬",
        "updated": "2026-05-31",
        "sections": [
            {
                "name": "2026年5月最新",
                "items": [
                    {"text": "死这么早，孤儿寡母怎么办？", "source": "《给阿嬷的情书》", "note": "最朴素的语言有最强的力量"},
                    {"text": "今日我二人，以此身此魂镇压尔等罪人！", "source": "《Enemy》", "note": "仪式化牺牲台词——用咒的形式说誓言"},
                    {"text": "势均力敌的搭档要比恋人难得太多太多！", "source": "《Enemy》", "note": "写搭档比写恋人更有化学反应"},
                    {"text": "上一世我拼尽全力修成天下第一，这一世我只想做条咸鱼。", "source": "《咸鱼飞升》", "note": "反内卷是2026的集体情绪"},
                    {"text": "看着你的腹肌我听不进去任何话。", "source": "《今晚正好》", "note": "直球台词=短视频金矿"}
                ]
            },
            {
                "name": "大女主觉醒类",
                "items": [
                    {"text": "请务必一而再再而三地救自己于水火。", "source": "《好一个乖乖女》", "template": "\"请务必___\"——万能觉醒句式"},
                    {"text": "麻烦你，风光又体面地活着，活给我看！", "source": "《好一个乖乖女》", "template": "\"麻烦你，___地活着\""},
                    {"text": "从今天起，我不再做你的妻子。", "source": "万能觉醒句", "template": "\"从今天起，我不再做___的___\""}
                ]
            },
            {
                "name": "霸总/忠犬护妻类",
                "items": [
                    {"text": "我是你的狗！", "source": "《栀栀复栀栀》第5集", "template": "\"我是你的___\"——卑微到尘埃的告白"},
                    {"text": "家规只有一条——惹江晚栀，不行！", "source": "《栀栀复栀栀》第42集", "template": "\"规矩只有一条——惹___，不行！\""},
                    {"text": "踩着我的肩膀爬到你所能爬到的最高点！", "source": "《好一个乖乖女》", "template": "\"踩着我的___，爬到___\"——托举式爱情"},
                    {"text": "你再骗骗我，我很好骗的。", "source": "《栀栀复栀栀》第65集", "template": "爱到甘愿被骗的绝望告白"}
                ]
            },
            {
                "name": "复仇打脸类",
                "items": [
                    {"text": "三年前你杀我的时候，想过今天吗。", "source": "《重生千亿》", "template": "\"[时间]前你[做过的事]，想过今天吗\""},
                    {"text": "你以为的金手指，其实是别人的玩具。", "source": "行业通用金句", "template": "\"你以为的___，其实是别人的___\""}
                ]
            },
            {
                "name": "万能台词公式",
                "items": [
                    {"text": "万能反转句：\"我以为___，原来___。\"", "source": "通用"},
                    {"text": "万能碾压句：\"你以为___？不，___。\"", "source": "通用"},
                    {"text": "万能情感句：\"___年了，你终于___了。可惜___。\"", "source": "通用"}
                ]
            }
        ]
    },
    "scenes": {
        "title": "名场面",
        "icon": "🎬",
        "updated": "2026-05-31",
        "sections": [
            {
                "name": "2026年5月最新名场面",
                "items": [
                    {"name": "《Enemy》民国篇——戏台殉国", "episode": "第5集", "data": "五一全网爆发，B站二创霸榜，央视点名表扬", "why": "仪式感拉满+家国情怀+5000元拍出电影质感", "template": "仪式化牺牲：咒语式台词+身体动作+旁观者震撼→切黑"},
                    {"name": "《给阿嬷的情书》——死这么早孤儿寡母怎么办", "episode": "全片最催泪名场面", "data": "电影黑马，票房11亿+，豆瓣9.1", "why": "最朴素的语言有最强的力量+即兴的真实感无法复制", "template": "朴素力量：用角色最本能的一句话制造最大情感冲击"}
                ]
            },
            {
                "name": "高转化名场面拆解",
                "items": [
                    {"name": "#1 首富女儿下跪喊爸", "source": "《都市神医》第1集末", "structure": "主角完成小事→高身份角色低姿态→信息揭露一半→表情最大瞬间切黑", "why": "信息炸弹+关键处切断+身份反差"},
                    {"name": "#2 女主自己跳下楼梯", "source": "《重生千亿》第6集", "structure": "制造主角犯错场面→所有人指责→揭示真相(主角早算到)→主角平静", "why": "观众也被骗+双重打脸+微笑封神"},
                    {"name": "#3 我是你的狗", "source": "《栀栀复栀栀》第5集", "structure": "建立高姿态→制造失去危机→超越底线举动→极端比喻封神", "why": "上位者为爱低头+台词冲击力+情感浓度拉满"},
                    {"name": "#4 天师令解封", "source": "《离婚后天师身份藏不住》第1集", "structure": "日常动作特写→身体异常变化→扩散到环境→旁观者震惊→大环境呼应", "why": "0.5秒建立世界观+五层视觉叠加+封印解除爽感"},
                    {"name": "#5 尸潮围超市", "source": "《我在末世开公司》第15集", "structure": "数据化绝望→出乎意料举动→举动有效→引发更大麻烦", "why": "极致压力数据化+荒诞笑点+智慧代替武力"}
                ]
            },
            {
                "name": "名场面设计三原则",
                "items": [
                    {"name": "视觉先行", "desc": "让摄影机能拍出震撼——0.5秒的金光炸裂>台词解释"},
                    {"name": "情绪蓄力", "desc": "炸之前让观众憋足一口气——名场面前至少5-10秒情绪蓄力"},
                    {"name": "切断留白", "desc": "在最关键画面上切断——未完成比已完成传播力强10倍"}
                ]
            }
        ]
    }
}

# Add libraryContent to data
data['libraryContent'] = libraryContent

# Make resourceLibrary URLs relative
if 'resourceLibrary' in data:
    data['resourceLibrary'].pop('baseUrl', None)
    data['resourceLibrary']['path'] = '素材库/'
    for f in data['resourceLibrary'].get('files', []):
        f['url'] = '素材库/' + f['name']

# Remove unused sections
data.pop('scripts', None)
data.pop('industry2026Q1', None)

# JSON data as compact string
json_str = json.dumps(data, ensure_ascii=False, separators=(',', ':'))

# Read the CSS/HTML template from current index.html
with open('index.html', 'r', encoding='utf-8') as f:
    current = f.read()

# Extract CSS (from <style> to </style>)
style_start = current.find('<style>')
style_end = current.find('</style>') + len('</style>')
css = current[style_start:style_end]

# Extract HTML skeleton (from <div class="app" to the closing </div> before <script>)
app_start = current.find('<div class="app" id="app">')
script_start = current.find('<script>', app_start)
html_skeleton = current[app_start:script_start]

# Generate the COMPLETE new index.html
new_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no,viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#1a1a2e">
<title>编剧工作台 v5.0</title>
<link rel="manifest" href="manifest.json">
{css}
</head>
<body>
<div id="offline-bar" style="display:none;background:#e94560;color:#fff;text-align:center;padding:6px;font-size:12px;position:fixed;top:0;left:0;right:0;z-index:1000">离线模式 — 数据已内嵌，功能完整</div>
<div id="install-banner" style="display:none;position:fixed;bottom:70px;left:16px;right:16px;background:#1a1a2e;border:1px solid var(--accent);border-radius:12px;padding:12px 16px;z-index:999;box-shadow:0 4px 24px rgba(0,0,0,0.5)">
  <div style="display:flex;align-items:center;gap:10px">
    <span style="font-size:28px">📱</span>
    <div style="flex:1"><strong style="font-size:14px">添加到主屏幕</strong><br><span style="font-size:11px;color:var(--sub)">一键打开编剧工作台</span></div>
    <button class="btn-install" id="btn-install">立即添加</button>
    <button class="btn-dismiss" id="btn-dismiss-install">&times;</button>
  </div>
</div>

{html_skeleton}

<script>
// ==================== Utilities ====================
function $(id) {{ return document.getElementById(id); }}
function debounce(fn, ms) {{ let t; return (...a) => {{ clearTimeout(t); t = setTimeout(() => fn(...a), ms); }}; }}

// ==================== Escape HTML ====================
var ESC_MAP = {{ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', \"'\": '&#39;' }};
function escapeHtml(str) {{
  if (!str) return '';
  return String(str).replace(/[&<>\"']/g, function(c) {{ return ESC_MAP[c]; }});
}}

// ==================== Global State (safe init) ====================
var DATA = {json_str};
var currentTab = 'dash';
var currentLib = 'memes';
var checkState = {{}};
var projects = (function() {{ try {{ return JSON.parse(localStorage.getItem('scripter_projects') || '[]'); }} catch(e) {{ return []; }} }})();
var activeProject = localStorage.getItem('scripter_active') || '';
var ruleSearchQuery = '';
var collapsedSections = {{}};
var deferredPrompt = null;
(function() {{
  var saved = localStorage.getItem('scripter_checks');
  if (saved) {{ try {{ checkState = JSON.parse(saved); }} catch(e) {{ checkState = {{}}; }} }}
}})();

// Mark version
$('data-version').textContent = '5.0';
$('sync-info').innerHTML = '<span style="color:#4caf84">● 已就绪</span> · v5.0 · 2026-05-31';

var RULE_SECTIONS = [
  {{key:'redlines', title:'🚫 写作红线（9条·零容忍）', tag:'tag-red'}},
  {{key:'iron', title:'⚡ 内容铁律（3条·每集强制）', tag:'tag-gold'}},
  {{key:'emotion', title:'🏦 情绪银行机制', tag:'tag-gold'}},
  {{key:'hooks', title:'🪝 钩子工程学', tag:'tag-green'}},
  {{key:'rhythm', title:'🎵 节奏工程学', tag:'tag-green'}},
  {{key:'game', title:'🎮 游戏化系统设计', tag:'tag-gold'}},
  {{key:'character', title:'👤 人物驱动设计', tag:'tag-gold'}},
  {{key:'format', title:'📄 剧本格式规范', tag:'tag-green'}}
];

// ==================== Toast ====================
function toast(msg) {{
  var t = $('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(function() {{ t.classList.remove('show'); }}, 2000);
}}

// ==================== Tab Switching ====================
function switchTab(tab) {{
  if (currentTab === tab) {{ render(); return; }}
  currentTab = tab;
  document.querySelectorAll('.tab').forEach(function(t) {{ t.classList.remove('active'); }});
  document.querySelectorAll('.nav-btn').forEach(function(b) {{ b.classList.remove('active'); }});
  document.querySelectorAll('[data-tab=\"' + tab + '\"]').forEach(function(el) {{ el.classList.add('active'); }});
  var content = $('tab-content');
  content.classList.add('loading');
  requestAnimationFrame(function() {{
    render();
    content.classList.remove('loading');
  }});
  window.scrollTo(0, 0);
}}

// ==================== Render ====================
function render() {{
  var c = $('tab-content');
  if (!DATA) {{ c.innerHTML = '<div class=\"card\" style=\"text-align:center\"><p>数据加载中...</p></div>'; return; }}

  // Preserve input focus
  var activeEl = document.activeElement;
  var selStart = 0, selEnd = 0, activeElId = null;
  if (activeEl && activeEl.tagName === 'INPUT' && activeEl.closest('#tab-content')) {{
    activeElId = activeEl.id;
    try {{ selStart = activeEl.selectionStart; selEnd = activeEl.selectionEnd; }} catch(e) {{}}
  }}

  var html = '';
  switch(currentTab) {{
    case 'dash': html = renderDash(); break;
    case 'flow': html = renderFlow(); break;
    case 'rules': html = renderRules(); break;
    case 'check': html = renderCheck(); break;
    case 'library': html = renderLibrary(); break;
  }}
  c.innerHTML = html;

  // Restore focus
  if (activeElId) {{
    var restored = document.getElementById(activeElId);
    if (restored) {{
      restored.focus();
      try {{ restored.setSelectionRange(selStart, selEnd); }} catch(e) {{}}
    }}
  }}

  bindTabEvents();
}}

// ==================== Dashboard ====================
function renderDash() {{
  var html = '<div class=\"card\"><h3>📊 项目总览</h3>';
  html += '<div class=\"stats\">';
  html += '<div class=\"stat\"><div class=\"num\">' + projects.length + '</div><div class=\"label\">项目数</div></div>';
  html += '<div class=\"stat\"><div class=\"num\">54</div><div class=\"label\">核心规则</div></div>';
  html += '<div class=\"stat\"><div class=\"num\">48</div><div class=\"label\">自检项</div></div>';
  html += '<div class=\"stat\"><div class=\"num\">9</div><div class=\"label\">写作红线</div></div>';
  html += '</div>';

  // Active project
  if (activeProject) {{
    html += '<div style=\"margin-top:8px;padding:8px 12px;background:rgba(240,192,96,0.08);border-radius:8px;font-size:12px\"><span style=\"color:var(--gold)\">📂 当前项目：</span>' + escapeHtml(activeProject) + '</div>';
  }}

  // Project list
  html += '<div style=\"margin-top:10px\">';
  projects.forEach(function(p, i) {{
    var isActive = p.name === activeProject;
    html += '<div style=\"display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);' + (isActive ? 'background:rgba(240,192,96,0.05);border-radius:6px;padding:6px 8px;' : '') + '\">';
    html += '<span style=\"font-size:14px\">📁</span>';
    html += '<div style=\"flex:1;font-size:12px;cursor:pointer\" data-select-project=\"' + escapeHtml(p.name) + '\"><strong>' + escapeHtml(p.name) + '</strong><br><span style=\"font-size:10px;color:var(--sub)\">' + escapeHtml(p.type || '') + ' · ' + escapeHtml(p.episodes || '') + '集</span></div>';
    html += '<button style=\"background:none;border:none;color:var(--sub);cursor:pointer;font-size:14px\" data-delete-project=\"' + escapeHtml(p.name) + '\">🗑</button>';
    html += '</div>';
  }});
  html += '</div>';
  html += '<button id=\"btn-new-project\" class=\"btn btn-outline btn-sm\" style=\"margin-top:8px\">+ 新建项目</button>';
  html += '</div>';

  // Core principles
  if (DATA.core) {{
    html += '<div class=\"card\"><h3>🎯 核心信条</h3>';
    html += '<div style=\"font-size:13px;color:var(--gold);margin-bottom:8px\">' + escapeHtml(DATA.core.motto) + '</div>';
    html += '<div style=\"font-size:12px;color:var(--sub);line-height:1.8\">';
    html += escapeHtml(DATA.core.newMotto) + '<br>';
    html += '公式：' + escapeHtml(DATA.core.formula) + '<br>';
    html += '平台：' + escapeHtml(DATA.core.platform) + '<br>';
    html += '受众：' + escapeHtml(DATA.core.audience);
    html += '</div></div>';
  }}

  // Hotlist
  if (DATA.hotlist && DATA.hotlist.length) {{
    html += '<div class=\"card\"><h3>🔥 红果+抖音 SS+ 实时热力榜</h3><div style=\"font-size:10px;color:var(--sub);margin-bottom:6px\">👆 点击剧名查看完整信息</div>';
    DATA.hotlist.forEach(function(h, i) {{
      var rankCls = h.rank === 1 ? 'r1' : h.rank === 2 ? 'r2' : h.rank === 3 ? 'r3' : 'rn';
      var heatCls = h.heat >= 95 ? 'super' : h.heat >= 85 ? 'high' : h.heat >= 75 ? 'mid' : 'low';
      html += '<div class=\"hotlist-item\" data-hotlist-idx=\"' + i + '\" style=\"cursor:pointer\">';
      html += '<div class=\"hot-rank ' + rankCls + '\">' + h.rank + '</div>';
      html += '<div class=\"hot-info\"><div class=\"hot-title\">' + escapeHtml(h.title) + '</div>';
      html += '<div class=\"hot-meta\">' + escapeHtml(h.type) + ' · ' + h.episodes + '集 · ' + escapeHtml(h.hook) + '</div>';
      html += '<div class=\"hot-highlight\">💡 ' + escapeHtml(h.highlight) + '</div></div>';
      html += '<div class=\"hot-heat\"><div class=\"hot-heat-bar\"><div class=\"hot-heat-fill ' + heatCls + '\" style=\"width:0%\" data-target=\"' + h.heat + '\"></div></div>';
      html += '<span class=\"hot-num\">' + h.heat + '°</span></div></div>';
    }});
    html += '</div>';
  }}

  // Theme tags
  if (DATA.hotThemeTags) {{
    html += '<div class=\"card\"><h3>🏷️ 火爆剧主题风向</h3><div class=\"theme-tags\">';
    DATA.hotThemeTags.forEach(function(t) {{
      var cls = t.heat >= 90 ? 't-fire' : t.heat >= 80 ? 't-hot' : 't-warm';
      html += '<span class=\"theme-tag ' + cls + '\">' + escapeHtml(t.tag) + ' <small>' + t.heat + '°</small></span>';
    }});
    html += '</div></div>';
  }}

  // Hook trends
  if (DATA.hookTrends) {{
    html += '<div class=\"card\"><h3>🪝 钩子风向</h3>';
    DATA.hookTrends.forEach(function(h, i) {{
      html += '<div class=\"hook-trend-row\" data-hook-idx=\"' + i + '\" style=\"cursor:pointer;display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04)\">';
      html += '<span class=\"hook-trend-icon\">' + h.icon + '</span>';
      html += '<div class=\"hook-trend-info\"><span class=\"hook-trend-name\">' + escapeHtml(h.hook) + '</span>';
      html += '<span class=\"hook-trend-desc\"> — ' + escapeHtml(h.desc) + '</span>';
      html += '<div class=\"hook-trend-theme\">🎬 ' + escapeHtml(h.theme) + '</div></div>';
      html += '<span class=\"hook-trend-rate\">' + h.rate + '%</span></div>';
      html += '<div class=\"hook-detail\" id=\"hook-detail-' + i + '\" style=\"display:none;padding:10px 14px;margin:0 0 4px 36px;background:rgba(255,255,255,0.02);border-radius:8px;font-size:11px;line-height:1.7;color:var(--sub);border-left:2px solid var(--border)\">';
      html += '<div style=\"color:var(--gold);font-weight:600;margin-bottom:6px\">📖 适用场景</div><div style=\"margin-bottom:8px\">' + escapeHtml(h.scenarios || '') + '</div>';
      html += '<div style=\"color:var(--accent);font-weight:600;margin-bottom:4px\">📍 最佳位置</div><div style=\"margin-bottom:8px\">' + escapeHtml(h.placement || '') + '</div>';
      html += '<div style=\"color:var(--green);font-weight:600;margin-bottom:4px\">🎬 爆款案例</div><div style=\"margin-bottom:8px\">' + escapeHtml(h.example || '') + '</div>';
      html += '<div style=\"color:#c084fc;font-weight:600;margin-bottom:4px\">🧠 观众心理</div><div>' + escapeHtml(h.psychology || '') + '</div></div>';
    }});
    html += '</div>';
  }}

  // Market trends
  if (DATA.trending) {{
    html += '<div class=\"card\"><h3>📡 市场动态</h3>';
    DATA.trending.forEach(function(t) {{
      var cls = t.heat >= 80 ? 'trend-hot' : t.heat >= 50 ? 'trend-new' : 'trend-up';
      html += '<div style=\"display:flex;align-items:center;gap:8px;padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:12px\">';
      html += '<span class=\"trend-tag ' + cls + '\">' + escapeHtml(t.type || '') + '</span>';
      html += '<span style=\"flex:1\">' + escapeHtml(t.label) + '</span>';
      if (t.heat) html += '<span class=\"trend-score\">' + t.heat + '°</span>';
      html += '</div>';
    }});
    html += '</div>';
  }}

  // 素材库 quick link
  html += '<div class=\"card\"><h3>📚 素材库</h3>';
  html += '<p style=\"font-size:12px;color:var(--sub);margin-bottom:10px\">🔥 热梗名梗 · 💬 爆款台词 · 🎬 名场面</p>';
  html += '<button class=\"btn btn-outline btn-sm\" data-tab=\"library\" style=\"display:inline-block;width:auto;cursor:pointer\">📖 打开素材库</button>';
  html += '</div>';

  // Version info
  html += '<div class=\"card\"><h3>🔧 关于</h3>';
  html += '<div style=\"font-size:12px;color:var(--sub);line-height:1.8\">';
  html += '<div>✅ 数据已内嵌 — 无需网络即可使用</div>';
  html += '<div>📱 支持离线 · PWA可安装 · 跨平台</div>';
  html += '<div>📅 更新于 2026-05-31 · v5.0</div></div></div>';

  // Workflow preview
  html += '<div class=\"card\"><h3>📋 工作流速览</h3>';
  DATA.workflow.forEach(function(w) {{
    html += '<div style=\"display:flex;align-items:center;gap:10px;padding:8px 0;font-size:13px;border-bottom:1px solid rgba(255,255,255,0.04)\">';
    html += '<span style=\"font-size:18px\">' + w.icon + '</span>';
    html += '<div><strong>' + escapeHtml(w.cmd) + '</strong><br><span style=\"font-size:11px;color:var(--sub)\">' + escapeHtml(w.desc) + '</span></div></div>';
  }});
  html += '</div>';
  return html;
}}

// ==================== Workflow ====================
function renderFlow() {{
  var html = '<div class=\"card\"><h3>📋 推荐工作流顺序</h3>';
  DATA.workflow.forEach(function(w, i) {{
    html += '<div class=\"step\"><div class=\"step-num\">' + (i+1) + '</div><div class=\"step-info\">';
    html += '<div class=\"name\">' + w.icon + ' ' + escapeHtml(w.cmd) + '</div>';
    html += '<div class=\"desc\">' + escapeHtml(w.desc) + '</div></div></div>';
  }});
  html += '</div>';

  if (DATA.discipline) {{
    html += '<div class=\"card\"><h3>📐 产出纪律</h3>';
    html += '<div style=\"font-size:12px;line-height:1.8;color:var(--sub)\">';
    html += '<div style=\"color:var(--gold);margin-bottom:4px\">执行前预判：</div>';
    html += '<pre style=\"font-size:11px;background:rgba(255,255,255,0.03);padding:8px;border-radius:6px;white-space:pre-wrap\">' + escapeHtml(DATA.discipline.preOutput) + '</pre>';
    html += '<div style=\"color:var(--gold);margin:8px 0 4px\">执行后输出：</div>';
    html += '<pre style=\"font-size:11px;background:rgba(255,255,255,0.03);padding:8px;border-radius:6px;white-space:pre-wrap\">' + escapeHtml(DATA.discipline.postOutput) + '</pre>';
    html += '</div></div>';
  }}

  if (DATA.rules && DATA.rules.saveTheCat) {{
    html += '<div class=\"card\"><h3>🐱 Save the Cat! 节拍表 × 短剧映射</h3>';
    html += '<table style=\"width:100%;font-size:11px;border-collapse:collapse\">';
    html += '<tr style=\"color:var(--gold);border-bottom:1px solid var(--border)\"><th style=\"padding:6px;text-align:left\">#</th><th>节拍</th><th>72集</th><th>45集</th><th style=\"text-align:left\">任务</th></tr>';
    DATA.rules.saveTheCat.forEach(function(b) {{
      html += '<tr style=\"border-bottom:1px solid rgba(255,255,255,0.04)\"><td style=\"padding:6px\">' + b.beat + '</td><td style=\"padding:6px\">' + escapeHtml(b.name) + '</td><td style=\"padding:6px;text-align:center\">' + escapeHtml(b.ep72) + '</td><td style=\"padding:6px;text-align:center\">' + escapeHtml(b.ep45) + '</td><td style=\"padding:6px;font-size:10px;color:var(--sub)\">' + escapeHtml(b.task) + '</td></tr>';
    }});
    html += '</table></div>';
  }}
  return html;
}}

// ==================== Rules ====================
function renderRules() {{
  var html = '<div class=\"search-wrap\"><input type=\"text\" id=\"rule-search\" class=\"search-input\" placeholder=\"🔍 搜索规则...\" value=\"' + escapeHtml(ruleSearchQuery) + '\"></div>';
  var query = ruleSearchQuery.trim().toLowerCase();

  RULE_SECTIONS.forEach(function(section) {{
    var rules = DATA.rules[section.key];
    if (!rules) return;
    var filtered = rules;
    if (query) {{
      filtered = rules.filter(function(r) {{
        return (r.title && r.title.toLowerCase().indexOf(query) !== -1) || (r.desc && r.desc.toLowerCase().indexOf(query) !== -1);
      }});
    }}
    if (filtered.length === 0) return;

    var isCollapsed = query ? false : (collapsedSections[section.key] !== false);
    html += '<div class=\"card\"><div class=\"collapse-header\" data-section=\"' + section.key + '\" style=\"cursor:pointer;display:flex;align-items:center;gap:8px\">';
    html += '<span style=\"font-size:12px\">' + (isCollapsed ? '▶' : '▼') + '</span>';
    html += '<h3 style=\"margin:0\"><span class=\"' + section.tag + '\">' + section.title + '</span></h3></div>';
    if (!isCollapsed) {{
      html += '<div style=\"margin-top:8px\">';
      filtered.forEach(function(r) {{
        var title = r.title || '';
        var desc = r.desc || '';
        if (query) {{
          var escaped = query.replace(/[.*+?^\${{}}()|[\\]\\\\]/g, '\\\\$&');
          var re = new RegExp('(' + escaped + ')', 'gi');
          title = title.replace(re, '<mark>$1</mark>');
          desc = desc.replace(re, '<mark>$1</mark>');
        }}
        html += '<div style=\"padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.04);font-size:12px\"><strong>' + title + '</strong><br><span style=\"color:var(--sub)\">' + desc + '</span></div>';
      }});
      html += '</div>';
    }}
    html += '</div>';
  }});
  return html;
}}

// ==================== Checklist ====================
function renderCheck() {{
  var total = 0, checked = 0;
  DATA.checklist.forEach(function(cat) {{
    cat.items.forEach(function() {{ total++; }});
  }});

  var html = '<div class=\"card\"><h3>✅ 自检清单</h3>';
  html += '<div class=\"progress-bar\"><div class=\"progress-fill\" style=\"width:0%\" id=\"check-progress\" data-target=\"' + (total ? Math.round(Object.keys(checkState).filter(function(k) {{ return checkState[k]; }}).length / total * 100) : 0) + '\"></div></div>';
  html += '<div style=\"font-size:10px;color:var(--sub);margin:4px 0 12px\">' + Object.keys(checkState).filter(function(k) {{ return checkState[k]; }}).length + '/' + total + ' 项已完成</div>';

  DATA.checklist.forEach(function(cat) {{
    html += '<div style=\"margin-bottom:12px\"><div style=\"font-weight:700;font-size:13px;margin-bottom:6px;color:var(--gold)\">' + escapeHtml(cat.cat) + '</div>';
    cat.items.forEach(function(item) {{
      var isChecked = !!checkState[item];
      html += '<div class=\"check-item\" data-item=\"' + escapeHtml(item) + '\" style=\"cursor:pointer;display:flex;align-items:center;gap:8px;padding:4px 0;font-size:12px\">';
      html += '<span style=\"font-size:16px\">' + (isChecked ? '☑' : '☐') + '</span>';
      html += '<span style=\"' + (isChecked ? 'text-decoration:line-through;color:var(--sub)' : '') + '\">' + escapeHtml(item) + '</span></div>';
    }});
    html += '</div>';
  }});

  html += '<div style=\"display:flex;gap:8px;margin-top:12px\"><button class=\"btn btn-outline btn-sm\" id=\"btn-save-checks\">💾 保存进度</button><button class=\"btn btn-outline btn-sm\" id=\"btn-reset-checks\">🔄 重置</button></div>';
  html += '</div>';
  return html;
}}

// ==================== Library ====================
function renderLibrary() {{
  if (!DATA.libraryContent) {{
    return '<div class=\"card\" style=\"text-align:center\"><p>素材库数据加载中...</p></div>';
  }}
  var LC = DATA.libraryContent;
  var html = '';

  var activeLib = currentLib || 'memes';
  html += '<div class=\"tabs\" style=\"margin-bottom:12px\">';
  html += '<button class=\"tab' + (activeLib==='memes'?' active':'') + '\" data-lib=\"memes\">🔥 热梗名梗</button>';
  html += '<button class=\"tab' + (activeLib==='quotes'?' active':'') + '\" data-lib=\"quotes\">💬 爆款台词</button>';
  html += '<button class=\"tab' + (activeLib==='scenes'?' active':'') + '\" data-lib=\"scenes\">🎬 名场面</button>';
  html += '</div>';

  var content = LC[activeLib];
  if (!content) return html + '<div class=\"card\">暂无数据</div>';

  html += '<div class=\"card\"><h3>' + content.icon + ' ' + content.title + ' <span style=\"font-size:10px;color:var(--sub);font-weight:normal\">更新于 ' + content.updated + '</span></h3>';

  content.sections.forEach(function(section) {{
    html += '<div style=\"margin-bottom:16px\">';
    html += '<div style=\"color:var(--gold);font-weight:700;font-size:13px;margin-bottom:8px;padding-bottom:4px;border-bottom:1px solid var(--border)\">' + section.name + '</div>';

    section.items.forEach(function(item) {{
      if (activeLib === 'memes') {{
        html += '<div style=\"padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04)\">';
        html += '<div style=\"font-weight:600;font-size:13px;margin-bottom:4px\">' + escapeHtml(item.name) + '</div>';
        if (item.origin) html += '<div style=\"font-size:11px;color:var(--sub);margin-bottom:3px\">📌 ' + escapeHtml(item.origin) + '</div>';
        if (item.data) html += '<div style=\"font-size:11px;color:var(--accent);margin-bottom:3px\">📊 ' + escapeHtml(item.data) + '</div>';
        if (item.usage) html += '<div style=\"font-size:11px;color:var(--green);margin-bottom:3px\">💡 ' + escapeHtml(item.usage) + '</div>';
        html += '</div>';
      }} else if (activeLib === 'quotes') {{
        html += '<div style=\"padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04)\">';
        html += '<div style=\"font-size:14px;color:var(--gold);font-style:italic;margin-bottom:2px\">\"' + escapeHtml(item.text) + '\"</div>';
        html += '<div style=\"font-size:11px;\"><span style=\"color:var(--accent)\">' + escapeHtml(item.source || '') + '</span>';
        if (item.note) html += ' <span style=\"color:var(--sub)\">— ' + escapeHtml(item.note) + '</span>';
        if (item.template) html += ' <span style=\"display:block;color:var(--green);margin-top:2px\">📝 ' + escapeHtml(item.template) + '</span>';
        html += '</div></div>';
      }} else if (activeLib === 'scenes') {{
        html += '<div style=\"padding:8px 0;border-bottom:1px solid rgba(255,255,255,0.04)\">';
        html += '<div style=\"font-weight:600;font-size:13px;margin-bottom:2px\">' + escapeHtml(item.name) + '</div>';
        if (item.source) html += '<div style=\"font-size:11px;color:var(--accent)\">📺 ' + escapeHtml(item.source) + '</div>';
        if (item.episode) html += '<div style=\"font-size:11px;color:var(--sub)\">📍 ' + escapeHtml(item.episode) + '</div>';
        if (item.data) html += '<div style=\"font-size:11px;color:var(--accent);margin-top:2px\">📊 ' + escapeHtml(item.data) + '</div>';
        if (item.structure) html += '<div style=\"font-size:11px;color:var(--green);margin-top:3px\">🔧 结构：' + escapeHtml(item.structure) + '</div>';
        if (item.why) html += '<div style=\"font-size:11px;color:var(--gold);margin-top:2px\">⭐ 为什么爆：' + escapeHtml(item.why) + '</div>';
        if (item.template) html += '<div style=\"font-size:11px;color:var(--green);margin-top:2px\">💡 复用模板：' + escapeHtml(item.template) + '</div>';
        if (item.desc) html += '<div style=\"font-size:11px;color:var(--sub);margin-top:2px\">' + escapeHtml(item.desc) + '</div>';
        html += '</div>';
      }}
    }});
    html += '</div>';
  }});
  html += '</div>';

  // Link to full MD file
  var rl = DATA.resourceLibrary;
  if (rl && rl.files) {{
    var fileInfo = rl.files.find(function(f) {{ return f.name.indexOf(activeLib === 'memes' ? '热梗' : activeLib === 'quotes' ? '台词' : '场面') !== -1; }});
    if (fileInfo && fileInfo.url) {{
      html += '<div class=\"card\" style=\"text-align:center;font-size:11px;color:var(--sub)\">📄 <a href=\"' + escapeHtml(fileInfo.url) + '\" target=\"_blank\" rel=\"noopener\" style=\"color:var(--accent)\">查看完整 ' + content.title + ' 文档 →</a></div>';
    }}
  }}
  return html;
}}

// ==================== Bind Events ====================
function bindTabEvents() {{
  // Rule search
  var searchInput = document.getElementById('rule-search');
  if (searchInput) {{
    searchInput.addEventListener('input', debounce(function() {{
      ruleSearchQuery = this.value;
      render();
    }}, 200));
    // Focus at end
    searchInput.focus();
  }}

  // Progress bar animation
  var progressBar = document.getElementById('check-progress');
  if (progressBar) {{
    setTimeout(function() {{
      var target = progressBar.dataset.target;
      if (target) progressBar.style.width = target + '%';
    }}, 60);
  }}

  // Hotlist click
  document.querySelectorAll('[data-hotlist-idx]').forEach(function(el) {{
    el.addEventListener('click', function() {{
      var idx = parseInt(this.dataset.hotlistIdx);
      if (isNaN(idx) || !DATA.hotlist || !DATA.hotlist[idx]) return;
      showDramaDetail(DATA.hotlist[idx]);
    }});
  }});

  // Hook trend click
  document.querySelectorAll('[data-hook-idx]').forEach(function(el) {{
    el.addEventListener('click', function() {{
      var i = this.dataset.hookIdx;
      var detail = document.getElementById('hook-detail-' + i);
      if (detail) detail.style.display = detail.style.display === 'none' ? 'block' : 'none';
    }});
  }});

  // Project buttons
  var btnNew = document.getElementById('btn-new-project');
  if (btnNew) btnNew.addEventListener('click', newProject);

  document.querySelectorAll('[data-select-project]').forEach(function(el) {{
    el.addEventListener('click', function() {{
      selectProject(this.dataset.selectProject);
    }});
  }});

  document.querySelectorAll('[data-delete-project]').forEach(function(el) {{
    el.addEventListener('click', function(e) {{
      e.stopPropagation();
      deleteProject(this.dataset.deleteProject);
    }});
  }});

  // Check buttons
  var btnSave = document.getElementById('btn-save-checks');
  if (btnSave) btnSave.addEventListener('click', saveChecks);
  var btnReset = document.getElementById('btn-reset-checks');
  if (btnReset) btnReset.addEventListener('click', resetChecks);
}}

// ==================== Projects ====================
function newProject() {{
  var name = prompt('请输入项目名称：');
  if (!name || !name.trim()) return;
  var type = prompt('类型（男频/女频）：') || '';
  var episodes = prompt('预计集数：') || '';
  projects.push({{ name: name.trim(), type: type, episodes: episodes, created: new Date().toISOString().slice(0,10) }});
  try {{ localStorage.setItem('scripter_projects', JSON.stringify(projects)); }} catch(e) {{}}
  selectProject(name.trim());
  render();
}}

function selectProject(name) {{
  activeProject = name;
  localStorage.setItem('scripter_active', name);
  render();
}}

function deleteProject(name) {{
  if (!confirm('确定要删除项目「' + name + '」吗？')) return;
  projects = projects.filter(function(p) {{ return p.name !== name; }});
  if (activeProject === name) activeProject = '';
  try {{ localStorage.setItem('scripter_projects', JSON.stringify(projects)); }} catch(e) {{}}
  localStorage.setItem('scripter_active', activeProject);
  render();
}}

// ==================== Drama Detail ====================
function showDramaDetail(d) {{
  if (!d) return;
  var html = '<div style=\"font-size:12px;line-height:1.8\">';
  html += '<strong>📺 ' + escapeHtml(d.synopsis || '暂无简介') + '</strong><br><br>';
  html += '🎣 <strong>钩子拆解：</strong><br>' + escapeHtml(d.hookBreakdown || '暂无') + '<br><br>';
  html += '⭐ <strong>成功因素：</strong><br>' + escapeHtml(d.successFactors || '暂无') + '<br><br>';
  html += '⏱ <strong>节奏分析：</strong><br>' + escapeHtml(d.pacing || '暂无');
  html += '</div>';
  var w = window.open('', '_blank', 'width=400,height=600');
  if (w) {{
    w.document.write('<html><head><meta charset=\"UTF-8\"><title>' + escapeHtml(d.title || '') + '</title><style>body{{font-family:system-ui,sans-serif;background:#0d0d1a;color:#e0e0e0;padding:16px;line-height:1.8}}h2{{color:#f0c060}}</style></head><body><h2>#' + d.rank + ' ' + escapeHtml(d.title) + '</h2>' + html + '</body></html>');
    w.document.close();
  }}
}}

// ==================== Check State ====================
function saveChecksSilent() {{
  try {{ localStorage.setItem('scripter_checks', JSON.stringify(checkState)); }} catch(e) {{}}
}}
function saveChecks() {{
  saveChecksSilent();
  toast('自检进度已保存 ✓');
}}
function resetChecks() {{
  if (confirm('确定要重置全部自检项？')) {{
    checkState = {{}};
    saveChecksSilent();
    render();
  }}
}}

// ==================== SW + Install + Network ====================
function registerSW() {{
  if (!('serviceWorker' in navigator)) return;
  navigator.serviceWorker.register('sw.js', {{ scope: './' }})
    .then(function(reg) {{
      reg.addEventListener('updatefound', function() {{
        var newWorker = reg.installing;
        if (!newWorker) return;
        newWorker.addEventListener('statechange', function() {{
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {{
            toast('有新版本可用，刷新页面后更新');
          }}
        }});
      }});
    }})
    .catch(function() {{ console.warn('SW registration failed'); }});
}}

function setupInstallPrompt() {{
  if (localStorage.getItem('scripter_install_dismissed')) return;
  window.addEventListener('beforeinstallprompt', function(e) {{
    e.preventDefault();
    deferredPrompt = e;
    setTimeout(function() {{
      var banner = document.getElementById('install-banner');
      if (banner) banner.classList.add('show');
    }}, 3000);
  }});
  var btnInstall = document.getElementById('btn-install');
  if (btnInstall) {{
    btnInstall.addEventListener('click', async function() {{
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      var result = await deferredPrompt.userChoice;
      deferredPrompt = null;
      var banner = document.getElementById('install-banner');
      if (banner) banner.classList.remove('show');
      if (result.outcome === 'accepted') {{
        localStorage.setItem('scripter_install_dismissed', '1');
      }}
    }});
  }}
}}

function setupNetworkDetection() {{
  function updateStatus() {{
    var bar = document.getElementById('offline-bar');
    if (!navigator.onLine) {{
      if (bar) bar.classList.add('show');
    }} else {{
      if (bar) bar.classList.remove('show');
    }}
  }}
  window.addEventListener('online', updateStatus);
  window.addEventListener('offline', updateStatus);
  updateStatus();
}}

// ==================== Global Event Delegation ====================
document.getElementById('app').addEventListener('click', function(e) {{
  // Tab clicks
  var tab = e.target.closest('[data-tab]');
  if (tab) {{
    if (!tab.closest('#tabs') && !tab.closest('#nav') && !tab.closest('.card')) return;
    switchTab(tab.dataset.tab); return;
  }}

  // Check items
  var checkItem = e.target.closest('.check-item[data-item]');
  if (checkItem) {{
    var item = checkItem.dataset.item;
    checkState[item] = !checkState[item];
    saveChecksSilent();
    render();
    return;
  }}

  // Library sub-tabs
  var libTab = e.target.closest('[data-lib]');
  if (libTab) {{
    currentLib = libTab.dataset.lib;
    document.querySelectorAll('[data-lib]').forEach(function(t) {{ t.classList.remove('active'); }});
    libTab.classList.add('active');
    render();
    return;
  }}

  // Collapse headers
  var collapseHeader = e.target.closest('.collapse-header[data-section]');
  if (collapseHeader) {{
    var key = collapseHeader.dataset.section;
    collapsedSections[key] = collapsedSections[key] === false ? true : false;
    render();
    return;
  }}

  // Install banner dismiss
  var btnDismiss = e.target.closest('#btn-dismiss-install');
  if (btnDismiss) {{
    var banner = document.getElementById('install-banner');
    if (banner) banner.classList.remove('show');
    localStorage.setItem('scripter_install_dismissed', '1');
    return;
  }}
}});

// ==================== Init ====================
function init() {{
  registerSW();
  setupInstallPrompt();
  setupNetworkDetection();
  render();
}}

init();
</script>
</body>
</html>'''

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f"Generated index.html: {len(new_html)} bytes")
print(f"libraryContent keys: {list(data['libraryContent'].keys())}")

# Verify
if '"memes"' in new_html and '"quotes"' in new_html and '"scenes"' in new_html:
    print("PASS: All 3 library sections embedded")
else:
    print("FAIL: Missing library sections")

if 'loadData' not in new_html and 'refreshData' not in new_html:
    print("PASS: No fetch-based loading")
else:
    print("FAIL: loadData/refreshData still present")

if 'activeElId' in new_html:
    print("PASS: Focus preservation in render()")
else:
    print("FAIL: No focus preservation")

if 'try { return JSON.parse' in new_html:
    print("PASS: Safe localStorage parsing")
else:
    print("FAIL: Unsafe localStorage")
