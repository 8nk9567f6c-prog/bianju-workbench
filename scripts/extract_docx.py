#!/usr/bin/env python3
"""Extract text from docx files via zipfile + XML parsing."""
import zipfile, os, sys
from xml.etree import ElementTree as ET

def extract_docx(fpath, outpath):
    with zipfile.ZipFile(fpath) as z:
        xml_content = z.read('word/document.xml').decode('utf-8')
        tree = ET.fromstring(xml_content)
        paragraphs = []
        ns = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
        for p in tree.iter(f'{ns}p'):
            texts = []
            for t in p.iter(f'{ns}t'):
                if t.text:
                    texts.append(t.text)
            line = ''.join(texts).strip()
            if line:
                paragraphs.append(line)
        text = '\n'.join(paragraphs)
    with open(outpath, 'w', encoding='utf-8') as f:
        f.write(text)
    return len(text), len(paragraphs)

if __name__ == '__main__':
    base = sys.argv[1] if len(sys.argv) > 1 else '作品/这个破碗觉醒黄金眼/_源文档'
    files = [f for f in os.listdir(base) if f.endswith('.docx')]
    for fname in files:
        fpath = os.path.join(base, fname)
        outname = fname.replace('.docx', '.txt')
        outpath = os.path.join(base, outname)
        try:
            chars, lines = extract_docx(fpath, outpath)
            print(f'OK {outname} — {chars} chars, {lines} lines')
        except Exception as e:
            print(f'ERR {fname}: {e}')
