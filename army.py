"""軍隊規則、分隊規則、戰略、強化的手動標記（自動讀不出來或讀錯的）。2026-11-15 起，先做禁軍（使用者：「你從禁軍開始」）。
規則都照 Wahapedia 第十一版原文（data/ 裡的 CSV）手動翻成標記，原文沒寫的不自己補。

每一條是 dict：
  name 名稱、kind '規則'|'戰略'|'軍隊規則'、cp、tags [標記]、on 預設算不算
  need 單位要有的關鍵字（全部都要）、need_not 有這些關鍵字的單位不算、names 只限這些資料卡名（含這幾個字就算）
  model_kw / model_not 只給模型（併隊時的那一組）有／沒有這關鍵字的
標記多了幾種效果（engine.py 會處理）：
  ('ign', 1)   可以無視命中、造傷、BS 的修正（只會無視壞的）
  ('mw', x)    每次這個單位攻擊（射擊或近戰一輪）另外造成平均 x 點致命傷
  ('rr1', n)   「重骰一顆命中／一顆造傷」：近似成多 n 次最好武器的攻擊
  pick='組名'  同一組的選項每次攻擊只能挑一個，程式會對每個目標自動挑最好的
"""
from manual import T

MV = ['MONSTER', 'VEHICLE']


def R(name, kind, tags, cp='', on=False, **kw):
    return dict(dict(name=name, kind=kind, cp=cp, tags=tags, on=on, need=[], need_not=[], names=[], model_kw=[], model_not=[]), **kw)


# ---------- 軍隊規則：Abilities.csv 的 id → 規則 ----------
# 套用到資料卡上有這個 Faction 能力的單位
ARMY = {
    '000008391': dict(name='Martial Ka’tah', rules=[
        R('Ka’tah 自動挑最好的一招', '軍隊規則', [
            T('Salvus', 'att', [('ign', 1)], scope='ranged', pick='katah'),
            T('Dacatarai', 'att', [('rr_hit', '1')], scope='melee', tkw_not=MV, pick='katah'),
            T('Rendax', 'att', [('kw', 'LETHAL HITS: MONSTER/VEHICLE')], scope='melee', pick='katah'),
        ], on=True, note='每個單位每回合只能用一招；程式對每個目標各挑最好的那招（稍微偏樂觀）'),
        R('Kaptaris（防守用，用了就不能用上面的攻擊招）', '軍隊規則', [
            T('Kaptaris', 'def', [('hit', -1)], scope='melee')]),
    ]),
}

# ---------- 分隊規則和戰略：分隊英文名 → 規則（取代自動讀的結果） ----------
OBJ = '要在目標點範圍內'
DET = {
    'Auric Champions': [
        R('Assemblage of Might', '規則', [T('Assemblage of Might', 'att', [('wound', 1)], why='只有角色模型、只打被選為 dreadful foe 的那一隊')], model_kw=['CHARACTER']),
    ],
    'Voyagers in Darkness': [
        R('Artificer Rounds', '戰略', [T('Artificer Rounds', 'att', [('kw', 'SUSTAINED HITS 1')], scope='ranged', why='目標要在 6 吋內')], cp='1'),
    ],
    'Black Ship Guardians': [
        R('Priority Quarry', '規則', [T('Priority Quarry', 'att', [('rr_hit', '1')], why='只打被選為 quarry 的兩隊')], need=['ANATHEMA PSYKANA']),
        R('Focused Fear', '戰略', [T('Focused Fear', 'def', [('ap', -1)])], cp='1', need=['ANATHEMA PSYKANA']),
        R('Blades of the Vigilators', '戰略', [T('Blades of the Vigilators', 'def', [('wound', -1)])], cp='1', names=['Vigilator', 'Aleya', 'Knight-Centura']),
        R('Punishment of the Prosecutors', '戰略', [T('Punishment of the Prosecutors', 'att', [('ap', 1)], scope='ranged', why='爆擊造傷再多 AP 1 沒算')], cp='1', names=['Prosecutor']),
    ],
    'Null Maiden Vigil': [
        R('Psy-chaff Volley', '戰略', [T('Psy-chaff Volley', 'att', [('ap', 1)], why='全軍打被 Prosecutor 標記的那一隊')], cp='1'),
        R('Purgation Sweep', '戰略', [T('Purgation Sweep', 'att', [('attacks', 1)], wkw='TORRENT')], cp='1', names=['Witchseeker']),
        R('Anathema Blademastery', '戰略', [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], pick='blademastery'),
                                         T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], pick='blademastery')], cp='1', names=['Vigilator']),
    ],
    'Lions of the Emperor': [
        R('Vigil Unending', '戰略', [T('Vigil Unending', 'def', [('dmg', -1)])], cp='2', need=['TERMINATOR']),
    ],
    'Might of the Moritoi': [
        R('Moritoi Ancients（低於起始人數）', '規則', [T('Moritoi Ancients', 'att', [('rr_hit', '1')], why='無畏低於起始人數時')], need=['DREADNOUGHT']),
        R('Moritoi Ancients（低於半數）', '規則', [T('Moritoi Ancients', 'att', [('rr_hit', '1'), ('rr_wound', '1')], why='無畏低於半數時')], need=['DREADNOUGHT']),
        R('Honoured Interred', '戰略', [T('Honoured Interred', 'att', [('rr_hit', '1')], why='光環：要在那台無畏 6 吋內')], cp='1'),
    ],
    'Shadowkeepers': [
        R('Wardens of the Dark Cells', '規則', [T('Wardens of the Dark Cells', 'def', [('wound', -1)], scope='melee', cond='s_gt_t', why=OBJ)], need_not=MV),
        R('Grim Responsibility', '戰略', [T('Grim Responsibility', 'att', [('kw', 'LETHAL HITS: CHARACTER/MONSTER')], scope='melee')], cp='1', need=['INFANTRY']),
    ],
    'Guardians of the Throne': [
        R('Martial Mastery', '規則', [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee', pick='mastery'),
                                    T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='melee', pick='mastery')], on=True,
          note='每次打架二選一，程式對每個目標自動挑好的'),
        R('In Auramite Clad', '戰略', [T('In Auramite Clad', 'def', [('ap', -1)])], cp='1', names_not=['Custodian Wardens']),
        R('Prime Target', '戰略', [T('Prime Target', 'att', [('rr1', 2)], scope='ranged', why='重骰一顆命中、一顆造傷，約等於多 2 次攻擊；重骰傷害骰沒算')], cp='1'),
    ],
    'Honoured Companions': [
        R('Companion’s Watch', '規則', [T('Companion’s Watch', 'att', [('rr_wound', '1')], why=OBJ)], need=['TRUSTED SENTINEL']),
        R('Avenge the Fallen', '戰略', [T('Avenge the Fallen', 'att', [('attacks', 2)], scope='melee', why='要低於起始人數；角色模型不算')], cp='1',
          need=['TRUSTED SENTINEL'], model_not=['CHARACTER']),
    ],
    'Emperor’s Chosen': [
        R('Magna Imperator', '規則', [T('Magna Imperator', 'att', [('rr1', 2)], why='重骰一顆命中、一顆造傷，約等於多 2 次攻擊')], on=True),
        R('Rendax 加碼（Favoured Ka’tah）', '規則', [T('Rendax 加碼', 'att', [('mw', 11 / 6)], scope='melee', tkw=MV, why='要用 Rendax，平均 1.8 致命傷')], fab='000008391'),
        R('In Auramite Clad', '戰略', [T('In Auramite Clad', 'def', [('ap', -1)])], cp='1', names_not=['Custodian Wardens']),
    ],
    'Emissaries Imperatus': [
        R('Bearers of His Light', '戰略', [T('Bearers of His Light', 'att', [('ign', 1)], scope='melee')], cp='1'),
        R('Slayers of Nightmares', '戰略', [T('Slayers of Nightmares', 'att', [('wound', 1)], scope='melee', cond='t_gt_t')], cp='1'),
    ],
    'Aquilan Shield': [
        R('Gilded Guardians', '規則', [T('Gilded Guardians', 'def', [('wound', -1)], scope='ranged', cond='s_gt_t', why=OBJ)], need_not=MV),
        R('Tip of the Talon', '戰略', [T('Tip of the Talon', 'att', [('strength', 1)], scope='ranged', why='目標要在 9 吋內')], cp='1'),
    ],
    'Grav-Assault Force': [
        R('Flare Shields', '規則', [T('Flare Shields', 'def', [('inv', 4)], scope='ranged')], on=True, need=['GRAV-ASSAULT']),
        R('Inevitable Annihilation', '戰略', [T('Inevitable Annihilation', 'att', [('ign', 1)], scope='ranged')], cp='1', need=['GRAV-ASSAULT']),
    ],
    'Dread Host': [
        R('Golden Light of the Moiraides', '戰略', [T('Golden Light of the Moiraides', 'def', [('hit', -1)], why='要剛做完 ingress 移動')], cp='2'),
    ],
    'Solar Watch': [],
}

# ---------- 強化：英文名（不含括號）→ 標記；預設算（軍表上有寫就是有帶） ----------
ENH = {
    'Memento Moritoi': [T('Memento Moritoi', 'att', [('attacks', 1), ('strength', 1), ('dmg', 1)], scope='melee', on=True, unitwide=False)],
    'Flawless Bladework': [T('Flawless Bladework', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee', on=True, unitwide=False)],
    'Not a Shell Wasted': [T('Not a Shell Wasted', 'att', [('attacks', 1)], scope='ranged', on=True)],
    'From the Hall of Armouries': [T('From the Hall of Armouries', 'att', [('kw', 'DEVASTATING WOUNDS')], scope='melee', on=True, unitwide=False)],
    'Oblivion Knight': [T('Oblivion Knight', 'att', [('hit', 1)], on=True)],
    'Bane of Abominations': [T('Bane of Abominations', 'att', [('wound', 1)], tkw=['CHARACTER', 'MONSTER', 'VEHICLE'], on=True, unitwide=False)],
    'Edge of the Blade': [T('Edge of the Blade', 'att', [('rr_hit', '1'), ('rr_wound', '1')], cond='charge', on=True, unitwide=False)],
    'Radiant Mantle': [T('Radiant Mantle', 'def', [('hit', -1)], on=True)],
    'Auric Exemplar': [T('Auric Exemplar', 'att', [('kw', 'CLEAVE 1')], scope='melee', on=True, unitwide=False)],
    'Augury Uplink': [T('Augury Uplink', 'def', [('fnp', 5)], on=True)],
    'Genalchemic Warding': [T('Genalchemic Warding', 'def', [('fnp', 5)], on=True, unitwide=False)],
}


# ---------- 其他陣營：rules/陣營代號.py（2026-11-16 起由 Sonnet 照 rules/GUIDE.md 手動標記，主 bot 抽查）----------
def _load_rules():
    import glob, importlib.util, os
    for path in sorted(glob.glob(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'rules', '*.py'))):
        name = os.path.basename(path)[:-3]
        if name.startswith('_'):
            continue
        spec = importlib.util.spec_from_file_location('rules_' + name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        ARMY.update(getattr(mod, 'ARMY', {}))
        DET.update(getattr(mod, 'DET', {}))
        ENH.update(getattr(mod, 'ENH', {}))


_load_rules()
