"""戰錘 40K 第十一版：兩張軍表互打的期望值計算（2026-11-15 使用者要求，不接 AI）。
資料：data/*.csv 是 Wahapedia 的資料匯出檔（wahapedia.ru/wh40k11ed/the-rules/data-export/），更新用 update_data.sh。
算武器數值、武器關鍵字、讀得懂的單位能力（tags.py／manual.py）、軍隊規則、分隊規則、戰略和強化（army.py 手動整理的，2026-11-15 先做禁軍；其他陣營用 tags.py 自動讀）。
使用者 2026-11-15 逐段核對過、確認的：命中和造傷修正最多 ±1；「無視修正」只無視壞的（掩體讓 BS 變差也不算）；DEVASTATING 的致命傷不溢傷；
保護骰修正沒有上限（修到 7+ 就不用骰），骰 1 一定失敗；扣血一隻一隻扣：攻擊方決定哪把先打、防守方決定誰接、受傷的要先接；整隊加總的方式（手槍二選一、每個模型一把近戰武器等）。
也確認了：CLEAVE X 照 BLAST 每 5 個模型 +X；Stealth 當成掩體（BS 變差 1）；傷害先減半再 -1。
合併單位照核心規則 19.02、05.03：T 用護衛裡最高的；非 CHARACTER 的組先接、CHARACTER 最後；每組用自己的 Sv／無敵。
還沒做的：05.03 的保護骰是一起骰、從最低的結果開始分配，所以排在後面的角色拿到的是比較高的骰子；程式每發獨立算，對領袖的傷害會偏高。
"""
import csv, difflib, functools, itertools, math, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json, string
import tags as tagger
import manual
import army
import zh_glossary

CJK = re.compile(r'[\u4e00-\u9fff]')

DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
csv.field_size_limit(10 ** 9)


def rd(n):
    with open(os.path.join(DATA, n + '.csv'), encoding='utf-8-sig') as f:
        return list(csv.DictReader(f, delimiter='|'))


def rd_safe(n):
    """Wahapedia 有些檔的欄位裡有換行（Stratagems.csv 的 legend），csv 模組會切錯；改用「每筆以 |換行 結尾」來切。"""
    try:
        with open(os.path.join(DATA, n + '.csv'), encoding='utf-8-sig') as f:
            t = f.read()
    except OSError:
        return []
    recs = [r.split('|') for r in re.split(r'\|\r?\n', t) if r.strip()]
    h = recs[0] if recs else []
    return [dict(zip(h, r)) for r in recs[1:] if len(r) >= len(h) - 1]


def norm(s):
    s = re.sub(r'<[^>]+>', '', s or '')
    s = s.replace('‑', '-').replace('‐', '-').replace('–', '-').replace('—', '-').replace('’', "'").replace('‘', "'")
    return re.sub(r'\s+', ' ', s).strip().lower()


def num(s, d=0):
    m = re.search(r'\d+', s or '')
    return int(m[0]) if m else d


# ---------- 骰子 ----------
@functools.lru_cache(None)
def dist(expr):
    """'D6+2'、'2D3'、'3' → {值: 機率}"""
    e = (expr or '').upper().replace(' ', '')
    m = re.fullmatch(r'(?:(\d*)D(\d+))?(?:\+?(\d+))?', e)
    if not m or not e or e == '-':
        return {0: 1.0}
    n, sides, k = int(m[1] or 1) if m[2] else 0, int(m[2] or 0), int(m[3] or 0)
    d = {k: 1.0}
    for _ in range(n):
        nd = {}
        for v, p in d.items():
            for r in range(1, sides + 1):
                nd[v + r] = nd.get(v + r, 0) + p / sides
        d = nd
    return d


def mean(expr):
    return sum(v * p for v, p in dist(expr).items())


@functools.lru_cache(None)
def dist_rr(expr, rr=''):
    """傷害骰可以重骰時的分布（2026-11-17）：rr='all' 骰到比平均低就整個重骰；rr='1' 骰到最小值（單顆骰的 1）才重骰。固定傷害沒差。"""
    d = dist(expr)
    if not rr or len(d) < 2:
        return d
    m = sum(v * p for v, p in d.items())
    lo = min(d)
    bad = {v for v in d if (v < m if rr == 'all' else v == lo)}
    pb = sum(d[v] for v in bad)
    return {v: (0.0 if v in bad else p) + pb * p for v, p in d.items()}


@functools.lru_cache(None)
def lost_dist(dexpr, bonus, fnp, reduce=0, half=False, rr=''):
    """一發沒擋住的攻擊實際讓模型掉幾傷的分布 {k: 機率}（還沒套「不溢傷」；FNP 每點各骰）。rr：傷害骰重骰（見 dist_rr）"""
    keep = (fnp - 1) / 6 if fnp else 1.0
    out = {}
    for d, p in dist_rr(dexpr, rr).items():
        d += bonus
        if half:
            d = math.ceil(d / 2)
        if reduce:
            d = max(1, d - reduce)
        if keep >= 1:
            out[d] = out.get(d, 0) + p
        else:
            for k in range(d + 1):
                out[k] = out.get(k, 0) + p * math.comb(d, k) * keep ** k * (1 - keep) ** (d - k)
    return out


def allocate(models, shots, stats=False, vals=None, dvals=None):
    """一隻一隻扣血（2026-11-15 使用者：攻擊方決定哪把先打、防守方決定誰接，受傷的要先接）。
    models：照接傷順序的每隻模型 W。shots：照開火順序 [(發數, 每發沒擋住機率（一個數，或每隻模型各一個）, 掉血分布)]。
    回傳平均掉的血＝死掉模型的血＋還活著那隻受的傷。發數有小數時，最後一發的機率按比例。"""
    n = len(models)
    off, tot = [], 0
    for wv in models:
        off.append(tot)
        tot += wv
    pr = [0.0] * (tot + 1)                              # 狀態：第 i 隻剩 r 血 → off[i]+r-1；最後一格＝全死
    pr[off[0] + models[0] - 1] = 1.0
    dead = tot
    for trials, q, kd in shots:
        kd = [(k, p) for k, p in kd.items() if k > 0 and p > 0]
        full = int(trials)
        for t in range(full + (1 if trials - full > 1e-9 else 0)):
            frac = 1.0 if t < full else trials - full
            new = [0.0] * (tot + 1)
            new[dead] = pr[dead]
            for i in range(n):
                qq = (q[i] if isinstance(q, (list, tuple)) else q) * frac      # 每隻模型可以有自己的保護（領袖的 Sv／無敵不一樣）
                for r in range(1, models[i] + 1):
                    p0 = pr[off[i] + r - 1]
                    if p0 < 1e-12:
                        continue
                    new[off[i] + r - 1] += p0 * (1 - qq)
                    hit = p0 * qq
                    miss = 1.0
                    for k, pk in kd:
                        miss -= pk
                        if k >= r:
                            j = dead if i + 1 >= n else off[i + 1] + models[i + 1] - 1
                        else:
                            j = off[i] + r - k - 1
                        new[j] += hit * pk
                    new[off[i] + r - 1] += hit * max(0.0, miss)
            pr = new
    left = deadw = 0.0
    for i in range(n):
        rest = sum(models[i + 1:])
        for r in range(1, models[i] + 1):
            left += pr[off[i] + r - 1] * (r + rest)
            deadw += pr[off[i] + r - 1] * off[i]
    if stats:                                           # (平均掉的血, 平均死掉模型的血, 全滅機率, 平均死幾隻, 平均死掉的分數)
        kn = [sum(pr[off[i] + r - 1] for r in range(1, models[i] + 1)) for i in range(n)] + [pr[dead]]   # 剛好死 i 隻的機率（2026-11-16 傷害分佈）
        deadn = sum(pr[off[i] + r - 1] * i for i in range(n) for r in range(1, models[i] + 1)) + pr[dead] * n
        vals = vals or [0.0] * n
        cum = [sum(vals[:i]) for i in range(n)]
        deadv = sum(pr[off[i] + r - 1] * cum[i] for i in range(n) for r in range(1, models[i] + 1)) + pr[dead] * sum(vals)
        # 還活著但受傷的那隻：照掉的血按比例算分數（之後它得先接傷，傷會被帶到下一次攻擊；2026-11-16 使用者：太陽被打殘之後都要先扛）
        partv = sum(pr[off[i] + r - 1] * vals[i] * (models[i] - r) / models[i] for i in range(n) for r in range(1, models[i] + 1))
        if dvals is not None:                           # 防守方心裡的價值（分數＋能力）：死掉的＋殘血按比例，用來挑接傷順序
            dc = [sum(dvals[:i]) for i in range(n)]
            cost = sum(pr[off[i] + r - 1] * (dc[i] + dvals[i] * (models[i] - r) / models[i]) for i in range(n) for r in range(1, models[i] + 1)) + pr[dead] * sum(dvals)
            return tot - left, deadw + pr[dead] * tot, pr[dead], deadn, deadv, partv, cost, kn
        return tot - left, deadw + pr[dead] * tot, pr[dead], deadn, deadv, partv
    return tot - left


def eff_damage(dexpr, bonus, w, fnp, reduce=0, half=False, rr=''):
    """一次沒擋住的攻擊，平均讓一個 W 傷的模型掉幾傷（多的傷害不會溢到別的模型；FNP 每點各骰）。rr：傷害骰重骰（見 dist_rr）"""
    keep = (fnp - 1) / 6 if fnp else 1.0
    tot = 0.0
    for d, p in dist_rr(dexpr, rr).items():
        d += bonus
        if half:
            d = math.ceil(d / 2)
        if reduce:
            d = max(1, d - reduce)
        if keep >= 1:
            tot += p * min(d, w)
        else:
            for k in range(d + 1):
                tot += p * math.comb(d, k) * keep ** k * (1 - keep) ** (d - k) * min(k, w)
    return tot


def enh_key(s):
    """強化名比對用：去掉「(one per army)」「(Upgrade)」「强化」之類"""
    s = re.sub(r'^\s*(?:enhancements?:?|强化|強化)\s*', '', s or '', flags=re.I)
    s = re.sub(r'\s*[（(](?:upgrade|升级|升級|one per army|每支军队限一个|每支軍隊限一個|\+?\d+ ?(?:pts|points|点|點))[)）]', '', s, flags=re.I)
    return norm(s)


# ---------- 資料 ----------
class DB:
    def __init__(self):
        self.updated = rd('Last_update')[0].get('last_update', '')
        self.factions = {norm(r['name']): r['id'] for r in rd('Factions')}
        self.faction_names = {r['id']: r['name'].replace('’', "'") for r in rd('Factions')}
        abil = {r['id']: r['name'] for r in rd('Abilities')}
        self.sheets, self.byname = {}, {}
        for r in rd('Datasheets'):
            if r.get('virtual') == 'true':
                continue
            s = dict(id=r['id'], name=r['name'], faction=r['faction_id'], models=[], weapons=[], kw=set(), fnp=0, stealth=False, costs=[], tags=[], fab=set(), abil_all=[], role=r.get('role', ''), loadout=re.sub(r'<[^>]+>', '', r.get('loadout', '')), options='')
            self.sheets[r['id']] = s
            self.byname.setdefault(norm(r['name']), []).append(s)
        for r in rd('Datasheets_models'):
            s = self.sheets.get(r['datasheet_id'])
            if s:
                s['models'].append(dict(name=r['name'], M=num(r['M']), T=num(r['T'], 1), Sv=num(r['Sv'], 7), inv=num(r['inv_sv']), W=num(r['W'], 1), OC=num(r['OC'])))
        for r in rd('Datasheets_wargear'):
            s = self.sheets.get(r['datasheet_id'])
            if s and r['name']:
                base = re.split(r'\s[–—-]\s', re.sub(r'<[^>]+>', '', r['name']))[0]
                s['weapons'].append(dict(name=re.sub(r'<[^>]+>', '', r['name']), base=norm(base), melee=r['type'].lower() == 'melee', range=r['range'],
                                         A=r['A'], skill=r['BS_WS'], S=r['S'], AP=r['AP'], D=r['D'], kw=parse_kw(r['description']),
                                         desc=re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', r['description'] or '')).strip()))
        for r in rd('Datasheets_keywords'):
            s = self.sheets.get(r['datasheet_id'])
            if s and r['keyword']:
                s['kw'].add(r['keyword'].upper())
        for r in rd('Datasheets_abilities'):
            s = self.sheets.get(r['datasheet_id'])
            if s and r['type'] in ('Datasheet', 'Wargear') and r['description']:
                s['tags'] += tagger.tag_ability(r['name'], r['description'])
            if s and r['type'] == 'Faction':
                s['fab'].add(r['ability_id'])
            if s and r['name'].strip().upper() == 'ORDERS':  # 星界軍軍官能下幾個命令、給誰（2026-11-16 使用者：角色要比單位價值，Lord Solar 的命令也算）
                d = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', r['description'] or '')).upper().replace('’', "'")
                mo = re.search(r'(\d+) ORDER', d)
                only = re.search(r'ONLY ISSUE THE (.+?) ORDERS', d)
                s['orders'] = dict(n=int(mo[1]) if mo else 1,
                                   kw=[k for k in ('REGIMENT', 'SQUADRON', 'TITANIC', 'CATACHAN JUNGLE FIGHTERS', "GAUNT'S GHOSTS") if k in d],
                                   only=only[1] if only else '')
            if s and r['type'] in ('Datasheet', 'Wargear', 'Core', 'Faction'):      # 全部列出來給使用者驗算（2026-11-15）
                nm = r['name'] or abil.get(r['ability_id'], '')
                if r['parameter'] and r['type'] == 'Core':
                    nm += ' ' + r['parameter'] + ('+' if nm.startswith('Feel No Pain') and not r['parameter'].endswith('+') else '')
                if nm and nm not in [a['name'] for a in s['abil_all']]:
                    s['abil_all'].append(dict(name=nm, type=r['type'], model=r['model'] or ''))
            if not s or r['type'] != 'Core':
                continue
            n = abil.get(r['ability_id'], '')
            if n == 'Feel No Pain' and not r['model']:
                s['fnp'] = num(r['parameter'])
            elif n == 'Stealth':
                s['stealth'] = True
        for r in rd('Datasheets_models_cost'):
            s = self.sheets.get(r['datasheet_id'])
            if s and r['cost'].strip().isdigit():
                s['costs'].append((r['description'], int(r['cost'])))
        for r in rd('Datasheets_options'):
            s = self.sheets.get(r['datasheet_id'])
            if s:
                s['options'] += ' ' + norm(re.sub(r'<[^>]+>', ' ', r['description']))
        for nm, ts in manual.MANUAL.items():
            for sh in self.byname.get(norm(nm), []):
                sh['tags'] = [t for t in sh['tags'] if t['name'] not in {x['name'] for x in ts}] + ts
        self.allnames = list(self.byname)
        try:                                             # 中文單位名 → 英文名（update_zh.py 從官方點數網站做的）
            with open(os.path.join(DATA, 'zh_units.json'), encoding='utf-8') as f:
                self.zh = {norm(k): (v if isinstance(v, list) else [v]) for k, v in json.load(f).items()}
        except OSError:
            self.zh = {}
        try:                                             # 黑圖書館／社群中文規則書的譯名（tools/zh_comm_build.py，2026-11-27）：官方中文沒有的才補
            with open(os.path.join(DATA, 'zh_comm.json'), encoding='utf-8') as f:
                zc = json.load(f)
            for k, v in zc.get('units', {}).items():
                lst = self.zh.setdefault(norm(k), [])
                lst += [e for e in v if e not in lst]
            COMM_WEAP.clear()
            COMM_WEAP.update(zc.get('weap', {}))
            COMM_WEAP[''] = zc.get('gw', {})             # 很多資料卡都一樣的（爆弹枪＝Boltgun）：全部資料卡共用
            COMM_WEAP['*'] = zc.get('fw', {})            # 規則翻譯批次的武器譯名：中文 → [英文]，看哪個對得到這張資料卡
        except OSError:
            pass
        try:                                             # 官方點數頁上有的武器中文名（很少），zh_glossary 沒有時用
            with open(os.path.join(DATA, 'zh_wargear.json'), encoding='utf-8') as f:
                self.zh_wargear = json.load(f)
            ZH_WARGEAR.update(self.zh_wargear)
        except OSError:
            self.zh_wargear = {}
        try:                                             # 分隊、強化的中文名（update_zh_det.py 從官方點數網站做的）
            with open(os.path.join(DATA, 'zh_dets.json'), encoding='utf-8') as f:
                zd = json.load(f)
        except OSError:
            zd = {}
        self.zh_det, self.zh_enh = zd.get('det', {}), {enh_key(k): v for k, v in zd.get('enh', {}).items()}
        try:                                             # 社群／黑圖書館的分隊、強化譯名（zh_comm.json）：官方沒有的才補
            with open(os.path.join(DATA, 'zh_comm.json'), encoding='utf-8') as f:
                zc = json.load(f)
            for k, v in zc.get('det', {}).items():
                self.zh_det.setdefault(k, v)
            for k, v in zc.get('enh', {}).items():
                self.zh_enh.setdefault(enh_key(k), v)
        except OSError:
            pass
        self.enh = {}
        for r in rd_safe('Enhancements'):
            if r.get('name'):
                self.enh.setdefault(enh_key(r['name']), []).append(dict(name=r['name'], faction=r.get('faction_id', ''), desc=r.get('description', '')))
        self.load_detachments()

    def load_detachments(self):
        """分隊（Detachments）和它的規則、戰略。只留下 tags.py 讀得懂、會影響傷害的；其他的只計數。2026-11-15。"""
        self.dets, self.det_rules = {}, {}
        for r in rd_safe('Detachments'):
            if r.get('id') and r.get('name'):
                self.dets.setdefault(r['faction_id'], []).append(dict(id=r['id'], name=r['name']))
        def add(det_id, rid, kind, name, cp, text, need):
            ts = tagger.tag_ability(name, text)
            box = self.det_rules.setdefault(det_id, dict(rules=[], unread=0, total=0))
            box['total'] += 1
            if ts:
                box['rules'].append(dict(id=rid, kind=kind, name=name, cp=cp, tags=ts, need=need))
            else:
                box['unread'] += 1
        for r in rd_safe('Detachment_abilities'):
            d = re.sub(r'<[^>]+>', ' ', r.get('description') or '')
            d = re.sub(r'\b(?:a|each) model from your army\b', 'a model in this unit', d, flags=re.I)
            d = re.sub(r'\bunits from your army\b', 'this unit', d, flags=re.I)
            add(r.get('detachment_id') or '', r.get('id', ''), '規則', r.get('name', ''), '', d, [])
        for r in rd_safe('Stratagems'):
            if 'boarding actions' in (r.get('type') or '').lower():
                continue
            raw = re.sub(r'<br\s*/?>', '\n', r.get('description') or '')
            tgt = re.search(r'TARGET:(.*?)(?:EFFECT:|$)', re.sub(r'<(?!/?span)[^>]+>', ' ', raw), re.S)
            need = sorted({k for k in DET_TYPE_KW if tgt and re.search(r'\b' + k + r'\b', re.sub(r'<[^>]+>', ' ', tgt[1]), re.I)})
            d = re.sub(r'<[^>]+>', ' ', raw)
            m = re.search(r'EFFECT:\s*(.*?)(?:RESTRICTIONS:|$)', d, re.S)
            e = re.sub(r'\byour unit\b', 'this unit', m[1] if m else d, flags=re.I)
            e = re.sub(r'(?:^|(?<=\. ))\s*until the end of the (?:phase|turn|battle round),\s*', '', e, flags=re.I)
            add(r.get('detachment_id') or ('core' if not r.get('faction_id') else ''), r.get('id', ''), '戰略',
                r.get('name', '').title() + ('（Challenger：分數落後才能用）' if 'challenger' in (r.get('type') or '').lower() else ''),
                r.get('cp_cost', ''), e.strip(), need)

    def sheets_named(self, name):
        """這個名字（英文或中文）對得上的所有資料卡。中文名可能對到兩個陣營的同名單位。"""
        out = []
        for en in self.zh.get(norm(name), [name]):
            n = norm(en)
            # 官方點數頁和資料卡的寫法有時差一個 s（Vyper／Vypers）；混沌泰坦在資料卡裡只有不帶 Chaos 的那張
            for cand in (n, n.rstrip('s'), n + 's', n[6:] if n.startswith('chaos ') and n.endswith('titan') else n):
                if cand in self.byname:
                    out += [s for s in self.byname[cand] if s not in out]
                    break
        return out

    def find(self, name, faction):
        c = self.sheets_named(name)
        if not c:
            return None
        return next((s for s in c if s['faction'] == faction), c[0])


def parse_kw(desc):
    """武器關鍵字 → dict。帶條件的（LETHAL HITS: NON-MONSTER/VEHICLE）存成 (值, 條件)"""
    k = {}
    for part in re.split(r',\s*', re.sub(r'<[^>]+>', '', desc or '').upper()):
        part = part.strip()
        if not part:
            continue
        cond = None
        if ':' in part:
            part, cond = [x.strip() for x in part.split(':', 1)]
        m = re.fullmatch(r'ANTI-(.+?) (\d)\+', part)
        if m:
            k.setdefault('anti', []).append((m[1], int(m[2])))
            continue
        m = re.fullmatch(r'(RAPID FIRE|SUSTAINED HITS|MELTA|BLAST|CLEAVE) ?(\S+)?', part)
        if m:
            k[m[1]] = (m[2] or '1', cond)
            continue
        k[part] = ('1', cond)
    return k


def kwmatch(cond, tkw):
    """條件 'NON-MONSTER/VEHICLE'、'MONSTER/VEHICLE'、'INFANTRY'"""
    if not cond:
        return True
    if cond.startswith('NON-'):
        return not any(x.strip() in tkw for x in cond[4:].split('/'))
    return any(x.strip() in tkw for x in cond.split('/'))


def has(w, key, tkw):
    v = w['kw'].get(key)
    return bool(v) and kwmatch(v[1], tkw)


# ---------- 一把武器打一個目標 ----------
def kw_in(k, tkw):
    return k in tkw or k.rstrip('S') in tkw


def applies(t, w, tgt, opt, s=0, aT=0):
    """這個能力標記對這次攻擊有沒有效"""
    if t['scope'] == 'ranged' and w['melee'] or t['scope'] == 'melee' and not w['melee']:
        return False
    if t['side'] == 'att':
        if t['weapon'] and t['weapon'].rstrip('s') not in w['name'].lower():
            return False
        if t.get('wkw') and t['wkw'] not in w['kw']:
            return False
        if t['tkw'] and not any(kw_in(k, tgt['kw']) for k in t['tkw']):
            return False
        if t['tkw_not'] and any(kw_in(k, tgt['kw']) for k in t['tkw_not']):
            return False
    c = t['cond']
    if c == 'charge':
        return w['melee'] and bool(opt.get('charge'))
    if c == 'half':
        return not w['melee'] and bool(opt.get('half'))
    if c == 'still':
        return bool(opt.get('still'))
    if c == 's_gt_t':
        return s > tgt['T']
    if c == 't_gt_t':
        return tgt['T'] > aT
    return True


def weapon_damage(w, tgt, opt, fx=(), aT=0, detail=False):
    """一把武器（一個模型拿的一把）對目標造成的期望傷數（已考慮保護、FNP、傷害不溢出、勾選的能力）"""
    tkw, ranged = tgt['kw'], not w['melee']
    kw = w['kw']
    am = dict(hit=0, wound=0, ap=0, dmg=0, attacks=0, strength=0, rr_hit=None, rr_wound=None, crit_hit=6, crit_wound=6, ign=0, mw=0, rr1=0, skill=0, tgt_t=0,
              crit_ap=0, rr_dmg=None, rr1d=0, mw_pm=0, mw_cap=0)
    for t in fx:
        if applies(t, w, tgt, opt, 0, aT):
            for k, v in t['effs']:
                if k == 'kw':
                    kw = dict(kw)
                    for kk, vv in parse_kw(v).items():
                        kw[kk] = kw.get(kk, []) + vv if kk == 'anti' else vv
                elif k in ('rr_hit', 'rr_wound', 'rr_dmg'):
                    am[k] = 'all' if 'all' in (v, am[k]) else '1'
                elif k in ('crit_hit', 'crit_wound'):
                    am[k] = min(am[k], v)
                else:
                    am[k] += v
    s = mean(w['S']) + am['strength']
    dm = dict(hit=0, wound=0, ap=0, dmg=0, half=False, cover=False, inv=tgt['inv'], fnp=tgt['fnp'], sv=0, sv3=0)
    for t in tgt.get('dfx', ()):
        if applies(t, w, tgt, opt, s):
            for k, v in t['effs']:
                if k in ('inv', 'fnp'):
                    dm[k] = min(dm[k] or 7, v)
                elif k in ('half', 'cover'):
                    dm[k] = True
                elif k in dm:
                    dm[k] += v
    has = lambda key: bool(kw.get(key)) and kwmatch(kw[key][1], tkw)
    half = ranged and opt.get('half')
    a = mean(w['A']) + am['attacks']
    per5 = tgt['models'] // 5
    if 'BLAST' in kw:
        a += mean(kw['BLAST'][0]) * per5
    if 'CLEAVE' in kw:
        a += mean(kw['CLEAVE'][0]) * per5
    if half and 'RAPID FIRE' in kw:
        a += mean(kw['RAPID FIRE'][0])
    # 命中
    sk = num(w['skill'])
    if sk and am['skill']:                             # 「BS／WS 提升 1」是改數值，不是命中修正（不受 ±1 上限）
        sk = max(2, sk - am['skill'])
    qe_h = 0.0                                          # 一顆命中骰「失敗而且還沒被重骰過」的機率（給「重骰一顆」用；核心 01.05.02：同一顆不能重骰兩次）
    if 'TORRENT' in kw or not sk:
        crit_h, norm_h = 0.0, a
    else:
        mod = am['hit'] + dm['hit']
        if ranged and (opt.get('cover') or tgt['stealth'] or dm['cover']) and 'IGNORES COVER' not in kw and not am['ign']:
            sk += 1          # 第十一版：掩體讓攻擊方的 BS 變差 1
        if ranged and opt.get('still') and 'HEAVY' in kw:
            mod += 1
        mod = max(0 if am['ign'] else -1, min(1, mod))
        ch = am['crit_hit']
        p_c = (7 - ch) / 6
        p_n = sum(1 for r in range(2, ch) if r + mod >= sk) / 6
        f = 1 + (1 - p_c - p_n) if am['rr_hit'] == 'all' else 1 + 1 / 6 if am['rr_hit'] == '1' else 1
        qe_h = 0.0 if am['rr_hit'] == 'all' else max(0.0, 1 - p_c - p_n - (1 / 6 if am['rr_hit'] == '1' else 0))
        crit_h, norm_h = a * p_c * f, a * p_n * f
    sus = mean(kw['SUSTAINED HITS'][0]) if has('SUSTAINED HITS') else 0
    lethal = has('LETHAL HITS')
    to_wound = norm_h + crit_h * sus + (0 if lethal else crit_h)
    auto_w = crit_h if lethal else 0
    # 造傷
    t = max(1, tgt['T'] - am['tgt_t'])                # tgt_t：目標 T 降低（例：死亡守衛 Nurgle’s Gift 被感染的敵人 T−1）
    thr = 2 if s >= 2 * t else 3 if s > t else 4 if s == t else 6 if s * 2 <= t else 5
    wmod = (1 if (w['melee'] and opt.get('charge') and 'LANCE' in kw) else 0) + am['wound'] + dm['wound']
    wmod = max(0 if am['ign'] else -1, min(1, wmod))
    crit_y = min([y for x, y in kw.get('anti', []) if kwmatch(x, tkw)] + [6, am['crit_wound']])
    p_crit = (7 - crit_y) / 6
    p_norm = sum(1 for r in range(2, crit_y) if r + wmod >= thr) / 6
    rr = 'all' if 'TWIN-LINKED' in kw else am['rr_wound']
    f = 2 - p_crit - p_norm if rr == 'all' else 1 + 1 / 6 if rr == '1' else 1
    qe_w = 0.0 if rr == 'all' else max(0.0, 1 - p_crit - p_norm - (1 / 6 if rr == '1' else 0))
    p_crit, p_norm = p_crit * f, p_norm * f
    crit_w, norm_w = to_wound * p_crit, to_wound * p_norm + auto_w
    mortal = 0.0
    if has('DEVASTATING WOUNDS'):
        mortal = crit_w
    else:
        norm_w += crit_w
    # 保護
    sv = tgt['Sv']
    if dm['sv']:                                         # 「保護提升 1」：改 Sv 數值
        sv = max(2, sv - dm['sv'])
    if dm['sv3']:                                        # 同上，但最多到 3+（例如星界軍的 Take Cover!）
        sv = max(min(sv, 3), sv - dm['sv3'])
    need = sv + max(0, abs(num(w['AP'])) + am['ap'] + dm['ap'])
    if dm['inv']:
        need = min(need, dm['inv'])
    p_fail = min(1.0, max(1 / 6, (need - 1) / 6))
    # 「爆擊造傷時 AP 再好 1」（2026-11-17）：爆擊造傷那幾發用更好的 AP 擲保護，多打穿的部分另外算（DEVASTATING 已經不用擲保護就不算）
    crit_x = 0.0
    if am['crit_ap'] and not has('DEVASTATING WOUNDS'):
        need_c = sv + max(0, abs(num(w['AP'])) + am['ap'] + am['crit_ap'] + dm['ap'])
        if dm['inv']:
            need_c = min(need_c, dm['inv'])
        crit_x = crit_w * max(0.0, min(1.0, max(1 / 6, (need_c - 1) / 6)) - p_fail)
    bonus = (int(mean(kw['MELTA'][0])) if (half and 'MELTA' in kw) else 0) + am['dmg']
    rrd = am['rr_dmg'] or ''
    ev = norm_w * p_fail + mortal + crit_x             # 平均幾發沒擋住（含 DEVASTATING 的致命傷，一樣不溢傷）
    exp = ev * eff_damage(w['D'], bonus, tgt['W'], dm['fnp'], -dm['dmg'], dm['half'], rrd)
    if detail == 'rr1':                                 # 給「重骰一顆」用：每次攻擊的命中率、每次攻擊要骰幾顆造傷、每顆造傷成功率
        return exp, a, (crit_h + norm_h) / a if a else 0, to_wound / a if a else 0, p_crit + p_norm, qe_h, qe_w
    if detail == 'sv':                                  # 給 05.04「保護骰從小到大分配」用：要擲幾顆保護骰、致命傷幾發、幾點以下擋不住
        return norm_w, mortal + crit_x, min(7, max(2, need)), a, lost_dist(w['D'], bonus, dm['fnp'], -dm['dmg'], dm['half'], rrd)
    if detail:
        return exp, ev, a, lost_dist(w['D'], bonus, dm['fnp'], -dm['dmg'], dm['half'], rrd)
    return exp


def pool_shots(w, tgt, opt, fx, aT, cnt, keys, scale=1.0):
    """核心規則 05.04（第十一版）：同一批相同的攻擊，保護骰一起擲，防守方從最小的點數開始一顆一顆分給目前接傷的模型。
    所以小點數（誰都擋不住的）先落在前面的模型上，後面的角色拿到的是大點數。
    回傳 [(發數, {保護: 每發打穿機率})…]：先是「每一組都擋不住」的點數（含 DEVASTATING 的致命傷），
    再來是「有的組擋得住、有的擋不住」的點數，一個點數一段、由小到大。每一組的總打穿數跟原本一樣。
    近似：每一段當成獨立的 n 次嘗試（沒算同一批骰子之間的負相關）。所有組保護一樣時，跟原本的算法完全相同。"""
    info = {k: weapon_damage(w, dict(tgt, Sv=k[0], inv=k[1]), opt, fx, aT, detail='sv') for k in keys}
    nsave, _, _, a, kd = next(iter(info.values()))
    nsave = nsave * cnt * scale
    mort = {k: v[1] * cnt * scale for k, v in info.items()}      # 每種保護各自的「一定打穿」：致命傷＋爆擊造傷多的 AP 多打穿的（2026-11-17）
    need = {k: v[2] for k, v in info.items()}
    ev = {k: mort[k] + nsave * (need[k] - 1) / 6 for k in keys}
    top = max(ev.values()) if ev else 0
    if top <= 0:
        return [], kd, a
    trials = max(a * cnt * scale, top)
    lo, hi = min(need.values()), max(need.values())
    subs = [(trials, {k: (mort[k] + nsave * (lo - 1) / 6) / trials for k in keys})]
    for v in range(lo, hi):
        subs.append((trials, {k: (nsave / 6 / trials if need[k] > v else 0.0) for k in keys}))
    return subs, kd, a


def alloc_orders(body, lead, cap=48):
    """防守方可以宣告的接傷順序（05.03：非 CHARACTER 的組先、CHARACTER 的組後，兩邊各自的順序防守方自己挑）。
    保護骰從小到大分配（05.04）之後，角色之間誰排後面也有差，所以角色的順序也要試。組合太多時角色只試三種排法（原順序、保護好的排後面、保護好的排前面）；非角色的順序照舊全部試。"""
    bp = list(itertools.permutations(body)) if body else [()]
    lp = list(itertools.permutations(lead)) if lead else [()]
    if len(bp) * len(lp) > cap:
        sv = lambda k: min(k[1], k[2] or 7)                 # 越後面拿到的骰子越大：保護好的排後面通常最划算
        lp = list(dict.fromkeys([tuple(lead), tuple(sorted(lead, key=lambda k: -sv(k))), tuple(sorted(lead, key=sv))]))
    return [list(b) + list(l) for b in bp for l in lp]


def merge_pools(pools):
    """同一種攻擊（每發機率、傷害分布都一樣）不管來自哪幾個模型、拆成幾份，都是同一批一起擲保護骰（05.04）：發數加在一起。
    pools：[(subs, kd, …其他)]，回傳同樣格式（其他欄位取第一個）。"""
    out, idx = [], {}
    for pl in pools:
        subs, kd = pl[0], pl[1]
        key = (tuple(tuple(sorted((k, round(v, 9)) for k, v in q.items())) for tr, q in subs), tuple(sorted((k, round(v, 9)) for k, v in kd.items())))
        if key in idx:
            o = out[idx[key]]
            o[0] = [(t0 + t1, q) for (t0, q), (t1, _) in zip(o[0], subs)]
        else:
            idx[key] = len(out)
            out.append([list(subs)] + list(pl[1:]))
    return [tuple(o) for o in out]


def rr1_equiv(w, tgt, opt, fx, aT, cnt):
    """「重骰一顆命中、一顆造傷」等於多幾次攻擊（2026-11-15 使用者要求重骰算準一點）：
    重骰命中的收穫＝至少有一顆沒中的機率 × 一次攻擊的平均傷害；
    重骰造傷的收穫＝至少有一顆沒造傷的機率 × 一顆造傷骰的平均傷害（換算成攻擊數）。
    回傳 (相當於多幾次攻擊, 一次攻擊的平均傷害)"""
    exp, a, ph, wr, pw, qe_h, qe_w = weapon_damage(w, tgt, opt, fx, aT, detail='rr1')
    n = a * cnt
    if n <= 0 or exp <= 0:
        return 0.0, 0.0
    m = wr * n                                           # 要骰的造傷骰數（Lethal 自動成功的不用骰）
    # 2026-11-16 使用者問「帝皇偉力和圖拉真光環的重投能不能生效」：同一顆骰子不能重骰兩次（核心 01.05.02），
    # 所以只有「失敗、而且沒被別的規則重骰過」的骰子能用這次重骰（例：有重骰 1 時，命中 2+ 的失敗全是重骰過的 1 → 沒得用）
    eq = 1 - (1 - qe_h) ** n                             # 至少一顆能重骰的沒中
    if m > 0:
        eq += (1 - (1 - qe_w) ** m) * n / m              # 至少一顆能重骰的沒造傷
    return eq, exp * cnt / n


def dmg_rr_gain(w, tgt, opt, fx, aT, cnt):
    """「重骰一顆傷害骰」（Prime Target、Armoured Wrath、Warpfire Infusion…，2026-11-17）：
    這一輪至少一發沒擋住的機率 × 重骰一次平均多掉的血（骰到比平均低才重骰）。回傳多幾傷。"""
    exp, ev, a, kd = weapon_damage(w, tgt, opt, fx, aT, detail=True)
    if ev <= 0 or cnt <= 0:
        return 0.0
    t = dict(name='_rr1d', side='att', scope='all', effs=[('rr_dmg', 'all')], tkw=[], tkw_not=[], weapon=None, cond=None)
    gain = (weapon_damage(w, tgt, opt, list(fx) + [t], aT) - exp) / ev
    return (1 - math.exp(-ev * cnt)) * gain


def tag_mw(t, nmodels):
    """一個標記「另外造成的致命傷」：固定的 ('mw', x) ＋ 每個模型擲骰的 ('mw_pm', p)（上限 ('mw_cap', n)，例：衝鋒後每個模型 4+ 一點、最多 6 點）"""
    x = sum(v for k, v in t['effs'] if k == 'mw')
    pm = sum(v for k, v in t['effs'] if k == 'mw_pm')
    cap = max([v for k, v in t['effs'] if k == 'mw_cap'] or [0])
    if pm:
        x += min(cap or 1e9, pm * nmodels)
    return x


def ppw_of(u):
    """這隊最便宜的每點傷值幾分（致命傷照接傷順序，護衛先扛）"""
    gs = u.get('groups') or []
    return min((g.get('pts_each', 0) / max(1, g['model']['W']) for g in gs), default=0.0)


def chg_mw(tgt, att):
    """att 衝鋒進 tgt 時，tgt 的防守規則讓 att 吃幾點致命傷（2026-11-17：Minefield、Warpflame Gargoyles…）。已扣 att 的 FNP。
    ('mw_chg', x)：固定平均 x 點；('mw_chg_pm', p)：衝鋒那隊每個模型 p 點（上限 ('mw_cap', n)）"""
    x = pm = cap = 0
    for t in tgt.get('dfx', ()):
        if t['side'] != 'def' or t['scope'] == 'ranged':
            continue
        for k, v in t['effs']:
            if k == 'mw_chg':
                x += v
            elif k == 'mw_chg_pm':
                pm += v
            elif k == 'mw_cap':
                cap = max(cap, v)
    if pm:
        x += min(cap or 1e9, pm * sum(g['count'] for g in att['groups']))
    f = att.get('fnp') or 0
    return x * (f - 1) / 6 if f else x


def unit_damage(att, tgt, melee, opt, hi=False, info=None):
    """整個單位打一輪（射擊或近戰）對目標的期望傷數。有「二選一」的規則（pick）時，每個選法都算一次取最好的。
    info（dict）：填 haz＝這輪開了幾把 [HAZARDOUS] 武器（2026-11-16 對戰總表也算危險武器自傷）"""
    sc = 'melee' if melee else 'ranged'
    picks = {}
    for g in att['groups']:
        for t in g.get('fx', ()):
            if t.get('pick') and t['scope'] in ('all', sc) and t['name'] not in picks.setdefault(t['pick'], []):
                picks[t['pick']].append(t['name'])
    if not picks:
        return _unit_damage(att, tgt, melee, opt, {}, hi, info)
    ks = sorted(picks)
    combos = [{}]
    for k in ks:
        combos = [dict(c, **{k: n}) for c in combos for n in picks[k]]
    best = None
    for c in combos:
        inf = {}
        v = _unit_damage(att, tgt, melee, opt, c, hi, inf)
        if best is None or v > best[0]:
            best = (v, inf)
    if info is not None:
        info.update(best[1])
    return best[0]


def _unit_damage(att, tgt, melee, opt, chosen, hi=False, info=None):
    total, extra, used = 0.0, 0.0, []
    sc = 'melee' if melee else 'ranged'
    # 危險武器的代價換算成目標的傷數（每把一次危險骰的平均損失分數 ÷ 目標每點傷值幾分）；挑模式時扣掉
    hw = haz_pts(att) / max(1e-9, tgt.get('points', 0) / max(1, tgt['wounds'])) if tgt.get('points') else 0.0
    nhaz = 0
    for g in att['groups']:
        fx = [t for t in g.get('fx', ()) if not t.get('pick') or chosen.get(t['pick']) == t['name']]
        entries = []                                   # (每把期望傷數, 幾把, 武器)
        for cnt, profs in g['weapons']:
            ps = [p for p in profs if p['melee'] == melee]
            if ps:
                best = max(ps, key=lambda p: weapon_damage(p, tgt, opt, fx, g['model']['T']) - (hw if 'HAZARDOUS' in p['kw'] else 0))
                entries.append((weapon_damage(best, tgt, opt, fx, g['model']['T']), cnt, best))
        # 「另外造成致命傷」「重骰一顆骰」：整個單位一次，不是每把武器
        mw = rr1 = rr1d = 0
        nmod = sum(gg['count'] for gg in att['groups'])
        for t in fx:
            if t['side'] != 'att' or t['scope'] not in ('all', sc):
                continue
            if t['tkw'] and not any(kw_in(k, tgt['kw']) for k in t['tkw']):
                continue
            if t['tkw_not'] and any(kw_in(k, tgt['kw']) for k in t['tkw_not']):
                continue
            if t['cond'] == 'charge' and not (melee and opt.get('charge')):
                continue
            mw += tag_mw(t, nmod)
            for k, v in t['effs']:
                rr1 += v if k == 'rr1' else 0
                rr1d += v if k == 'rr1d' else 0
        g_extra = 0.0                                  # 這組模型的「整隊一次」加成；每組都帶著整隊的標記，所以各組取最大，不相加
        if mw:
            g_extra += mw * (1 - (7 - tgt['fnp']) / 6 if tgt['fnp'] else 1)
        if (rr1 or rr1d) and entries:                  # 重骰一顆（命中／造傷／傷害骰）：用在最划算的那把武器上
            best_rr = 0.0
            for d, c, w in entries:
                v = 0.0
                if rr1:
                    eq, per = rr1_equiv(w, tgt, opt, fx, g['model']['T'], c)
                    v += rr1 / 2 * eq * per
                if rr1d:
                    v += min(1, rr1d) * dmg_rr_gain(w, tgt, opt, fx, g['model']['T'], c)
                best_rr = max(best_rr, v)
            g_extra += best_rr
        extra = max(extra, g_extra)
        if melee:
            chosen_e = [(d, c, w) for d, c, w in entries if 'EXTRA ATTACKS' in w['kw']]
            left = g['count']                          # 每個模型只用一把近戰武器：挑最好的
            for d, c, w in sorted((e for e in entries if 'EXTRA ATTACKS' not in e[2]['kw']), key=lambda e: -e[0]):
                use = min(c, left)
                if use > 0:
                    chosen_e.append((d, use, w))
                left -= use
        else:
            pistol = lambda w: 'PISTOL' in w['kw'] or 'CLOSE-QUARTERS' in w['kw']
            a = [e for e in entries if not pistol(e[2])]
            b = [e for e in entries if pistol(e[2])]
            chosen_e = a + b if g['big'] else max(a, b, key=lambda es: sum(d * c for d, c, w in es))  # 非怪獸／載具：手槍和其他槍二選一
        total += sum(d * c for d, c, w in chosen_e)
        nhaz += sum(c for d, c, w in chosen_e if 'HAZARDOUS' in w['kw'])
        used += [(w, c, fx, g['model']['T']) for d, c, w in chosen_e]
    if info is not None:
        info['haz'] = nhaz
        if melee and opt.get('charge'):
            info['chg_mw'] = chg_mw(tgt, att)          # 衝鋒進去被對方的規則咬的致命傷（2026-11-17）
    if used and needs_alloc(tgt, used, opt):
        total = alloc_best(tgt, used, opt, hi)
    return min(total + extra, tgt['wounds'])


def needs_alloc(tgt, used, opt):
    """舊算法（每發都當打在滿血模型上）不準的時候才一隻一隻扣：模型的 W 不只一種，或有傷害不能整除 W"""
    ws = {g[1] for g in tgt['wgroups']}
    if len(ws) > 1 or len({(g[3], g[4]) for g in tgt['wgroups']}) > 1:
        return True
    W = next(iter(ws))
    for w, c, fx, aT in used:
        for k in weapon_damage(w, tgt, opt, fx, aT, detail=True)[3]:
            if 0 < k < W and W % k:
                return True
    return False


def alloc_best(tgt, used, opt, hi=False):
    """攻擊方挑開火順序（D 大的先或 D 小的先），防守方挑哪種模型先接：攻擊方取最好、防守方取對自己最好。
    核心規則 05.03（第十一版）：非 CHARACTER 的組先接（受傷的組最先），CHARACTER 最後；每一組用自己的 Sv／無敵；T 用護衛裡最高的（19.02）。
    hi=True：防守方接得最差的情況（給使用者看可能的範圍）"""
    groups = {}                                         # (W, Sv, 無敵, 是不是角色) → 模型數
    for c, wv, ld, sv, inv, *_ in tgt["wgroups"]:
        k = (wv, sv, inv, ld)
        groups[k] = groups.get(k, 0) + c
    body = [k for k in groups if not k[3]]
    lead = [k for k in groups if k[3]]
    saves = sorted({(k[1], k[2]) for k in groups})
    shots = []
    for w, c, fx, aT in used:
        subs, kd, a = pool_shots(w, tgt, opt, fx, aT, c, saves)
        if subs:
            shots.append((subs, kd, sum(k * p for k, p in kd.items())))
    shots = merge_pools(shots)
    if not shots:
        return 0.0
    best = 0.0
    for att in (sorted(shots, key=lambda s: -s[2]), sorted(shots, key=lambda s: s[2])):
        res = []
        for order in alloc_orders(body, lead):
            seq = [k for k in order for _ in range(groups[k])]
            res.append(allocate([k[0] for k in seq], [(tr, [q[(k[1], k[2])] for k in seq], kd) for subs, kd, m in att for tr, q in subs]))
        best = max(best, (max if hi else min)(res))
    return best


# ---------- 讀軍表 ----------
SECTION = re.compile(r"^[A-Z][A-Z '&/-]+$")
HEAD = re.compile(r'^(.+?) ?[(（]?([\d,]+) ?(?:points?|pts|点|點)[)）]?$', re.I)  # App 設成中文時是「点」；新版 App 是「(180点)」沒空格、也有全形括號
CJK_SECTION = re.compile(r'^[一-鿿]+$')                                   # 中文版的分類標題：角色、战线、其他数据表…
ITEM = re.compile(r'^(\d+)x (.+)$')


def bl_convert(text):
    """黑圖書館（中文軍表 App）匯出的格式 → GW 官方 App 中文匯出的格式（2026-11-27）。
    差別：(115分)／(115点)、「联合单位：1」、項目符號「·」、领导／领袖、「强化：X；分数：20」、名字後的(主将)、单位组成／扩编次数 行。"""
    out, block = [], []
    def flush():
        ind = sorted({len(l) - len(l.lstrip()) for l in block if l.lstrip().startswith('·')})
        for l in block:
            s = l.lstrip()
            if s.startswith('·'):
                lv = ind.index(len(l) - len(s))
                body = re.sub(r'\s*\(\d+分\)$', '', s.lstrip('· ').strip())
                out.append('  ' * (lv + 1) + '• ' + body)
            else:
                out.append(l)
        block.clear()
    for l in text.replace('\r', '').split('\n'):
        s = l.strip()
        if re.fullmatch(r'-{3,}', s) or re.match(r'^(单位组成|單位組成|扩编次数|擴編次數)[：:]', s) or re.match(r'^(由黑图书馆|版本号|感/谢)', s):
            continue
        if re.match(r'^(进行联合的单位|進行聯合的單位)[：:]', s):
            block.append('• ' + s.replace('领导', '领袖').replace('領導', '領袖')); continue
        if re.match(r'^(强化|強化)[：:]', s):
            block.append('• ' + re.sub(r'[；;]\s*(分数|分數)[：:]\s*\d+$', '', s)); continue
        if s.startswith('·'):
            block.append(l); continue
        flush()
        m = re.fullmatch(r'(联合单位|聯合單位)[：:]\s*(\d+)', s)
        if m:
            out.append(m[1] + m[2]); continue
        m = re.fullmatch(r'(.+?)\s*(?:\((?:主将|主將|领主|Warlord)\))?\s*[(（](\d+)分[)）]', s)
        if m:
            out.append(f'{m[1]} ({m[2]}点)'); continue
        out.append(l)
    flush()
    return '\n'.join(out)


def parse_list(text, db):
    ZH_GUESSED.clear()
    if '黑图书馆' in text or '黑圖書館' in text or re.search(r'^\S.*[(（]\d+分[)）]\s*$', text, re.M):
        text = bl_convert(text)
    lines = [l.replace('\t', '    ').rstrip() for l in text.replace('\r', '').split('\n')]
    out = dict(name='', faction='', points=0, units=[], unknown=[], notes=[])
    fid = None
    for l in lines[:12]:
        if norm(l) in db.factions and not fid:
            fid, out['faction'] = db.factions[norm(l)], l.strip()
    m = HEAD.match(lines[0].strip()) if lines else None
    declared, skipped = 0, []                            # 表頭寫的總分；看起來像單位、但沒當單位讀的行（2026-11-16 讀不到的單位跳警告）
    if m:
        out['name'] = m[1]
        declared = int(m[2].replace(',', ''))
    if not fid:                                          # 表頭的陣營名不是英文（App 設成中文）：看單位名最多屬於哪個陣營
        votes = {}
        for l in lines[1:]:
            mh = HEAD.match(l.strip()) if l[:1] not in ' \t•◦' else None
            for sh in (db.sheets_named(mh[1]) if mh else []):
                votes[sh['faction']] = votes.get(sh['faction'], 0) + 1
        if votes:
            fid = max(votes, key=votes.get)
            out['faction'] = db.faction_names.get(fid, fid)
    raw, cur, attach, attach_id, started = [], None, None, 0, False
    for i, l in enumerate(lines):
        st = l.strip()
        if not st:
            continue
        ind = len(l) - len(l.lstrip())
        if ind == 0 and st[0] not in '•◦':
            ma = re.fullmatch(r'(?:Attached Unit|联合单位|聯合單位) ?(\d+)', st, re.I)
            if ma:
                started = True
                attach_id += 1
                attach = attach_id
                cur = None
                continue
            if SECTION.match(st) or CJK_SECTION.match(st):
                started = started or i > 2
                attach, cur = None, None
                continue
            m = HEAD.match(st)
            if m and i > 0:
                sheet = db.find(m[1], fid)
                if not sheet and int(m[2].replace(',', '')) not in (500, 1000, 2000, 3000) and (re.search(r'[A-Za-z]', m[1]) or started) and not re.match(r'(strike force|incursion|onslaught|combat patrol)', m[1], re.I):
                    near = difflib.get_close_matches(norm(m[1]), db.allnames, 1, 0.88)
                    sheet = db.find(near[0], fid) if near else None
                    if not sheet and CJK.search(m[1]):          # 中文譯名差一兩個字（荒蝎驱逐者／荒蝎毁灭者）：同陣營裡找最像的中文名
                        zk = [k for k, v in db.zh.items() if any(s['faction'] == fid for s in db.sheets_named(k))]
                        pts = int(m[2].replace(',', ''))
                        near = [k for k in difflib.get_close_matches(norm(m[1]), zk, 5, 0.5)
                                if any(c == pts for s in db.sheets_named(k) if s['faction'] == fid for d, c in s['costs'])]   # 分數也要對得上才算
                        sheet = db.find(near[0], fid) if near else None
                        if sheet:
                            out['notes'].append(f'「{m[1]}」照名字相近＋分數對得上，當成「{sheet["name"]}」（請確認）')
                    if sheet:
                        out['notes'].append(f'「{m[1]}」資料裡沒有完全同名的，用「{sheet["name"]}」代替')
                    else:
                        out['unknown'].append(m[1])
                elif not sheet and int(m[2].replace(',', '')) not in (500, 1000, 2000, 3000):
                    skipped.append(st)
                if sheet:
                    cur = dict(sheet=sheet, name=m[1] + (f'（{sheet["name"]}）' if CJK.search(m[1]) else ''), points=int(m[2].replace(',', '')), attach=attach, role='', items=[], extra=[])
                    raw.append(cur)
                else:
                    cur = None
                continue
        if cur is None:
            continue
        if st[0] == '◦':
            ind += 50
        body = st.lstrip('•◦- ').strip()
        mi = ITEM.match(body)
        if mi:
            cur['items'].append(dict(ind=ind, bullet=st[0] in '•◦', n=int(mi[1]), name=mi[2]))
        elif body.lower().startswith('attached as:') or re.match(r'(进行联合的单位|進行聯合的單位)', body):
            lead = re.search(r'leader|support|领袖|領袖|辅助|輔助', body.lower())
            cur['role'] = 'leader' if lead else 'bodyguard'
        elif re.match(r'(enhancement|强化|強化)', body.lower()):
            cur['extra'].append(body)
    out['fid'] = fid
    low = norm(text)
    zdet = {norm(en) for zh, en in db.zh_det.items() if norm(zh) in low}          # 中文軍表的分隊名
    out['det_auto'] = [d['id'] for d in db.dets.get(fid, []) if norm(d['name']) in low or norm(d['name']) in zdet]
    built = [build_unit(u, db, out) for u in raw]
    # 合併領袖和護衛
    done = set()
    for u in built:
        if id(u) in done:
            continue
        if u['attach']:
            mates = [x for x in built if x['attach'] == u['attach']]
            done.update(id(x) for x in mates)
            out['units'].append(merge(mates) if len(mates) > 1 else u)
        else:
            out['units'].append(u)
    present = {norm(n) for u in out['units'] for n in u['body'] | u['leaders']}
    for gr in manual.GRANTS:
        if norm(gr['src']) not in present:
            continue
        for u in out['units']:
            mine = norm(gr['src']) in {norm(n) for n in u['body'] | u['leaders']}
            if all(k in u['kw'] for k in gr['need']) and not any(k in u['kw'] for k in gr['excl']) and not (mine and gr['src'] in manual.MANUAL):
                u['tags'].append(dict(gr['tag'], src=gr['src'], granted=True))
    out['points'] = sum(u['points'] for u in out['units'])
    out['warn'] = []
    if declared and out['units'] and declared != out['points']:
        out['warn'].append(f'軍表表頭寫 {declared} 分，讀到的單位加起來 {out["points"]} 分，差 {declared - out["points"]} 分：可能有單位沒讀到或分數讀錯'
                           + (f'（這幾行沒當成單位：{"、".join(skipped)}）' if skipped else ''))
    for u in out['units']:
        dry = [g['name'] for g in u['groups'] if not g['weapons'] and g['count']]
        if dry and not (u['kw'] & {'FORTIFICATION'}):
            out['warn'].append(f'{u["name"]}：{"、".join(dry)} 讀不到任何武器，這些模型不會出手')
    return out


DET_TYPE_KW = ('INFANTRY', 'VEHICLE', 'MONSTER', 'MOUNTED', 'CHARACTER', 'WALKER', 'TERMINATOR', 'BATTLELINE', 'BEAST', 'SWARM', 'FLY', 'PSYKER', 'TITANIC')
ZH_UNKNOWN = set()
ZH_GUESSED = set()                                       # (資料卡, 中文, 英文)：拆字推測的
ZH_WARGEAR = {}                                          # DB() 載入時填
COMM_WEAP = {}                                           # 英文資料卡名 → {社群中文武器名: 英文}（zh_comm.json，DB() 載入時填）
_MORPH = sorted(getattr(zh_glossary, 'MORPH', {}).items(), key=lambda kv: -len(kv[0]))


def zh_guess(name, cands):
    """中文名拆成字詞 → 跟 cands（英文名清單）比，回傳明顯最像的一個，沒把握就 None。"""
    rest, parts, generic = name, [], 0
    for zh, en in _MORPH:
        if zh in rest:
            parts.append(en.split('/')); rest = rest.replace(zh, '｜')
            generic += zh in ('炮', '枪', '武器')
    left = len(re.sub(r'[｜·\s]', '', rest))            # 拆不出來的中文字數（專有名詞）
    if not parts or generic == len(parts):              # 只拆出「炮」「枪」這種太籠統的字，不猜
        return None
    scored = []
    for c in cands:
        flat = re.sub(r'[^a-z]', '', c.lower()); words = [w for w in re.split(r'[^a-z]+', c.lower()) if w]
        hit = sum(any(e.replace(' ', '') in flat for e in alts) for alts in parts)
        pw = [x for alts in parts for e in alts if e.replace(' ', '') in flat for x in e.split()]
        covered = [w for w in words if any(w.startswith(e[:4]) or e.startswith(w[:4]) for e in pw)]
        cover = sum(map(len, covered)) / max(1, len(flat))
        if len(covered) < len(words):                   # 英文有中文沒講到的字：多半是別把武器（爆矢枪≠Inferno boltgun、干扰炮≠splinter cannon）
            continue
        scored.append((hit - 0.5 * (len(parts) - hit) + cover - 0.15 * left, c, hit))
    if not scored:
        return None
    scored.sort(reverse=True)
    best = scored[0]
    if best[2] < len(parts) or (len(scored) > 1 and best[0] - scored[1][0] < 0.25):
        return None
    return best[1]


def match_weapon(name, sheet):
    if CJK.search(name):
        cw = COMM_WEAP.get(sheet['name'], {})
        key = re.sub(r'\s+', '', name)
        near = cw.get(key) or next(iter(difflib.get_close_matches(key, list(cw), 1, 0.6)), None)
        if near and not cw.get(key) and not COMM_WEAP.get('', {}).get(key):
            ZH_GUESSED.add((sheet['name'], name.strip(), cw[near]))
        comm = cw.get(key) or COMM_WEAP.get('', {}).get(key) or (cw[near] if near else None)
        ens = [e for e in (comm, zh_glossary.WEAPONS.get(name.strip()), ZH_WARGEAR.get(name.strip())) if e]
        ens = [e for e in COMM_WEAP.get('*', {}).get(key, []) if e not in ens] + ens
        if not ens:
            names = {}
            for w in sheet['weapons']:
                names.setdefault(re.sub(r'\s*[-–]\s.*$', '', w['name']).strip(), w['base'])
            g = zh_guess(name.strip(), list(names))
            if not g:
                ZH_UNKNOWN.add((sheet['name'], name.strip()))
                return None
            ZH_GUESSED.add((sheet['name'], name.strip(), g))
            ens = [g]
        for en in ens[:-1]:                              # 同一個中文名在不同單位可能是不同武器（导弹发射器）：先試對得到這張資料卡的
            hit = match_weapon(en, sheet)
            if hit:
                return hit
        name = ens[-1]
    n = norm(name)
    bases = {}
    for w in sheet['weapons']:
        bases.setdefault(w['base'], []).append(w)
    for cand in (n, n.rstrip('s'), n + 's'):
        if cand in bases:
            return bases[cand]
    near = difflib.get_close_matches(n, list(bases), 1, 0.86)
    return bases[near[0]] if near else None


def match_model(name, sheet):
    if CJK.search(name):
        name = getattr(zh_glossary, 'MODELS', {}).get(name.strip(), name)
    n = norm(name).rstrip('s')
    for m in sheet['models']:                            # 先找完全同名（Scout 和 Scout Sergeant 要分得開）
        if norm(m['name']).rstrip('s') == n:
            return m
    for m in sheet['models']:
        mn = norm(m['name']).rstrip('s')
        if mn in n or n in mn:
            return m
    return None


def split_combo(name):
    """'2 Lascannons and 2 Twin Heavy Bolters' → [(2, 'Lascannons'), (2, 'Twin Heavy Bolters')]"""
    out = []
    for part in re.split(r'\s+and\s+', name):
        m = re.match(r'(\d+)\s+(.+)', part.strip())
        out.append((int(m[1]), m[2]) if m else (1, part.strip()))
    return out


def loadout_items(sheet, gname, strict=False):
    """資料卡的預設配備：挑主詞對得上這組模型的那句，回傳 [(數量, 武器各型態)]。
    strict=True（補「軍表沒列的固定武器」用）：只用主詞對得上、或「This model／Every model」的那句，不亂套別的模型的配備。"""
    # 2026-11-16：主詞也可能是名字（Ibram Gaunt is equipped with）、Each model、A Medusae、1 Tanith Ghost；句點後常少空格、最後一句常沒句點
    lo = re.sub(r'\.(?=[A-Z0-9])', '. ', (sheet['loadout'] or '').strip())
    lo = lo if lo.endswith('.') else lo + '.'
    sents = re.findall(r'(?:^|(?<=\. ))([^.:]+?) (?:is|are) equipped with: ([^.]*)\.', lo)
    if not sents:
        return []
    subj = lambda x: re.sub(r'^(?:every|each|the|an?|\d+) ', '', norm(x)).rstrip('s')
    g = norm(gname).rstrip('s')
    pick = next((x for x in sents if subj(x[0]) == g), None)
    pick = pick or next((x for x in sents if subj(x[0]) in ('this model', 'model')), None) or (None if strict else sents[-1])
    if not pick:
        return []
    res = []
    for part in pick[1].split(';'):
        for n, nm in split_combo(part.strip()):
            profs = match_weapon(nm, sheet)
            if profs:
                res.append((n, nm, profs))
    return res


def build_unit(u, db, out):
    sheet, items = u['sheet'], u['items']
    groups, cur, ignored, added = [], None, [], []
    top = min((it['ind'] for it in items if it['bullet']), default=0)
    nested = any(it['ind'] > top and it['bullet'] for it in items)

    def weapons_of(it):
        profs = match_weapon(it['name'], sheet)
        if profs:
            return [(it['n'], profs)]
        parts = [(n, match_weapon(nm, sheet)) for n, nm in split_combo(it['name'])]
        return [(it['n'] * n, p) for n, p in parts] if len(parts) > 1 and all(p for n, p in parts) else None

    for i, it in enumerate(items):
        ws = weapons_of(it)
        child = i + 1 < len(items) and items[i + 1]['ind'] > it['ind'] and items[i + 1]['bullet']
        is_model = it['bullet'] and (child or (not ws and (match_model(it['name'], sheet) or (nested and it['ind'] == top) or (not nested and i + 1 < len(items) and weapons_of(items[i + 1])))))
        if is_model:
            cur = dict(count=it['n'], name=it['name'], model=match_model(it['name'], sheet), weapons=[])
            groups.append(cur)
        elif ws:
            if cur is None:
                cur = dict(count=0, name=sheet['name'], model=None, weapons=[])
                groups.append(cur)
            cur['weapons'] += ws
        else:
            ignored.append(it['name'])
    if not groups:
        groups = [dict(count=0, name=sheet['name'], model=None, weapons=[])]
    big = bool(sheet['kw'] & {'MONSTER', 'VEHICLE'})
    for g in groups:
        if not g['count']:                               # 沒列模型數：用點數反查，查不到當 1 個
            n = [num(d) for d, c in sheet['costs'] if c == u['points'] and re.search(r'\d+ model', d)]
            g['count'] = n[0] if n else 1
        g['model'] = g['model'] or (sheet['models'][0] if sheet['models'] else dict(name='?', M=0, T=4, Sv=7, inv=0, W=1, OC=0))
        g['big'] = big
        g['src'] = sheet['name']
    nmod = sum(g['count'] for g in groups) or 1
    for g in groups:
        g['pts_each'] = u['points'] / nmod                 # 每隻模型值幾分（領袖和護衛分開算，2026-11-15）
    single = len(groups) == 1 and groups[0]['count'] == 1
    for g in groups:
        have = {id(p) for c, p in g['weapons']} | {p[0]['base'] for c, p in g['weapons']}
        if not g['weapons']:                             # 這組模型沒列武器：用資料卡的預設配備
            for n, nm, profs in loadout_items(sheet, g['name']):
                g['weapons'].append((n * g['count'], profs))
                added.append(nm)
            if not g['weapons'] and single and CJK.search(u['name']) and sheet['weapons']:   # 中文軍表的武器名都對不上、預設配備也讀不到：資料卡上的武器全部算（2026-11-27 黑圖書館）
                bases = {}
                for w in sheet['weapons']:
                    bases.setdefault(w['base'], []).append(w)
                for b, profs in bases.items():
                    g['weapons'].append((1, profs))
                out['notes'].append(f'{u["name"]}：武器名都對不上，資料卡上的武器全部算上（{", ".join(p[0]["name"] for p in bases.values())}；有選配的話可能多算）')
        else:                                            # 補上軍表沒列、又不能換掉的固定武器（App 匯出常省略 close combat weapon、坐騎的蹄子等）
            for n, nm, profs in loadout_items(sheet, g['name'], strict=not single):   # 2026-11-16 跟 Kill Grid 對照時發現：卡迪安突擊兵、Tempestus Aquilons 近戰少算
                b = profs[0]['base']
                if b not in have and not re.search(re.escape(b) + r's?(?:(?! with ).){0,25}replaced', sheet['options']):
                    g['weapons'].append((n * (1 if single else g['count']), profs))
                    added.append(nm)
    gear_ab = {norm(a['name']): a['name'] for a in sheet['abil_all'] if a.get('type') == 'Wargear'}
    gear = []                                            # 盾、旗這類「裝備能力」：資料卡上的能力已經照能力算（或不影響傷害），不算「沒讀到」
    for nm in sorted(set(ignored)):
        en = getattr(zh_glossary, 'GEAR', {}).get(nm.strip(), nm)
        if norm(en) in gear_ab:
            gear.append(nm if en == nm else f'{nm}＝{gear_ab[norm(en)]}')
            ignored = [x for x in ignored if x != nm]
    if gear:
        out['notes'].append(f'{u["name"]}：裝備 {"、".join(gear)} 是資料卡上的裝備能力，照能力算（不影響傷害的就不算）')
    if ignored:
        out['notes'].append(f'{u["name"]}：沒算進去的裝備 {", ".join(sorted(set(ignored)))}')
    zhmiss = sorted({n for sn, n in ZH_UNKNOWN if sn == sheet['name']} & set(ignored))
    if zhmiss:
        out['notes'].append(f'{u["name"]}：這些中文武器名還沒有英文對照，沒算或改用預設武器 {"、".join(zhmiss)}')
        try:
            with open(os.path.join(os.path.dirname(DATA), 'unknown_zh.txt'), 'a', encoding='utf-8') as f:
                for n in zhmiss:
                    f.write(f'{sheet["name"]}\t{n}\n')
        except OSError:
            pass
    guessed = sorted((zh, en) for sn, zh, en in ZH_GUESSED if sn == sheet['name'])
    if guessed:
        out['notes'].append(f'{u["name"]}：中文武器名用拆字推測對照（請確認） ' + '、'.join(f'{zh}＝{en}' for zh, en in guessed))
    if added:
        out['notes'].append(f'{u["name"]}：軍表沒列、照資料卡預設補上 {", ".join(sorted(set(added)))}')
    main = max(groups, key=lambda g: g['count'])['model']
    return dict(name=u['name'], points=u['points'], attach=u['attach'], role=u['role'], groups=groups, kw=set(sheet['kw']),
                fnp=sheet['fnp'], stealth=sheet['stealth'], extra=u['extra'], main=main, fab=set(sheet['fab']), info=[dict(src=sheet['name'], abil=sheet['abil_all'])],
                tags=[dict(t, src=sheet['name']) for t in sheet['tags'] + enh_tags(u, sheet, db, out)], body={sheet['name']}, leaders=set())


def enh_tags(u, sheet, db, out):
    """軍表上寫的強化（Enhancement／强化）→ 標記。先看 army.ENH 手動的，沒有就用 tags.py 讀 Wahapedia 原文。"""
    res = []
    for e in u['extra']:
        k = enh_key(e)
        en = db.zh_enh.get(k, k)
        rows = db.enh.get(enh_key(en), [])
        row = next((r for r in rows if r['faction'] == sheet['faction']), rows[0] if rows else None)
        if not row:
            out['notes'].append(f'{u["name"]}：強化「{e}」資料裡找不到，沒算')
            continue
        nm = re.sub(r'\s*\(one per army\)', '', row['name'], flags=re.I)
        ts = army.ENH.get(nm) or tagger.tag_ability(nm, row['desc'])
        if ts:
            res += [dict(t, name='強化 ' + nm) for t in ts]
        else:
            out['notes'].append(f'{u["name"]}：強化 {nm} 沒有會影響傷害的效果（或讀不懂），沒算')
    return res


def merge(mates):
    body = [m for m in mates if m['role'] != 'leader'] or mates[-1:]
    lead = [m for m in mates if m not in body]
    b = body[0]
    return dict(name=' + '.join(m['name'] for m in lead + body), points=sum(m['points'] for m in mates), attach=b['attach'], role='',
                groups=[g for m in body + lead for g in m['groups']], kw=set().union(*(m['kw'] for m in mates)),
                fnp=b['fnp'], stealth=all(m['stealth'] for m in mates), extra=[e for m in mates for e in m['extra']], main=b['main'],
                fab=set().union(*(m['fab'] for m in mates)), info=[i for m in body + lead for i in m['info']],
                tags=[t for m in body + lead for t in m['tags']], body={n for m in body for n in m['body']}, leaders={n for m in lead for n in m['body']})


def tag_key(t):
    return f"{t['src']}|{t['name']}|{t['side']}|{t['label']}"


def resolve(lst, over):
    """照預設和使用者的勾選，決定每個單位哪些能力有算。over = {'單位序號|key': True/False}"""
    for i, u in enumerate(lst['units']):
        act, seen, u['abil'] = [], set(), []
        for t in u['tags']:
            k = tag_key(t)
            if k in seen:
                continue
            seen.add(k)
            why = ''
            if t['leading'] and t['src'] not in u['leaders']:
                why = '要帶隊才有'
            elif t['side'] == 'def' and not (t['leading'] or t.get('unitwide') or t.get('granted') or t['src'] in u['body']):
                why = '只保護領袖自己，併隊後不算'
            avail = not why
            on = bool(over.get(f'{i}|{k}', t['on'])) and avail
            u['abil'].append(dict(key=f'{i}|{k}', name=t['name'], src=t['src'], label=t['label'], on=on, avail=avail, why=why, once=bool(t.get('once'))))
            if on:
                act.append(t)
        for g in u['groups']:
            g['fx'] = [t for t in act if t['side'] == 'att' and (t['leading'] or t.get('unitwide') or t.get('granted') or t['src'] == g['src'])]
        u['dfx'] = [t for t in act if t['side'] == 'def' and (t['leading'] or t.get('unitwide') or t.get('granted') or t['src'] in u['body'])]


def _fits(u, r):
    """這個單位符不符合規則／戰略的對象限制"""
    names = {n.lower() for n in u['body'] | u['leaders']}
    if not all(n in u['kw'] for n in r.get('need', [])) or any(n in u['kw'] for n in r.get('need_not', [])):
        return False
    if r.get('names') and not any(x.lower() in n for x in r['names'] for n in names):
        return False
    if r.get('names_not') and any(x.lower() in n for x in r['names_not'] for n in {b.lower() for b in u['body']}):
        return False
    return not r.get('fab') or r['fab'] in u.get('fab', ())


def _restrict(r):
    s = []
    if r.get('need'):
        s.append('限 ' + '/'.join(r['need']))
    if r.get('names'):
        s.append('限 ' + '/'.join(r['names']))
    if r.get('need_not') or r.get('names_not'):
        s.append('不含 ' + '/'.join(r.get('need_not', []) + r.get('names_not', [])))
    if r.get('model_kw'):
        s.append('只有 ' + '/'.join(r['model_kw']) + ' 模型')
    if r.get('model_not'):
        s.append(' 不含 ' + '/'.join(r['model_not']) + ' 模型')
    return s


def apply_dets(lst, over, db):
    """軍隊規則、分隊規則和戰略。over 的 key：'D|分隊id' 選分隊（預設＝軍表裡讀到的分隊名，軍隊規則預設選）、
    'R|分隊id|規則名' 勾規則或戰略（預設照 army.py 的 on；自動讀的都不勾）。勾了的戰略當作「每個符合條件的單位都用了」。"""
    groups = []
    for abid, spec in army.ARMY.items():                 # 軍隊規則：有這個能力的單位才有
        if any(abid in u.get('fab', ()) for u in lst['units']):
            groups.append(dict(id='army' + abid, name='軍隊規則：' + spec['name'], army=True,
                               rules=[dict(r, fab=abid) for r in spec['rules']], unread=0))
    for d in db.dets.get(lst.get('fid'), []):
        box = db.det_rules.get(d['id'], dict(rules=[], unread=0, total=0))
        hand = army.DET.get(d['id'], army.DET.get(d['name']))   # rules/*.py 用分隊 id 當 key（有兩個陣營的分隊同名），army.py 的禁軍用名字
        if hand is not None:
            rules = hand
            unread = max(0, box['total'] - len(rules))
        else:
            rules = [dict(name=r['name'], kind=r['kind'], cp=r['cp'], tags=r['tags'], need=r['need'], on=False) for r in box['rules']]
            unread = box['unread']
        groups.append(dict(id=d['id'], name=d['name'], rules=rules, unread=unread, hand=hand is not None))
    core = db.det_rules.get('core', {})
    if core.get('rules'):
        groups.append(dict(id='core', name='通用戰略（Core）', rules=[dict(name=r['name'], kind=r['kind'], cp=r['cp'], tags=r['tags'], need=r['need'], on=False)
                                                               for r in core['rules']], unread=core['unread']))
    sheet_kw = lambda g: (db.byname.get(norm(g['src'])) or [dict(kw=set())])[0]['kw']
    out = []
    for d in groups:
        auto = d.get('army') or d['id'] in lst.get('det_auto', [])
        on = bool(over.get('D|' + d['id'], auto))
        if d['id'] == 'core' and not on:                 # 通用戰略沒勾也拿去算「值不值得」
            for r in d['rules']:
                lst.setdefault('_rules', []).append(dict(r, det=d['name'], on_now=False))
        item = dict(id=d['id'], name=d['name'], key='D|' + d['id'], on=on, auto=bool(auto), rules=[], unread=d['unread'], n=len(d['rules']),
                    army=bool(d.get('army')), hand=bool(d.get('hand')))
        if on:
            for r in d['rules']:
                key = f"R|{d['id']}|{r['name']}"
                ron = bool(over.get(key, r.get('on', False)))
                lab = '；'.join(t['label'] if not t.get('pick') else t['name'] + '：' + t['label'] for t in r['tags'])
                if r.get('note'):
                    lab += f'（{r["note"]}）'
                item['rules'].append(dict(key=key, kind=r['kind'], name=r['name'], cp=r['cp'], label=lab, need=_restrict(r), on=ron))
                lst.setdefault('_rules', []).append(dict(r, det=d['name'], on_now=ron, model_kw=r.get('model_kw', []), model_not=r.get('model_not', [])))
                if not ron:
                    continue
                for t in r['tags']:
                    tt = dict(t, src=r['name'], granted=True, situ=False)
                    for u in lst['units']:
                        if not _fits(u, r):
                            continue
                        if tt['side'] == 'att':
                            for g in u['groups']:
                                gk = sheet_kw(g)
                                if all(k in gk for k in r.get('model_kw', [])) and not any(k in gk for k in r.get('model_not', [])):
                                    g['fx'] = g.get('fx', []) + [tt]
                        else:
                            u['dfx'] = u.get('dfx', []) + [tt]
        out.append(item)
    lst['dets'] = out


# ---------- 每個選項值多少（2026-11-15 使用者：「給我看細節差異 例如六種武藝要不要開cp」）----------
def _variant(u, add=(), drop=(), r=None, db=None):
    """單位的複本：加上 add 這些標記、拿掉來源是 drop 的標記"""
    v = dict(u)
    sk = lambda g: (db.byname.get(norm(g['src'])) or [dict(kw=set())])[0]['kw'] if db else set()
    gs = []
    for g in u['groups']:
        fx = [t for t in g.get('fx', []) if t.get('src') not in drop]
        gk = sk(g)
        if r is None or (all(k in gk for k in r.get('model_kw', [])) and not any(k in gk for k in r.get('model_not', []))):
            fx += [t for t in add if t['side'] == 'att']
        gs.append(dict(g, fx=fx))
    v['groups'] = gs
    v['dfx'] = [t for t in u.get('dfx', []) if t.get('src') not in drop] + [t for t in add if t['side'] == 'def']
    return v


def _off(u, foe, opt, scopes):
    """這個單位一輪最多殺幾分（射擊、近戰各挑最賺的目標）"""
    tot = 0.0
    for melee in (False, True):
        if ('melee' if melee else 'ranged') not in scopes:
            continue
        tot += max((unit_damage(u, target_of(y), melee, opt) / (target_of(y)['wounds'] or 1) * y['points'] for y in foe['units']), default=0)
    return tot


def _def(u, foe, opt, scopes):
    """對面單一一隊打這個單位，最多殺它幾分（射擊、近戰取大的）"""
    t = target_of(u)
    w = t['wounds'] or 1
    return max((unit_damage(x, t, melee, opt) / w * u['points'] for x in foe['units'] for melee in (False, True)
                if ('melee' if melee else 'ranged') in scopes), default=0)


def _exchange(u, foe, opt):
    """近戰交換（2026-11-15 使用者：禁軍通常是衝鋒、先打的那方）：u 衝鋒先打一隊，對面剩下的才打回來。
    回傳最好的目標的「殺掉的分數 − 被打回來的分數」。打回來＝對面一整輪近戰 ×（1 − 被打掉的比例）。"""
    oc = dict(opt, charge=True)
    tu = target_of(u)
    best = None
    for y in foe['units']:
        ty = target_of(y)
        k = min(1.0, unit_damage(u, ty, True, oc) / (ty['wounds'] or 1))
        back = min(1.0, unit_damage(y, tu, True, opt) / (tu['wounds'] or 1)) * (1 - k)
        v = k * y['points'] - back * u['points']
        best = v if best is None else max(best, v)
    return best or 0.0


def option_values(me, foe, opt, db):
    """每條規則／戰略／Ka'tah 招式：用在哪個單位最賺、多殺幾分或少被殺幾分。戰略＝用在一個單位；規則＝全部符合的單位一起。"""
    out = []
    for r in me.get('_rules', []):
        variants = []
        picks = [t for t in r['tags'] if t.get('pick')]
        if picks and len(picks) > 1:                      # 二選一的（Ka'tah、Martial Mastery）：每個選項分開算
            for t in picks:
                variants.append((t['name'], [dict(t, pick=None, src=r['name'], granted=True, situ=False)]))
        else:
            variants.append(('', [dict(t, src=r['name'], granted=True, situ=False) for t in r['tags']]))
        for vname, tags in variants:
            scopes = set()
            for t in tags:
                scopes |= {'ranged', 'melee'} if t['scope'] == 'all' else {t['scope']}
            rows = []
            for u in me['units']:
                if not _fits(u, r):
                    continue
                base = _variant(u, drop={r['name']}, db=db)
                plus = _variant(u, add=tags, drop={r['name']}, r=r, db=db)
                att = any(t['side'] == 'att' for t in tags)
                dfn = any(t['side'] == 'def' for t in tags)
                # 射擊：打最賺的目標多殺幾分；被射：對面射最痛的一隊少殺幾分
                g_off = _off(plus, foe, opt, {'ranged'}) - _off(base, foe, opt, {'ranged'}) if att and 'ranged' in scopes else 0
                g_def = _def(base, foe, opt, {'ranged'}) - _def(plus, foe, opt, {'ranged'}) if dfn and 'ranged' in scopes else 0
                # 近戰：照「我方衝鋒先打、對面剩下的打回來」算（多殺的和少被打回來的都算進去）
                g_mel = _exchange(plus, foe, opt) - _exchange(base, foe, opt) if 'melee' in scopes else 0
                if g_mel > 0:
                    if att:
                        g_off += g_mel
                    else:
                        g_def += g_mel
                if r['kind'] == '戰略' and (g_off + g_def) > 0 and 'ranged' in scopes and 'melee' in scopes:
                    rng = (g_off - (g_mel if att and g_mel > 0 else 0)) + (g_def - (g_mel if not att and g_mel > 0 else 0))
                    if g_mel > rng:                       # 戰略只能用一個階段：射擊或近戰挑大的
                        g_off, g_def = (g_mel, 0) if att else (0, g_mel)
                    else:
                        g_off, g_def = (g_off - g_mel, g_def) if att and g_mel > 0 else (g_off, g_def - (g_mel if g_mel > 0 else 0))
                if g_off + g_def > 0.5:
                    rows.append(dict(unit=u['name'], off=round(g_off), deff=round(g_def), gain=round(g_off + g_def)))
            rows.sort(key=lambda x: -x['gain'])
            strat = r['kind'] == '戰略'
            total = rows[0]['gain'] if strat and rows else sum(x['gain'] for x in rows)
            cp = int(r['cp']) if str(r.get('cp', '')).isdigit() else 0
            nm = r['name']
            if vname:
                nm = (r['det'].replace('軍隊規則：', '') if r['kind'] == '軍隊規則' else r['name']) + '：' + vname
            out.append(dict(det=r['det'], name=nm, kind=r['kind'], cp=cp, on=r['on_now'],
                            gain=total, per_cp=round(total / cp) if cp else None, units=rows[:5], strat=strat))
    # Superhuman Focus（禁軍 Emperor’s Chosen／Guardians of the Throne，1CP）：讓已經用過招的單位再 readied 一次，
    # 同一輪可以攻擊招和 Kaptaris 都用。價值＝兩招裡比較小的那一招（本來只能二選一，選大的）。
    if any(d['on'] and d['name'] in ('Emperor’s Chosen', 'Guardians of the Throne') for d in me.get('dets', [])):
        per = {}
        for v in out:
            if v['kind'] == '軍隊規則' and '：' in v['name']:
                st = v['name'].split('：', 1)[1]
                for x in v['units']:
                    per.setdefault(x['unit'], {})[st] = x['gain']
            elif v['name'].startswith('Kaptaris'):
                for x in v['units']:
                    per.setdefault(x['unit'], {})['Kaptaris'] = x['gain']
        rows = []
        for un, d in per.items():
            atk = max((g for k, g in d.items() if k != 'Kaptaris'), default=0)
            sec = min(atk, d.get('Kaptaris', 0))
            if sec > 0:
                rows.append(dict(unit=un, off=0, deff=0, gain=sec))
        rows.sort(key=lambda x: -x['gain'])
        if rows:
            out.append(dict(det='Emperor’s Chosen／Guardians of the Throne', name='Superhuman Focus：同一輪攻擊招和 Kaptaris 都用', kind='戰略', cp=1, on=False,
                            gain=rows[0]['gain'], per_cp=rows[0]['gain'], units=rows[:5], strat=True))
    out.sort(key=lambda x: -x['gain'])
    return out


def target_of(u):
    m = u['main']
    return dict(T=m['T'], Sv=m['Sv'], inv=m['inv'], W=m['W'], fnp=u['fnp'], stealth=u['stealth'], kw=u['kw'], dfx=u.get('dfx', ()), points=u['points'],
                models=sum(g['count'] for g in u['groups']), wounds=sum(g['count'] * g['model']['W'] for g in u['groups']),
                wgroups=[(g['count'], g['model']['W'], g['src'] in u.get('leaders', ()), g['model']['Sv'], g['model']['inv'], g.get('pts_each', 0)) for g in u['groups']],
                gnames=[g['name'] for g in u['groups']])


def describe(u):
    t = target_of(u)
    return dict(name=u['name'], points=u['points'], models=t['models'], wounds=t['wounds'], T=t['T'], Sv=t['Sv'], inv=t['inv'], W=t['W'],
                fnp=t['fnp'], M=u['main']['M'], OC=sum(g['count'] * g['model']['OC'] for g in u['groups']), extra=u['extra'], abil=u.get('abil', []),
                weapons=sorted({p[0]['name'].split(' – ')[0] for g in u['groups'] for c, p in g['weapons']}),
                data=[dict(src=g['src'], name=g['name'], count=g['count'], M=g['model']['M'], T=g['model']['T'], Sv=g['model']['Sv'], inv=g['model']['inv'],
                           W=g['model']['W'], weapons=[dict(n=c, name=w['name'], range=w['range'], A=w['A'], skill=w['skill'], S=w['S'], AP=w['AP'], D=w['D'], kw=w.get('desc', ''))
                                                       for c, ps in g['weapons'] for w in ps]) for g in u['groups']],
                info=u.get('info', []), stealth=u['stealth'])


def matrix(a, b, opt, hz=None):
    """a 的每個單位打 b 的每個單位：[射擊比例, 近戰比例]（0~1，佔目標總傷數）。
    hz（list）：填每格 [射擊自傷分, 近戰自傷分]（危險武器，2026-11-16）"""
    rows = []
    for x in a['units']:
        row, hrow, hp = [], [], haz_pts(x)
        for y in b['units']:
            t = target_of(y)
            w = t['wounds'] or 1
            i1, i2 = {}, {}
            cell = [round(unit_damage(x, t, False, opt, info=i1) / w, 3), round(unit_damage(x, t, True, opt, info=i2) / w, 3)]
            hrow.append([round(i1.get('haz', 0) * hp, 1), round(i2.get('haz', 0) * hp + i2.get('chg_mw', 0) * ppw_of(x), 1)])   # 近戰的自傷另含衝鋒吃的致命傷
            if len({g[1] for g in t['wgroups'] if not g[2]}) > 1:     # 非角色的模型 W 不只一種時，防守方怎麼接才有差
                cell += [round(unit_damage(x, t, False, opt, True) / w, 3), round(unit_damage(x, t, True, opt, True) / w, 3)]   # 防守方接得差時
            row.append(cell)
        rows.append(row)
        if hz is not None:
            hz.append(hrow)
    return rows


def summary(a, b, m, hz=None):
    """a 打 b 的摘要。m = matrix(a, b)；hz＝危險武器自傷分（matrix 填的）"""
    s = dict(shoot_pts=0, melee_pts=0, no_answer=[], best=[], shoot_haz=0.0, melee_haz=0.0)
    bp = [u['points'] for u in b['units']]
    for i, x in enumerate(a['units']):
        if not b['units']:
            break
        sh = max(range(len(bp)), key=lambda j: m[i][j][0] * bp[j])
        me = max(range(len(bp)), key=lambda j: m[i][j][1] * bp[j])
        s['shoot_pts'] += m[i][sh][0] * bp[sh]
        s['melee_pts'] += m[i][me][1] * bp[me]
        if hz:
            s['shoot_haz'] += hz[i][sh][0]
            s['melee_haz'] += hz[i][me][1]
        s['best'].append(dict(unit=x['name'], shoot=b['units'][sh]['name'], shoot_pts=round(m[i][sh][0] * bp[sh]), melee=b['units'][me]['name'], melee_pts=round(m[i][me][1] * bp[me])))
    for j, y in enumerate(b['units']):
        top = max((1 - (1 - m[i][j][0]) * (1 - m[i][j][1]) for i in range(len(a['units']))), default=0)
        if top < 0.25:
            s['no_answer'].append(dict(unit=y['name'], best=round(top, 2)))
    s['shoot_pts'], s['melee_pts'] = round(s['shoot_pts']), round(s['melee_pts'])
    s['shoot_haz'], s['melee_haz'] = round(s['shoot_haz'], 1), round(s['melee_haz'], 1)
    return s


def threats(me, foe, m_me, m_foe):
    """foe 每個單位對 me 的威脅，和 me 要花多少火力才打得掉它。m_me = matrix(me, foe)，m_foe = matrix(foe, me)
    威脅 = 它射擊打最賺的目標的殺分 + 近戰打最賺的目標的殺分（一輪）。
    要花的火力 = 從打它最痛的單位開始加，加到剛好 100% 為止，這些單位的分數（最後一個按用到的比例算）。
    優先分數 = 威脅 ÷ 要花的火力 × 100（每花 100 分火力能消掉幾分威脅）。"""
    mp = [u['points'] for u in me['units']]
    comb = lambda c: 1 - (1 - c[0]) * (1 - c[1])
    out = []
    for j, y in enumerate(foe['units']):
        row = m_foe[j]
        sh = max((row[i][0] * mp[i] for i in range(len(mp))), default=0)
        ml = max((row[i][1] * mp[i] for i in range(len(mp))), default=0)
        kills = sorted((dict(unit=me['units'][i]['name'], pct=round(comb(row[i]), 2), points=mp[i]) for i in range(len(mp)) if comb(row[i]) >= 0.75),
                       key=lambda k: -k['points'])
        att = sorted(((comb(m_me[i][j]), i) for i in range(len(mp))), reverse=True)

        def plan(order):
            need, used, cost = 1.0, [], 0.0
            for f, i in order:
                if f < 0.01 or need <= 1e-6:
                    break
                take = min(f, need)
                used.append(dict(unit=me['units'][i]['name'], pct=round(f, 2), points=mp[i]))
                cost += mp[i] * take / f
                need -= take
            return need, used, cost
        # 兩種挑法取便宜的：用最少單位（打最痛的先上）、或用最少分數（每分火力最有效的先上）
        need, used, cost = min(plan(att), plan(sorted(att, key=lambda x: -x[0] / (mp[x[1]] or 1))), key=lambda r: (r[0] > 1e-6, r[2]))
        total = sum(f for f, i in att)
        can = need <= 1e-6
        if not can:                                      # 全軍一輪打不掉：照比例外推
            cost = sum(mp) / total if total > 0.01 else 0
        threat = sh + ml
        out.append(dict(unit=y['name'], points=y['points'], shoot=round(sh), melee=round(ml), threat=round(threat), kills=kills,
                        can=can, max_pct=round(min(total, 1), 2), used=used if can else [], cost=round(cost),
                        score=round(threat / cost * 100, 1) if cost else 0))
    return out


def compare(text_a, text_b, opt, db):
    a, b = parse_list(text_a, db), parse_list(text_b, db)
    over = opt.get('abil') or {}
    resolve(a, over.get('a') or {})
    resolve(b, over.get('b') or {})
    apply_dets(a, over.get('a') or {}, db)
    apply_dets(b, over.get('b') or {}, db)
    hab, hba = [], []
    ab, ba = matrix(a, b, opt, hab), matrix(b, a, opt, hba)
    if opt.get('lite'):                                 # 「打全 meta」只要兩邊的殺分摘要（2026-11-17）
        return dict(sum_ab=summary(a, b, ab, hab), sum_ba=summary(b, a, ba, hba), a_points=a['points'], b_points=b['points'],
                    a_units=len(a['units']), b_units=len(b['units']), b_unknown=len(b['unknown']))
    vals = dict(a=option_values(a, b, opt, db), b=option_values(b, a, opt, db)) if opt.get('values') else None

    def side(l):
        us = [describe(u) for u in l['units']]
        return dict(name=l['name'], faction=l['faction'], points=l['points'], units=us, unknown=l['unknown'], warn=l.get('warn', []), notes=l['notes'], dets=l.get('dets', []),
                    oc=sum(u['OC'] for u in us), wounds=sum(u['wounds'] for u in us), models=sum(u['models'] for u in us))
    return dict(a=side(a), b=side(b), ab=ab, ba=ba, hz_ab=hab, hz_ba=hba, sum_ab=summary(a, b, ab, hab), sum_ba=summary(b, a, ba, hba), thr_a=threats(a, b, ab, ba), thr_b=threats(b, a, ba, ab), data_updated=db.updated, values=vals)



def det_compare(text_a, text_b, opt, db, det=None, base=None):
    """把 A 陣營的每個分隊各開一次（其他分隊都關、軍隊規則照使用者勾的），跟「不開分隊」比
    （2026-11-17 使用者：禁軍 15 個分隊的表「完善到網頁」）。
    回傳 base＝不開分隊的總表殺分／被殺分；rows＝每個分隊：總表殺分（只算一直有效的規則）、被殺分、每條規則和戰略值多少（option_values，條件當作成立）。
    det='list'：只算 base 和分隊清單；det=分隊 id：只算那一個分隊（網頁一個一個要，公開版瀏覽器才不會卡住太久）。"""
    over = dict((opt.get('abil') or {}).get('a') or {})
    ob = (opt.get('abil') or {}).get('b') or {}
    a0 = parse_list(text_a, db)
    dets = [d for d in db.dets.get(a0.get('fid'), [])]
    if not dets:
        return dict(error='讀不出 A 是哪個陣營，或這個陣營沒有分隊資料')
    keys = ['D|' + d['id'] for d in dets]

    def run(det_id, values):
        oa = dict(over, **{k: (k == 'D|' + str(det_id)) for k in keys})
        a, b = parse_list(text_a, db), parse_list(text_b, db)
        resolve(a, over)
        resolve(b, ob)
        apply_dets(a, oa, db)
        apply_dets(b, ob, db)
        dd = next((d for d in a.get('dets', []) if d['id'] == det_id), None)
        if dd is not None and not any(r['on'] for r in dd.get('rules', [])):
            row = dict(base)                            # 這個分隊沒有一直有效（或使用者勾了）的規則：總表跟不開分隊一樣，省掉重算
        else:
            hab, hba = [], []
            ab, ba = matrix(a, b, opt, hab), matrix(b, a, opt, hba)
            s1, s2 = summary(a, b, ab, hab), summary(b, a, ba, hba)
            row = dict(kill_s=s1['shoot_pts'], kill_m=s1['melee_pts'], lost_s=s2['shoot_pts'], lost_m=s2['melee_pts'])
        if values:
            name = next((d['name'] for d in a.get('dets', []) if d['id'] == det_id), '')
            row['vals'] = [dict(name=v['name'], kind=v['kind'], cp=v['cp'], on=v['on'], gain=v['gain'], per_cp=v['per_cp'],
                                best=v['units'][0]['unit'] if v['units'] else '') for v in option_values(a, b, opt, db) if v['det'] == name]
            row['n_rules'] = next((len(d.get('rules', [])) for d in a.get('dets', []) if d['id'] == det_id), 0)
            row['unread'] = next((d.get('unread', 0) for d in a.get('dets', []) if d['id'] == det_id), 0)
        return row
    base = base if isinstance(base, dict) and base else run(None, False)   # 網頁一個一個分隊要的時候，把第一次算的 base 傳回來，不用每次重算
    if det == 'list':
        return dict(faction=a0.get('faction', ''), name=a0.get('name', ''), base=base,
                    dets=[dict(id=d['id'], name=d['name']) for d in dets])
    rows = []
    for d in dets:
        if det is not None and d['id'] != det:
            continue
        r = run(d['id'], True)
        r.update(id=d['id'], name=d['name'], on_now=bool(over.get('D|' + d['id'], d['id'] in a0.get('det_auto', []))))
        rows.append(r)
    return dict(faction=a0.get('faction', ''), name=a0.get('name', ''), base=base, rows=rows)

# ---------- 英文軍表 → 中文（2026-11-15，使用者「英文軍表翻譯成中文」）----------
# 單位名用官方點數網站的中文（跟 App 中文版一樣，簡體）；武器和模型名用 zh_glossary／官方點數頁對得到的，對不到的保留英文。
# 分類標題只翻 App 中文匯出裡看過的寫法，沒看過的不自己編。
ZH_SECTIONS = {'characters': '角色', 'character': '角色', 'battleline': '战线', 'dedicated transports': '专用运输工具',
               'other datasheets': '其他数据表', 'attached units': '联合单位'}
ZH_FACTIONS = {'space marines': '阿斯塔特修会', 'adeptus astartes': '阿斯塔特修会', 'ultramarines': '极限战士',   # App 中文匯出裡看過的
               'adeptus custodes': '帝皇禁军', 'chaos space marines': '阿斯塔特叛军', 'heretic astartes': '阿斯塔特叛军'}
ZH_ROLE = {'leader': '领袖', 'bodyguard': '护卫', 'support': '辅助', 'character': '角色'}


def _zh_maps(db):
    if getattr(db, '_zh_rev', None) is None:
        units = {}
        try:
            with open(os.path.join(DATA, 'zh_units.json'), encoding='utf-8') as f:
                for zh, ens in json.load(f).items():
                    for en in (ens if isinstance(ens, list) else [ens]):
                        units.setdefault(norm(en), zh)
        except OSError:
            pass
        items = {}
        for src in (ZH_WARGEAR, zh_glossary.WEAPONS, getattr(zh_glossary, 'MODELS', {})):
            for zh, en in src.items():
                items[norm(en)] = zh
        db._zh_rev = (units, items)
    return db._zh_rev


def translate_list(text, db):
    units, items = _zh_maps(db)
    out, keep_u, keep_i, nu, ni = [], [], [], 0, 0
    def item_zh(name):
        n = norm(name)
        for c in (n, n.rstrip('s'), n + 's'):
            if c in items:
                return items[c]
        return None
    for l in text.replace('\r', '').split('\n'):
        st = l.strip()
        pre = l[:len(l) - len(l.lstrip())]
        bullet = ''
        if st[:1] in '•◦+-' and st[1:2] == ' ':
            bullet, st = st[:2], st[2:].strip()
        body = st
        m = HEAD.match(st)
        if m and not CJK.search(m[1]):
            name = m[1]
            zh = units.get(norm(name))
            if re.fullmatch(r'strike force', name, re.I):
                zh = '突击'
            if zh:
                nu += 1
            elif re.search(r'[a-z]', name) and int(m[2].replace(',', '')) not in (500, 1000, 2000, 3000):
                nu += 1; keep_u.append(name)
            body = f'{zh or name} ({m[2]} 点)'
        elif norm(st) in ZH_FACTIONS:
            body = ZH_FACTIONS[norm(st)]
        elif norm(st) in ZH_SECTIONS:
            body = ZH_SECTIONS[norm(st)]
        elif re.fullmatch(r'attached unit ?(\d+)', st, re.I):
            body = '联合单位' + re.sub(r'\D', '', st)
        elif re.match(r'attached as:', st, re.I):
            role = st.split(':', 1)[1].strip()
            body = '进行联合的单位：' + re.sub(r'[A-Za-z]+', lambda w: ZH_ROLE.get(w[0].lower(), w[0]), role)
        elif norm(st) == 'warlord':
            body = '统帅'
        elif re.match(r'enhancements?:', st, re.I):
            body = '强化：' + st.split(':', 1)[1].strip()
        elif norm(st) == 'take and hold':
            body = '占领与坚守'
        elif re.match(r'exported with app version', st, re.I):
            body = re.sub(r'exported with app version:?\s*', '已导出，应用程序版本：', st, flags=re.I)
            body = re.sub(r',\s*data version:?\s*', '，数据版本：', body, flags=re.I)
        else:
            mi = ITEM.match(st)
            if mi and not CJK.search(mi[2]):
                zh = item_zh(mi[2]); ni += 1
                if not zh:
                    keep_i.append(mi[2])
                body = f'{mi[1]}x {zh or mi[2]}'
        out.append(pre + bullet + body)
    return dict(zh='\n'.join(out), units=nu, units_kept=sorted(set(keep_u)), items=ni, items_kept=sorted(set(keep_i)))


# ---------- 單位測試：選幾隊打幾隊，幫你分槍（2026-11-15 使用者：「兩隊終結者…對面是太陽領主和科技技師 我要怎麼分槍」）----------
def haz_pts(u):
    """[HAZARDOUS] 每把開過火的武器要擲一次危險骰（核心規則 06.03）：1～2 失敗，這隊吃 1 點致命傷（整隊都是 MONSTER/VEHICLE 吃 3 點）。
    回傳一次危險骰平均損失幾分：1/3 × 致命傷 × 這隊最便宜的每點傷分數（致命傷照一般接傷順序，護衛先接）。"""
    gs = u.get('groups') or []
    if not gs:
        return 0.0
    mw = 3 if all(g.get('big') for g in gs) else 1
    ppw = min(g.get('pts_each', 0) / max(1, g['model']['W']) for g in gs)
    return mw * ppw / 3


def _shot_for(w, fx, aT, tgt, opt, cnt, extra=0, haz_w=0.0, extra_d=0):
    """一把（或 cnt 把一樣的）武器打 tgt：挑最好的模式，回傳每種保護的 (發數, 每發打穿機率, 掉血分布, 平均 D)。
    haz_w：[HAZARDOUS] 模式每把的代價（換算成目標的傷數），挑模式時扣掉（2026-11-16：電漿超載不是免費的）"""
    best = None
    for p in w:
        sv = {}
        a = kd = None
        for g in {(c[3], c[4]) for c in tgt['wgroups']}:
            exp, ev, a, kd = weapon_damage(p, dict(tgt, Sv=g[0], inv=g[1]), opt, fx, aT, detail=True)
            sv[g] = (exp, ev)
        tot = sum(e for e, v in sv.values())
        score = tot - (haz_w * len(sv) if 'HAZARDOUS' in p['kw'] else 0)
        if best is None or score > best[5]:
            best = (tot, p, sv, a, kd, score)
    tot, p, sv, a, kd, score = best
    scale = 1.0
    if (extra or extra_d) and a * cnt > 0:              # 「重骰一顆」換算成多幾次攻擊（Magna Imperator 等），每發機率不變
        add = extra / 2 * rr1_equiv(p, tgt, opt, fx, aT, cnt)[0] if extra else 0.0
        if extra_d:                                     # 重骰一顆傷害骰（2026-11-17）：多掉的血換算成攻擊數
            per = weapon_damage(p, tgt, opt, fx, aT) / a if a else 0
            add += dmg_rr_gain(p, tgt, opt, fx, aT, cnt) / per if per > 0 else 0.0
        scale = 1 + add / (a * cnt)
    subs, kd, a = pool_shots(p, tgt, opt, fx, aT, cnt, sorted(sv), scale)   # 05.04：保護骰從小到大分配
    return dict(name=p['name'], subs=subs, kd=kd, md=sum(k * pp for k, pp in kd.items()), exp=tot * cnt,
                score=score * cnt, haz=cnt if 'HAZARDOUS' in p['kw'] else 0)


def _mw_shot(t, x, tgt):
    """「另外造成 x 點致命傷」打 tgt：條件（目標關鍵字）不合就是 0。致命傷沒有保護，FNP 照算，一點一點照接傷順序扣（會溢到下一隻）。"""
    keys = sorted({(c[3], c[4]) for c in tgt['wgroups']})
    ok = not (t['tkw'] and not any(kw_in(k, tgt['kw']) for k in t['tkw'])) and not (t['tkw_not'] and any(kw_in(k, tgt['kw']) for k in t['tkw_not']))
    if tgt.get('fnp'):
        x = x * (tgt['fnp'] - 1) / 6
    if not ok or x <= 0:
        return dict(name=t['name'] + '（致命傷）', subs=[], kd={1: 1.0}, md=1.0, exp=0.0, score=0.0, haz=0, haz_pts=0.0)
    trials = max(1, math.ceil(x))
    return dict(name=t['name'] + '（致命傷）', subs=[(trials, {k: x / trials for k in keys})], kd={1: 1.0}, md=1.0, exp=x, score=x, haz=0, haz_pts=0.0)


def _target_value(tgt, shots, points):
    """一個目標被這些武器打：(平均打死的分數, 全滅機率, 平均死幾隻)。攻擊方挑開火順序，防守方挑接傷順序（讓死掉的分數最少）"""
    tgt['_order'], tgt['_kdist'], tgt['_gdead'] = [], [1.0], []
    if not shots:
        return 0.0, 0.0, 0.0, 0.0
    groups, names = {}, {}
    for gi, g in enumerate(tgt['wgroups']):
        c, wv, ld, sv, inv = g[:5]
        pe = g[5] if len(g) > 5 else points / max(1, tgt['models'])
        dv = g[6] if len(g) > 6 else pe                 # 防守方心裡的價值＝分數＋角色能力一輪值多少分
        k = (wv, sv, inv, ld, round(pe, 3), round(dv, 3))
        groups[k] = groups.get(k, 0) + c
        if tgt.get('gnames'):
            names.setdefault(k, []).append(tgt['gnames'][gi])
    body = [k for k in groups if not k[3]]
    lead = [k for k in groups if k[3]]
    tot = tgt['wounds'] or 1
    shots = [dict(subs=sb, kd=kd, md=md) for sb, kd, md in merge_pools([(s['subs'], s['kd'], s['md']) for s in shots if s['subs']])]
    best = None
    for att in (sorted(shots, key=lambda s: -s['md']), sorted(shots, key=lambda s: s['md'])):
        worst = None
        for order in alloc_orders(body, lead):
            seq = [k for k in order for _ in range(groups[k])]
            lost, deadw, pw, dn, deadv, partv, cost, kn = allocate([k[0] for k in seq], [(tr, [q[(k[1], k[2])] for k in seq], s["kd"]) for s in att for tr, q in s['subs']],
                                                               stats=True, vals=[k[4] for k in seq], dvals=[k[5] for k in seq])
            # 打死的分數照每隻模型自己的分數算（領袖要真的死了才算他的分數）；打殘沒死的只算一點點，讓程式傾向確保打死
            v = (deadv + 0.05 * (lost - deadw) / tot * points, pw, dn, deadw / tot)
            # 防守方挑順序：用「單位價值」（分數＋角色能力一輪值多少分；2026-11-16 使用者：比兩個單位的價值更適合），
            # 死掉的＋殘血按比例（殘血的角色之後要先接傷，傷會留著；所以寧可先送便宜的血包，不讓重要的角色被打殘）
            if worst is None or cost < worst[0]:
                worst = (cost, v, order, kn)
        if best is None or worst[1][0] > best[0]:
            best = worst[1]
            tgt['_order'] = ['／'.join(dict.fromkeys(names.get(k, []))) for k in worst[2]]   # 防守方挑的接傷順序（給使用者看）
            tgt['_kdist'] = [round(p, 4) for p in worst[3]]
            # 每一組（照接傷順序）整組被打死的機率：死的隻數 ≥ 到這組為止的累計隻數
            cum, gd = 0, []
            for k in worst[2]:
                cum += groups[k]
                gd.append(dict(name=tgt['_order'][len(gd)], n=groups[k], p=round(sum(worst[3][cum:]), 3)))
            tgt['_gdead'] = gd
    return best


def _key_group(u, src):
    """一張資料卡在併隊裡有好幾組模型時（例：Command Squad＝Commander＋老兵），能力算在哪一組：只有一隻的那組（軍官、隊長）"""
    gs = [i for i, g in enumerate(u['groups']) if g['src'] == src]
    if not gs:
        return None
    return min(gs, key=lambda i: (u['groups'][i]['count'] != 1, -u['groups'][i]['model']['W'],
                                  not re.search(r'commander|officer|captain|sergeant|leader', u['groups'][i]['name'].lower())))


def _order_gains(me, foe, opt, db):
    """星界軍的命令：每個友軍單位接到每種命令一輪多殺幾分＋少被殺幾分。回傳 [(單位序號, 命令名, 值)]"""
    rule = next((r for r in me.get('_rules', []) if r['name'] == 'Voice of Command'), None)
    if not rule:
        return []
    out = []
    for i, u in enumerate(me['units']):
        base = _variant(u, drop={'Voice of Command'}, db=db)
        for t in rule['tags']:
            plus = _variant(u, add=[dict(t, pick=None, src='Voice of Command', granted=True, situ=False)], drop={'Voice of Command'}, db=db)
            sc = {'ranged', 'melee'} if t['scope'] == 'all' else {t['scope']}
            g = (_off(plus, foe, opt, sc) - _off(base, foe, opt, sc)) if t['side'] == 'att' else (_def(base, foe, opt, {'ranged'}) - _def(plus, foe, opt, {'ranged'}))
            if g > 0.5:
                out.append((i, t['name'], g))
    return out


def _orders_total(me, officers, gains):
    """officers：[(軍官 key, 張數, 可以給的關鍵字, 限定的命令)]。貪心分配：每隊最多一個命令，值大的先給、能給的軍官裡選限制最多的。"""
    slots = [[n, kw, only] for k, n, kw, only in officers]
    used, tot = set(), 0.0
    for i, name, g in sorted(gains, key=lambda x: -x[2]):
        if i in used:
            continue
        u = me['units'][i]
        ok = [s for s in slots if s[0] > 0 and any(k in u['kw'] for k in s[1]) and (not s[2] or name.upper().replace('’', "'") in s[2])]
        if ok:
            s = min(ok, key=lambda s: (len(s[1]), s[0]))
            s[0] -= 1
            used.add(i)
            tot += g
    return tot


def char_values(me, foe, opt, db, idx):
    """防守方的「單位價值」（2026-11-16 使用者）：me 的第 idx 隊裡每個角色，死了會少掉多少「一輪的價值」。
    1. 帶隊能力（例：圖拉真給 Allarus 重骰）：隊友一輪少殺幾分＋多被殺幾分。角色自己的武器不算（分數已經包含）。
    2. 星界軍軍官的命令：全軍的命令重新分配，少了這個軍官的命令少賺幾分。
    回傳 {組序號: (加的分數, [說明])}"""
    u = me['units'][idx]
    out = {}
    both = {'ranged', 'melee'}
    for src in u.get('leaders', ()):
        gi = _key_group(u, src)
        if gi is None:
            continue
        v = dict(u)
        v['groups'] = [dict(g, fx=[t for t in g.get('fx', []) if g['src'] == src or t.get('src') != src]) for g in u['groups']]
        v['dfx'] = [t for t in u.get('dfx', []) if t.get('src') != src]
        gain = max(0.0, _off(u, foe, opt, both) - _off(v, foe, opt, both)) + max(0.0, _def(v, foe, opt, both) - _def(u, foe, opt, both))
        notes = [f'帶隊能力 {gain:.0f}'] if gain >= 0.5 else []
        out[gi] = (gain, notes)
    # 命令
    gains = None
    officers = []
    for k, x in enumerate(me['units']):
        for src in x['body'] | x.get('leaders', set()):
            sh = (db.byname.get(norm(src)) or [{}])[0]
            if sh.get('orders') and 'OFFICER' in sh.get('kw', ()):
                officers.append(((k, src), sh['orders']['n'], sh['orders']['kw'], sh['orders']['only']))
    mine = [o for o in officers if o[0][0] == idx]
    if mine:
        gains = _order_gains(me, foe, opt, db)
        full = _orders_total(me, officers, gains)
        for o in mine:
            lost = full - _orders_total(me, [x for x in officers if x[0] != o[0]], gains)
            gi = _key_group(u, o[0][1])
            if gi is None or lost < 0.5:
                continue
            g0, n0 = out.get(gi, (0.0, []))
            out[gi] = (g0 + lost, n0 + [f'命令 {o[1]} 個 {lost:.0f}'])
    return out


def scenario(text_a, text_b, opt, db, sel):
    """sel = {att: [A 的單位序號], tgt: [B 的單位序號], melee: bool}。每把武器分開指定目標，找平均打死分數最多的分法。"""
    a, b = parse_list(text_a, db), parse_list(text_b, db)
    over = opt.get('abil') or {}
    resolve(a, over.get('a') or {})
    resolve(b, over.get('b') or {})
    apply_dets(a, over.get('a') or {}, db)
    apply_dets(b, over.get('b') or {}, db)
    melee = bool(sel.get('melee'))
    atk = [i for i in sel.get('att', []) if 0 <= i < len(a['units'])]
    tg = [j for j in sel.get('tgt', []) if 0 <= j < len(b['units'])]
    KAT = '000008391'
    kat_on = any(d.get('army') and d['on'] and d['id'] == 'army' + KAT for d in a.get('dets', []))
    if opt.get('_kaptaris'):                            # 這個近戰階段改用 Kaptaris（防守），就不能用攻擊的 Ka'tah
        kt = army.ARMY[KAT]['rules'][1]['tags'][0]
        for i in atk:
            u = a['units'][i]
            if KAT in u.get('fab', ()):
                for g in u['groups']:
                    g['fx'] = [t for t in g.get('fx', []) if t.get('pick') != 'katah']
                u['dfx'] = [t for t in u.get('dfx', []) if t.get('name') != 'Kaptaris'] + [dict(kt, src='Kaptaris', granted=True, situ=False)]
    if not atk or not tg:
        return dict(error='至少要選一隊出手、一個目標')
    tgts = [target_of(b['units'][j]) for j in tg]
    pts = [b['units'][j]['points'] for j in tg]
    cvals = []                                          # 角色的單位價值（防守方挑接傷順序用；打死的分數照舊只算分數）
    for n, j in enumerate(tg):
        cv = char_values(b, a, opt, db, j) if b['units'][j].get('leaders') else {}
        wg = tgts[n]['wgroups']
        tgts[n]['wgroups'] = [w + (w[5] + cv[gi][0] / max(1, w[0]),) if gi in cv else w for gi, w in enumerate(wg)]
        cvals.append([dict(name=b['units'][j]['groups'][gi]['name'], points=round(wg[gi][5] * wg[gi][0]), extra=round(x[0]), why='；'.join(x[1]))
                      for gi, x in sorted(cv.items(), key=lambda kv: -kv[1][0]) if x[0] >= 0.5])
    items = []                                          # 每把武器一項：(單位序號, 武器模式們, fx, 攻擊方 T)
    for i in atk:
        u = a['units'][i]
        for g in u['groups']:
            fx = [t for t in g.get('fx', []) if not t.get('pick')]
            picks = [t for t in g.get('fx', []) if t.get('pick') and t['scope'] in ('all', 'melee' if melee else 'ranged')]
            ents = [(c, [p for p in ps if p['melee'] == melee]) for c, ps in g['weapons']]
            ents = [(c, ps) for c, ps in ents if ps]
            if not melee and not g['big']:              # 一般步兵：有長槍就不算手槍
                long_ = [(c, ps) for c, ps in ents if not any('PISTOL' in p['kw'] or 'CLOSE-QUARTERS' in p['kw'] for p in ps)]
                ents = long_ or ents
            if melee:                                   # 每個模型一把近戰武器：平均對所有目標最強的先分
                ex = [(c, ps) for c, ps in ents if any('EXTRA ATTACKS' in p['kw'] for p in ps)]
                rest = sorted((e for e in ents if e not in ex), key=lambda e: -max(weapon_damage(p, t, opt, fx, g['model']['T']) for p in e[1] for t in tgts))
                left, use = g['count'], []
                for c, ps in rest:
                    k = min(c, left)
                    if k > 0:
                        use.append((k, ps))
                    left -= k
                ents = ex + use
            rr1 = sum(v for t in fx if t['side'] == 'att' and t['scope'] in ('all', 'melee' if melee else 'ranged')
                      for k, v in t['effs'] if k == 'rr1')
            rr1d = min(1, sum(v for t in fx if t['side'] == 'att' and t['scope'] in ('all', 'melee' if melee else 'ranged')
                              for k, v in t['effs'] if k == 'rr1d'))
            first = len(items)
            for c, ps in ents:
                fxs = [fx + [t] for t in picks] or [fx]
                n = int(round(c))
                step = max(1, -(-n // 10))              # 同一種武器最多拆 10 份
                while n > 0:
                    k = min(step, n)
                    items.append(dict(u=i, ps=ps, fxs=fxs, aT=g['model']['T'], n=k, extra=0, extra_d=0, haz_pts=haz_pts(u)))
                    n -= k
            if (rr1 or rr1d) and len(items) > first and not u.get('_rr1'):    # 一個單位只算一次，加在這組最強的那把
                def rrv(k):                             # 用在「重骰一顆」最划算的那把（整種武器一起算）
                    tot_n = sum(x['n'] for x in items[first:] if x['ps'] is items[k]['ps'])
                    f0, aT0 = items[k]['fxs'][0], items[k]['aT']
                    return max((rr1 / 2 * e * per if rr1 else 0) + (rr1d * dmg_rr_gain(p, t, opt, f0, aT0, tot_n) if rr1d else 0)
                               for p in items[k]['ps'] for t in tgts for e, per in [rr1_equiv(p, t, opt, f0, aT0, tot_n)])
                bi = max(range(first, len(items)), key=rrv)
                items[bi]['extra'] = rr1
                items[bi]['extra_d'] = rr1d
                u['_rr1'] = True
    # 「另外造成致命傷」（例：帝皇親選的 Rendax 加碼）：每個單位一項，當成一把可以指定目標的「武器」（2026-11-16 使用者：致命傷沒算）
    sc_ = 'melee' if melee else 'ranged'
    for i in atk:
        seen = set()
        for g in a['units'][i]['groups']:
            for t in g.get('fx', []):
                if t['side'] == 'att' and t['scope'] in ('all', sc_) and t['name'] not in seen and any(k in ('mw', 'mw_pm') for k, v in t['effs']):
                    if t['cond'] == 'charge' and not (melee and opt.get('charge')):
                        continue
                    seen.add(t['name'])
                    items.append(dict(u=i, ps=[], fxs=[[]], aT=g['model']['T'], n=1, extra=0, extra_d=0, haz_pts=0.0, mw_tag=t,
                                      mw=tag_mw(t, sum(gg['count'] for gg in a['units'][i]['groups']))))
    if not items:
        return dict(error='選的單位沒有可用的' + ('近戰' if melee else '射擊') + '武器')
    cache = {}
    def shot(it, j):
        key = (id(it), j)
        if key not in cache:
            if it.get('mw_tag'):
                cache[key] = _mw_shot(it['mw_tag'], it['mw'], tgts[j])
                return cache[key]
            hw = it['haz_pts'] / max(1e-9, pts[j] / max(1, tgts[j]['wounds']))     # 危險武器的代價換算成目標的傷數
            s_ = max((_shot_for(it['ps'], f, it['aT'], tgts[j], opt, it['n'], it['extra'], hw, it.get('extra_d', 0)) for f in it['fxs']), key=lambda s: s['score'])
            s_['haz_pts'] = s_['haz'] * it['haz_pts']
            cache[key] = s_
        return cache[key]
    wipe = sel.get('goal') == 'wipe'                    # 2026-11-15 使用者：「人物很多時候是不用在意分數的」「你可以看他們的能力決定」
    # 角色的能力價值：這隊有角色時，角色給的能力讓這隊每輪多殺幾分（拿掉角色的標記重算一次）。滅隊的價值＝分數＋2 輪的能力價值
    buff = []
    for j in tg:
        y = b['units'][j]
        if y['leaders']:
            both = {'ranged', 'melee'}
            buff.append(max(0.0, _off(y, a, opt, both) - _off(_variant(y, drop=set(y['leaders']), db=db), a, opt, both)))
        else:
            buff.append(0.0)
    worth = [pts[k] + 2 * buff[k] for k in range(len(tg))]
    # 對面反打（2026-11-15 使用者：「你要看我打完對面反打我的狀況」）：每個目標剩下的部分（照死掉的血算比例）打回來，
    # 挑我方出手單位裡它打最痛的那隊。近戰：同一個近戰階段打回來（只算近戰）；射擊：對面下一回合射擊＋近戰。
    def back_of(y, mine):
        """對面這隊（滿編）打回來，挑我方出手單位裡打最痛的：(殺我幾分, 打誰)"""
        best_b, who = 0.0, None
        for i in atk:
            mu = mine.get(i, a['units'][i])
            tu = target_of(mu)
            w_ = tu['wounds'] or 1
            f = min(1.0, unit_damage(y, tu, True, opt) / w_)
            if not melee:
                f = min(1.0, f + unit_damage(y, tu, False, opt) / w_)
            if f * mu['points'] > best_b:
                best_b, who = f * mu['points'], i
        return best_b, who
    back, back_who = [], []
    for j in tg:
        v_, w_ = back_of(b['units'][j], {})
        back.append(v_)
        back_who.append(w_)
    # 死掉幾隻之後還剩多少輸出（2026-11-15 使用者：照比例扣「很怪」）：防守方自己挑誰死，
    # 護衛裡輸出最低的先死、角色最後；每隻模型的輸出＝那一組模型單獨打的傷害 ÷ 隻數
    per_model = []
    for jj, j in enumerate(tg):
        y = b['units'][j]
        who = back_who[jj]
        if who is None:
            per_model.append([])
            continue
        tu = target_of(a['units'][who])
        w_ = tu['wounds'] or 1
        body_m, lead_m = [], []
        for g in y['groups']:
            yv = dict(y, groups=[g])
            o = unit_damage(yv, tu, True, opt) / w_ + (0 if melee else unit_damage(yv, tu, False, opt) / w_)
            (lead_m if g['src'] in y.get('leaders', ()) else body_m).extend([o / max(1, g['count'])] * int(g['count']))
        per_model.append(sorted(body_m) + sorted(lead_m))
    def rem_frac(jj, dn):
        pm = per_model[jj]
        tot_o = sum(pm)
        if not pm or tot_o <= 0:
            return max(0.0, 1 - dn / max(1, tgts[jj]['models']))
        k = int(dn)
        removed = sum(pm[:k]) + (dn - k) * (pm[k] if k < len(pm) else 0)
        return max(0.0, 1 - removed / tot_o)
    # 衝鋒進去被對方的規則咬（2026-11-17：Minefield、Warpflame Gargoyles…）：每個「我方單位→目標」只算一次，換成分數
    chg = {}
    if melee and opt.get('charge'):
        for i in atk:
            for jj in range(len(tg)):
                x = chg_mw(tgts[jj], a['units'][i])
                if x > 0:
                    chg[(i, jj)] = x * ppw_of(a['units'][i])
    def chg_cost(asg):
        return sum(chg.get(p, 0.0) for p in {(it['u'], x) for it, x in zip(items, asg) if x is not None and x >= 0})
    def value(asg):
        tot = -chg_cost(asg)
        for j in range(len(tg)):
            v, pw, dn, df = _target_value(tgts[j], [shot(it, j) for it, x in zip(items, asg) if x == j], pts[j])
            tot += (pw * worth[j] + 0.01 * v if wipe else v) - rem_frac(j, dn) * back[j]
        tot -= sum(shot(it, x)['haz_pts'] for it, x in zip(items, asg) if x is not None and x >= 0)
        return tot
    # 先貪心：傷害大的武器先放，每把放到「多打死最多分」的目標；再一把一把試著換目標，直到沒有更好
    order = sorted(range(len(items)), key=lambda k: -max(shot(items[k], j)['exp'] for j in range(len(tg))))
    asg = [None] * len(items)
    for k in order:
        bestj, bestv = 0, None
        for j in range(len(tg)):
            asg[k] = j
            v = value([x if x is not None else -1 for x in asg])
            if bestv is None or v > bestv:
                bestj, bestv = j, v
        asg[k] = bestj
    def improve(asg):
        cur = value(asg)
        for _ in range(8):
            moved = False
            for k in range(len(items)):
                for j in range(len(tg)):
                    if j == asg[k]:
                        continue
                    old = asg[k]
                    asg[k] = j
                    v = value(asg)
                    if v > cur + 1e-6:
                        cur, moved = v, True
                    else:
                        asg[k] = old
            if not moved:
                break
        return cur, asg
    # 從好幾個起點各自改進，取最好的（只從貪心開始容易卡住：例如一門砲打不死大角色，就永遠不會往那邊移）
    starts = [asg] + [[j] * len(items) for j in range(len(tg))]
    cur, asg = max((improve(list(st)) for st in starts), key=lambda x: x[0])
    def lab(lst, i):                                    # 同名的單位加編號
        nm = lst['units'][i]['name']
        same = [k for k, u in enumerate(lst['units']) if u['name'] == nm]
        return nm + (f' #{same.index(i) + 1}' if len(same) > 1 else '')
    res_t = []
    for j in range(len(tg)):
        v, pw, dn, df = _target_value(tgts[j], [shot(it, j) for it, x in zip(items, asg) if x == j], pts[j])
        res_t.append(dict(name=lab(b, tg[j]), buff=round(buff[j]), back=round(rem_frac(j, dn) * back[j]), back_full=round(back[j]), points=pts[j], models=tgts[j]['models'], value=round(v), p_wipe=round(pw, 3), dead=round(dn, 2), cvals=cvals[j], order=tgts[j].get('_order', []), kdist=tgts[j].get('_kdist', []), gdead=tgts[j].get('_gdead', [])))
    plan_ = {}
    for it, j in zip(items, asg):
        s = shot(it, j)
        if it.get('mw_tag') and s['exp'] <= 0:          # 致命傷打不到這個目標（例：Rendax 加碼只打怪獸／載具）就不列
            continue
        key = (lab(a, it['u']), s['name'], lab(b, tg[j]))
        plan_[key] = plan_.get(key, 0) + it['n']
    # 對照：全部集火同一個目標
    alt = []
    for j in range(len(tg)):
        v, pw, dn, df = _target_value(tgts[j], [shot(it, j) for it in items], pts[j])
        bk = rem_frac(j, dn) * back[j] + sum(back[k] for k in range(len(tg)) if k != j)      # 沒打的目標全力反打
        hz = sum(shot(it, j)['haz_pts'] for it in items) + chg_cost([j] * len(items))
        alt.append(dict(name=lab(b, tg[j]), value=round(v), p_wipe=round(pw, 3), dead=round(dn, 2), models=tgts[j]['models'], back=round(bk), hazard=round(hz, 1), net=round(v - bk - hz), kdist=tgts[j].get('_kdist', [])))
    tot_pts = sum(t['value'] for t in res_t)
    tot_back = sum(t['back'] for t in res_t)
    tot_haz = sum(shot(it, j)['haz_pts'] for it, j in zip(items, asg)) + chg_cost(asg)
    out = dict(melee=melee, goal='wipe' if wipe else 'points', total=round(tot_pts), back=round(tot_back), hazard=round(tot_haz, 1), chg=round(chg_cost(asg), 1), net=round(tot_pts - tot_back - tot_haz), targets=res_t, plan=[dict(unit=k[0], weapon=k[1], target=k[2], n=n) for k, n in plan_.items()], focus=alt)
    # 用了「每場一次」的能力：另外算不用的話會怎樣，讓使用者決定要不要省（2026-11-15 使用者要求）
    once = [(x['key'], x['name']) for i in atk for x in a['units'][i]['abil'] if x['on'] and x.get('once')]
    if once and not opt.get('_noonce'):
        ab = dict(over.get('a') or {}, **{k: False for k, n in once})
        sub = scenario(text_a, text_b, dict(opt, abil=dict(over, a=ab), _noonce=True), db, sel)
        if not sub.get('error'):
            out['save_once'] = dict(names=sorted({n for k, n in once}), total=sub['total'], targets=sub['targets'])
    # 反打時我方可以用的防守（2026-11-15 使用者「要加」）：防守戰略（擋一隊的反打）和 Kaptaris（整個近戰階段，代替攻擊招）
    dfs = []
    rem = [rem_frac(j, _target_value(tgts[j], [shot(it, j) for it, x in zip(items, asg) if x == j], pts[j])[2]) for j in range(len(tg))]
    for r in a.get('_rules', []):
        if r['kind'] != '戰略' or not r['tags'] or any(t['side'] != 'def' for t in r['tags']):
            continue
        if not any(t['scope'] in ('all', 'melee' if melee else 'ranged') or not melee for t in r['tags']):
            continue
        best = None
        for i in atk:
            if not _fits(a['units'][i], r):
                continue
            mu = _variant(a['units'][i], add=[dict(t, src=r['name'], granted=True, situ=False) for t in r['tags']], db=db)
            for j in range(len(tg)):
                nb, _w = back_of(b['units'][tg[j]], {i: mu})
                red = rem[j] * (back[j] - nb)
                if red > 0.5 and (best is None or red > best[0]):
                    best = (red, i, j)
        if best:
            dfs.append(dict(name=r['name'], kind=r['kind'], cp=r.get('cp', ''), save=round(best[0]), unit=lab(a, atk[0] if best[1] is None else best[1]), vs=lab(b, tg[best[2]])))
    dfs.sort(key=lambda x: -x['save'])
    out['defense'] = dfs
    if melee and kat_on and not opt.get('_kaptaris') and any(KAT in a['units'][i].get('fab', ()) for i in atk):
        kp = scenario(text_a, text_b, dict(opt, _kaptaris=True, _noonce=True), db, sel)
        if not kp.get('error'):
            out['kaptaris'] = dict(total=kp['total'], back=kp['back'], net=kp['net'], plan=kp['plan'])
    has_char = [j for j in range(len(tg)) if any(g[2] for g in tgts[j]['wgroups'])]
    out['char_note'] = bool(has_char)
    return out


# ---------- 軍表健檢（List Check，2026-11-24 使用者要做 Lexmechanic 的工具）----------
# 拿一張表去打 6 種固定的標準目標，看每一類一輪能打掉幾個；跟 meta 表（data/listcheck_bench.json）比強弱，弱的那類推薦同陣營 meta 表裡最會打它的單位。
# 標準目標用真的資料卡（照官方 App 格式寫一小張表給 parse_list 讀），點數只是佔位，不影響計算。
LC_REFS = [
    ('horde', '步兵海', 'Boyz ×20', "R (170 Points)\n\nOrks\n\nBoyz (170 Points)\n• 1x Boss Nob\n• 19x Boy\n"),
    ('meq', '中裝步兵', 'Intercessor Squad ×10', "R (160 Points)\n\nSpace Marines\n\nIntercessor Squad (160 Points)\n• 1x Intercessor Sergeant\n• 9x Intercessor\n"),
    ('elite', '終結者', 'Terminator Squad ×5', "R (170 Points)\n\nSpace Marines\n\nTerminator Squad (170 Points)\n• 1x Terminator Sergeant\n• 4x Terminator\n"),
    ('tank', '坦克', 'Land Raider', "R (240 Points)\n\nSpace Marines\n\nLand Raider (240 Points)\n• 1x Land Raider\n"),
    ('monster', '怪獸', 'Carnifex', "R (115 Points)\n\nTyranids\n\nCarnifex (115 Points)\n• 1x Carnifex\n"),
    ('knight', '騎士', 'Knight Paladin', "R (375 Points)\n\nImperial Knights\n\nKnight Paladin (375 Points)\n• 1x Knight Paladin\n"),
]
_LC_T = {}


def _lc_load(db):
    if id(db) not in _LC_T:
        out = []
        for k, zh, desc, txt in LC_REFS:
            l = parse_list(txt, db)
            if l['units']:
                resolve(l, {})
                apply_dets(l, {}, db)
                out.append((k, zh, desc, l['units'][0]))
        _LC_T[id(db)] = out
    return _LC_T[id(db)]


def lc_targets(db):
    return [(k, zh, d, target_of(u)) for k, zh, d, u in _lc_load(db)]


def lc_attackers(db):
    """耐打度用（2026-11-24）：同樣 6 個標準單位反過來當攻擊方，用它們預設的武器。"""
    return _lc_load(db)


def lc_def_rows(lst, opt, db):
    """每個標準單位打我的每個單位：[射擊打掉幾 %, 近戰打掉幾 %]（0~1）。"""
    A = lc_attackers(db)
    rows = []
    for u in lst['units']:
        t = target_of(u)
        w = t['wounds'] or 1
        rows.append([[round(unit_damage(x, t, False, opt) / w, 3), round(unit_damage(x, t, True, opt) / w, 3)] for k, zh, d, x in A])
    return rows


def lc_def_tot(lst, drows):
    """全軍耐打度：標準單位一輪（射擊＋近戰）打我每個單位，平均打掉幾 %（照單位分數加權）。越低越耐打。"""
    pts = [max(u['points'], 1) for u in lst['units']]
    n = len(drows[0]) if drows else 0
    return [round(sum(p * min(1, r[i][0] + r[i][1]) for p, r in zip(pts, drows)) / sum(pts), 3) for i in range(n)] if pts else []


def lc_rows(lst, opt, db):
    """每個單位打每種標準目標：[射擊打掉幾 %, 近戰打掉幾 %]（佔目標總傷數，0~1，可超過 1＝一輪能打掉不只一個）。"""
    T = lc_targets(db)
    return [[[round(unit_damage(u, t, False, opt) / (t['wounds'] or 1), 3), round(unit_damage(u, t, True, opt) / (t['wounds'] or 1), 3)] for k, zh, d, t in T]
            for u in lst['units']]


def lc_bench():
    try:
        with open(os.path.join(DATA, 'listcheck_bench.json'), encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def listcheck(text, opt, db):
    a = parse_list(text, db)
    over = opt.get('abil') or {}
    resolve(a, over.get('a') or {})
    apply_dets(a, over.get('a') or {}, db)
    T = lc_targets(db)
    rows = lc_rows(a, opt, db)
    tot = [[round(sum(r[i][0] for r in rows), 2), round(sum(r[i][1] for r in rows), 2)] for i in range(len(T))]
    bench = lc_bench()
    b = bench.get('all', {})
    verdict = []
    for i, (k, zh, d, t) in enumerate(T):
        q = b.get(k)
        v = tot[i][0] + tot[i][1]
        # 跟 meta 表比：低於 25% 分位＝弱、高於 75%＝強（meta 表是 4 勝以上的代表表）
        verdict.append('' if not q else ('弱' if v < q[0] else '強' if v > q[2] else '普通'))
    drows = lc_def_rows(a, opt, db)
    dtot = lc_def_tot(a, drows)
    bd = bench.get('def', {})
    # 耐打：被打掉的 % 越低越好，所以低於 25% 分位＝強、高於 75%＝弱
    dverdict = ['' if not bd.get(k) else ('強' if dtot[i] < bd[k][0] else '弱' if dtot[i] > bd[k][2] else '普通') for i, (k, *_) in enumerate(T)]
    fac = bench.get('fac', {}).get(a['faction'], {})
    fixes = {k: fac.get(k, [])[:3] for i, (k, zh, d, t) in enumerate(T) if verdict[i] == '弱'}
    return dict(name=a['name'], faction=a['faction'], points=a['points'], unknown=a['unknown'], warn=a.get('warn', []),
                units=[dict(name=u['name'], points=u['points']) for u in a['units']],
                drows=drows, dtot=dtot, dbench=bd, dverdict=dverdict,
                refs=[dict(key=k, zh=zh, desc=d, stat=f"T{t['T']}、{t['Sv']}+" + (f"／{t['inv']}++" if t['inv'] else '') + f"、共 {t['wounds']} 傷") for k, zh, d, t in T], rows=rows, tot=tot, bench=b, verdict=verdict, fixes=fixes,
                bench_n=bench.get('n', 0), bench_date=bench.get('date', ''), data_updated=db.updated)


# ── 偵察／階段小抄（scout.html，2026-11-24）────────────────────────────────
# 貼一張表 → 全軍規則、分隊規則、強化、能用的戰術卡、每個單位的威脅距離和能力，再照階段排成小抄。
# 規則原文只在 HP 版（full=True）回傳；公開版只給名字、時機、CP、能用的單位，和計算器讀得懂的效果（中文）。
SC_PH = (('pre', '開戰前／部署'), ('cmd', '指揮階段'), ('move', '移動階段'), ('shoot', '射擊階段'), ('charge', '衝鋒階段'), ('fight', '格鬥階段'), ('any', '任何階段'), ('always', '常駐'))
SC_CORE = {                                              # 核心能力：自己寫的一句中文說明（不是抄規則原文）
    'deadly demise': ('致命爆炸', '被消滅時擲 D6，6 的話 6" 內的單位都吃致命傷'),
    'deep strike': ('深入打擊', '從預備隊降到離所有敵人 8" 以外的任何地方，敵方部署區也可以'),
    'scouts': ('偵察', '開戰前可以先移動；也可從戰略預備隊直接放進自己部署區'),
    'feel no pain': ('不覺疼痛', '每失去一點傷擲 D6，達到數值就不扣'),
    'stealth': ('隱匿', '被射擊時算有掩體'),
    'infiltrators': ('滲透', '部署時可放在離敵方部署區和敵人 8" 以外的任何地方'),
    'damaged': ('受損', '剩下的傷降到數值以下時，攻擊命中 -1'),
    'lone operative': ('獨行特工', '沒加入其他單位時，敵人在 12" 外看不到它，也不能用間接射擊打它'),
    'firing deck': ('射擊甲板', '載具射擊時，裡面載的幾個模型可以一起開火'),
    'hover': ('懸浮', '起飛時移動距離不用扣 2"'),
    'fights first': ('先攻', '格鬥階段比一般單位先打'),
    'super-heavy walker': ('超重型步行', '可以穿過 4" 以下的地形和非泰坦模型'),
}
SC_CORE_STRAT = {                                        # 第十一版核心戰術卡：自己寫的中文名和一句說明
    'smokescreen': ('煙幕', '對方射擊階段開始時：SMOKE 單位，和被它擋住的單位，被射擊時算有掩體'),
    'command re-roll': ('指揮重骰', '擲完骰後重骰一顆（命中、造傷、傷害、豁免、前進、衝鋒…；衝鋒要整組重骰）'),
    'epic challenge': ('史詩挑戰', '角色單位被選去格鬥時：一個角色模型的近戰武器得到 [PRECISION]'),
    'insane bravery': ('瘋狂之勇', '一次戰鬥震撼檢定自動通過（每場一次）'),
    'counteroffensive': ('反擊', '對方一個單位打完後：我方一個可格鬥的單位得到先攻，接著馬上打'),
    'heroic intervention': ('英勇介入', '對方衝鋒階段結束時：12" 內沒交戰的單位反衝鋒（載具要是角色或步行者）'),
    'explosives': ('爆破', '沒前進的 EXPLOSIVES／GRENADES 單位：8" 內一個敵人擲 6 顆 D6，每個 4+ 吃 1 致命傷'),
    'crushing impact': ('碾壓衝擊', '怪獸／載具衝鋒到位後：擲 T 顆 D6，1 自己吃 1 致命傷，5+ 對方吃 1（最多 6）'),
    'rapid ingress': ('快速進場', '對方移動階段結束時：戰略預備隊的一個單位進場（第一輪不行）'),
    'fire overwatch': ('守望射擊', '對方移動階段結束時：一個沒交戰的單位用快速射擊開火'),
}
SC_SKIP = {'leader', 'support'}
_SC = {}


def _sc_txt(s):
    s = re.sub(r'<p class="ShowFluff.*?</p>', '', s or '', flags=re.S)
    s = re.sub(r'<br\s*/?>|</li>|</p>', '\n', s)
    s = re.sub(r'<li>', '• ', s)
    s = re.sub(r'<[^>]+>', ' ', s).replace('\xa0', ' ')
    s = re.sub(r'[ \t]+', ' ', s)
    return re.sub(r'\n\s*\n+', '\n', s).strip()


def _sc_target(html):
    """戰術卡 TARGET 段 → (需要的關鍵字, 排除的關鍵字)。每個都是「組」的清單，組＝格子的清單，格子＝可以替換的字（A/B）。
    例：「ADEPTUS CUSTODES INFANTRY/MOUNTED unit」→ [[['ADEPTUS'],['CUSTODES'],['INFANTRY','MOUNTED']]]。
    「或」分開的是不同組（符合一組就行）；「You can only select…」這種附加條件不看。"""
    m = re.search(r'TARGET:(.*?)(?:EFFECT:|$)', html, re.S)
    t = re.sub(r'<br\s*/?>.*', '', m[1] if m else '', flags=re.S)
    t = re.split(r'\.\s', t)[0]
    excl = []
    for ex in re.findall(r'\(excluding(.*?)\)', t, re.S):
        excl += _sc_groups(ex)[:1]
    t = re.sub(r'\(excluding.*?\)', ' ', t, flags=re.S)
    return _sc_groups(t), excl


def _sc_groups(t):
    toks = list(re.finditer(r'<span class="kwb">([^<]+)</span>', t))
    groups, cur, last = [], None, None
    for mt in toks:
        gap = re.sub(r'<[^>]+>', ' ', t[last:mt.start()]) if last is not None else ''
        w = [x.upper() for x in mt[1].split()]
        if cur is not None and gap.strip() == '/':
            cur[-1] += w[:1]
            cur += [[x] for x in w[1:]]
        elif cur is not None and not gap.strip():
            cur += [[x] for x in w]
        else:
            if cur is not None and not re.search(r'\bor\b', gap):
                break
            cur = [[x] for x in w]
            groups.append(cur)
        last = mt.end()
    return groups


def _sc_fit(words, g):
    return all(any(x in words for x in slot) for slot in g)


def _sc_phases(t):
    """一段規則文字 → (階段, 誰的回合) 清單。回合：me＝自己、opp＝對方、both。"""
    low = t.lower().replace('’', "'")
    out = []
    for k, en in (('cmd', 'command phase'), ('move', 'movement phase'), ('shoot', 'shooting phase'), ('charge', 'charge phase'), ('fight', 'fight phase')):
        if en not in low:
            continue
        me = re.search(r"\byour " + en, low)
        op = re.search(r"opponent's " + en, low)
        out.append((k, 'both' if (me and op) or not (me or op) else 'me' if me else 'opp'))
    if not out:
        for k, rx in (('charge', r'charge move|declares? a charge'), ('shoot', r'selected to shoot|ranged attack'), ('fight', r'selected to fight|melee attack')):
            if re.search(rx, low):
                out.append((k, 'me' if k == 'charge' else 'both'))
    if not out and re.search(r'any phase', low):
        out.append(('any', 'both'))
    if not out and re.search(r'start of (?:the|each) battle round', low):
        out.append(('cmd', 'me'))
    if not out and re.search(r'deploy|pre-battle|muster|declare battle formations|start of the battle|first battle round', low):
        out.append(('pre', 'me'))
    return out or [('always', 'both')]


def _sc_load(db):
    if id(db) in _SC:
        return _SC[id(db)]
    ab = {r['id']: r for r in rd('Abilities')}
    sheet_ab = {}
    for r in rd('Datasheets_abilities'):
        if r['type'] not in ('Datasheet', 'Wargear', 'Core', 'Faction', 'Primarch', 'Psychic'):
            continue
        a = ab.get(r['ability_id']) or {}
        nm = (r['name'] or a.get('name', '')).strip()
        if not nm:
            continue
        sheet_ab.setdefault(r['datasheet_id'], []).append(dict(name=nm, type=r['type'], param=(r['parameter'] or '').strip(), model=r['model'] or '',
                                                                 id=r['ability_id'] or '', text=_sc_txt(r['description'] or a.get('description', '')),
                                                                 key='B' + (r['ability_id'] or r['datasheet_id'] + '.' + r['line'])))
    strats = {}
    for r in rd_safe('Stratagems'):
        ty = r.get('type') or ''
        if 'boarding' in ty.lower():
            continue
        key = r.get('detachment_id') or ('core' if ty == 'Core Stratagem' else '')
        if not key:
            continue
        d = _sc_txt(r.get('description'))
        need, excl = _sc_target(r.get('description') or '')
        ph = (r.get('phase') or '').lower()
        phs = [k for k, en in (('cmd', 'command'), ('move', 'movement'), ('shoot', 'shooting'), ('charge', 'charge'), ('fight', 'fight')) if en in ph] or ['any']
        tu = (r.get('turn') or '').lower()
        strats.setdefault(key, []).append(dict(id=r.get('id', ''), name=string.capwords((r.get('name') or '').lower()), cp=r.get('cp_cost', ''), type=ty, phases=phs,
                                               turn='me' if tu.startswith('your') else 'opp' if tu.startswith('opponent') else 'both',
                                               need=need, excl=excl, text=d, det=r.get('detachment', '')))
    det_ab = {}
    for r in rd_safe('Detachment_abilities'):
        det_ab.setdefault(r.get('detachment_id', ''), []).append(dict(id=r.get('id', ''), name=r.get('name', ''), text=_sc_txt(r.get('description'))))
    enh = {}
    for r in rd_safe('Enhancements'):
        enh.setdefault(enh_key(r.get('name', '')), []).append(dict(id=r.get('id', ''), name=re.sub(r'\s*\(one per army\)', '', r.get('name', ''), flags=re.I), faction=r.get('faction_id', ''),
                                                                    det=r.get('detachment_id', ''), text=_sc_txt(r.get('description'))))
    tagmap = {}
    for did, box in db.det_rules.items():
        for x in box['rules']:
            tagmap[x['id']] = '；'.join(tagger.label(t) for t in x['tags'])
    try:                                                 # 繁體中文名（tools/zh_scout.py 產生）
        with open(os.path.join(DATA, 'zh_scout.json'), encoding='utf-8') as f:
            zh = json.load(f)
    except OSError:
        zh = {}
    try:                                                 # 規則中文摘要（zh_sum/*.json 抽查過的合併成 data/zh_sum.json；編號 A/D/S/E＋Wahapedia id）
        with open(os.path.join(DATA, 'zh_sum.json'), encoding='utf-8') as f:
            sm = json.load(f)
    except OSError:
        sm = {}
    _SC[id(db)] = dict(ab=ab, sheet_ab=sheet_ab, strats=strats, det_ab=det_ab, enh=enh, tagmap=tagmap, zh=zh, sum=sm)
    return _SC[id(db)]


def _sc_range(w):
    m = re.match(r'\s*(\d+)', str(w.get('range', '')))
    return int(m[1]) if m and not w.get('melee') else 0


def _p2d6(n):
    return sum(1 for a in range(1, 7) for b in range(1, 7) if a + b >= n) / 36


def scout(text, db, full=False):
    L = _sc_load(db)
    Z = L['zh']
    zr = lambda n: Z.get('rules', {}).get(norm(n), '')

    def zu(name):
        if CJK.search(name):
            return ''
        ps = [Z.get('units', {}).get(norm(p), '') for p in name.split(' + ')]
        return ' + '.join(ps) if all(ps) else ''

    a = parse_list(text, db)
    resolve(a, {})
    fid = a.get('fid') or ''
    units = []
    for i, u in enumerate(a['units']):
        t = target_of(u)
        M = u['main']['M']
        rng = max((_sc_range(w) for g in u['groups'] for c, ps in g['weapons'] for w in ps), default=0)
        core, abil, seen = [], [], set()
        for inf in u['info']:
            sh = db.find(inf['src'], fid) or {}
            for x in L['sheet_ab'].get(sh.get('id'), []):
                low = norm(x['name'])
                if low in SC_SKIP or (x['type'], low) in seen:
                    continue
                seen.add((x['type'], low))
                if x['type'] == 'Core':
                    zh, note = SC_CORE.get(low, ('', ''))
                    prm = x['param'] + ('+' if low == 'feel no pain' and x['param'] and not x['param'].endswith('+') else '')
                    core.append(dict(name=x['name'] + (' ' + prm if prm else ''), param=prm,
                                     zh=zh, note=note, src=inf['src'] if len(u['info']) > 1 else '', model=x['model']))
                elif x['type'] != 'Faction':
                    abil.append(dict(key=x['key'], name=x['name'], zh=zr(x['name']), src=inf['src'] if len(u['info']) > 1 else '', model=x['model'], ph=_sc_phases(x['text']), text=x['text'] if full else ''))
        ds = any(c['name'].lower().startswith('deep strike') for c in core)
        enh = []
        for e in u['extra']:
            k = enh_key(e)
            rows = L['enh'].get(enh_key(db.zh_enh.get(k, k)), [])
            row = next((r for r in rows if r['faction'] == fid), rows[0] if rows else None)
            if row:
                enh.append(dict(key='E' + row['id'], name=row['name'], zh=Z.get('enh', {}).get(norm(row['name']), ''), sum=L['sum'].get('E' + row['id'], ''), ph=_sc_phases(row['text']), text=row['text'] if full else ''))
        units.append(dict(i=i, name=u['name'], zh=zu(u['name']), points=u['points'], M=M, T=t['T'], Sv=t['Sv'], inv=t['inv'], W=t['W'], wounds=t['wounds'], models=t['models'],
                          fnp=t['fnp'], OC=sum(g['count'] * g['model']['OC'] for g in u['groups']), kw=sorted(u['kw']),
                          fly='FLY' in u['kw'], rng=rng, chg=[M + 7, M + 12], reach=M + rng if rng else 0, ds=ds,
                          ds_p=round(_p2d6(9), 3) if ds else 0, core=core, abil=abil, enh=enh,
                          leaders=sorted(u['leaders']), body=sorted(u['body'])))
    # 軍隊規則（陣營能力）
    fab = set().union(*(u['fab'] for u in a['units'])) if a['units'] else set()
    army = [dict(key='A' + x, name=L['ab'][x]['name'], zh=zr(L['ab'][x]['name']), sum=L['sum'].get('A' + x, ''), ph=_sc_phases(_sc_txt(L['ab'][x]['description'])), text=_sc_txt(L['ab'][x]['description']) if full else '')
            for x in sorted(fab) if x in L['ab']]
    dets = []
    for did in a.get('det_auto', []):
        nm = next((d['name'] for d in db.dets.get(fid, []) if d['id'] == did), did)
        rules = [dict(key='D' + r['id'], name=r['name'], zh=zr(r['name']), sum=L['sum'].get('D' + r['id'], ''), ph=_sc_phases(r['text']), text=r['text'] if full else '') for r in L['det_ab'].get(did, [])]
        dets.append(dict(id=did, name=nm, zh=Z.get('dets', {}).get(norm(nm), ''), rules=rules))
    # 戰術卡：選到的分隊＋核心。哪些單位能用：TARGET 裡的粗體關鍵字（「或」分開的每一組要全部符合），陣營關鍵字大家都有就不看
    allw = [{x for k in u['kw'] for x in k.split()} for u in a['units']]
    common = set.intersection(*allw) if allw else set()
    strats = []
    for key in a.get('det_auto', []) + ['core']:
        for s in L['strats'].get(key, []):
            ok = [i for i, w in enumerate(allw) if (not s['need'] or any(_sc_fit(w, g) for g in s['need'])) and not any(_sc_fit(w, g) for g in s['excl'])]
            groups = [' '.join('/'.join(sl) for sl in g if not all(x in common for x in sl)) for g in s['need']]
            groups = [g for g in groups if g]
            cz = SC_CORE_STRAT.get(norm(s['name']), ('', '')) if key == 'core' else ('', '')
            strats.append(dict(key='S' + s['id'], name=s['name'], zh=cz[0] or zr(s['name']), note=cz[1] or L['sum'].get('S' + s['id'], ''), cp=s['cp'], phases=s['phases'], turn=s['turn'], det=s['det'] if key != 'core' else '核心',
                               core=key == 'core', units=ok, need=groups, excl=[' '.join('/'.join(sl) for sl in g) for g in s['excl']], eff=L['tagmap'].get(s['id'], ''),
                               text=s['text'] if full else ''))
    return dict(name=a['name'], faction=a['faction'], fid=fid, points=a['points'], unknown=a['unknown'], warn=a.get('warn', []),
                units=units, army=army, dets=dets, strats=strats, full=full, data_updated=db.updated, phases=SC_PH)


_PR = {}


def _pr_models(db):
    """Datasheets_models：每個資料卡的模型能力值（含 Ld、底座），列印用。"""
    if id(db) not in _PR:
        box = {}
        for r in rd('Datasheets_models'):
            box.setdefault(r['datasheet_id'], []).append(dict(name=r['name'], M=r['M'], T=r['T'], Sv=r['Sv'], inv=(r['inv_sv'] or '').strip('-'),
                                                              W=r['W'], Ld=r['Ld'], OC=r['OC'], base=r['base_size']))
        _PR[id(db)] = box
    return _PR[id(db)]


def printout(text, db, full=False):
    """⑨ 印軍表＋⑩ 印戰術卡（2026-11-25）：偵察的資料再加每個單位的模型能力值和武器表。規則原文只在 full（HP 版）時給。"""
    j = scout(text, db, full)
    a = parse_list(text, db)
    resolve(a, {})
    fid = a.get('fid') or ''
    M = _pr_models(db)
    L = _sc_load(db)
    kinds = {}
    for key, rows in L['strats'].items():
        for s in rows:
            ty = s['type']
            kinds[(key, s['name'])] = '核心' if ty == 'Core Stratagem' else ty.split('–', 1)[1].replace('Stratagem', '').strip() if '–' in ty else ''
    for s, key in zip(j['strats'], [k for k in a.get('det_auto', []) + ['core'] for _ in L['strats'].get(k, [])]):
        s['kind'] = kinds.get((key, s['name']), '')
    for ju, u in zip(j['units'], a['units']):
        models, seen = [], set()
        for inf in u['info']:
            sh = db.find(inf['src'], fid) or {}
            for m in M.get(sh.get('id'), []):
                if m['name'] not in seen:
                    seen.add(m['name'])
                    models.append(m)
        ws = {}
        for g in u['groups']:
            for c, ps in g['weapons']:
                for w in ps:
                    k = (w['name'], w['melee'], w['range'], w['A'], w['S'], w['AP'], w['D'])
                    if k not in ws:
                        ws[k] = dict(name=w['name'], melee=w['melee'], range=w['range'], A=w['A'], skill=w['skill'], S=w['S'], AP=w['AP'], D=w['D'], kw=w.get('desc', ''), n=0, who=[])
                    ws[k]['n'] += c
                    if g['name'] not in ws[k]['who']:
                        ws[k]['who'].append(g['name'])
        comp = [dict(n=g['count'], name=g['name']) for g in u['groups']]
        ju.update(models=models, weapons=list(ws.values()), comp=comp)
    if full:
        _pr_zh(j)
    return j


# 武器關鍵字中文（2026-11-25，詞取自社群中文規則書；間接射擊、單發、轉換是自己翻的 ⚠️）
PR_WKW = [('rapid fire', '速射'), ('sustained hits', '連擊'), ('lethal hits', '致命一擊'), ('devastating wounds', '毀滅傷害'), ('twin-linked', '雙聯'),
          ('torrent', '洪流'), ('blast', '爆炸'), ('melta', '熱熔'), ('hazardous', '危險'), ('precision', '精準'), ('ignores cover', '無視掩體'),
          ('indirect fire', '間接射擊'), ('lance', '騎槍'), ('extra attacks', '額外攻擊'), ('one shot', '單發'), ('psychic', '靈能'), ('cleave', '劈砍'),
          ('close-quarters', '近距離'), ('conversion', '轉換'), ('assault', '突擊'), ('heavy', '重型'), ('pistol', '手槍'), ('anti-', '反')]


PR_UKW = {'MONSTER': '巨獸', 'VEHICLE': '載具', 'INFANTRY': '步兵', 'CHARACTER': '角色', 'PSYKER': '靈能者', 'MOUNTED': '騎乘', 'FLY': '飛行',
          'TITANIC': '泰坦級', 'BEAST': '野獸', 'SWARM': '蟲群', 'WALKER': '步行機', 'AIRCRAFT': '飛行器', 'EPIC HERO': '史詩英雄', 'TOWERING': '高聳'}


def _pr_ukw(t):
    for en, zh in sorted(PR_UKW.items(), key=lambda x: -len(x[0])):
        t = re.sub(r'(?<![A-Za-z])' + en + r'(?![A-Za-z])', zh, t, flags=re.I)
    return re.sub(r'(?<![A-Za-z])non-', '非', t, flags=re.I).replace('/', '／')


def _pr_kw(desc):
    out = []
    for part in [x.strip() for x in (desc or '').split(',') if x.strip()]:
        low = part.lower()
        for en, zh in PR_WKW:
            if low.startswith(en):
                rest = part[len(en):].strip()
                if en == 'anti-':
                    out.append('反' + _pr_ukw(rest))
                else:
                    num, _, cond = rest.partition(':')
                    out.append(zh + (' ' + num.strip() if num.strip() else '') + ('（' + _pr_ukw(cond.strip()) + '）' if cond.strip() else ''))
                break
        else:
            out.append(part)
    return '、'.join(out)


def _pr_zh(j):
    """把 data/zh_full.json（規則完整中文翻譯，只在 HP）接到列印資料上：每條加 zn（中文名）、zt（中文全文）。"""
    if 'zh_full' not in _PR:
        try:
            with open(os.path.join(DATA, 'zh_full.json'), encoding='utf-8') as f:
                _PR['zh_full'] = json.load(f)
        except OSError:
            _PR['zh_full'] = {}
    Z = _PR['zh_full']
    def put(x):
        z = Z.get(x.get('key', ''))
        if z:
            x['zn'], x['zt'] = z.get('n', ''), z.get('t', '')
    for x in j['army'] + j['strats']:
        put(x)
    for d in j['dets']:
        for x in d['rules']:
            put(x)
    for u in j['units']:
        for x in u['abil'] + u['enh']:
            put(x)
        for w in u['weapons']:
            w['zn'] = Z.get('W' + norm(w['name']), {}).get('n', '')
            w['kw_zh'] = _pr_kw(w['kw'])
    j['zh_full'] = bool(Z)


def api(req, db):
    """網頁送來的 {a, b, opt} → 計算結果；{translate: true, a, b} → 兩張表翻成中文。app.py（伺服器）和 browser.js（瀏覽器裡跑）共用。"""
    if req.get('print'):
        return printout(str(req.get('a', '')), db, bool(req.get('full')))
    if req.get('scout'):
        return scout(str(req.get('a', '')), db, bool(req.get('full')))
    if req.get('listcheck'):
        ro = req.get('opt') or {}
        opt = {k: bool(ro.get(k)) for k in ('half', 'cover', 'charge', 'still')}
        opt['abil'] = {'a': {str(k): bool(v) for k, v in ((ro.get('abil') or {}).get('a') or {}).items()}, 'b': {}}
        return listcheck(str(req.get('a', '')), opt, db)
    if req.get('translate'):
        return {k: translate_list(str(req.get(k, '')), db) for k in ('a', 'b')}
    if req.get('scenario'):
        ro = req.get('opt') or {}
        opt = {k: bool(ro.get(k)) for k in ('half', 'cover', 'charge', 'still')}
        ab = ro.get('abil') or {}
        opt['abil'] = {sd: {str(k): bool(v) for k, v in (ab.get(sd) or {}).items()} for sd in ('a', 'b')}
        sc = req['scenario']
        ta, tb = str(req.get('a', '')), str(req.get('b', ''))
        if sc.get('rev'):                                # B 出手打 A
            ta, tb = tb, ta
            opt['abil'] = dict(a=opt['abil']['b'], b=opt['abil']['a'])
        return scenario(ta, tb, opt, db,
                        dict(att=[int(x) for x in sc.get('att', [])], tgt=[int(x) for x in sc.get('tgt', [])], melee=bool(sc.get('melee')), goal=sc.get('goal', 'points')))
    ro = req.get('opt') or {}
    opt = {k: bool(ro.get(k)) for k in ('half', 'cover', 'charge', 'still', 'values', 'lite')}
    ab = ro.get('abil') or {}
    opt['abil'] = {sd: {str(k): bool(v) for k, v in (ab.get(sd) or {}).items()} for sd in ('a', 'b')}
    if req.get('detcmp') in ('a', 'b'):                  # 「比較所有分隊」（2026-11-17）：B 的就把兩張表對調
        ta, tb = str(req.get('a', '')), str(req.get('b', ''))
        if req['detcmp'] == 'b':
            ta, tb = tb, ta
            opt['abil'] = dict(a=opt['abil']['b'], b=opt['abil']['a'])
        return dict(det_compare(ta, tb, opt, db, req.get('det'), req.get('base')), side=req['detcmp'])
    return compare(str(req.get('a', '')), str(req.get('b', '')), opt, db)
