#!/bin/bash
# 更新 Wahapedia 第十一版資料匯出檔（有新點數／新 codex 時跑），跑完重啟服務：systemctl --user restart matchup
cd "$(dirname "$0")/data" || exit 1
for f in Last_update Factions Datasheets Datasheets_models Datasheets_wargear Datasheets_abilities Datasheets_keywords Datasheets_unit_composition Datasheets_models_cost Datasheets_options Abilities Detachments Detachment_abilities Stratagems Enhancements; do
  curl -sf -m 60 -A "Mozilla/5.0" -o "$f.csv.new" "https://wahapedia.ru/wh40k11ed/$f.csv" && mv "$f.csv.new" "$f.csv" || echo "失敗：$f"
  sleep 1
done
cat Last_update.csv
