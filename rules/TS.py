from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

TS = ['THOUSAND SONS']

ARMY = {
    # 000008359 Dark Pacts 寫在 CSM.py
    '000008424': dict(name='Cabal of Sorcerers', rules=[
        R('Destiny’s Ruin', '軍隊規則', [T('Destiny’s Ruin', 'att', [('rr_hit', '1')], why='Psychic test 5 成功；10+ 可重骰全部命中；只打被選的那一隊')], on=False, need=TS),
        R('Twist of Fate', '軍隊規則', [T('Twist of Fate', 'att', [('ap', 1)], why='Psychic test 9 成功；12+ 為 AP+2；只打被選的那一隊')], on=False, need=TS),
        R('Doombolt', '軍隊規則', [T('Doombolt', 'att', [('mw', 2)], scope='ranged', why='Psychic test 7 成功；D3 致命傷（11+ 為 D3+3）；只打被選的那一隊')], on=False),
    ]),
}

DET = {
    '000000969': [
        R('Witchsight', '規則', [T('Witchsight', 'att', [('kw', 'IGNORES COVER')], scope='ranged')], on=True, need=TS),
        R('Tzeentch’s Boon', '戰略', [T('Tzeentch’s Boon', 'att', [('rr_wound', 'all')], wkw='PSYCHIC', why='只限 Psychic Attack；單位要在目標點範圍內')], cp='1', need=['PSYKER']),
        R('Costly Blessing', '戰略', [T('Costly Blessing', 'def', [('inv', 3)], scope='melee', why='只給 PSYKER CHARACTER 模型；階段結束受 D3 致命傷')], cp='1', need=['PSYKER', 'CHARACTER']),
        # Empyric Desecration / Inferno Bolters (AP 0，穿艙門) 不影響傷害
    ],
    '000000970': [
        R('Fervent Devotees', '規則', [T('Fervent Devotees', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee', why='目標單位要在目標點範圍內')], on=False, need=TS),
        R('Flesh Change', '戰略', [T('Flesh Change', 'def', [('fnp', 5)])], cp='1', need=['TZAANGORS']),
    ],
    '000000971': [],   # Overwatch、PISTOL、可見性、移動、fight on death（不算）
    '000000983': [
        R('Flow of Magic (re-roll 1)', '規則', [T('Flow of Magic', 'att', [('rr_wound', '1')], wkw='PSYCHIC', why='只限 Psychic Attack')], on=True, need=TS),
        R('Flow of Magic (+1 wound)', '規則', [T('Flow of Magic +1', 'att', [('wound', 1)], wkw='PSYCHIC', why='模型要完全在 Flow of Magic 內；此時取代重骰 1')], on=False, need=TS),
        R('Kaleidoscopic Tempest', '戰略', [T('Kaleidoscopic Tempest', 'def', [('cover', 1)], scope='ranged', why='Stealth')], cp='1', need=['PSYKER']),
        R('Scouring Warpflame', '戰略', [T('Scouring Warpflame', 'att', [('kw', 'IGNORES COVER')], scope='ranged', why='單位要完全在 Flow of Magic 內')], cp='1', need=['PSYKER']),
        # Wrath of the Doomed 屬 fight on death，不算
    ],
    '000001061': [
        R('Kindred Sorcery: Psychic Maelstrom', '規則', [T('Psychic Maelstrom', 'att', [('wound', 1)], wkw='PSYCHIC', pick='kindred')], on=False, need=TS, note='每場每種只能選一次，三選一'),
        R('Kindred Sorcery: Wrath of the Immaterium', '規則', [T('Wrath of the Immaterium', 'att', [('kw', 'DEVASTATING WOUNDS')], wkw='PSYCHIC', pick='kindred')], on=False, need=TS, note='每場每種只能選一次，三選一'),
        R('Devastating Sorcery', '戰略', [T('Devastating Sorcery', 'att', [('rr_hit', 'all'), ('rr_wound', 'all')], wkw='PSYCHIC', why='只限 Psychic weapon')], cp='2', need=['PSYKER']),
        R('Psychic Dominion', '戰略', [T('Psychic Dominion', 'def', [('fnp', 4)], why='只對 Psychic Attack 有效（程式無法區分，近似全部攻擊）；對方 Psychic 武器還有 Hazardous')], cp='1', need=TS),
        # Destined by Fate（失敗豁免後傷害變 0，單一次）、Egotistical Power（重複選）不算
    ],
    '000001062': [
        R('Daemonic Illusions', '規則', [T('Daemonic Illusions', 'def', [('inv', 4)], scope='ranged', why='要在 6" 內有可見的 SCINTILLATING LEGIONS 單位')], on=False, need=['PSYKER']),
        R('Sulphurous Veil', '戰略', [T('Sulphurous Veil', 'def', [('hit', -1)])], cp='1'),
    ],
    '000001063': [
        R('Warpmeld Sacrifice (attack)', '規則', [T('Warpmeld Sacrifice', 'att', [('wound', 1)], why='選擇獻祭：階段結束受 D3 致命傷（自傷沒算）')], on=False),
        R('Warpmeld Sacrifice (defend)', '規則', [T('Warpmeld Sacrifice', 'def', [('wound', -1)], why='選擇獻祭：階段結束受 D3 致命傷（自傷沒算）；限 TZEENTCH MUTANT')], on=False),
        R('Warped Vicissitude', '戰略', [T('Warped Vicissitude', 'def', [('inv', 4)])], cp='1', need=['TZAANGORS']),
    ],
    '000001064': [
        R('All is Dust', '規則', [T('All is Dust', 'def', [('sv', 1)], why='只對原始傷害 1 的攻擊有效（程式無法判斷，近似全部）')], on=False, need=['RUBRICAE']),
        R('Unwavering Phalanx', '戰略', [T('Unwavering Phalanx', 'def', [('wound', -1)], cond='s_gt_t')], cp='1', need=['RUBRIC MARINES']),
        R('Implacable Guardians', '戰略', [T('Implacable Guardians', 'def', [('dmg', -1)], scope='ranged', why='不含 PSYKER 模型')], cp='2', need=['RUBRIC MARINES', 'PSYKER'], model_not=['PSYKER']),
        # Inexorable Advance (Assault)、Infernal Fusillade (Psychic 標籤)、Revenge of the Rubricae 不算
    ],
    '000001065': [
        R('Warpfire Infusion (base)', '規則', [T('Warpfire Infusion', 'att', [('rr1', 1)], why='重骰一顆命中或一顆造傷或一次傷害骰；傷害骰沒算')], on=True, need=TS + ['VEHICLE']),
        R('Warpfire Infusion (near Psyker)', '規則', [T('Warpfire Infusion near Psyker', 'att', [('rr1', 1)], why='6" 內有 Thousand Sons Psyker：命中、造傷各重骰一顆（與上條合計 2）；傷害骰沒算')], on=False, need=TS + ['VEHICLE']),
        R('Ensorcelled Infusion', '戰略', [T('Ensorcelled Infusion', 'att', [('wound', 1)], scope='ranged', why='要在 6" 內有 Thousand Sons Psyker 單位')], cp='2', need=TS + ['VEHICLE']),
        R('Hex-marked Armour', '戰略', [T('Hex-marked Armour', 'def', [('ap', -1)])], cp='1', need=TS + ['VEHICLE']),
        R('Malevolent Animus', '戰略', [T('Malevolent Animus', 'att', [('ign', 1)], why='可無視命中／造傷／BS 修正；要在 6" 內有 Thousand Sons Psyker')], cp='1', need=TS + ['VEHICLE']),
        # Mutate Landscape、Warpflame Gargoyles（衝鋒階段致命傷）、Deadly Demise 不算
    ],
    '000001170': [],   # 只有回血、重生、致命傷 FNP、移動相關
    '000001171': [
        R('Infusion', '規則', [T('Infusion', 'att', [('skill', 1)], scope='melee', why='12" 內有友軍 SEKHETAR ROBOTS；原文 +1 WS 當作 WS 改善 1')], on=False, need=['PSYKER']),
        R('Warp Fields', '戰略', [T('Warp Fields', 'def', [('wound', -1)], scope='ranged', cond='s_gt_t', why='要在 12" 內有 Thousand Sons Psyker')], cp='1', need=['SEKHETAR ROBOTS']),
    ],
    '000001172': [],   # 偵測範圍、移動相關（Mobile、Assault）不算
}

ENH = {
    'Prescient Authority': [T('Prescient Authority', 'att', [('rr_wound', '1')], on=False, why='每回合一次；單位在持有者 3" 內；限 CULTISTS/TZAANGORS')],
    'Arcane Might': [T('Arcane Might', 'att', [('strength', 1)], wkw='PSYCHIC', on=True),
                     T('Arcane Might (Flow of Magic)', 'att', [('strength', 1)], wkw='PSYCHIC', on=False, why='單位完全在 Flow of Magic 內再多 +1（共 +2）')],
    'Empyric Onslaught': [T('Empyric Onslaught', 'att', [('attacks', 3)], scope='ranged', wkw='PSYCHIC', on=False, unitwide=False, why='持有者完全在 Flow of Magic 內')],
    'Eldritch Vortex of E’taph': [T('Eldritch Vortex of E’taph', 'att', [('strength', 1), ('dmg', 1)], wkw='PSYCHIC', on=True, unitwide=False)],
    'Tome of True Names': [T('Tome of True Names', 'def', [('inv', 2)], on=False, unitwide=False, once=True, why='每場一次，一個階段內')],
    'Diamond of Distortion': [T('Diamond of Distortion', 'def', [('hit', -1)], on=True, why='持有者要帶領單位')],
    'Flowing Flesh': [T('Flowing Flesh', 'def', [('fnp', 4)], on=True, unitwide=False, why='Wounds 改 5 沒算')],
    'Lord of the Rubricae': [T('Lord of the Rubricae', 'att', [('hit', 1)], on=True, why='原文只限 Rubricae 模型；持有者要帶領單位')],
    'The Stave Abominus': [T('The Stave Abominus', 'att', [('kw', 'SUSTAINED HITS D3'), ('kw', 'DEVASTATING WOUNDS')], scope='melee', on=True, unitwide=False)],
    'Occulus Infernum': [T('Occulus Infernum', 'att', [('hit', 1)], scope='ranged', on=False, why='只給 12"... 6" 內友軍 SEKHETAR ROBOTS 單位，且要在移動階段選定')],
    'Thicket of Bladed Bone': [T('Thicket of Bladed Bone', 'att', [('ap', 1), ('kw', 'CLEAVE 1')], scope='melee', on=True)],
}
