#!/usr/bin/env python3
"""check_text_variety.py — 文本可预测性检测（Perplexity Gate 简化实现）
检测维度：句长方差/词汇多样性/句式重复/段落均匀度/AI腔密度
用法: python check_text_variety.py "file.md" --threshold 70
退出码: 0=通过 1=警告(≥1项临界) 2=拒绝(≥1项红线)
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
    diffs = sum(abs(a - b) for a in lengths for b in lengths)
    gini = diffs / (2 * len(lengths) * len(lengths) * mean_len) if mean_len > 0 else 1
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
               '然而', '因此', '于是', '随后', '与此同时', '就这样', '不仅如此']
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
    args = parser.parse_args()

    result = analyze_file(args.file)

    if "error" in result:
        print(f"✗ {result['error']}", file=sys.stderr)
        sys.exit(2)

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
