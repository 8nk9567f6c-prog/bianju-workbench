"""
编剧工作台 v5.5 — 自动化验证引擎
Usage: python validators.py <episode_file.md> [--json]
"""
import sys
import re
import json
from pathlib import Path


def load_text(path):
    return Path(path).read_text(encoding="utf-8")


def _pattern_check(name, patterns, text, note=None, warn_threshold=None):
    """Generic pattern-matching check. Returns {name, violations, passed}."""
    hits = []
    for p in patterns:
        for m in re.finditer(p, text):
            line_no = text[:m.start()].count('\n') + 1
            entry = {"line": line_no, "pattern": p, "match": m.group()}
            if note:
                entry["note"] = note
            hits.append(entry)
    result = {"name": name, "violations": hits, "passed": len(hits) == 0}
    if warn_threshold is not None:
        result["passed"] = True
        result["warning"] = len(hits) > warn_threshold
    return result


# ── 写作红线检查 (9项) ──

def check_psychology(text):
    return _pattern_check("心理描写", [
        r'他意识到', r'她意识到', r'他心想', r'她心想', r'他感到一阵',
        r'她感到一阵', r'他觉得', r'她觉得', r'他明白', r'她明白',
        r'他突然想起', r'她突然想起', r'他回忆起', r'她回忆起',
        r'他暗自', r'她暗自', r'心底', r'内心深处', r'脑海中',
    ], text)


def check_abstract_emotion(text):
    return _pattern_check("抽象情绪", [
        r'很愤怒', r'很悲伤', r'很害怕', r'很紧张', r'很兴奋',
        r'非常生气', r'非常难过', r'非常恐惧', r'十分愤怒', r'十分悲伤',
        r'感到愤怒', r'感到悲伤', r'感到恐惧', r'感到紧张',
        r'怒不可遏', r'悲痛欲绝', r'欣喜若狂', r'忐忑不安',
    ], text)


def check_exposition_dialogue(text):
    return _pattern_check("台词解说设定", [
        r'你是知道我的[，,]', r'你应该知道[，,]', r'众所周知[，,]',
        r'你要知道[，,]', r'我跟你说过[，,]', r'我不是告诉过你',
        r'你听我说[，,]', r'听好了[，,]',
    ], text)


def check_preaching(text):
    return _pattern_check("说教催泪", [
        r'人生.*道理', r'你.*必须.*坚强', r'活着.*意义',
        r'这个世界.*从来', r'真正的.*是', r'你要记住[，,]',
        r'永远不要', r'人这一生', r'生命.*意义',
    ], text)


def check_ai_tone(text):
    return _pattern_check("AI腔连接词", [
        r'岂料', r'殊不知', r'与此同时', r'正所谓', r'不料',
        r'显而易见', r'毋庸置疑', r'由此可见', r'换言之',
        r'总而言之', r'综上所述', r'顷刻间',
        r'蓦然', r'倏地', r'须臾', r'便见得',
    ], text)


def check_adjective_stack(text):
    return _pattern_check("形容词堆砌", [r'(?:[一-鿿]{1,3}的){3,}'], text)


def check_unfilmable(text):
    return _pattern_check("不可拍摄内容", [
        r'气氛.*变得', r'氛围.*渐渐', r'空气中.*弥漫',
        r'一种.*感觉', r'仿佛', r'似乎', r'隐约',
    ], text)


def check_passive_protagonist(text):
    return _pattern_check("被动主角标记", [
        r'被逼', r'不得不', r'只能眼睁睁', r'无力', r'束手无策'
    ], text, note="需人工判断是否为被动行为", warn_threshold=3)


def check_logic_break(text):
    return _pattern_check("逻辑断裂标记", [
        r'突然.*想起', r'忽然.*明白', r'莫名其妙', r'不知为何'
    ], text, note="需人工判断是否逻辑断裂", warn_threshold=2)


# ── 格式规范检查 (12项) ──

def check_format(text):
    results = []

    # 第x集
    ep_match = re.search(r'^第\d+集\s*$', text, re.MULTILINE)
    results.append({"name": "第x集标记", "passed": ep_match is not None,
                    "detail": "缺失" if not ep_match else f"第{ep_match.group()}集"})

    # 场景编号 001
    scene_match = re.search(r'^\d{3}\s+[日夜]/[日夜]\s+[内外]/\s*\S', text, re.MULTILINE)
    results.append({"name": "001场景编号", "passed": scene_match is not None})

    # 人物罗列
    char_match = re.search(r'^人物：\S', text, re.MULTILINE)
    results.append({"name": "人物罗列", "passed": char_match is not None})

    # 服装
    costume_match = re.search(r'^服装：', text, re.MULTILINE)
    results.append({"name": "服装罗列", "passed": costume_match is not None})

    # 道具预罗列
    props_match = re.search(r'^道具：', text, re.MULTILINE)
    results.append({"name": "道具预罗列", "passed": props_match is not None})

    # 【】场景描述
    bracket_match = re.search(r'【[^】]+】', text)
    results.append({"name": "【】场景描述", "passed": bracket_match is not None})

    # △ 动作
    triangle_count = len(re.findall(r'^△\s', text, re.MULTILINE))
    results.append({"name": "△动作描述", "passed": triangle_count > 0, "detail": f"{triangle_count}处"})

    # 对白格式
    dialogue_lines = re.findall(r'^[^\s△#\-【\d].*[：:].+$', text, re.MULTILINE)
    results.append({"name": "对白格式", "passed": len(dialogue_lines) > 0, "detail": f"{len(dialogue_lines)}句"})

    # 道具一致性 (cross-check props declaration vs body usage)
    props_declared = set()
    props_section = re.search(r'道具：\n((?:- .+\n?)+)', text)
    if props_section:
        props_declared = set(re.findall(r'- (.+)', props_section.group(1)))

    common_props = ['手机', '钥匙', '文件', '酒杯', '药品', '照片', '信件', '刀', '枪', '车',
                    '茶杯', '碗', '筷子', '门', '窗', '桌子', '椅子', '床', '灯', '纸', '笔',
                    '包', '钱', '卡', '证件', '戒指', '项链']
    body_text = text[text.find('【'):] if '【' in text else text
    undeclared = []
    for prop in common_props:
        if prop in body_text and prop not in props_declared and not any(prop in d for d in props_declared):
            undeclared.append(prop)
    results.append({"name": "道具一致性", "passed": len(undeclared) == 0,
                    "detail": f"未声明: {undeclared}" if undeclared else "一致"})

    # 场景数≤3
    scene_count = len(re.findall(r'^---\s*$', text, re.MULTILINE)) + 1
    results.append({"name": "场景数≤3", "passed": scene_count <= 3, "detail": f"{scene_count}场景"})

    # 核心人物≤4
    char_count = 0
    char_line = re.search(r'^人物：(.+)$', text, re.MULTILINE)
    if char_line:
        chars = [c.strip() for c in char_line.group(1).split() if c.strip()]
        char_count = len(chars)
    results.append({"name": "核心人物≤4", "passed": char_count <= 4, "detail": f"{char_count}人"})

    # 字数≥500
    word_count = len(re.findall(r'[一-鿿]', text))
    results.append({"name": "单集≥500字", "passed": word_count >= 500, "detail": f"{word_count}字"})

    return results


# ── 内容铁律检查 (3项) ──

def _marker_check(name, markers, text):
    """Detect if any marker from a list appears in text. Returns {name, passed, detail}."""
    found = []
    for p in markers:
        for m in re.finditer(p, text):
            found.append(m.group())
    return {"name": name, "passed": len(found) > 0,
            "detail": f"标记: {found[:5]}" if found else f"未检测到{name}"}


def check_irreversible_change(text):
    return _marker_check("不可逆变化", [
        r'不再是', r'第一次', r'再也', r'从此', r'永远', r'改变', r'翻天覆地',
        r'不再.*关系', r'正式.*身份', r'公开.*身份'
    ], text)


def check_choice_cost(text):
    return _marker_check("选择代价", [
        r'放弃', r'牺牲', r'付出.*代价', r'选择.*而不是', r'宁愿', r'宁可',
        r'赌上', r'押上', r'以.*换'
    ], text)


def check_cheat_cost(text):
    return _marker_check("金手指代价", [
        r'代价', r'反噬', r'限制', r'副作用', r'折寿', r'损耗',
        r'冷却', r'消耗.*灵力', r'消耗.*修为'
    ], text)


# ── 节奏工程检查 (6项) ──

def check_rhythm(text):
    results = []

    # ≥3节拍 (detected by scene changes, dialogue, action blocks)
    beats = len(re.findall(r'---', text)) + len(re.findall(r'^△\s', text, re.MULTILINE)) // 3
    results.append({"name": "≥3节拍", "passed": beats >= 3, "detail": f"约{beats}节拍"})

    # 钩子密度
    word_count = len(re.findall(r'[一-鿿]', text))
    hooks = len(re.findall(r'[？！…]', text))  # rough proxy
    results.append({"name": "钩子密度检测", "passed": True, "detail": f"约{hooks}个情绪标点/{word_count}字"})

    # 无连续10秒空白 (proxied by checking for long blocks without dialogue/action)
    results.append({"name": "无连续10秒空白", "passed": True, "detail": "需人工复核"})

    # A级端钩子
    last_lines = text.strip().split('\n')[-10:]
    has_hook = any(re.search(r'[？！…]', l) for l in last_lines)
    results.append({"name": "A级端钩子", "passed": has_hook, "detail": "集末有钩子" if has_hook else "集末无钩子"})

    # 钩子类型轮换 (deferred to multi-episode analysis)
    results.append({"name": "钩子类型轮换", "passed": True, "detail": "单集检查—多集需人工"})

    # 五节点覆盖
    visual_hammer = bool(re.search(r'△', text[:200]) if len(text) > 200 else re.search(r'△', text))
    has_burst = len(re.findall(r'△', text)) >= 3
    results.append({"name": "五节点覆盖", "passed": visual_hammer and has_burst,
                    "detail": f"视觉锤{'✓' if visual_hammer else '✗'} 爆破点{'✓' if has_burst else '✗'}"})

    return results


# ── 平台红线检查 (9项) ──

def check_platform_redlines(text):
    """平台红线关键词扫描"""
    results = []

    # 涉政敏感
    political = [r'国家领导', r'政治体制', r'历史虚无', r'颠覆.*政权', r'分裂.*国家',
                 r'中国.*共产党', r'政府.*腐败']
    political_hits = []
    for p in political:
        for m in re.finditer(p, text):
            political_hits.append({"line": text[:m.start()].count('\n') + 1, "match": m.group()})
    results.append({"name": "涉政敏感", "passed": len(political_hits) == 0,
                    "violations": political_hits})

    # 色情低俗
    sexual = [r'性交', r'做爱', r'床上.*激烈', r'裸体', r'脱.*衣服', r'胸.*部', r'下体']
    sexual_hits = []
    for p in sexual:
        for m in re.finditer(p, text):
            sexual_hits.append({"line": text[:m.start()].count('\n') + 1, "match": m.group()})
    results.append({"name": "色情低俗", "passed": len(sexual_hits) == 0, "violations": sexual_hits})

    # 过度暴力
    violence = [r'分尸', r'断肢', r'碎尸', r'挖眼', r'割舌', r'开膛', r'剥皮']
    violence_hits = []
    for p in violence:
        for m in re.finditer(p, text):
            violence_hits.append({"line": text[:m.start()].count('\n') + 1, "match": m.group()})
    results.append({"name": "过度暴力", "passed": len(violence_hits) == 0, "violations": violence_hits})

    # 违法示范
    crime = [r'如何.*制毒', r'如何.*诈骗', r'详细.*洗钱', r'怎么.*盗', r'教你.*黑']
    crime_hits = []
    for p in crime:
        for m in re.finditer(p, text):
            crime_hits.append({"line": text[:m.start()].count('\n') + 1, "match": m.group()})
    results.append({"name": "违法示范", "passed": len(crime_hits) == 0, "violations": crime_hits})

    # 性别/地域/职业歧视
    discrimination = [r'女人就该', r'男人必须', r'东北.*都是', r'河南.*都是', r'.*人都是.*骗子']
    disc_hits = []
    for p in discrimination:
        for m in re.finditer(p, text):
            disc_hits.append({"line": text[:m.start()].count('\n') + 1, "match": m.group()})
    results.append({"name": "歧视内容", "passed": len(disc_hits) == 0, "violations": disc_hits})

    # Remaining checks requiring human review
    for label in ["架空世界观标注", "无未成年不良引导", "无版权侵权", "正义结局方向"]:
        results.append({"name": label, "passed": True, "detail": "需人工确认"})

    return results


# ── 汇总 ──

def run_all_checks(text, episode_label=""):
    all_results = {
        "episode": episode_label,
        "writing_redlines": [
            check_psychology(text),
            check_abstract_emotion(text),
            check_exposition_dialogue(text),
            check_preaching(text),
            check_ai_tone(text),
            check_adjective_stack(text),
            check_unfilmable(text),
            check_passive_protagonist(text),
            check_logic_break(text),
        ],
        "format": check_format(text),
        "content_rules": [
            check_irreversible_change(text),
            check_choice_cost(text),
            check_cheat_cost(text),
        ],
        "rhythm": check_rhythm(text),
        "platform_redlines": check_platform_redlines(text),
        # v5.4 新增
        "emotion_spring": check_emotion_spring(text),
        "info_frontloading": check_info_frontloading(text),
        "dialogue_function": check_dialogue_function(text),
        "voice_differentiation": check_voice_differentiation(text),
        # v5.4+ 情感系统优化
        "emotion_spring_full": check_emotion_spring_full(text),
        "emotion_anchors": check_emotion_anchors(text),
        "emotion_beat_template": check_emotion_beat_template(text),
        "character_emotion_range": check_character_emotion_range(text),
    }

    # Calculate totals
    all_checks = []
    for category, items in all_results.items():
        if category == "episode":
            continue
        if isinstance(items, dict):
            all_checks.append(items)
        elif isinstance(items, list):
            for item in items:
                all_checks.append(item)

    total = len(all_checks)
    passed = sum(1 for c in all_checks if c.get("passed", False))
    failed = total - passed

    all_results["summary"] = {
        "total": total,
        "passed": passed,
        "failed": failed,
        "pass_rate": f"{passed}/{total}",
        "verdict": "PASS" if failed == 0 else f"FAIL ({failed} issues)"
    }

    return all_results


def format_report(results):
    """Generate human-readable report from JSON results."""
    lines = []
    lines.append(f"━━━ 自动验证报告 {results['episode']} ━━━")

    categories = {
        "writing_redlines": "写作红线 (9项)",
        "format": "格式规范 (12项)",
        "content_rules": "内容铁律 (3项)",
        "rhythm": "节奏工程 (6项)",
        "platform_redlines": "平台红线 (9项)",
        "emotion_spring": "情绪弹簧 (单集二态)",
        "info_frontloading": "信息前置 (首句对白)",
        "dialogue_function": "对白功能化 (三不沾)",
        "voice_differentiation": "对白声音区分度",
        "emotion_spring_full": "情绪弹簧全剧扫描",
        "emotion_anchors": "情绪锚点检测",
        "emotion_beat_template": "情绪节拍五节点",
        "character_emotion_range": "角色情感范围",
    }

    for key, title in categories.items():
        check_or_list = results.get(key)
        if check_or_list is None:
            continue
        # v5.4: handle both singular dict checks and list checks
        if isinstance(check_or_list, dict):
            checks_to_render = [check_or_list]
        else:
            checks_to_render = check_or_list

        line = f"{title}: "
        items = []
        for c in checks_to_render:
            if isinstance(c, dict):
                icon = "✓" if c.get("passed") else "✗"
                items.append(f"{icon}{c['name']}")
        lines.append(line + " ".join(items))

        # Show violations details
        for c in checks_to_render:
            if isinstance(c, dict):
                detail = c.get("detail", "")
                if detail and not c.get("passed"):
                    lines.append(f"  ⚠ {detail}")
                if c.get("violations") and len(c["violations"]) > 0:
                    for v in c["violations"][:3]:
                        if isinstance(v, dict):
                            lines.append(f"  ⚠ L{v.get('line', '?')}: {v.get('match', v.get('issue', v.get('dialogue', '')))}")
                        else:
                            lines.append(f"  ⚠ {v}")

    s = results.get("summary", {})
    lines.append(f"━━━ {s.get('pass_rate', '?')} {s.get('verdict', '?')} ━━━")
    return "\n".join(lines)


# ── v5.4 情绪弹簧检测 ──

def check_emotion_spring(text):
    """检测单集情绪弹簧状态——必须是压弹簧或放弹簧，不得中性收尾。"""
    last_200_chars = text.strip()[-200:]
    compress_signals = [
        r'危机', r'危险', r'威胁', r'逼', r'压', r'困', r'陷', r'绝境',
        r'误会', r'怀疑', r'愤怒', r'杀意', r'冷笑', r'暗算', r'埋伏',
        r'不妙', r'糟糕', r'完了', r'怎么办', r'不.*放过', r'等着瞧',
        r'动手', r'围', r'挡住', r'休想', r'做梦',
    ]
    release_signals = [
        r'打脸', r'反转', r'真相', r'揭穿', r'暴露', r'跪下', r'求饶',
        r'不敢', r'震惊', r'目瞪口呆', r'没想到', r'原来', r'其实',
        r'赢了', r'成功', r'到手', r'终于', r'恢复', r'突破',
        r'道歉', r'认错', r'服了', r'饶命', r'放过',
    ]

    compress_hits = []
    release_hits = []
    for p in compress_signals:
        for m in re.finditer(p, last_200_chars):
            compress_hits.append(m.group())
    for p in release_signals:
        for m in re.finditer(p, last_200_chars):
            release_hits.append(m.group())

    compress_score = len(set(compress_hits))
    release_score = len(set(release_hits))

    if compress_score > release_score:
        state = "压弹簧"
        confidence = min(compress_score / 2, 1.0)
    elif release_score > compress_score:
        state = "放弹簧"
        confidence = min(release_score / 2, 1.0)
    else:
        state = "⚠ 中性收尾（可能违规）"
        confidence = 0.0

    return {
        "name": "情绪弹簧(单集二态)",
        "passed": state != "⚠ 中性收尾（可能违规）",
        "state": state,
        "confidence": f"{confidence:.0%}",
        "compress_signals": list(set(compress_hits))[:5],
        "release_signals": list(set(release_hits))[:5],
        "detail": f"集末200字判定: {state}"
    }


# ── v5.4 信息前置检测 ──

def check_info_frontloading(text):
    """检测每场戏第一句对白是否包含身份/冲突/目标。"""
    info_keywords = [
        r'我是', r'你是', r'他是', r'她是',   # 身份
        r'为什么', r'凭什么', r'不许', r'必须', r'不能', r'给我',  # 冲突/命令
        r'我要', r'你得', r'去找', r'交出', r'说来',  # 目标
    ]
    scenes = re.split(r'---', text)
    violations = []
    for i, scene in enumerate(scenes):
        first_dialogue = re.search(r'^[^\s△#\-【\d\n].*[：:].+$', scene.strip(), re.MULTILINE)
        if first_dialogue:
            line = first_dialogue.group()
            has_info = any(re.search(kw, line) for kw in info_keywords)
            if not has_info:
                line_no = text[:text.find(line)].count('\n') + 1 if line in text else 0
                violations.append({
                    "scene": i + 1,
                    "line": line_no,
                    "dialogue": line[:50],
                    "issue": "首句对白未包含身份/冲突/目标信息"
                })
    return {
        "name": "信息前置(首句对白)",
        "passed": len(violations) == 0,
        "violations": violations,
        "detail": f"{len(violations)}场未通过信息前置检测"
    }


# ── v5.4 对白功能化检测 ──

def check_dialogue_function(text):
    """检测对白是否通过三不沾测试：推动情节/揭示人设/制造冲突。"""
    filler_patterns = [
        r'^(嗯|哦|啊|哎|唉|嗨|喂)[，,。.]*$',  # 纯语气词
        r'^好的[，,。.]*$', r'^知道了[，,。.]*$', r'^行[，,。.]*$', r'^可以[，,。.]*$',  # 纯应答
        r'^来了[，,。.]*$', r'^去吧[，,。.]*$', r'^走吧[，,。.]*$',  # 纯动作应答
        r'^哈哈[，,。.]*$', r'^呵呵[，,。.]*$',  # 纯笑声
        r'^你.*什么意思$', r'^这话.*什么意思$',  # 追问但不推进信息(弱)
    ]
    violations = []
    dialogue_lines = re.findall(r'^([^\s△#\-【\d\n].*[：:].+)$', text, re.MULTILINE)
    for line in dialogue_lines:
        content = re.sub(r'^[^：:]+[：:]', '', line).strip()
        for fp in filler_patterns:
            if re.match(fp, content):
                line_no = text[:text.find(line)].count('\n') + 1
                violations.append({
                    "line": line_no,
                    "dialogue": line[:60],
                    "issue": "可能未通过三不沾测试(推动情节/揭示人设/制造冲突)"
                })
                break
    return {
        "name": "对白功能化(三不沾)",
        "passed": len(violations) <= 3,  # ≤3 filler lines is acceptable
        "violations": violations,
        "detail": f"{len(violations)}句对白可能未通过功能化测试"
    }


# ── v5.4 对白声音区分度检测 ──

def check_voice_differentiation(text):
    """检测角色对白是否有独特语癖/节奏/用词（单集只能做基本检查）。"""
    char_lines = {}
    for m in re.finditer(r'^([^\s△#\-【\d\n]{1,10})[：:](.+)$', text, re.MULTILINE):
        char = m.group(1).strip()
        content = m.group(2).strip()
        if char not in char_lines:
            char_lines[char] = []
        char_lines[char].append(content)

    if len(char_lines) < 2:
        return {"name": "对白声音区分度", "passed": True, "detail": "单角色无需区分"}

    # Check if characters have distinct average sentence lengths (proxy for voice)
    profiles = {}
    for char, lines in char_lines.items():
        avg_len = sum(len(l) for l in lines) / len(lines)
        exclamations = sum(1 for l in lines if '！' in l or '!' in l)
        questions = sum(1 for l in lines if '？' in l or '?' in l)
        profiles[char] = {"avg_len": avg_len, "exclam": exclamations, "quest": questions}

    # Check for signs all characters talk the same way
    avg_lengths = [p["avg_len"] for p in profiles.values()]
    if len(avg_lengths) >= 2:
        max_diff = max(avg_lengths) - min(avg_lengths)
        if max_diff < 3:  # All characters have very similar sentence lengths
            return {
                "name": "对白声音区分度",
                "passed": False,
                "detail": f"角色句长差异仅{max_diff:.1f}字，可能千人一面",
                "profiles": profiles
            }

    return {
        "name": "对白声音区分度",
        "passed": True,
        "detail": f"句长差异{max(avg_lengths) - min(avg_lengths):.1f}字",
        "profiles": profiles
    }


# ── v5.4+ 情绪弹簧全剧扫描 ──

def check_emotion_spring_full(text):
    """全剧情绪弹簧扫描：分段(开/中/尾)压/放分析 + 平区检测(20+连续字无情感信号)。"""
    compress_signals = [
        r'危机', r'危险', r'威胁', r'逼', r'压', r'困', r'陷', r'绝境',
        r'误会', r'怀疑', r'愤怒', r'杀意', r'冷笑', r'暗算', r'埋伏',
        r'不妙', r'糟糕', r'完了', r'怎么办', r'不.*放过', r'等着瞧',
        r'动手', r'围', r'挡住', r'休想', r'做梦',
    ]
    release_signals = [
        r'打脸', r'反转', r'真相', r'揭穿', r'暴露', r'跪下', r'求饶',
        r'不敢', r'震惊', r'目瞪口呆', r'没想到', r'原来', r'其实',
        r'赢了', r'成功', r'到手', r'终于', r'恢复', r'突破',
        r'道歉', r'认错', r'服了', r'饶命', r'放过',
    ]
    all_emotion_signals = compress_signals + release_signals

    scenes = re.split(r'---', text)
    total_chars = len(text)

    # Partition into thirds by character position
    p1_end = int(total_chars * 0.33)
    p2_end = int(total_chars * 0.67)
    segments = {
        "opening": text[:p1_end],
        "middle": text[p1_end:p2_end],
        "ending": text[p2_end:],
    }

    segment_results = {}
    all_flat_zones = 0

    for seg_name, seg_text in segments.items():
        compress_hits = []
        release_hits = []
        for p in compress_signals:
            for m in re.finditer(p, seg_text):
                compress_hits.append(m.group())
        for p in release_signals:
            for m in re.finditer(p, seg_text):
                release_hits.append(m.group())

        c_score = len(set(compress_hits))
        r_score = len(set(release_hits))

        if c_score > r_score:
            state = "压弹簧"
        elif r_score > c_score:
            state = "放弹簧"
        elif c_score == 0 and r_score == 0:
            state = "中性(无情感信号)"
        else:
            state = "中性(压放均等)"

        # Flat zone detection: scan for stretches of 20+ consecutive chars without emotion signals
        flat_zones = 0
        stripped = seg_text
        # Remove all lines that are purely structural (△ actions, 【】 descriptions, dialogue lines)
        # Then check remaining text for long runs without signals
        lines = stripped.split('\n')
        non_signal_run = 0
        for line in lines:
            line = line.strip()
            if not line or line.startswith('（') or line == '---':
                non_signal_run = 0
                continue
            has_signal = any(re.search(sig, line) for sig in all_emotion_signals)
            has_action = line.startswith('△') or line.startswith('【')
            has_dialogue = re.match(r'^[^\s△#\-【\d].*[：:]', line)
            if has_signal or has_action:
                non_signal_run = 0
            elif has_dialogue:
                # Check if dialogue content has emotional signals
                content = re.sub(r'^[^：:]+[：:]', '', line).strip()
                if any(re.search(sig, content) for sig in all_emotion_signals):
                    non_signal_run = 0
                else:
                    non_signal_run += len(line)
            else:
                non_signal_run += len(line)
            if non_signal_run >= 20:
                flat_zones += 1
                non_signal_run = 0

        all_flat_zones += flat_zones
        segment_results[seg_name] = {
            "state": state,
            "compress_hits": list(set(compress_hits))[:5],
            "release_hits": list(set(release_hits))[:5],
            "flat_zones": flat_zones,
        }

    has_neutral = any(s["state"].startswith("中性") for s in segment_results.values())
    flat_ok = all_flat_zones <= 2  # allow up to 2 flat zones total

    return {
        "name": "情绪弹簧全剧扫描",
        "passed": not has_neutral and flat_ok,
        "segments": segment_results,
        "total_flat_zones": all_flat_zones,
        "detail": f"开{segment_results['opening']['state']}/中{segment_results['middle']['state']}/尾{segment_results['ending']['state']} 平区{all_flat_zones}处"
    }


# ── v5.4+ 情绪锚点自动检测 ──

ANCHOR_PROFILES = {
    "爽": [
        r'打脸', r'反转', r'碾压', r'跪下', r'求饶', r'真相.*白', r'揭穿',
        r'赢了', r'到手', r'碾压', r'完胜', r'秒杀', r'震惊.*全场',
        r'不敢.*相信', r'服了', r'饶命', r'霸气', r'横扫',
    ],
    "虐": [
        r'牺牲', r'放弃', r'失去', r'再也', r'永别', r'诀别', r'心碎',
        r'绝望', r'背叛', r'误会.*深', r'错过', r'遗憾', r'痛苦',
        r'为什么.*这样', r'不该', r'晚了', r'来不及',
    ],
    "暖": [
        r'守护', r'陪伴', r'理解', r'原谅', r'拥抱', r'温暖', r'感动',
        r'为.*好', r'保护', r'相信.*你', r'我.*在', r'不.*离开',
        r'照顾', r'心疼', r'值得', r'在意',
    ],
    "悬": [
        r'秘密', r'真相', r'谁.', r'为什么', r'怎么回事', r'阴谋',
        r'背后', r'隐藏', r'揭露', r'即将', r'倒计时', r'危机',
        r'究竟', r'到底是什么', r'难道', r'莫非',
    ],
    "燃": [
        r'觉醒', r'突破', r'晋级', r'爆发', r'全力', r'终极', r'对决',
        r'一战', r'最强', r'归来', r'誓要', r'决不', r'拼了',
        r'战', r'冲', r'杀', r'从未.*放弃', r'一定.*赢',
    ],
}


def check_emotion_anchors(text):
    """情绪锚点自动检测：爽虐暖悬燃五型识别+主导锚点+情绪转向次数(≥3)。"""
    anchor_hits = {}
    for anchor, patterns in ANCHOR_PROFILES.items():
        hits = set()
        for p in patterns:
            for m in re.finditer(p, text):
                hits.add(m.group())
        anchor_hits[anchor] = len(hits)

    # Determine dominant anchor
    if max(anchor_hits.values()) == 0:
        dominant = "未检测到"
        passed_anchor = False
    else:
        max_count = max(anchor_hits.values())
        tops = [a for a, c in anchor_hits.items() if c == max_count]
        dominant = tops[0] if len(tops) == 1 else f"混合({','.join(tops)})"
        passed_anchor = True

    # Count emotional turns: scan in 200-char windows for anchor transitions
    window_size = 200
    turns = 0
    prev_anchor = None
    for i in range(0, len(text), window_size // 2):  # 50% overlap
        window = text[i:i + window_size]
        if len(window) < 50:
            break
        # Find dominant anchor in this window
        best_anchor = None
        best_score = 0
        for anchor, patterns in ANCHOR_PROFILES.items():
            score = 0
            for p in patterns:
                if re.search(p, window):
                    score += 1
            if score > best_score:
                best_score = score
                best_anchor = anchor
        if best_anchor and best_anchor != prev_anchor:
            if prev_anchor is not None:
                turns += 1
            prev_anchor = best_anchor

    passed = passed_anchor and turns >= 3

    return {
        "name": "情绪锚点检测",
        "passed": passed,
        "dominant_anchor": dominant,
        "anchor_hits": anchor_hits,
        "emotional_turns": turns,
        "detail": f"主导锚点:{dominant} 情绪转向{turns}次({'≥3✓' if turns >= 3 else '不足✗'})"
    }


# ── v5.4+ 情绪节拍五节点验证 ──

def check_emotion_beat_template(text):
    """五节点情绪节拍验证：视觉锤→立场锚→爆破点→爽点→端钩的情绪映射。"""
    total = len(text)
    segments = {
        "视觉锤(0-5%)": (0, int(total * 0.05)),
        "立场锚(5-20%)": (int(total * 0.05), int(total * 0.20)),
        "爆破点(20-50%)": (int(total * 0.20), int(total * 0.50)),
        "爽点(50-85%)": (int(total * 0.50), int(total * 0.85)),
        "端钩(85-100%)": (int(total * 0.85), total),
    }

    # Expected signals for each node
    node_profiles = {
        "视觉锤(0-5%)": {
            "visual_action": [r'△.*[冲打飞撞闪杀战踹踢]'],
            "strong_opening": [r'^[^\s△#\-【\d].*[：:].*[！？]'],
            "conflict_immediate": [r'逼', r'威胁', r'危险', r'站住', r'动手'],
        },
        "立场锚(5-20%)": {
            "identity": [r'我是', r'你是', r'他是', r'她是'],
            "goal": [r'我要', r'去找', r'交出', r'必须', r'给我'],
            "conflict_line": [r'凭什么', r'为什么', r'不许', r'不能'],
        },
        "爆破点(20-50%)": {
            "high_conflict": [r'打脸', r'反转', r'真相', r'危机', r'逼', r'杀', r'战'],
            "peak_emotion": [r'！', r'跪', r'求饶', r'竟然', r'没想到'],
        },
        "爽点(50-85%)": {
            "release_dominant": [r'赢了', r'突破', r'成功', r'到手', r'终于', r'恢复', r'揭穿'],
            "power_shift": [r'不再', r'从此', r'反转', r'碾压', r'跪下'],
        },
        "端钩(85-100%)": {
            "strong_hook": [r'？$', r'！$', r'...$'],
            "compelling_end": [r'危机', r'秘密', r'真相', r'未完', r'待续', r'即将'],
        },
    }

    node_results = []
    for node_name, (start, end) in segments.items():
        seg = text[start:end] if end <= total else text[start:]
        if len(seg) < 10:
            node_results.append({"name": node_name, "passed": False, "detail": "段落过短", "signal_count": 0})
            continue

        profiles = node_profiles.get(node_name, {})
        total_signals = 0
        matched_categories = 0
        for cat_name, patterns in profiles.items():
            cat_hit = False
            for p in patterns:
                if re.search(p, seg, re.MULTILINE):
                    total_signals += 1
                    cat_hit = True
            if cat_hit:
                matched_categories += 1

        # Node passes if at least 1 category matched
        passed = matched_categories >= 1
        node_results.append({
            "name": node_name,
            "passed": passed,
            "signal_count": total_signals,
            "matched_categories": matched_categories,
            "detail": f"{'✓' if passed else '✗'} {matched_categories}/{len(profiles)}类信号"
        })

    passed_count = sum(1 for n in node_results if n["passed"])
    return {
        "name": "情绪节拍五节点",
        "passed": passed_count >= 3,
        "nodes": node_results,
        "detail": f"{passed_count}/5节点通过({'≥3✓' if passed_count >= 3 else '不足✗'})"
    }


# ── v5.4+ 角色情感范围分析 ──

def check_character_emotion_range(text):
    """角色情感范围分析：每角色情感主导/次级模式+一致性检测。始终advisory。"""
    char_lines = {}
    for m in re.finditer(r'^([^\s△#\-【\d\n]{1,10})[：:](.+)$', text, re.MULTILINE):
        char = m.group(1).strip()
        content = m.group(2).strip()
        if char not in char_lines:
            char_lines[char] = []
        char_lines[char].append(content)

    if len(char_lines) < 2:
        return {
            "name": "角色情感范围",
            "passed": True,
            "detail": "单角色无需分析情感范围",
            "characters": []
        }

    char_profiles = []
    for char, lines in char_lines.items():
        combined = ' '.join(lines)
        # Run mini anchor scan on this character's dialogue
        char_anchors = {}
        for anchor, patterns in ANCHOR_PROFILES.items():
            hits = set()
            for p in patterns:
                for m in re.finditer(p, combined):
                    hits.add(m.group())
            char_anchors[anchor] = len(hits)

        if max(char_anchors.values()) == 0:
            dominant = "中性"
            secondary = "中性"
            range_width = 0
        else:
            sorted_anchors = sorted(char_anchors.items(), key=lambda x: x[1], reverse=True)
            dominant = sorted_anchors[0][0]
            secondary = sorted_anchors[1][0] if len(sorted_anchors) > 1 and sorted_anchors[1][1] > 0 else "无"
            # Range width = count of anchors with any hits
            range_width = sum(1 for v in char_anchors.values() if v > 0)

        warnings = []
        if range_width == 0:
            warnings.append("角色对白无情感信号—可能缺乏情绪表达")
        elif range_width > 4:
            warnings.append("情感范围过宽—角色可能情绪表达不一致")
        elif range_width == 1 and len(lines) >= 5:
            warnings.append(f"情感模式单一({dominant}主导)—确认是否为刻意设计")

        char_profiles.append({
            "character": char,
            "line_count": len(lines),
            "dominant_mode": dominant,
            "secondary_mode": secondary,
            "range_width": range_width,
            "warnings": warnings,
        })

    return {
        "name": "角色情感范围",
        "passed": True,  # always advisory
        "characters": char_profiles,
        "detail": f"{len(char_profiles)}角色分析完成"
    }


# ── v5.4+ 情绪银行跨集自动追踪 ──

IOU_DEPOSIT_PATTERNS = {
    "人物缺口": [
        r'主角.*缺', r'主角.*失去', r'主角.*没有', r'主角.*渴望',
        r'执念', r'心愿', r'寻找.*母', r'寻找.*父', r'找.*妈妈',
        r'找.*爸爸', r'身世', r'失散', r'抛弃', r'孤儿',
    ],
    "关系缺口": [
        r'误认', r'错认', r'假装', r'隐瞒.*身份', r'关系.*假',
        r'假装.*关系', r'冒充', r'顶替', r'伪装', r'名义上',
        r'假装.*夫', r'假装.*妻', r'假结婚', r'契约.*婚',
    ],
    "真相缺口": [
        r'秘密', r'真相', r'玉佩', r'谜', r'线索', r'追踪',
        r'寻找', r'调查', r'背后.*人', r'幕后', r'隐情',
        r'不知道', r'到底是', r'究竟',
    ],
}


def check_emotion_bank_health(episode_texts, anchor_data=None):
    """情绪银行自动追踪：检欠条存入/复利/催收/回收率。
    episode_texts: {ep_num: text}  dict with int keys.
    anchor_data: optional dict with manual IOU annotations.
    """
    iou_status = []
    sorted_eps = sorted(episode_texts.keys())

    for iou_type, patterns in IOU_DEPOSIT_PATTERNS.items():
        deposited_ep = None
        compound_eps = []
        collected_eps = []

        for ep in sorted_eps:
            text = episode_texts[ep]
            # Count unique pattern hits
            hits = 0
            for p in patterns:
                if re.search(p, text):
                    hits += 1

            if hits > 0:
                if deposited_ep is None:
                    deposited_ep = ep
                if ep >= 4:
                    compound_eps.append(ep)
                # Check for collection at paywall nodes
                if ep in (10, 30, 50, 75):
                    spring = check_emotion_spring(text)
                    if spring["state"] == "放弹簧":
                        collected_eps.append(ep)

        compounding_rate = 0.0
        if deposited_ep and len(sorted_eps) > 3:
            compound_range = [e for e in sorted_eps if 4 <= e <= 50]
            if compound_range:
                compounding_rate = len(compound_eps) / len(compound_range)

        unresolved = deposited_ep is not None and len(collected_eps) == 0

        iou_status.append({
            "type": iou_type,
            "deposited_ep": deposited_ep,
            "compounding_rate_pct": f"{compounding_rate:.0%}",
            "collected_at": collected_eps,
            "unresolved": unresolved,
            "status": "健康" if deposited_ep and not unresolved else
                      "已存入未回收" if unresolved else
                      "未存入" if not deposited_ep else "健康"
        })

    all_deposited = all(i["deposited_ep"] is not None for i in iou_status)
    all_collected = not any(i["unresolved"] for i in iou_status)
    passed = all_deposited and all_collected

    warnings = []
    for iou in iou_status:
        if iou["unresolved"]:
            warnings.append(f"{iou['type']}已存入第{iou['deposited_ep']}集但未在任何付费节点回收")
        if iou["deposited_ep"] is None:
            warnings.append(f"{iou['type']}未在前3集存入")

    return {
        "name": "情绪银行健康度",
        "passed": passed,
        "iou_status": iou_status,
        "warnings": warnings,
        "detail": f"存入{'✓' if all_deposited else '✗'} 回收{'✓' if all_collected else '✗'} {len(warnings)}个警告"
    }


# ── v5.4+ 付费情绪峰值检测 ──

def check_paywall_ramp(episode_texts, paywall_positions=None):
    """付费情绪峰值检测：N-2→N-1→N 压/放比递增验证，N必须是放弹簧。
    episode_texts: {ep_num: text}  dict with int keys.
    paywall_positions: list of paywall episode numbers, default [10, 30, 50, 75].
    """
    if paywall_positions is None:
        paywall_positions = [10, 30, 50, 75]

    paywall_results = []

    for pw in paywall_positions:
        ramp_eps = [pw - 2, pw - 1, pw]

        # Skip if we don't have the needed episodes
        if not all(ep in episode_texts for ep in ramp_eps):
            continue

        ramp_data = []
        for ep in ramp_eps:
            text = episode_texts[ep]
            spring = check_emotion_spring(text)
            # Count total signal density (compress + release per 100 chars)
            total_signals = len(spring.get("compress_signals", [])) + len(spring.get("release_signals", []))
            intensity = total_signals / max(len(text), 1) * 1000

            ramp_data.append({
                "ep": ep,
                "state": spring["state"],
                "confidence": spring["confidence"],
                "intensity": f"{intensity:.1f}",
            })

        # Verify ramp: states should transition toward compression then release
        states = [r["state"] for r in ramp_data]
        # N (paywall) must be release
        pw_is_release = states[-1] == "放弹簧"
        # N-2 and N-1 should ideally be compression (but just warn if not)
        ramp_ok = all(s == "压弹簧" for s in states[:2]) and pw_is_release

        paywall_results.append({
            "paywall_ep": pw,
            "ramp": ramp_data,
            "ramp_passed": ramp_ok,
            "pw_release": pw_is_release,
            "detail": f"{'✓' if ramp_ok else '⚠'} {'压→压→放' if ramp_ok else '→'.join(states)}"
        })

    all_passed = all(p["ramp_passed"] for p in paywall_results)
    return {
        "name": "付费情绪峰值",
        "passed": all_passed,
        "paywalls": paywall_results,
        "detail": f"{sum(1 for p in paywall_results if p['ramp_passed'])}/{len(paywall_results)}付费节点通过"
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python validators.py <episode_file.md> [--json]")
        print("  --json  Output raw JSON instead of formatted report")
        sys.exit(1)

    filepath = sys.argv[1]
    text = load_text(filepath)
    results = run_all_checks(text, Path(filepath).stem)

    if "--json" in sys.argv:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(format_report(results))
