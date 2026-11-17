from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

ARMY = {
    '000008359': dict(name='Dark Pacts', rules=[
        R('Dark Pacts', '軍隊規則', [
            T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], pick='pact', why='要過領導力測試，失敗吃 D3 致命傷（沒算）'),
            T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], pick='pact', why='要過領導力測試，失敗吃 D3 致命傷（沒算）'),
        ], on=True, note='每次射擊／近戰二選一，程式對每個目標自動挑好的；自傷風險未計入'),
    ]),
    # 000008428 Blessings of Khorne 寫在 WE.py
    # 000008396 Nurgle’s Gift 是死亡守衛的軍隊規則，寫在 DG.py
    # 000008424 Cabal of Sorcerers 寫在 TS.py
}

DET = {
    # Pactbound Zealots
    '000000751': [
        R('Marks of Chaos (Khorne)', '規則', [T('Marks of Chaos', 'att', [('crit_hit', 5)], scope='melee', why='要 Dark Pact 取得 Lethal Hits 且領導力通過')], need=['KHORNE']),
        R('Marks of Chaos (Slaanesh)', '規則', [T('Marks of Chaos', 'att', [('crit_hit', 5)], scope='melee', why='要 Dark Pact 取得 Sustained Hits 且領導力通過')], need=['SLAANESH']),
        R('Marks of Chaos (Tzeentch)', '規則', [T('Marks of Chaos', 'att', [('crit_hit', 5)], scope='ranged', why='要 Dark Pact 取得 Lethal Hits 且領導力通過')], need=['TZEENTCH']),
        R('Marks of Chaos (Nurgle)', '規則', [T('Marks of Chaos', 'att', [('crit_hit', 5)], scope='ranged', why='要 Dark Pact 取得 Sustained Hits 且領導力通過')], need=['NURGLE']),
        R('Marks of Chaos (Undivided)', '規則', [T('Marks of Chaos', 'att', [('rr_hit', '1')], why='要 Dark Pact 且領導力通過')], need=['CHAOS UNDIVIDED']),
        R('Profane Zeal', '戰略', [T('Profane Zeal', 'att', [('rr_wound', 'all')])], cp='1', need=['CHAOS UNDIVIDED']),
        R('Eye of the Gods', '戰略', [T('Eye of the Gods', 'att', [('attacks', 1), ('strength', 1), ('dmg', 1)], scope='melee', unitwide=False, once=True, why='只給那個角色模型；敵方單位被消滅後才能用')], cp='1', model_kw=['CHARACTER']),
        R('Festering Miasma', '戰略', [T('Festering Miasma', 'def', [('cover', 1)], why='Stealth；Nurgle 另有 18" 限制沒算')], cp='1'),
    ],
    # Veterans of the Long War
    '000000867': [
        R('Focus of Hatred', '規則', [T('Focus of Hatred', 'att', [('rr_hit', 'all')], why='只打被選的 focus of hatred')], need_not=['DAMNED']),
        R('Let the Galaxy Burn', '戰略', [T('Let the Galaxy Burn', 'att', [('kw', 'IGNORES COVER')], scope='ranged', why='Torrent 武器 Attacks 變 6 沒算')], cp='1', need_not=['TZEENTCH']),
        R('Contemptuous Disregard', '戰略', [T('Contemptuous Disregard', 'def', [('ap', -1)], scope='all')], cp='1', need_not=['DAMNED']),
        R('Black Crusade', '戰略', [T('Black Crusade', 'att', [('kw', 'DEVASTATING WOUNDS')], scope='ranged', weapon='bolt', why='bolt pistol/boltgun/combi-bolter；每回合最多 6 傷沒限制')], cp='1', need=['INFANTRY'], need_not=['DAMNED']),
    ],
    # Deceptors
    '000000868': [
        R('Pick Them Off', '戰略', [T('Pick Them Off', 'att', [('rr_hit', 'all')], scope='ranged', why='只打低於起始人數的目標'),
                                  T('Pick Them Off (wound)', 'att', [('rr_wound', 'all')], scope='ranged', why='目標低於半數才有')], cp='1'),
    ],
    # Renegade Raiders
    '000000869': [
        R('Raiders and Reavers', '規則', [T('Raiders and Reavers', 'att', [('ap', 1)], why='目標要在目標點範圍內')]),
        R('Unfailingly Obdurate', '戰略', [T('Unfailingly Obdurate', 'def', [('ap', -1)])], cp='1', need_not=['DAMNED']),
        R('Ruinous Raid', '戰略', [T('Ruinous Raid', 'att', [('rr_hit', 'all'), ('rr_wound', 'all')], why='目標要在目標點範圍內；單位本回合要從運輸載具下車')], cp='1'),
    ],
    # Dread Talons
    '000000870': [
        R('Pitiless Hunters', '戰略', [T('Pitiless Hunters', 'att', [('rr_hit', 'all'), ('rr_wound', 'all')], scope='ranged', why='只打 Battle-shocked 或低於半數的目標')], cp='1', need=['INFANTRY']),
        R('Depthless Cruelty', '戰略', [T('Depthless Cruelty', 'att', [('ap', 1)], why='只打 Battle-shocked 或低於半數的目標')], cp='1', need=['INFANTRY']),
    ],
    # Fellhammer Siege-host
    '000000871': [
        R('Iron Fortitude', '規則', [T('Iron Fortitude', 'def', [('wound', -1)], scope='ranged', cond='s_gt_t')], on=True, need_not=['DAMNED']),
        R('Pitiless Cannonade', '戰略', [T('Pitiless Cannonade', 'att', [('crit_hit', 5)], scope='ranged', why='只打低於半數的目標')], cp='1'),
        R('Persistent Assailants', '戰略', [T('Persistent Assailants', 'att', [('rr_hit', 'all')], scope='melee'),
                                          T('Persistent Assailants (wound)', 'att', [('rr_wound', 'all')], scope='melee', why='自己低於半數才有')], cp='1'),
        R('Steadfast Determination', '戰略', [T('Steadfast Determination', 'def', [('fnp', 5)], scope='ranged')], cp='1', need_not=['DAMNED']),
    ],
    # Chaos Cult
    '000000872': [
        R('Chosen for Glory', '戰略', [T('Chosen for Glory', 'att', [('rr_hit', 'all')]),
                                     T('Chosen for Glory (wound)', 'att', [('rr_wound', 'all')], why='Desperate Pact 領導力測試通過才有')], cp='1', need=['DAMNED']),
        R('Infernal Sacrifice', '戰略', [T('Infernal Sacrifice', 'att', [('attacks', 1)], scope='melee', why='Desperate Pact 另吃 D3 致命傷（沒算）'),
                                       T('Infernal Sacrifice (strength)', 'att', [('strength', 1)], scope='melee', why='領導力測試通過才有')], cp='1', need=['DAMNED']),
        R('Crazed Focus', '戰略', [T('Crazed Focus', 'att', [('ap', 1)], scope='ranged', why='要做 Desperate Pact'),
                                 T('Crazed Focus (strength)', 'att', [('strength', 1)], scope='ranged', why='領導力測試通過才有')], cp='1', need=['DAMNED']),
    ],
    # Soulforged Warpack
    '000000873': [
        R('Debt to the Soul Forge', '規則', [T('Debt to the Soul Forge (ranged)', 'att', [('wound', 1)], scope='ranged', why='要做 Dark Pact 並 invoke contract'),
                                           T('Debt to the Soul Forge (melee)', 'att', [('attacks', 2)], scope='melee', why='要做 Dark Pact 並 invoke contract')], need=['DAEMON', 'VEHICLE']),
        R('Desperate Pledge', '戰略', [T('Desperate Pledge', 'att', [('ap', 1)], why='要 invoke contract')], cp='1', need=['DAEMON', 'VEHICLE']),
    ],
    # Infernal Reavers
    '000000946': [],  # Dark Rewards 只有 CP；強化 Swollen with Power 是 T+1 沒有標記可用
    # (strategems below attached via second key not allowed; see ENH/notes)
    # Underdeck Uprising
    '000000947': [
        R('Fleeting Might', '戰略', [T('Fleeting Might', 'att', [('kw', 'DEVASTATING WOUNDS')], why='要剛做完 Dark Pact')], cp='1', need=['DAMNED']),
        R('Infernal Altars', '戰略', [T('Infernal Altars', 'def', [('fnp', 5)], why='要在目標點範圍內')], cp='1', need=['DAMNED'], need_not=['CULTIST MOB']),
        R('Infernal Altars (Cultist Mob)', '戰略', [T('Infernal Altars', 'def', [('fnp', 4)], why='要在目標點範圍內')], cp='1', need=['DAMNED', 'CULTIST MOB']),
    ],
    # Champions of Chaos
    '000000948': [
        R('Imperious Advance', '戰略', [T('Imperious Advance', 'att', [('attacks', 1)], scope='melee', why='只給選定的模型；只能打艙門另一側的敵人')], cp='1', need=['TERMINATOR']),
    ],
    # Creations of Bile
    '000000991': [
        R('Cholinergic Accelerants', '規則', [T('Cholinergic Accelerants', 'att', [('attacks', 1)], scope='melee', why='戰前選的強化（選一或骰兩個）')], need=['INFANTRY'], need_not=['DAMNED']),
        R('Macrotensile Sinews', '規則', [T('Macrotensile Sinews', 'att', [('strength', 1)], scope='melee', why='戰前選的強化（選一或骰兩個）')], need=['INFANTRY'], need_not=['DAMNED']),
        R('Paraneural Reactions', '規則', [T('Paraneural Reactions', 'att', [('skill', 1)], scope='melee', why='戰前選的強化（選一或骰兩個）')], need=['INFANTRY'], need_not=['DAMNED']),
        R('Ophthalmic Enhancement', '規則', [T('Ophthalmic Enhancement', 'att', [('skill', 1)], scope='ranged', why='戰前選的強化（選一或骰兩個）')], need=['INFANTRY'], need_not=['DAMNED']),
        R('Specimens for the Spider', '戰略', [T('Specimens for the Spider', 'att', [('rr_wound', 'all')], scope='melee', tkw=['CHARACTER'])], cp='2', need=['INFANTRY']),
        R('Monstrous Visages', '戰略', [T('Monstrous Visages', 'def', [('hit', -1)])], cp='1', need=['INFANTRY']),
    ],
    # Cabal of Chaos
    '000001058': [
        R('Empyric Wellspring (Psyker)', '規則', [T('Empyric Wellspring', 'att', [('strength', 1)], scope='ranged', why='要做 Dark Pact')], need=['PSYKER'], need_not=['DAEMON']),
        R('Empyric Wellspring (Daemon Prince)', '規則', [T('Empyric Wellspring', 'att', [('strength', 2), ('ap', 1)], scope='melee', why='要做 Dark Pact')], names=['Daemon Prince'], need_not=['KHORNE']),
        R('Wreathed in Warpflame', '戰略', [T('Wreathed in Warpflame', 'att', [('kw', 'IGNORES COVER')], scope='ranged')], cp='1', need=['PSYKER']),
    ],
    # Nightmare Hunt
    '000001122': [
        R('Terror Made Manifest (hit)', '規則', [T('Terror Made Manifest', 'att', [('hit', 1)], why='只打低於半數的目標')]),
        R('Terror Made Manifest (wound)', '規則', [T('Terror Made Manifest', 'att', [('wound', 1)], why='只打 Battle-shocked 的目標')]),
        R('Terror Made Manifest (defence)', '規則', [T('Terror Made Manifest', 'def', [('hit', -1)], why='攻擊者要是 Battle-shocked')]),
        R('Prey on the Weak', '戰略', [T('Prey on the Weak', 'att', [('rr_hit', 'all')], why='只打 Battle-shocked 或低於半數的目標')], cp='1', need=['INFANTRY']),
        R('Talons Sunk Deep', '戰略', [T('Talons Sunk Deep', 'att', [('ap', 1)], why='只打 Battle-shocked 或低於半數的目標')], cp='1', need=['INFANTRY']),
    ],
    # Huron's Marauders
    '000001133': [
        R('Huron’s Elite', '規則', [T('Huron’s Elite', 'att', [('hit', 1)], why='要選此能力，且單位在 Huron Blackheart 視線內')], need=['INFANTRY']),
        R('Reavers’ Flurry', '戰略', [T('Reavers’ Flurry', 'att', [('attacks', 1)], scope='melee', why='本回合衝鋒過')], cp='1'),
        R('Hardened Killers (BS)', '戰略', [T('Hardened Killers', 'att', [('skill', 1)], scope='ranged', why='三選一效果')], cp='1', need=['DAMNED']),
        R('Hardened Killers (Save)', '戰略', [T('Hardened Killers', 'def', [('sv', 1)], why='三選一效果')], cp='1', need=['DAMNED']),
    ],
    # Renegade Warband
    '000001134': [
        R('Vendetta', '規則', [T('Vendetta', 'att', [('rr_hit', 'all')], why='只打 Vendetta 目標')], need_not=['DAMNED']),
        R('Corrupted Munitions', '戰略', [T('Corrupted Munitions', 'att', [('ap', 1)], scope='ranged')], cp='1'),
        R('Vengeful Destruction', '戰略', [T('Vengeful Destruction', 'att', [('wound', 1)], why='只打 Vendetta 目標；Mounted 單位也可用但沒限定')], cp='1', need_not=['DAMNED']),
        R('Never Outgunned', '戰略', [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], pick='outgunned'),
                                    T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], pick='outgunned')], cp='1'),
    ],
    # Warpstrike Champions
    '000001141': [
        R('Empyric Dislocation', '戰略', [T('Empyric Dislocation', 'def', [('ap', -1)])], cp='1', need_not=['DAMNED']),
        R('Siegebreaker Strike', '戰略', [T('Siegebreaker Strike', 'att', [('kw', 'IGNORES COVER')], scope='ranged', why='要本回合 Deep Strike 登場')], cp='1'),
        R('Armour of Corruption', '戰略', [T('Armour of Corruption', 'def', [('dmg', -1)])], cp='2', names=['Terminator', 'Obliterator', 'Mutilator']),
    ],
    # Cult of the Arkifane
    '000001142': [
        R('Soul Forge Boons', '規則', [T('Soul Forge Boons', 'def', [('inv', 5)])], on=True, need=['VEHICLE'],
          note='Soul Forge 單位 = 載具、Lord Discordant、Vashtorr；Vashtorr 若不是 VEHICLE 沒算到'),
        R('Soul-Tally Offering', '戰略', [T('Soul-Tally Offering', 'att', [('rr_wound', 'all')], tkw=['CHARACTER', 'MONSTER', 'VEHICLE'])], cp='2', need=['VEHICLE']),
        R('Touch of the Arkifane', '戰略', [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], why='要做 Dark Pact，兩個能力都拿'),
                                          T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], why='要做 Dark Pact，兩個能力都拿')], cp='1', need_not=['DAMNED']),
        R('Balefire Boon', '戰略', [T('Balefire Boon', 'att', [('ap', 1)])], cp='1', need=['VEHICLE']),
    ],
    # Devotees of Destruction
    '000001183': [
        R('Rain of Ruin (Havocs)', '規則', [T('Heavy', 'att', [('hit', 1)], scope='ranged', cond='still')], on=True, need=['HAVOCS']),
        R('Rain of Ruin (Obliterators)', '規則', [T('Heavy', 'att', [('hit', 1)], scope='ranged', cond='still')], on=True, need=['OBLITERATORS']),
        R('Undying Hatred', '戰略', [T('Undying Hatred', 'def', [('wound', -1)], scope='ranged', cond='s_gt_t')], cp='1', need=['HAVOCS']),
        R('Ruination’s Bounty', '戰略', [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='ranged', pick='bounty', why='要用 Dark Pacts'),
                                       T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', pick='bounty', why='要用 Dark Pacts')], cp='1', need=['HAVOCS']),
    ],
    # Murdertalon Raiders
    '000001184': [
        R('Prey on the Weak (attack)', '規則', [T('Prey on the Weak', 'att', [('rr_hit', '1')], why='只打 Battle-shocked 或半數以下的目標')], need=['INFANTRY', 'FLY']),
        R('Prey on the Weak (defence)', '規則', [T('Prey on the Weak', 'def', [('hit', -1)], why='攻擊者要是 Battle-shocked 或半數以下')], need=['INFANTRY', 'FLY']),
        R('Plunging Talons', '戰略', [T('Plunging Talons', 'att', [('kw', 'LANCE')], scope='melee', why='要本回合衝鋒過')], cp='1', need=['INFANTRY', 'FLY']),
    ],
}
# 注：000000946 Infernal Reavers 的戰略（Low Cunning、Inveterate Murderers）見下方補充
DET['000000946'] = [
    R('Low Cunning', '戰略', [T('Low Cunning', 'def', [('wound', -1)], cond='s_gt_t')], cp='1', need_not=['DAMNED']),
    R('Inveterate Murderers', '戰略', [T('Inveterate Murderers', 'att', [('wound', 1)], scope='melee', why='只在攻擊 S ≤ 目標 T 時才有（程式無此條件，請自行判斷）')], cp='1', need_not=['DAMNED']),
]

ENH = {
    'Warp Tracer': [T('Warp Tracer', 'att', [('kw', 'IGNORES COVER')], scope='ranged', on=False, why='帶的模型射完後選一隊被打中的：本階段不能有掩體（實際全軍打它都算，這裡只給帶的這隊）')],
    'Intoxicating Elixir': [T('Intoxicating Elixir', 'def', [('fnp', 5)], on=True, unitwide=False)],
    'Talisman of Burning Blood': [T('Talisman of Burning Blood', 'att', [('attacks', 1), ('strength', 1)], scope='melee', on=True, unitwide=False, why='Dark Pact 後改為 D3 加成沒算')],
    'Eager for Vengeance': [T('Eager for Vengeance', 'att', [('hit', 1)], on=False, why='只打 focus of hatred，且本回合 Fell Back')],
    'Warmaster’s Gift': [T('Warmaster’s Gift', 'att', [('crit_wound', 5)], on=False, unitwide=False, why='只打 focus of hatred')],
    'Cursed Fang': [T('Cursed Fang', 'att', [('ap', 1)], scope='melee', on=True, unitwide=False)],
    'Shroud of Obfuscation': [T('Shroud of Obfuscation', 'def', [('cover', 1)], on=True, unitwide=False, why='Stealth')],
    'Dread Reaver': [T('Dread Reaver', 'att', [('rr_hit', 'all'), ('rr_wound', 'all')], scope='melee', on=False, unitwide=False, why='要在敵方部署區 12" 內')],
    'Night’s Shroud': [T('Night’s Shroud', 'def', [('cover', 1)], on=True, why='Stealth')],
    'Iron Artifice': [T('Iron Artifice', 'att', [('kw', 'ANTI-VEHICLE 4+'), ('kw', 'ANTI-FORTIFICATION 4+')], on=True, unitwide=False)],
    'Ironbound Enmity': [T('Ironbound Enmity', 'att', [('wound', 1)], on=False, unitwide=False, why='要在目標點範圍內')],
    'Incendiary Goad': [T('Incendiary Goad', 'att', [('strength', 1)], scope='melee', on=False, why='單位低於起始人數；半數以下再 +1 Attacks；只給 DAMNED 模型')],
    'Voice of the Octed': [T('Voice of the Octed', 'att', [('kw', 'LETHAL HITS'), ('kw', 'SUSTAINED HITS 1')], on=False, why='要做 Dark Pact，兩個能力都拿')],
    'Dark Majesty': [T('Dark Majesty', 'def', [('hit', -1)], on=False, why='只對被 stunned 的敵方單位（衝鋒後選一隊）')],
    'Living Carapace': [T('Living Carapace', 'def', [('fnp', 5)], on=True, unitwide=False)],
    'Prime Test Subject': [T('Prime Test Subject', 'att', [('dmg', 1), ('rr_hit', 'all')], scope='melee', on=True, unitwide=False)],
    'Conduit of Chaos': [T('Conduit of Chaos', 'att', [('kw', 'LANCE')], scope='melee', on=True, unitwide=False, why='Lance 只在衝鋒時有效')],
    'Greyveil Hex': [T('Greyveil Hex', 'def', [('cover', 1)], on=True, why='Stealth；掌控目標點時另有 18" 限制沒算')],
    'Voice of the Tyrant': [T('Voice of the Tyrant', 'att', [('hit', 1)], on=True, why='同時有 Huron’s Elite 和 Mobile Marauders')],
    'Eyes of the Hunter': [T('Eyes of the Hunter', 'att', [('kw', 'IGNORES COVER')], scope='ranged', on=True)],
    'Fratricidal Trophies': [T('Fratricidal Trophies', 'att', [('rr_hit', 'all')], on=False, why='要本回合選擇 Default to Doctrine')],
    'Tzagulla': [T('Tzagulla', 'att', [('attacks', 1), ('strength', 1), ('ap', 1)], on=True, unitwide=False),
                 T('Tzagulla (arrival)', 'att', [('dmg', 1)], on=False, unitwide=False, why='只在本回合從預備隊登場後')],
    'Mark of the Soul Forges': [T('Mark of the Soul Forges', 'att', [('crit_hit', 5)], on=True, unitwide=False)],
    'Shadowcowl Talisman': [T('Shadowcowl Talisman', 'def', [('inv', 5)], on=True, unitwide=False)],
    'Pact of Cursed Pinions': [T('Pact of Cursed Pinions', 'att', [('attacks', 1)], scope='melee', on=True, unitwide=False)],
}
