"""給 Sonnet 手動標記用：把一個陣營的軍隊規則、分隊規則、分隊戰略、強化的 Wahapedia 原文一次印出來。2026-11-16。
用法：python3 tools/det_prep.py 陣營代號（例如 AM）"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import engine

cl = lambda x: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', x or '')).strip()
fid = sys.argv[1]
fac = {r['id']: r['name'] for r in engine.rd('Factions')}
if fid not in fac:
    sys.exit(f'沒有這個陣營代號：{fid}。可用：' + ', '.join(f'{k}={v}' for k, v in fac.items()))
print(f'# 陣營 {fid} = {fac[fid]}\n')
db = engine.DB()
kws = sorted(set().union(*[s['kw'] for s in db.sheets.values() if s['faction'] == fid] or [set()]))
print('## 這個陣營資料卡上的所有關鍵字（need／need_not／model_kw 只能用這些，或 MONSTER／VEHICLE／CHARACTER／INFANTRY 這類通用的）')
print('、'.join(kws) + '\n')
ab = [r for r in engine.rd_safe('Abilities') if r.get('faction_id') == fid]
print('## 軍隊規則（ARMY 的 key 用這裡的 id）')
for r in ab:
    print(f"- id {r['id']}｜{r['name']}：{cl(r['description'])}")
dets = [r for r in engine.rd_safe('Detachments') if r.get('faction_id') == fid]
da = engine.rd_safe('Detachment_abilities')
st = engine.rd_safe('Stratagems')
en = engine.rd_safe('Enhancements')
print(f'\n## 分隊（共 {len(dets)} 個；DET 的 key 用分隊 id）')
for d in dets:
    print(f"\n### 分隊 id {d['id']}｜{d['name']}（分隊點數 {d.get('dp', '')}）")
    for r in da:
        if r.get('detachment_id') == d['id']:
            print(f"- 規則｜{r['name']}：{cl(r['description'])}")
    for r in st:
        if r.get('detachment_id') == d['id']:
            print(f"- 戰略｜{r['name']}｜{r.get('cp_cost', '')}CP｜{cl(r.get('turn'))}／{cl(r.get('phase'))}：{cl(r['description'])}")
    for r in en:
        if r.get('detachment_id') == d['id']:
            print(f"- 強化｜{r['name']}：{cl(r['description'])}")
