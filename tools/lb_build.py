"""單位排行（Leaderboards，2026-11-24）：meta 表（metalists/data，4 勝以上、讀得到全文的表）裡出現過的每個單位，
用玩家實際帶的裝備和編制，算它打 6 種標準目標一輪打掉幾 %（進攻），和 6 個標準單位打它一輪打掉它幾 %（耐打）。
同名單位取最常見的點數那幾隊的平均。領袖加入的組合（「A + B」）另列一列。寫到 data/leaderboard.json 給 leaderboards.html 讀。
跑法：python3 tools/lb_build.py（約 2 分鐘）。
為什麼不用資料卡的預設裝備：多種模型的小隊，預設裝備讀不準（會整隊都拿特殊武器），排名會亂。
沒算：分隊規則、戰術卡（只算資料卡本身、軍隊規則、領袖給的）。"""
import collections, glob, importlib.util, json, os, sys, statistics as st, datetime as dt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import engine

HOME = os.path.expanduser("~")
try:
    sys.path.insert(0, os.path.join(HOME, "warhammer-zh/lib"))
    from opencc import OpenCC
    s2t = OpenCC("s2t").convert
except Exception:
    s2t = lambda x: x

db = engine.DB()
opt = {"abil": {"a": {}, "b": {}}}
T = engine.lc_targets(db)
A = engine.lc_attackers(db)
zrev = {}
for zh, ens in json.load(open(os.path.join(ROOT, "data", "zh_units.json"), encoding="utf-8")).items():
    for en in (ens if isinstance(ens, list) else [ens]):
        zrev.setdefault(engine.norm(en), s2t(zh))

seen = collections.defaultdict(list)     # (陣營, 單位名) → [(點數, 進攻, 耐打, 模型數, 總傷, T, Sv, inv)]
fzh, nlists = {}, 0
for f in sorted(glob.glob(os.path.join(ROOT, "metalists", "data", "*.json"))):
    if f.endswith("index.json"):
        continue
    d = json.load(open(f, encoding="utf-8"))
    for l in d.get("lists", []):
        if not l.get("text") or not l.get("u"):
            continue
        a = engine.parse_list(l["text"], db)
        if len(a["units"]) < 5 or len(a["unknown"]) > 1:
            continue
        engine.resolve(a, {})
        engine.apply_dets(a, {}, db)
        nlists += 1
        fzh[a["faction"]] = d.get("zh", "")
        off = engine.lc_rows(a, opt, db)
        de = engine.lc_def_rows(a, opt, db)
        for u, o, e in zip(a["units"], off, de):
            t = engine.target_of(u)
            seen[(a["faction"], u["name"])].append((u["points"], o, e, t["models"], t["wounds"], t["T"], t["Sv"], t["inv"]))


def avg(rows):
    return [[round(st.mean(r[i][j] for r in rows), 3) for j in (0, 1)] for i in range(len(rows[0]))]


out_rows = []
for (fac, name), xs in seen.items():
    c = collections.Counter(x[0] for x in xs)
    pts = min(c, key=lambda p: (-c[p], p))
    m = [x for x in xs if x[0] == pts]
    parts = [p.strip() for p in name.split("+")]
    zh = " + ".join(zrev.get(engine.norm(p), "") for p in parts) if all(zrev.get(engine.norm(p)) for p in parts) else ""
    out_rows.append(dict(n=name, zh=zh, f=fac, fz=fzh.get(fac, ""), pts=pts, seen=len(xs), lead="+" in name,
                         models=m[0][3], W=m[0][4], T=m[0][5], Sv=m[0][6], inv=m[0][7], off=avg([x[1] for x in m]), de=avg([x[2] for x in m])))
out_rows.sort(key=lambda r: (r["f"], r["n"]))
res = dict(date=dt.date.today().isoformat(), data_updated=db.updated, lists=nlists,
           refs=[dict(key=k, zh=zh, desc=d) for k, zh, d, x in T], rows=out_rows)
json.dump(res, open(os.path.join(ROOT, "data", "leaderboard.json"), "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(nlists, "張表，", len(out_rows), "個單位（含領袖組合", sum(r["lead"] for r in out_rows), "）")
