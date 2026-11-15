from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

ARMY = {
    '000008377': dict(name='Voice of Command', rules=[
        R('Voice of Command', '軍隊規則', [
            T('Fix Bayonets!', 'att', [('skill', 1)], scope='melee', pick='orders'),
            T('Take Aim!', 'att', [('skill', 1)], scope='ranged', pick='orders'),
            T('First Rank, Fire! Second Rank, Fire!', 'att', [('attacks', 1)], scope='ranged', wkw='RAPID FIRE', pick='orders'),
            T('Take Cover!', 'def', [('sv3', 1)], pick='orders', why='Save 不能好過 3+'),
        ], on=False, note='軍官在 6" 內下令，每次一個命令；Move!/Duty and Honour! 不影響傷害'),
    ]),
}

DET = {
    # Combined Arms
    '000000760': [
        R('Born Soldiers (Regiment)', '規則', [T('Born Soldiers', 'att', [('kw', 'LETHAL HITS')], scope='ranged', tkw_not=MV)], on=True, need=['REGIMENT']),
        R('Born Soldiers (Squadron)', '規則', [T('Born Soldiers', 'att', [('kw', 'LETHAL HITS')], scope='ranged', tkw=MV)], on=True, need=['SQUADRON']),
        R('Stalwart Protector', '戰略', [T('Stalwart Protector', 'def', [('cover', 1)], scope='ranged', why='要有己方載具擋住視線')], cp='1', need=['INFANTRY']),
        R('Fields of Fire', '戰略', [T('Fields of Fire', 'att', [('ap', 1)], why='只打被選的那一隊；限 Regiment 與 Squadron 各一隊')], cp='1'),
    ],
    # Embarked Regiment
    '000000927': [
        R('Duck and Cover', '戰略', [T('Duck and Cover', 'def', [('hit', -1)], why='要隔著開啟的艙門')], cp='1', need_not=['OGRYN']),
    ],
    # Tempestus Boarding Regiment
    '000000928': [
        R('Purge-Sweep Protocols', '規則', [T('Purge-Sweep Protocols', 'att', [('kw', 'LETHAL HITS')], scope='ranged', why='要在艙門 1" 內、只打門另一側被選的那一隊')], need=['MILITARUM TEMPESTUS']),
        R('Brutal Training', '戰略', [T('Brutal Training', 'att', [('attacks', 1), ('strength', 1)], scope='melee')], cp='1', need=['MILITARUM TEMPESTUS']),
    ],
    # Bridgehead Strike
    '000000996': [
        R('Fire Zone Purge', '規則', [T('Fire Zone Purge', 'att', [('hit', 1)], scope='ranged', why='要本回合剛設置上場')], need=['MILITARUM TEMPESTUS']),
        R('Servo-Designators', '戰略', [T('Servo-Designators', 'att', [('kw', 'IGNORES COVER')], scope='ranged', why='只打被選的那一隊')], cp='1', need=['MILITARUM TEMPESTUS']),
        R('Firing Hot', '戰略', [T('Firing Hot', 'att', [('strength', 1), ('ap', 1)], scope='ranged', weapon='hot-shot', why='只限目標在 12" 內')], cp='2'),
    ],
    # Siege Regiment
    '000001010': [
        R('Artillery Support: Smoke Shells', '規則', [T('Smoke Shells', 'def', [('cover', 1)], scope='ranged', why='Stealth（程式當成掩體）；選到的單位才有')],
          note='每回合三選一；Creeping Barrage / Incendiary Bombardment 未計算'),
        R('Furious Fusillade', '戰略', [T('Furious Fusillade', 'att', [('attacks', 1)], scope='ranged', cond='half')], cp='1', need=['PLATOON']),
        R('Flare Burst', '戰略', [T('Flare Burst', 'att', [('rr_hit', 'all')], scope='ranged', why='只限目標在 12" 內')], cp='1', need=['CHARACTER']),
    ],
    # Mechanised Assault
    '000001011': [
        R('Armoured Fist', '規則', [T('Armoured Fist', 'att', [('wound', 1)], scope='ranged', why='要本回合從運輸載具下車')]),
        R('Clear and Secure', '戰略', [T('Clear and Secure', 'att', [('rr_hit', 'all'), ('rr_wound', 'all')], why='目標要在目標點範圍內；要本回合下車')], cp='1'),
    ],
    # Hammer of the Emperor
    '000001012': [
        R('Furious Cannonade', '戰略', [T('Furious Cannonade', 'att', [('ap', 1)], why='只限目標在 12" 內')], cp='1', need=['SQUADRON']),
        R('Final Hour', '戰略', [T('Final Hour', 'att', [('ign', 1), ('kw', 'HAZARDOUS')], scope='ranged', why='要低於半數；可無視 BS/命中修正，但武器變 HAZARDOUS')], cp='1', need=['SQUADRON']),
        R('Ablative Plating', '戰略', [T('Ablative Plating', 'def', [('dmg', -1)], scope='ranged')], cp='2', need=['VEHICLE']),
    ],
    # Recon Element
    '000001013': [
        R('Masters of Camouflage', '規則', [T('Stealth', 'def', [('cover', 1)], scope='ranged', why='Stealth（程式當成掩體）')], on=True, need_not=['TITANIC']),
        R('Crack Shots', '戰略', [T('Crack Shots', 'att', [('kw', 'PRECISION')], scope='ranged')], cp='1', need=['PLATOON']),
        R('Courageous Diversion', '戰略', [T('Courageous Diversion', 'def', [('fnp', 6), ('hit', -1)], why='-1 命中只在本單位是最近的可選目標時；資料卡需為 Infantry 或 Mounted')], cp='1'),
    ],
    # Grizzled Company
    '000001121': [
        R('Ruthless Discipline', '規則', [T('Ruthless Discipline', 'att', [('rr_hit', '1')], why='要單位正受命令影響')]),
        R('Additional Armour', '戰略', [T('Additional Armour', 'def', [('ap', -1)])], cp='1'),
        R('Veteran Sharpshooters', '戰略', [T('Veteran Sharpshooters', 'att', [('kw', 'IGNORES COVER')], scope='ranged')], cp='1'),
        R('Purging Fire', '戰略', [T('Purging Fire', 'att', [('kw', 'LETHAL HITS')], scope='ranged', why='要受命令影響且在目標點範圍內')], cp='1'),
        R('Mordian Minute', '戰略', [T('Mordian Minute', 'att', [('strength', 1)], why='要受 First Rank, Fire! 命令影響')], cp='1', need=['INFANTRY']),
    ],
    # Steel Hammer
    '000001149': [
        R('Accuracy Under Pressure', '戰略', [T('Accuracy Under Pressure', 'att', [('rr_hit', 'all')])], cp='2'),
        R('Engine of Wrath', '戰略', [T('Engine of Wrath', 'att', [('attacks', 6), ('ap', 2)], scope='melee', why='只打被選的那一隊')], cp='1', need=['TITANIC']),
    ],
    # Armoured Infantry
    '000001150': [
        R('Opening Salvo', '戰略', [T('Opening Salvo', 'att', [('wound', 1)], why='要本回合從運輸載具下車')], cp='1'),
        R('Combined Fire', '戰略', [T('Combined Fire', 'att', [('strength', 2)], why='只限 Armoured Skirmisher（Squadron 非砲兵）打被選的那一隊；Benefit of Cover 移除未算')], cp='1', need=['SQUADRON']),
        R('Supporting Ordnance', '戰略', [T('Supporting Ordnance', 'att', [('rr_hit', 'all')], tkw=MV)], cp='1', need=['SQUADRON']),
    ],
    # Abhuman Auxiliaries
    '000001161': [
        R('Thick-Skulled Obdurance', '戰略', [T('Thick-Skulled Obdurance', 'def', [('ap', -1)], why='要在目標點範圍內')], cp='1', names=['Bullgryn', 'Ogryn']),
    ],
    # Designation Force
    '000001163': [
        R('Sump-Smog Screen', '戰略', [T('Sump-Smog Screen', 'def', [('cover', 1)], scope='ranged')], cp='1', need=['INFANTRY'], note='限帶 SMOKE 的單位'),
    ],
}

ENH = {
    'Drill Commander': [T('Drill Commander', 'att', [('crit_hit', 5)], scope='ranged', cond='still', on=True)],
    'Legacy Sidearm': [T('Legacy Sidearm', 'att', [('attacks', 2)], scope='ranged', weapon='pistol', on=True, unitwide=False)],
    'Stalwart’s Honours': [T('Stalwart’s Honours', 'def', [('sv3', 1)], on=False, why='單位受命令時同時受 Take Cover!；Save 不能好過 3+')],
    'Veteran Crew': [T('Veteran Crew', 'att', [('rr_hit', '1')], scope='ranged', on=True)],
    'Indomitable Steed': [T('Indomitable Steed', 'def', [('fnp', 6)], on=True, unitwide=False)],
    'Elimination Force': [T('Elimination Force', 'att', [('wound', 1)], on=False, why='只打被選的那一隊，且攻擊 S 小於目標 T 時')],
    'Aquilan Eye': [T('Aquilan Eye', 'att', [('ap', 1)], scope='ranged', on=False, why='要選 Target Weak Spot 命令，目標在 12" 內')],
    'Spec Ops Veteran': [T('Spec Ops Veteran', 'def', [('cover', 1)], scope='ranged', on=False, why='要選 Move to the Shadows 命令（Stealth，程式當成掩體）')],
    'Smoke Grenades': [T('Smoke Grenades', 'def', [('cover', 1)], scope='ranged', on=False, why='要整隊在友方運輸載具 3" 內（掩護＋Stealth，兩個都是掩體不重複算）')],
    'Omnissian Unguents  (Aura)': [T('Omnissian Unguents', 'def', [('fnp', 5)], on=False, why='光環：Armoured Skirmisher 在持有者 3" 內')],
    'Exemplar of Duty': [T('Exemplar of Duty', 'def', [('fnp', 4)], on=True, unitwide=False)],
}
