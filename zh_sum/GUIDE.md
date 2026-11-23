# 規則中文摘要：寫作說明

你要替一個戰錘 40K（第十一版）陣營的每一條規則寫**一行繁體中文摘要**，放在網站的「階段小抄」上，讓玩家在桌邊一眼看懂這條規則做什麼。

## 輸出

用 Write 寫成一個 JSON 檔（路徑在最下面），格式：`{"編號": "摘要", ...}`。編號照下面清單抄，**每一條都要有**，不要多也不要少。
寫完跑檢查指令（最下面）。有 ERROR 就修好再跑，直到最後一行印 OK。然後回一句話：寫了幾條、有沒有你沒把握的（列編號＋原因）。

## 怎麼寫

- **用自己的話**講效果，不要逐句翻譯原文。這是摘要，不是翻譯。不要加原文沒有的東西。
- 長度：一般 20～45 個字；複雜的規則最多 65 個字（檢查器會擋太長的）。
- 先講**對誰**（目標或條件），再講**效果**。例：「一個 TERMINATOR 單位：被攻擊時傷害 -1」「角色帶隊的單位造傷骰 +1」。
- 時機（哪個階段、誰的回合）網頁會另外顯示，摘要裡**不用重複**；但有特別的觸發點要寫，例如「衝鋒到位後」「被選為攻擊目標時」「單位被消滅時」。
- 「每場一次」「每回合一次」「第一大回合不能用」這類限制要寫。
- 有好幾個選項的（例：選一種姿態），寫「三選一：A（效果）、B（效果）、C（效果）」，每個效果盡量短。
- 純粹是編制、選將、關鍵字規則（例：可以帶某單位、某單位得到 BATTLELINE），也照樣寫一句。
- 原文只有一句「下面是特殊移動方式」之類沒有實際效果的，寫「說明用，沒有效果」。

## 用詞（照這張表，不要自創）

| 原文 | 中文 |
| --- | --- |
| hit roll／wound roll／damage roll | 命中骰／造傷骰／傷害骰 |
| save／invulnerable save | 豁免／特殊豁免（寫成 4++ 也可以） |
| re-roll | 重骰 |
| Critical Hit／Critical Wound | 命中暴擊（6）／造傷暴擊 |
| mortal wounds | 致命傷 |
| Feel No Pain 5+ | 5+ 不覺疼痛（也可寫 FNP 5+） |
| Armour Penetration (AP)／Strength (S)／Attacks (A)／Damage (D) | AP／S／A／D（直接用英文字母） |
| Move (M)／Toughness (T)／Leadership (Ld)／Objective Control (OC) | M／T／Ld／OC |
| battle-shock (test) | 戰鬥震撼（檢定） |
| Command phase／Movement／Shooting／Charge／Fight phase | 指揮／移動／射擊／衝鋒／格鬥階段 |
| battle round | 大回合 |
| turn | 回合 |
| Advance／Fall Back／Normal move | 前進／撤退／一般移動 |
| charge／declare a charge／charge roll | 衝鋒／宣告衝鋒／衝鋒骰 |
| pile in／consolidate | 堆進／鞏固 |
| Engagement Range／engaged | 接戰範圍／交戰中 |
| Fights First | 先攻 |
| objective marker | 目標點 |
| Deep Strike／strategic reserves／Reserves | 深入打擊／戰略預備隊／預備隊 |
| ingress move | 進場移動 |
| Stealth／Lone Operative／Infiltrators／Scouts | 隱匿／獨行特工／滲透／偵察 |
| benefit of cover | 掩體 |
| visible／line of sight | 看得到／視線 |
| aura | 光環 |
| Warlord | 軍閥 |
| Character／Leader／Bodyguard／attached unit | 角色／領袖／護衛／聯合單位 |
| Psychic | 靈能 |
| Transport／embark／disembark | 運輸載具／上車／下車 |
| CP（command points） | CP |
| Stratagem | 戰術卡 |
| Enhancement | 強化 |
| Detachment | 分隊 |
| destroyed | 被消滅 |
| below Starting Strength／Below Half-strength | 不滿編／不到一半 |
| hazard roll | 危險骰 |

- 單位關鍵字（INFANTRY、VEHICLE、MONSTER、CHARACTER、BATTLELINE、陣營關鍵字等）**保留英文大寫**。
- 武器能力保留英文加中括號：[LETHAL HITS]、[SUSTAINED HITS 1]、[DEVASTATING WOUNDS]、[PRECISION]、[ASSAULT]、[HEAVY]、[IGNORES COVER] 等。
- 單位名、武器名、規則名、能力名：保留英文原名（網頁會另外顯示中文名）。
- 距離寫 6"、12"；骰子寫 D6、2D6、D3。

## 範例

- `Assemblage of Might`（原文：指揮階段選一個敵方單位當 dreadful foe，到你下個指揮階段開始；角色模型打它造傷骰 +1）
  → `選一個敵方單位當「可怕之敵」到下個指揮階段：我方 CHARACTER 打它造傷骰 +1`
- `Aquila Commander`（大回合開始時，有這能力的模型是軍閥就 +1CP）
  → `這個模型是軍閥時，每大回合開始 +1CP`
- 戰術卡 `Vigil Unending`（目標一個 TERMINATOR 單位；效果：被攻擊時傷害 -1）
  → `一個 TERMINATOR 單位：被攻擊時每次傷害 -1`

---
