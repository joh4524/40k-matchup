"""比較兩份 Wahapedia 匯出資料的點數和規則差異（2026-11-25，每週自動更新用）。
跑法：python3 tools/points_diff.py 舊資料夾 新資料夾 [--zh]
印出：每個陣營的單位點數變動（舊→新）、新增／移除的資料卡、強化點數變動、分隊／戰術卡數量變動。沒有變動印「沒有變動」。"""
import csv, json, os, sys
from collections import defaultdict

csv.field_size_limit(10 ** 8)


def rd(d, name):
    p = os.path.join(d, name + '.csv')
    if not os.path.exists(p):
        return []
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f, delimiter='|'))


def load(d):
    sheets = {r['id']: (r['name'], r['faction_id']) for r in rd(d, 'Datasheets') if r.get('virtual', '').lower() != 'true'}
    cost = defaultdict(list)
    for r in rd(d, 'Datasheets_models_cost'):
        if r['datasheet_id'] in sheets and r.get('cost'):
            cost[r['datasheet_id']].append((r['description'].strip(), r['cost'].strip()))
    enh = {(r['faction_id'], r['name']): r['cost'] for r in rd(d, 'Enhancements')}
    dets = defaultdict(int)
    for r in rd(d, 'Detachments'):
        dets[r.get('faction_id', '')] += 1
    strats = defaultdict(int)
    for r in rd(d, 'Stratagems'):
        strats[r.get('faction_id', '')] += 1
    return sheets, cost, enh, dets, strats


def main():
    old, new = sys.argv[1], sys.argv[2]
    zh = {}
    try:
        with open(os.path.join(new, 'zh_scout.json'), encoding='utf-8') as f:
            zh = json.load(f).get('units', {})
    except OSError:
        pass
    name_of = lambda n: (zh.get(n.lower().replace('’', "'"), '') + ' ' if zh.get(n.lower().replace('’', "'")) else '') + n
    so, co, eo, do, sto = load(old)
    sn, cn, en, dn, stn = load(new)
    fac = {r['id']: r['name'] for r in rd(new, 'Factions')}
    out = defaultdict(list)
    for i, (nm, f) in sn.items():
        if i not in so:
            out[f].append(f'新增 {name_of(nm)}：' + '、'.join(f'{a} {c}' for a, c in cn.get(i, [])))
        elif co.get(i) != cn.get(i):
            a, b = dict(co.get(i, [])), dict(cn.get(i, []))
            ch = [f'{k} {a.get(k, "—")}→{b.get(k, "—")}' for k in list(dict.fromkeys(list(a) + list(b))) if a.get(k) != b.get(k)]
            if ch:
                out[f].append(f'{name_of(nm)}：' + '、'.join(ch))
    for i, (nm, f) in so.items():
        if i not in sn:
            out[f].append(f'移除 {name_of(nm)}')
    for k in set(eo) | set(en):
        if eo.get(k) != en.get(k):
            out[k[0]].append(f'強化 {k[1]}：{eo.get(k, "—")}→{en.get(k, "—")}')
    for f in set(do) | set(dn):
        if do.get(f) != dn.get(f):
            out[f].append(f'分隊數 {do.get(f, 0)}→{dn.get(f, 0)}')
    for f in set(sto) | set(stn):
        if sto.get(f) != stn.get(f):
            out[f].append(f'戰術卡數 {sto.get(f, 0)}→{stn.get(f, 0)}')
    if not out:
        print('沒有變動')
        return
    for f in sorted(out, key=lambda f: fac.get(f, f)):
        print(f'【{fac.get(f, f)}】{len(out[f])} 項')
        for line in sorted(out[f])[:40]:
            print('・' + line)
        if len(out[f]) > 40:
            print(f'・…另外 {len(out[f]) - 40} 項')


if __name__ == '__main__':
    main()
