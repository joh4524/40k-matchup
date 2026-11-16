from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

ARMY = {
    # Power from Pain：Pain 能力原文沒寫在這裡，不標記
    # Battle Focus / Disparate Paths / Corsairs and Travelling Players：不影響傷害
}

DET = {
    # Skysplinter Assault
    '000000831': [
        R('Rain Of Cruelty (ranged)', '規則', [T('Rain Of Cruelty', 'att', [('kw', 'IGNORES COVER')], scope='ranged', why='只在本回合剛下載的單位')], need=['DRUKHARI']),
        R('Rain Of Cruelty (melee)', '規則', [T('Rain Of Cruelty', 'att', [('kw', 'LANCE')], scope='melee', why='只在本回合剛下載的單位')], need=['DRUKHARI']),
        R('Skyborne Annihilation', '戰略', [T('Skyborne Annihilation', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged')], cp='1', need=['DRUKHARI'], names_not=['Kabalite Warriors', 'Hand of the Archon']),
        R('Skyborne Annihilation (Kabalite/Hand)', '戰略', [T('Skyborne Annihilation', 'att', [('kw', 'SUSTAINED HITS 2')], scope='ranged')], cp='1', need=['DRUKHARI'], names=['Kabalite Warriors', 'Hand of the Archon']),
        R('Night Shield', '戰略', [T('Night Shield', 'def', [('inv', 4)], scope='ranged')], cp='1', need=['DRUKHARI', 'VEHICLE']),
        # Vicious Blades（致命傷數量看艙內模型）、Pounce、Swooping、Wraithlike：不標記
    ],
    # Space Lane Raiders
    '000000934': [
        R('Crew-Thieves', '戰略', [T('Crew-Thieves', 'att', [('kw', 'ANTI-INFANTRY 3+')], scope='melee')], cp='1', need=['WRACKS']),
        R('Shipboard Shades', '戰略', [T('Shipboard Shades', 'def', [('hit', -1)])], cp='1', need=['DRUKHARI']),
    ],
    # Kabalite Corsairs
    '000000935': [
        R('Deckplate Sweepers', '戰略', [T('Deckplate Sweepers', 'att', [('ap', 1)], scope='ranged', weapon='splinter', why='只限 splinter cannon／rifle／pistol')], cp='1', need=['KABAL']),
        R('Elusive Duellists', '戰略', [T('Elusive Duellists', 'def', [('hit', -1)])], cp='1', need=['DRUKHARI']),
        R('Elusive Duellists (Incubi)', '戰略', [T('Elusive Duellists', 'def', [('inv', 4)])], cp='1', need=['INCUBI']),
    ],
    # Ship-killer Cult
    '000000936': [
        R('Appetite for Adulation', '規則', [T('Appetite for Adulation', 'att', [('kw', 'ANTI-INFANTRY 4+')], scope='melee', why='要在 Fight phase 被 Empower')], need=['WYCH CULT']),
        R('Hyperagility', '戰略', [T('Hyperagility', 'def', [('hit', -1), ('wound', -1)])], cp='1', need=['WYCH CULT']),
    ],
    # Painbringers
    '000000937': [
        R('Moulded Musculature', '戰略', [T('Moulded Musculature', 'att', [('strength', 1), ('ap', 1)], scope='melee', why='只給選定的模型；且必須打 Hatchway 另一側的敵人')], cp='1', need=['HAEMONCULUS COVENS']),
        # Unfeeling Abominations / Terrifying Aura / Horrifying Form：不標記
        # 強化 Rending Chain-Flails、Vile Surgeon（原文未給基礎傷害）不標記
    ],
    # Reaper's Wager
    '000000993': [
        R('Callous Competition (winning)', '規則', [T('Callous Competition (winning)', 'att', [('rr_hit', '1')], why='Drukhari 領先賭局時；起始為 Drukhari 領先')], on=True),
        R('Callous Competition (losing)', '規則', [T('Callous Competition (losing)', 'att', [('rr_hit', '1'), ('rr_wound', '1')], why='落後賭局時（取代領先的效果）')]),
        R('Murderer’s Circus', '戰略', [T('Murderer’s Circus', 'def', [('hit', -1)], scope='melee')], cp='1'),
        R('Malicious Frenzy', '戰略', [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], pick='frenzy'),
                                     T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], pick='frenzy')], cp='1'),
        # Fateful Role、Shorten the Odds、Dance Macabre、Scintillating Tempo：不標記
    ],
    # Realspace Raiders
    '000000804': [
        R('Insensible to Pain', '戰略', [T('Insensible to Pain', 'def', [('dmg', -1)])], cp='2', need=['HAEMONCULUS COVENS']),
        R('Instinctive Spite (hit)', '戰略', [T('Instinctive Spite', 'att', [('hit', 1)], why='只打低於半數的敵人')], cp='1', need=['DRUKHARI']),
        R('Instinctive Spite (wound, 1 Pain)', '戰略', [T('Instinctive Spite', 'att', [('wound', 1)], why='花 1 Pain token；只打低於半數的敵人')], cp='0', need=['DRUKHARI']),
        R('Fighting Shadows', '戰略', [T('Fighting Shadows', 'def', [('hit', -1)])], cp='1', need=['DRUKHARI'], need_not=['HAEMONCULUS COVENS']),
        R('Dark Harvest', '戰略', [T('Dark Harvest', 'att', [('kw', 'LETHAL HITS')], scope='melee')], cp='1', need=['DRUKHARI']),
        # Eager for the Kill、Raid and Fade：移動
    ],
    # Spectacle of Spite
    '000001113': [
        R('Combat Drug: Adrenalight', '規則', [T('Adrenalight', 'att', [('attacks', 1)], scope='melee', why='開始指揮階段選定的戰鬥藥')], need=['WYCH CULT']),
        R('Combat Drug: Serpentin', '規則', [T('Serpentin', 'att', [('skill', 1)], scope='melee', why='開始指揮階段選定的戰鬥藥')], need=['WYCH CULT']),
        R('Combat Drug: Grave Lotus', '規則', [T('Grave Lotus', 'att', [('strength', 1)], scope='melee', why='開始指揮階段選定的戰鬥藥')], need=['WYCH CULT']),
        R('Combat Drug: Splintermind', '規則', [T('Splintermind', 'att', [('skill', 1)], scope='ranged', why='開始指揮階段選定的戰鬥藥')], need=['WYCH CULT']),
        # Hypex、Painbringer(T+1 程式無對應)：不標記
        R('Acrobatic Display', '戰略', [T('Acrobatic Display', 'def', [('inv', 5)], scope='ranged')], cp='1', need=['WYCH CULT']),
        R('Deadly Debut', '戰略', [T('Deadly Debut', 'att', [('kw', 'LETHAL HITS')], scope='melee', cond='charge')], cp='1', need=['DRUKHARI']),
        R('Deadly Debut (Wyches)', '戰略', [T('Deadly Debut', 'att', [('ap', 1)], scope='melee', cond='charge')], cp='1', need=['DRUKHARI'], names=['Wyches']),
    ],
    # Covenite Coterie
    '000001114': [
        R('Stitchflesh Abominations', '規則', [T('Stitchflesh Abominations', 'def', [('wound', -1)], cond='s_gt_t')], on=True, need=['HAEMONCULUS COVENS']),
        R('Connoisseurs of Pain', '戰略', [T('Connoisseurs of Pain', 'def', [('ap', -1)])], cp='1', need=['DRUKHARI'], note='需花 1 Pain token'),
        R('Distillers of Fear', '戰略', [T('Distillers of Fear', 'att', [('kw', 'DEVASTATING WOUNDS')], why='只打 Battle-shocked 的目標')], cp='2', need=['HAEMONCULUS COVENS']),
        # Poisoner’s Art、Symphony、Postmortality、Enfolding：不標記
    ],
    # Kabalite Cartel
    '000001115': [
        R('Murderous Agenda', '規則', [T('Sow Fear and Terror', 'att', [('kw', 'SUSTAINED HITS 1')], tkw=['INFANTRY', 'MOUNTED'], pick='contract', why='選此 Contract 時'),
                                     T('Show of Strength', 'att', [('kw', 'LETHAL HITS')], tkw=MV, pick='contract', why='選此 Contract 時')],
          need=['KABAL'], note='三個 Contract 擇一；Trophy Hunters 的 PRECISION 不算；Blades for Hire 單位未納入'),
        R('Taken Alive', '戰略', [T('Taken Alive', 'att', [('hit', 1)], scope='melee')], cp='1', need=['DRUKHARI']),
        R('Making a Point', '戰略', [T('Making a Point', 'att', [('skill', 1), ('ap', 1)], scope='ranged')], cp='1', names=['Kabalite Warriors', 'Hand of the Archon']),
        R('Tailored Toxins', '戰略', [T('Tailored Toxins', 'att', [('crit_hit', 5)], why='只打 Contract 單位')], cp='1', need=['KABAL']),
        # Double-Cross、Deadly Deceivers、Enemies Without Number：不標記；Leechbite Plate(Sv 3+) 不標記
    ],
    # Exhibition of Slaughter
    '000001185': [
        R('Exacting Cruelty', '規則', [T('Exacting Cruelty', 'att', [('kw', 'LETHAL HITS')], scope='melee', tkw_not=MV)], on=True, need=['WYCH CULT']),
        R('Acrobatic Display', '戰略', [T('Acrobatic Display', 'def', [('inv', 5)], scope='ranged')], cp='1', need=['WYCH CULT']),
        R('Planned Strikes', '戰略', [T('Planned Strikes', 'att', [('kw', 'LETHAL HITS')], scope='melee')], cp='1', need=['WYCH CULT']),
    ],
    # Kabalite Agonysts
    '000001186': [
        R('Contracted Harvest (Kabal)', '規則', [T('Contracted Harvest', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', tkw_not=MV)], on=True, need=['KABAL']),
        R('Contracted Harvest (Blades for Hire)', '規則', [T('Contracted Harvest', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', tkw_not=MV)], on=True, need=['BLADES FOR HIRE']),
        R('Prioritised Victim', '戰略', [T('Prioritised Victim', 'att', [('rr_hit', '1'), ('rr_wound', '1')], tkw=['CHARACTER'])], cp='1', note='原文限 BLADES FOR HIRE／KABAL 單位，這裡未限制'),
        R('Killers from the Dark Spires', '戰略', [T('Killers from the Dark Spires', 'att', [('kw', 'IGNORES COVER')], scope='ranged')], cp='1', need=['KABALITE WARRIORS']),
    ],
    # Tools of Torment
    '000001187': [
        R('Darkest Artifice', '規則', [T('Darkest Artifice', 'def', [('wound', -1)], cond='s_gt_t')], on=True, names=['Cronos', 'Talos']),
        R('Salting the Wound', '戰略', [T('Salting the Wound', 'att', [('kw', 'DEVASTATING WOUNDS')], why='只打 Battle-shocked 的目標')], cp='1', names=['Cronos', 'Talos']),
    ],
}

ENH = {
    'Phantasmal Smoke': [T('Phantasmal Smoke', 'def', [('cover', 1)], scope='ranged', on=False, why='要在友方 Drukhari Transport 6" 內')],
    'Eye of Spite': [T('Eye of Spite', 'att', [('attacks', 1), ('ap', 1)], scope='melee', on=True, unitwide=False),
                     T('Eye of Spite (1 Pain)', 'att', [('attacks', 1), ('ap', 1)], scope='melee', on=False, unitwide=False, why='花 1 Pain token：改為 +2（此處是在上面 +1 之外再加 +1）')],
    "Morghenna’s Curse": [T('Morghenna’s Curse', 'att', [('ap', 1), ('dmg', 1)], scope='melee', on=True, unitwide=False)],
    'Master Nemesine': [T('Master Nemesine', 'att', [('kw', 'ANTI-BEAST 2+'), ('kw', 'ANTI-MONSTER 4+')], on=True, unitwide=False)],
    'Gnarlskin Experimentor': [T('Gnarlskin Experimentor', 'def', [('wound', -1)], cond='s_gt_t', on=True)],
    'Elixir of the Corpse Courts': [T('Elixir of the Corpse Courts', 'def', [('inv', 5)], on=True)],
}
