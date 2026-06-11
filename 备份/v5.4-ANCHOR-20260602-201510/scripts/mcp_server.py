"""
编剧工作台 MCP Server — stdio JSON-RPC 2.0, zero external dependencies.
Exposes validators.py as MCP tools for Claude Code auto-validation.
"""
import sys
import json
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import validators


def _json_result(data):
    return {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False, indent=2)}]}


def _call_validate_episode(args):
    path = args.get("file_path", "")
    if not path or not os.path.exists(path):
        return _json_result({"error": f"文件不存在: {path}"})
    text = validators.load_text(path)
    results = validators.run_all_checks(text, os.path.basename(path))
    report = validators.format_report(results)
    return {"content": [
        {"type": "text", "text": report},
        {"type": "text", "text": json.dumps(results, ensure_ascii=False, indent=2)}
    ]}


def _call_check_writing_redlines(args):
    text = args.get("text", "")
    return _json_result([
        validators.check_psychology(text), validators.check_abstract_emotion(text),
        validators.check_exposition_dialogue(text), validators.check_preaching(text),
        validators.check_ai_tone(text), validators.check_adjective_stack(text),
        validators.check_unfilmable(text), validators.check_passive_protagonist(text),
        validators.check_logic_break(text)
    ])


def _call_check_format(args):
    return _json_result(validators.check_format(args.get("text", "")))


def _call_check_platform_redlines(args):
    return _json_result(validators.check_platform_redlines(args.get("text", "")))


def _call_check_content_rules(args):
    text = args.get("text", "")
    return _json_result([
        validators.check_irreversible_change(text),
        validators.check_choice_cost(text),
        validators.check_cheat_cost(text)
    ])


def _call_check_rhythm(args):
    return _json_result(validators.check_rhythm(args.get("text", "")))


def _call_check_emotion_spring(args):
    return _json_result(validators.check_emotion_spring(args.get("text", "")))


def _call_check_info_frontloading(args):
    return _json_result(validators.check_info_frontloading(args.get("text", "")))


def _call_check_dialogue_quality(args):
    text = args.get("text", "")
    return _json_result({
        "dialogue_function": validators.check_dialogue_function(text),
        "voice_differentiation": validators.check_voice_differentiation(text)
    })


def _call_validate_multi_episodes(args):
    paths = args.get("file_paths", [])
    all_results = {}
    for p in paths:
        if os.path.exists(p):
            all_results[os.path.basename(p)] = validators.run_all_checks(validators.load_text(p), os.path.basename(p))
        else:
            all_results[os.path.basename(p)] = {"error": "文件不存在"}
    return _json_result({"episodes": all_results, "cross_analysis": {
        "hook_rotation": "需人工确认—检查连续3集是否无重复钩子类型",
        "foreshadowing": "需人工确认—伏笔清单跨集一致性",
        "character_arc": "需人工确认—人物弧光四阶段进度",
        "props_cross_episode": "需人工确认—道具跨集出现是否一致",
        "emotion_bank_health": "需人工确认—情绪欠条存入/催收是否按节点",
    }})


DISPATCH = {
    "validate_episode": _call_validate_episode,
    "check_writing_redlines": _call_check_writing_redlines,
    "check_format": _call_check_format,
    "check_platform_redlines": _call_check_platform_redlines,
    "check_content_rules": _call_check_content_rules,
    "check_rhythm": _call_check_rhythm,
    "check_emotion_spring": _call_check_emotion_spring,
    "check_info_frontloading": _call_check_info_frontloading,
    "check_dialogue_quality": _call_check_dialogue_quality,
    "validate_multi_episodes": _call_validate_multi_episodes,
}

TOOLS = [
    {
        "name": "validate_episode",
        "description": "对单集剧本执行全部65项自检：写作红线9项 + 格式规范12项 + 内容铁律3项 + 节奏工程6项 + 平台红线9项。返回结构化JSON报告。",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "剧本集数文件路径，如 C:\\Users\\17928\\Desktop\\编剧工作台\\项目\\剧本-第1集.md"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "check_writing_redlines",
        "description": "仅检查写作红线9项：心理描写/抽象情绪/台词解说设定/说教催泪/AI腔/形容词堆砌/不可拍摄/被动主角/逻辑断裂",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "要检查的剧本文本"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "check_format",
        "description": "仅检查格式规范12项：第x集/001编号/人物/服装/道具预罗列/【】/△/对白/道具一致/场景≤3/人物≤4/≥500字",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "要检查的剧本文本"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "check_platform_redlines",
        "description": "仅检查平台红线9项：涉政/色情/过度暴力/违法/歧视/架空/未成年/侵权/正义结局",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "要检查的剧本文本"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "check_content_rules",
        "description": "仅检查内容铁律3项：不可逆变化/选择代价/金手指代价",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "要检查的剧本文本"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "check_rhythm",
        "description": "仅检查节奏工程6项：≥3节拍/钩子密度/无10s空白/A端钩/钩子轮换/五节点",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "要检查的剧本文本"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "check_emotion_spring",
        "description": "v5.4 情绪弹簧检测：分析单集结尾200字，判定是'压弹簧'(积蓄紧张)还是'放弹簧'(释放爽感)，中性收尾=违规",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "要检查的剧本文本"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "check_info_frontloading",
        "description": "v5.4 信息前置检测：检查每场戏首句对白是否包含身份/冲突/目标信息，空话开场=违规",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "要检查的剧本文本"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "check_dialogue_quality",
        "description": "v5.4 对白质量综合评估：对白功能化(三不沾测试)+ 声音区分度(角色语癖/节奏/用词差异) + 信息密度",
        "inputSchema": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "要检查的剧本文本"}
            },
            "required": ["text"]
        }
    },
    {
        "name": "validate_multi_episodes",
        "description": "对多集剧本执行交叉验证：钩子类型轮换/伏笔一致性/人物弧光进度/道具跨集一致/情绪欠条健康度/情绪弹簧节奏",
        "inputSchema": {
            "type": "object",
            "properties": {
                "file_paths": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "多个剧本文件路径列表"
                }
            },
            "required": ["file_paths"]
        }
    }
]


def handle_initialize(_):
    return {
        "protocolVersion": "0.3.0",
        "capabilities": {"tools": {}},
        "serverInfo": {"name": "bianju-validators", "version": "1.0.0"}
    }


def handle_tools_list(_):
    return {"tools": TOOLS}


def handle_tools_call(params):
    name = params.get("name", "")
    args = params.get("arguments", {})
    handler = DISPATCH.get(name)
    if handler:
        return handler(args)
    return {"content": [{"type": "text", "text": f"Unknown tool: {name}"}]}


METHODS = {
    "initialize": handle_initialize,
    "tools/list": handle_tools_list,
    "tools/call": handle_tools_call,
}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue

        req_id = request.get("id")
        method = request.get("method", "")
        handler = METHODS.get(method)
        if method == "notifications/initialized":
            continue
        result = handler(request.get("params", {})) if handler else {
            "error": {"code": -32601, "message": f"Method not found: {method}"}
        }
        if req_id is not None:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "id": req_id, "result": result}, ensure_ascii=False) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
