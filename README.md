# 軍表對戰計算（Warhammer 40,000 第十一版）

貼上兩張官方 App 匯出的軍表，算出雙方每個單位打一輪（射擊一次或近戰一次）平均能殺掉對方每個單位幾 %，以及「該先打誰」的排行。不接 AI，全部是固定規則的期望值計算。

## 會算什麼

- 武器數值和武器關鍵字、無敵保護、Feel No Pain、Stealth、掩體、半射程、衝鋒、沒移動。
- 一部分單位能力：`tags.py` 照固定句型讀資料卡文字，讀得懂的會列在每個單位下面讓你勾；`manual.py` 是手動補的。
- App 設成中文時匯出的軍表（中文單位名對照自官方點數網站的中英兩版）。

## 不會算什麼

- 分隊規則、戰術卡、強化、大部分光環和指定目標的能力。
- 射程、視線、地形、能不能打得到。近戰假設打得到。
- 中文武器名沒有完整的官方對照：`zh_glossary.py` 是照意思對的，沒對到的會在網頁註記列出來。

規則文字裡沒查到明文、照慣例假設的：造傷表 2+/3+/4+/5+/6+、命中和造傷修正最多 ±1、合併單位用護衛的 T。

## 怎麼用

**直接當靜態網站**：整個資料夾放到任何靜態主機（例如 GitHub Pages）就能用。`browser.js` 會用 [Pyodide](https://pyodide.org) 在瀏覽器裡跑 `engine.py`，軍表不會傳到任何伺服器。

**自己架**：

```
python3 app.py          # 預設只開 127.0.0.1:8090
```

環境變數 `MATCHUP_BIND`、`MATCHUP_PORT`、`MATCHUP_ALLOW`（允許的來源位址，逗號分隔）。

## 更新資料

```
./update_data.sh        # 重抓 Wahapedia 匯出檔（新點數、新 codex）
python3 update_zh.py    # 重做中文單位名對照
```

## 資料來源

- 資料卡：[Wahapedia 資料匯出檔](https://wahapedia.ru/wh40k11ed/the-rules/data-export/)（Powered by Wahapedia）。
- 中文單位名：官方點數網站 mfm.warhammer-community.com 的英文版和中文版。

非官方工具，與 Games Workshop 無關。Warhammer 40,000 及相關名稱是 Games Workshop 的商標。
