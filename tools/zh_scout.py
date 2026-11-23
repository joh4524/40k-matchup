"""偵察／階段小抄（scout.html，2026-11-24）用的繁體中文名：單位、分隊、強化（官方點數網站的簡體轉繁體），
戰術卡、規則名（warhammer-translate 技能的 rules-terms.tsv，從各陣營中文規則書抄的名字）。寫到 data/zh_scout.json。
跑法：python3 tools/zh_scout.py"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import engine
HOME = os.path.expanduser("~")
sys.path.insert(0, os.path.join(HOME, "warhammer-zh/lib"))
from opencc import OpenCC
s2t = OpenCC("s2t").convert

out = dict(units={}, dets={}, enh={}, rules={})
for zh, ens in json.load(open(os.path.join(ROOT, "data/zh_units.json"), encoding="utf-8")).items():
    for en in (ens if isinstance(ens, list) else [ens]):
        out["units"].setdefault(engine.norm(en), s2t(zh))
zd = json.load(open(os.path.join(ROOT, "data/zh_dets.json"), encoding="utf-8"))
for zh, en in zd.get("det", {}).items():
    out["dets"].setdefault(engine.norm(en), s2t(zh))
for zh, en in zd.get("enh", {}).items():
    out["enh"].setdefault(engine.norm(en), s2t(zh))
tsv = os.path.join(HOME, ".claude/skills/warhammer-translate/references/rules-terms.tsv")
for line in open(tsv, encoding="utf-8"):
    p = line.rstrip("\n").split("\t")
    if len(p) < 4 or p[3] != "other":
        continue
    en = re.sub(r"\s+\d+\s*CP$", "", p[1].strip()).strip()
    # 「戰略技能」是規則書的分類標題，不是卡名
    if p[2] in ("戰略技能",) or not en:
        continue
    out["rules"].setdefault(engine.norm(en), s2t(p[2]))
json.dump(out, open(os.path.join(ROOT, "data/zh_scout.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print({k: len(v) for k, v in out.items()})
