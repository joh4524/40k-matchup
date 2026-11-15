#!/bin/bash
# 改完程式或資料、commit 之前跑：把 index.html 裡 browser.js?v= 的版本號換成現在時間，公開版的使用者就不會拿到舊快取。2026-11-15。
cd "$(dirname "$0")" && sed -i -E "s/browser\.js(\?v=[0-9]+)?\"/browser.js?v=$(date +%Y%m%d%H%M)\"/" index.html && grep -o 'browser.js?v=[0-9]*' index.html
