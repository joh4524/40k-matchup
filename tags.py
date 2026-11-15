"""把資料卡能力的文字自動轉成程式看得懂的標記（2026-11-15）。不用 AI：照固定句型比對，全陣營通用。
只認「這個單位自己攻擊時」和「這個單位被打時」的句型；選一個敵人、給友軍加成、戰術卡、Overwatch 之類的不處理。
標記：dict(name 能力名, side 'att'|'def', scope 'ranged'|'melee'|'all', effs [(效果, 值)], tkw 目標關鍵字, weapon 限定武器,
           cond 'charge'|'half'|'still'|'s_gt_t'|None（程式會自己判斷）, leading 要帶隊才有, on 預設有沒有算, label 中文說明)
"""
import html, re

M = r"(?:this model|this unit|that unit|the bearer|a model in (?:this|that|the bearer[’']s) unit|models in (?:this|that) unit)"
LEAD = re.compile(r"^while (?:this model|the bearer) is leading a unit,\s*", re.I)
A1 = re.compile(rf"^each time {M} makes (?:a|an) (ranged |melee )?attack(.*)$", re.I)
A2 = re.compile(rf"^(ranged |melee )?weapons equipped by {M} have the (.+?) abilit", re.I)
D1 = re.compile(rf"^each time (?:a|an) (ranged |melee )?attack (?:targets|is allocated to) {M}(.*)$", re.I)
D2 = re.compile(rf"^{M} ha(?:s|ve) a (\d)\+ invulnerable save", re.I)
D3 = re.compile(rf"^{M} ha(?:s|ve) the feel no pain (\d)\+ ability(.*)$", re.I)
# 第十一版新 codex 的短句寫法（例：This unit’s melee attacks that target … have +1 AP／Attacks that target this unit have -1 D）
NEWA = re.compile(r"^(?P<pre>(?:if|while|in) [^,]*,\s*(?:if [^,]*,\s*)?)?this (?P<who>unit|model)[’']s (?P<scope>ranged |melee )?attacks"
                  r"(?P<tgt> that target [^:]*?)? (?:have|can)\b(?P<rest>.*)$", re.I)
NEWD = re.compile(r"^(?P<scope>ranged |melee )?attacks (?:that target this (?P<who>unit|model)|allocated to this model|allocated to models in this unit)"
                  r"(?P<cond> with a S greater than this (?:unit|model)[’']s T)? have (?P<rest>.*)$", re.I)
COVER = re.compile(rf"^{M} ha(?:s|ve) the benefit of cover", re.I)
SL = r"((?:[A-Z][A-Z\-]+)(?: [A-Z][A-Z\-]+)*(?: / (?:[A-Z][A-Z\-]+)(?: [A-Z][A-Z\-]+)*)*)"
SKIP = re.compile(r"overwatch|stratagem|deadly demise|battle-shock test", re.I)
# 程式沒辦法判斷的條件 → 預設不算，讓使用者自己勾
SITU = re.compile(r"objective marker|\border\b|closest eligible|starting strength|battle-shocked|within \d|more than \d|disembark|until the|"
                  r"friendly|provided|below|first time|\bwhile\b|\bif\b|psychic|mortal wound|instead|deployment zone|within (?!half)|that is |that contains|that has |"
                  r"targets (?:its|that|the) |hated|quarry", re.I)
EXCL = re.compile(r"\(excluding ([A-Z][A-Z\- ]+?(?:,? (?:and|or) [A-Z][A-Z\- ]+?)*)(?: units?)?\s*\)")
TKW = re.compile(r"targets (?:an? |one or more )?(?:enemy )?(?:unit that can )?((?:[A-Z][A-Z\-]+(?: [A-Z][A-Z\-]+)*)(?:,? (?:or|and) (?:[A-Z][A-Z\-]+(?: [A-Z][A-Z\-]+)*))*)")
NAMES = dict(hit='命中', wound='造傷', rr_hit='命中重骰', rr_wound='造傷重骰', ap='AP', dmg='傷害', attacks='攻擊數', strength='S',
             crit_hit='爆擊命中', inv='無敵保護', fnp='FNP', half='傷害減半', cover='算有掩體')


def clean(t):
    return re.sub(r'\s+', ' ', html.unescape(re.sub(r'<[^>]+>', ' ', t or ''))).strip()


def effects(low, orig, side):
    e = []
    for pat, key, val in ((r'add 1 to the hit roll', 'hit', 1), (r'subtract 1 from the hit roll', 'hit', -1),
                          (r'add 1 to the wound roll', 'wound', 1), (r'subtract 1 from the wound roll', 'wound', -1)):
        if re.search(pat, low):
            e.append((key, val))
    if side == 'att':
        if re.search(r're-roll a hit roll of 1', low):
            e.append(('rr_hit', '1'))
        elif re.search(r're-roll the hit roll', low):
            e.append(('rr_hit', 'all'))
        if re.search(r're-roll a wound roll (?:of|or) 1', low):
            e.append(('rr_wound', '1'))
        elif re.search(r're-roll the wound roll', low):
            e.append(('rr_wound', 'all'))
        for pat, key in ((r'improve the armour penetration characteristic of that attack by (\d)', 'ap'), (r'add (\d) to the damage characteristic', 'dmg'),
                         (r'add (\d) to the attacks characteristic', 'attacks'), (r'add (\d) to the strength characteristic', 'strength'),
                         (r'unmodified hit roll of (\d)\+ scores a critical hit', 'crit_hit')):
            m = re.search(pat, low)
            if m:
                e.append((key, int(m[1])))
        if re.search(r'ha(?:s|ve) the \[', low):
            e += [('kw', k.upper()) for k in re.findall(r'\[([^\]]+)\]', orig)]
    else:
        if re.search(r'subtract 1 from the damage characteristic', low):
            e.append(('dmg', -1))
        if re.search(r'halve the damage', low):
            e.append(('half', 1))
        m = re.search(r'worsen the armour penetration characteristic of that attack by (\d)', low)
        if m:
            e.append(('ap', -int(m[1])))
        if re.search(r'has the benefit of cover', low) and 'because of' not in low:
            e.append(('cover', 1))
    return e


def effects_new(low, orig, side):
    e = []
    sg = 1 if side == 'att' else -1
    for pat, key in ((r'%s(\d) ap\b', 'ap'), (r'%s(\d) to wound rolls', 'wound'), (r'%s(\d) to hit rolls', 'hit'), (r'%s(\d) d\b', 'dmg')):
        m = re.search(pat % ('\\+' if side == 'att' else '-'), low)
        if m:
            e.append((key, sg * int(m[1])))
    if side == 'att':
        for pat, key in ((r'\+(\d) a\b', 'attacks'), (r'\+(\d) s\b', 'strength')):
            m = re.search(pat, low)
            if m:
                e.append((key, int(m[1])))
        if re.search(r're-roll hit rolls of 1', low):
            e.append(('rr_hit', '1'))
        elif re.search(r're-roll hit rolls', low):
            e.append(('rr_hit', 'all'))
        if re.search(r're-roll wound rolls of 1', low):
            e.append(('rr_wound', '1'))
        elif re.search(r're-roll wound rolls', low):
            e.append(('rr_wound', 'all'))
        e += [('kw', re.sub(r'\s+', ' ', k).strip().upper()) for k in re.findall(r'\[([^\]]+)\]', orig)]
    return e


def label(t):
    sc = dict(ranged='射擊', melee='近戰', all='')[t['scope']]
    parts = []
    for k, v in t['effs']:
        if k == 'kw':
            parts.append(f'[{v}]')
        elif k in ('rr_hit', 'rr_wound'):
            parts.append(NAMES[k] + ('（只重骰 1）' if v == '1' else ''))
        elif k in ('inv', 'fnp', 'crit_hit'):
            parts.append(f'{NAMES[k]} {v}+')
        elif k in ('half', 'cover'):
            parts.append(NAMES[k])
        elif k == 'ign':
            parts.append('無視命中／造傷／BS 的負修正')
        elif k == 'mw':
            parts.append(f'另外致命傷 {v:.1f}')
        elif k == 'rr1':
            parts.append(f'重骰一顆骰（約多 {v} 次攻擊）')
        else:
            parts.append(f'{NAMES[k]} {v:+d}')
    s = ('被' + sc + '打時 ' if t['side'] == 'def' else (sc + ' ' if sc else '')) + '、'.join(parts)
    extra = []
    if t['weapon']:
        extra.append('限 ' + t['weapon'])
    if t['tkw']:
        extra.append('目標是 ' + '/'.join(t['tkw']))
    if t.get('wkw'):
        extra.append('限 [' + t['wkw'] + '] 武器')
    if t['tkw_not']:
        extra.append('目標不是 ' + '/'.join(t['tkw_not']))
    if t['cond']:
        extra.append(dict(charge='衝鋒時', half='半射程內', still='沒移動時', s_gt_t='對方 S 大於 T 時', t_gt_t='目標 T 比自己高時')[t['cond']])
    if t['leading']:
        extra.append('帶隊時給整隊')
    if t.get('once'):
        extra.append('每場一次，預設有算')
    if t['situ']:
        extra.append('有其他條件，預設不算')
    return s + ('（' + '，'.join(extra) + '）' if extra else '')


def tag_ability(name, desc):
    out = []
    text = clean(desc)
    text = re.sub(r'\.\s+(?=Re-roll )', '; ', text)                 # 「can: Re-roll A. Re-roll B.」是同一句
    text = re.sub(r'\.\s+Or:', '; or:', text)
    # 「每場一次」之類的：使用者 2026-11-15「一定都開的 沒人省這種東西」→ 預設算，標出來（計算時提醒可以省）
    once = bool(re.search(r'once per battle', name + ' ' + clean(desc), re.I))
    for sent in re.split(r'(?<=[a-z\]\)0-9”"])\.\s+', text):
        sent = sent.strip().rstrip('.')
        if not sent or SKIP.search(sent):
            continue
        leading = bool(LEAD.match(sent))
        body = LEAD.sub('', sent)
        body = re.split(r'\s+and,\s+if\s+', body)[0]            # 「…，而且如果…可以改成…」只取前半
        low = body.lower()
        t = dict(name=name, side='att', scope='all', effs=[], tkw=[], tkw_not=[], weapon=None, cond=None, leading=leading, on=True, situ=False, unitwide=False)
        rest = low
        nb = re.sub(r'^if you do,\s*', '', body, flags=re.I)
        na, nd = NEWA.match(nb), NEWD.match(nb)
        if na or nd or COVER.match(body):
            situ = nb != body
            if na:
                t['scope'] = (na['scope'] or 'all').strip().lower()
                t['unitwide'] = na['who'].lower() == 'unit'
                r1 = na['rest'].split('; or:')[0]
                r1, cnd = re.subn(r'\bif\b.*$', '', r1, flags=re.I)
                t['effs'] = effects_new(r1.lower(), r1, 'att')
                tg, pre = na['tgt'] or '', (na['pre'] or '')
                if re.search(r'made a charge move', pre, re.I):
                    t['cond'], pre = 'charge', ''
                if re.search(r'with a T greater than this (?:unit|model)[’\']s T', tg):
                    t['cond'] = 't_gt_t'
                    tg = re.sub(r'with a T greater than this (?:unit|model)[’\']s T', '', tg)
                mx = re.search(r'\(excluding ' + SL + r' units?\s*\)', tg)
                if mx:
                    t['tkw_not'] = [k.strip() for k in mx[1].split(' / ')]
                    tg = tg.replace(mx[0], '')
                mk = re.search(r'target an? ' + SL + r' unit', tg)
                if mk:
                    t['tkw'] = [k.strip() for k in mk[1].split(' / ')]
                    tg = tg.replace(mk[0], '')
                situ = situ or bool(cnd) or bool(pre.strip()) or bool(re.sub(r'that target|that|a unit|\s', '', tg))
            elif nd:
                t['side'], t['scope'] = 'def', (nd['scope'] or 'all').strip().lower()
                t['unitwide'] = (nd['who'] or '').lower() == 'unit'
                t['effs'] = effects_new(nd['rest'].lower(), nd['rest'], 'def')
                if nd['cond']:
                    t['cond'] = 's_gt_t'
            else:
                t['side'], t['effs'] = 'def', [('cover', 1)]
            if not t['effs']:
                continue
            t['situ'], t['on'], t['once'] = situ, not situ, once
            t['label'] = label(t)
            out.append(t)
            continue
        m = A1.match(body)
        if m:
            t['scope'] = (m[1] or 'all').strip().lower() or 'all'
            rest = m[2]
            mw = re.match(r"\s*with (?:its|this model[’']s|their) (.+?)(?: that targets|,|$)", rest, re.I)
            if mw:
                t['weapon'] = mw[1].strip().lower()
            t['effs'] = effects(rest.lower(), rest, 'att')
        elif A2.match(body):
            m = A2.match(body)
            t['scope'] = (m[1] or 'all').strip().lower() or 'all'
            t['effs'] = [('kw', k.upper()) for k in re.findall(r'\[([^\]]+)\]', body)]
            rest = ''
        elif D1.match(body):
            m = D1.match(body)
            t['side'], t['scope'], rest = 'def', (m[1] or 'all').strip().lower() or 'all', m[2]
            t['effs'] = effects(rest.lower(), rest, 'def')
        elif D2.match(body):
            t['side'], t['effs'], rest = 'def', [('inv', int(D2.match(body)[1]))], ''
        elif D3.match(body):
            m = D3.match(body)
            t['side'], t['effs'], rest = 'def', [('fnp', int(m[1]))], m[2]
        else:
            continue
        if not t['effs']:
            continue
        mk = TKW.search(rest) if t['side'] == 'att' else None
        if mk:
            t['tkw'] = [k.strip() for k in re.split(r',? (?:or|and) ', mk[1]) if k.strip()]
        mx = EXCL.search(rest) if t['side'] == 'att' else None
        if mx:
            t['tkw_not'] = [k.strip() for k in re.split(r',? (?:or|and) ', mx[1]) if k.strip()]
        r2 = rest.lower()
        for pat, c in ((r"(?:if (?:it|that model|this model|that model[’']s unit|this unit|the bearer) |that )?made a charge move this turn", 'charge'),
                       (r'(?:that targets a unit )?within half range', 'half'), (r'(?:if (?:it|this model|this unit) )?remained stationary(?: this turn)?', 'still'),
                       (r'if the strength characteristic of that attack is greater than (?:the|this unit[’\']s|this model[’\']s|that unit[’\']s) toughness(?: characteristic)?(?: of this unit| of that unit)?', 's_gt_t')):
            if re.search(pat, r2):
                t['cond'] = c
                r2 = re.sub(pat, '', r2)
        t['situ'] = bool(SITU.search(r2))
        t['on'] = not t['situ']
        t['once'] = once
        t['label'] = label(t)
        out.append(t)
    return out
