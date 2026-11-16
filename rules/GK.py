from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

ARMY = {
    '000010345': dict(name='Gate of Infinity', rules=[]),   # 只有預備隊移動，不影響傷害
}
DET = {
    '000000943': [   # Void Purge Force
        R('SANCTIFIED SLAUGHTER', '戰略', [T('Sanctified Slaughter', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee', cond='charge',
            why='本回合衝鋒過；已有 Sustained Hits 的武器改為 5+ 爆擊，這裡沒算')], cp='1'),
    ],
    '000000944': [   # Baneslayer Strike
        R('ARMOURED AEGIS', '戰略', [T('Armoured Aegis', 'def', [('fnp', 4)], why='只給 CHARACTER 模型')], cp='1', model_kw=['CHARACTER']),
        R('PSYBOLT AMMUNITION', '戰略', [T('Psybolt Ammunition', 'att', [('ap', 1)], scope='ranged', weapon='storm bolter')], cp='1'),
    ],
    '000000992': [   # Warpbane Task Force
        R('Hallowed Ground', '規則', [T('Hallowed Ground', 'att', [('rr_hit', '1')])], on=True,
          note='遠程需目標可見；全軍重骰命中 1'),
        R('Hallowed Ground (Purifier)', '規則', [T('Hallowed Ground', 'att', [('rr_hit', 'all')])], on=True, need=['PURIFIER SQUAD'],
          note='Purifier 可重骰全部命中'),
        R('Hallowed Ground (in zone)', '規則', [T('Hallowed Ground', 'att', [('rr_hit', 'all')], why='整隊都要在己方 Hallowed Ground 內')], on=False),
        R('AEGIS ETERNAL', '戰略', [T('Aegis Eternal', 'def', [('inv', 4)], scope='ranged', why='只有整個在 Hallowed Ground 內的模型')], cp='1', need=['INFANTRY']),
        R('SANCTIFIED KILL ZONE', '戰略', [T('Sanctified Kill Zone', 'att', [('rr_wound', '1')], why='整隊要在 Hallowed Ground 內')], cp='1'),
        R('SANCTIFIED KILL ZONE (Purifier)', '戰略', [T('Sanctified Kill Zone', 'att', [('rr_wound', 'all')], why='整隊要在 Hallowed Ground 內')], cp='1', need=['PURIFIER SQUAD']),
    ],
    '000001081': [   # Brotherhood Strike
        R('Fury of Titan', '規則', [T('Fury of Titan', 'att', [('rr_hit', '1'), ('rr_wound', '1')], why='本回合以 Deep Strike 降臨的單位')], on=False),
        R('PURGATION PATTERN', '戰略', [T('Purgation Pattern', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', why='本回合 Deep Strike 降臨的單位')], cp='1'),
        R('SHINING VEIL', '戰略', [T('Shining Veil', 'def', [('cover', 1)], scope='ranged', why='Stealth')], cp='1'),
        R('TRUESILVER CHANNELLING', '戰略', [T('Truesilver Channelling', 'att', [('kw', 'DEVASTATING WOUNDS')], scope='melee', wkw='PSYCHIC')], cp='2', need=['INFANTRY']),
    ],
    '000001082': [   # Hallowed Conclave
        R('GIANTS OF THE BATTLEFIELD', '戰略', [T('Giants of the Battlefield', 'att', [('attacks', 1)], scope='melee')], cp='1', need=['TERMINATOR']),
        R('POINT-BLANK PURGATION', '戰略', [T('Point-Blank Purgation', 'att', [('kw', 'TWIN-LINKED')], scope='ranged', weapon='storm bolter')], cp='1', need=['INFANTRY']),
        R('SHINING RESOLVE', '戰略', [T('Shining Resolve', 'def', [('wound', -1)], scope='ranged', cond='s_gt_t')], cp='1', need=['INFANTRY']),
    ],
    '000001083': [   # Banishers
        R('Channelled Force', '規則', [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee', wkw='PSYCHIC', pick='channel', why='需通過 Leadership 測試'),
                                     T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='melee', wkw='PSYCHIC', pick='channel', why='需通過 Leadership 測試')], on=False,
          note='開戰時 Leadership 測試通過才二選一；只限 Psychic 近戰武器'),
        R('WARDING CHANT', '戰略', [T('Warding Chant', 'def', [('fnp', 5)], why='只對未修正傷害為 1 的攻擊有效，這裡對全部攻擊算，會高估')], cp='1', need=['PSYKER']),
        R('CHAOS BANE', '戰略', [T('Chaos Bane', 'att', [('kw', 'ANTI-CHAOS 4+')], scope='ranged')], cp='1', need=['PSYKER']),
    ],
    '000001084': [   # Sanctic Spearhead
        R('ABOMINUS-CLASS TARGETS', '戰略', [T('Abominus-Class Targets', 'att', [('wound', 1)], tkw=['MONSTER', 'VEHICLE'])], cp='1'),
    ],
    '000001085': [   # Augurium Task Force
        R('AGGRESSIVE ANTICIPATION', '戰略', [T('Aggressive Anticipation', 'att', [('rr_hit', 'all')])], cp='1', need=['PSYKER']),
        R('APPOINTED HOUR', '戰略', [T('Appointed Hour', 'att', [('crit_hit', 5)])], cp='1', need=['PSYKER']),
        R('FOREWARNED EVASION', '戰略', [T('Forewarned Evasion', 'def', [('hit', -1)])], cp='1', need=['WALKER']),
    ],
    '000001216': [   # Argent Assault
        R('Dauntless Champions', '規則', [T('Dauntless Champions', 'att', [('wound', 1)], scope='melee', why='只有武器 S 低於目標 T 時才有效')], on=False, need=['PALADIN SQUAD']),
    ],
    '000001217': [   # Fires of Purgation
        R('FOCUSED IMMOLATION', '戰略', [T('Focused Immolation', 'att', [('kw', 'DEVASTATING WOUNDS'), ('kw', 'SUSTAINED HITS 1')], scope='ranged', why='只打被選的那一隊')], cp='1', need=['PURGATION SQUAD']),
        R('SPIRITSEAR', '戰略', [T('Spiritsear', 'att', [('mw', 3)], scope='ranged', why='D3+1 致命傷（平均 3）；只打被擊震的敵人')], cp='1', need=['PURGATION SQUAD']),
    ],
    '000001218': [   # Immaterial Interdiction
        R('BLADES FROM THE BEYOND', '戰略', [T('Blades from the Beyond', 'att', [('kw', 'LANCE')], scope='melee', cond='charge')], cp='1', need=['INTERCEPTOR SQUAD']),
    ],
}
ENH = {
    'Shield of Admonishment': [T('Shield of Admonishment', 'def', [('hit', -1)], scope='melee', on=True, unitwide=False)],
    'Phial of the Abyss': [T('Phial of the Abyss', 'def', [('cover', 1)], on=True, why='Stealth')],
    'Sanctic Reaper': [T('Sanctic Reaper', 'att', [('attacks', 3)], scope='melee', on=True, unitwide=False)],
    'Sigil of the Hunt': [T('Sigil of the Hunt', 'att', [('rr_hit', '1')], scope='ranged', on=True)],
    'The Sixty-sixth Seal': [T('The Sixty-sixth Seal', 'att', [('ap', 1)], scope='ranged', on=True)],
    'Pyresoul (Psychic)': [T('Pyresoul', 'att', [('mw', 2)], scope='ranged', on=True, unitwide=False, why='射擊階段開始選一個 24" 內的敵人，D3 致命傷')],
    'Grimoire of Conjunctions': [T('Grimoire of Conjunctions', 'att', [('strength', 4)], scope='melee', on=True, once=True, unitwide=False)],
    'Boons of Deimos': [T('Boons of Deimos', 'att', [('strength', 2)], scope='ranged', on=True)],
    'Astral Overlap': [T('Astral Overlap', 'def', [('cover', 1)], on=True, why='Stealth')],
}
