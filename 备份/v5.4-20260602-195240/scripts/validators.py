"""
编剧工作台 v5.4 — 自动化验证引擎
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
