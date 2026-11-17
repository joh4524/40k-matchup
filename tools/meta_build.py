#!/usr/bin/env python3
"""各陣營 GT 前段（全勝／只輸一場）的代表軍表，給網頁的「對手選單」和「打全 meta」用（2026-11-17，使用者：「12」）。

資料：listhammer.info 的 /factions/<slug> 頁（跟 noon digest 同一個來源；robots.txt 不准碰的 /api/ /list/ /players/ /events/ 都不碰）。
2026-11-17 使用者同意放公開版（meta/meta.json 進 git，網頁註明來源連結）；網站的 robots 寫 use=reference。
做法：每個陣營照分隊組合分組，取表最多的前 3 組（至少 2 張）；每組挑「跟同組其他表最像」的一張真實軍表當代表
（比單位張數的加權 Jaccard），不自己拼湊。只用 2026-09-30 平衡調整之後的比賽；禁軍只用 10/21 新 Codex 之後、而且不是只有 Lions of the Emperor 的表。
用法：python3 tools/meta_build.py   → 寫 meta/meta.json"""
import datetime as dt, json, os, pathlib, sys, time
HERE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, os.path.expanduser('~/listhammer'))
import engine, report

SLUGS = ['adepta-sororitas', 'adeptus-custodes', 'adeptus-mechanicus', 'aeldari', 'astra-militarum', 'black-templars', 'blood-angels',
         'chaos-daemons', 'chaos-knights', 'chaos-space-marines', 'dark-angels', 'death-guard', 'deathwatch', 'drukhari', 'emperors-children',
         'genestealer-cult', 'grey-knights', 'imperial-agents', 'imperial-knights', 'leagues-of-votann', 'necrons', 'orks', 'space-marines',
         'space-wolves', 'tau-empire', 'thousand-sons', 'tyranids', 'world-eaters']
SINCE = '2026-09-30'                                     # 使用者 11/3：最新平衡調整之前的都不用
SPECIAL = {'adeptus-custodes': dict(since='2026-10-21', old_combo='Lions of the Emperor')}   # 使用者 11/3：禁軍新 Codex
MIN_LISTS, TOP_BUILDS = 2, 3


def page_for(slug):
    today = dt.date.today().isoformat()
    f = report.ROOT / 'meta-cache' / f'{today}_{slug}.json'
    if f.exists():
        return json.loads(f.read_text())
    name = slug.replace('-', ' ').title()
    p = report.cached_page(slug, name)
    time.sleep(2)                                        # 對網站客氣一點
    return p


def combo_of(l):
    return ' + '.join(sorted(x.strip().replace('‑', '-') for x in (l.get('detachment') or '').split('|') if x.strip()))


def vec(units):
    v = {}
    for u in units:
        v[u['name']] = v.get(u['name'], 0) + 1
    return v


def sim(a, b):
    keys = set(a) | set(b)
    top = sum(max(a.get(k, 0), b.get(k, 0)) for k in keys)
    return sum(min(a.get(k, 0), b.get(k, 0)) for k in keys) / top if top else 0.0


def main():
    db = engine.DB()
    out = dict(updated=dt.datetime.now().strftime('%Y-%m-%d %H:%M'), source='https://listhammer.info', since=SINCE, factions=[])
    for slug in SLUGS:
        try:
            page = page_for(slug)
        except Exception as e:
            print('讀不到', slug, e, file=sys.stderr)
            continue
        sp = SPECIAL.get(slug, {})
        since = sp.get('since', SINCE)
        lists = [l for l in page['lists'] if (l.get('startDate') or '') >= since and l.get('listText')]
        if sp.get('old_combo'):
            lists = [l for l in lists if combo_of(l) != sp['old_combo']]
        groups = {}
        for l in lists:
            groups.setdefault(combo_of(l) or '（沒寫分隊）', []).append(l)
        builds = []
        for combo, ls in sorted(groups.items(), key=lambda kv: -len(kv[1]))[:TOP_BUILDS]:
            if len(ls) < MIN_LISTS and builds:
                break
            parsed = []
            for l in ls:
                p = engine.parse_list(l['listText'], db)
                if p['units'] and not p['unknown']:
                    parsed.append((l, p, vec(p['units'])))
            if not parsed:
                continue
            best = max(parsed, key=lambda x: (sum(sim(x[2], y[2]) for y in parsed), int(x[0].get('wins') or 0)))
            l, p = best[0], best[1]
            w = sum(int(x.get('wins') or 0) for x in ls)
            lo = sum(int(x.get('losses') or 0) for x in ls)
            builds.append(dict(combo=combo, n=len(ls), record=f'{w}-{lo}', list_text=l['listText'], player=l.get('playerName', ''),
                               event=l.get('eventName', ''), date=l.get('startDate', ''), result=f"{l.get('wins')}-{l.get('losses')}",
                               points=p['points'], units=len(p['units'])))
        if builds:
            out['factions'].append(dict(slug=slug, faction=page['stats'].get('faction') or slug, total=len(lists), builds=builds))
        print(slug, len(lists), [(b['combo'][:40], b['n']) for b in builds], flush=True)
    out['factions'].sort(key=lambda f: -f['total'])
    (HERE / 'meta').mkdir(exist_ok=True)
    (HERE / 'meta' / 'meta.json').write_text(json.dumps(out, ensure_ascii=False, indent=1))
    print('寫好', sum(len(f['builds']) for f in out['factions']), '張代表表')


if __name__ == '__main__':
    main()
