"""把抽查過的 zh_sum/<陣營>.json（不含 pending/）合併成 data/zh_sum.json，給 engine.scout 和公開版讀。2026-11-24。
上線流程：sum-batch 寫到 zh_sum/pending/ → 主 bot 抽查、修 → mv 到 zh_sum/ → python3 tools/sum_merge.py → bump.sh → push"""
import glob, json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
out = {}
for f in sorted(glob.glob(os.path.join(ROOT, 'zh_sum', '*.json'))):
    out.update(json.load(open(f, encoding='utf-8')))
json.dump(out, open(os.path.join(ROOT, 'data', 'zh_sum.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
print(len(out), '條')
