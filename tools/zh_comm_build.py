#!/usr/bin/env python3
"""黑圖書館（中文軍表 App）用的社群譯名 → 英文對照（2026-11-27，使用者：「把黑圖書館的表加在網頁」「1234都開始」）。
黑圖書館的單位、武器名跟 ~/warhammer-zh/rules-txt 的社群中文規則書同一套，不是 GW 官方中文（data/zh_units.json）。
社群規則書每張資料卡：「中文名   N 分」下一行是英文名；武器表只有中文名＋數值 → 用數值對 Wahapedia 同一張資料卡的武器。
輸出 data/zh_comm.json（只有名字對名字，沒有規則內文）：
  {"units": {中文: [英文資料卡名]}, "weap": {英文資料卡名: {中文武器名: 英文武器名}}}
用法：python3 tools/zh_comm_build.py [-v]
"""
import difflib, glob, json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import engine

SRC = os.path.expanduser('~/warhammer-zh/rules-txt')
OUT = os.path.join(ROOT, 'data', 'zh_comm.json')
V = '-v' in sys.argv
HEADER = re.compile(r'^\s*([一-鿿][^\d\s]*(?: [^\d\s]+)*?)\s{2,}(?:\d+ ?(?:名|个)?模型\s*)?(\d+) ?分\s*$')
ROW = re.compile(r'^\s*(\S.*?)\s{2,}(近战|\d+"?|N/A)\s+(\S+)\s+(\d\+|N/A|-)\s+(\S+)\s+(-?\d+|0)\s+(\S+)(?:\s{2,}(.*))?$')


def nstat(x):
    return re.sub(r'["\s+]', '', str(x)).lower().replace('–', '-').replace('n/a', 'na')


def find_sheet(db, en):
    s = db.find(en, None)
    if s:
        return s
    near = difflib.get_close_matches(engine.norm(en), db.allnames, 1, 0.88)
    if near:
        return db.find(near[0], None)
    pre = [n for n in db.allnames if n.startswith(engine.norm(en) + ' ')]   # LORD DISCORDANT → Lord Discordant on Helstalker
    return db.find(pre[0], None) if len(pre) == 1 else None


ENG = re.compile(r"^[A-Za-z][A-Za-z0-9 ,'’&()\-]+$")
ZHN = re.compile(r'^[\u4e00-\u9fff][\u4e00-\u9fff·・\-（）()A-Za-z0-9 ]{0,24}$')
ROW2 = re.compile(r'^(\S.*?)\s+(近战|\d+"?|N/A)\s+(D?\d+(?:D\d+)?(?:\+\d+)?|D\d+|\d+)\s+(\d\+|N/A|-)\s+(\d+)\s+(-?\d+|0)\s+(D?\d+(?:\+\d+)?|D\d+)\b')


KW_WORDS = {'反步兵', '速射', '致命一击', '爆炸', '手枪', '热熔', '重型', '突击', '持续命中', '毁灭伤害', '精准', '忽视掩体', '喷射', '双联', '间接火力', '危险', '反载具', '反巨兽', '额外攻击', '骑枪', '无', '技能'}


def heads_of(L, db):
    """找資料卡標題：一行中文名（後面可能接分數），下面 1–4 個非空行內有一行英文、而且對得到 Wahapedia 資料卡。"""
    out = []
    for i, l in enumerate(L):
        s = re.sub(r'\s{2,}(?:\d+ ?(?:名|个)?模型\s*)?\d+ ?分\s*$', '', l.strip())
        s = re.sub(r'\s{2,}.*$', '', s)
        if not ZHN.match(s) or len(s) < 2:
            continue
        seen = 0
        for j in range(i + 1, min(i + 8, len(L))):
            e = L[j].strip()
            if not e:
                continue
            if re.fullmatch(r'[\d\s+/模型分名个]+', e):          # 「6 模型 170 分」「3+95/180」這種分數行跳過
                continue
            seen += 1
            e = re.sub(r'\s{2,}.*$', '', e)
            if ENG.match(e) and len(e) > 3:
                sh = find_sheet(db, e)
                if sh:
                    out.append((i, s.replace(' ', ''), sh))
                break
            if seen >= 2:
                break
    return out


def main():
    db = engine.DB()
    units, weap, per, alias = {}, {}, {}, {}
    det_hdr = []
    rows = mapped = 0
    for f in sorted(glob.glob(os.path.join(SRC, '*.txt'))):
        L = open(f, encoding='utf-8').read().split('\n')
        heads = heads_of(L, db)
        per[os.path.basename(f)] = len(heads)
        # 分隊名：「万古长战老兵 2DP」或「诅咒军团」下一行「2DP，肃清敌人」。官方中文沒有的分隊裡，同陣營、同 DP 只剩一個的才對
        facs = {}
        for _, _, sh in heads:
            facs[sh['faction']] = facs.get(sh['faction'], 0) + 1
        fid = max(facs, key=facs.get) if facs else None
        if fid:
            for i, l in enumerate(L):
                m = re.match(r'^\s*([\u4e00-\u9fff][\u4e00-\u9fff·]{1,15})\s*(?:(\d)\s*DP)?\s*$', l)
                if not m:
                    continue
                dp = m[2]
                if not dp:
                    nxt = next((x.strip() for x in L[i + 1:i + 4] if x.strip()), '')
                    m2 = re.match(r'^(\d)\s*DP', nxt)
                    if not m2:
                        continue
                    dp = m2[1]
                det_hdr.append((fid, m[1], dp))
        for k, (i, zh, sh) in enumerate(heads):
            lst = units.setdefault(zh, [])
            if sh['name'] not in lst:
                lst.append(sh['name'])
            end = heads[k + 1][0] if k + 1 < len(heads) else min(len(L), i + 200)
            # 模型名（「传送霸主-40mm」）：只有一種模型的資料卡，黑圖書館常直接用模型名當單位名
            mods = list(dict.fromkeys(m[1] for l in L[i:end] for m in [re.match(r'^\s*([\u4e00-\u9fff][\u4e00-\u9fff·]*)\s*-\s*\d+mm', l)] if m))
            if len(mods) == 1 and mods[0] != zh:
                alias.setdefault(mods[0], set()).add(sh['name'])
            wm = weap.setdefault(sh['name'], {})
            melee, last = None, ''
            for l in L[i:end]:
                if '射击武器' in l:
                    melee = False; continue
                if '近战武器' in l:
                    melee = True; continue
                if melee is None or '武器名' in l:
                    continue
                st = l.strip()
                r = ROW2.match(st)
                if not r:
                    m0 = re.match(r'^([\u4e00-\u9fff][^\s（(]*)', st)
                    if m0 and not re.search(r'选择|属性|武器技能', st):
                        last = m0[1]
                    continue
                name = re.sub(r'\s+', '', r[1])
                prof = re.match(r'^[（(]', name)
                base = last if prof else re.sub(r'[（(].*$', '', name)
                base = re.sub(r'[-–—].*$', '', base).strip()
                if not prof:
                    last = base
                if not base or not re.search(r'[\u4e00-\u9fff]', base) or len(base) > 14 or base in KW_WORDS:
                    continue
                rows += 1
                key = [nstat(x) for x in (r[3], r[4], r[5], r[6], r[7])]
                isml = r[2] == '近战' or melee
                hits = {re.sub(r'\s*[-–—]\s.*$', '', w['name']).strip() for w in sh['weapons']
                        if w['melee'] == isml and [nstat(w[x]) for x in ('A', 'skill', 'S', 'AP', 'D')] == key}
                if len(hits) == 1:
                    wm.setdefault(base, hits.pop()); mapped += 1
                elif V:
                    print('  武器沒對上', sh['name'], base, key, sorted(hits)[:3])
            if not wm:
                weap.pop(sh['name'], None)
    # 同一個中文武器名在很多資料卡都對到同一把英文：當全域對照；單張資料卡對到少數派的（多半是表格錯位）丟掉
    from collections import Counter
    cnt = {}
    for sh, wm in weap.items():
        for zh, en in wm.items():
            cnt.setdefault(zh, Counter())[engine.norm(en)] += 1
    glob_w = {}
    for zh, c in cnt.items():
        (top, n), tot = c.most_common(1)[0], sum(c.values())
        if tot >= 2 and n / tot >= 0.7:
            glob_w[zh] = next(en for wm in weap.values() for z, en in wm.items() if z == zh and engine.norm(en) == top)
        if tot >= 3 and n / tot >= 0.7:
            for wm in weap.values():
                if zh in wm and engine.norm(wm[zh]) != top:
                    del wm[zh]
    # 規則完整翻譯（data/zh_full.json，HP 才有；譯名照社群規則書挑的）：武器、分隊、強化的名字，繁體轉簡體
    fw, det, enh = {}, {}, {}
    try:
        sys.path.insert(0, os.path.expanduser('~/warhammer-zh/lib'))
        from opencc import OpenCC
        t2s = OpenCC('t2s').convert
        full = json.load(open(os.path.join(ROOT, 'data', 'zh_full.json'), encoding='utf-8'))
    except Exception as e:
        print('沒有 zh_full.json 或 opencc，跳過', e); full = {}
    dn = {r['id']: r['name'] for r in engine.rd_safe('Detachments')}
    en_ = {r['id']: r['name'] for r in engine.rd_safe('Enhancements')}
    for k, v in full.items():
        zh = t2s(re.sub(r'（.*?）|\(.*?\)', '', v.get('n', ''))).strip()
        if not zh:
            continue
        if k[0] == 'W':
            lst = fw.setdefault(re.sub(r'\s+', '', zh), [])
            if k[1:] not in lst:
                lst.append(k[1:])
        elif k[0] == 'D' and k[1:] in dn:
            det.setdefault(zh, dn[k[1:]])
        elif k[0] == 'E' and k[1:] in en_:
            enh.setdefault(zh, en_[k[1:]])
    try:
        official = set(json.load(open(os.path.join(ROOT, 'data', 'zh_dets.json'), encoding='utf-8')).get('det', {}).values())
    except OSError:
        official = set()
    drows = [r for r in engine.rd_safe('Detachments') if r.get('name')]
    taken = set(det.values()) | official
    for fid, zh, dp in det_hdr:
        if zh in det:
            continue
        c = [r['name'] for r in drows if r['faction_id'] == fid and r.get('dp') == dp and r['name'] not in taken]
        if len(c) == 1:
            det[zh] = c[0]; taken.add(c[0])
    for zh, ens in alias.items():
        if zh not in units and len(ens) == 1:
            units[zh] = sorted(ens)
    json.dump(dict(src='~/warhammer-zh/rules-txt 社群中文規則書（只取名字）', units=units, weap=weap, gw=glob_w, fw=fw, det=det, enh=enh),
              open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
    print(f"翻譯批次來的：武器 {len(fw)}、分隊 {len(det)}、強化 {len(enh)}；全域武器名 {len(glob_w)}；單位 {len(units)} 個中文名；武器列 {rows}，對上 {mapped}，武器名 {sum(map(len, weap.values()))}")
    for k, v in per.items():
        print(f'  {v:4d} 張  {k}')

main()
