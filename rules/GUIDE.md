# 分隊規則手動標記說明（給 Sonnet）

2026-11-16 主 bot 寫。目的：把一個陣營的**軍隊規則、分隊規則、分隊戰略、強化**的 Wahapedia 第十一版原文，翻成計算程式看得懂的「標記」，寫成 `rules/陣營代號.py`。計算程式只算**期望傷害**，所以只標記會改變攻擊或受傷結果的效果。

## 你要做的事（照順序，越少步驟越好）

1. 原文已經附在這份說明後面，不用再跑 det_prep.py，也不用讀其他檔案。
2. 一次寫好整個 `rules/陣營代號.py`（用 Write，一次寫完）。
3. 跑 `python3 tools/det_check.py 陣營代號`。有 ERROR 就改，直到最後一行是 `OK`。WARN 要看：是故意的就不用改。
4. 最後的回覆只寫 3～6 行：做了幾個分隊、幾條規則／戰略、幾個強化；哪些你不確定（用 ⚠️ 標出）。不要貼程式碼。

**原文沒寫的不要自己補，不確定的寧可不算（on=False）並在 why 說明。**

## 檔案格式

```python
from manual import T
from army import R, MV          # MV = ['MONSTER', 'VEHICLE']

ARMY = {   # 軍隊規則：key = 軍隊規則 id（原文「軍隊規則」段的 id）
    '000008391': dict(name='Martial Ka’tah', rules=[R(...), R(...)]),
}
DET = {    # 分隊：key = 分隊 id（字串）。每個分隊都要有一個 key，沒有能算的就寫 [] 並加註解
    '000000760': [R(...), R(...)],
    '000000927': [],   # 只有移動／艙門／CP 相關，不影響傷害
}
ENH = {    # 強化：key = 強化英文名（照原文，不含括號）
    'Drill Commander': [T(...)],
}
```

### R(名稱, 種類, [標記...], cp='', on=False, ...)：一條規則或戰略

- 種類：`'規則'`（分隊規則）、`'戰略'`、`'軍隊規則'`
- `cp='1'`：戰略一定要寫 CP
- `on`：**預設算不算**。一直有效、沒有條件的分隊規則 → `on=True`。戰略 → 一律 `on=False`（使用者自己勾）。要看位置、要在目標點上、要先選目標、要低於起始人數這種條件 → `on=False`，條件寫在標記的 `why`。
- 限定哪些單位（不寫就是全軍）：
  - `need=['REGIMENT']` 單位要有這些關鍵字（全部都要）；`need_not=MV` 有這些就不算
  - `names=['Vigilator']` 資料卡名含這幾個字才算；`names_not=[...]`
  - `model_kw=['CHARACTER']` 併隊時只給有這關鍵字的那組模型；`model_not=['CHARACTER']`
  - 戰略的 TARGET 寫「One INFANTRY unit」→ `need=['INFANTRY']`
- `note='…'`：給使用者看的補充說明

### T(名稱, side, [(效果, 數值)...], scope='all', why='', ...)：一個效果

- side：`'att'` 這個單位攻擊時；`'def'` 這個單位被攻擊時
- scope：`'all'`、`'ranged'`（射擊）、`'melee'`（近戰）
- `why='…'`：條件或近似說明（中文，短）
- `tkw=['MONSTER','VEHICLE']` 只打這些關鍵字的目標；`tkw_not=MV` 目標不是這些（只用在 att）
- `wkw='TORRENT'` 只限有這個關鍵字的武器；`weapon='power fist'` 只限這把武器（小寫、名字的一部分）
- `cond`：程式能判斷的條件，只有這幾種：`'charge'`（衝鋒的那次近戰）、`'half'`（半射程內）、`'still'`（沒移動）、`'s_gt_t'`（攻擊的 S 大於被打者的 T，def 用）、`'t_gt_t'`（目標 T 比自己高）
- `pick='組名'`：同一條規則裡「每次選一個」的選項，放同一個 pick 組，程式對每個目標挑最好的（例：Ka'tah 三招、命令 Orders）
- `once=True`：每場一次的
- `unitwide=False`：強化只給帶它的那個模型（例：「the bearer's melee weapons」）；寫 bearer's unit 就是整隊，不用加

### 效果對照（原文 → 標記）

攻擊方（side='att'）：
| 原文 | 標記 |
|---|---|
| add 1 to the Hit roll | `('hit', 1)` |
| add 1 to the Wound roll | `('wound', 1)` |
| improve the Armour Penetration by 1 | `('ap', 1)` |
| add 1 to the Damage | `('dmg', 1)` |
| add 1 to the Attacks | `('attacks', 1)` |
| add 1 to the Strength | `('strength', 1)` |
| improve the Ballistic/Weapon Skill by 1（改數值，不是命中修正） | `('skill', 1)` |
| re-roll a Hit roll of 1 | `('rr_hit', '1')` |
| re-roll the Hit roll（全部重骰） | `('rr_hit', 'all')` |
| re-roll a Wound roll of 1／re-roll the Wound roll | `('rr_wound', '1')`／`('rr_wound', 'all')` |
| re-roll one Hit roll and one Wound roll（每次只重骰一顆） | `('rr1', 2)`（只有一顆命中或一顆造傷就 `('rr1', 1)`） |
| Critical Hit on 5+ | `('crit_hit', 5)` |
| Critical Wound on 5+（不限目標） | `('crit_wound', 5)` |
| 武器得到 [LETHAL HITS]、[SUSTAINED HITS 1]、[DEVASTATING WOUNDS]、[IGNORES COVER]、[LANCE]、[ANTI-INFANTRY 4+]、[TWIN-LINKED]、[CLEAVE 1] | `('kw', 'LETHAL HITS')`、`('kw', 'SUSTAINED HITS 1')`、`('kw', 'ANTI-INFANTRY 4+')`…（ANTI 只限某目標時，關鍵字寫在 ANTI 裡就好） |
| 可以無視命中／造傷／BS 的修正 | `('ign', 1)` |
| 另外造成 D3 致命傷（每次這單位攻擊一輪） | `('mw', 2)`（填平均值：D3=2、D6=3.5；有擲骰門檻要乘機率，例：每個模型擲 D6、4+ 造成 1 致命傷 → 寫平均總數並在 why 說明） |

被攻擊方（side='def'）：
| 原文 | 標記 |
|---|---|
| subtract 1 from the Hit roll | `('hit', -1)` |
| subtract 1 from the Wound roll | `('wound', -1)` |
| worsen the Armour Penetration by 1 | `('ap', -1)` |
| subtract 1 from the Damage | `('dmg', -1)` |
| halve the Damage | `('half', 1)` |
| 4+ invulnerable save | `('inv', 4)` |
| Feel No Pain 5+ | `('fnp', 5)` |
| Benefit of Cover | `('cover', 1)` |
| Stealth（第十一版 Stealth 等於掩體：攻擊方 BS 變差 1）| `('cover', 1)`；同時有 Benefit of Cover 和 Stealth 也只寫一個 `('cover', 1)`（不重複算）|
| improve the Save by 1 | `('sv', 1)`；寫「不能好過 3+」的用 `('sv3', 1)` |

### 不要標記（直接跳過，不寫成 R）

移動、前進、衝鋒距離、撤退、Deep Strike／Reserves、OC、目標點、Battle-shock、Leadership、CP 增減、重骰衝鋒、擋射線、艙門（Boarding Actions）、讓對方減移動、復活模型、回血、Fight first／fight on death（打的順序程式不算）、Overwatch、只影響戰略花費的。
這些分隊如果全部都不影響傷害，就寫 `'id': []  # 原因`。

### 判斷原則

- 效果有兩段（例：「+1 命中；如果在目標點上，再 +1 造傷」）→ 分成兩個 R：無條件的 on=True，有條件的 on=False。
- 「選一個敵人／被標記的那一隊」才有效 → on=False，why 寫「只打被選的那一隊」。
- 戰略同時有攻擊和防守效果 → 同一個 R 放兩個 T。
- 規則只給特定單位種類（REGIMENT、SQUADRON、某資料卡名）→ 用 need／names 限定。關鍵字要用資料卡上真的有的大寫英文：原文最前面有「這個陣營資料卡上的所有關鍵字」清單，從那裡挑（例：原文寫 Tempestus，關鍵字其實是 MILITARUM TEMPESTUS）。need 是「全部都要有」；原文寫「A 或 B」的單位，就只用其中共同的關鍵字，或乾脆不限，並在 why 說明。
- Favoured ka'tah 這類「用了某招才有」→ on=False，why 寫清楚。
- 數字要照原文：寫 +1 就是 1，不要自己估更大的值。

## 範例（禁軍，已經上線，照這個風格）

```python
'Shadowkeepers': [
    R('Wardens of the Dark Cells', '規則', [T('Wardens of the Dark Cells', 'def', [('wound', -1)], scope='melee', cond='s_gt_t', why='要在目標點範圍內')], need_not=MV),
    R('Grim Responsibility', '戰略', [T('Grim Responsibility', 'att', [('kw', 'LETHAL HITS: CHARACTER/MONSTER')], scope='melee')], cp='1', need=['INFANTRY']),
],
'Guardians of the Throne': [
    R('Martial Mastery', '規則', [T('Sustained Hits 1', 'att', [('kw', 'SUSTAINED HITS 1')], scope='melee', pick='mastery'),
                                T('Lethal Hits', 'att', [('kw', 'LETHAL HITS')], scope='melee', pick='mastery')], on=True,
      note='每次打架二選一，程式對每個目標自動挑好的'),
    R('In Auramite Clad', '戰略', [T('In Auramite Clad', 'def', [('ap', -1)])], cp='1', names_not=['Custodian Wardens']),
    R('Prime Target', '戰略', [T('Prime Target', 'att', [('rr1', 2)], scope='ranged', why='重骰一顆命中、一顆造傷，約等於多 2 次攻擊；重骰傷害骰沒算')], cp='1'),
],
```
（上面禁軍的 key 是分隊名字，你的檔案 key 一律用分隊 id。）

強化範例：
```python
ENH = {
    'Memento Moritoi': [T('Memento Moritoi', 'att', [('attacks', 1), ('strength', 1), ('dmg', 1)], scope='melee', on=True, unitwide=False)],
    'Augury Uplink': [T('Augury Uplink', 'def', [('fnp', 5)], on=True)],
}
```
強化寫在軍表上就代表有帶，所以強化的 T 一律 `on=True`；有條件的才在 why 說明（並改 on=False）。
