from manual import T
from army import R, MV

AOI = ['AGENTS OF THE IMPERIUM']
ARMY = {}   # Assigned Agents / Kill Team: 不影響期望傷害

def _any(kws, name, kind, tags, **kw):
    """原文寫「A、B 或 C 單位」→ 每個關鍵字各一條（單位通常只有其中一個）"""
    return [R(name, kind, tags, need=[k], **kw) for k in kws]

_MT = [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], pick='mt'),
       T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], pick='mt')]

DET = {
    # Ordo Xenos Alien Hunters
    '000000892': [
        R('Deathwatch Mission Tactics', '規則', _MT, need=['DEATHWATCH'], on=True,
          note='每次指揮階段選一個（每場各一次）；Purgatus 只給 PRECISION，不影響傷害'),
        R('Armour of Contempt', '戰略', [T('Armour of Contempt', 'def', [('ap', -1)])], cp='1', need=['DEATHWATCH']),
        R('Adaptive Tactics', '戰略', [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], pick='ad'),
                                      T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], pick='ad')], cp='1', need=['DEATHWATCH']),
        R('Dragonfire Rounds', '戰略', [T('Dragonfire Rounds', 'att', [('kw', 'IGNORES COVER')], scope='ranged')], cp='1', need=['DEATHWATCH', 'INFANTRY']),
        R('Hellfire Rounds', '戰略', [T('Hellfire Rounds', 'att', [('kw', 'ANTI-INFANTRY 2+'), ('kw', 'ANTI-MONSTER 5+')], scope='ranged',
                                       why='原文排除有 DEVASTATING WOUNDS 的武器')], cp='1', need=['DEATHWATCH', 'INFANTRY']),
        R('Kraken Rounds', '戰略', [T('Kraken Rounds', 'att', [('ap', 1)], scope='ranged')], cp='1', need=['DEATHWATCH', 'INFANTRY']),
    ],
    # Ordo Hereticus Purgation Force
    '000000893': (
        _any(['ADEPTUS ARBITES', 'INQUISITOR', 'INQUISITORIAL AGENTS', 'ORDO HERETICUS'], 'Root out Heresy (Ignores Cover)', '規則',
             [T('Root out Heresy', 'att', [('kw', 'IGNORES COVER')], scope='ranged')], on=True)
        + _any(['ADEPTUS ARBITES', 'INQUISITOR', 'INQUISITORIAL AGENTS', 'ORDO HERETICUS'], 'Root out Heresy (Sustained Hits)', '規則',
               [T('Root out Heresy', 'att', [('kw', 'SUSTAINED HITS 1')], tkw=['CHAOS'], why='只打 5 個模型以上的 CHAOS 單位')])
        + [
        R('Dispense Justice', '戰略', [T('Dispense Justice', 'att', [('kw', 'LETHAL HITS')])], cp='1',
          note='限 ADEPTUS ARBITES／INQUISITORIAL AGENTS／ORDO HERETICUS 單位'),
        R('Inviolate Jurisdiction', '戰略', [T('Inviolate Jurisdiction', 'def', [('fnp', 5)], why='要在目標點範圍內')], cp='1', need=['INFANTRY'],
          note='限 ADEPTUS ARBITES／INQUISITORIAL AGENTS／ORDO HERETICUS 單位'),
    ]),
    # Ordo Malleus Daemon Hunters
    '000000894': (
        _any(['INQUISITOR', 'INQUISITORIAL AGENTS', 'ORDO MALLEUS'], 'Destroy the Daemonic (Hit)', '規則',
             [T('Destroy the Daemonic', 'att', [('rr_hit', '1')])], on=True)
        + _any(['INQUISITOR', 'INQUISITORIAL AGENTS', 'ORDO MALLEUS'], 'Destroy the Daemonic (Wound)', '規則',
               [T('Destroy the Daemonic', 'att', [('rr_wound', '1')], tkw=['DAEMON'])], on=True)
        + [
        R('Rites of Exorcism', '戰略', [T('Rites of Exorcism', 'att', [('kw', 'DEVASTATING WOUNDS')], tkw=['DAEMON'],
                                         why='目標 DAEMON 單位要先戰震失敗；友軍 AGENTS OF THE IMPERIUM 都有效')], cp='1',
          note='限 INQUISITOR／INQUISITORIAL AGENTS／ORDO MALLEUS 單位使用'),
        R('Psybolt Ammunition', '戰略', [T('Psybolt Ammunition', 'att', [('kw', 'LETHAL HITS')], scope='ranged')], cp='1',
          need=['GREY KNIGHTS TERMINATOR SQUAD']),
        R('Truesilver Armour', '戰略', [T('Truesilver Armour', 'def', [('ap', -1)])], cp='1', need=['GREY KNIGHTS TERMINATOR SQUAD']),
    ]),
    # Imperialis Fleet
    '000000895': [
        R('Eliminate At All Costs', '規則', [T('Eliminate At All Costs', 'att', [('hit', 1)], why='只打被選的那一隊')], need=AOI),
        R('Acquire At All Costs', '規則', [T('Acquire At All Costs', 'def', [('inv', 5)], why='要在被選的目標點範圍內')], need=AOI),
        R('Close-quarters Barrage', '戰略', [T('Close-quarters Barrage', 'att', [('strength', 1), ('ap', 1)], scope='ranged', why='只打 12" 內的目標')],
          cp='1', need=['VOIDFARERS']),
        R('Violent Acquisition', '戰略', [T('Violent Acquisition', 'att', [('kw', 'SUSTAINED HITS 1'), ('kw', 'LANCE'), ('kw', 'IGNORES COVER')],
                                           why='只打在目標點範圍內的敵人')], cp='2', need=AOI),
        R('Displacer Field', '戰略', [T('Displacer Field', 'def', [('inv', 4)])], cp='1', need=AOI + ['CHARACTER'], need_not=['OFFICIO ASSASSINORUM']),
    ],
    # Voidship's Company
    '000000924': [
        R('Ammo Rations', '戰略', [T('Ammo Rations', 'att', [('ap', 1)], why='只打被選的那一隊')], cp='1', need=['VOIDFARERS']),
        R('Breach and Clear', '戰略', [T('Breach and Clear', 'att', [('hit', 1), ('wound', 1)], why='模型要在艙門另一側（穿過艙門後）')],
          cp='1', need=['IMPERIAL NAVY BREACHERS']),
    ],
    # Interdiction Team
    '000000925': [
        R('Duty and Death', '戰略', [T('Duty and Death', 'def', [('fnp', 4)])], cp='1', need=['ADEPTUS ARBITES']),
        R('Crackdown', '戰略', [T('Crackdown', 'att', [('rr_hit', 'all'), ('rr_wound', 'all')], scope='melee')], cp='1', need=['ADEPTUS ARBITES']),
        R('Arbitrary Execution', '戰略', [T('Arbitrary Execution', 'att', [('kw', 'LETHAL HITS')], scope='ranged', weapon='shotpistol',
                                           why='只算 LETHAL HITS；Attacks 改為 2 沒算')], cp='1', need=['ADEPTUS ARBITES']),
    ],
    # Veiled Blade Elimination Force
    '000000987': [
        R('Prime Target', '戰略', [T('Prime Target', 'att', [('rr_wound', '1')], tkw=['CHARACTER'], why='Officio Assassinorum 打敵方 WARLORD 可全重骰，沒算')],
          cp='1', need=AOI),
        R('Hyperstimms', '戰略', [T('Hyperstimms', 'def', [('fnp', 4)], why='只有 EVERSOR ASSASSIN 有；T+1 沒算')], cp='2', need=['EVERSOR ASSASSIN']),
        R('Ensnaring Trap', '戰略', [T('Ensnaring Trap', 'att', [('wound', 1)], scope='melee', why='只在這次戰略造成的衝鋒後')],
          cp='1', need=['CALLIDUS ASSASSIN']),
        R('Will-sapping Salvo', '戰略', [T('Will-sapping Salvo', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged',
                                          why='CULEXUS ASSASSIN 另有傷害改 3，沒算')], cp='1', need=AOI + ['INFANTRY']),
    ],
}

ENH = {
    # 892
    'Blackweave Shroud': [T('Blackweave Shroud', 'def', [('fnp', 4)], on=True, unitwide=False)],
    'Universal Anathema': [T('Universal Anathema', 'att', [('kw', 'ANTI-INFANTRY 2+'), ('kw', 'ANTI-MONSTER 4+')], scope='melee', on=True, unitwide=False)],
    # 893
    'Ignis Judicium': [T('Ignis Judicium', 'att', [('kw', 'DEVASTATING WOUNDS'), ('kw', 'MELTA 1')], scope='ranged', on=True, unitwide=False)],
    'Witch Hunter': [T('Witch Hunter', 'att', [('rr_hit', 'all')], tkw=['PSYKER'], on=True, why='帶領單位時，打 PSYKER')],
    # 894
    'Daemon Slayer': [T('Daemon Slayer', 'att', [('attacks', 1), ('kw', 'ANTI-DAEMON 3+')], scope='melee', on=True, unitwide=False)],
    'Grimoire of True Names (Aura)': [T('Grimoire of True Names', 'def', [('hit', -1), ('wound', -1)], on=False, why='只對 9" 內攻擊的敵方 DAEMON 單位有效')],
    # 895
    'Digital Weapons': [T('Digital Weapons', 'att', [('mw', 1.5)], scope='melee', on=True, unitwide=False,
                          why='選擇戰鬥時擲 3 顆 D6，每個 4+ 1 致命傷，平均 1.5')],
    # 924
    'Heirloom Blade': [T('Heirloom Blade', 'att', [('attacks', 1), ('strength', 1), ('ap', 1), ('dmg', 1), ('skill', 1)], scope='melee',
                         weapon='monomolecular', once=True, on=False, unitwide=False, why='每場一次，monomolecular cane-rapier 全數值 +1')],
    # 925
    'Manhunter’s Helm': [T('Manhunter’s Helm', 'att', [('wound', 1)], on=False, why='只打被選的 Priority Target')],
    # 987
    'Micromelta Rounds': [T('Micromelta Rounds', 'att', [('kw', 'ANTI-MONSTER 4+'), ('kw', 'ANTI-VEHICLE 4+')], scope='ranged', weapon='exitus rifle', on=True, unitwide=False)],
}
