from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

TE = ['T’AU EMPIRE']

ARMY = {
    '000008439': dict(name='For the Greater Good', rules=[
        R('For the Greater Good', '軍隊規則', [T('Guided: BS +1', 'att', [('skill', 1)], scope='ranged', why='要有 Observer 標記目標（Spotted），且自己是 Guided 單位')],
          on=False, note='自己要有 For the Greater Good 能力且不是 Observer'),
        R('For the Greater Good (Markerlight)', '軍隊規則', [T('Markerlight Ignores Cover', 'att', [('kw', 'IGNORES COVER')], scope='ranged', why='只有 Observer 帶 MARKERLIGHT 才有')],
          on=False),
    ]),
}

DET = {
    # Kauyon
    '000000781': [
        R('Patient Hunter', '規則', [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', why='只有第 3、4、5 回合')], need=TE, on=False,
          note='第 3~5 回合才有，使用者自己勾'),
        R('Patient Hunter (Guided)', '規則', [T('Ignore modifiers', 'att', [('ign', 1)], scope='ranged', why='第 3~5 回合、Guided 打 Spotted 時')], need=TE, on=False),
        R('POINT-BLANK AMBUSH', '戰略', [T('Point-Blank Ambush', 'att', [('ap', 1)], scope='ranged', why='只打 9" 內的目標；第 3 回合起')], cp='1', need=TE),
        R('A TEMPTING TRAP', '戰略', [T('A Tempting Trap', 'att', [('wound', 1)], scope='ranged', why='目標要在 Trap 目標點範圍內；第 3 回合起')], cp='1', need=TE),
        R('COORDINATE TO ENGAGE', '戰略', [T('Coordinate to Engage', 'att', [('skill', 1)], scope='ranged', why='只打 Spotted 目標'),
                                         T('Ignores Cover', 'att', [('kw', 'IGNORES COVER')], scope='ranged', why='只有該單位有 MARKERLIGHT 才有')], cp='1', need=TE),
    ],
    # Mont'ka
    '000000845': [
        R('Killing Blow', '規則', [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='ranged', why='只有第 1~3 回合、Guided 單位')], on=False,
          note='ASSAULT 部分不影響傷害，未標記'),
        R('FOCUSED FIRE', '戰略', [T('Focused Fire', 'att', [('ap', 1)])], cp='1', need=TE, note='第 4、5 回合不能用'),
        R('PINPOINT COUNTER-OFFENSIVE', '戰略', [T('Pinpoint Counter-offensive', 'att', [('rr_hit', 'all')], why='只打毀滅己方單位的那一隊')], cp='1', need=TE, need_not=['KROOT']),
        R('COMBAT DEBARKATION', '戰略', [T('Combat Debarkation', 'att', [('rr_wound', 'all')], why='只打最近的敵人；本回合要剛下車')], cp='1', need=['T’AU EMPIRE', 'INFANTRY']),
        R('COUNTERFIRE DEFENCE SYSTEMS', '戰略', [T('Counterfire Defence Systems', 'def', [('dmg', -1)], scope='ranged')], cp='2', need=TE),
    ],
    # Retaliation Cadre
    '000000846': [
        R('Bonded Heroes (S)', '規則', [T('Bonded Heroes S+1', 'att', [('strength', 1)], scope='ranged', why='只打 12" 內的目標')], need=['BATTLESUIT']),
        R('Bonded Heroes (AP)', '規則', [T('Bonded Heroes AP+1', 'att', [('ap', 1)], scope='ranged', why='只打 8" 內的目標')], need=['BATTLESUIT']),
        R('THE ARRO’KON PROTOCOL', '戰略', [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], pick='arrokon', why='目標 6 個以上模型'),
                                          T('Sustained Hits 2', 'att', [('kw', 'SUSTAINED HITS 2')], pick='arrokon', why='目標 11 個以上模型')], cp='1', need=['BATTLESUIT']),
        R('STIMM INJECTORS', '戰略', [T('Stimm Injectors', 'def', [('fnp', 6)])], cp='1', need=['BATTLESUIT']),
    ],
    # Kroot Hunting Pack
    '000000847': [
        R('Hunter’s Instincts (Hit)', '規則', [T('Hunter’s Instincts hit', 'att', [('hit', 1)], why='目標低於起始人數')], need=['KROOT']),
        R('Hunter’s Instincts (Wound)', '規則', [T('Hunter’s Instincts wound', 'att', [('wound', 1)], why='目標低於半數')], need=['KROOT']),
        R('Skirmish Fighters', '規則', [T('Skirmish Fighters melee', 'def', [('inv', 6)], scope='melee'),
                                      T('Skirmish Fighters ranged', 'def', [('inv', 5)], scope='ranged')], need=['KROOT'], on=True),
        R('A TRAP WELL LAID', '戰略', [T('A Trap Well Laid', 'att', [('ap', 1)], why='只打被選中（已被命中）的那一隊；單位不能 Battle-shocked')], cp='1', need=['KROOT']),
        R('EMP GRENADES', '戰略', [T('EMP Grenades', 'def', [('hit', -1)], why='只對敵方 VEHICLE；原文是 WS/BS 變差 1，以 -1 命中近似')], cp='1', need=['KROOT', 'GRENADES']),
    ],
    # Starfire Cadre
    '000000966': [
        R('Markerlight Precision', '規則', [T('Markerlight BS+1', 'att', [('skill', 1)], scope='ranged', why='目標要被友方 MARKERLIGHT 單位看見'),
                                          T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', why='目標要被友方 MARKERLIGHT 單位看見')],
          need=TE, need_not=['KROOT']),
        R('RESPONSIVE VOLLEY', '戰略', [T('Responsive Volley', 'att', [('crit_hit', 5)], scope='ranged', why='目標要在艙門另一側')], cp='1', names=['Strike Team', 'Breacher Team', 'Pathfinder']),
    ],
    # Kroot Raiding Party
    '000000967': [
        R('BOARDING BLADES', '戰略', [T('Boarding Blades', 'att', [('ap', 1), ('crit_ap', 1)], scope='melee', why='爆擊造傷時 AP 再多 1')], cp='1', need=['KROOT']),
    ],
    # Auxiliary Cadre
    '000001005': [
        R('EXPERIMENTAL MODIFICATIONS', '戰略', [T('Experimental Modifications', 'att', [('ap', 1)], why='只限 KROOT / VESPID STINGWINGS，這裡未限定')], cp='1'),
        R('GUIDED BY UNITY', '戰略', [T('Guided by Unity', 'att', [('kw', 'LETHAL HITS')], scope='ranged', why='目標要在友方 KROOT/VESPID 9" 內')], cp='1', need=TE, need_not=['KROOT', 'VESPID STINGWINGS']),
    ],
    # Experimental Prototype Cadre
    '000001028': [
        R('EXPERIMENTAL AMMUNITION', '戰略', [T('+1 S', 'att', [('strength', 1)], scope='ranged', pick='ammo'),
                                            T('+1 S, +1 AP (Hazardous)', 'att', [('strength', 1), ('ap', 1)], scope='ranged', pick='ammo', why='AP 數值原文缺，按 +1 算；Hazardous 未算')],
          cp='1', need=['BATTLESUIT', 'CHARACTER']),
    ],
    # Advanced Acquisition Cadre
    '000001200': [
        R('AUTOREACTIVE CAMOUFLAGE', '戰略', [T('Autoreactive Camouflage', 'def', [('sv', 1)], why='要在 hidden 狀態')], cp='1', names=['Pathfinder', 'Stealth']),
    ],
}

ENH = {
    # Kauyon
    'Precision of the Patient Hunter': [T('Precision of the Patient Hunter', 'att', [('hit', 1)], scope='ranged', on=True, unitwide=False),
                                        T('Precision of the Patient Hunter (round 3+)', 'att', [('wound', 1)], scope='ranged', on=False, unitwide=False, why='第 3 回合起')],
    'Through Unity, Devastation': [T('Through Unity, Devastation', 'att', [('kw', 'LETHAL HITS')], scope='ranged', on=False, why='該單位是 Observer，Guided 單位打 Spotted 時')],
    # Mont'ka
    'Coordinated Exploitation': [T('Coordinated Exploitation', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', on=False, why='該單位是 Observer，Guided 單位打 Spotted 時')],
    # Retaliation Cadre
    'Prototype Weapon System': [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='ranged', on=True, unitwide=False, pick='proto'),
                                T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', on=True, unitwide=False, pick='proto')],
    # Kroot Hunting Pack
    'Borthrod Gland': [T('Borthrod Gland', 'att', [('crit_hit', 5)], scope='melee', on=True)],
    'Kroothawk Flock': [T('Kroothawk Flock', 'att', [('kw', 'IGNORES COVER')], scope='ranged', on=True)],
    'Root-carved Weapons': [T('Root-carved Weapons', 'att', [('kw', 'DEVASTATING WOUNDS')], on=True, unitwide=False, why='PRECISION 未算')],
    # Starfire Cadre
    'Target Optimisation Microdrones': [T('Target Optimisation Microdrones', 'att', [('ap', 1)], scope='ranged', on=True, why='每回合一次，範圍 6" 內的 FIRE WARRIOR/PATHFINDER/FIREBLADE 單位')],
    # Kroot Raiding Party
    'Experienced Leader': [T('Experienced Leader', 'att', [('rr_wound', 'all')], on=False, why='只打開戰選的那一隊')],
    # Experimental Prototype Cadre
    'Thermoneutronic Projector': [T('Thermoneutronic Projector', 'att', [('strength', 2), ('ap', 1)], weapon='flamer', on=True, unitwide=False, why='原文 D 的數值缺，未算傷害')],
    'Plasma Accelerator Rifle': [T('Plasma Accelerator Rifle', 'att', [('strength', 2), ('attacks', 1)], weapon='plasma rifle', on=True, unitwide=False, why='原文 AP、D 的數值缺，未算')],
    'Supernova Launcher': [T('Supernova Launcher', 'att', [('strength', 3), ('ap', 1)], weapon='airbursting fragmentation', on=True, unitwide=False, why='原文 D 的數值缺，未算傷害')],
}
