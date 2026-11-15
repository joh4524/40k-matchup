"""官方點數網站（mfm.warhammer-community.com）有英文版和簡體中文版。每個單位在兩個語言的頁面裡帶著同一個編號（UUID），
這支照編號把中文名和英文名對起來，不靠排列順序（兩邊順序有時不一樣，2026-11-15 之前照順序對的版本在機械修會等陣營對錯過）。
寫出：
  data/zh_units.json    中文單位名 → [英文單位名]（engine.py 讀軍表用；同名不同陣營時會有兩個）
  data/zh_wargear.json  點數頁上「每個 ○○ 加幾點」的武器中文名 → 英文名（官方的武器對照只有這幾個）
每對名字都核對人數和點數兩邊一樣，不一樣的會印出來。每頁間隔 1 秒。
用法：python3 update_zh.py [存放網頁的資料夾]   有給資料夾時，裡面已經有的頁面不重抓。跑完重啟服務：systemctl --user restart matchup"""
import json, os, re, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = 'https://mfm.warhammer-community.com'
UUID = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
CACHE = sys.argv[1] if len(sys.argv) > 1 else None
CJK = re.compile(r'[一-鿿]')


def fetch(lang, slug):
    p = os.path.join(CACHE, f'{slug or "index"}_{lang}.html') if CACHE else None
    if p and os.path.exists(p):
        return open(p, encoding='utf-8', errors='ignore').read()
    req = urllib.request.Request(f'{SITE}/{lang}/{slug}'.rstrip('/'), headers={'User-Agent': 'Mozilla/5.0'})
    t = urllib.request.urlopen(req, timeout=30).read().decode('utf-8', 'ignore')
    time.sleep(1)
    if p:
        open(p, 'w', encoding='utf-8').write(t)
    return t


def rows(t):
    """整頁內容放在 self.__next_f.push 裡，一列一個元件。回傳 {列編號: 內容}。"""
    s = ''.join(json.loads(m[1]) for m in re.finditer(r'self\.__next_f\.push\(\[1,("(?:[^"\\]|\\.)*")\]\)', t))
    out = {}
    for m in re.finditer(r'^([0-9a-f]+):(.*)$', s, re.M):
        if m[2][:1] in '[{"':
            try:
                out[m[1]] = json.loads(m[2])
            except ValueError:
                pass
    return out


def strings(node, R, depth=0):
    """元件裡的文字，照順序；遇到 $Lxx 就接到那一列。"""
    if depth > 40:
        return
    if isinstance(node, str):
        m = re.fullmatch(r'\$L?([0-9a-f]+)', node)
        if m and m[1] in R:
            yield from strings(R[m[1]], R, depth + 1)
        elif not node.startswith('$'):
            yield node
    elif isinstance(node, list):
        if len(node) == 4 and node[0] == '$' and isinstance(node[3], dict):
            yield from strings(node[3].get('children'), R, depth + 1)
        else:
            for x in node:
                yield from strings(x, R, depth + 1)


def keyed(node, R, found, depth=0):
    """所有 key 是 UUID 的元件：{key: (className, [文字])}"""
    if depth > 60 or not isinstance(node, list):
        return
    if len(node) == 4 and node[0] == '$' and isinstance(node[3], dict):
        k = node[2]
        if isinstance(k, str) and re.fullmatch(f'{UUID}(-{UUID})?', k) and k not in found:
            found[k] = (node[3].get('className', ''), [x.strip() for x in strings(node, R) if x and x.strip()])
        keyed(node[3].get('children'), R, found, depth + 1)
    else:
        for x in node:
            keyed(x, R, found, depth + 1)


def page(lang, slug):
    R, found = rows(fetch(lang, slug)), {}
    for v in R.values():
        keyed(v, R, found)
    return found


def nums(txt):
    return re.findall(r'\d+', ' '.join(x for x in txt[1:] if 'UNIT' not in x.upper() and '单位' not in x))


slugs = sorted(set(re.findall(r'href="/en/([a-z0-9-]+)"', fetch('en', ''))))
units, wargear, clash, differ, untranslated, per = {}, {}, [], [], [], []
for slug in slugs:
    en, zh = page('en', slug), page('zh', slug)
    n = tot = 0
    for k, (cls, e) in en.items():
        z = zh.get(k, ('', []))[1]
        if not e or not z:
            continue
        if cls.startswith('flex flex-col space-y-1 m-1') and not (len(e) > 1 and re.fullmatch(r'\d+DP', e[1])):
            tot += 1
            if nums(e) != nums(z):
                differ.append(f'{slug} {e[0]}／{z[0]}')
            if not CJK.search(z[0]):
                untranslated.append(f'{slug} {e[0]}')
                continue
            if e[0] not in units.setdefault(z[0], []):
                units[z[0]].append(e[0])
            n += 1
        elif cls == '' and e[0].startswith('per '):
            zw = re.sub(r'^每个\s*', '', z[0])
            if CJK.search(zw):
                wargear[zw] = e[0][4:]
    per.append(f'{slug} {n}/{tot}')
    print(f'{slug}: {tot} 個單位，{n} 個有中文名', flush=True)
clash = [f'{z} → {"／".join(e)}' for z, e in units.items() if len(e) > 1]
json.dump(units, open(os.path.join(HERE, 'data', 'zh_units.json'), 'w'), ensure_ascii=False, indent=0)
json.dump(wargear, open(os.path.join(HERE, 'data', 'zh_wargear.json'), 'w'), ensure_ascii=False, indent=0)
print(f'共 {len(slugs)} 頁，{len(units)} 個中文單位名，{len(wargear)} 個武器名')
print('人數或點數兩邊不一樣：', '；'.join(differ) or '無')
print('同一個中文名對到不只一個英文名（都留著，讀軍表時看陣營挑）：', '；'.join(clash) or '無')
print('中文頁還沒翻的：', '；'.join(untranslated) or '無')
