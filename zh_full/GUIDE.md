# 規則完整翻譯：寫作說明

你要把一個戰錘 40K（第十一版）陣營的規則**完整翻成繁體中文**，給玩家在 HP 自己架的網站上印資料卡和戰術卡用（不公開）。這是**完整翻譯，不是摘要**：每一句都要翻，不能省略、不能加料。

## 輸出

用 Write 寫成一個 JSON 檔（路徑在最下面），格式：
`{"編號": {"n": "中文名稱", "t": "中文全文", "src": "ref 或 own"}, ...}`
- 編號照下面清單抄，**每一條都要有**，不多不少。
- n：規則／戰術卡／強化／能力／武器的中文名。
- t：中文全文。武器名（W 開頭）沒有全文，**不要寫 t**。英文原文是空的也不要寫 t。
- src：有在參考中文規則裡找到這一條（或同名規則）並照它的譯法寫的，填 "ref"；參考裡沒有、自己翻的，填 "own"。
- 條目很多，可以分幾次寫（先 Write 一部分，再用 Edit 或重寫補上），但最後檔案要是完整的一個 JSON。
- 也可以把條目寫成 Python 檔放在 zh_full/work/（例：zh_full/work/AC.1_a.py），最後一個檔 json.dump 到輸出路徑，再用 `python3 zh_full/work/檔名.py` 執行（只允許執行這個資料夾裡的檔）。
寫完跑檢查指令（最下面）。有 ERROR 就修好再跑，直到最後一行印 OK。然後回兩三句話：幾條 ref、幾條 own、有沒有你沒把握的（列編號＋原因）。

## 參考中文規則（很重要）

條目清單前面通常附了「參考段落」（R 開頭編號），是程式從中文規則書裡用英文名找到的段落；每個條目標了「參考 R…」。**先看參考段落**，裡面有就照它；段落裡找不到、或標「參考：沒對到」，才去參考檔 Grep。段落是程式猜的，可能對錯條目，內容對不上英文就不要用。

最下面會列這個陣營的社群中文規則檔（簡體，從中文規則書轉的文字，排版有點亂）。用法：
- 用 Grep 在參考檔裡找英文名（參考檔大多在中文名後面附大寫英文名，例如「雷霆出击 CALISTUS」）或關鍵中文詞，再 Read 那附近幾十行。**不要整個檔案一次讀完**（太大）。
- 找到同一條規則：名稱和用詞照參考的講法，**轉成繁體**（例：备战状态→備戰狀態、近战阶段→格鬥階段要照下面用詞表）。但**數字、條件、效果以英文原文為準**：參考版本可能比較舊，跟英文不一樣時照英文翻，不要照抄參考。
- 參考裡找不到：自己翻，src 填 "own"。
- 沒有列參考檔的陣營全部自己翻（src 都是 "own"）。
- 戰錘專有名詞（單位、人物、武器、軍團）先查 ~/.claude/skills/warhammer-translate/references/glossary.md（可以 Grep），表裡有就照表。

## 怎麼翻

- 數字、骰值（3+、D6、D3）、距離（6"，可以寫 6 寸或 6"）、次數一個都不能改，**英文裡的每個數字中文裡都要出現**（檢查器會比對）。
- 原文的換行（清單裡用「 / 」表示）在中文裡用 \n 換行；「•」項目符號照留。
- 戰術卡的 WHEN: / TARGET: / EFFECT: / RESTRICTIONS: 翻成「時機：」「目標：」「效果：」「限制：」，每段開頭一行。
- 大寫的單位關鍵字（ADEPTUS CUSTODES、INFANTRY、CHARACTER、MONSTER／VEHICLE）翻成中文（帝皇禁軍、步兵、角色、巨獸／載具），照參考或譯名表；沒把握就中文後面括號附英文，例：「靈能者（PSYKER）」。
- 句子要像中文規則書，清楚、不口語化，但不要文言。
- 看不懂或原文有歧義：照字面翻，並在最後回報時列出編號。
- 武器名（W）：照譯名表或參考裡的武器名；沒有就自己翻（src own）。「– strike」「– sweep」這類型態後綴翻成「－重擊」「－橫掃」之類並保留破折號。

## 武器關鍵字（網頁會自動翻，你翻規則文字時遇到也照這樣寫）

突擊（Assault）、速射 X（Rapid Fire X）、重型（Heavy）、手槍（Pistol）、致命一擊（Lethal Hits）、連擊 X（Sustained Hits X）、毀滅傷害（Devastating Wounds）、雙聯（Twin-linked）、洪流（Torrent）、爆炸（Blast）、熱熔 X（Melta X）、危險（Hazardous）、精準（Precision）、無視掩體（Ignores Cover）、間接射擊（Indirect Fire）、騎槍（Lance）、額外攻擊（Extra Attacks）、單發（One Shot）、反 X N+（Anti-X N+，例：反載具 4+）、靈能（Psychic）、劈砍 X（Cleave X）

## 用詞（照這張表；表跟參考檔講法不同時照這張表）

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

| ready／readied（禁軍 Ka'tah） | 備戰狀態 |
| ka'tah | 武技（Ka'tah） |

