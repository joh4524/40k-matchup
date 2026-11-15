"""手動補的能力（自動讀不出來的）。2026-11-15：使用者那兩張表（星界軍、混沌星際戰士）和禁軍。
MANUAL：資料卡名 → 這張卡自己多出來的標記。
GRANTS：某個單位在軍表裡時，可以給別的單位的加成（光環、選一個目標之類），預設不算，要自己勾。
"""
import tags as tagger


def T(name, side, effs, scope='all', on=False, why='', **kw):
    t = dict(name=name, side=side, scope=scope, effs=effs, tkw=[], tkw_not=[], weapon=None, cond=None, leading=False, on=on, situ=not on, unitwide=True)
    t.update(kw)
    t['label'] = tagger.label(dict(t, situ=False)) + (f'（{why}）' if why else '')
    return t


MANUAL = {
    'Defiler': [T('Daemonforge', 'att', [('rr_wound', '1')], why='這階段有簽 Dark Pact 才有')],
    'Trajann Valoris': [T('Captain-General (Aura)', 'att', [('rr_hit', '1'), ('rr_wound', '1')], on=True, why='他自己這隊'),
                        T('Moment Shackle', 'att', [('attacks', 3)], scope='melee', weapon='watcher’s axe', unitwide=False, why='每場一次')],
    # 2026-11-15 禁軍補充（使用者「你從禁軍開始」）
    'Caladius Annihilator Grav-Tank': [T('Advanced Firepower', 'att', [('rr1', 2)], scope='ranged', tkw=['MONSTER', 'VEHICLE'], on=True,
                                         why='重骰一顆命中、一顆造傷，約等於多 2 次攻擊；重骰傷害骰沒算')],
    'Blade Champion': [T('Sword of the Throne', 'att', [('wound', 1)], unitwide=False, why='只打被選為 mark 的那一隊')],
}

GRANTS = [
    dict(src='Trajann Valoris', need=['ADEPTUS CUSTODES'], excl=['MONSTER', 'VEHICLE'],
         tag=T('Trajann 的光環 Captain-General', 'att', [('rr_hit', '1'), ('rr_wound', '1')], why='要在 Trajann 6 吋內')),
    dict(src='Tech-Priest Enginseer', need=['VEHICLE'], excl=[],
         tag=T('Enginseer 的 Omnissiah’s Blessing', 'def', [('inv', 4)], why='Enginseer 每回合只能給一台')),
    dict(src='Scout Sentinels', need=['ASTRA MILITARUM'], excl=[],
         tag=T('Scout Sentinels 的 Daring Recon', 'att', [('rr_hit', '1')], why='打被 Sentinel 指定的那個目標時')),
    dict(src='Lord Discordant on Helstalker', need=['HERETIC ASTARTES'], excl=[],
         tag=T('Lord Discordant 的 Spirit Thief', 'att', [('rr_wound', '1')], tkw=['VEHICLE'], why='打被他指定的那台載具時')),
]
