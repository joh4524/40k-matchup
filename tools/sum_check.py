"""檢查 zh_sum/<陣營>.json：每個編號都有、是中文、不超過長度。印 ERROR／WARN，全過印 OK。2026-11-24。
跑法：python3 tools/sum_check.py AC [檔案路徑]"""
import json, os, re, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fid = sys.argv[1]
path = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, 'zh_sum', fid + '.json')
ids = subprocess.run([sys.executable, os.path.join(ROOT, 'tools', 'sum_prep.py'), '--ids', fid], capture_output=True, text=True).stdout.split()
try:
    d = json.load(open(path, encoding='utf-8'))
except Exception as e:
    print('ERROR 讀不到 JSON：', e); print('FAIL'); sys.exit(1)
err = warn = 0
for i in ids:
    v = d.get(i)
    if not isinstance(v, str) or not v.strip():
        print('ERROR 缺', i); err += 1; continue
    w = sum(2 if '⺀' <= c <= '￿' else 1 for c in v)
    if not re.search(r'[一-鿿]', v):
        print('ERROR 不是中文', i, v[:40]); err += 1
    elif w > 140:
        print('ERROR 太長（寬度', w, '> 140）', i, v[:30]); err += 1
    elif re.search(r'[A-Za-z]{3,}(?: [a-z]{2,}){3,}', v):
        print('WARN 有一整句英文', i, v[:40]); warn += 1
extra = [k for k in d if k not in ids]
if extra:
    print('ERROR 多出不存在的編號', extra[:5]); err += 1
print(f'{len(ids)} 條，ERROR {err}，WARN {warn}')
print('OK' if not err else 'FAIL')
