from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

ARMY = {
    # Acts of Faith：Miracle dice 替換骰值，無法標記成固定效果
}

NOT_PEN = ['Arco', 'Repentia']

DET = {
    # Hallowed Martyrs
    '000000791': [
        R('The Blood of Martyrs (Below Starting Strength)', '規則', [T('Blood of Martyrs +1 Hit', 'att', [('hit', 1)], why='單位低於起始人數才有效')], on=False),
        R('The Blood of Martyrs (Below Half-strength)', '規則', [T('Blood of Martyrs +1 Wound', 'att', [('wound', 1)], why='單位低於半數才有效（同時也低於起始人數，兩條都要勾）')], on=False),
        R('Righteous Vengeance', '戰略', [
            T('Righteous Vengeance hit', 'att', [('rr_hit', 'all')], scope='melee'),
            T('Righteous Vengeance wound', 'att', [('rr_wound', 'all')], scope='melee', on=False, why='單位低於半數才能重骰造傷'),
        ], cp='1'),
    ],
    # Penitent Host
    '000000878': [
        R('Absolution in Battle', '規則', [T('Absolution in Battle', 'att', [('attacks', 1), ('strength', 1)], scope='melee', cond='charge', why='要選這個 Vow（每場一次）')], on=False, model_kw=['PENITENT']),
        R('Passion of the Penitent', '戰略', [T('Passion of the Penitent', 'att', [('crit_hit', 5)], scope='melee')], cp='1', need=['PENITENT']),
        R('Purity of Suffering', '戰略', [T('Purity of Suffering', 'def', [('fnp', 4)])], cp='1', need=['PENITENT']),
    ],
    # Bringers of Flame
    '000000879': [
        R('Fervent Purgation', '規則', [T('Fervent Purgation', 'att', [('strength', 1)], scope='ranged', why='只在目標 6" 內；[ASSAULT] 與傷害無關')], on=False),
        R('Cleansing Flames', '戰略', [T('Cleansing Flames', 'att', [('kw', 'DEVASTATING WOUNDS')], scope='ranged', wkw='TORRENT')], cp='2'),
        R('Shield of Aversion', '戰略', [T('Shield of Aversion', 'def', [('ap', -1)])], cp='1'),
        R('Righteous Blows', '戰略', [T('Righteous Blows', 'att', [('kw', 'LETHAL HITS')], scope='melee')], cp='1'),
        R('Rites of Fire', '戰略', [T('Rites of Fire', 'att', [('wound', 1)], scope='ranged', why='要剛從運輸載具下車，目標 6" 內且在目標點範圍內')], cp='1'),
    ],
    # Army of Faith
    '000000880': [
        R('Light of the Emperor', '戰略', [T('Light of the Emperor', 'att', [('ign', 1)], why='無視命中／BS 等修正（只標攻擊面）')], cp='2'),
        R('Divine Guidance', '戰略', [T('Divine Guidance', 'att', [('ap', 1)])], cp='1'),
        R('Faith and Fury', '戰略', [T('Faith and Fury', 'att', [('kw', 'LANCE')], scope='melee')], cp='1'),
        R('Blinding Radiance', '戰略', [T('Blinding Radiance', 'def', [('hit', -1)])], cp='1', need=['INFANTRY']),
    ],
    # Pious Protectors
    '000000916': [
        R('The Emperor Protects', '規則', [
            T('Inv 4+', 'def', [('inv', 4)], pick='inv', why='要在目標點範圍內'),
            T('Inv 3+ (Secure Site)', 'def', [('inv', 3)], pick='inv', why='要在目標點範圍內，且上個射擊階段執行過 Secure Site'),
        ], on=False, names_not=NOT_PEN),
        R('Prayer of Precision', '戰略', [
            T('Re-roll Hit 1', 'att', [('rr_hit', '1')], scope='ranged', pick='prec'),
            T('Re-roll Hit (discard Miracle dice)', 'att', [('rr_hit', 'all')], scope='ranged', pick='prec', why='要棄 1 顆 Miracle dice'),
        ], cp='1'),
    ],
    # Penitents and Pilgrims
    '000000917': [
        R('Contempt for Death', '戰略', [T('Contempt for Death', 'def', [('wound', -1)], cond='s_gt_t')], cp='1'),
    ],
    # Champions of Faith
    '000001003': [
        R('Righteous Purpose', '規則', [T('Righteous Purpose', 'att', [('skill', 1)], why='單位要被選為 Righteous（每回合最多 3 隊）')], on=False,
          names=['Battle Sisters', 'Insidiants', 'Sacresants', 'Paragon']),
        R('Bastion of Faith', '戰略', [T('Bastion of Faith', 'def', [('hit', -1)])], cp='1', names=['Sacresants']),
        R('To the Heart of Heresy', '戰略', [
            T('To the Heart of Heresy S', 'att', [('strength', 1)], scope='melee'),
            T('To the Heart of Heresy AP', 'att', [('ap', 1)], scope='melee', on=False, why='單位要是 Righteous'),
        ], cp='1'),
        R('Suffer Not the Unfaithful', '戰略', [
            T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], pick='suffer', why='單位要是 Righteous'),
            T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], pick='suffer', why='單位要是 Righteous'),
        ], cp='1'),
    ],
    # Chorus of Condemnation
    '000001155': [
        R('Devastating Reprise', '戰略', [T('Devastating Reprise', 'att', [('kw', 'DEVASTATING WOUNDS')], scope='ranged', tkw_not=MV, why='只打被 Exorcist 打中的那一隊')], cp='1', need=['INFANTRY', 'FLY']),
        R('Harmonised Exorcism', '戰略', [T('Harmonised Exorcism', 'att', [('hit', 1)], scope='ranged', why='只打選定的那一隊（9" 內且有 INFANTRY FLY 友軍看得到）')], cp='1', need=['EXORCIST']),
    ],
    # Sacred Champions
    '000001156': [
        R('Holy Quest', '規則', [T('Holy Quest', 'att', [('skill', 1)])], on=True, need=['CELESTIAN']),
        R('Sanctified Blows', '戰略', [T('Sanctified Blows', 'att', [('attacks', 1), ('strength', 1)], scope='melee')], cp='1', names=['Sacresants']),
    ],
    # Sanctified Orators：只有強化
    '000001157': [],
}

ENH = {
    # Hallowed Martyrs
    'Through Suffering, Strength': [
        T('Through Suffering, Strength', 'att', [('attacks', 1), ('strength', 1), ('dmg', 1)], scope='melee', on=True, unitwide=False),
        T('Through Suffering, Strength (wounded)', 'att', [('attacks', 1), ('strength', 1), ('dmg', 1)], scope='melee', on=False, unitwide=False, why='持有者已受傷：總共 +2（此條在基本 +1 之上再 +1）'),
    ],
    # Penitent Host
    'Refrain of Enduring Faith': [T('Refrain of Enduring Faith', 'def', [('inv', 5)], on=True, why='持有者帶領單位時')],
    # Bringers of Flame
    'Righteous Rage': [T('Righteous Rage', 'att', [('attacks', 1), ('strength', 1)], scope='melee', on=False, unitwide=False, why='每棄 1 顆 Miracle dice +1（最多 3 顆），這裡以 1 顆計')],
    'Fire and Fury': [
        T('Fire and Fury Torrent', 'att', [('attacks', 1)], scope='ranged', wkw='TORRENT', on=True),
        T('Fire and Fury Sustained', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', on=True, why='原文只給非 Torrent 武器（Torrent 自動命中，無差別）'),
    ],
    'Iron Surplice of Saint Istalela': [T('Iron Surplice of Saint Istalela', 'def', [('fnp', 5), ('sv', 1)], on=True, unitwide=False, why='Save 變 2+，以原本 3+ 改善 1 近似')],
    # Army of Faith
    'Blade of Saint Ellynor': [T('Blade of Saint Ellynor', 'att', [('strength', 1), ('ap', 1)], scope='melee', on=True, unitwide=False, why='[PRECISION] 沒算')],
    # Penitents and Pilgrims
    'Fervent Ferocity': [T('Fervent Ferocity', 'def', [('fnp', 4)], on=True, unitwide=False)],
    # Champions of Faith
    'Triptych of Judgement': [T('Triptych of Judgement', 'att', [('ign', 1)], on=True)],
    'Mark of Devotion': [
        T('Mark of Devotion', 'att', [('attacks', 1)], scope='melee', on=True, unitwide=False),
        T('Mark of Devotion (Righteous)', 'att', [('attacks', 1), ('dmg', 1)], scope='melee', on=False, unitwide=False, why='單位是 Righteous：總共 +2 A、+1 D（此條在基本 +1 A 之上再加）'),
    ],
    # Sanctified Orators
    'Hagiomnifex': [
        T('Psalm of Righteous Smiting', 'att', [('strength', 1)], on=False, pick='hagio', why='每回合開始選一個能力'),
        T('Chorus of Repudiation', 'def', [('wound', -1)], cond='s_gt_t', on=False, pick='hagio', why='每回合開始選一個能力'),
    ],
}
