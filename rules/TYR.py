from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

ARMY = {
    '000000705': dict(name='Synapse', rules=[
        R('Synapse', '軍隊規則', [T('Synapse', 'att', [('strength', 1)], scope='melee', why='要在友方 Synapse 模型 6" 內')], on=False,
          need=['TYRANIDS']),
    ]),
    # 000000707 Shadow in the Warp：只有 Battle-shock，不標記
}

HYPER = lambda: [
    T('Swarming Instincts', 'att', [('kw', 'SUSTAINED HITS 1')], tkw=['INFANTRY', 'SWARM'], pick='hyper'),
    T('Hyper-aggression', 'att', [('kw', 'LETHAL HITS')], tkw=['MONSTER', 'VEHICLE'], pick='hyper'),
]

DET = {
    '000000748': [   # Invasion Fleet
        R('Hyper-adaptations', '規則', HYPER(), on=True, need=['TYRANIDS'],
          note='戰鬥開始選一個，程式對每個目標挑好的；Hive Predators 只給 PRECISION，沒算'),
        R('Adrenal Surge', '戰略', [T('Adrenal Surge', 'att', [('crit_hit', 5)])], cp='2', need=['TYRANIDS']),
        R('Rapid Regeneration', '戰略', [T('Rapid Regeneration', 'def', [('fnp', 6)], why='在 Synapse Range 內是 FNP 5+，這裡只算 6+')], cp='1', need=['TYRANIDS']),
        R('Predatory Imperative', '戰略', HYPER(), cp='1', need=['TYRANIDS'],
          note='額外啟動一個 Hyper-adaptation（不能選與第一回合相同的）'),
    ],
    '000000769': [   # Crusher Stampede
        R('Enraged Behemoths (below Starting Strength)', '規則', [T('Enraged Behemoths', 'att', [('hit', 1)], why='單位低於起始人數')], need=['TYRANIDS', 'MONSTER']),
        R('Enraged Behemoths (below Half-strength)', '規則', [T('Enraged Behemoths', 'att', [('wound', 1)], why='單位低於半數')], need=['TYRANIDS', 'MONSTER']),
        R('Rampaging Monstrosities', '戰略', [T('Rampaging Monstrosities', 'att', [('rr_hit', 'all')], scope='melee')], cp='1', need=['TYRANIDS', 'MONSTER']),
        R('Savage Roar', '戰略', [T('Savage Roar', 'def', [('hit', -1)], scope='melee'),
                                T('Savage Roar (failed Battle-shock)', 'def', [('wound', -1)], scope='melee', on=False, why='對方 Battle-shock 失敗才有')],
          cp='1', need=['TYRANIDS', 'MONSTER']),
        R('Swarm-guided Salvoes', '戰略', [T('Swarm-guided Salvoes', 'att', [('kw', 'IGNORES COVER'), ('ign', 1)], scope='ranged')], cp='1', need=['TYRANIDS', 'MONSTER']),
        R('Massive Impact', '戰略', [T('Massive Impact', 'att', [('mw', 3)], scope='melee', cond='charge', why='六顆 D6 每個 4+ 一點致命傷，平均 3')], cp='1', need=['TYRANIDS', 'MONSTER']),
    ],
    '000000770': [   # Unending Swarm
        R('Teeming Masses', '戰略', [T('Teeming Masses', 'def', [('hit', -1)])], cp='1', need=['ENDLESS MULTITUDE']),
        R('Swarming Masses', '戰略', [T('Swarming Masses', 'att', [('kw', 'SUSTAINED HITS 1')]),
                                    T('Swarming Masses (15+ models)', 'att', [('crit_hit', 5)], on=False, why='單位有 15 個以上模型')],
          cp='1', need=['ENDLESS MULTITUDE']),
    ],
    '000000771': [   # Assimilation Swarm
        R('Broodguard Impulse', '戰略', [T('Broodguard Impulse', 'att', [('wound', 1)], why='只打殺掉你 Harvester 的那一隊')], cp='1', need=['TYRANIDS']),
        R('Ablative Carapace', '戰略', [T('Ablative Carapace', 'def', [('fnp', 5)], why='在你控制的目標點範圍內是 FNP 4+，這裡只算 5+')], cp='2', need=['HARVESTER']),
        R('Secure Biomass', '戰略', [T('Secure Biomass', 'att', [('kw', 'LETHAL HITS')], scope='melee'),
                                   T('Secure Biomass (Harvester)', 'att', [('crit_hit', 5)], scope='melee', on=False, why='Harvester 單位才有')],
          cp='1', need=['TYRANIDS']),
    ],
    '000000772': [   # Vanguard Onslaught
        R('Surprise Assault (Hit)', '戰略', [T('Surprise Assault', 'att', [('hit', 1)], why='只打被選的那一隊')], cp='1', need=['VANGUARD INVADER']),
        R('Surprise Assault (Wound)', '戰略', [T('Surprise Assault', 'att', [('wound', 1)], why='只打被選的那一隊，且對方 Battle-shock 失敗')], cp='1', need=['VANGUARD INVADER']),
        # Assassin Beasts 只給 PRECISION，不標記
    ],
    '000000773': [   # Synaptic Nexus
        R('Synaptic Imperatives', '規則', [
            T('Synaptic Augmentation', 'def', [('inv', 5)], pick='imperative', why='要在 Synapse Range 內'),
            T('Goaded to Slaughter', 'att', [('hit', 1)], scope='melee', pick='imperative', why='要在 Synapse Range 內'),
          ], need=['TYRANIDS'], note='每回合選一個，每個一場只能選一次'),
        R('Irresistible Will', '戰略', [T('Irresistible Will', 'att', [('rr_hit', '1'), ('rr_wound', '1')], why='只打被選的那一隊，攻擊單位要在 Synapse 單位 6" 內')], cp='1', need=['TYRANIDS']),
        R('Reinforced Hive Node', '戰略', [T('Reinforced Hive Node', 'def', [('ap', -1)])], cp='1', need=['SYNAPSE']),
        R('The Smothering Shadow', '戰略', [T('The Smothering Shadow', 'att', [('mw', 4)], why='敵方 Battle-shock 失敗才有；六顆 D6 每個 3+，平均 4')], cp='1', need=['SYNAPSE']),
    ],
    '000000973': [   # Tyranid Attack
        R('Bio-acid Surge', '戰略', [T('Bio-acid Surge', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee')], cp='1', need=['TYRANIDS']),
        # Expendable Biomass / Phagic Spores 太條件化，不標記
    ],
    '000000974': [   # Boarding Swarm
        R('Lithe Killers', '戰略', [T('Lithe Killers', 'def', [('inv', 5)], scope='melee')], cp='1', need=['TYRANIDS']),
    ],
    '000000975': [   # Biotide
        R('Onrushing Horde', '戰略', [T('Onrushing Horde', 'def', [('hit', -1)], scope='ranged')], cp='1', need=['TYRANIDS'], names_not=['Winged Tyranid Prime']),
        R('Swarm Hunters', '戰略', [T('Swarm Hunters', 'att', [('rr_hit', 'all')], scope='ranged', why='要在 Synapse Range 內')], cp='1', names=['Termagant']),
    ],
    '000000979': [   # Infestation Swarm
        R('Half-Glimpsed Shadows', '規則', [T('Half-Glimpsed Shadows', 'def', [('hit', -1)], scope='ranged', why='攻擊模型不在 6" 內')], need=['GREAT DEVOURER']),
        R('Hyperadrenal Reflexes', '戰略', [T('Hyperadrenal Reflexes', 'def', [('inv', 4)], scope='melee')], cp='1', need=['GREAT DEVOURER']),
    ],
    '000000982': [   # Warrior Bioform Onslaught
        R('Leader-beasts', '規則', [T('Leader-beasts', 'def', [('inv', 5)])], on=True,
          names=['Tyranid Warriors', 'Tyranid Prime', 'Winged Tyranid Prime']),
        R('Parasitic Payload', '戰略', [T('Parasitic Payload', 'att', [('kw', 'IGNORES COVER')], scope='ranged')], cp='1', names=['Tyranid Warriors']),
        R('Alien Physiology', '戰略', [T('Alien Physiology', 'def', [('wound', -1)], cond='s_gt_t')], cp='1', names=['Tyranid Warriors']),
    ],
    '000001057': [   # Subterranean Assault
        R('Surprise Assault', '規則', [T('Surprise Assault', 'att', [('rr_hit', '1')])], on=True, need=['TYRANIDS']),
        R('Enfilading Emergence', '戰略', [T('Enfilading Emergence', 'att', [('kw', 'SUSTAINED HITS 1'), ('kw', 'IGNORES COVER')], why='本回合以援軍進場的單位')], cp='1', need=['TYRANIDS']),
    ],
    '000001197': [   # Ambush Predators
        R('Mindhunger', '規則', [T('Mindhunger', 'att', [('rr_hit', '1')], tkw=['CHARACTER'])], on=True, names=['Lictor', 'Neurolictor']),
        R('Counterpredation', '戰略', [T('Counterpredation', 'att', [('strength', 1), ('ap', 1)], why='只打隱藏（hidden）的目標')], cp='1',
          names=['Deathleaper', 'Lictor', 'Neurolictor', 'Von Ryan']),
        # 其餘只有移動／偵測範圍
    ],
    '000001198': [   # Talons of the Norn Queen
        R('Lesser Prey', '戰略', [T('Lesser Prey', 'att', [('strength', 2)], scope='melee')], cp='1', names=['Norn Assimilator', 'Norn Emissary']),
        # Catalytic Biofortification 只對致命傷 FNP，不標記
    ],
}

ENH = {
    # Invasion Fleet
    'Adaptive Biology': [T('Adaptive Biology', 'def', [('fnp', 5)], on=True, unitwide=False, why='低於起始傷口後升為 FNP 4+，這裡只算 5+')],
    'Perfectly Adapted': [T('Perfectly Adapted', 'att', [('rr1', 2), ('rr1d', 1)], on=True, unitwide=False, why='每回合一次：重骰一顆命中、一顆造傷、一顆傷害骰（帶的模型自己）')],
    # Crusher Stampede
    'Monstrous Nemesis': [T('Monstrous Nemesis', 'att', [('wound', 1)], scope='melee', tkw=['MONSTER', 'VEHICLE'], on=True, unitwide=False)],
    # Unending Swarm
    'Naturalised Camouflage': [T('Naturalised Camouflage', 'def', [('cover', 1)], scope='ranged', on=False, why='只給第一回合選的最多三個 Endless Multitude 單位')],
    'Piercing Talons': [T('Piercing Talons', 'att', [('crit_ap', 1)], on=True, why='爆擊造傷時 AP 再好 1')],
    # Assimilation Swarm
    'Parasitic Biomorphology': [T('Parasitic Biomorphology', 'att', [('strength', 1)], scope='melee', on=True,
                                  why='首次在附近 Harvester 旁殺掉敵方單位後再 +1 Attacks，沒算')],
    # Vanguard Onslaught
    'Chameleonic': [T('Chameleonic', 'def', [('cover', 1)], on=True, why='Stealth')],
    'Stalker': [T('Stalker', 'att', [('hit', 1), ('wound', 1)], on=False, unitwide=False, why='只打開場選的那一隊')],
    # Synaptic Nexus
    'Power of the Hive Mind': [T('Power of the Hive Mind', 'att', [('strength', 1), ('ap', 1)], wkw='PSYCHIC', on=True, unitwide=False)],
    'Synaptic Control': [T('Synaptic Control', 'def', [('dmg', -1)], on=True, unitwide=False)],
    # Tyranid Attack
    'Reinforced Carapace': [T('Reinforced Carapace', 'def', [('dmg', -1)], on=True, unitwide=False)],
    # Warrior Bioform Onslaught
    'Elevated Might': [T('Elevated Might', 'att', [('rr_wound', 'all'), ('ap', 1)], scope='melee', on=True, unitwide=False)],
    'Ocular Adaptation': [T('Ocular Adaptation', 'att', [('hit', 1)], scope='melee', on=True)],
    # Subterranean Assault
    'Trygon Prime': [T('Trygon Prime', 'att', [('strength', 1), ('skill', 1)], scope='melee', on=True, unitwide=False)],
    # Talons of the Norn Queen
    'Destabilising Predation': [T('Destabilising Predation', 'att', [('kw', 'ANTI-CHARACTER 2+')], scope='ranged', on=True)],
    'Synaptoprescience': [T('Synaptoprescience', 'def', [('inv', 4)], on=True)],
}
