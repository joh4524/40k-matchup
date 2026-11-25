#!/bin/bash
# 每週自動更新 Wahapedia 規則／點數資料（2026-11-25 使用者：「1」＝規則資料每週自動更新＋點數變動提醒）。
# 流程：網站 Last_update 沒變就結束 → 備份舊資料 → update_data.sh → 點數差異 → 引擎冒煙測試（5 張範例表 × 對戰／偵察／健檢／列印）
#       → 過了：重算健檢基準和單位排行、bump、重啟 HP 服務、commit＋push、確認公開版版本號 → Telegram 傳點數變動摘要
#       → 沒過：還原舊資料，Telegram 報錯，不 push。
# 不叫任何 AI（不花 Claude 額度）。手動跑：~/matchup/tools/data_weekly.sh [--force]
set -u
M="$HOME/matchup"; cd "$M" || exit 1
LOG="$HOME/matchup-data-logs"; mkdir -p "$LOG"; T=$(date +%F); R="$LOG/$T.txt"; : > "$R"
say() { echo "$*" >> "$R"; }
tg() { "$HOME/bin/tg-send.sh" "$R" >/dev/null 2>&1; }
remote=$(curl -sf -m 30 -A 'Mozilla/5.0' https://wahapedia.ru/wh40k11ed/Last_update.csv | tail -1 | cut -d'|' -f1)
local_=$(tail -1 data/Last_update.csv | cut -d'|' -f1)
if [ -z "$remote" ]; then say "40K 資料週更：連不到 Wahapedia，下週再試"; tg; exit 1; fi
if [ "$remote" = "$local_" ] && [ "${1:-}" != "--force" ]; then echo "$(date '+%F %T') 沒有新資料（$local_）" >> "$LOG/runs.log"; exit 0; fi
PREV="$LOG/data-$T-prev"; rm -rf "$PREV"; cp -a data "$PREV"
./update_data.sh > "$LOG/$T-download.txt" 2>&1
if grep -q '失敗' "$LOG/$T-download.txt"; then cp -a "$PREV"/. data/; say "40K 資料週更：下載有檔案失敗，已還原舊資料"; grep '失敗' "$LOG/$T-download.txt" >> "$R"; tg; exit 1; fi
DIFF=$(python3 tools/points_diff.py "$PREV" data 2>&1)
SMOKE=$(python3 - <<'PY' 2>&1
import engine, traceback
db = engine.DB()
txt = [open(f'sample_{c}.txt', encoding='utf-8').read() for c in 'abcde']
bad = 0
for i, a in enumerate(txt):
    b = txt[(i + 1) % 5]
    for req in ({'a': a, 'b': b, 'opt': {}}, {'scout': True, 'a': a}, {'listcheck': True, 'a': a}, {'print': True, 'a': a, 'full': True}):
        try:
            r = engine.api(req, db)
            if req.get('scout') and not r['units']:
                raise ValueError('讀不到單位')
        except Exception as e:
            bad += 1; print('FAIL', 'abcde'[i], list(req)[0], type(e).__name__, str(e)[:120])
print('OK' if not bad else f'FAIL {bad}')
PY
)
if [ "$(echo "$SMOKE" | tail -1)" != "OK" ]; then
  cp -a "$PREV"/. data/
  say "40K 資料週更：新資料（$remote）讓計算程式出錯，已還原舊資料、沒有上線，要主機器人修："; echo "$SMOKE" | head -8 >> "$R"; tg; exit 1
fi
python3 tools/lc_bench.py > "$LOG/$T-bench.txt" 2>&1 || say "⚠️ 健檢基準重算失敗（看 $LOG/$T-bench.txt），沿用舊的"
python3 tools/lb_build.py > "$LOG/$T-lb.txt" 2>&1 || say "⚠️ 單位排行重算失敗（看 $LOG/$T-lb.txt），沿用舊的"
./bump.sh > /dev/null
systemctl --user restart matchup
V=$(grep -o 'browser.js?v=[0-9]*' index.html)
git add data/*.csv data/listcheck_bench.json data/leaderboard.json index.html matchup.html listcheck.html scout.html dice.html leaderboards.html print.html rules/index.json 2>/dev/null
git commit -q -m "Weekly data update: Wahapedia $remote

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" && git push -q 2>>"$LOG/$T-push.txt"
pv=""
for i in $(seq 1 18); do pv=$(curl -s "https://joh4524.github.io/40k-matchup/?t=$RANDOM" | grep -o 'browser.js?v=[0-9]*'); [ "$pv" = "$V" ] && break; sleep 10; done
{ echo "40K 資料週更：Wahapedia $local_ → $remote"
  [ "$pv" = "$V" ] && echo "已上線（HP＋公開版 $V），5 張範例表測試通過" || echo "⚠️ 公開版版本號還沒對上（$pv，應為 $V），HP 版已更新"
  echo; echo "點數／規則變動："; echo "$DIFF" | head -60; } > "$R.tmp" && cat "$R" >> "$R.tmp" && mv "$R.tmp" "$R"
tg
echo "$(date '+%F %T') 更新 $local_ → $remote" >> "$LOG/runs.log"
