from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

HYB = ['Acolyte Hybrids', 'Hybrid Metamorphs', 'Neophyte Hybrids']
ABR = ['Aberrants', 'Biophagus', 'Purestrain']
KIL = ['Kelermorph', 'Locus', 'Reductus', 'Sanctus']

ARMY = {
    # Synapse 只給 TYRANIDS 陣營；Cult Ambush 是增援，都不影響傷害
}

DET = {
    # Host of Ascension
    '000000884': [
        R('A Perfect Ambush', '規則', [T('A Perfect Ambush', 'att', [('kw', 'SUSTAINED HITS 1'), ('kw', 'IGNORES COVER')], why='只限剛以增援登場、到下個近戰階段結束')], need=['GENESTEALER CULTS']),
        R('Primed and Readied', '戰略', [T('Primed and Readied', 'att', [('crit_hit', 5)])], cp='2', need=['GENESTEALER CULTS']),
        R('Coordinated Trap', '戰略', [T('Coordinated Trap', 'att', [('wound', 1)], why='只打被選的那一隊')], cp='2', need=['GENESTEALER CULTS']),
        # A Deadly Snare：對衝鋒者造成致命傷，非攻擊，不算
    ],
    # Xenocreed Congregation
    '000000885': [
        R('Unquestioning Fanaticism (Magus)', '規則', [T('Unquestioning Fanaticism', 'def', [('fnp', 3)], why='帶領該隊時')], on=True, model_kw=['MAGUS']),
        R('Unquestioning Fanaticism (Primus)', '規則', [T('Unquestioning Fanaticism', 'def', [('fnp', 3)], why='帶領該隊時')], on=True, model_kw=['PRIMUS']),
        R('Unquestioning Fanaticism (Iconward)', '規則', [T('Unquestioning Fanaticism', 'def', [('fnp', 3)], why='帶領該隊時')], on=True, model_kw=['ACOLYTE ICONWARD']),
        R('Frenzied Devotion', '戰略', [T('Frenzied Devotion', 'att', [('attacks', 1), ('skill', 1)], scope='melee', why='不含 CHARACTER；武器同時得到 HAZARDOUS（未計）')], cp='1', names=HYB, model_not=['CHARACTER']),
        R('Vengeance for the Martyr!', '戰略', [T('Vengeance for the Martyr!', 'att', [('rr_hit', '1')], why='只打殺死角色的那一隊；若死的是 Magus/Primus/Iconward 可全部重骰')], cp='1', names=HYB),
        # Transcendent Celerity：ASSAULT，不影響傷害
    ],
    # Biosanctic Broodsurge
    '000000886': [
        R('Hypermorphic Fury', '規則', [T('Hypermorphic Fury', 'att', [('attacks', 1)], scope='melee', cond='charge')], on=True, names=ABR),
        R('Gene-Twisted Muscle', '戰略', [T('Gene-Twisted Muscle', 'att', [('wound', 1)], scope='melee', tkw=MV)], cp='1', names=ABR),
        R('Bio-Horror Revelation', '戰略', [T('Bio-Horror Revelation', 'def', [('hit', -1)], scope='ranged', why='只在敵人 Leadership 測試失敗時')], cp='1', names=ABR),
        # Saintly Paroxysm：致命傷，非攻擊，不算
    ],
    # Outlander Claw
    '000000887': [
        R('Deft Manoeuvring', '戰略', [T('Deft Manoeuvring', 'def', [('inv', 4)], scope='ranged')], cp='1', names=['Achilles Ridgerunners', 'Atalan Jackals']),
        R('Close-Range Shoot-out', '戰略', [T('Close-Range Shoot-out', 'att', [('kw', 'LETHAL HITS')], scope='ranged', why='只打 18" 內的目標')], cp='1', need=['GENESTEALER CULTS']),
        R('Devoted Crew', '戰略', [T('Devoted Crew', 'def', [('dmg', -1)])], cp='1', names=['Goliath Rockgrinder', 'Goliath Truck']),
    ],
    # Brood Brother Auxilia
    '000000888': [
        R('Integrated Tactics', '規則', [T('Integrated Tactics', 'att', [('hit', 1)], scope='ranged', why='只打被選為 overlapping fire 的那一隊')], need=['GENESTEALER CULTS']),
        R('Symbiotic Destruction', '戰略', [T('Symbiotic Destruction', 'att', [('rr_wound', '1')], why='只打被選的那一隊')], cp='1'),
        # Acceptable Losses 等為致命傷／移動，不算
    ],
    # Cult Unveiled
    '000000939': [
        R('Lurking Menace', '戰略', [T('Lurking Menace', 'def', [('hit', -1)], scope='ranged', why='攻擊者不在 3" 內')], cp='1', need=['GENESTEALER CULTS']),
        # For the Brood：自傷致命傷，不算
    ],
    # Genespawn Onslaught
    '000000940': [
        R('Blessed Visages', '規則', [T('Blessed Visages', 'def', [('hit', -1)], scope='melee', why='敵人宣告衝鋒後且 Leadership 失敗，到回合結束')], need=['GENESTEALER CULTS']),
    ],
    # Infestation Swarm
    '000000941': [
        R('Half-Glimpsed Shadows', '規則', [T('Half-Glimpsed Shadows', 'def', [('hit', -1)], scope='ranged', why='攻擊者不在 6" 內')], need=['GREAT DEVOURER']),
        R('Hyperadrenal Reflexes', '戰略', [T('Hyperadrenal Reflexes', 'def', [('inv', 4)], scope='melee')], cp='1', need=['GREAT DEVOURER']),
    ],
    # Final Day
    '000001002': [
        R('Catalyst', '規則', [T('Catalyst', 'att', [('hit', 1)], why='目標在友方 TYRANIDS 單位 6" 內')], need=['GENESTEALER CULTS']),
        R('Psionic Parasitism (Tyranids)', '規則', [T('Psionic Parasitism', 'att', [('hit', 1)], why='被選為受益的 TYRANIDS 單位，到下個移動階段')], need=['TYRANIDS']),
        R('Avenge the Star Children', '戰略', [T('Avenge the Star Children', 'att', [('hit', 1), ('wound', 1)], why='只打殺死 TYRANIDS 角色的那一隊')], cp='1', need=['GENESTEALER CULTS']),
        R('Hyperferocity', '戰略', [T('Hyperferocity (1)', 'att', [('rr_wound', '1')], pick='hf'),
                                  T('Hyperferocity (all)', 'att', [('rr_wound', 'all')], pick='hf', why='目標 6" 內要有友方 TYRANIDS')], cp='1', need=['GENESTEALER CULTS']),
        # Divine Imperative / Darting Attacks / Psi Surge：移動或衝鋒，不算
    ],
    # Heroes of the Uprising
    '000001188': [
        R('Killer Reputation', '規則', [T('Killer Reputation', 'att', [('rr_hit', '1'), ('rr_wound', '1')])], on=True, names=KIL),
        R('Surging Broodworship', '戰略', [T('Surging Broodworship', 'att', [('kw', 'DEVASTATING WOUNDS')])], cp='1', names=KIL),
        # Loyal to the End：死後仍可打，程式不算
    ],
    # Purestrain Broodswarm
    '000001189': [],   # Enemy Within 與戰略都只有移動／偵測距離
    # Xenocult Masses
    '000001190': [
        R('Slunk from the Underbelly', '戰略', [T('Slunk from the Underbelly', 'def', [('ap', -1)], scope='ranged', why='整隊要在地形區域內')], cp='1', names=['Neophyte Hybrids']),
        R('Fanatical Hail', '戰略', [T('Fanatical Hail', 'att', [('rr_hit', 'all')], scope='ranged', why='只打被選的那一隊')], cp='1', names=['Neophyte Hybrids']),
    ],
}

ENH = {
    'A Chink in Their Armour': [T('A Chink in Their Armour', 'att', [('kw', 'LETHAL HITS')], scope='ranged', on=False, why='只限以增援登場後到下個近戰階段結束')],
    'Assassination Edict': [T('Assassination Edict', 'att', [('hit', 1)], tkw=['CHARACTER'], on=True)],
    'Denunciator of Tyrants': [T('Denunciator of Tyrants', 'att', [('hit', 1), ('wound', 1)], tkw=['CHARACTER'], on=True)],
    'Biomorph Adaptation': [T('Biomorph Adaptation', 'att', [('ap', 1), ('dmg', 1)], scope='melee', on=True, unitwide=False)],
    'Assault Commando': [T('Assault Commando', 'att', [('rr_hit', 'all')], scope='ranged', on=False, why='只限本回合從運輸載具下車')],
    'Miasmic Fumes': [T('Miasmic Fumes', 'def', [('hit', -1), ('wound', -1)], on=True, unitwide=False)],
    'Vanguard Tyrant': [T('Vanguard Tyrant', 'att', [('strength', 1), ('ap', 1)], scope='melee', on=True, unitwide=False)],
    'Inhuman Integration': [T('Inhuman Integration', 'att', [('kw', 'SUSTAINED HITS 1')], on=False, why='只打友方 TYRANIDS 6" 內的目標')],
    'Gene-Tailored Toxins': [T('Gene-Tailored Toxins', 'att', [('dmg', 1)], on=True, unitwide=False)],
    'Contraband Munitions': [T('Contraband Munitions', 'att', [('strength', 2)], scope='ranged', on=True, unitwide=False)],
    # Mark of the Star Children 另有 +1 T、4+ Sv，無對應標記，只算近戰 +1 S
    'Mark of the Star Children': [T('Mark of the Star Children', 'att', [('strength', 1)], scope='melee', on=True, why='另有 +1 T、4+ Sv 未計')],
    'Talons of the Sire': [T('Talons of the Sire', 'att', [('rr_wound', '1')], on=True, unitwide=False)],
}
