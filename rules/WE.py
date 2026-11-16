from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

ARMY = {
    # 000008359 Dark Pacts：只限 HERETIC ASTARTES 軍隊陣營，WE 不適用，不標記
    # 000010071 Pact of Blood：只影響組軍，不標記
    '000008428': dict(name='Blessings of Khorne', rules=[
        R('Martial Excellence', '軍隊規則', [T('Martial Excellence', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee')],
          note='每回合最多啟動兩個祝福，使用者自己勾選'),
        R('Warp Blades', '軍隊規則', [T('Warp Blades', 'att', [('kw', 'LETHAL HITS')], scope='melee')],
          note='每回合最多啟動兩個祝福，使用者自己勾選'),
        R('Decapitating Strikes', '軍隊規則', [T('Decapitating Strikes', 'att', [('kw', 'DEVASTATING WOUNDS')], scope='melee', tkw=['INFANTRY'])],
          note='每回合最多啟動兩個祝福，使用者自己勾選'),
    ]),
}

DET = {
    # Berzerker Warband
    '000000777': [
        R('Relentless Rage', '規則', [T('Relentless Rage', 'att', [('attacks', 1)], scope='melee')], on=True, need=['WORLD EATERS']),
        R('Frenzied Resilience', '戰略', [T('Frenzied Resilience', 'def', [('dmg', -1)], scope='melee', why='原文限被選為目標時')], cp='2', need=['WORLD EATERS']),
        R('Hack and Slash', '戰略', [T('Hack and Slash', 'att', [('ap', 1)], scope='melee', why='限本回合衝鋒過的單位')], cp='1', need=['WORLD EATERS']),
    ],
    # Boarding Butchers
    '000000977': [
        R('Savage Resilience', '戰略', [T('Savage Resilience', 'def', [('dmg', -1)], scope='ranged')], cp='1', need=['WORLD EATERS']),
        R('Unstoppable Rage', '戰略', [T('Unstoppable Rage', 'def', [('hit', -1)], why='只對艙門另一側 3" 內的敵方單位有效（眩暈）')], cp='1', need=['WORLD EATERS']),
    ],
    # Skullsworn：Reap the Tally 為死後還能打，程式不算；戰略只有移動／目標點
    '000000978': [],
    # Vessels of Wrath
    '000001007': [
        R('Wrath of Khorne', '規則', [T('Cleave 1', 'att', [('kw', 'CLEAVE 1')], scope='melee', pick='wrath'),
                                    T('+1 AP', 'att', [('ap', 1)], scope='melee', pick='wrath')],
          on=True, need=['WORLD EATERS', 'CHARACTER'], need_not=['EPIC HERO'], model_kw=['CHARACTER'],
          note='每次打架二選一；限 CHARACTER 模型'),
        R('Aspire to Infamy', '戰略', [T('Aspire to Infamy', 'att', [('attacks', 1), ('strength', 2)], scope='melee')],
          cp='1', need=['WORLD EATERS', 'CHARACTER'], need_not=['EPIC HERO'], model_kw=['CHARACTER']),
        # Scorn the Witch 只對致命傷，不標記
    ],
    # Cult of Blood
    '000001042': [
        R('Idols of Khorne', '規則', [
            T('Idol of Infinite Rage', 'att', [('hit', 1), ('wound', 1)], pick='idol', why='需在 Monster/Titanic 光環範圍內（6"/9"），且已選此 Idol'),
            T('Idol of Blessed Blood', 'def', [('inv', 4)], pick='idol', why='需在 Monster/Titanic 光環範圍內（6"/9"），且已選此 Idol'),
        ], names=['Jakhals', 'Goremongers'], note='每個 Idol 每場只能選一次，一次一個'),
        R('Bloody Vengeance', '戰略', [T('Bloody Vengeance', 'att', [('rr_hit', 'all')], why='只打毀滅己方 Monster/Titanic 的那一隊')], cp='1', names=['Jakhals', 'Goremongers']),
        R('In the Shadow of Brass Idols', '戰略', [T('In the Shadow of Brass Idols', 'def', [('fnp', 6)], why='靠近己方 Monster 6"／Titanic 9" 內改為 FNP 5+')], cp='1', names=['Jakhals', 'Goremongers']),
        R('Fail Not the Blood God', '戰略', [T('Fail Not the Blood God', 'att', [('rr_hit', '1')], scope='melee', why='靠近己方 Monster 6"／Titanic 9" 內可重骰全部命中（此處只算重骰 1）')], cp='1', names=['Jakhals', 'Goremongers']),
    ],
    # Khorne Daemonkin
    '000001043': [
        R('Daemonic Rage', '規則', [T('Daemonic Rage', 'att', [('kw', 'LANCE')], scope='melee')], need=['BLOOD LEGIONS'], note='需花 3 BTP 啟動'),
        R('Boon of Blood', '規則', [T('Boon of Blood', 'def', [('inv', 4)])], need=['BLOOD LEGIONS'], note='需花 4 BTP 啟動'),
        R('Blessing of Burning Blood', '戰略', [T('Blessing of Burning Blood', 'def', [('inv', 5)], why='Boon of Blood 啟動時改為 4+')], cp='1', need=['WORLD EATERS']),
        R('Daemonic Fury', '戰略', [T('Daemonic Fury', 'att', [('kw', 'LANCE')], scope='melee', why='Daemonic Rage 啟動時再加 TWIN-LINKED（未算）')], cp='1', need=['WORLD EATERS']),
    ],
    # Possessed Slaughterband
    '000001044': [
        R('Daemonic Resistance', '戰略', [T('Daemonic Resistance', 'def', [('wound', -1)])], cp='2', need=['WORLD EATERS', 'POSSESSED']),
        R('Daemonic Strength (Eightbound)', '戰略', [T('Daemonic Strength', 'att', [('dmg', 1)], tkw_not=MV)], cp='1', need=['WORLD EATERS', 'POSSESSED', 'EIGHTBOUND'],
          note='Eightbound 打非 MONSTER/VEHICLE'),
        R('Daemonic Strength (Exalted)', '戰略', [T('Daemonic Strength', 'att', [('dmg', 1)], tkw=MV)], cp='1', need=['WORLD EATERS', 'POSSESSED', 'EXALTED EIGHTBOUND'],
          note='Exalted Eightbound 打 MONSTER/VEHICLE'),
        # Immortal Fury 死後還能打，不算
    ],
    # Goretrack Onslaught
    '000001045': [
        R('Rush to the Fray', '規則', [T('Rush to the Fray', 'att', [('kw', 'LANCE')], scope='melee', why='限本回合從運輸載具下車的單位')], need=['WORLD EATERS']),
    ],
    # Brazen Engines
    '000001178': [
        R('Apoplectic Clarity', '戰略', [T('Apoplectic Clarity', 'att', [('ign', 1)])], cp='1', need=['DAEMON', 'VEHICLE']),
    ],
    # Butchers of Khorne
    '000001179': [
        R('Adamantine Avalanche (Martial Excellence)', '規則', [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee', pick='aa', why='戰鬥階段開始骰祝福，隨機啟動一個')],
          need=['TERMINATOR SQUAD'], note='隨機啟動一個祝福，使用者自己勾選'),
        R('Adamantine Avalanche (Warp Blades)', '規則', [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='melee', pick='aa', why='隨機啟動一個祝福')],
          need=['TERMINATOR SQUAD']),
        R('Adamantine Avalanche (Decapitating Strikes)', '規則', [T('Devastating Wounds', 'att', [('kw', 'DEVASTATING WOUNDS')], scope='melee', tkw=['INFANTRY'], pick='aa', why='隨機啟動一個祝福')],
          need=['TERMINATOR SQUAD']),
        R('Wrath Beyond Reason', '戰略', [T('Wrath Beyond Reason', 'def', [('dmg', -1)], scope='ranged')], cp='2', need=['TERMINATOR SQUAD']),
        R('A Trophy for the Throne', '戰略', [T('A Trophy for the Throne', 'att', [('wound', 1)], scope='melee', tkw=MV)], cp='1', need=['TERMINATOR SQUAD']),
        R('Focused Ferocity', '戰略', [T('Focused Ferocity', 'att', [('attacks', 1)], scope='melee')], cp='1', need=['TERMINATOR SQUAD']),
    ],
}

ENH = {
    'Berzerker Glaive': [T('Berzerker Glaive', 'att', [('attacks', 1), ('dmg', 1)], scope='melee', on=True, unitwide=False, why='不含 Extra Attacks 武器')],
    'Helm of Brazen Ire': [T('Helm of Brazen Ire', 'def', [('dmg', -1)], on=True, unitwide=False)],
    'Brazen Form': [T('Brazen Form', 'def', [('fnp', 5)], on=True, unitwide=False, why='另有 T+1 沒算')],
    'Blade of Endless Bloodshed': [T('Blade of Endless Bloodshed', 'att', [('attacks', 1), ('strength', 1), ('dmg', 1)], scope='melee', on=True, unitwide=False)],
    'Frenzied Focus': [T('Frenzied Focus', 'att', [('crit_hit', 5)], on=True, why='限 DAEMON 模型所在的單位')],
    'Talons of Butchery': [T('Talons of Butchery', 'att', [('kw', 'CLEAVE 2')], scope='melee', weapon='maulerfiend fist', on=True)],
    'Gore-Stained Veterans': [T('Gore-Stained Veterans', 'att', [('skill', 1)], scope='melee', on=True)],
}
