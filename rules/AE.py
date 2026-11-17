from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

WC = ['WRAITH CONSTRUCT']
ASPECT = ['Dire Avengers', 'Fire Dragons', 'Swooping Hawks', 'Warp Spiders']

def void_ghosts():
    return R('Void Ghosts', '戰略', [T('Void Ghosts', 'def', [('hit', -1)])], cp='1', need=['AELDARI'])

ARMY = {
    # Strands of Fate (Fate dice) and Battle Focus (movement/Overwatch/ASSAULT only): not modelled
}

DET = {
    # Khaine's Arrow
    '000000919': [
        R('Focused Fusillade', '戰略', [T('Focused Fusillade', 'att', [('wound', 1)], scope='ranged')], cp='1', names=ASPECT),
        R('Bladefocus', '戰略', [T('Bladefocus', 'att', [('rr_hit', 'all')], scope='melee', cond='charge')], cp='1', names=['Howling Banshees', 'Striking Scorpions']),
        void_ghosts(),
    ],
    # Protector Host
    '000000920': [
        R('Determined Defence', '規則', [T('Determined Defence', 'def', [('sv', 1)], why='要在目標點範圍內')], names=['Guardian', 'Dire Avengers']),
        R('Shuriken Storm', '戰略', [T('Shuriken Storm', 'att', [('strength', 1)], scope='ranged', weapon='shuriken', why='只限 shuriken catapult／pistol／cannon')], cp='1', need=['AELDARI']),
        void_ghosts(),
    ],
    # Wraiths of the Void
    '000000921': [
        R('Guardian Constructs', '戰略', [T('Guardian Constructs', 'def', [('wound', -1)], scope='melee', why='攻擊者要在艙門另一側')], cp='1', need=WC),
        R('Wraithsight', '戰略', [T('Wraithsight', 'att', [('kw', 'IGNORES COVER'), ('ign', 1)], scope='ranged')], cp='1', need=['AELDARI']),
        R('D-Strike', '戰略', [T('D-Strike', 'def', [('hit', -1)], why='只對艙門 3" 內、另一側被眩暈的敵軍')], cp='1', need=WC),
    ],
    # Star-dancer Masque
    '000000922': [
        R('Darting Strikes', '戰略', [T('Darting Strikes', 'att', [('rr_wound', 'all')], scope='melee')], cp='1', need=['AELDARI']),
        void_ghosts(),
    ],
    # Armoured Warhost
    '000000990': [
        # Skilled Crews = ASSAULT only, no damage effect
        R('Soulsight', '戰略', [T('Soulsight', 'att', [('rr1', 2), ('rr1d', 1)], scope='ranged', why='重骰一顆命中、一顆造傷、一顆傷害骰')], cp='1', need=['AELDARI', 'VEHICLE']),
    ],
    # Warhost
    '000001017': [
        R('Blitzing Firepower', '戰略', [T('Blitzing Firepower', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', why='只限目標 12" 內；已有 Sustained 的武器改為 5+ 暴擊（沒算）')], cp='1', need=['ASURYANI']),
        R('Lightning-Fast Reactions', '戰略', [T('Lightning-Fast Reactions', 'def', [('hit', -1)])], cp='1', need=['ASURYANI'], need_not=WC),
    ],
    # Windrider Host
    '000001018': [
        R('Death from on High', '戰略', [T('Death from on High', 'att', [('rr_wound', 'all')], why='要是這回合從預備隊上場')], cp='1', need=['ASURYANI']),
        R('Spiralling Evasion', '戰略', [T('Spiralling Evasion', 'def', [('inv', 4)], scope='ranged')], cp='1', need=['ASURYANI']),
        R('Focused Firepower', '戰略', [T('Focused Firepower', 'att', [('ap', 1)], scope='ranged')], cp='1', need=['ASURYANI']),
    ],
    # Spirit Conclave
    '000001019': [
        R('Shepherds of the Dead', '規則', [T('Shepherds of the Dead', 'att', [('hit', 1), ('wound', 1)], why='只打帶 Vengeful Dead 標記的敵軍')], need=WC),
        R('Wraithbone Armour', '戰略', [T('Wraithbone Armour', 'def', [('dmg', -1)])], cp='1', need=WC, need_not=['TITANIC']),
        R('Blades from Beyond', '戰略', [T('Blades from Beyond', 'att', [('kw', 'DEVASTATING WOUNDS')], scope='melee')], cp='1', names=['Wraithblades', 'Wraithlord', 'Wraithknight']),
        # Seer's Eye (ignore AP/Damage modifiers), Crushing Strides (mortal wounds) not modelled
    ],
    # Guardian Battlehost
    '000001020': [
        R('Defend at All Costs', '規則', [T('Defend at All Costs', 'att', [('hit', 1)], why='自己或目標要在目標點範圍內')], names=['Dire Avengers', 'Guardian', 'War Walker', 'Platform']),
        R('Shield Nodes', '戰略', [T('Shield Nodes', 'def', [('wound', -1)], why='要在目標點範圍內')], cp='1', names=['Dire Avengers', 'Guardian']),
        R('Warding Salvoes', '戰略', [T('Warding Salvoes', 'att', [('rr_wound', 'all')], why='只打在目標點範圍內的敵軍')], cp='1', names=['Dire Avengers', 'Guardian']),
    ],
    # Ghosts of the Webway
    '000001021': [],   # movement / fight-on-death / reserves only
    # Devoted of Ynnead
    '000001022': [
        R('Emissaries of Ynnead', '戰略', [T('Emissaries of Ynnead', 'att', [('rr_hit', '1')], scope='melee', why='低於起始人數時可全部重骰（沒算）')], cp='1', need=['YNNARI', 'INFANTRY']),
        R('Macabre Resilience', '戰略', [T('Macabre Resilience', 'def', [('wound', -1)])], cp='1', need=['YNNARI'], need_not=WC),
        R('Soulsight', '戰略', [T('Soulsight', 'att', [('kw', 'LETHAL HITS'), ('kw', 'IGNORES COVER')], scope='ranged')], cp='1', need=['YNNARI']),
    ],
    # Seer Council
    '000001023': [
        R('Fate Inescapable', '戰略', [T('Fate Inescapable', 'att', [('kw', 'IGNORES COVER'), ('crit_ap', 1)], scope='ranged', why='爆擊造傷時 AP 再好 1')], cp='1', need=['ASURYANI', 'INFANTRY'], need_not=WC),
        R('Forewarned', '戰略', [T('Forewarned', 'def', [('hit', -1), ('wound', -1)], scope='melee')], cp='1', need=['ASURYANI', 'INFANTRY'], need_not=WC),
    ],
    # Aspect Host
    '000001024': [
        R('Path of the Warrior', '規則', [T('Reroll Hit 1', 'att', [('rr_hit', '1')], pick='path'),
                                         T('Reroll Wound 1', 'att', [('rr_wound', '1')], pick='path')], on=True, need=['ASPECT WARRIORS'],
          note='每次射擊／打架二選一'),
        R('Path of the Warrior', '規則', [T('Reroll Hit 1', 'att', [('rr_hit', '1')], pick='path'),
                                         T('Reroll Wound 1', 'att', [('rr_wound', '1')], pick='path')], on=True, need=['AVATAR OF KHAINE'],
          note='每次射擊／打架二選一'),
        R('Preternatural Precision', '戰略', [T('Ignores Cover', 'att', [('kw', 'IGNORES COVER')], scope='ranged', pick='pp'),
                                              T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='ranged', pick='pp'),
                                              T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', pick='pp')],
          cp='1', need=['ASPECT WARRIORS'], note='選一個；移除 Aspect Shrine token 可選兩個（沒算）'),
        R('Warrior Focus', '戰略', [T('Warrior Focus', 'att', [('ign', 1)])], cp='1', need=['ASPECT WARRIORS']),
        R('Warrior Focus', '戰略', [T('Warrior Focus', 'att', [('ign', 1)])], cp='1', need=['AVATAR OF KHAINE']),
    ],
    # Serpent's Brood
    '000001124': [
        R('Boons of the Brood (Mounted)', '規則', [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')])], on=True, need=['HARLEQUINS'], model_kw=['MOUNTED']),
        R('Boons of the Brood (Vehicle)', '規則', [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')])], on=True, need=['HARLEQUINS'], model_kw=['VEHICLE']),
        R('Boons of the Brood (Disembark)', '規則', [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], why='只在下車的那回合')], need=['HARLEQUINS']),
    ],
    # Eldritch Raiders
    '000001135': [
        R('No Prey Too Big', '戰略', [T('No Prey Too Big', 'att', [('wound', 1)], scope='ranged', cond='t_gt_t')], cp='1', names=['Corsair', 'Rangers', 'Shroud Runners']),
        R('Yriel’s Example', '戰略', [T('Yriel’s Example', 'def', [('fnp', 5)])], cp='1', need=['AELDARI', 'INFANTRY'], need_not=WC),
        R('Ruthless Killers', '戰略', [T('Ruthless Killers', 'att', [('dmg', 1)])], cp='1', need=['CORSAIR VOIDSCARRED']),
    ],
    # Corsair Coterie
    '000001136': [
        R('Pirates’ Due', '戰略', [T('Pirates’ Due', 'att', [('rr_wound', '1')], scope='melee')], cp='1', need=['AELDARI']),
        R('Pirates’ Due (Anhrathe)', '戰略', [T('Pirates’ Due', 'att', [('rr_wound', 'all')], scope='melee', why='只打在目標點範圍內的敵軍')], cp='1', need=['ANHRATHE']),
        R('Cloak and Shadow', '戰略', [T('Cloak and Shadow', 'def', [('cover', 1)], scope='ranged', why='要在自己控制的目標點範圍內；另限 18" 內才能被射擊（沒算）')], cp='1', need=['AELDARI', 'INFANTRY']),
        R('Relentless Raiders', '規則', [T('Relentless Raiders', 'def', [('mw_chg', 5 / 3)], scope='melee', why='在自己控制的目標點範圍內：對方衝鋒進來 2+ 吃 D3 致命傷')], on=False),
        R('Outcast Ambush', '戰略', [T('Outcast Ambush', 'att', [('kw', 'IGNORES COVER'), ('kw', 'RAPID FIRE 1'), ('ap', 1)], scope='ranged')], cp='1', names=['Rangers', 'Shroud Runners']),
    ],
    # Fateful Performance
    '000001201': [],   # movement / reserves / fight-on-death only
    # Path of the Outcast
    '000001202': [],   # detection range / movement / battle-shock only
    # Twilight Flickers
    '000001203': [
        R('Dance of Distortion', '規則', [T('Dance of Distortion', 'def', [('cover', 1)])], on=True, need=['HARLEQUINS'], note='Stealth 等於掩體'),
        R('Presaged Rehearsal', '戰略', [T('Presaged Rehearsal', 'att', [('kw', 'LANCE')], scope='melee')], cp='1', need=['TROUPE']),
    ],
}

ENH = {
    'Breath of Vaul': [T('Breath of Vaul', 'att', [('rr_dmg', 'all')], scope='ranged', weapon='fusion gun', on=False, why='要帶 Storm Guardians；fusion gun 重骰傷害骰（flamer 重骰攻擊數沒算）')],
    'Cegorach’s Coil': [T('Cegorach’s Coil', 'att', [('mw_pm', 0.5), ('mw_cap', 6)], scope='melee', cond='charge', on=True, why='衝鋒結束：這隊每個模型 4+ 造成 1 點致命傷，最多 6')],
    'Runes of Sanctuary (Psychic)': [T('Runes of Sanctuary', 'def', [('ap', -1)], scope='ranged', on=False, why='每回合一次，給 9" 內被選為目標的友軍')],
    'Grace of Khaine': [T('Grace of Khaine', 'att', [('rr_hit', '1'), ('rr_wound', '1'), ('rr_dmg', '1')], on=True, unitwide=False)],
    'Path of Eldanesh': [T('Path of Eldanesh', 'att', [('ap', 1)], scope='melee', on=False, unitwide=False, why='要在開艙門的那回合')],
    'Guiding Presence': [T('Guiding Presence', 'att', [('hit', 1)], scope='ranged', on=False, why='給 6" 內被選的友軍載具')],
    'Psychic Destroyer': [T('Psychic Destroyer', 'att', [('dmg', 1)], scope='ranged', wkw='PSYCHIC', on=True, unitwide=False)],
    'Mirage Field': [T('Mirage Field', 'def', [('hit', -1)], on=True)],
    'Seersight Strike': [T('Seersight Strike', 'att', [('kw', 'ANTI-MONSTER 2+'), ('kw', 'ANTI-VEHICLE 2+')], wkw='PSYCHIC', on=True, unitwide=False)],
    'Rune of Mists': [T('Rune of Mists', 'def', [('cover', 1)], scope='ranged', on=False, why='攻擊者在 18" 內則無效；給 12" 內被選的友軍')],
    'Murder’s Jest': [T('Murder’s Jest', 'att', [('crit_hit', 2)], on=False, unitwide=False, why='只打低於半數的目標；命中即暴擊，近似')],
    'Gaze of Ynnead': [T('Gaze of Ynnead', 'att', [('kw', 'DEVASTATING WOUNDS')], weapon='eldritch storm', on=True, unitwide=False)],
    'Borrowed Vigour': [T('Borrowed Vigour', 'att', [('attacks', 2)], scope='melee', on=True, unitwide=False)],
    'Morbid Might': [T('Morbid Might', 'att', [('rr_wound', 'all')], scope='melee', on=True, unitwide=False)],
    'Aspect of Murder': [T('Aspect of Murder', 'att', [('dmg', 1)], scope='melee', on=True, unitwide=False, why='Precision 沒算')],
    'Mantle of Wisdom': [T('Mantle of Wisdom', 'att', [('rr_hit', '1'), ('rr_wound', '1')], on=True, why='領 Aspect Warriors 時兩個都有')],
    'Shimmerstone': [T('Shimmerstone', 'def', [('wound', -1)], scope='ranged', on=True)],
    'Weavers’ Wail': [T('Weavers’ Wail', 'att', [('strength', 3), ('attacks', 1)], scope='melee', on=True, unitwide=False)],
    'Alacritous Assault': [T('Alacritous Assault', 'att', [('kw', 'LANCE')], scope='melee', on=True)],
    'Exotic Munitions': [T('Exotic Munitions', 'att', [('kw', 'ANTI-MONSTER 5+'), ('kw', 'ANTI-VEHICLE 5+')], scope='ranged', on=True)],
    'Voidstone': [T('Voidstone', 'def', [('inv', 5)], on=True)],
    'Assassins\' Eye': [T('Assassins\' Eye', 'att', [('ap', 1)], scope='ranged', tkw=['CHARACTER'], on=True)],
}
