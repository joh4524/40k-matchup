from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

BL = '只有該單位有 BATTLELINE 或在 6" 內有友方 ADEPTUS MECHANICUS BATTLELINE 才有效'


def imp_both(src, on=True):
    """Conqueror + Protector 同時啟動（強化／戰略用）"""
    return [
        T(src + ' (BS)', 'att', [('skill', 1)], scope='ranged', on=on, why='Protector：遠程 BS 改善 1'),
        T(src + ' (WS)', 'att', [('skill', 1)], scope='melee', on=on, why='Conqueror：近戰 WS 改善 1'),
        T(src + ' (AP)', 'att', [('ap', 1)], on=False, why='Conqueror：' + BL),
        T(src + ' (-1 Hit)', 'def', [('hit', -1)], scope='melee', on=False, why='Protector：' + BL),
    ]


ARMY = {
    '000008382': dict(name='Doctrina Imperatives', rules=[
        R('Protector Imperative', '軍隊規則', [
            T('Protector: BS+1', 'att', [('skill', 1)], scope='ranged'),
            T('Protector: Heavy', 'att', [('hit', 1)], scope='ranged', cond='still', why='HEAVY：沒移動才 +1 命中（武器本來就有 HEAVY 的不會再加）'),
            T('Protector: -1 to be hit', 'def', [('hit', -1)], scope='melee', why=BL),
        ], on=False, note='每回合二選一（Protector／Conqueror）；只給有 Doctrina Imperatives 能力的單位'),
        R('Conqueror Imperative', '軍隊規則', [
            T('Conqueror: WS+1', 'att', [('skill', 1)], scope='melee'),
            T('Conqueror: AP+1', 'att', [('ap', 1)], why=BL),
        ], on=False, note='每回合二選一（Protector／Conqueror）；Assault 能力不算'),
    ]),
}

DET = {
    # Rad-Zone Corps
    '000000762': [
        R('Baleful Halo', '戰略', [T('Baleful Halo', 'def', [('wound', -1)])], cp='2', need_not=['VEHICLE']),
        R('Pre-calibrated Purge Solution', '戰略', [T('Pre-calibrated Purge Solution', 'att', [('rr_hit', 'all')], scope='ranged', why='只打在對手部署區內的目標')], cp='1'),
        R('Bulwark Imperative', '戰略', [T('Bulwark Imperative', 'def', [('inv', 4)], scope='ranged')], cp='2', need=['SKITARII']),
        R('Lethal Dosage', '戰略', [T('Lethal Dosage', 'att', [('kw', 'LETHAL HITS')], scope='ranged')], cp='1'),
        # Rad-bombardment／Aggressor Imperative／Extinction Order：致命傷（回合開始／指揮階段）或移動，不算
    ],
    # Skitarii Hunter Cohort
    '000000820': [
        R('Stealth Optimisation', '規則', [T('Stealth', 'def', [('cover', 1)])], on=True, need=['SKITARII'], need_not=['TRANSPORT'],
          note='原文只給 SKITARII INFANTRY／MOUNTED／IRONSTRIDER BALLISTARII，程式無法精確限定，其他 SKITARII 載具可能多算'),
        R('Binharic Offence', '戰略', [T('Binharic Offence', 'att', [('ap', 1)], why='只能打被選的那一隊敵人')], cp='2', need=['SKITARII']),
        R('Isolate and Destroy', '戰略', [T('Isolate and Destroy', 'att', [('wound', 1)], scope='ranged', why='目標 6" 內沒有其他敵方單位')], cp='1'),
        R('Bionic Endurance', '戰略', [T('Bionic Endurance', 'def', [('fnp', 5)])], cp='1',
          note='只限 SICARIAN／PTERAXII／SYDONIAN，程式無法限定'),
    ],
    # Data-Psalm Conclave
    '000000821': [
        R('Panegyric Procession', '規則', [T('Panegyric Procession', 'att', [('ap', 1)], scope='ranged', cond='half')], need=['CULT MECHANICUS'],
          note='戰鬥開始時二選一（與 Citation in Savagery）'),
        R('Citation in Savagery', '規則', [T('Citation in Savagery', 'att', [('strength', 1), ('attacks', 1)], scope='melee', cond='charge')], need=['CULT MECHANICUS'],
          note='戰鬥開始時二選一（與 Panegyric Procession）'),
        R('Chant of the Remorseless Fist', '戰略', [T('Chant of the Remorseless Fist', 'att', [('wound', 1)], scope='melee')], cp='1', need=['CULT MECHANICUS']),
        R('Luminescent Blessing', '戰略', [T('Luminescent Blessing', 'def', [('inv', 4)], scope='ranged')], cp='1', need=['CULT MECHANICUS']),
        R('Tribute of Emphatic Veneration', '戰略', [T('Tribute of Emphatic Veneration', 'def', [('hit', -1)], why='要被選的敵方單位 Battle-shock 失敗，只對那一隊的攻擊有效')], cp='1'),
        R('Litany of the Electromancer', '戰略', [T('Litany of the Electromancer', 'att', [('mw', 0.67)], scope='ranged', why='每個 6" 內敵方單位 5+ 造成 D3 致命傷 ≈ 0.67（ELECTRO-PRIEST 4+ 約 1.0）')], cp='1', need=['CULT MECHANICUS']),
        # Incantation（只對致命傷的 FNP 4+）、Verse of Vengeance 不算
    ],
    # Explorator Maniple
    '000000822': [
        R('Acquisition At Any Cost', '規則', [T('Acquisition At Any Cost', 'att', [('rr_wound', '1')], why='自己或目標要在 Acquisition 目標點範圍內')], need=['ADEPTUS MECHANICUS']),
        R('Auto-oracular Retrieval', '戰略', [T('Auto-oracular Retrieval', 'att', [('wound', 1)], scope='ranged', why='剛從 TRANSPORT 下車；目標在 Acquisition 目標點範圍內')], cp='2'),
        R('Incense Exhausts', '戰略', [T('Incense Exhausts', 'def', [('cover', 1)], scope='ranged')], cp='1', need=['INFANTRY']),
    ],
    # Cohort Cybernetica
    '000000823': [
        R('Auto-divinatory Targeting', '戰略', [T('Auto-divinatory Targeting', 'att', [('kw', 'IGNORES COVER')], scope='ranged', why='BS 變 3+（程式沒算）；只能打選定目標點範圍內的單位')], cp='1'),
        R('Benevolence of the Omnissiah', '戰略', [T('Benevolence of the Omnissiah', 'def', [('fnp', 6)], why='對致命傷是 5+（致命傷改善沒算）')], cp='1'),
        R('Machine Spirit Resurgent', '戰略', [
            T('Machine Spirit Resurgent (hit)', 'att', [('rr_hit', 'all')], why='要低於起始人數'),
            T('Machine Spirit Resurgent (wound)', 'att', [('rr_wound', 'all')], why='要低於半數人數'),
        ], cp='1'),
        R('Machine Superiority', '戰略', [T('Machine Superiority', 'att', [('ign', 1)], why='不含 Save 修正')], cp='1'),
        R('Transcendent Cogitation', '戰略', imp_both('Transcendent Cogitation', on=True), cp='1', need=['VEHICLE']),
    ],
    # Electromartyrs
    '000000912': [
        R('Overload Machine Spirits', '規則', [T('Overload Machine Spirits', 'att', [('ap', 1)], scope='ranged', why='武器同時有 HAZARDOUS（危險測試沒算）')], note='選擇使用才有效'),
        R('Saviour Systems', '戰略', [T('Saviour Systems', 'def', [('wound', -1)])], cp='1', need_not=['KATAPHRON']),
        R('Omni-targeters', '戰略', [T('Omni-targeters', 'att', [('hit', 1)], scope='ranged', why='只限武器本來就有 PISTOL，且目標在 6" 內')], cp='1'),
        R('Ballistic Synchrony', '戰略', [T('Ballistic Synchrony', 'att', [('kw', 'LETHAL HITS')], scope='ranged')], cp='1'),
        # Auto-vengeance：死後還能打，程式不算
    ],
    # Response Clade
    '000000913': [
        R('Procedural Elimination (ranged)', '規則', [T('Procedural Elimination', 'att', [('rr_hit', '1')], scope='ranged')], need=['SKITARII'], note='每回合選遠程或近戰'),
        R('Procedural Elimination (melee)', '規則', [T('Procedural Elimination', 'att', [('rr_hit', '1')], scope='melee')], need=['SKITARII'], note='每回合選遠程或近戰'),
        R('Precognitated Firefields', '戰略', [T('Precognitated Firefields', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged')], cp='1', need=['SKITARII'], need_not=['BATTLELINE']),
        R('Precognitated Firefields (Battleline)', '戰略', [T('Precognitated Firefields', 'att', [('kw', 'SUSTAINED HITS 2')], scope='ranged')], cp='1', need=['SKITARII', 'BATTLELINE']),
        R('Responsive Shielding', '戰略', [T('Responsive Shielding', 'def', [('inv', 4)], why='要在目標點範圍內')], cp='1', need=['SKITARII']),
    ],
    # Machine Cult
    '000000914': [
        R('Electrogheist Visitations', '戰略', [T('Electrogheist Visitations', 'def', [('hit', -1)], why='攻擊的模型在 6" 內')], cp='1', need=['ELECTRO-PRIESTS']),
    ],
    # Haloscreed Battle Clade
    '000000984': [
        R('Muted Servomotors', '規則', [T('Muted Servomotors', 'def', [('cover', 1)])],
          note='Noospheric Transference 的 Override 四選一，要有 HALO OVERRIDE。⚠️ Microactuator Bracing（T+1）程式沒有對應效果，沒算'),
        R('Targeting Override', '戰略', [T('Targeting Override', 'att', [('crit_hit', 5)])], cp='1'),
        R('Eradication Protocols', '戰略', [
            T('Eradication Protocols (wound)', 'att', [('rr_wound', '1')]),
            T('Eradication Protocols (hit)', 'att', [('rr_hit', '1')], on=False, why='要有 HALO OVERRIDE 才有'),
        ], cp='1'),
    ],
    # Eradication Cohort
    '000001143': [
        R('Murderous Imperative (Protector)', '規則', [T('Murderous Imperative', 'att', [('rr_hit', '1')], why='要 Protector Imperative 啟動')], need=['SKITARII']),
        R('Murderous Imperative (Conqueror)', '規則', [T('Murderous Imperative', 'att', [('rr_wound', '1')], why='要 Conqueror Imperative 啟動')], need=['SKITARII']),
        R('Servo-driven Charge', '戰略', [T('Servo-driven Charge', 'att', [('kw', 'LANCE')], scope='melee')], cp='1'),
        R('Unshackled Wrath', '戰略', [
            T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', pick='wrath'),
            T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='ranged', pick='wrath'),
        ], cp='1', need=['SKITARII'], note='二選一；也可三個一起拿但武器變 HAZARDOUS（沒算）'),
        R('Precision Onslaught', '戰略', [T('Precision Onslaught', 'att', [('mw_pm', 0.5)], scope='melee', cond='charge', why='衝鋒結束：每個模型 4+ 造成 1 點致命傷')], cp='1', need=['SICARIAN']),
        R('Threat-cogitation Targeters', '戰略', [T('Threat-cogitation Targeters', 'att', [('rr_dmg', 'all')], scope='ranged', tkw=MV)], cp='1', need=['SKITARII', 'VEHICLE']),
    ],
    '000001158': [
        R('Defect Scrutiny', '戰略', [T('Defect Scrutiny', 'att', [('kw', 'IGNORES COVER')], scope='ranged', why='只打被選的敵方單位')], cp='1'),
    ],
    # Lords of the Forge
    '000001159': [
        R('War-Form Mantles (4+ invulnerable)', '規則', [T('War-Form Mantles', 'def', [('inv', 4)])], on=True, model_kw=['TECH-PRIEST']),
        R('War-Form Mantles (FNP)', '規則', [T('War-Form Mantles', 'def', [('fnp', 5)])], on=True, model_kw=['TECH-PRIEST']),
        R('Scriptural Prognosis', '戰略', [T('Scriptural Prognosis', 'def', [('ap', -1)], why='⚠️ 原文 "-1 AP" 解讀為對方 AP 變差 1；要在目標點範圍內')], cp='1', need=['TECH-PRIEST']),
    ],
    # Luminen Auto-choir
    '000001160': [
        R('Cyber-Static Canticles', '規則', [T('Cyber-Static Canticles', 'att', [('kw', 'LETHAL HITS')], scope='ranged')], on=True, need=['CORPUSCARII']),
        R('Echoes of the Conduit Wars', '戰略', [
            T('Echoes (hit)', 'att', [('rr_hit', '1')], why='目標要在目標點範圍內'),
            T('Echoes (wound)', 'att', [('rr_wound', '1')], why='目標要在目標點範圍內'),
        ], cp='1', need=['ELECTRO-PRIESTS']),
    ],
}

ENH = {
    # Rad-Zone Corps
    'Malphonic Susurrus': [T('Malphonic Susurrus', 'def', [('cover', 1)], on=True)],
    'Peerless Eradicator': [T('Peerless Eradicator', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', on=True)],
    'Autoclavic Denunciation': [T('Autoclavic Denunciation', 'att', [('kw', 'ANTI-INFANTRY 2+'), ('kw', 'ANTI-MONSTER 4+')], scope='ranged', on=True, unitwide=False)],
    # Skitarii Hunter Cohort
    'Cantic Thrallnet': [T('Cantic Thrallnet', 'att', [('skill', 1)], on=False, why='每回合選 12" 內一個友方 SKITARII 單位兩個 Imperative 都啟動（不是帶的人的單位）；BS／WS 都改善 1')],
    # Data-Psalm Conclave: Mantle of the Gnosticarch（傷害改 1）程式沒有對應效果，沒算
    # Explorator Maniple
    'Genetor': [T('Genetor', 'def', [('inv', 4)], on=False, why='帶領的單位要在 Acquisition 目標點範圍內')],
    'Logis': [T('Logis', 'att', [('hit', 1)], on=False, why='目標要在 Acquisition 目標點範圍內')],
    # Cohort Cybernetica
    'Arch-negator': [T('Arch-negator', 'att', [('kw', 'ANTI-VEHICLE 4+')], scope='ranged', on=True, unitwide=False)],
    # Haloscreed Battle Clade
    'Cognitive Reinforcement': imp_both('Cognitive Reinforcement', on=True),
    'Inloaded Lethality': [T('Inloaded Lethality', 'att', [('attacks', 3), ('dmg', 1)], scope='melee', on=True, unitwide=False)],
    # Eradication Cohort
    'Omnicogitator': imp_both('Omnicogitator', on=True),
    'Belicosa-Class Capacitor Vanes': [T('Belicosa-Class Capacitor Vanes', 'att', [('strength', 1)], scope='ranged', on=True)],
    'Omnissiah’s Fury': [T('Omnissiah’s Fury', 'att', [('attacks', 2), ('ap', 1), ('dmg', 1)], scope='melee', on=True, unitwide=False)],
    # Luminen Auto-choir
    'Electromiasmic Brazier': [T('Electromiasmic Brazier', 'def', [('cover', 1)], on=True)],
    # Lords of the Forge: Vingh’s Wafers／TL-4Ø9 沒有影響傷害的效果（TL-4Ø9 原文為空）
}
