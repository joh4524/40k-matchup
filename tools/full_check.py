"""檢查規則完整翻譯 zh_full/pending/<陣營>[.份].json：每個編號都有、是中文、英文裡的數字中文裡都有。印 ERROR／WARN，全過印 OK。2026-11-25。
跑法：python3 tools/full_check.py AC 檔案路徑 [2/3]"""
import json, os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'tools'))
sys.path.insert(0, ROOT)
import full_prep

fid, path = sys.argv[1], sys.argv[2]
its, _, _ = full_prep.pick(fid, sys.argv[3] if len(sys.argv) > 3 else '')
CJK = re.compile(r'[一-鿿]')
try:
    d = json.load(open(path, encoding='utf-8'))
except Exception as e:
    print('ERROR 讀不到 JSON：', e); print('FAIL'); sys.exit(1)
err = warn = 0
for i, kind, name, det, text in its:
    v = d.get(i)
    if not isinstance(v, dict):
        print('ERROR 缺', i); err += 1; continue
    n, t, src = v.get('n', ''), v.get('t', ''), v.get('src', '')
    if not isinstance(n, str) or not CJK.search(n):
        print('ERROR 名稱不是中文', i, str(n)[:30]); err += 1
    if src not in ('ref', 'own'):
        print('ERROR src 要是 ref 或 own', i, src); err += 1
    if text.strip():
        if not isinstance(t, str) or not CJK.search(t):
            print('ERROR 缺中文全文', i); err += 1; continue
        miss = sorted(set(re.findall(r'\d+', text)) - set(re.findall(r'\d+', t)), key=int)
        if miss:
            print('ERROR 英文有、中文沒有的數字', i, miss[:6]); err += 1
        if len(t) < len(text) * 0.18:
            print('WARN 中文好像太短（可能漏翻）', i, len(t), '字 vs 英文', len(text)); warn += 1
        if re.search(r'[A-Za-z]{3,}(?: [a-z]{2,}){4,}', t):
            print('WARN 有一整句英文沒翻', i, re.search(r'[A-Za-z]{3,}(?: [a-z]{2,}){4,}', t)[0][:40]); warn += 1
    elif t:
        print('ERROR 這條沒有原文，不要寫 t', i); err += 1
ids = {x[0] for x in its}
extra = [k for k in d if k not in ids]
if extra:
    print('ERROR 多出不存在的編號', extra[:5]); err += 1
print(f'{len(its)} 條，ref {sum(1 for x in d.values() if isinstance(x, dict) and x.get("src") == "ref")}，ERROR {err}，WARN {warn}')
print('OK' if not err else 'FAIL')
