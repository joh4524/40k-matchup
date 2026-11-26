#!/usr/bin/env python3
"""黑圖書館軍表能讀多少：拿 meta 表（meta/meta.json 各陣營代表表）用到的單位和武器，看社群中文譯名表（data/zh_comm.json）有沒有（2026-11-27）。
黑圖書館用社群譯名；這裡沒有的，黑圖書館軍表貼進來就要靠官方中文名、名字相近＋分數、或資料卡預設武器。
用法：python3 tools/bl_coverage.py [-v]
"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import engine
V = '-v' in sys.argv
db = engine.DB()
zc = json.load(open(os.path.join(ROOT, 'data', 'zh_comm.json'), encoding='utf-8'))
cu = {engine.norm(e) for v in zc['units'].values() for e in v}
cw = {sh: {engine.norm(e) for e in m.values()} for sh, m in zc['weap'].items()}
gw = {engine.norm(e) for e in zc['gw'].values()} | {e for v in zc['fw'].values() for e in v}
meta = json.load(open(os.path.join(ROOT, 'meta', 'meta.json'), encoding='utf-8'))
print('陣營｜單位有社群中文名｜武器有中文名｜沒名字的常見單位')
for f in meta['factions']:
    us, ws, miss = {}, {}, {}
    for b in f.get('builds', []):
        for txt in [b.get('list_text', '')] + [x.get('list_text', '') for x in b.get('lists', []) if isinstance(x, dict)]:
            if not txt:
                continue
            r = engine.parse_list(txt, db)
            for u in r['units']:
                for g in u['groups']:
                    sh = g['src']
                    us[sh] = engine.norm(sh) in cu
                    if not us[sh]:
                        miss[sh] = miss.get(sh, 0) + 1
                    for c, profs in g['weapons']:
                        base = re.sub(r'\s*[-–—]\s.*$', '', profs[0]['name']).strip()
                        ws[(sh, base)] = engine.norm(base) in cw.get(sh, set()) or engine.norm(base) in gw
    if not us:
        continue
    pu = 100 * sum(us.values()) // len(us); pw = 100 * sum(ws.values()) // max(1, len(ws))
    top = '、'.join(k for k, _ in sorted(miss.items(), key=lambda x: -x[1])[:4])
    print(f"{f['faction']}｜{pu}%（{sum(us.values())}/{len(us)}）｜{pw}%（{sum(ws.values())}/{len(ws)}）｜{top}")
    if V:
        print('   沒中文名的武器：', sorted(f'{s}:{w}' for (s, w), ok in ws.items() if not ok)[:15])
