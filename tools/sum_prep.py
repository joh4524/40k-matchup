"""規則中文摘要批次（2026-11-24）：印出一個陣營要寫摘要的全部條目（軍隊規則、分隊規則、戰術卡、強化），每條「編號|類別|名字|英文原文」。
跑法：python3 tools/sum_prep.py AC        印出來給 Sonnet 讀
      python3 tools/sum_prep.py --ids AC  只印編號（sum_check.py 用）
      python3 tools/sum_prep.py --list    列出所有陣營代號和條數"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import engine


def items(fid):
    db = engine.DB()
    dets = {d['id']: d['name'] for d in db.dets.get(fid, [])}
    out = []
    for r in engine.rd('Abilities'):
        if r['faction_id'] == fid:
            out.append(('A' + r['id'], '軍隊規則', r['name'], '', engine._sc_txt(r['description'])))
    for r in engine.rd_safe('Detachment_abilities'):
        if r.get('detachment_id') in dets:
            out.append(('D' + r['id'], '分隊規則', r['name'], dets[r['detachment_id']], engine._sc_txt(r.get('description'))))
    for r in engine.rd_safe('Stratagems'):
        if r.get('detachment_id') in dets and 'boarding' not in (r.get('type') or '').lower():
            out.append(('S' + r['id'], '戰術卡 ' + (r.get('cp_cost') or '') + 'CP', r['name'].title(), dets[r['detachment_id']], engine._sc_txt(r.get('description'))))
    for r in engine.rd_safe('Enhancements'):
        if r.get('faction_id') == fid:
            out.append(('E' + r['id'], '強化', r['name'], r.get('detachment') or '', engine._sc_txt(r.get('description'))))
    return out


if __name__ == '__main__':
    a = sys.argv[1:]
    if a and a[0] == '--list':
        db = engine.DB()
        for f in sorted(db.dets):
            print(f, len(items(f)))
    elif a and a[0] == '--ids':
        print('\n'.join(x[0] for x in items(a[1])))
    else:
        for i, kind, name, det, text in items(a[0]):
            print(f"### {i}｜{kind}｜{name}" + (f"（分隊 {det}）" if det else ''))
            print(text.replace('\n', ' / '))
            print()
