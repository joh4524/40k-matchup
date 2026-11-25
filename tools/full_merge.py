"""把抽查過的完整翻譯（zh_full/<陣營>.<份>.json，從 pending/ 搬出來的）合併成 data/zh_full.json，給 HP 版列印頁用。2026-11-25。
跑法：python3 tools/full_merge.py
data/zh_full.json 和 zh_full/*.json 都在 .gitignore（規則全文翻譯不放公開網站）。改完要重開 matchup.service 才會讀到新的。"""
import glob, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {}
for f in sorted(glob.glob(os.path.join(ROOT, 'zh_full', '*.json'))):
    for k, v in json.load(open(f, encoding='utf-8')).items():
        if isinstance(v, dict) and v.get('n'):
            out[k] = {x: v[x] for x in ('n', 't', 'src') if v.get(x)}
with open(os.path.join(ROOT, 'data', 'zh_full.json'), 'w', encoding='utf-8') as f:
    json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
print(len(out), '條 →', 'data/zh_full.json')
