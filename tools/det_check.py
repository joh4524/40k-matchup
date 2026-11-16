"""檢查 rules/陣營代號.py（Sonnet 手動標記的軍隊規則／分隊／戰略／強化）。2026-11-16。
用法：python3 tools/det_check.py 陣營代號
印出錯誤（ERROR，一定要改）和提醒（WARN，看一下是不是故意的）。全部沒有 ERROR 時最後一行印「OK」。"""
import importlib.util, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import engine

fid = sys.argv[1]
path = os.path.join(ROOT, 'rules', fid + '.py')
errs, warns = [], []
E = lambda m: errs.append(m)
W = lambda m: warns.append(m)
if not os.path.exists(path):
    sys.exit(f'ERROR 找不到 {path}')
try:
    spec = importlib.util.spec_from_file_location('chk', path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
except Exception as e:
    sys.exit(f'ERROR 檔案跑不起來：{type(e).__name__}: {e}')
ARMY, DET, ENH = getattr(mod, 'ARMY', {}), getattr(mod, 'DET', {}), getattr(mod, 'ENH', {})

dets = {r['id']: r['name'] for r in engine.rd_safe('Detachments') if r.get('faction_id') == fid}
abil = {r['id']: r['name'] for r in engine.rd_safe('Abilities') if r.get('faction_id') == fid}
enh = {engine.enh_key(r['name']): r['name'] for r in engine.rd_safe('Enhancements') if r.get('faction_id') == fid}
db = engine.DB()
sheets = [s for s in db.sheets.values() if s['faction'] == fid]
kws = set().union(*[s['kw'] for s in sheets]) if sheets else set()
names = [s['name'].lower() for s in sheets]

ATT = {'hit', 'wound', 'ap', 'dmg', 'attacks', 'strength', 'rr_hit', 'rr_wound', 'crit_hit', 'crit_wound', 'ign', 'mw', 'rr1', 'kw', 'skill', 'tgt_t'}
DEF = {'hit', 'wound', 'ap', 'dmg', 'inv', 'fnp', 'half', 'cover', 'sv', 'sv3'}
CONDS = {None, 'charge', 'half', 'still', 's_gt_t', 't_gt_t'}

for k in dets:
    if k not in DET:
        E(f'分隊 {k} {dets[k]} 沒有寫（沒有能算的也要寫 \'{k}\': [] 並加註解說明為什麼）')
for k in DET:
    if k not in dets:
        E(f'DET 的 key {k!r} 不是這個陣營的分隊 id')
for k in ARMY:
    if k not in abil:
        E(f'ARMY 的 key {k!r} 不是這個陣營的軍隊規則 id（Abilities.csv）')
for k in abil:
    if k not in ARMY:
        W(f'軍隊規則 {k} {abil[k]} 沒寫進 ARMY（不影響傷害就不用寫）')
for k in ENH:
    if engine.enh_key(k) not in enh:
        E(f'ENH 的 key {k!r} 不是這個陣營的強化名（要跟 Enhancements.csv 的英文名一樣）')

# 範例武器和目標：拿這個陣營第一把射擊、第一把近戰武器打一個 T5 Sv3+ 的步兵
dummy_t = dict(kw={'INFANTRY'}, T=5, Sv=3, inv=0, fnp=0, W=2, models=5, stealth=False, dfx=[], wounds=10)
wr = next((w for s in sheets for w in s['weapons'] if not w['melee'] and engine.num(w['skill'])), None)
wm = next((w for s in sheets for w in s['weapons'] if w['melee'] and engine.num(w['skill'])), None)


def chk_tag(t, where):
    if not isinstance(t, dict) or 'effs' not in t:
        E(f'{where}：標記要用 T(...) 做')
        return
    if t['side'] not in ('att', 'def'):
        E(f'{where}：side 只能是 att 或 def')
    if t['scope'] not in ('all', 'ranged', 'melee'):
        E(f'{where}：scope 只能是 all／ranged／melee')
    if t.get('cond') not in CONDS:
        E(f'{where}：cond {t.get("cond")!r} 程式不認得（可用 {sorted(c for c in CONDS if c)}）')
    ok = ATT if t['side'] == 'att' else DEF
    for e in t['effs']:
        if not (isinstance(e, tuple) and len(e) == 2):
            E(f'{where}：effs 每一項要是 (效果, 數值)')
            continue
        k, v = e
        if k not in ok:
            E(f'{where}：{t["side"]} 不能用效果 {k!r}（可用 {sorted(ok)}）')
        if k in ('rr_hit', 'rr_wound') and v not in ('1', 'all'):
            E(f'{where}：{k} 的值要是 \'1\' 或 \'all\'')
        if k == 'kw':
            if not engine.parse_kw(v):
                E(f'{where}：武器關鍵字 {v!r} 讀不懂（例：\'LETHAL HITS\'、\'SUSTAINED HITS 1\'、\'ANTI-INFANTRY 4+\'）')
    for kk in t.get('tkw', []) + t.get('tkw_not', []):
        if not re.fullmatch(r'[A-Z0-9 \-’\']+', kk):
            W(f'{where}：目標關鍵字 {kk!r} 要全大寫英文')
    # 跑一次，確定程式算得動、而且真的有影響
    try:
        tgt = dict(dummy_t, kw=set(t.get('tkw') or ['INFANTRY']))
        moved = False
        for w in (wr, wm):
            if not w:
                continue
            if t['side'] == 'att':
                base = engine.weapon_damage(w, tgt, {'charge': True, 'half': True, 'still': True}, [], 4)
                new = engine.weapon_damage(w, tgt, {'charge': True, 'half': True, 'still': True}, [dict(t, cond=None, weapon=None)], 4)
            else:
                base = engine.weapon_damage(w, tgt, {}, [], 4)
                new = engine.weapon_damage(w, dict(tgt, dfx=[dict(t, cond=None)]), {}, [], 4)
            moved |= abs(new - base) > 1e-9
        if not moved and not any(k in ('mw', 'rr1', 'crit_hit', 'crit_wound') for k, v in t['effs']):   # 爆擊門檻要武器有 Lethal／Sustained／Dev 才有差
            W(f'{where}：用範例武器算，這個標記沒有改變任何傷害（確認效果方向和 scope）')
    except Exception as e:
        E(f'{where}：計算時出錯 {type(e).__name__}: {e}')


def chk_rule(r, where):
    if not isinstance(r, dict) or 'tags' not in r:
        E(f'{where}：要用 R(...) 做')
        return
    if r['kind'] not in ('規則', '戰略', '軍隊規則'):
        E(f'{where}：kind 只能是 規則／戰略／軍隊規則')
    if r['kind'] == '戰略' and not str(r.get('cp', '')).strip():
        E(f'{where}：戰略要寫 cp')
    if r['kind'] == '戰略' and r.get('on'):
        W(f'{where}：戰略預設 on=True？（通常戰略預設不開）')
    for kk in r.get('need', []) + r.get('need_not', []) + r.get('model_kw', []) + r.get('model_not', []):
        if kk not in kws and kk not in ('MONSTER', 'VEHICLE', 'CHARACTER', 'INFANTRY', 'MOUNTED', 'WALKER', 'FLY'):
            W(f'{where}：關鍵字 {kk!r} 這個陣營沒有任何資料卡有（拼錯？）')
    for n in r.get('names', []) + r.get('names_not', []):
        if not any(n.lower() in x for x in names):
            W(f'{where}：names {n!r} 對不到這個陣營任何資料卡名')
    if not r['tags']:
        E(f'{where}：tags 是空的（沒有能算的效果就不要寫這條）')
    for i, t in enumerate(r['tags']):
        chk_tag(t, f'{where} 標記{i + 1}')


for k, spec in ARMY.items():
    for r in spec.get('rules', []):
        chk_rule(r, f'ARMY {abil.get(k, k)}｜{r.get("name")}')
for k, rules in DET.items():
    for r in rules:
        chk_rule(r, f'DET {dets.get(k, k)}｜{r.get("name")}')
for k, tags in ENH.items():
    for i, t in enumerate(tags):
        chk_tag(t, f'ENH {k} 標記{i + 1}')

n_rules = sum(len(v) for v in DET.values()) + sum(len(v.get('rules', [])) for v in ARMY.values())
print(f'{fid}：分隊 {len(DET)}/{len(dets)}、規則和戰略 {n_rules} 條、強化 {len(ENH)} 個')
for m in warns:
    print('WARN', m)
for m in errs:
    print('ERROR', m)
print('OK' if not errs else f'{len(errs)} 個 ERROR')
