"""分隊（Detachment）和強化（Enhancement）的中文名 → 英文名（2026-11-15）。
來源跟 update_zh.py 一樣是官方點數網站的英文版和簡體中文版，照每個項目帶的同一個編號（UUID）配對。
只留英文名在 Wahapedia 的 Detachments.csv／Enhancements.csv 裡找得到的（避免抓到別的東西）。
寫出 data/zh_dets.json：{"det": {中文: 英文}, "enh": {中文: 英文}}
用法：python3 update_zh_det.py [存放網頁的資料夾]"""
import json, os, re, sys
import update_zh as U

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import engine

clean = lambda s: re.sub(r'\s*[（(](?:upgrade|升级|升級|one per army|每支军队限一个|每支軍隊限一個)[)）]', '', s, flags=re.I).strip()
dets_en = {engine.norm(r['name']): r['name'] for r in engine.rd_safe('Detachments') if r.get('name')}
enh_en = {engine.norm(clean(r['name'])): r['name'] for r in engine.rd_safe('Enhancements') if r.get('name')}
slugs = sorted(set(re.findall(r'href="/en/([a-z0-9-]+)"', U.fetch('en', ''))))
det, enh, skipped = {}, {}, 0
for slug in slugs:
    en, zh = U.page('en', slug), U.page('zh', slug)
    for k, (cls, e) in en.items():
        z = zh.get(k, ('', []))[1]
        if not e or not z or not U.CJK.search(z[0]):
            continue
        ce, cz = clean(e[0]), clean(z[0])
        if len(e) > 1 and re.fullmatch(r'\d+DP', e[1]) and engine.norm(ce) in dets_en:
            det[cz] = dets_en[engine.norm(ce)]
            # 分隊方塊裡的強化：「名稱、點數」成對排在 ENHANCEMENTS 之後，兩種語言位置一樣
            if len(e) == len(z) and 'ENHANCEMENTS' in [x.upper() for x in e]:
                i = [x.upper() for x in e].index('ENHANCEMENTS')
                for a, b in zip(e[i + 1::2], z[i + 1::2]):
                    if engine.norm(clean(a)) in enh_en and U.CJK.search(b):
                        enh[clean(b)] = enh_en[engine.norm(clean(a))]
        elif engine.norm(ce) in enh_en:
            enh[cz] = enh_en[engine.norm(ce)]
    print(slug, len(det), len(enh), flush=True)
json.dump(dict(det=det, enh=enh), open(os.path.join(HERE, 'data', 'zh_dets.json'), 'w'), ensure_ascii=False, indent=0)
print(f'分隊 {len(det)} 個、強化 {len(enh)} 個；Wahapedia 分隊 {len(dets_en)}、強化 {len(enh_en)}')
