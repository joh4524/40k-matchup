"""戰錘 40K 第十一版：兩張軍表互打的期望值計算（2026-11-15 使用者要求，不接 AI）。
資料：data/*.csv 是 Wahapedia 的資料匯出檔（wahapedia.ru/wh40k11ed/the-rules/data-export/），更新用 update_data.sh。
算武器數值、武器關鍵字、讀得懂的單位能力（tags.py／manual.py）、軍隊規則、分隊規則、戰略和強化（army.py 手動整理的，2026-11-15 先做禁軍；其他陣營用 tags.py 自動讀）。
假設（沒在規則裡查到明文的）：造傷表 2+/3+/4+/5+/6+；命中和造傷修正最多 ±1；合併單位用護衛的 T。
"""
import csv, difflib, functools, math, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import json
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
def eff_damage(dexpr, bonus, w, fnp, reduce=0, half=False):
    """一次沒擋住的攻擊，平均讓一個 W 傷的模型掉幾傷（多的傷害不會溢到別的模型；FNP 每點各骰）"""
    keep = (fnp - 1) / 6 if fnp else 1.0
    tot = 0.0
    for d, p in dist(dexpr).items():
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
            add(r.get('detachment_id') or ('core' if not r.get('faction_id') else ''), r.get('id', ''), '戰略', r.get('name', '').title(),
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


def weapon_damage(w, tgt, opt, fx=(), aT=0):
    """一把武器（一個模型拿的一把）對目標造成的期望傷數（已考慮保護、FNP、傷害不溢出、勾選的能力）"""
    tkw, ranged = tgt['kw'], not w['melee']
    kw = w['kw']
    am = dict(hit=0, wound=0, ap=0, dmg=0, attacks=0, strength=0, rr_hit=None, rr_wound=None, crit_hit=6, ign=0, mw=0, rr1=0)
    for t in fx:
        if applies(t, w, tgt, opt, 0, aT):
            for k, v in t['effs']:
                if k == 'kw':
                    kw = dict(kw)
                    for kk, vv in parse_kw(v).items():
                        kw[kk] = kw.get(kk, []) + vv if kk == 'anti' else vv
                elif k in ('rr_hit', 'rr_wound'):
                    am[k] = 'all' if 'all' in (v, am[k]) else '1'
                elif k == 'crit_hit':
                    am[k] = min(am[k], v)
                else:
                    am[k] += v
    s = mean(w['S']) + am['strength']
    dm = dict(hit=0, wound=0, ap=0, dmg=0, half=False, cover=False, inv=tgt['inv'], fnp=tgt['fnp'])
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
        crit_h, norm_h = a * p_c * f, a * p_n * f
    sus = mean(kw['SUSTAINED HITS'][0]) if has('SUSTAINED HITS') else 0
    lethal = has('LETHAL HITS')
    to_wound = norm_h + crit_h * sus + (0 if lethal else crit_h)
    auto_w = crit_h if lethal else 0
    # 造傷
    t = tgt['T']
    thr = 2 if s >= 2 * t else 3 if s > t else 4 if s == t else 6 if s * 2 <= t else 5
    wmod = (1 if (w['melee'] and opt.get('charge') and 'LANCE' in kw) else 0) + am['wound'] + dm['wound']
    wmod = max(0 if am['ign'] else -1, min(1, wmod))
    crit_y = min([y for x, y in kw.get('anti', []) if kwmatch(x, tkw)] + [6])
    p_crit = (7 - crit_y) / 6
    p_norm = sum(1 for r in range(2, crit_y) if r + wmod >= thr) / 6
    rr = 'all' if 'TWIN-LINKED' in kw else am['rr_wound']
    f = 2 - p_crit - p_norm if rr == 'all' else 1 + 1 / 6 if rr == '1' else 1
    p_crit, p_norm = p_crit * f, p_norm * f
    crit_w, norm_w = to_wound * p_crit, to_wound * p_norm + auto_w
    mortal = 0.0
    if has('DEVASTATING WOUNDS'):
        mortal = crit_w
    else:
        norm_w += crit_w
    # 保護
    need = tgt['Sv'] + max(0, abs(num(w['AP'])) + am['ap'] + dm['ap'])
    if dm['inv']:
        need = min(need, dm['inv'])
    p_fail = min(1.0, max(1 / 6, (need - 1) / 6))
    bonus = (int(mean(kw['MELTA'][0])) if (half and 'MELTA' in kw) else 0) + am['dmg']
    return (norm_w * p_fail + mortal) * eff_damage(w['D'], bonus, tgt['W'], dm['fnp'], -dm['dmg'], dm['half'])


def unit_damage(att, tgt, melee, opt):
    """整個單位打一輪（射擊或近戰）對目標的期望傷數。有「二選一」的規則（pick）時，每個選法都算一次取最好的。"""
    sc = 'melee' if melee else 'ranged'
    picks = {}
    for g in att['groups']:
        for t in g.get('fx', ()):
            if t.get('pick') and t['scope'] in ('all', sc) and t['name'] not in picks.setdefault(t['pick'], []):
                picks[t['pick']].append(t['name'])
    if not picks:
        return _unit_damage(att, tgt, melee, opt, {})
    ks = sorted(picks)
    combos = [{}]
    for k in ks:
        combos = [dict(c, **{k: n}) for c in combos for n in picks[k]]
    return max(_unit_damage(att, tgt, melee, opt, c) for c in combos)


def _unit_damage(att, tgt, melee, opt, chosen):
    total, extra = 0.0, 0.0
    sc = 'melee' if melee else 'ranged'
    for g in att['groups']:
        fx = [t for t in g.get('fx', ()) if not t.get('pick') or chosen.get(t['pick']) == t['name']]
        entries = []                                   # (每把期望傷數, 幾把, 武器)
        for cnt, profs in g['weapons']:
            ps = [p for p in profs if p['melee'] == melee]
            if ps:
                best = max(ps, key=lambda p: weapon_damage(p, tgt, opt, fx, g['model']['T']))
                entries.append((weapon_damage(best, tgt, opt, fx, g['model']['T']), cnt, best))
        # 「另外造成致命傷」「重骰一顆骰」：整個單位一次，不是每把武器
        mw = rr1 = 0
        for t in fx:
            if t['side'] != 'att' or t['scope'] not in ('all', sc):
                continue
            if t['tkw'] and not any(kw_in(k, tgt['kw']) for k in t['tkw']):
                continue
            if t['tkw_not'] and any(kw_in(k, tgt['kw']) for k in t['tkw_not']):
                continue
            if t['cond'] == 'charge' and not (melee and opt.get('charge')):
                continue
            for k, v in t['effs']:
                mw += v if k == 'mw' else 0
                rr1 += v if k == 'rr1' else 0
        if mw:
            extra = max(extra, mw * (1 - (7 - tgt['fnp']) / 6 if tgt['fnp'] else 1))
        if rr1 and entries:
            extra = max(extra, rr1 * max(d / max(1.0, mean(w['A'])) for d, c, w in entries))
        if melee:
            total += sum(d * c for d, c, w in entries if 'EXTRA ATTACKS' in w['kw'])
            left = g['count']                          # 每個模型只用一把近戰武器：挑最好的
            for d, c, w in sorted((e for e in entries if 'EXTRA ATTACKS' not in e[2]['kw']), key=lambda e: -e[0]):
                use = min(c, left)
                total += d * use
                left -= use
        else:
            pistol = lambda w: 'PISTOL' in w['kw'] or 'CLOSE-QUARTERS' in w['kw']
            a = sum(d * c for d, c, w in entries if not pistol(w))
            b = sum(d * c for d, c, w in entries if pistol(w))
            total += a + b if g['big'] else max(a, b)  # 非怪獸／載具：手槍和其他槍二選一
    return min(total + extra, tgt['wounds'])


# ---------- 讀軍表 ----------
SECTION = re.compile(r"^[A-Z][A-Z '&/-]+$")
HEAD = re.compile(r'^(.+?) ?[(（]?([\d,]+) ?(?:points?|pts|点|點)[)）]?$', re.I)  # App 設成中文時是「点」；新版 App 是「(180点)」沒空格、也有全形括號
CJK_SECTION = re.compile(r'^[一-鿿]+$')                                   # 中文版的分類標題：角色、战线、其他数据表…
ITEM = re.compile(r'^(\d+)x (.+)$')


def parse_list(text, db):
    ZH_GUESSED.clear()
    lines = [l.replace('\t', '    ').rstrip() for l in text.replace('\r', '').split('\n')]
    out = dict(name='', faction='', points=0, units=[], unknown=[], notes=[])
    fid = None
    for l in lines[:12]:
        if norm(l) in db.factions and not fid:
            fid, out['faction'] = db.factions[norm(l)], l.strip()
    m = HEAD.match(lines[0].strip()) if lines else None
    if m:
        out['name'] = m[1]
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
                    if sheet:
                        out['notes'].append(f'「{m[1]}」資料裡沒有完全同名的，用「{sheet["name"]}」代替')
                    else:
                        out['unknown'].append(m[1])
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
    return out


DET_TYPE_KW = ('INFANTRY', 'VEHICLE', 'MONSTER', 'MOUNTED', 'CHARACTER', 'WALKER', 'TERMINATOR', 'BATTLELINE', 'BEAST', 'SWARM', 'FLY', 'PSYKER', 'TITANIC')
ZH_UNKNOWN = set()
ZH_GUESSED = set()                                       # (資料卡, 中文, 英文)：拆字推測的
ZH_WARGEAR = {}                                          # DB() 載入時填
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
        ens = [e for e in (zh_glossary.WEAPONS.get(name.strip()), ZH_WARGEAR.get(name.strip())) if e]
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


def loadout_items(sheet, gname):
    """資料卡的預設配備：挑主詞對得上這組模型的那句，回傳 [(數量, 武器各型態)]"""
    sents = re.findall(r'(This model|Every model|Every [^.:]*?|The [^.:]*?) (?:is|are) equipped with: ([^.]*)\.', sheet['loadout'])
    if not sents:
        return []
    g = norm(gname).rstrip('s')
    pick = next((x for x in sents if norm(x[0]).replace('every ', '').replace('the ', '').rstrip('s') == g), None)
    pick = pick or next((x for x in sents if x[0] in ('This model', 'Every model')), None) or sents[-1]
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
    single = len(groups) == 1 and groups[0]['count'] == 1
    for g in groups:
        have = {id(p) for c, p in g['weapons']} | {p[0]['base'] for c, p in g['weapons']}
        if not g['weapons']:                             # 這組模型沒列武器：用資料卡的預設配備
            for n, nm, profs in loadout_items(sheet, g['name']):
                g['weapons'].append((n * g['count'], profs))
                added.append(nm)
        elif single:                                     # 單一模型：補上軍表沒列、又不能換掉的固定武器
            for n, nm, profs in loadout_items(sheet, g['name']):
                b = profs[0]['base']
                if b not in have and not re.search(re.escape(b) + r's?(?:(?! with ).){0,25}replaced', sheet['options']):
                    g['weapons'].append((n, profs))
                    added.append(nm)
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
            u['abil'].append(dict(key=f'{i}|{k}', name=t['name'], src=t['src'], label=t['label'], on=on, avail=avail, why=why))
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
        if d['name'] in army.DET:
            rules = army.DET[d['name']]
            unread = max(0, box['total'] - len(rules))
        else:
            rules = [dict(name=r['name'], kind=r['kind'], cp=r['cp'], tags=r['tags'], need=r['need'], on=False) for r in box['rules']]
            unread = box['unread']
        groups.append(dict(id=d['id'], name=d['name'], rules=rules, unread=unread, hand=d['name'] in army.DET))
    core = db.det_rules.get('core', {})
    if core.get('rules'):
        groups.append(dict(id='core', name='通用戰略（Core）', rules=[dict(name=r['name'], kind=r['kind'], cp=r['cp'], tags=r['tags'], need=r['need'], on=False)
                                                               for r in core['rules']], unread=core['unread']))
    sheet_kw = lambda g: (db.byname.get(norm(g['src'])) or [dict(kw=set())])[0]['kw']
    out = []
    for d in groups:
        auto = d.get('army') or d['id'] in lst.get('det_auto', [])
        on = bool(over.get('D|' + d['id'], auto))
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


def target_of(u):
    m = u['main']
    return dict(T=m['T'], Sv=m['Sv'], inv=m['inv'], W=m['W'], fnp=u['fnp'], stealth=u['stealth'], kw=u['kw'], dfx=u.get('dfx', ()),
                models=sum(g['count'] for g in u['groups']), wounds=sum(g['count'] * g['model']['W'] for g in u['groups']))


def describe(u):
    t = target_of(u)
    return dict(name=u['name'], points=u['points'], models=t['models'], wounds=t['wounds'], T=t['T'], Sv=t['Sv'], inv=t['inv'], W=t['W'],
                fnp=t['fnp'], M=u['main']['M'], OC=sum(g['count'] * g['model']['OC'] for g in u['groups']), extra=u['extra'], abil=u.get('abil', []),
                weapons=sorted({p[0]['name'].split(' – ')[0] for g in u['groups'] for c, p in g['weapons']}),
                data=[dict(src=g['src'], name=g['name'], count=g['count'], M=g['model']['M'], T=g['model']['T'], Sv=g['model']['Sv'], inv=g['model']['inv'],
                           W=g['model']['W'], weapons=[dict(n=c, name=w['name'], range=w['range'], A=w['A'], skill=w['skill'], S=w['S'], AP=w['AP'], D=w['D'], kw=w.get('desc', ''))
                                                       for c, ps in g['weapons'] for w in ps]) for g in u['groups']],
                info=u.get('info', []), stealth=u['stealth'])


def matrix(a, b, opt):
    """a 的每個單位打 b 的每個單位：[射擊比例, 近戰比例]（0~1，佔目標總傷數）"""
    rows = []
    for x in a['units']:
        row = []
        for y in b['units']:
            t = target_of(y)
            w = t['wounds'] or 1
            row.append([round(unit_damage(x, t, False, opt) / w, 3), round(unit_damage(x, t, True, opt) / w, 3)])
        rows.append(row)
    return rows


def summary(a, b, m):
    """a 打 b 的摘要。m = matrix(a, b)"""
    s = dict(shoot_pts=0, melee_pts=0, no_answer=[], best=[])
    bp = [u['points'] for u in b['units']]
    for i, x in enumerate(a['units']):
        if not b['units']:
            break
        sh = max(range(len(bp)), key=lambda j: m[i][j][0] * bp[j])
        me = max(range(len(bp)), key=lambda j: m[i][j][1] * bp[j])
        s['shoot_pts'] += m[i][sh][0] * bp[sh]
        s['melee_pts'] += m[i][me][1] * bp[me]
        s['best'].append(dict(unit=x['name'], shoot=b['units'][sh]['name'], shoot_pts=round(m[i][sh][0] * bp[sh]), melee=b['units'][me]['name'], melee_pts=round(m[i][me][1] * bp[me])))
    for j, y in enumerate(b['units']):
        top = max((1 - (1 - m[i][j][0]) * (1 - m[i][j][1]) for i in range(len(a['units']))), default=0)
        if top < 0.25:
            s['no_answer'].append(dict(unit=y['name'], best=round(top, 2)))
    s['shoot_pts'], s['melee_pts'] = round(s['shoot_pts']), round(s['melee_pts'])
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
    ab, ba = matrix(a, b, opt), matrix(b, a, opt)

    def side(l):
        us = [describe(u) for u in l['units']]
        return dict(name=l['name'], faction=l['faction'], points=l['points'], units=us, unknown=l['unknown'], notes=l['notes'], dets=l.get('dets', []),
                    oc=sum(u['OC'] for u in us), wounds=sum(u['wounds'] for u in us), models=sum(u['models'] for u in us))
    return dict(a=side(a), b=side(b), ab=ab, ba=ba, sum_ab=summary(a, b, ab), sum_ba=summary(b, a, ba), thr_a=threats(a, b, ab, ba), thr_b=threats(b, a, ba, ab), data_updated=db.updated)


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


def api(req, db):
    """網頁送來的 {a, b, opt} → 計算結果；{translate: true, a, b} → 兩張表翻成中文。app.py（伺服器）和 browser.js（瀏覽器裡跑）共用。"""
    if req.get('translate'):
        return {k: translate_list(str(req.get(k, '')), db) for k in ('a', 'b')}
    ro = req.get('opt') or {}
    opt = {k: bool(ro.get(k)) for k in ('half', 'cover', 'charge', 'still')}
    ab = ro.get('abil') or {}
    opt['abil'] = {sd: {str(k): bool(v) for k, v in (ab.get(sd) or {}).items()} for sd in ('a', 'b')}
    return compare(str(req.get('a', '')), str(req.get('b', '')), opt, db)
