from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

LD = ['LEGIONES DAEMONICA']

ARMY = {
    # 000008359 Dark Pacts 寫在 CSM.py（混沌星際戰士的軍隊規則）
    # The Shadow of Chaos / Daemonic Pact: 只有 Battle-shock／編軍，不影響傷害
}

DET = {
    # Daemonic Incursion（Warp Rifts）
    '000000779': [
        # DAEMONIC INVULNERABILITY（重骰無敵 1）程式無對應標記，略過
        R('Draught of Terror', '戰略', [
            T('Draught of Terror', 'att', [('ap', 1)]),
            T('Draught of Terror (re-roll wound)', 'att', [('rr_wound', 'all')], on=False, why='只打 Battle-shocked 的目標'),
        ], cp='1', need=LD),
    ],
    # Unnatural Energies：只有戰術動作
    '000000953': [
        R('Incorporeal Terrors', '戰略', [T('Incorporeal Terrors', 'def', [('hit', -1)], scope='ranged')], cp='1', need=LD),
        # PARTING BLOWS（死後再打）程式不算
    ],
    '000000954': [],   # Infernal Onslaught：只有移動／艙門／士氣
    '000000955': [
        R('Foul Resilience', '戰略', [T('Foul Resilience', 'def', [('fnp', 5)])], cp='1', need=LD + ['NURGLE'], names_not=['Nurglings']),
    ],
    '000000956': [
        R('Seductive Whispers', '戰略', [T('Seductive Whispers', 'def', [('hit', -1)], scope='melee')], cp='1', need=LD + ['SLAANESH']),
    ],
    '000000957': [
        R('Living Flame', '規則', [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', why='目標要在任一友軍單位的 Engagement Range 內')],
          need=LD + ['TZEENTCH'], on=False),
        # FATE SYPHONING（重骰 Save 1）、FICKLE BLESSINGS（Pistol/Hazardous）略過
    ],
    '000000997': [
        R('Seductive Gambit', '規則', [
            T('Seductive Gambit (hit)', 'att', [('rr_hit', 'all'), ('rr_wound', '1')], scope='melee', why='衝鋒結束後宣告；失去 Fights First'),
        ], need=LD + ['SLAANESH'], on=False),
        R('Archagonists', '戰略', [T('Archagonists', 'att', [('wound', 1)])], cp='2', need=LD + ['SLAANESH']),
        R('Overwhelming Excess', '戰略', [T('Overwhelming Excess', 'def', [('hit', -1)])], cp='1', need=LD + ['SLAANESH']),
        R('Cavalcade of Blades', '戰略', [T('Cavalcade of Blades', 'att', [('mw', 3)], scope='melee', why='只算 MONSTER：6D6 每個 4+ 一致命傷；非 MONSTER 看模型數，未計')],
          cp='1', need=LD + ['SLAANESH', 'MONSTER']),
        R('Rapturous Agony', '戰略', [T('Rapturous Agony', 'def', [('wound', -1)], cond='s_gt_t')], cp='1', need=LD + ['SLAANESH'], need_not=MV),
    ],
    '000000998': [
        # Fates in Flux（Flux token 重骰，數量有限）程式無法算，略過
        R('Pyrogenesis', '戰略', [
            T('Pyrogenesis +2 S', 'att', [('strength', 2)], pick='pyro'),
            T('Pyrogenesis +3 S, AP1 (Flux)', 'att', [('strength', 3), ('ap', 1)], pick='pyro', on=False, why='要花 1 個 Flux token'),
        ], cp='1', need=LD + ['TZEENTCH']),
        # FLICKERING REALITY、FICKLEFIRE 略過
    ],
    '000000999': [
        R('Skulls Beget Blood', '戰略', [T('Skulls Beget Blood', 'att', [('mw', 3)], scope='ranged', why='6D6 每個 4+ 一致命傷；目標 8" 內且可見；限 INFANTRY／MOUNTED')],
          cp='1', need=LD + ['KHORNE']),
        # SHEATHED IN BRASS（Save 改成 3+，不是 +1）、WRATH UNDENIABLE 略過
    ],
    '000001000': [
        R('Seeping Virulence', '戰略', [T('Seeping Virulence', 'att', [('crit_hit', 5)])], cp='1', need=LD + ['NURGLE']),
        R('Fever Visions', '戰略', [T('Fever Visions', 'att', [('hit', 1)])], cp='1', need=LD + ['NURGLE']),
    ],
    '000001027': [
        R('Penumbral Puppetry', '規則', [
            T('Stealth', 'def', [('cover', 1)], scope='ranged'),
            T('Penumbral Puppetry', 'def', [('hit', -1)], scope='melee'),
        ], need=['SHADOW LEGION', 'TZEENTCH'], on=True),
        R('Gloam Rot', '規則', [T('Gloam Rot', 'def', [('wound', -1)], cond='s_gt_t')], need=['SHADOW LEGION', 'NURGLE'], on=True),
        R('Disciples of Be’lakor', '規則', [
            T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], pick='pact', why='Dark Pacts；Ld 失敗受 D3 致命傷（未計）'),
            T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], pick='pact', why='同上'),
        ], need=['SHADOW LEGION', 'UNDIVIDED'], on=False),
        R('Encroaching Darkness', '戰略', [T('Encroaching Darkness', 'att', [('kw', 'IGNORES COVER')], why='只限本回合從 Reserves 抵達的單位')], cp='1', need=['SHADOW LEGION']),
        R('Channelled Wrath', '戰略', [
            T('Channelled Wrath', 'att', [('kw', 'LANCE')], scope='melee'),
            T('Channelled Wrath (Khorne)', 'att', [('ap', 1)], scope='melee', on=False, why='只限 KHORNE 單位'),
        ], cp='1', need=['SHADOW LEGION']),
    ],
    '000001175': [],   # Cavalcade of Chaos：只有移動／撤退／預備隊
    '000001176': [
        R('Call to Murder', '戰略', [T('Call to Murder', 'att', [('attacks', 1)], scope='melee', cond='charge')], cp='1',
          need=LD + ['KHORNE', 'CHARACTER'], need_not=['MONSTER']),
        R('Skirling Magicks', '戰略', [T('Skirling Magicks', 'att', [('kw', 'LETHAL HITS')], scope='ranged')], cp='1',
          need=LD + ['TZEENTCH', 'CHARACTER'], need_not=['MONSTER']),
        R('Bilious Blessing', '戰略', [T('Bilious Blessing', 'att', [('mw', 3.5)], scope='ranged', why='7D6 每個 4+ 一致命傷；目標 8" 內且可見')], cp='1',
          need=LD + ['NURGLE', 'CHARACTER'], need_not=['MONSTER']),
    ],
    '000001177': [
        R('Incorporeal Entities', '戰略', [T('Incorporeal Entities', 'def', [('wound', -1)], scope='ranged', cond='s_gt_t')], cp='1', need=LD + ['BATTLELINE']),
        # Shudderblink：Assault／衝鋒資格，不影響傷害
    ],
}

ENH = {
    'A’rgath, the King of Blades': [
        T('A’rgath', 'att', [('attacks', 1), ('strength', 1)], scope='melee', on=True, unitwide=False),
        T('A’rgath (Shadow of Chaos)', 'att', [('attacks', 1), ('strength', 1)], scope='melee', on=False, unitwide=False, why='在 Shadow of Chaos 內總共 +2（此為額外 +1）'),
    ],
    'The Endless Gift': [T('The Endless Gift', 'def', [('fnp', 5)], on=True, unitwide=False)],
    'The Everstave': [
        T('The Everstave', 'att', [('strength', 1)], scope='ranged', on=True, unitwide=False),
        T('The Everstave (Shadow of Chaos)', 'att', [('strength', 1)], scope='ranged', on=False, unitwide=False, why='在 Shadow of Chaos 內總共 +2（此為額外 +1）'),
    ],
    'Fulgurating Presence': [T('Fulgurating Presence', 'def', [('hit', -1)], on=True, unitwide=False)],
    'Fatal Caress': [T('Fatal Caress', 'att', [('crit_wound', 5)], scope='melee', on=True, unitwide=False)],
    'False Majesty (Aura)': [T('False Majesty', 'att', [('wound', 1)], scope='melee', on=True, why='光環：6" 內非 MONSTER 的 Slaanesh 單位')],
    'Dreaming Crown (Aura)': [T('Dreaming Crown', 'att', [('hit', 1)], scope='melee', on=True, why='光環：6" 內非 MONSTER 的 Slaanesh 單位')],
    'Neverblade': [T('Neverblade', 'att', [('strength', 2), ('attacks', 1), ('ap', 1), ('hit', 1)], scope='melee', on=True, unitwide=False)],
    'Slaughterthirst (Aura)': [T('Slaughterthirst', 'att', [('kw', 'LANCE')], on=True, why='光環：6" 內非 MONSTER 的 Khorne 單位')],
    'Fury’s Cage': [T('Fury’s Cage', 'att', [('rr_hit', 'all'), ('rr_wound', 'all')], scope='melee', on=False, unitwide=False, why='每次打架自選使用，自己受 D3+1 致命傷（未計）')],
    'Font of Spores (Aura)': [T('Font of Spores', 'att', [('ap', 1)], on=True, why='光環：6" 內的 Nurgle 單位')],
    'Maggot Maws': [T('Maggot Maws', 'att', [('mw', 1.33)], scope='ranged', on=False, unitwide=False, why='射擊階段選 6" 內敵人，D6 3+ 造 D3 致命傷（2×2/3）')],
    'Malice Made Manifest': [T('Malice Made Manifest', 'att', [('mw', 1.83)], scope='melee', on=False, unitwide=False, why='打架開始時對交戰的敵人：2-5 → D3、6 → 3 致命傷')],
    'Bane-Forged Weapons': [T('Bane-Forged Weapons', 'att', [('strength', 1)], on=True)],
}
