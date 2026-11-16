from manual import T
from army import R, MV

IK = ['IMPERIAL KNIGHTS']

ARMY = {
    # 000008382 Doctrina Imperatives 寫在 AdM.py
    '000008458': dict(name='Code Chivalric', rules=[
        R('Oath Quality: martial valour', '軍隊規則', [
            T('Martial valour', 'att', [('rr1', 2)], why='選這個 Quality 才有；每次射擊／打架重骰一顆命中、一顆造傷')]),
    ]),
}

DET = {
    # Questor Forgepact
    '000000988': [
        R('Cogbound Alliance (Assisted Targeting)', '規則', [
            T('Assisted Targeting', 'att', [('skill', 1), ('kw', 'HEAVY')], scope='ranged', why='AdMech 單位要在友方 Imperial Knights 6" 內')],
          need=['ADEPTUS MECHANICUS']),
        R('Vengeance of the Machine Cult', '戰略', [
            T('Vengeance', 'att', [('rr_wound', 'all')], why='只打被標記的那一隊')], cp='1', need=['ADEPTUS MECHANICUS']),
    ],
    # Valourstrike Lance
    '000001106': [
        R('Bold Gallantry', '規則', [
            T('Bold Gallantry', 'att', [('kw', 'ASSAULT')], scope='ranged', why='該回合有 Advance 才有')], need=IK),
        R('Vow of Retribution', '戰略', [T('Vow of Retribution', 'att', [('kw', 'LETHAL HITS')], scope='ranged')], cp='1', need=IK),
        R('Run Them Through!', '戰略', [T('Run Them Through!', 'att', [('kw', 'LANCE')], scope='melee')], cp='1', need=IK),
        R('Rotate Ion Shields', '戰略', [T('Rotate Ion Shields', 'def', [('inv', 4)], scope='ranged')], cp='1', need=IK),
        # Thunderstomp: ⚠️ 設定 Feet 武器 Attacks 為 8/12，無對應標記，不算
    ],
    # Gate Warden Lance
    '000001107': [
        R('Dauntless Defenders (Against the Horde)', '規則', [
            T('Against the Horde (ign)', 'att', [('ign', 1)], why='要在防線上'),
            T('Against the Horde (SH1)', 'att', [('kw', 'SUSTAINED HITS 1')], why='要在防線上')], need=IK),
        R('Drive Them Out!', '戰略', [T('Drive Them Out!', 'att', [('crit_hit', 5)], why='只打防線上的敵人')], cp='1', need=IK),
        R('Titanic Bombardment', '戰略', [T('Titanic Bombardment', 'att', [('kw', 'SUSTAINED HITS 2')], scope='ranged', cond='still', why='要在防線上')], cp='1', need=IK + ['TITANIC']),
        R('Steadfast Superiority', '戰略', [T('Steadfast Superiority', 'att', [('rr_hit', 'all')], scope='melee', why='要在防線上')], cp='1', need=IK),
        R('Lancebreaker', '戰略', [T('Lancebreaker', 'def', [('wound', -1)], scope='melee', cond='s_gt_t', why='要在防線上')], cp='1', need=IK),
    ],
    # Questoris Companions
    '000001108': [
        R('Courageous Stand', '戰略', [T('Courageous Stand', 'def', [('fnp', 6)])], cp='1', need=IK + ['TITANIC']),
        R('Titanic Duel', '戰略', [T('Titanic Duel', 'att', [('hit', 1), ('wound', 1)], tkw=['MONSTER', 'TITANIC', 'WALKER'])], cp='1', need=IK + ['TITANIC']),
    ],
    # Spearhead-At-Arms
    '000001109': [
        R("Exemplar's Wisdom", '戰略', [T("Exemplar's Wisdom", 'att', [('ap', 1)], scope='ranged', why='只打被選的那一隊')], cp='1', need=['ARMIGER']),
        R('Thin Their Ranks', '戰略', [T('Thin Their Ranks', 'att', [('kw', 'RAPID FIRE 1')], scope='ranged')], cp='1', need=['ARMIGER']),
        R('Virtue of Courage', '戰略', [T('Virtue of Courage', 'att', [('hit', 1)], scope='melee', why='只打被選的那一隊')], cp='1', need=['ARMIGER']),
        R('Let Duty Be Your Shield', '戰略', [T('Let Duty Be Your Shield', 'def', [('ap', -1)], scope='ranged')], cp='1', need=['ARMIGER']),
    ],
    # Freeblade Company
    '000001145': [
        R('Knights of Legend', '規則', [T('Knights of Legend', 'def', [('fnp', 6)], on=True)], on=True, need=IK),
        R('Strength from Exile', '戰略', [T('Strength from Exile', 'att', [('rr_hit', '1'), ('rr_wound', '1')], why='9" 內沒有其他友方單位')], cp='1', need=IK),
        R('Survivor of Strife', '戰略', [T('Survivor of Strife', 'def', [('wound', -1)], scope='ranged', cond='s_gt_t')], cp='1', need=IK),
    ],
    # Dominus Foebreakers
    '000001219': [
        R('Rain of Devastation', '規則', [T('Rain of Devastation', 'att', [('hit', 1)], why='目標要在地形區域內')], need=IK + ['DOMINUS']),
        R('Foebreaker Firestorm', '戰略', [T('Foebreaker Firestorm', 'att', [('attacks', 1)], scope='ranged', wkw='BLAST', why='要陷入近戰；同時失去 BLAST')], cp='1', need=IK + ['DOMINUS']),
    ],
    # Throne-Bonded Outriders
    '000001167': [
        R('Driven from Their Lairs', '規則', [T('Driven from Their Lairs', 'att', [('kw', 'IGNORES COVER')], scope='ranged', why='要受 Bondsman 影響')], need=['ARMIGER']),
    ],
}

ENH = {
    # Questor Forgepact: Knight of the Opus Machina 效果給附近 AdMech 單位，不是帶它的單位，不算
    # Valourstrike Lance: 四個強化都是給另一個模型，不算
    # Gate Warden Lance
    "Purgation’s Hand": [T("Purgation’s Hand", 'att', [('rr_hit', '1'), ('rr_wound', '1')], scope='melee', unitwide=False, on=False, why='要在防線上')],
    'Augury Halo': [T('Augury Halo', 'att', [('kw', 'IGNORES COVER')], scope='ranged', unitwide=False, on=False, why='要在防線上')],
    # Questoris Companions（每次用掉才算，需 Oath 完成才恢復）
    'Wyrmslayer Divination': [T('Wyrmslayer Divination', 'att', [('rr_hit', 'all')], scope='ranged', unitwide=False, on=False, why='只打會飛的目標；一次性')],
    'Pennant of Silvered Fury': [T('Pennant of Silvered Fury', 'att', [('kw', 'SUSTAINED HITS 2')], scope='melee', unitwide=False, on=False, why='一次性，用掉後要完成 Oath 才恢復')],
    'Crushing Condemnation': [T('Crushing Condemnation', 'att', [('mw', 3)], scope='melee', unitwide=False, on=False, why='擲六顆 D6、4+ 各 1 致命傷（平均 3）；需先消滅敵人；一次性')],
    # Freeblade Company
    'Bringer of Justice': [T('Bringer of Justice', 'att', [('attacks', 2), ('hit', 1)], scope='melee', on=True, unitwide=False)],
    "Hunter’s Eye": [T("Hunter’s Eye", 'att', [('kw', 'IGNORES COVER')], scope='ranged', on=True, unitwide=False)],
    'Sanctuary': [T('Sanctuary', 'def', [('inv', 5)], on=True, unitwide=False)],
    # Dominus Foebreakers: Blessed Plate (+1 T 自己) 沒有對應標記，Archeotech Autoloaders 不算
}
