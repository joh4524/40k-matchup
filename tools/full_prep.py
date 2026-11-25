"""規則完整中文翻譯批次（2026-11-25 使用者：「你把他完整翻譯」）：印出一個陣營要翻的全部條目。
條目：A 軍隊規則、D 分隊規則、S 戰術卡、E 強化、B 資料卡能力（Datasheet／Wargear／Primarch／Psychic）、W 武器名。
跑法：python3 tools/full_prep.py AC            印出全部條目給 Sonnet 讀
      python3 tools/full_prep.py AC 2/3        只印第 2 份（共 3 份，照條目平均切）
      python3 tools/full_prep.py --ids AC [2/3]  只印編號（full_check.py 用）
      python3 tools/full_prep.py --list        每個陣營的條數、英文字數、建議切幾份
結果只放 HP（data/zh_full.json 不進 git、公開版不載入），因為是規則全文。"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, 'tools'))
import engine
import sum_prep

PART_CHARS = int(os.environ.get('FULL_PART', '60000'))   # Haiku 批次用小一點（full-batch 設 FULL_PART）

# 陣營代號 → ~/warhammer-zh/rules-txt 裡的中文規則（社群翻譯，簡體）；沒有的陣營自己翻
ZH_REF = {
    'AC': ['帝皇禁军十一版中文疯医版1.0.txt'],
    'SM': ['星际战士11版中文1.12.txt', '圣血天使11版中文1.02.txt', '黑暗天使11版中文1.04.txt', '太空野狼11版中文1.03.txt', '黑色圣堂CODEX-双子星版 V1.20.txt', '11E-Deathwatch1.0.txt'],
    'CSM': ['混沌星际战士11版中文1.03.txt'],
    'ORK': ['兽人11版中文1.05.txt', '11E欧克蛮人规则V1.10-双子星版.txt'],
    'NEC': ['11版太空死灵规则1.1.txt'],
    'TAU': ['钛帝国11版规则-20260919.txt'],
    'AM': ['星界军11版中文1.02.txt'],
    'AdM': ['机械修会11版中文1.02.txt'],
    'DG': ['死亡守卫11版中文咸鱼罐头版v1.0.3.txt'],
    'EC': ['帝皇之子11版中文1.0.txt'],
    'QI': ['帝国骑士11版中文1.0.txt'],
    'QT': ['混沌骑士11E规则-双子星版V1.0 .txt'],
    'AE': ['艾达灵族11版中文1.3.txt'],
    'DRU': ['黑暗灵族11版中文1.0.txt'],
    'TYR': ['泰伦虫族11版中文1.01.txt'],
    'CD': ['混沌恶魔11E中文1.03.txt'],
}
REF_DIR = os.path.expanduser('~/warhammer-zh/rules-txt')
B_TYPES = ('Datasheet', 'Wargear', 'Primarch', 'Psychic')


def bkey(r):
    """資料卡能力的編號：共用能力用 ability_id，資料卡自己的用 資料卡id.行號（engine._sc_load 也用同一個規則）。"""
    return 'B' + (r['ability_id'] if r.get('ability_id') else r['datasheet_id'] + '.' + r['line'])


def items(fid):
    out = [(i, kind, name, det, text) for i, kind, name, det, text in sum_prep.items(fid)]
    out = [(i, kind, engine.string.capwords(name.lower()) if i[0] == 'S' else name, det, text) for i, kind, name, det, text in out]
    sheets = {r['id']: r['name'] for r in engine.rd('Datasheets') if r['faction_id'] == fid and r.get('virtual', '').lower() != 'true'}
    ab = {r['id']: r for r in engine.rd('Abilities')}
    seen = set()
    for r in engine.rd('Datasheets_abilities'):
        if r['datasheet_id'] not in sheets or r['type'] not in B_TYPES:
            continue
        k = bkey(r)
        if k in seen:
            continue
        seen.add(k)
        a = ab.get(r['ability_id']) or {}
        name = (r['name'] or a.get('name', '')).strip()
        text = engine._sc_txt(r['description'] or a.get('description', ''))
        if name or text:
            out.append((k, '能力', name, sheets[r['datasheet_id']], text))
    wn = {}
    for r in engine.rd('Datasheets_wargear'):
        if r['datasheet_id'] in sheets and r['name'].strip():
            wn.setdefault(engine.norm(r['name']), (r['name'].strip(), sheets[r['datasheet_id']]))
    for k, (name, sheet) in sorted(wn.items()):
        out.append(('W' + k, '武器名', name, sheet, ''))
    return out


def parts(its):
    """照英文字數切成幾份，每份大約 PART_CHARS 字；同一個類別盡量放一起。"""
    tot = sum(len(x[4]) + len(x[2]) + 40 for x in its)
    n = max(1, -(-tot // PART_CHARS))
    out, cur, size = [], [], 0
    for x in its:
        cur.append(x)
        size += len(x[4]) + len(x[2]) + 40
        if size >= tot / n and len(out) < n - 1:
            out.append(cur)
            cur, size = [], 0
    if cur:
        out.append(cur)
    return out


def pick(fid, part):
    its = items(fid)
    if not part:
        return its, 1, 1
    k, n = (int(x) for x in part.split('/'))
    ps = parts(its)
    if n != len(ps):
        sys.exit(f'{fid} 現在要切 {len(ps)} 份，不是 {n} 份')
    return ps[k - 1], k, n



# ── 中英對照（2026-11-25 使用者：「中英文的資料你都有了」「你給自己開 haiku」）──
# 中文規則書裡的資料卡、戰術卡、規則大多在中文名旁邊附大寫英文名（例：「TRAJAAN VALORIS」「SUPERHUMAN FOCUS 1CP」）。
# 用英文名模糊比對找到那一行，把附近幾十行當參考段落，跟英文條目一起交給 Haiku，省掉它自己翻找。
import difflib, re

_REF = {}


def ref_lines(fid):
    if fid not in _REF:
        lines = []
        for f in ZH_REF.get(fid, []):
            try:
                lines += open(os.path.join(REF_DIR, f), encoding='utf-8', errors='ignore').read().split('\n')
            except OSError:
                pass
        anchors = []
        for i, l in enumerate(lines):
            for m in re.finditer(r"[A-Z][A-Z'’\-]+(?:\s+[A-Z][A-Z'’\-]+)*", l):
                if len(m[0]) >= 4:
                    anchors.append((i, re.sub(r'[’\-]', "'", m[0]).replace("'", '').strip()))
        _REF[fid] = (lines, anchors)
    return _REF[fid]


def _key(name):
    n = re.sub(r'\s*\(.*?\)', '', name or '').upper().replace('’', "'").replace('-', ' ')
    return re.sub(r"[^A-Z ]", '', n).strip()


def find_ref(fid, name):
    """英文名 → 中文規則書裡最像的那一行（行號），找不到回 None。"""
    lines, anchors = ref_lines(fid)
    k = _key(name)
    if len(k) < 4:
        return None
    best, bi = 0, None
    for i, a in anchors:
        a2 = re.sub(r"[^A-Z ]", '', a.replace('-', ' '))
        if abs(len(a2) - len(k)) > max(6, len(k) // 2):
            continue
        r = difflib.SequenceMatcher(None, k, a2).ratio()
        if r > best:
            best, bi = r, i
    return bi if best >= 0.82 else None


def ref_block(fid, i, n):
    lines, _ = ref_lines(fid)
    seg = [l.rstrip() for l in lines[max(0, i - 3): i + n]]
    return '\n'.join(l for l in seg if l.strip())


def with_refs(fid, its):
    """每條找參考段落：規則／戰術卡／強化用自己的英文名，資料卡能力和武器名用資料卡名；同一段只印一次。"""
    blocks, tag = {}, {}
    for i, kind, name, det, text in its:
        if kind == '武器名':
            at = find_ref(fid, det)
            if at is not None:
                key = f'W{at}'
                if key not in blocks:
                    lines, _ = ref_lines(fid)
                    rows = [l.strip() for l in lines[at: at + 75] if len(re.findall(r'\d+', l)) >= 4 and re.search(r'[一-鿿]', l)]
                    blocks[key] = '（武器表）\n' + '\n'.join(rows) if rows else ''
                if blocks[key]:
                    tag[i] = key
            continue
        if kind == '能力':
            at = find_ref(fid, det)
            span = 60
        else:
            at = find_ref(fid, name)
            span = 22
            if at is None and det:
                at = find_ref(fid, det)
                span = 70
        if at is not None:
            key = f'R{at}'
            blocks.setdefault(key, ref_block(fid, at, span))
            tag[i] = key
    return blocks, tag


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--list':
        db = engine.DB()
        for f in sorted(db.dets):
            its = items(f)
            print(f, len(its), sum(len(x[4]) for x in its), len(parts(its)), '份', '參考：' + '、'.join(ZH_REF.get(f, ['（無）'])))
    elif a and a[0] == '--ids':
        its, _, _ = pick(a[1], a[2] if len(a) > 2 else '')
        print('\n'.join(x[0] for x in its))
    elif a and a[0] == '--refs':
        print('\n'.join(os.path.join(REF_DIR, x) for x in ZH_REF.get(a[1], [])))
    else:
        withref = '--ref' in a
        a = [x for x in a if x != '--ref']
        its, k, n = pick(a[0], a[1] if len(a) > 1 else '')
        blocks, tag = with_refs(a[0], its) if withref else ({}, {})
        if withref:
            print(f'## 參考段落（中文規則書，簡體；{len(blocks)} 段，{sum(1 for x in its if x[0] in tag)}/{len(its)} 條有對到）\n')
            for key, b in blocks.items():
                if b:
                    print(f'#### {key}\n```\n{b}\n```\n')
            print('## 條目\n')
        for i, kind, name, det, text in its:
            src = ('（資料卡 ' if kind in ('能力', '武器名') else '（分隊 ') + det + '）' if det else ''
            print(f"### {i}｜{kind}｜{name}{src}" + (f"｜參考 {tag[i]}" if i in tag else ('｜參考：沒對到' if withref else '')))
            if text:
                print(text.replace('\n', ' / '))
            print()
