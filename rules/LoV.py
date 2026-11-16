from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

HK = ['Kâhl', 'Einhyr Hearthguard', 'Ûthar']

ARMY = {
    '000010432': dict(name='Prioritised Efficiency', rules=[
        R('Hostile Acquisition', '軍隊規則', [T('Hostile Acquisition', 'att', [('hit', 1)], why='只打在目標點範圍內的敵人；YP<7 時生效')], on=False),
        R('Fortify Takeover', '軍隊規則', [T('Fortify Takeover', 'att', [('hit', 1)], why='自己要在你控制的目標點範圍內；YP≥7 時生效'),
                                           T('Fortify Takeover', 'def', [('wound', -1)], cond='s_gt_t', why='YP≥7 時生效')], on=False, need_not=['VEHICLE'],
          note='防守的 -1 造傷不適用 VEHICLE（攻擊 +1 命中適用所有單位，這裡一併排除 VEHICLE 為近似）'),
    ]),
}

DET = {
    # Void Salvagers
    '000000950': [
        # Stalwart Advance：移動；Corridor Covered：Overwatch；Point-Blank Fire：Pistol（不算）；Relic Cypher：艙門
        R('Judged and Punished', '戰略', [T('Judged and Punished', 'att', [('rr_hit', 'all'), ('rr_wound', 'all')],
                                            why='目標需有 Judgement token：1 個才能重骰命中，2 個才能再重骰造傷')], cp='1'),
    ],
    # Hearthfire Strike
    '000000951': [
        R('Weavefield Flare', '戰略', [T('Weavefield Flare', 'def', [('wound', -1)], cond='s_gt_t')], cp='1'),
        R('Pan-Spectral Visualiser', '戰略', [T('Ignores Cover', 'att', [('kw', 'IGNORES COVER')], scope='ranged'),
                                              T('Pan-Spectral Visualiser', 'att', [('ign', 1)], scope='ranged')], cp='1'),
        R('Gravitronic Pulse', '戰略', [T('Gravitronic Pulse', 'def', [('hit', -1)], scope='melee', why='只對衝鋒後接戰的敵方單位有效')], cp='1'),
        # Economy of Aggression：Attacks 變 6 且限定目標在艙門另一側，不確定怎麼表示，不算
    ],
    # Hearthband
    '000001001': [
        R('Methodical Annihilation', '規則', [T('Methodical Annihilation', 'att', [('rr_wound', '1')], why='只打最近的可攻擊目標或已接戰的目標')], on=False),
        R('Methodical Annihilation (AP)', '規則', [T('Methodical Annihilation AP', 'att', [('ap', 1)], why='只打最近的可攻擊目標或已接戰的目標')], names=HK, on=False,
          note='Kâhl／Einhyr Hearthguard／Ûthar the Destined'),
        R('Brëkkeknots', '戰略', [T('Brëkkeknots', 'def', [('inv', 4)])], cp='1', names=HK),
        R('Fury of the Hearth', '戰略', [T('Fury of the Hearth', 'att', [('strength', 1)], scope='ranged'),
                                         T('Fury of the Hearth (1YP)', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', why='要花 1YP')], cp='1', names=['Einhyr Hearthguard']),
        R('Superior Craftsmanship', '戰略', [T('Superior Craftsmanship', 'att', [('dmg', 1)], tkw=MV)], cp='2'),
    ],
    # Needgaârd Oathband
    '000001096': [
        R('Huntr’s Mark', '戰略', [T('Huntr’s Mark', 'att', [('rr_hit', '1'), ('rr_wound', '1')], scope='ranged')], cp='1'),
        R('Ancestral Sentence', '戰略', [T('Ancestral Sentence', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', why='花 3YP 的話是 SUSTAINED HITS 2（未算）')], cp='1'),
        R('Honour of the Hold', '戰略', [T('Honour of the Hold', 'att', [('ap', 1)], scope='melee', why='只打被選的那一隊；花 3YP 的話是 AP+2（未算）')], cp='1'),
        R('Void Hardened', '戰略', [T('Void Hardened', 'def', [('ap', -1)], why='需要軍隊有 Fortify Takeover')], cp='1'),
    ],
    # Persecution Prospect
    '000001097': [
        R('Exposed Flaws', '戰略', [T('Exposed Flaws', 'att', [('rr_wound', 'all')], why='花 2YP 或目標是 assailed 才有效')], cp='1', need=['HERNKYN']),
        R('Ranger Tactics', '戰略', [T('Ranger Tactics', 'att', [('rr_hit', 'all')], why='目標是 assailed 或自己是 HERNKYN 才有效')], cp='1'),
        R('Dispersed Formation', '戰略', [T('Dispersed Formation', 'def', [('cover', 1)], scope='ranged')], cp='1', need=['INFANTRY'],
          note='INFANTRY 或 MOUNTED 單位皆可'),
    ],
    # Dêlve Assault Shift
    '000001098': [
        R('Cyberstimm Infusion', '戰略', [T('Cyberstimm Infusion', 'att', [('rr_wound', '1')], why='花 2YP 的話可重骰全部造傷（未算）')], cp='1', need=['BESERKS']),
        R('Weavewërke Buttress', '戰略', [T('Weavewërke Buttress', 'def', [('wound', -1)], scope='ranged', why='需要軍隊有 Hostile Acquisition')], cp='1', need=['INFANTRY']),
    ],
    # Brandfast Oathband
    '000001099': [
        R('Firebase Control', '規則', [T('Firebase Control', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', why='INFANTRY 要完全在己方 TRANSPORT 6" 內')], need=['INFANTRY'], on=False),
        R('Illuminated Priority', '戰略', [T('Illuminated Priority', 'att', [('rr_hit', '1')], why='只打被選的那一隊')], cp='1', need=['INFANTRY']),
    ],
    # Hearthfyre Arsenal
    '000001100': [
        R('Optimal Application', '規則', [T('Optimal Application', 'att', [('rr_hit', '1')], scope='ranged', why='要花 1YP')],
          names=['Brôkhyr', 'Ironkin Steeljacks', 'Arkanyst'], on=False),
        R('Unwavering Accuracy', '戰略', [T('Unwavering Accuracy', 'att', [('ign', 1)], scope='ranged', why='也可無視 AP 修正，程式只處理命中／造傷')], cp='2', need=['THUNDERKYN']),
        # Wall of Steel／Delayed-Fire Rounds：致命傷看模型數，不算
    ],
    # Mercenary Oathband
    '000001137': [
        # Ruthless Reinvestment 只是切換軍隊規則；Auxiliary Contract 的 PRECISION 不影響傷害
        R('Optimal Expenditure', '戰略', [T('Optimal Expenditure', 'att', [('rr_hit', '1'), ('rr_wound', '1')], scope='melee', why='花 3YP 的話造傷可全部重骰（未算）')], cp='1', need=['INFANTRY']),
        R('Privateer Arsenal', '戰略', [T('Privateer Arsenal', 'att', [('rr_hit', '1'), ('rr_wound', '1')], scope='ranged', why='花 3YP 的話命中可全部重骰（未算）')], cp='1', need=['INFANTRY']),
    ],
    # Armoured Trailblazers
    '000001194': [
        R('Built to Last', '戰略', [T('Built to Last', 'def', [('wound', -1)], scope='ranged', cond='s_gt_t')], cp='1', need=['SAGITAUR']),
        R('Coordinated Crossfire', '戰略', [T('Coordinated Crossfire', 'att', [('rr_hit', '1'), ('rr_wound', '1')], scope='ranged', why='只打被選的那一隊')], cp='1', need=['SAGITAUR']),
    ],
    # Farseekers
    '000001195': [
        R('Eye of the Hunt', '規則', [T('Eye of the Hunt', 'att', [('hit', 1)], scope='ranged', why='目標要在 12" 內')], need=['HERNKYN'], on=False),
        R('No Shot Wasted', '戰略', [T('No Shot Wasted', 'att', [('kw', 'LETHAL HITS')], scope='ranged')], cp='1', need=['HERNKYN']),
        R('Scornful Analysis', '戰略', [T('Scornful Analysis', 'att', [('kw', 'IGNORES COVER')], why='只打被選的那一隊（12" 內可見）')], cp='1'),
    ],
    # Hearthguard Covenant
    '000001196': [
        R('Avatars of the Ancestors', '規則', [T('Avatars of the Ancestors', 'att', [('rr_wound', '1')], scope='ranged', why='目標要在 9" 內')], names=HK, on=False,
          note='Kâhl／Einhyr Champion／Einhyr Hearthguard／Ûthar the Destined'),
        R('Brëkkeknots', '戰略', [T('Brëkkeknots', 'def', [('inv', 4)])], cp='1', need=['EINHYR HEARTHGUARD']),
        R('Fury of the Hearth', '戰略', [T('Fury of the Hearth', 'att', [('strength', 1)], scope='ranged'),
                                         T('Fury of the Hearth (1YP)', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', why='要花 1YP')], cp='1', need=['EINHYR HEARTHGUARD']),
    ],
}

ENH = {
    'Masterful Construction': [
        T('Devastating Wounds', 'att', [('kw', 'DEVASTATING WOUNDS')], on=True, unitwide=False, pick='mc', why='不含 Psychic 武器'),
        T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], on=True, unitwide=False, pick='mc', why='不含 Psychic 武器'),
        T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], on=True, unitwide=False, pick='mc', why='不含 Psychic 武器'),
    ],
    'Gûlyk’s Stars': [T('Gûlyk’s Stars', 'att', [('mw', 1.17)], on=False, unitwide=False, why='帶的模型衝鋒結束後擲 D6：2-4 造 1 致命傷、5+ 造 2（平均約 1.17）')],
    'Bastion Shield': [T('Bastion Shield', 'def', [('ap', -1)], scope='ranged', on=False, why='攻擊者在 12" 內（花 1YP 變 18"）')],
    'Oathbound Speculator': [
        T('Oathbound Speculator', 'att', [('rr_wound', '1')], on=True),
        T('Oathbound Speculator (3YP)', 'att', [('wound', 1)], on=False, why='要花 3YP'),
    ],
    'Iron Ambassador': [T('Iron Ambassador', 'att', [('dmg', 3)], scope='ranged', on=False, once=True, unitwide=False, why='每場一次，花 3YP（最多）加傷害；只限帶 Autoch-pattern combi-bolter 的模型')],
    'Eye for Weakness': [T('Eye for Weakness', 'att', [('wound', 1)], on=False, why='只打 assailed 的敵人')],
    'Piledriver': [T('Piledriver', 'att', [('dmg', 2)], scope='melee', on=False, unitwide=False, why='花 2YP（最多）加傷害')],
    'Trivärg Cyber Implant': [T('Trivärg Cyber Implant', 'att', [('kw', 'SUSTAINED HITS 2')], scope='ranged', on=False, why='從 Transport 下車的回合，或花 2YP')],
    'Etacarn SB9 Targeting Implant': [
        T('Etacarn SB9 Targeting Implant', 'att', [('rr_hit', '1')], on=True),
        T('Etacarn SB9 (3YP)', 'att', [('kw', 'SUSTAINED HITS 1')], on=False, why='要花 3YP'),
    ],
    'Saturation Rounds': [T('Saturation Rounds', 'att', [('kw', 'IGNORES COVER')], scope='ranged', on=True)],
}
