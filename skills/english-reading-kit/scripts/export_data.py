#!/usr/bin/env python3
"""Reverse-engineer structured data from generated reading-kit pages.

Reads the study page (English + translation + vocabulary cards) and emits:
  chapter.json        nested: sections -> paragraphs / vocabulary
  paragraphs.csv      id,section,audio,en,zh
  vocabulary.csv      id,word,ipa,pos,level,meaning,example,memory,audio
  audio_manifest.csv  path,bytes  (only for files that exist)

The ids are the contract: paragraph 007 <-> audio/para/007.mp3,
vocabulary 012 <-> audio/words/012.mp3.

Usage:
  python3 export_data.py --html harry-potter-ch1-study.html --root . --out data
"""
import argparse
import csv
import html
import json
import os
import re


def clean(s):
    t = re.sub(r"<[^>]+>", " ", s)
    t = html.unescape(t)
    return re.sub(r"\s+", " ", t).strip()


def parse(study_html):
    sections = []
    para_i = word_i = 0

    for m in re.finditer(r'<section class="ch" id="(s\d+)">(.*?)</section>', study_html, re.S):
        n = int(m.group(1)[1:])
        body = m.group(2)

        h2 = re.search(r"<h2>(.*?)</h2>", body, re.S).group(1)
        zh = re.search(r'<span class="zh">(.*?)</span>', h2)
        title = re.sub(r'<span class="zh">.*?</span>', "", h2)
        title = re.sub(r'<span class="num">.*?</span>', "", title)
        title = clean(title)

        en_block = re.search(r'<div class="en">(.*?)</div>', body, re.S).group(1)
        en_ps = re.findall(r"<p>(.*?)</p>", en_block, re.S)
        cn_block = re.search(r'<div class="cn">(.*?)</div>', body, re.S).group(1)
        cn_ps = re.findall(r"<p>(.*?)</p>", cn_block, re.S)

        if len(en_ps) != len(cn_ps):
            raise SystemExit(f"section {n}: {len(en_ps)} EN paragraphs but {len(cn_ps)} ZH — fix pairing first")

        vocab = []
        vm = re.search(r'<div class="vocab">(.*?)</div>\s*(?:<div class="petbox">|</section>)', body, re.S)
        if vm:
            for w in re.finditer(
                r'<div class="w(?: ph| sy)?">\s*<div class="wh">(.*?)</div>\s*'
                r'<div class="wm">(.*?)</div>\s*<div class="we">(.*?)</div>\s*<div class="wt">(.*?)</div>',
                vm.group(1), re.S):
                word_i += 1
                head = w.group(1)
                ipa = re.search(r'class="ipa">(.*?)<', head)
                pos = re.search(r'class="pos">(.*?)<', head)
                lv = re.search(r'class="lv (\w+)"', head)
                vocab.append({
                    "id": f"{word_i:03d}",
                    "word": clean(re.search(r"<b>(.*?)</b>", head).group(1)),
                    "ipa": ipa.group(1) if ipa else "",
                    "pos": pos.group(1) if pos else "",
                    "level": lv.group(1) if lv else "",
                    "meaning": clean(w.group(2)),
                    "example": clean(w.group(3)),
                    "memory": clean(w.group(4)),
                    "audio": f"audio/words/{word_i:03d}.mp3",
                })

        paragraphs = []
        for e, c in zip(en_ps, cn_ps):
            para_i += 1
            paragraphs.append({
                "id": f"{para_i:03d}",
                "section": n,
                "en_html": re.sub(r"\s+", " ", e).strip(),
                "en": clean(e),
                "zh": clean(c),
                "audio": f"audio/para/{para_i:03d}.mp3",
            })

        sections.append({
            "n": n,
            "title": title,
            "title_zh": zh.group(1) if zh else "",
            "audio": f"audio/{n:02d}.mp3",
            "paragraphs": paragraphs,
            "vocabulary": vocab,
        })
    return sections


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True, help="study page with .en / .cn / .vocab blocks")
    ap.add_argument("--root", default=".", help="folder audio paths are relative to")
    ap.add_argument("--out", default="data")
    args = ap.parse_args()

    sections = parse(open(args.html, encoding="utf-8").read())
    os.makedirs(args.out, exist_ok=True)

    json.dump(sections, open(f"{args.out}/chapter.json", "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)

    with open(f"{args.out}/paragraphs.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "section", "audio", "en", "zh"])
        for s in sections:
            for p in s["paragraphs"]:
                w.writerow([p["id"], p["section"], p["audio"], p["en"], p["zh"]])

    with open(f"{args.out}/vocabulary.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "word", "ipa", "pos", "level", "meaning", "example", "memory", "audio"])
        for s in sections:
            for v in s["vocabulary"]:
                w.writerow([v["id"], v["word"], v["ipa"], v["pos"], v["level"],
                            v["meaning"], v["example"], v["memory"], v["audio"]])

    with open(f"{args.out}/audio_manifest.csv", "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["path", "bytes"])
        for s in sections:
            for path in [s["audio"]] + [p["audio"] for p in s["paragraphs"]] + [v["audio"] for v in s["vocabulary"]]:
                full = os.path.join(args.root, path)
                w.writerow([path, os.path.getsize(full) if os.path.exists(full) else "MISSING"])

    paras = sum(len(s["paragraphs"]) for s in sections)
    words = sum(len(s["vocabulary"]) for s in sections)
    print(f"{len(sections)} sections · {paras} paragraphs · {words} vocabulary → {args.out}/")


if __name__ == "__main__":
    main()
