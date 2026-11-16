from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

EC = ['EMPEROR’S CHILDREN']

ARMY = {}   # Thrill Seekers 只有移動／射擊資格，Pact of Excess 只有組軍限制，都不影響傷害

DET = {
    # Mercurial Host
    '000001033': [
        R('Capricious Reactions', '戰略', [T('Capricious Reactions', 'def', [('hit', -1)], scope='ranged')], cp='1', need=EC),
        R('Combat Stimms', '戰略', [T('Combat Stimms', 'def', [('wound', -1)], scope='melee')], cp='2', need=EC + ['INFANTRY']),
        R('Violent Excess', '戰略', [T('Violent Excess', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee')], cp='1', need=EC),
    ],
    # Peerless Bladesmen
    '000001034': [
        R('Exquisite Swordsmanship', '規則', [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='melee', cond='charge', pick='swords'),
                                            T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee', cond='charge', pick='swords')],
          on=True, need=EC, note='衝鋒後打架二選一，程式對每個目標自動挑好的'),
        R('Cruel Bladesman', '戰略', [T('Cruel Bladesman', 'att', [('ap', 1)], scope='melee', cond='charge')], cp='1', need=EC),
        R('Deft Parry', '戰略', [T('Deft Parry', 'def', [('hit', -1)], scope='melee')], cp='1', need=EC),
    ],
    # Rapid Evisceration
    '000001035': [
        R('Mechanised Murder', '規則', [T('Mechanised Murder', 'att', [('rr_hit', '1'), ('rr_wound', '1')], why='只限 Transport 模型或本回合從 Transport 下車的單位')], need=EC),
    ],
    # Carnival of Excess
    '000001036': [
        R('Daemonic Empowerment', '規則', [T('Daemonic Empowerment', 'att', [('kw', 'SUSTAINED HITS 1')], why='要在 6" 內有友方 Legions of Excess／Emperor’s Children；已有 Sustained 的武器改為 5+ 爆擊，這裡未算')],
          note='Emperor’s Children 或 Legions of Excess 單位皆適用，所以不限關鍵字'),
        R('Uncanny Reactions', '戰略', [T('Uncanny Reactions', 'def', [('hit', -1)], scope='ranged')], cp='1', need=['SLAANESH']),
    ],
    # Coterie of the Conceited
    '000001037': [
        R('Pledges: 1+ Pact points', '規則', [T('Pact 1+', 'att', [('rr_hit', '1')], why='要累積 1+ Pact points')], need=EC),
        R('Pledges: 3+ Pact points', '規則', [T('Pact 3+', 'att', [('rr_wound', '1')], why='要累積 3+ Pact points')], need=EC),
        R('Pledges: 5+ Pact points', '規則', [T('Pact 5+', 'att', [('kw', 'LETHAL HITS'), ('kw', 'SUSTAINED HITS 1')], scope='melee', why='要累積 5+ Pact points')], need=EC),
        R('Pledges: 7+ Pact points', '規則', [T('Pact 7+', 'att', [('crit_hit', 5)], why='要累積 7+ Pact points')], need=EC),
        R('Martial Perfection', '戰略', [T('Martial Perfection', 'att', [('rr_hit', 'all')])], cp='1', need=EC),
        R('Unshakeable Opponents', '戰略', [T('Unshakeable Opponents', 'att', [('ign', 1)])], cp='1', need=EC),
        R('Protection of the Dark Prince', '戰略', [T('Protection of the Dark Prince', 'def', [('fnp', 6)], why='對致命傷是 4+，這裡只算一般攻擊')], cp='1', need=EC),
        R('Armour of Abhorrence', '戰略', [T('Armour of Abhorrence', 'def', [('ap', -1)])], cp='1', need=EC),
    ],
    # Slaanesh’s Chosen
    '000001038': [
        R('Internal Rivalries', '規則', [T('Favoured Champions', 'att', [('rr_wound', 'all')], why='只限目前的 Favoured Champions 單位')], need=EC + ['CHARACTER']),
        R('Heightened Jealousy', '戰略', [T('Heightened Jealousy', 'att', [('strength', 1)], why='給其他非 Favoured Champions 的 EC CHARACTER')], cp='1', need=EC + ['CHARACTER']),
        R('Devoted Duellists', '戰略', [T('Devoted Duellists', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee', why='只打被選的那一隊')], cp='1', need=EC + ['CHARACTER']),
    ],
    # Court of the Phoenician
    '000001125': [
        R('Sensational Performance', '規則', [T('Sensational Performance', 'att', [('strength', 1), ('ap', 1)], scope='melee', cond='charge',
                                               why='要選擇使用；不能打開打前就接觸的目標，也不能打已被其他單位攻擊的目標')], need=EC),
        R('Close-Quarters Excruciation', '戰略', [T('Close-Quarters Excruciation', 'att', [('strength', 1), ('ap', 1)], scope='ranged', why='只限 12" 內的目標')], cp='1', need=EC),
        R('Prideful Superiority', '戰略', [T('Prideful Superiority', 'att', [('rr_hit', 'all'), ('rr_wound', 'all')], tkw=['CHARACTER'])], cp='2', need=EC),
        R('Contemptuous Disregard', '戰略', [T('Contemptuous Disregard', 'def', [('wound', -1)], cond='s_gt_t')], cp='1', need=EC),
    ],
    # Sublime Strike
    '000001154': [
        R('Alluring Grotesquerie', '戰略', [T('Alluring Grotesquerie', 'def', [('hit', -1)], scope='melee')], cp='1', need=EC),
    ],
    # Elegant Brutes
    '000001180': [
        R('Delight in Agony', '戰略', [T('Delight in Agony', 'def', [('wound', -1)], cond='s_gt_t')], cp='1', need=EC + ['TERMINATOR']),
        R('Psychedelic Soulflame', '戰略', [T('Psychedelic Soulflame', 'att', [('strength', 2)])], cp='1', need=EC + ['TERMINATOR']),
    ],
    # Frenzied Host
    '000001181': [
        R('Frantic Focus', '規則', [T('Frantic Focus', 'att', [('kw', 'SUSTAINED HITS 1')], why='只在該單位前進／撤退的回合，且只給 BATTLELINE 模型')],
          need=EC + ['BATTLELINE'], model_kw=['BATTLELINE']),
        R('Possessive Mania', '戰略', [T('Possessive Mania', 'def', [('ap', -1)], why='單位要在目標點範圍內')], cp='1', need=EC + ['BATTLELINE']),
    ],
    # Spectacle of Slaughter：Fights First、Precision、移動，都不影響傷害期望
    '000001182': [],
}

ENH = {
    # Mercurial Host
    'Steeped in Suffering': [T('Steeped in Suffering (hit)', 'att', [('hit', 1)], why='目標低於起始人數才有效'),
                             T('Steeped in Suffering (wound)', 'att', [('wound', 1)], why='目標低於半數兵力才有效')],
    'Intoxicating Musk': [T('Intoxicating Musk', 'def', [('wound', -1)], scope='melee', cond='s_gt_t', on=True)],
    # Peerless Bladesmen
    'Distortion': [T('Distortion', 'att', [('attacks', 1), ('dmg', 1)], scope='melee', on=True, unitwide=False)],
    # Carnival of Excess
    'Dark Blessings': [T('Dark Blessings', 'def', [('inv', 3)], on=True, once=True, unitwide=False)],
    'Possessed Blade': [T('Possessed Blade (attacks)', 'att', [('attacks', 1)], scope='melee', on=True, unitwide=False, why='只加在選定的一把近戰武器，這裡近似為全部近戰武器'),
                        T('Possessed Blade (fight)', 'att', [('dmg', 1), ('kw', 'DEVASTATING WOUNDS')], scope='melee', on=True, unitwide=False,
                          why='選定武器；每次打架可選擇使用，Hazardous 風險沒算')],
    # Coterie of the Conceited：Pledge of Unholy Fortune／Mortal Pain 不算
    # Slaanesh’s Chosen
    'Slayer of Champions': [T('Slayer of Champions', 'att', [('strength', 1), ('ap', 1)], scope='melee', tkw=['CHARACTER'], on=True, unitwide=False)],
    # Court of the Phoenician
    'Tears of the Phoenix': [T('Tears of the Phoenix', 'att', [('ign', 1)], scope='melee', on=True)],
    'Spiritsliver': [T('Spiritsliver', 'att', [('strength', 1), ('attacks', 1)], scope='melee', on=True, unitwide=False)],
    # Sublime Strike
    'Venom of the Six-fanged Serpent': [T('Venom of the Six-fanged Serpent', 'att', [('strength', 1), ('dmg', 1), ('ap', 2)], scope='melee', on=True, unitwide=False)],
    # Elegant Brutes
    'Cacophonic Accompaniment': [T('Cacophonic Accompaniment', 'att', [('kw', 'IGNORES COVER')], scope='ranged', on=True)],
    'Frenzied Ferocity': [T('Frenzied Ferocity', 'att', [('kw', 'SUSTAINED HITS 1')], on=True)],
    # Frenzied Host
    'Euphoric Crown': [T('Euphoric Crown', 'att', [('strength', 1)], scope='melee', on=True, unitwide=False)],
    'Howling Plate': [T('Howling Plate', 'att', [('ap', 1)], scope='ranged', on=True)],
}
