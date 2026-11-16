from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

ARMY = {
    # 000008359 Dark Pacts 寫在 CSM.py
    '000008512': dict(name='Harbingers of Dread', rules=[
        R('Doom', '軍隊規則', [T('Doom', 'att', [('wound', 1)], why='只打 Battle-shocked 的目標；要先選中 Doom')]),
        R('Darkness', '軍隊規則', [T('Darkness', 'def', [('cover', 1)], why='Stealth；要先選中 Darkness')]),
    ]),
    '000008513': dict(name='Super-heavy Walker', rules=[]),   # 只有移動
    '000008514': dict(name='Dreadblades', rules=[]),          # 只有組軍
}

DET = {
    '000000806': [   # Traitoris Lance
        R('Conquerors Without Mercy', '戰略', [T('Conquerors Without Mercy', 'att', [('ap', 1)], scope='melee', cond='charge')], cp='1'),
        R('Disdain for the Weak', '戰略', [T('Disdain for the Weak', 'def', [('fnp', 6)], scope='melee'),
                                          T('Disdain for the Weak (battle-shocked)', 'def', [('fnp', 5)], scope='melee', pick='dftw', why='只對 Battle-shocked 的攻擊者 FNP 5+，否則 6+')], cp='1', need=['CHAOS KNIGHTS']),
        R('Storm of Darkness', '戰略', [T('Storm of Darkness', 'def', [('cover', 1)], why='Stealth'),
                                       T('Storm of Darkness (melee)', 'def', [('hit', -1)], scope='melee')], cp='1', need=['CHAOS KNIGHTS']),
        # Paragons of Terror / Imperious Advance / A Long Leash / Pterrorshades（致命傷為對方單位，未計）：不影響攻擊結果
    ],
    '000000989': [   # Iconoclast Fiefdom
        R('Avenge the Masters!', '戰略', [T('Avenge the Masters!', 'att', [('kw', 'LETHAL HITS')], why='只打被標記的那一隊')], cp='1', need=['DAMNED']),
    ],
    '000001075': [   # Infernal Lance
        R('Malefic Surge: Diabolic Power', '規則', [T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], pick='surge'),
                                                T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], pick='surge')],
          note='要先在指揮階段 Malefic Surge 且變 Empowered（失敗受 D3 致命傷，未計）'),
        R('Malefic Surge: Unnatural Fortitude', '規則', [T('5+ invulnerable', 'def', [('inv', 5)], pick='fort'),
                                                    T('Feel No Pain 6+', 'def', [('fnp', 6)], pick='fort')],
          note='要先 Malefic Surge 且變 Empowered；被攻擊時二選一'),
        R('Hellforged Construction', '戰略', [T('Hellforged Construction', 'def', [('ap', -1)], scope='melee')], cp='1', need=['CHAOS KNIGHTS']),
        R('Warp Vision', '戰略', [T('Warp Vision', 'att', [('kw', 'IGNORES COVER')], scope='ranged')], cp='1', need=['CHAOS KNIGHTS']),
        R('Diabolic Bulwark', '戰略', [T('Diabolic Bulwark', 'def', [('inv', 4)], scope='ranged')], cp='1', need=['CHAOS KNIGHTS']),
    ],
    '000001076': [   # Lords of Dread
        R('Titanic Duel', '戰略', [T('Titanic Duel', 'att', [('rr_hit', '1'), ('rr_wound', '1')], tkw=MV, pick='duel', why='只打被選的那一隊'),
                                  T('Titanic Duel (TITANIC)', 'att', [('rr_hit', 'all'), ('rr_wound', 'all')], tkw=['TITANIC'], pick='duel', why='只打被選的那一隊，目標是 TITANIC')],
          cp='1', need=['CHARACTER', 'CHAOS KNIGHTS']),
        R('Runes of Disdain', '戰略', [T('Runes of Disdain', 'def', [('dmg', -1)])], cp='2', need=['CHARACTER', 'CHAOS KNIGHTS']),
        # Tyrannical Court / Crushed Like Vermin（致命傷為對方單位，未計）/ 其餘：不影響傷害
    ],
    '000001077': [   # Houndpack Lance
        R('Marked Prey', '規則', [T('Marked Prey', 'att', [('kw', 'SUSTAINED HITS 1')], why='只打被選的那一隊，且要看得見')], need=['WAR DOG']),
        R('Hungry for Combat', '戰略', [T('Hungry for Combat', 'att', [('crit_hit', 5)], why='要兩隊以上 War Dog 圍同一個敵人，只能打被選的那一隊')], cp='1', need=['WAR DOG']),
    ],
    '000001144': [   # Helhunt Lance
        R('Merciless Fusillade', '戰略', [T('Merciless Fusillade', 'att', [('kw', 'SUSTAINED HITS 1')], why='只打被選的那一隊；限 Titanic 單位和最多兩隊 War Dog')], cp='1'),
        R('Beasthide Manifestation', '戰略', [T('Beasthide Manifestation', 'def', [('ap', -1)])], cp='1', need=['CHAOS KNIGHTS']),
        # Masters of the Pack：光環共享，不直接算；Feral Arrogance 只對致命傷，未計
    ],
    '000001173': [   # Bastions of Tyranny
        R('Annihilate the Unworthy', '規則', [T('Annihilate the Unworthy', 'att', [('hit', 1)], why='只打 Battle-shocked 的目標')], need=['KNIGHT TYRANT']),
        R('Intimidating Reminder', '戰略', [T('Intimidating Reminder', 'def', [('hit', -1)], why='只對被壓制的那一隊敵人（需先射中它）')], cp='1', need=['KNIGHT TYRANT']),
        # Rune-Cursed Stronghold 只對致命傷，未計
    ],
    '000001174': [   # Hunting Warpack
        R('Stalking Focus', '戰略', [T('Stalking Focus', 'def', [('ap', -1)], scope='ranged', why='要在目標點範圍內')], cp='1', need=['WAR DOG']),
        R('Insensate Bloodthirst', '戰略', [T('Insensate Bloodthirst', 'def', [('fnp', 5)], scope='melee')], cp='1', need=['WAR DOG']),
    ],
}

ENH = {
    'Veil of Medrengard': [T('Veil of Medrengard (ranged)', 'def', [('inv', 4)], scope='ranged', on=True, unitwide=False),
                           T('Veil of Medrengard (melee)', 'def', [('inv', 5)], scope='melee', on=True, unitwide=False)],
    'Knight Diabolus': [T('Knight Diabolus', 'att', [('skill', 1)], scope='melee', on=True, unitwide=False),
                        T('Knight Diabolus (Lance)', 'att', [('kw', 'LANCE')], scope='melee', on=False, unitwide=False, why='只在使用 Diabolic Power 時')],
    'Blessing of the Dark Master': [T('Blessing of the Dark Master', 'def', [('cover', 1)], on=True, unitwide=False, why='Stealth；每場一次改傷害為 0 未計')],
    'Panoply of the Cursed Knight': [T('Panoply of the Cursed Knight', 'def', [('ap', -1)], on=True, unitwide=False)],
    'Final Howl (Aura)': [T('Final Howl', 'att', [('rr_wound', '1')], on=False, why='光環：只給 6" 內的友方 War Dog')],
    'Snarling Rivalry': [T('Snarling Rivalry', 'att', [('kw', 'IGNORES COVER')], scope='ranged', on=True)],
}
