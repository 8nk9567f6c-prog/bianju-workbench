import re
import sys

with open(r'C:\Users\17928\Desktop\真千金只想考清华\verify_script.md', 'r', encoding='utf-8') as f:
    text = f.read()

ep_markers = list(re.finditer(r'（第(\d+)集）', text))

episodes = {}
for i, m in enumerate(ep_markers):
    ep_num = int(m.group(1))
    start = 0 if i == 0 else ep_markers[i-1].end()
    end = m.start()
    episodes[ep_num] = text[start:end]

output_lines = []

for ep_num in sorted(episodes.keys()):
    content = episodes[ep_num]
    chinese_chars = len(re.findall(r'[一-鿿]', content))
    scenes = len(re.findall(r'^\d+-\d+\s+', content, re.MULTILINE))

    # Dialogue clause checks
    dialogue_violations = []
    for line in content.split('\n'):
        line = line.strip()
        m2 = re.match(r'^[一-鿿\w]+：', line)
        if m2:
            speaker_end = m2.end()
            rest = line[speaker_end:]
            clauses = re.split(r'[，。！？、；：]', rest)
            for c in clauses:
                c = c.strip()
                if c:
                    cn = len(re.findall(r'[一-鿿]', c))
                    if cn > 15:
                        dialogue_violations.append((c, cn, line[:60]))

    # Action clause checks
    action_violations = []
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('△'):
            action_text = re.sub(r'^△\s*', '', line)
            clauses = re.split(r'[，。！？、；：]', action_text)
            for c in clauses:
                c = c.strip()
                if c:
                    cn = len(re.findall(r'[一-鿿]', c))
                    if cn > 20:
                        action_violations.append((c, cn, line[:80]))

    cast_lines = re.findall(r'出场人物[：:](.*?)$', content, re.MULTILINE)
    all_cast = []
    for cl in cast_lines:
        chars = re.split(r'[、，,]', cl)
        all_cast.extend([c.strip() for c in chars if c.strip()])

    status = 'OK' if (350 <= chinese_chars <= 700 and scenes <= 2 and not dialogue_violations and not action_violations) else 'FAIL'
    issues = []
    if chinese_chars > 700: issues.append(f'chars={chinese_chars}>700')
    if chinese_chars < 350: issues.append(f'chars={chinese_chars}<350')
    if scenes > 2: issues.append(f'scenes={scenes}>2')
    if dialogue_violations: issues.append(f'dialogue={len(dialogue_violations)}')
    if action_violations: issues.append(f'action={len(action_violations)}')

    output_lines.append(f'Ep{ep_num}: {chinese_chars} chars | {scenes} scenes | cast={len(all_cast)} | {status}')
    if issues:
        output_lines.append(f'  ISSUES: {" | ".join(issues)}')
    for c, n, orig in dialogue_violations:
        output_lines.append(f'  DIALOGUE({n} chars): [{c}]')
        output_lines.append(f'    Full line: {orig}')
    for c, n, orig in action_violations:
        output_lines.append(f'  ACTION({n} chars): [{c}]')
        output_lines.append(f'    Full line: {orig}')
    output_lines.append('')

total = sum(len(re.findall(r'[一-鿿]', episodes[ep])) for ep in episodes)
output_lines.append(f'TOTAL: {total} | AVG: {total//len(episodes)}')

result = '\n'.join(output_lines)
with open(r'C:\Users\17928\Desktop\真千金只想考清华\verify_result.txt', 'w', encoding='utf-8') as f:
    f.write(result)
print(result)
