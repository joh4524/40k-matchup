from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

AA = ['ADEPTUS ASTARTES']

# 軍隊規則：Combat Doctrines 只有移動／ASSAULT 關鍵字（無傷害影響），Kill Team 的多數 T 規則不標記
ARMY = {}


def aoc():
    return R('Armour of Contempt', '戰略', [T('Armour of Contempt', 'def', [('ap', -1)])], cp='1', need=AA)


def mission_tactics():
    return R('Mission Tactics', '規則', [
        T('Furor Tactics', 'att', [('kw', 'SUSTAINED HITS 1')], why='要啟用 devastator doctrine'),
        T('Malleus Tactics', 'att', [('kw', 'LETHAL HITS')], why='要啟用 tactical doctrine')],
        need=['KILL TEAM'], on=False, note='Purgatus (PRECISION) 不算；教條要自己確認')


def kill_team_strats():
    return [
        R('Kraken Rounds', '戰略', [T('Kraken Rounds', 'att', [('strength', 1)], scope='ranged', why='射程 +6" 沒算')], cp='1', need=['KILL TEAM']),
        R('Hellfire Rounds', '戰略', [T('Hellfire Rounds', 'att', [('kw', 'ANTI-NON-VEHICLE 4+')], scope='ranged', why='不含已有 [DEVASTATING WOUNDS] 的攻擊')], cp='1', need=['KILL TEAM']),
        R('Dragonfire Rounds', '戰略', [T('Dragonfire Rounds', 'att', [('rr_wound', '1'), ('kw', 'IGNORES COVER')], scope='ranged')], cp='1', need=['KILL TEAM']),
    ]


def relentless_assault():
    return R('Relentless Assault', '戰略', [
        T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], tkw_not=MV, pick='ra'),
        T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], tkw=MV, pick='ra')], cp='1', need=['TACTICUS'],
        note='打 MONSTER/VEHICLE 用 Lethal Hits，其他目標用 Sustained Hits 1')


DET = {
    '000000750': [   # Gladius Task Force
        R('Storm of Devastation', '戰略', [T('Storm of Devastation', 'att', [('kw', 'IGNORES COVER')], scope='ranged')], cp='1', need=AA),
        aoc(),
        R('Might of Angels', '戰略', [T('Might of Angels', 'att', [('kw', 'LANCE')], scope='melee')], cp='1', need=AA),
    ],
    '000000794': [   # Ironstorm Spearhead
        R('Ironstorm Auto-targeters', '規則', [T('Auto-targeters', 'att', [('rr1', 2)], scope='ranged', why='重骰一顆命中、一顆造傷')], on=True, need=AA + ['VEHICLE'], need_not=['WALKER']),
        R('Might of the Machine Spirit', '戰略', [T('Might of the Machine Spirit', 'att', [('ign', 1)])], cp='1', need=AA + ['VEHICLE'], need_not=['DEDICATED TRANSPORT', 'FLY', 'WALKER']),
        R('Headhunter Doctrine', '戰略', [T('Headhunter Doctrine', 'att', [('kw', 'LETHAL HITS: MONSTER/VEHICLE')], scope='ranged')], cp='1', need=AA + ['VEHICLE'], need_not=['DEDICATED TRANSPORT', 'FLY', 'WALKER']),
        # Layered Ceramite：只對致命傷的 FNP，不標記
    ],
    '000000796': [   # Stormlance Task Force
        R('Hurtling Targets', '戰略', [T('Hurtling Targets', 'def', [('hit', -1)], scope='ranged')], cp='1', need=AA, note='原文限 MOUNTED／SPEEDER，程式無法限定「或」，請自行確認'),
    ],
    '000000808': [   # Black Spear Task Force
        mission_tactics(),
    ] + kill_team_strats() + [aoc()],
    '000000835': [   # Inner Circle Task Force
        R('Vowed Target', '規則', [T('Vowed Target', 'att', [('wound', 1)], why='只打在誓約目標點範圍內的敵人')], need=['DEATHWING', 'INFANTRY']),
        # Wrath of the Lion（致命傷隨模型數）、Duty unto Death 不標記
    ],
    '000000905': [   # Boarding Strike
        R('Drive Home the Blade', '規則', [T('Drive Home the Blade', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', why='要在開著的艙門 1" 內，只打門另一側選的敵隊')], need=AA),
        R('In the Emperor’s Name', '戰略', [T('In the Emperor’s Name', 'def', [('fnp', 5)], why='要在目標點範圍內')], cp='1', need=AA + ['BATTLELINE']),
        R('Ceramite Bulwark', '戰略', [T('Ceramite Bulwark', 'att', [('attacks', 1), ('strength', 1)], scope='melee', why='只給選定的模型，且只能打艙門另一側的敵人')], cp='1', need=AA + ['BATTLELINE']),
    ],
    '000000906': [   # Pilum Strike Team
        R('Master Marksmen', '戰略', [T('Master Marksmen', 'att', [('kw', 'DEVASTATING WOUNDS')], scope='ranged')], cp='1', need=AA),
        R('Knife Work', '戰略', [T('Knife Work', 'att', [('strength', 1), ('ap', 1)], scope='melee')], cp='1', need=AA),
        R('Fighting Retreat', '戰略', [T('Fighting Retreat', 'att', [('mw', 1.17)], why='撤退時選敵隊擲 D6：2-4 = 1 致命傷、5+ = 2 致命傷，平均約 1.17')], cp='1', need=AA),
    ],
    '000000907': [   # Terminator Assault
        R('Sacred Oath', '規則', [T('Sacred Oath', 'att', [('rr_wound', 'all')], once=True, why='只打 Oath of Moment 目標，每場一次')], need=AA),
        # Cleansing Sweep 是 Overwatch；其他為移動／OC
    ],
    '000001004': [   # Angelic Inheritors
        R('Legacy of the Angel', '規則', [T('Legacy of the Angel', 'att', [('rr_hit', '1'), ('rr_wound', '1')])], on=True, need=['BLOOD ANGELS', 'CHARACTER']),
        R('In the Shadow of Great Wings', '戰略', [T('In the Shadow of Great Wings', 'def', [('cover', 1)], scope='ranged', why='Stealth')], cp='1', need=AA + ['CHARACTER']),
        R('Strike Now for Glory', '戰略', [T('Strike Now for Glory', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged')], cp='1', need=AA),
        R('Focused Fury', '戰略', [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='melee'),
                                  T('Lance', 'att', [('kw', 'LANCE')], scope='melee', why='只有 CHARACTER 單位才有')], cp='1', need=AA),
    ],
    '000001008': [   # Champions of Fenris
        R('Heroic Resolve', '戰略', [T('Heroic Resolve', 'def', [('dmg', -1)])], cp='2', need=AA + ['CHARACTER']),
        R('Champion’s Guidance', '戰略', [T('Champion’s Guidance', 'att', [('rr_hit', '1'), ('rr_wound', '1')], scope='melee')], cp='1', need=AA + ['CHARACTER']),
    ],
    '000001059': [   # Wrath of the Rock
        R('Dutiful Tenacity', '規則', [T('Dutiful Tenacity', 'def', [('wound', -1)], cond='s_gt_t')], on=True, need_not=MV, note='原文限 INFANTRY／MOUNTED，這裡以「非 MONSTER／VEHICLE」近似'),
        R('Relics of the Dark Age', '戰略', [T('Relics of the Dark Age', 'att', [('strength', 2)], scope='ranged')], cp='1', need=AA, need_not=MV),
    ],
    '000001070': [   # Saga of the Beastslayer
        R('Legendary Slayers', '規則', [T('Legendary Slayers', 'att', [('kw', 'LETHAL HITS: CHARACTER/MONSTER/VEHICLE')])], on=True, names=['Blood Claws', 'Thunderwolf Cavalry', 'Wulfen']),
        R('Unbridled Ferocity', '戰略', [T('Unbridled Ferocity', 'att', [('kw', 'LANCE')], scope='melee')], cp='1', names=['Blood Claws', 'Thunderwolf Cavalry', 'Wulfen']),
    ],
    '000001086': [   # Forgefather’s Seekers
        R('Vulkan’s Quest', '規則', [T('Vulkan’s Quest', 'att', [('strength', 1)], scope='ranged', why='只打 12" 內的目標')], need=AA),
        R('Immolation Protocols', '戰略', [T('Immolation Protocols', 'att', [('ap', 1)], scope='ranged', wkw='TORRENT')], cp='1', need=AA + ['INFANTRY']),
        R('Crucible of Battle', '戰略', [T('Crucible of Battle', 'att', [('rr_hit', '1'), ('rr_wound', '1')], why='只打 6" 內的敵人')], cp='1', need=AA + ['INFANTRY']),
        R('Forged in Fire', '戰略', [T('Forged in Fire', 'att', [('attacks', 1)], scope='ranged', wkw='TORRENT', why='要在交戰中；Torrent 失去 [Blast]、得到 [Close-Quarters]')], cp='1', need=AA),
    ],
    '000001104': [   # Shadowmark Talon
        R('Shadow Tactics', '規則', [T('Stealth', 'def', [('cover', 1)], scope='ranged', why='Stealth = 掩體')], on=True, need=AA),
        R('Murderous Fusillade', '戰略', [T('Murderous Fusillade', 'att', [('skill', 1), ('ap', 1)], scope='ranged', why='要本回合有 ingress move')], cp='1', need=AA + ['INFANTRY']),
    ],
    '000001119': [   # Spearpoint Task Force
        R('Spear Thrust and Sabre Swing', '戰略', [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='melee', pick='sp'),
                                                  T('Lance', 'att', [('kw', 'LANCE')], scope='melee', pick='sp')], cp='1', need=AA, note='二選一'),
        R('Spear Thrust and Sabre Swing (Mounted)', '戰略', [T('Lethal Hits + Lance', 'att', [('kw', 'LETHAL HITS'), ('kw', 'LANCE')], scope='melee')], cp='1', need=AA + ['MOUNTED'], note='MOUNTED 單位兩個都有（同一個戰略，只算一次 CP）'),
        R('Evasive Manoeuvers', '戰略', [T('Evasive Manoeuvers', 'def', [('wound', -1)], scope='ranged')], cp='1', need=AA, note='原文限 MOUNTED／SPEEDER，請自行確認'),
    ],
    '000001120': [   # Blade of Ultramar
        aoc(),
        R('Exemplary Vigilance', '戰略', [T('Exemplary Vigilance', 'att', [('kw', 'IGNORES COVER')], scope='ranged')], cp='1', need=AA),
        R('Courage and Honour!', '戰略', [T('Courage and Honour!', 'att', [('kw', 'LANCE')], scope='melee')], cp='1', need=AA),
        R('Tactical Foresight', '戰略', [T('Tactical Foresight', 'def', [('wound', -1)], cond='s_gt_t')], cp='1', need=AA),
    ],
    '000001126': [   # Saga of the Great Wolf
        R('Master of Wolves', '規則', [T('Hunter’s Eye', 'att', [('rr_hit', '1')], scope='ranged', why='要啟用 devastator doctrine'),
                                      T('Ferocious Strike', 'att', [('kw', 'SUSTAINED HITS 1')], why='要啟用 tactical doctrine，且目標在 9" 內')], need=AA, need_not=MV),
        R('Eye of the Pack', '戰略', [T('Eye of the Pack', 'att', [('rr_wound', '1')], why='原文可重骰 1 和 2，這裡只算 1（低估）')], cp='1', need=AA + ['INFANTRY']),
    ],
    '000001139': [   # Shield of the Void
        R('Focused Response', '規則', [T('Focused Response', 'def', [('hit', -1)], why='只有在 Set To Defend 的單位')], need=AA),
        R('Adaptive Purge', '戰略', [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='ranged', pick='ap'),
                                    T('Ignores Cover', 'att', [('kw', 'IGNORES COVER')], scope='ranged', pick='ap'),
                                    T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', pick='ap')], cp='1', need=AA),
    ],
    '000001146': [   # Ceramite Sentinels
        R('Adaptive Defence', '規則', [T('Adaptive Defence', 'att', [('rr_wound', '1')], why='要在地形區域內')], need=AA),
        R('Priority Strike', '戰略', [T('Priority Strike', 'att', [('wound', 1)], tkw=MV)], cp='1', need=AA),
        R('Augmented Targeting', '戰略', [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], pick='at'),
                                         T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], pick='at')], cp='1', need=AA),
        R('Augmented Targeting (entrenched)', '戰略', [T('Lethal + Sustained', 'att', [('kw', 'LETHAL HITS'), ('kw', 'SUSTAINED HITS 1')])], cp='1', need=AA, note='要 entrenched；同一個戰略，只算一次 CP'),
        R('Stand to the End', '戰略', [T('Stand to the End', 'def', [('wound', -1)], cond='s_gt_t')], cp='1', need=AA, need_not=MV),
        R('Stand to the End (entrenched)', '戰略', [T('Stand to the End', 'def', [('wound', -1)])], cp='1', need=AA, need_not=MV, note='要 entrenched；同一個戰略，只算一次 CP'),
    ],
    '000001209': [   # Marshal’s Household
        R('Faith-fuelled Resolve', '規則', [T('Faith-fuelled Resolve', 'att', [('attacks', 1)], scope='melee', why='要在目標點範圍內')], names=['Sword Brethren']),
        R('Slayers of Abominations', '戰略', [T('Slayers of Abominations', 'att', [('strength', 2)], scope='melee', tkw=MV)], cp='1', names=['Sword Brethren']),
        # Blade of Detestation 致命傷隨模型數，不標記
    ],
    '000001214': [   # Encarmine Speartip
        R('Blinding Blurs of Vengeance', '戰略', [T('Blinding Blurs of Vengeance', 'def', [('cover', 1)], scope='ranged', why='Stealth')], cp='1', names=['Sanguinary Guard']),
        # Judgement of the Golden Host 致命傷隨模型數，不標記
    ],
    '000001215': [   # Wrath of the Doomed
        R('Death Begets Vengeance', '戰略', [T('Death Begets Vengeance', 'att', [('wound', 1)], why='只打被標記為 hated 的敵隊')], cp='1', need=['DEATH COMPANY']),
    ],
    '000001205': [   # Darkflight Pursuit
        R('Black-winged Vigilance', '規則', [T('Black-winged Vigilance', 'att', [('kw', 'IGNORES COVER')], scope='ranged')], on=True, need=['RAVENWING', 'FLY']),
        R('Wings of Shadow', '戰略', [T('Wings of Shadow', 'def', [('cover', 1)], scope='ranged', why='Stealth')], cp='1', need=['RAVENWING']),
    ],
    '000001229': [   # Deathwatch Support
        mission_tactics(),
    ] + kill_team_strats(),
    '000001230': [   # Vow-sworn Crusaders
        R('Templar Vows', '規則', [T('Abhor the Witch', 'att', [('kw', 'LANCE')], scope='melee', tkw=['PSYKER'], pick='vow', why='[PRECISION] 沒算'),
                                  T('Accept Any Challenge', 'att', [('wound', 1)], scope='melee', cond='t_gt_t', pick='vow')], need=AA,
          note='開戰選一個 Vow（Uphold 為目標點／行動，不算）'),
        R('Pious Enmity', '戰略', [T('Re-roll hit 1', 'att', [('rr_hit', '1')], scope='melee', pick='pe'),
                                  T('vs MONSTER/VEHICLE', 'att', [('rr_hit', '1'), ('rr_wound', '1')], scope='melee', tkw=MV, pick='pe')], cp='1', names=['Chaplain', 'Judiciar']),
        R('Spoor of the Unholy', '戰略', [T('Spoor of the Unholy', 'att', [('ign', 1)])], cp='1', need=AA),
    ],
    '000001231': [   # Fist of the God-Emperor
        R('Avowed Destruction', '戰略', [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='melee', pick='ad'),
                                        T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee', pick='ad')], cp='1', names=['Crusader Squad']),
        R('Angels Defiant', '戰略', [T('Angels Defiant', 'def', [('wound', -1)], cond='s_gt_t')], cp='1', names=['Crusader Squad']),
    ],
    '000001232': [   # Medusa’s Wrath
        R('Armoured Wrath', '規則', [T('Armoured Wrath', 'att', [('rr1', 1)], why='重骰一顆命中或造傷（傷害骰沒算）')], on=True, need=AA),
        R('Armoured Wrath (Feirros)', '規則', [T('Armoured Wrath', 'att', [('rr1', 2)], why='額外再多重骰兩顆（合計命中、造傷、傷害各一）；要在 Cannok Var／Iron Father Feirros 6" 內')], need=AA),
        R('Ancient Fury', '戰略', [T('Ancient Fury', 'att', [('hit', 1)])], cp='1', need=AA + ['DREADNOUGHT'], note='+1 T 沒算'),
        R('Unbowed Conviction', '戰略', [T('Unbowed Conviction', 'att', [('ign', 1)], why='只有低於起始人數才能用')], cp='1', need=AA),
        R('Methodical Brutality', '戰略', [T('Methodical Brutality', 'att', [('kw', 'SUSTAINED HITS 1')])], cp='1', need=AA),
        R('Methodical Brutality (VEHICLE)', '戰略', [T('Methodical Brutality (VEHICLE)', 'att', [('wound', 1)])], cp='1', need=AA + ['VEHICLE'], note='同一個戰略的 VEHICLE 附加效果，只算一次 CP'),
    ],
    '000001233': [   # Gauntlet Task Force
        R('Combined Deployment', '規則', [T('Combined Deployment', 'att', [('kw', 'SUSTAINED HITS 1')], why='只打被標為 assailed 的敵隊，且本回合下過載具')], need=AA),
    ],
    '000001234': [   # Phobos Shadow Force
        R('Strike from the Shadows', '戰略', [T('Strike from the Shadows', 'att', [('strength', 1), ('kw', 'LETHAL HITS')], why='要是 hidden 單位')], cp='1', need=['PHOBOS']),
    ],
    '000001235': [   # Tacticus Attack Force
        relentless_assault(),
    ],
    '000001236': [   # Phobos Shock Force
        R('Vanguard Ambushers', '規則', [T('Vanguard Ambushers', 'att', [('rr_wound', '1')], why='要在移動階段結束時 hidden')], need=['PHOBOS']),
        R('Strike from the Shadows', '戰略', [T('Strike from the Shadows', 'att', [('strength', 1), ('kw', 'LETHAL HITS')], why='要是 hidden 單位')], cp='1', need=['PHOBOS']),
        R('Umbral Evasion', '戰略', [T('Umbral Evasion', 'def', [('hit', -1)], scope='ranged')], cp='1', need=['PHOBOS']),
    ],
    '000001237': [   # Terminator Storm Force
        R('Tactical Dreadnought Fortitude', '戰略', [T('Tactical Dreadnought Fortitude', 'def', [('dmg', -1)])], cp='2', need=AA + ['TERMINATOR']),
        R('Merciless Veterans', '戰略', [T('Merciless Veterans', 'att', [('kw', 'LETHAL HITS'), ('kw', 'SUSTAINED HITS 1')], scope='ranged')], cp='1', need=AA + ['TERMINATOR']),
    ],
    '000001238': [   # Assault Brethren
        aoc(),
        R('Gene-wrought Might', '戰略', [T('Lance', 'att', [('kw', 'LANCE')], scope='melee'),
                                        T('+1 AP (assault doctrine)', 'att', [('ap', 1)], scope='melee', on=False, why='要啟用 assault doctrine')], cp='1', need=AA),
    ],
    '000001239': [   # Gravis Linebreaker Force
        R('Walking Fortress', '規則', [T('Walking Fortress', 'att', [('hit', 1)], scope='ranged', why='只有本回合普通移動過；也失去 [HEAVY]')], need=['GRAVIS']),
        R('Annihilating Force', '戰略', [T('Annihilating Force', 'att', [('kw', 'LETHAL HITS')])], cp='1', need=['GRAVIS']),
        # Armoured Impact 致命傷隨模型數，不標記
    ],
    '000001240': [   # Devastator Brethren
        aoc(),
        R('Storm of Fire', '戰略', [T('Ignores Cover', 'att', [('kw', 'IGNORES COVER')], scope='ranged'),
                                   T('+1 AP (devastator doctrine)', 'att', [('ap', 1)], scope='ranged', on=False, why='要啟用 devastator doctrine')], cp='1', need=AA),
    ],
    '000001241': [   # Gravis Siege Force
        R('Indomitable Defence', '規則', [T('Indomitable Defence', 'def', [('wound', -1)], cond='s_gt_t', why='要在目標點範圍內')], need=['GRAVIS']),
        R('Annihilating Force', '戰略', [T('Annihilating Force', 'att', [('kw', 'LETHAL HITS')])], cp='1', need=['GRAVIS']),
    ],
    '000001242': [   # Tactical Brethren
        aoc(),
        R('Domination Fire', '戰略', [T('Domination Fire', 'def', [('hit', -1)], why='被打中的一隊敵人到你下回合開始前攻擊 -1 命中；程式只算它打這隊（其實打誰都 -1）')], cp='1', need=AA),
    ],
    '000001243': [   # Ironclad Champions
        R('Enduring Vengeance', '規則', [T('Enduring Vengeance', 'att', [('rr_hit', '1')])], on=True, need=AA + ['DREADNOUGHT']),
        R('Mercy Is Weakness', '戰略', [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], pick='mw'),
                                       T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], pick='mw')], cp='1', need=['DREADNOUGHT']),
    ],
    '000001244': [   # Tacticus Firestorm Force
        # Codex Fire-patterns（最大射程也算 Rapid Fire）程式沒有對應標記，不算
        R('Point-Blank Brutality', '戰略', [T('Point-Blank Brutality', 'att', [('kw', 'IGNORES COVER')], scope='ranged', why='要在交戰中；不含 [BLAST] 武器')], cp='1', need=['TACTICUS']),
        relentless_assault(),
    ],
}

ENH = {
    # Gladius
    'Standard of the Emperor Ascendant': [
        T('Standard of the Emperor Ascendant', 'def', [('fnp', 5)], on=True, unitwide=False),
        T('Ancient Exhortation', 'att', [('attacks', 1)], scope='melee', once=True, why='每場一次，開打時用'),
    ],
    'Laurels of Triumph': [
        T('Laurels of Triumph', 'att', [('strength', 1), ('ap', 1)], scope='melee', on=True, unitwide=False),
        T('Laurels (assault doctrine)', 'att', [('strength', 1), ('ap', 1)], scope='melee', unitwide=False, why='assault doctrine 時總共 +2，這裡是額外再 +1'),
    ],
    'Artificer Armour': [T('Artificer Armour', 'def', [('sv', 1), ('fnp', 5)], on=True, unitwide=False, why='Sv 變 2+，以改善 1 近似（3+ 的模型）')],
    # Ironstorm
    'Redoubtable Machine Spirit': [T('Redoubtable Machine Spirit', 'def', [('inv', 5)], on=True)],
    'Gunnery Honours': [T('Gunnery Honours', 'att', [('hit', 1)], scope='ranged', cond='still', why='得到 [HEAVY]：沒移動才 +1；原本就有 Heavy 的武器不疊加')],
    # Inner Circle
    'Champion of the Deathwing': [T('Champion of the Deathwing', 'att', [('kw', 'SUSTAINED HITS 1')], why='只打誓約目標點範圍內的敵人')],
    # Boarding Strike
    'Adamantine Mantle': [T('Adamantine Mantle', 'def', [('dmg', -1)], on=True, unitwide=False)],
    # Pilum
    'Omni-Structural Auspex': [T('Omni-Structural Auspex', 'att', [('ap', 1)], scope='ranged', why='帶者射擊後選一隊被命中的敵人；非 CHARACTER 模型對它 AP +1')],
    # Terminator Assault
    'Seal of Indomitability': [T('Seal of Indomitability', 'def', [('inv', 3)], once=True, unitwide=False, why='每場一次')],
    # Fenris
    'A Giant Amongst Giants': [T('A Giant Amongst Giants', 'att', [('strength', 1)], scope='melee', on=True, unitwide=False)],
    # Wrath of the Rock
    'Ancient Weapons': [T('Ancient Weapons', 'att', [('strength', 2), ('ap', 1)], scope='melee', on=True, unitwide=False)],
    # Forgefather
    'Forged in Battle': [T('Forged in Battle', 'att', [('ign', 1)], on=True)],
    'War Tempered Artifice': [T('War Tempered Artifice', 'att', [('strength', 1), ('dmg', 1)], scope='melee', on=True, unitwide=False)],
    'Immolator': [T('Immolator', 'att', [('attacks', 1)], scope='ranged', wkw='TORRENT', on=True)],
    # Spearpoint
    'Hunter’s Eye': [T('Hunter’s Eye', 'att', [('kw', 'IGNORES COVER'), ('kw', 'SUSTAINED HITS 1')], scope='ranged', on=True)],
    'Spearpoint Paragon': [
        T('Spearpoint Paragon', 'att', [('strength', 1), ('ap', 1)], scope='melee', on=True, unitwide=False),
        T('Spearpoint Paragon (charged)', 'att', [('strength', 1), ('ap', 1)], scope='melee', cond='charge', unitwide=False, why='衝鋒後總共 +2，這裡是額外再 +1'),
    ],
    # Blade of Ultramar
    'Armour of Antoninus': [T('Armour of Antoninus', 'def', [('sv', 1), ('fnp', 5)], on=True, unitwide=False, why='Sv 變 2+，以改善 1 近似（3+ 的模型）')],
    'Oath of Macragge': [
        T('Oath of Macragge', 'att', [('strength', 1), ('ap', 1)], scope='melee', on=True, unitwide=False),
        T('Oath of Macragge (assault doctrine)', 'att', [('strength', 1), ('ap', 1)], scope='melee', unitwide=False, why='assault doctrine 時總共 +2，這裡是額外再 +1'),
    ],
    'Veteran of Behemoth': [T('Veteran of Behemoth', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', on=True)],
    # Great Wolf
    'Skjald’s Foretelling': [T('Skjald’s Foretelling', 'att', [('kw', 'LANCE')], scope='melee', on=True)],
    # Ceramite Sentinels
    'Spy-skull Data Link': [T('Spy-skull Data Link', 'att', [('kw', 'IGNORES COVER')], scope='ranged', on=True)],
    # Encarmine
    'Shadow of Abomination': [T('Shadow of Abomination', 'att', [('dmg', 1)], scope='melee', once=True, unitwide=False, why='每場一次')],
    'Angelic Executioner': [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='melee', on=True, pick='ae'),
                            T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee', on=True, pick='ae')],
    # Wrath of the Doomed
    'On the Archtraitor’s Bridge': [T('On the Archtraitor’s Bridge', 'att', [('attacks', 2)], scope='melee', on=True, unitwide=False)],
    # Vow-sworn
    'Incendiary Animus': [T('Incendiary Animus', 'att', [('strength', 1)], scope='melee', on=True, unitwide=False)],
    'Consecrating Aura': [T('Consecrating Aura', 'def', [('inv', 5)], on=True)],
    # Medusa
    'The Flesh is Weak': [T('The Flesh is Weak', 'def', [('fnp', 5)], on=True, unitwide=False, why='+1 T 沒算')],
    # Phobos
    'Venator Omni-auspex': [T('Venator Omni-auspex', 'att', [('rr_wound', '1')], why='只打 hidden 的敵人；assault doctrine 時可重骰 1-2，這裡只算 1')],
    # Tacticus
    'Martial Paragon': [T('Martial Paragon', 'att', [('rr1', 2)], on=True, why='重骰一顆命中、一顆造傷')],
    # Terminator Storm
    'Champion of the First Company': [T('Champion of the First Company', 'att', [('kw', 'LETHAL HITS')], scope='melee', on=True)],
    # Assault Brethren
    'Furious Assault': [T('Furious Assault', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee', tkw_not=MV, on=True)],
    # Gravis
    'Indefatigable Fortitude': [T('Indefatigable Fortitude', 'def', [('wound', -1)], cond='s_gt_t', on=True)],
    # Devastator
    'Master-forged Firearms': [T('Master-forged Firearms', 'att', [('attacks', 1), ('strength', 1), ('ap', 1), ('dmg', 1)], scope='ranged', on=True, unitwide=False, why='不含 [PSYCHIC] 攻擊')],
    'Honour of Vigilance': [T('Honour of Vigilance', 'att', [('kw', 'LETHAL HITS')], scope='ranged', on=True)],
    # Ironclad
    'Artificer Sarcophagus': [T('Artificer Sarcophagus', 'def', [('dmg', -1)], on=True)],
}
