from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

ARMY = {
    '000003676': dict(name='Waaagh!', rules=[
        R('Waaagh! (riled up)', '軍隊規則', [T('Riled up', 'def', [('inv', 5)], why='要處於 riled up（War Cry 每場一次）；Assault 不影響傷害')], on=False, need=['ORKS']),
    ]),
    '000011126': dict(name='Da Boss', rules=[]),   # 只加 CP
    '000011127': dict(name='Unstable Energies', rules=[]),   # 靈能等級，不影響傷害
}

DET = {
    # War Horde
    '000000852': [
        R('Get Stuck In', '規則', [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee')], on=True, need=['ORKS']),
        R("CLOSE-RANGE DAKKA", '戰略', [T('Rapid Fire 1', 'att', [('kw', 'RAPID FIRE 1')], scope='ranged', why='已有 RAPID FIRE 的武器是 +1，這裡只算 Rapid Fire 1')], cp='1', need=['ORKS']),
        R("MOW 'EM DOWN", '戰略', [T('Cleave 1', 'att', [('kw', 'CLEAVE 1')], scope='melee', why='要本回合衝鋒過；已有 CLEAVE 的武器是 +1')], cp='1', need=['ORKS', 'VEHICLE'], need_not=['WALKER']),
        R("HIT 'EM HARDER", '戰略', [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='melee')], cp='1', need=['ORKS']),
        # FUNGUS-FUEL INJECTION / BREAKIN' HEADS / ORKS IS NEVER BEATEN: 移動、戰震、死後再打，不算
    ],
    # Da Big Hunt
    '000000853': [
        R('Da Hunt is On', '規則', [T('Da Hunt is On', 'att', [('ap', 1)], tkw=MV)], on=True, need=['BEAST SNAGGA']),
    ],
    # Kult of Speed
    '000000854': [
        # Speediest Freeks 是「未修正命中骰 1-3 失敗」，無對應標記，不算
        R('DAKKASTORM', '戰略', [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged')], cp='1', need=['SPEED FREEKS']),
    ],
    # Dread Mob
    '000000855': [
        R('Try Dat Button!', '規則', [
            T('+1 Attacks', 'att', [('attacks', 1)], pick='tdb', why='D6 1-2'),
            T('+2 Strength', 'att', [('strength', 2)], pick='tdb', why='D6 3-4'),
            T('+1 AP', 'att', [('ap', 1)], pick='tdb', why='D6 5-6'),
        ], on=False, need=['ORKS', 'WALKER'], need_not=['TITANIC'],
          note='實際是擲骰隨機（各 1/3），程式挑最好的，會高估；擲兩顆還要做一次 hazard roll'),
        # 其他戰略：riled up／不死骰／MOBILE，不算
    ],
    # Green Tide
    '000000856': [
        R('Mob-handed Brutality (Boyz)', '規則', [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee')], on=True, names=['Boyz']),
        R('Mob-handed Brutality (charge)', '規則', [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='melee', cond='charge', tkw_not=MV)], on=True, need=['ORKS', 'INFANTRY']),
        R('UNBRIDLED CARNAGE', '戰略', [T('Unbridled Carnage', 'att', [('attacks', 1)], scope='melee', cond='charge')], cp='1', names=['Boyz']),
    ],
    # Bully Boyz
    '000000857': [
        R('Displays of Savagery', '規則', [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee')], on=True, names=['Meganobz', 'Nobz']),
        R('HULKING BRUTES', '戰略', [T('Hulking Brutes', 'def', [('wound', -1)], scope='ranged', cond='s_gt_t')], cp='1', names=['Meganobz', 'Nobz'],
          note='加 1CP（共 2CP）可改成不限 S>T，這裡只算 1CP 版'),
        R('ARMED TO DA TEEF', '戰略', [
            T('Re-roll 1s', 'att', [('rr_hit', '1')], pick='teef'),
            T('Re-roll hits (riled up)', 'att', [('rr_hit', 'all')], pick='teef', why='要 riled up'),
        ], cp='1', names=['Meganobz', 'Nobz']),
        # TOO ARROGANT TO DIE：不死骰，不算
    ],
    # Ramship Raiders
    '000000963': [
        R('Belligerent Boarders', '規則', [T('Belligerent Boarders', 'def', [('wound', -1)], cond='s_gt_t')], on=True, need=['ORKS'], need_not=['GROTS']),
    ],
    # Kaptin Killers
    '000000964': [
        R('LOOT ON THE MOVE', '戰略', [T('Loot on the Move', 'def', [('ap', -1)], why='要剛打開艙門的單位')], cp='1', need=['ORKS']),
        # Cornered and Krumped 是移動階段的特殊戰鬥（命中要 6），不算
    ],
    # Taktikal Brigade
    '000000995': [],   # 只有移動／撤退相關
    # Blitz Brigade
    '000001152': [],   # 衝鋒／移動／戰震／艙門，不影響傷害
    # Wreckas
    '000001222': [
        R('Wreckin’ and Lootin’', '規則', [T('Re-roll hit 1s', 'att', [('rr_hit', '1')], scope='ranged', why='自己或目標在目標點範圍內')], need=['ORKS'], names=['Breaka Boyz', 'Flash Gitz', 'Tankbustas']),
        R("DRIVE-BY BUSTIN'", '戰略', [T('Drive-by Bustin', 'att', [('hit', 1)], scope='ranged', why='只限 Firing Deck 選的武器')], cp='1', need=['ORKS', 'TRANSPORT']),
    ],
    # Runt Swarm
    '000001223': [],   # 移動／復活／Grot Shields 替代攻擊，不算
    # Shoota Boyz
    '000001224': [
        R('NEVER ENOUGH DAKKA', '戰略', [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged')], cp='1', need=['ORKS', 'INFANTRY']),
        R('KUSTOM DAKKA', '戰略', [T('Kustom Dakka', 'att', [('wound', 1)], scope='ranged', tkw_not=MV)], cp='1', need=['ORKS', 'INFANTRY']),
        R("GLOWIN' DAKKA", '戰略', [T('Glowin Dakka', 'att', [('ap', 1)], scope='ranged', why='只打 9" 內的目標')], cp='1', need=['ORKS', 'INFANTRY']),
        # Dakka! Dakka! Dakka! 只有 Assault 和射程，不算
    ],
    # Madcap Meks
    '000001225': [
        R('VINDICTIVE ARTILLERISTS', '戰略', [
            T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='ranged', pick='art'),
            T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', pick='art'),
        ], cp='1', names=['Mek Gunz'], note='第三選項（Hazardous + 兩者都有）沒算'),
        # Unpredictable Genius 是 D6 隨機效果，不算
    ],
    # Brute Bosses
    '000001226': [],   # 只有不死骰；強化另列
    # Flyboyz
    '000001227': [
        R('Skyborne Loons', '規則', [T('Skyborne Loons', 'att', [('hit', 1)], scope='ranged', why='只限 AIRCRAFT／Deffkoptas 且 riled up')], on=False, need=['ORKS']),
        R('LONG, UNCONTROLLED BURSTS', '戰略', [T('Long Bursts', 'att', [('rr_hit', 'all')], scope='ranged', tkw=['FLY'])], cp='1', need=['ORKS'], note='只限 AIRCRAFT／Deffkoptas'),
    ],
    # Wurrband
    '000001228': [
        R('Powers of da Waaagh!', '規則', [T('Psychic +1 S', 'att', [('strength', 1)], wkw='PSYCHIC', why='每 5 個模型再 +1 S 沒算')], on=True, need=['PSYKER']),
    ],
}

ENH = {
    # War Horde
    "Headwoppa's Killchoppa": [T("Headwoppa's Killchoppa", 'att', [('ap', 1)], scope='melee', cond='charge', on=True, unitwide=False)],
    # Green Tide
    'Ferocious Show-off': [T('Ferocious Show-off', 'att', [('attacks', 1)], scope='melee', on=True, unitwide=False, why='單位 11+ 模型時是 +2 A，這裡只算 +1')],
    # Kult of Speed
    'Smoky Gubbinz': [T('Smoky Gubbinz', 'def', [('cover', 1)], on=False, why='只在被這單位擋住視線時')],
    # Taktikal Brigade
    'Throat-slittas': [T('Throat-slittas', 'att', [('kw', 'LETHAL HITS')], scope='melee', tkw_not=MV, on=True)],
    'Kill Kommanda': [T('Kill Kommanda', 'def', [('cover', 1)], scope='ranged', on=True, why='Stealth；要在附屬單位中')],
    # Blitz Brigade
    "Targetin' Gizmos": [T("Targetin' Gizmos", 'att', [('kw', 'IGNORES COVER')], scope='ranged', on=False, why='要有 Big Mek 在艙內')],
    # Wreckas
    'Supa-snazz Dakka': [T('Supa-snazz Dakka', 'att', [('kw', 'RAPID FIRE 1')], scope='ranged', weapon='snazzgun', on=True)],
    # Shoota Boyz
    'Supa-glowy Fing': [
        T('Supa-glowy Fing', 'att', [('kw', 'ANTI-INFANTRY 4+'), ('kw', 'DEVASTATING WOUNDS')], scope='ranged', on=True, unitwide=False, why='SUPA-HAZARDOUS 自傷（每把武器 2 次 hazard roll）沒算'),
    ],
    # Madcap Meks
    'Mekwaaagh! Mastermind': [T('Mekwaaagh! Mastermind', 'def', [('inv', 5)], on=True, why='riled up 的 5+ 無敵save')],
    # Ramship Raiders
    'Scarred Brute': [T('Scarred Brute', 'def', [('fnp', 5)], on=True, unitwide=False)],
    # Brute Bosses
    "Brutal But Kunnin'": [T("Brutal But Kunnin'", 'att', [('dmg', 1)], scope='melee', on=True, unitwide=False)],
    'Proper Killy': [T('Proper Killy', 'att', [('rr_hit', '1')], on=True, unitwide=False)],
    'Blitzboss': [],   # 只給載具，不算
}
