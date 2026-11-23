"""軍表健檢的比較基準（2026-11-24）：拿 metalists/data 裡全部讀得到的 meta 表（4 勝以上）跑 listcheck，
存 data/listcheck_bench.json：all＝每類目標「一輪打掉幾個」的 25%／50%／75% 分位；fac＝每個陣營每類目標每 100 分最會打的單位（推薦用）。
跑法：python3 tools/lc_bench.py（約 1 分鐘）。meta 表每天 11:40 更新，這份不用天天重跑，大改版或規則改了再跑。"""
import glob, json, os, sys, statistics as st, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import engine
db = engine.DB()
opt = {'abil': {'a': {}, 'b': {}}}
T = engine.lc_targets(db)
vals = {k: [] for k, *_ in T}
fac = {}
n = 0
for f in sorted(glob.glob(os.path.join(ROOT, 'metalists', 'data', '*.json'))):
    if f.endswith('index.json'):
        continue
    d = json.load(open(f, encoding='utf-8'))
    for l in d.get('lists', []):
        if not l.get('text') or not l.get('u'):
            continue
        a = engine.parse_list(l['text'], db)
        if len(a['units']) < 5 or len(a['unknown']) > 1 or not 1900 <= a['points'] <= 2010:
            continue
        engine.resolve(a, {})
        engine.apply_dets(a, {}, db)
        rows = engine.lc_rows(a, opt, db)
        n += 1
        for i, (k, *_) in enumerate(T):
            vals[k].append(sum(r[i][0] + r[i][1] for r in rows))
        F = fac.setdefault(a['faction'], {})
        for u, r in zip(a['units'], rows):
            for i, (k, *_) in enumerate(T):
                eff = (r[i][0] + r[i][1]) / max(u['points'], 1) * 100
                best = F.setdefault(k, {})
                if eff > best.get(u['name'], (0,))[0]:
                    best[u['name']] = (round(eff, 3), u['points'], round(r[i][0], 2), round(r[i][1], 2))
q = lambda xs: [round(x, 2) for x in st.quantiles(xs, n=4)] if len(xs) >= 4 else []
out = dict(date=dt.date.today().isoformat(), n=n, all={k: q(v) for k, v in vals.items()},
           fac={fa: {k: [dict(name=nm, per100=e, points=p, shoot=s, melee=m) for nm, (e, p, s, m) in sorted(b.items(), key=lambda kv: -kv[1][0])[:5]]
                     for k, b in F.items()} for fa, F in fac.items()})
json.dump(out, open(os.path.join(ROOT, 'data', 'listcheck_bench.json'), 'w', encoding='utf-8'), ensure_ascii=False)
print(n, '張表；分位', out['all'])
