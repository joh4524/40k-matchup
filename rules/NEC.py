from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

ARMY = {
    '000008369': dict(name='Reanimation Protocols', rules=[]),   # 回血／復活模型，不影響傷害
}

DET = {
    # Awakened Dynasty
    '000000756': [
        R('Command Protocols', '規則', [T('Command Protocols', 'att', [('hit', 1)], why='要有 NECRONS CHARACTER 帶隊')], on=False),
        R('Protocol of the Conquering Tyrant', '戰略', [
            T('Re-roll Hit 1 (half range)', 'att', [('rr_hit', '1')], scope='ranged', cond='half', pick='tyrant'),
            T('Re-roll Hit (led by Character)', 'att', [('rr_hit', 'all')], scope='ranged', cond='half', pick='tyrant', why='要有 NECRONS CHARACTER 帶隊'),
        ], cp='1'),
        R('Protocol of the Hungry Void', '戰略', [
            T('Hungry Void S+1', 'att', [('strength', 1)], scope='melee'),
            T('Hungry Void AP', 'att', [('ap', 1)], scope='melee', why='要有 NECRONS CHARACTER 帶隊；不與其他 AP 改善疊加', on=False),
        ], cp='1'),
        # Eternal Revenant / Vengeful Stars / Sudden Storm / Undying Legions：復活、移動、回血，不算
    ],
    # Annihilation Legion
    '000000815': [
        R('Annihilation Protocol', '規則', [T('Annihilation Protocol', 'att', [('ap', 1)], scope='ranged', why='只打最近的可選目標')], need=['DESTROYER CULT'], on=False),
        R('Masks of Death', '戰略', [T('Masks of Death', 'def', [('hit', -1)])], cp='1', note='只限 DESTROYER CULT 或 FLAYED ONES 單位'),
        R('The Spoor of Frailty', '戰略', [
            T('Spoor: hit', 'att', [('hit', 1)], why='目標低於起始人數'),
            T('Spoor: wound', 'att', [('wound', 1)], why='目標低於半數'),
        ], cp='1', note='只限 DESTROYER CULT 或 FLAYED ONES 單位'),
        # Insanity's Ire / Blood-fuelled Cruelty（目標撤退時的致命傷，不算）/ Pitiless Hunters / Murderous Reanimation：不算
    ],
    # Canoptek Court
    '000000816': [
        R('Power Matrix (CRYPTEK)', '規則', [T('Re-roll Hit 1', 'att', [('rr_hit', '1')])], need=['CRYPTEK'], on=True),
        R('Power Matrix (CANOPTEK)', '規則', [T('Re-roll Hit 1', 'att', [('rr_hit', '1')])], need=['CANOPTEK'], on=True),
        R('Power Matrix (CRYPTEK, in matrix)', '規則', [T('Re-roll Hit', 'att', [('rr_hit', 'all')])], need=['CRYPTEK'], on=False, note='整隊完全在 Power Matrix 內才能全部重骰命中'),
        R('Power Matrix (CANOPTEK, in matrix)', '規則', [T('Re-roll Hit', 'att', [('rr_hit', 'all')])], need=['CANOPTEK'], on=False, note='整隊完全在 Power Matrix 內才能全部重骰命中'),
        R('Curse of the Cryptek', '戰略', [T('Curse of the Cryptek', 'att', [('hit', 1), ('wound', 1)], why='只打殺死你 CRYPTEK 的那一隊')], cp='1', need=['CANOPTEK']),
        R('Cynosure of Eradication', '戰略', [T('Cynosure of Eradication', 'att', [('kw', 'DEVASTATING WOUNDS')])], cp='2', note='只限完全在 Power Matrix 內的 CRYPTEK 或 CANOPTEK 單位'),
        R('Solar Pulse', '戰略', [T('Solar Pulse', 'att', [('kw', 'IGNORES COVER')], scope='ranged', why='只打選定目標點範圍內的目標')], cp='1'),
    ],
    # Obeisance Phalanx
    '000000817': [
        R('Worthy Foes (NOBLE)', '規則', [T('Worthy Foes', 'att', [('wound', 1)], why='只打被選的那一隊')], need=['NOBLE'], on=False),
        R('Worthy Foes (LYCHGUARD)', '規則', [T('Worthy Foes', 'att', [('wound', 1)], why='只打被選的那一隊')], need=['LYCHGUARD'], on=False),
        R('Worthy Foes (TRIARCH)', '規則', [T('Worthy Foes', 'att', [('wound', 1)], why='只打被選的那一隊')], need=['TRIARCH'], on=False),
        R('Nanoassembly Protocols', '戰略', [T('Nanoassembly Protocols', 'def', [('dmg', -1)])], cp='1', need=['VEHICLE']),
        R('Enslaved Artifice', '戰略', [T('Enslaved Artifice', 'att', [('crit_hit', 5)])], cp='1', need_not=['TITANIC']),
        # Suffer No Rival（PRECISION）、Sentinels of Eternity（死後還能打）等不算
    ],
    # Hypercrypt Legion
    '000000818': [
        R('Quantum Deflection', '戰略', [T('Quantum Deflection', 'def', [('inv', 4)])], cp='1', need=['VEHICLE']),
        # Hyperphasing / Hyperphasic Recall / Entropic Damping（HAZARDOUS 是打我的人受傷，不算）等：不算
    ],
    # Tomb Ship Complement
    '000000959': [
        R('Conquest Protocols', '規則', [T('Conquest Protocols', 'att', [('crit_ap', 1)], why='自己或目標在目標點範圍內：爆擊造傷時 AP 再好 1')], need=['NECRONS'], on=False),
        R('Concentrated Atomisation', '戰略', [T('Concentrated Atomisation', 'att', [('rr_hit', 'all')], scope='ranged')], cp='1', names=['Necron Warriors', 'Immortals']),
        R('Disruption Fields', '戰略', [T('Disruption Fields', 'att', [('strength', 1)], scope='melee')], cp='1'),
        R('Unwavering Defence', '戰略', [T('Unwavering Defence', 'att', [('kw', 'SUSTAINED HITS 2')], scope='melee', why='要 Set to Defend 且還沒打過')], cp='1'),
    ],
    # Deranged Outcasts
    '000000960': [
        R('Terrifying Charge', '規則', [T('Terrifying Charge', 'def', [('hit', -1)], scope='melee', why='自己衝鋒後，被衝的敵人 Leadership 測試失敗才 -1')], on=False),
    ],
    # Canoptek Harvesters
    '000000961': [
        R('Retribution Protocols', '規則', [T('Retribution Protocols', 'att', [('rr_hit', 'all')], why='只打殺死你 CRYPTEK 的那一隊')], on=False),
        R('Targeting Algorithms', '戰略', [T('Targeting Algorithms', 'att', [('rr_hit', 'all'), ('rr_wound', 'all')])], cp='1', model_kw=['CRYPTEK']),
        R('Quantum Flare-shield', '戰略', [T('Quantum Flare-shield', 'def', [('inv', 4)])], cp='1', model_kw=['CRYPTEK']),
    ],
    # Starshatter Arsenal
    '000000985': [
        R('Relentless Onslaught', '規則', [T('Relentless Onslaught', 'att', [('hit', 1)], why='目標要在目標點範圍內')], need_not=['MONSTER'], on=False),
        R('Unyielding Forms (VEHICLE)', '戰略', [T('Unyielding Forms', 'def', [('wound', -1)], cond='s_gt_t')], cp='2', need=['VEHICLE'], need_not=['TITANIC']),
        R('Unyielding Forms (MOUNTED)', '戰略', [T('Unyielding Forms', 'def', [('wound', -1)], cond='s_gt_t')], cp='2', need=['MOUNTED'], need_not=['TITANIC']),
        R('Merciless Reclamation', '戰略', [T('Merciless Reclamation', 'att', [('wound', 1)], why='目標要在目標點範圍內')], cp='2', need_not=['MONSTER', 'TITANIC']),
    ],
    # Cryptek Conclave
    '000001127': [
        R('Technosorcerous Augmentations', '規則', [
            T('Anti-Infantry 3+', 'att', [('kw', 'ANTI-INFANTRY 3+')], scope='ranged', pick='techno'),
            T('Anti-Mounted 4+', 'att', [('kw', 'ANTI-MOUNTED 4+')], scope='ranged', pick='techno'),
            T('Heavy', 'att', [('hit', 1)], scope='ranged', cond='still', pick='techno', why='HEAVY：沒移動 +1 命中'),
            T('Ignores Cover', 'att', [('kw', 'IGNORES COVER')], scope='ranged', pick='techno'),
        ], need=['CRYPTEK'], on=True, note='每次射擊選一個；ASSAULT 不影響傷害所以沒列'),
        R('Molecular Targeting', '戰略', [T('Molecular Targeting', 'att', [('ign', 1)], why='CRYPTEK 單位另可無視造傷修正')], cp='1'),
        R('Animus Curse', '戰略', [T('Animus Curse', 'att', [('rr_hit', 'all')], why='只打殺死你 CRYPTEK 的那一隊')], cp='1'),
        # Microscarab Swarm：原文要求 CRYPTEK INFANTRY 單位卻又看 NECRON WARRIORS／IMMORTALS 關鍵字，條件矛盾，不算
    ],
    # Cursed Legion
    '000001128': [
        R('Cold Fervour', '規則', [T('Cold Fervour', 'att', [('strength', 2)])], need=['DESTROYER CULT'], on=True),
        R('Cold Fervour (other NECRONS)', '規則', [T('Cold Fervour', 'att', [('strength', 2)], why='本回合 DESTROYER CULT 單位消滅或打到低於半數一隊之後')], need_not=['DESTROYER CULT', 'MONSTER', 'TITANIC'], on=False),
        R('Methodical Murder', '戰略', [T('Methodical Murder', 'att', [('kw', 'SUSTAINED HITS 1')])], cp='1', need_not=MV),
        R('Image of Death', '戰略', [T('Image of Death', 'def', [('hit', -1)])], cp='1', need=['DESTROYER CULT']),
    ],
    # Pantheon of Woe
    '000001129': [
        R('Cosmic Distortion', '規則', [T('Unravelling', 'att', [('ap', 1)], why='目標要在 NECRONS MONSTER 6"（自損 3 致命傷時 9"）內')], on=False),
        R('Entrophasic Aura Targeting', '戰略', [
            T('Re-roll Hit 1', 'att', [('rr_hit', '1')]),
            T('Re-roll Wound 1', 'att', [('rr_wound', '1')], why='只打 unravelling 的目標', on=False),
        ], cp='1', need_not=['MONSTER']),
    ],
    # Harbinger Cabal
    '000001140': [
        R('Transharmonic Disruption', '規則', [T('Transharmonic Disruption', 'att', [('strength', 1)], why='6" 內要有選此光環的 CRYPTEK')], on=False),
        R('Quantum Interface', '規則', [T('Quantum Interface', 'def', [('inv', 5)], why='6" 內要有選此光環的 CRYPTEK')], on=False),
        R('Hologyric Simulation', '戰略', [
            T('Re-roll Hit', 'att', [('rr_hit', 'all')], why='要在友方 CRYPTEK 6" 內'),
            T('Re-roll Wound', 'att', [('rr_wound', 'all')], why='要在友方 CRYPTEK 6" 內，且本單位有 CRYPTEK 關鍵字', on=False),
        ], cp='1'),
        # Anti-Proximal Subroutines（PISTOL）等：不算
    ],
    # Hand of the Dynasty
    '000001191': [],   # ASSAULT／OC／目標點／snap shooting，不影響傷害計算
    # Skyshroud Spearhead
    '000001192': [
        R('Transdimensional Deployment', '規則', [T('Transdimensional Deployment', 'att', [('hit', 1)], scope='ranged', why='本回合有 ingress move')], need=['TOMB BLADES'], on=False),
        R('Evasive Protocols', '戰略', [T('Evasive Protocols', 'def', [('wound', -1)], scope='ranged', cond='s_gt_t')], cp='1', need=['MOUNTED']),
    ],
    # The Phaeron's Armoury
    '000001193': [
        R('Cosmic Storm', '戰略', [T('Cosmic Storm', 'att', [('ap', 1)], scope='ranged', weapon='tesla')], cp='1', names=['Obelisk', 'Tesseract Vault']),
        R('Subsurface Quantumweave', '戰略', [T('Subsurface Quantumweave', 'def', [('ap', -1)])], cp='1', need=['TITANIC', 'FLY']),
    ],
}

ENH = {
    # Awakened Dynasty
    'Veil of Darkness': [],
    'Nether-realm Casket': [T('Nether-realm Casket', 'def', [('cover', 1)], on=True, why='Stealth')],
    'Phasal Subjugator (Aura)': [T('Phasal Subjugator', 'att', [('hit', 1)], on=True, why='光環 6"，只給非 CHARACTER 的 NECRONS 單位')],
    'Enaegic Dermal Bond': [T('Enaegic Dermal Bond', 'def', [('fnp', 4)], on=True, unitwide=False)],
    # Annihilation Legion
    'Eternal Madness': [],
    'Ingrained Superiority': [T('Ingrained Superiority', 'att', [('crit_ap', 1)], on=True, why='爆擊造傷時 AP 再好 1')],
    'Soulless Reaper': [],
    'Eldritch Nightmare': [],
    # Canoptek Court
    'Dimensional Sanctum': [],
    'Hyperphasic Fulcrum': [T('Hyperphasic Fulcrum', 'att', [('rr_wound', '1')], on=False, why='整隊要完全在 Power Matrix 內')],
    'Autodivinator': [],
    'Metalodermal Tesla Weave': [],
    # Obeisance Phalanx
    'Honourable Combatant': [],
    'Unflinching Will': [T('Unflinching Will', 'att', [('kw', 'ANTI-INFANTRY 5+')], scope='melee', on=True, unitwide=False)],
    'Warrior Noble': [T('Warrior Noble', 'def', [('hit', -1)], scope='melee', on=True)],
    'Eternal Conqueror': [T('Eternal Conqueror', 'att', [('rr_hit', 'all')], on=False, why='目標要在目標點範圍內')],
    # Hypercrypt Legion
    'Dimensional Overseer': [],
    'Arisen Tyrant': [
        T('Arisen Tyrant', 'att', [('rr_hit', '1')], on=True, pick='tyrant'),
        T('Arisen Tyrant (set up this turn)', 'att', [('rr_hit', 'all')], on=False, pick='tyrant', why='本回合剛降落'),
    ],
    'Hyperspatial Transfer Node': [],
    'Osteoclave Fulcrum': [],
    # Tomb Ship Complement
    'Resurrection Protocols': [],
    'Mindshackle Scarabs': [],
    # Deranged Outcasts
    'Inured to Damage': [
        T('Inured to Damage', 'def', [('fnp', 6)], on=True, unitwide=False, pick='inured'),
        T('Inured to Damage (after kill)', 'def', [('fnp', 5)], on=False, unitwide=False, pick='inured', why='已消滅過敵方單位'),
    ],
    'Domineering Presence': [],
    # Canoptek Harvesters
    'Nanoscarab Reconstitution': [],
    'Impromptu Translocation': [],
    # Starshatter Arsenal
    'Dread Majesty (Aura)': [T('Dread Majesty', 'att', [('rr_hit', '1'), ('rr_wound', '1')], on=True, why='光環 6"，不含 MONSTER／TITANIC')],
    'Miniaturised Nebuloscope': [T('Miniaturised Nebuloscope', 'att', [('kw', 'IGNORES COVER')], scope='ranged', on=True)],
    'Demanding Leader': [],
    'Chrono-impedance Fields': [T('Chrono-impedance Fields', 'def', [('dmg', -1)], on=False, why='要在指揮階段選中該 VEHICLE／MOUNTED 單位（6" 內）')],
    # Cryptek Conclave
    'Quantum Abacus': [],
    'Atomic Disintegrators': [
        T('Anti-Monster 5+', 'att', [('kw', 'ANTI-MONSTER 5+')], scope='ranged', on=True, pick='atomic'),
        T('Anti-Vehicle 5+', 'att', [('kw', 'ANTI-VEHICLE 5+')], scope='ranged', on=True, pick='atomic'),
    ],
    'Gauntlet of Compression': [],
    'Gravitic Bolas': [],
    # Cursed Legion
    'Destroyer Ankh': [T('Destroyer Ankh', 'att', [('attacks', 2)], scope='melee', on=True, unitwide=False)],
    'Murdermind': [],
    'Mark of the Nekrosor': [T('Mark of the Nekrosor', 'att', [('hit', 1)], on=True)],
    'Cursed Circlet': [],
    # Pantheon of Woe
    'Singularity Matrix': [],
    'Quantum Goad': [],
    'Animus Damper': [
        T('Animus Damper: hit', 'def', [('hit', -1)], scope='ranged', on=False, why='只對選定的敵方 VEHICLE，每回合一次'),
        T('Animus Damper: wound', 'def', [('wound', -1)], scope='ranged', on=False, why='只對選定的敵方 VEHICLE，且其 Leadership 測試失敗'),
    ],
    'Reletavistic Tether': [],
    # Harbinger Cabal（Cryptometric Experimentation 的 +1 T／+1 W 無對應標記，只算無敵保護）
    'Cryptometric Experimentation': [T('Cryptometric Experimentation', 'def', [('inv', 4)], on=True, unitwide=False)],
    'Portal Transmuter': [],
    # Hand of the Dynasty
    'Enlivened Sentinels': [],
    'Tools of Dominion': [T('Tools of Dominion', 'att', [('kw', 'RAPID FIRE 1')], scope='ranged', on=True)],
    # Skyshroud Spearhead
    'Recursive Reanimation': [],
    'Deepening Madness': [],
    # The Phaeron's Armoury
    'Relocational Optimiser': [
        T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='ranged', on=False, pick='reloc', why='本回合用 Monolith 的 Eternity Gate 降落'),
        T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', on=False, pick='reloc', why='本回合用 Monolith 的 Eternity Gate 降落'),
    ],
    'Mortality Shroud (Aura)': [],
}

