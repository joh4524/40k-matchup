#!/usr/bin/env python3
"""顏料配對／配色用的資料（2026-11-26，網站計畫 ⑪⑫）。
來源：~/paint-app/src/paints.json（由 Arcturus5404/miniature-paints 轉成，MIT 授權，色碼是近似值）。
輸出 data/paints.json：{"sets": [[品牌, 系列, 種類, 主系列]], "p": [[系列編號, 名稱, 色號, "#RRGGBB", 金屬]]}
種類：o＝一般不透明漆、t＝透明／特殊（洗色、Contrast、Speedpaint、底漆、噴罐…，配色不用）、x＝停產（配對時只當來源）。
主系列 1＝各品牌塗模型常用的那幾個系列（預設只在這些裡面找；噴筆用 Air、噴罐、工藝漆等是 0）。
金屬 1＝金屬漆：資料只有色碼，看不出金屬，所以用系列名和漆名猜（⚠️ 可能漏判或誤判）；配對時金屬只配金屬。
用法：python3 tools/paints_build.py [來源 json]
"""
import json, os, re, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser('~/paint-app/src/paints.json')
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'paints.json')
T = re.compile(r'wash|shade|contrast|speedpaint|xpress|glaze|ink|technical|\btone\b|fx|weathering|liquid|primer|spray|clear|crystal|primary color pigments|soil|inktensity|instant|pastel|auxiliary|lascivus|modulation|lacquer|dry', re.I)

MAIN = {
    'Citadel': r'^(Base|Layer|Contrast|Shade|Technical|Dry)$',
    'Vallejo': r'^(Game Color|Model Color|Mecha Color|Metal Color|Panzer Aces|Xpress Color|Game Color Wash|Xpress Color Intense)$',
    'Army Painter': r'^(Warpaints Fanatic|Warpaints Fanatic Wash|Speedpaint Set 2\.0|Metallic Colours Paint Set|Skin Tones Paint Set)$',
    'AK Interactive': r'3rd Gen',
    'Scale75': r'Fantasy|Scale Color|Metal N Alchemy|Warfront|Inktensity|Instant',
    'P3': r'.', 'Reaper': r'Core Colors|Bones|Pathfinder',
    'Mr.Hobby': r'Acrysion|Aqueous', 'Tamiya': r'Acrylics',
}
NOTMAIN = re.compile(r'\bAir\b|Primer|Spray|Auxiliary|Pastel', re.I)
METSET = re.compile(r'metal|metallic|liquid gold|alchemy', re.I)
METNAME = re.compile(r'metal|gold|silver|bronze|brass|copper|steel|iron\b|ironbreaker|alloy|leadbelcher|retributor|stormhost|alumin|chrome|titanium|pewter|mithril|platinum|tin bitz|screaming bell|plate mail|bell', re.I)
NOTMET = re.compile(r'bronze green|interior|yellow|drab|oxide|rust|brown|ochre|golden|marigold|goldenrod|legion|bluebell', re.I)

rows = json.load(open(SRC, encoding='utf-8'))
sets, idx, out = [], {}, []
for r in rows:
    s = re.sub(r'\s+', ' ', r['s']).strip()
    kind = 'x' if 'discontinued' in s.lower() else 't' if T.search(s) else 'o'
    key = (r['b'], s)
    if key not in idx:
        idx[key] = len(sets)
        main = 1 if re.search(MAIN.get(r['b'], r'.'), s) and not NOTMAIN.search(s) and kind != 'x' else 0
        sets.append([r['b'], s, kind, main])
    code = '' if r['c'] in ('null', 'None') else r['c']
    nm = r['n']
    # AK 的金屬漆都在 Metallic 系列，只看系列；其他品牌再看漆名（灰色名稱多半不是金屬，除了 Gunmetal）
    met = 1 if METSET.search(s) or (r['b'] != 'AK Interactive' and METNAME.search(nm) and not NOTMET.search(nm) and (not re.search(r'gr[ae]y', nm, re.I) or re.search(r'gun ?metal', nm, re.I))) else 0
    out.append([idx[key], r['n'], code, r['h'].upper(), met])
json.dump({'src': 'Arcturus5404/miniature-paints (MIT)', 'sets': sets, 'p': out},
          open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(len(sets), 'sets', len(out), 'paints', os.path.getsize(OUT) // 1024, 'KB')
