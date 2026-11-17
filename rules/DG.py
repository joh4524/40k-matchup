from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

ARMY = {
    # Dark Pacts 000008359 只限 HERETIC ASTARTES 陣營，Death Guard 不適用，不標記
    '000008396': dict(name='Nurgle’s Gift (Aura)', rules=[
        R('Afflicted：T−1（近戰）', '軍隊規則', [T('Afflicted T−1', 'att', [('tgt_t', 1)], scope='melee', why='近戰時敵人一定在 Contagion Range 內')], on=True,
          note='被感染（Afflicted）的敵人 T−1'),
        R('Afflicted：T−1（射擊）', '軍隊規則', [T('Afflicted T−1', 'att', [('tgt_t', 1)], scope='ranged', why='目標要在 Contagion Range 內（3" 起，戰鬥中變大）')]),
        R('Rattlejoint Ague', '軍隊規則', [T('Rattlejoint Ague', 'att', [('ap', 1)], why='開戰選這個瘟疫，且目標被感染；敵人 Save 變差 1（跟 AP+1 一樣）')],
          note='三種瘟疫選一：Rattlejoint Ague／Skullsquirm Blight 擇一勾'),
        R('Skullsquirm Blight', '軍隊規則', [
            T('Skullsquirm Blight (射擊)', 'def', [('cover', 1)], scope='ranged', why='攻擊者要被感染且選了這個瘟疫'),
            T('Skullsquirm Blight (近戰)', 'def', [('hit', -1)], scope='melee', why='攻擊者要被感染且選了這個瘟疫'),
        ], note='三種瘟疫選一：Rattlejoint Ague／Skullsquirm Blight 擇一勾'),
    ]),
}

DET = {
    '000000930': [   # Vectors of Decay
        R('CHINKS IN THE ARMOUR', '戰略', [T('Chinks in the Armour', 'att', [('crit_hit', 5)], why='目標要在 Contagion Range 內')], cp='1', need=['DEATH GUARD']),
    ],
    '000000931': [   # Unclean Uprising
        R('POX FLARE', '戰略', [T('Pox Flare', 'att', [('ap', 1)], scope='melee')], cp='1', need=['POXWALKERS']),
    ],
    '000000932': [   # Arch-Contaminators
        R('CLOUD OF FLIES', '戰略', [T('Cloud of Flies', 'def', [('hit', -1)], scope='ranged')], cp='1', need=['DEATH GUARD']),
    ],
    '000000980': [   # Flyblown Host
        R('DRONING HORROR', '戰略', [
            T('Droning Horror (hit 1)', 'att', [('rr_hit', '1')], scope='ranged'),
            T('Droning Horror (wound 1)', 'att', [('rr_wound', '1')], scope='ranged', cond='half', why='只限半射程內'),
        ], cp='1', need=['PLAGUE MARINES']),
    ],
    '000001049': [   # Virulent Vectorium
        R('DISGUSTINGLY RESILIENT', '戰略', [T('Disgustingly Resilient', 'def', [('dmg', -1)])], cp='2', need=['DEATH GUARD']),
        R('CREEPING BLIGHT', '戰略', [T('Creeping Blight', 'att', [('rr_hit', 'all'), ('rr_wound', 'all')], scope='ranged', why='只打 Afflicted 的目標')], cp='1', need=['DEATH GUARD', 'INFANTRY']),
    ],
    '000001050': [   # Mortarion’s Hammer
        R('DRAWN TO DESPAIR', '戰略', [T('Drawn to Despair', 'att', [('rr_hit', 'all')], why='只打在對方部署區內、看得見的敵軍（非 AIRCRAFT）')], cp='1', need=['DEATH GUARD']),
    ],
    '000001051': [   # Champions of Contagion
        R('BLESSINGS OF FILTH', '戰略', [T('Blessings of Filth', 'att', [('crit_hit', 5)])], cp='1', need=['DEATH GUARD'], note='只限帶領角色的 Attached 單位'),
        R('MALIGNANCE MAGNIFIED', '戰略', [T('Malignance Magnified', 'att', [('rr_hit', 'all'), ('rr_wound', 'all')], why='只打低於起始人數的目標')], cp='2', need=['DEATH GUARD'], note='只限 Attached 單位'),
    ],
    '000001052': [   # Tallyband Summoners
        R('CLUTCHING CORRUPTION', '戰略', [T('Clutching Corruption', 'att', [('rr_hit', 'all')], scope='melee', why='只打與 Plague Legions 交戰的目標')], cp='1', need=['DEATH GUARD']),
    ],
    '000001053': [   # Shamblerot Vectorium
        R('GNAWING HUNGER', '戰略', [T('Gnawing Hunger', 'att', [('attacks', 1), ('strength', 1)], scope='melee')], cp='1', need=['POXWALKERS']),
    ],
    '000001054': [   # Death Lord’s Chosen
        R('GRIM REAPERS', '戰略', [T('Grim Reapers', 'att', [('rr_hit', 'all')], tkw_not=MV)], cp='1', need=['TERMINATOR']),
        R('SICKENING IMPACT', '戰略', [T('Sickening Impact', 'att', [('mw_pm', 5 / 6), ('mw_cap', 6)], scope='melee', cond='charge', why='衝鋒結束：每個模型 2+ 造成 1 點致命傷，最多 6')], cp='1', need=['TERMINATOR']),
    ],
    '000001168': [   # Contagion Engines
        R('FRESH VECTORS', '戰略', [T('Fresh Vectors', 'att', [('rr_wound', '1')])], cp='1', names=['Bloat-drone', 'Helbrute', 'Blight-hauler'],
          note='只限 CONTAGION ENGINE（Bloat-drone／Helbrute／Blight-hauler）'),
    ],
    '000001169': [],   # Hypervirulent Strains 只改 Contagion Range，不影響傷害（強化在 ENH）
}

ENH = {
    'Foul Constitution': [T('Foul Constitution', 'def', [('dmg', -1)], on=True, unitwide=False)],
    'Insectile Murmuration': [T('Insectile Murmuration', 'att', [('rr_wound', '1')], on=False, why='目標要在 Contagion Range 內')],
    'Daemon Weapon of Nurgle': [T('Daemon Weapon of Nurgle', 'att', [('crit_hit', 5)], scope='melee', on=True, unitwide=False)],
    'Furnace of Plagues': [T('Furnace of Plagues', 'att', [('attacks', 1), ('strength', 1), ('kw', 'DEVASTATING WOUNDS')], scope='melee', on=True, unitwide=False)],
    'Arch Contaminator': [T('Arch Contaminator', 'att', [('rr_wound', 'all')], on=False, why='要在自己控制的目標點範圍內')],
    'Revolting Regeneration': [T('Revolting Regeneration', 'def', [('fnp', 5)], on=True, unitwide=False)],
    'Eye of Affliction': [T('Eye of Affliction', 'att', [('kw', 'IGNORES COVER')], scope='ranged', on=False, why='只打 Afflicted 的目標')],
    'Tendrilous Emissions': [T('Tendrilous Emissions', 'att', [('rr_wound', '1')], scope='ranged', on=False, why='只限附近友軍 VEHICLE 的射擊，且要在 3" 內')],
    'Fell Harvester': [T('Fell Harvester', 'att', [('attacks', 2)], scope='melee', on=True, unitwide=False)],
    'Rejuvenating Swarm': [T('Rejuvenating Swarm', 'def', [('wound', -1)], cond='s_gt_t', on=True)],
}
