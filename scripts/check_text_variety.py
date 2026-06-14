#!/usr/bin/env python3
"""check_text_variety.py — 文本可预测性检测（Perplexity Gate 简化实现）
检测维度：句长方差/词汇多样性/句式重复/段落均匀度/AI腔密度/风格基线漂移
用法: python check_text_variety.py "file.md" --threshold 70
      python check_text_variety.py "ep50.md" --baseline "ep1-3.md"  # 风格漂移检测
退出码: 0=通过 1=警告(≥1项临界) 2=拒绝(≥1项红线)
v7.1: 新增 --baseline 参数，对比风格基线检测漂移
"""

import sys
import re
import argparse
from pathlib import Path
from collections import Counter

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ── 检测维度 ────────────────────────────────

def sentence_length_gini(sentences):
    """句长方差系数——越小越单调"""
    lengths = [len(s) for s in sentences if len(s) > 2]
    if len(lengths) < 5:
        return 1.0, lengths
    mean_len = sum(lengths) / len(lengths)
    if mean_len == 0:
        return 1.0, lengths
    # O(N log N) via sorted cumulative sum: G = (2*Σ(i*sorted_i) - (n+1)*Σ(sorted_i)) / (n*Σ(sorted_i))
    sorted_lens = sorted(lengths)
    n = len(sorted_lens)
    total = sum(sorted_lens)
    weighted_sum = sum((i + 1) * val for i, val in enumerate(sorted_lens))
    gini = (2 * weighted_sum - (n + 1) * total) / (n * total) if total > 0 else 1
    return gini, lengths

def type_token_ratio(text):
    """词汇多样性 TTR——<0.4 表示词汇贫乏"""
    words = re.findall(r'[一-鿿]+', text)
    if len(words) < 50:
        return 1.0, len(set(words)), len(words)
    unique = len(set(words))
    total = len(words)
    return unique / total if total > 0 else 0, unique, total

def ngram_repetition_rate(sentences, n=3):
    """N-gram 句式重复率——>15% 表示句式单调"""
    if len(sentences) < 5:
        return 0.0, []
    patterns = []
    for s in sentences:
        chars = re.sub(r'[^一-鿿]', '', s)
        for i in range(len(chars) - n + 1):
            patterns.append(chars[i:i+n])
    if not patterns:
        return 0.0, []
    counter = Counter(patterns)
    repeated = sum(1 for v in counter.values() if v >= 3)
    rate = repeated / len(counter) if counter else 0
    top_repeats = [(k, v) for k, v in counter.most_common(5) if v >= 3]
    return rate, top_repeats

def paragraph_uniformity(paragraphs):
    """段落等长检测——CV<0.3 表示过于均匀"""
    lengths = [len(p) for p in paragraphs if len(p) > 5]
    if len(lengths) < 3:
        return 0.0, lengths
    mean_len = sum(lengths) / len(lengths)
    if mean_len == 0:
        return 0.0, lengths
    variance = sum((l - mean_len) ** 2 for l in lengths) / len(lengths)
    cv = (variance ** 0.5) / mean_len
    return cv, lengths

def ai_marker_density(text):
    """AI 标记词密度——每 600 字应 ≤ 1 个"""
    markers = ['仿佛', '忽然', '竟然', '不禁', '宛如', '猛地', '难以置信', '无形中',
               '然而', '因此', '于是', '随后', '与此同时', '就这样', '不仅如此',
               '岂料', '殊不知', '正所谓', '不料', '显而易见', '毋庸置疑',
               '由此可见', '换言之', '总而言之', '综上所述', '顷刻间',
               '蓦然', '倏地', '须臾', '便见得']
    total_chars = len(re.findall(r'[一-鿿]', text))
    if total_chars < 100:
        return 0.0, []
    found = []
    for m in markers:
        count = text.count(m)
        if count > 0:
            found.append((m, count))
    density = sum(c for _, c in found) / (total_chars / 600) if total_chars > 0 else 0
    return density, found

def formulaic_openings(sentences):
    """公式化句首检测——同一句首词连续使用"""
    if len(sentences) < 5:
        return 0, []
    openings = []
    for s in sentences:
        stripped = s.strip()
        if len(stripped) >= 2:
            openings.append(stripped[:2])
    counter = Counter(openings)
    issues = []
    for k, v in counter.most_common(10):
        if v >= 3:
            issues.append((k, v))
    return len(issues), issues

# ── 风格基线漂移检测 (v7.1) ──────────────────

def compute_style_fingerprint(text):
    """提取文本风格指纹（4维可量化指标）"""
    sentences = re.split(r'[。！？\n]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    words = re.findall(r'[一-鿿]+', text)
    total_chars = len(words)

    # 1. 句长分布：mean + std
    sent_lens = [len(re.findall(r'[一-鿿]', s)) for s in sentences if len(re.findall(r'[一-鿿]', s)) > 0]
    sent_mean = sum(sent_lens) / len(sent_lens) if sent_lens else 0
    sent_std = (sum((l - sent_mean) ** 2 for l in sent_lens) / len(sent_lens)) ** 0.5 if sent_lens and len(sent_lens) > 1 else 0

    # 2. 感官描写密度：感官词/千字
    sensory_words = ['看', '见', '望', '盯', '瞥', '凝视', '听', '闻', '嗅', '声', '音',
                     '热', '冷', '暖', '凉', '烫', '冰', '痛', '疼', '酸', '麻', '痒',
                     '光', '暗', '亮', '黑', '白', '红', '蓝', '绿', '金', '银',
                     '香', '臭', '腥', '甜', '苦', '辣', '咸', '淡',
                     '硬', '软', '粗', '细', '滑', '涩', '湿', '干', '黏',
                     '重', '轻', '沉', '飘']
    sensory_count = sum(text.count(w) for w in sensory_words)
    sensory_density = (sensory_count / (total_chars / 1000)) if total_chars > 0 else 0

    # 3. 对白占比
    dialogue_lines = len(re.findall(r'[^\n]+：.*', text))
    total_lines = text.count('\n') + 1
    dialogue_ratio = dialogue_lines / total_lines if total_lines > 0 else 0

    # 4. AI标记词密度（每600字）
    markers = ['仿佛', '忽然', '竟然', '不禁', '宛如', '猛地', '难以置信', '无形中',
               '然而', '因此', '于是', '随后', '与此同时', '就这样', '不仅如此',
               '岂料', '殊不知', '正所谓', '不料', '显而易见', '毋庸置疑',
               '由此可见', '换言之', '总而言之', '综上所述', '顷刻间',
               '蓦然', '倏地', '须臾', '便见得']
    marker_count = sum(text.count(m) for m in markers)
    marker_density = marker_count / (total_chars / 600) if total_chars > 0 else 0

    return {
        "sent_mean": round(sent_mean, 1),
        "sent_std": round(sent_std, 1),
        "sensory_density": round(sensory_density, 1),
        "dialogue_ratio": round(dialogue_ratio, 3),
        "marker_density": round(marker_density, 2),
        "total_chars": total_chars
    }

def compare_baseline(current_fp, baseline_fp):
    """对比当前文本与基线风格指纹，返回各维度偏差"""
    comparisons = []
    max_deviation = 0.0
    overall = "pass"

    dims = [
        ("句长均值", "sent_mean", 15, 25),
        ("句长标准差", "sent_std", 20, 30),
        ("感官描写密度", "sensory_density", 20, 30),
        ("对白占比", "dialogue_ratio", 20, 30),
        ("AI标记词密度", "marker_density", 20, 30),
    ]

    for label, key, warn_pct, reject_pct in dims:
        cur = current_fp[key]
        base = baseline_fp[key]
        if base == 0 and cur == 0:
            deviation = 0.0
        elif base == 0:
            deviation = 100.0
        else:
            deviation = abs(cur - base) / abs(base) * 100

        status = "pass"
        if deviation > reject_pct:
            status = "reject"
            overall = "reject"
        elif deviation > warn_pct:
            status = "warn"
            if overall == "pass":
                overall = "warn"

        max_deviation = max(max_deviation, deviation)
        comparisons.append({
            "dimension": label,
            "baseline": base,
            "current": cur,
            "deviation_pct": round(deviation, 1),
            "status": status
        })

    return {"overall": overall, "max_deviation_pct": round(max_deviation, 1), "comparisons": comparisons}


# ── 门禁规则 ────────────────────────────────

GATES = {
    "句长方差": {"check": "gini", "warn": 0.25, "reject": 0.15, "desc": "句子长度过于均匀→缺少节奏变化"},
    "词汇多样性": {"check": "ttr", "warn": 0.45, "reject": 0.35, "desc": "词汇贫乏→AI腔高风险"},
    "句式重复": {"check": "ngram_rate", "warn": 0.10, "reject": 0.18, "desc": "句式重复→读者疲劳"},
    "段落均匀度": {"check": "para_cv", "warn": 0.35, "reject": 0.20, "desc": "段落等长→视觉节奏单调"},
    "AI标记词": {"check": "ai_density", "warn": 1.0, "reject": 1.5, "desc": "AI标记词过密→疑似AI生成"},
    "公式化句首": {"check": "formulaic", "warn": 3, "reject": 5, "desc": "句首重复→模板化写作"},
}

def analyze_file(filepath):
    """Run all checks on a file, return structured results."""
    path = Path(filepath)
    if not path.exists():
        return {"error": f"文件不存在: {filepath}"}

    text = path.read_text(encoding="utf-8")

    # Split into sentences and paragraphs
    sentences = re.split(r'[。！？\n]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    paragraphs = re.split(r'\n\s*\n', text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]

    results = {}

    # 1. Sentence length Gini
    gini, lengths = sentence_length_gini(sentences)
    results["gini"] = {"value": round(gini, 3), "avg_len": round(sum(lengths)/len(lengths), 1) if lengths else 0}

    # 2. Type-Token Ratio
    ttr, unique, total = type_token_ratio(text)
    results["ttr"] = {"value": round(ttr, 3), "unique_words": unique, "total_words": total}

    # 3. N-gram repetition
    ngram_rate, top_repeats = ngram_repetition_rate(sentences)
    results["ngram_rate"] = {"value": round(ngram_rate, 3), "top_repeats": top_repeats}

    # 4. Paragraph uniformity
    para_cv, para_lengths = paragraph_uniformity(paragraphs)
    results["para_cv"] = {"value": round(para_cv, 3), "para_count": len(para_lengths)}

    # 5. AI marker density
    ai_density, ai_matches = ai_marker_density(text)
    results["ai_density"] = {"value": round(ai_density, 2), "matches": ai_matches}

    # 6. Formulaic openings
    formulaic_count, formulaic_issues = formulaic_openings(sentences)
    results["formulaic"] = {"value": formulaic_count, "issues": formulaic_issues}

    # Apply gates
    gate_results = []
    overall = "pass"
    for name, gate in GATES.items():
        check_key = gate["check"]
        if check_key not in results:
            continue
        value = results[check_key]["value"]
        if value <= gate["reject"] if check_key in ("gini", "ttr", "para_cv") else value >= gate["reject"]:
            gate_results.append({"gate": name, "status": "reject", "value": value, "desc": gate["desc"]})
            overall = "reject"
        elif value <= gate["warn"] if check_key in ("gini", "ttr", "para_cv") else value >= gate["warn"]:
            gate_results.append({"gate": name, "status": "warn", "value": value, "desc": gate["desc"]})
            if overall == "pass":
                overall = "warn"
        else:
            gate_results.append({"gate": name, "status": "pass", "value": value})

    score = sum(1 for g in gate_results if g["status"] == "pass") / len(gate_results) * 100 if gate_results else 0

    return {
        "file": filepath,
        "overall": overall,
        "score": round(score, 1),
        "chars": len(re.findall(r'[一-鿿]', text)),
        "sentences": len(sentences),
        "paragraphs": len(paragraphs),
        "gates": gate_results,
        "details": results
    }


def main():
    parser = argparse.ArgumentParser(description="文本可预测性检测 (Perplexity Gate)")
    parser.add_argument("file", help="文件路径")
    parser.add_argument("--threshold", type=int, default=70, help="通过阈值 (0-100)")
    parser.add_argument("--json", action="store_true", help="JSON 输出")
    parser.add_argument("--baseline", type=str, default=None, help="基线文件路径（用于风格漂移检测，对比前1-3集）")
    args = parser.parse_args()

    result = analyze_file(args.file)

    if "error" in result:
        print(f"✗ {result['error']}", file=sys.stderr)
        sys.exit(2)

    # ── 风格基线漂移检测 (v7.1) ──
    baseline_result = None
    if args.baseline:
        baseline_path = Path(args.baseline)
        if not baseline_path.exists():
            print(f"⚠ 基线文件不存在: {args.baseline}", file=sys.stderr)
        else:
            baseline_text = baseline_path.read_text(encoding="utf-8")
            cur_text = Path(args.file).read_text(encoding="utf-8")
            cur_fp = compute_style_fingerprint(cur_text)
            base_fp = compute_style_fingerprint(baseline_text)
            baseline_result = compare_baseline(cur_fp, base_fp)

            if not args.json:
                print(f"▸ 风格基线漂移检测 (v7.1)")
                print(f"  基线: {baseline_path.name}  (句长{base_fp['sent_mean']}±{base_fp['sent_std']}字)  "
                      f"感官密度{base_fp['sensory_density']}/千字  对白比{base_fp['dialogue_ratio']}")
                print(f"  当前: {Path(args.file).name}  (句长{cur_fp['sent_mean']}±{cur_fp['sent_std']}字)  "
                      f"感官密度{cur_fp['sensory_density']}/千字  对白比{cur_fp['dialogue_ratio']}")
                print(f"  最大漂移: {baseline_result['max_deviation_pct']}%  [{baseline_result['overall']}]")
                for c in baseline_result["comparisons"]:
                    mark = {"pass": "✓", "warn": "⚠", "reject": "✗"}[c["status"]]
                    print(f"  {mark} {c['dimension']}: {c['baseline']} → {c['current']}  "
                          f"偏差 {c['deviation_pct']}%")
                print()

            # 漂移检测可提升门禁等级
            if baseline_result["overall"] == "reject":
                result["overall"] = "reject"
            elif baseline_result["overall"] == "warn" and result["overall"] == "pass":
                result["overall"] = "warn"
            result["baseline"] = baseline_result

    if args.json:
        import json
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"▸ Perplexity Gate — {result['file']}")
        print(f"  中文字数: {result['chars']}  句子: {result['sentences']}  段落: {result['paragraphs']}")
        print(f"  综合评分: {result['score']}/100  [{result['overall']}]")
        print()
        for g in result["gates"]:
            mark = {"pass": "✓", "warn": "⚠", "reject": "✗"}[g["status"]]
            print(f"  {mark} {g['gate']}: {g['value']}  — {g['desc']}")
        print()
        if result["details"].get("ai_density", {}).get("matches"):
            print(f"  AI 标记词热力图:")
            for word, count in result["details"]["ai_density"]["matches"]:
                bar = "█" * count
                print(f"    {word}: {bar} ({count})")
        if result["details"].get("ngram_rate", {}).get("top_repeats"):
            print(f"  高频句式片段:")
            for pattern, count in result["details"]["ngram_rate"]["top_repeats"]:
                print(f"    '{pattern}' ×{count}")

    if result["overall"] == "reject":
        sys.exit(2)
    elif result["overall"] == "warn":
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
