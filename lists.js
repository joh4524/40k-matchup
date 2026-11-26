// 「我的軍表」和分頁合併（2026-11-24 使用者：「看能不能暫存表在裡面 很多功能沒必要分開」「12都做」）
// 每個工具頁（matchup／listcheck／scout／dice／leaderboards）都載入這個檔：
// 1. 單獨打開工具頁時，轉到首頁對應的分頁（index.html#名稱）
// 2. 在首頁分頁（iframe）裡時：藏掉頁面自己的標題列，計算程式共用首頁那一份（只載入一次）
// 3. MyLists.attach(textarea, 'a'|'b')：輸入框上面加一排「我的軍表」，存在這個瀏覽器的 localStorage；
//    同一個代號的輸入框在各分頁之間同步（A＝我方，三個工具共用；B＝對戰的對方）
(() => {
  const page = (document.currentScript && document.currentScript.dataset.page) || '';
  // 按鈕的按壓回饋、計算中的進度條（2026-11-27 使用者「行 你試試」：照 Emil Kowalski 的動畫規則；只動 transform／opacity，減少動態時不動）
  const fx = document.createElement('style');
  fx.textContent = 'button{transition:transform 160ms cubic-bezier(0.23,1,0.32,1)}button:not(:disabled):active{transform:scale(0.97)}'
    + 'button:disabled{opacity:.6;position:relative;overflow:hidden}'
    + 'button:disabled::after{content:"";position:absolute;left:0;right:0;bottom:0;height:3px;background:currentColor;animation:busy 900ms linear infinite}'
    + '@keyframes busy{from{transform:translateX(-100%)}to{transform:translateX(100%)}}@keyframes busyfade{from{opacity:.3}to{opacity:1}}'
    + '@media (prefers-reduced-motion:reduce){button:not(:disabled):active{transform:none;opacity:.8}button:disabled::after{animation:busyfade 1.2s ease-in-out infinite alternate}}';
  document.head.appendChild(fx);
  // iPhone Safari 要有 touchstart 才會套 :active
  document.addEventListener('touchstart', () => {}, {passive: true});
  let embed = false;
  try { embed = window.parent !== window && !!window.parent.document; } catch (e) { embed = false; }
  if (!embed && page && !/[?&]solo=1/.test(location.search)) { location.replace('./#' + page); return; }
  if (embed) {
    document.documentElement.classList.add('embed');
    const st = document.createElement('style');
    st.textContent = 'html.embed main>h1{display:none}html.embed main{padding-top:10px}';
    document.head.appendChild(st);
    // 計算共用首頁的 Pyodide（公開版）；HP 版兩邊都沒有 localCalc，照舊用 /api/calc
    try {
      if (window.parent.localCalc) {
        window.localCalc = async (req, status) => JSON.parse(JSON.stringify(await window.parent.localCalc(req, status)));
      }
    } catch (e) {}
  }

  const KEY = 'mu_lists', CUR = {a: 'mu_cur_a', b: 'mu_cur_b'};
  const get = (k, d) => { try { const v = localStorage.getItem(k); return v === null ? d : v; } catch (e) { return d; } };
  const put = (k, v) => { try { localStorage.setItem(k, v); return true; } catch (e) { return false; } };
  const load = () => { try { return JSON.parse(get(KEY, '[]')) || []; } catch (e) { return []; } };
  const store = (arr) => put(KEY, JSON.stringify(arr));
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;'}[c]));

  // 第一次用：把各工具舊的「最後一張」搬成共用的
  if (get(CUR.a, null) === null) { const old = get('mu_a', '') || get('lc_a', '') || get('sc_a', ''); if (old) put(CUR.a, old); }
  if (get(CUR.b, null) === null) { const old = get('mu_b', ''); if (old) put(CUR.b, old); }

  // 預設名稱：App 匯出的第一行通常是「表名 (2000 points)」
  function guessName(text) {
    const line = (text.split('\n').map((s) => s.trim()).find((s) => s) || '').replace(/[（(]\s*\d+\s*(points|pts|点|點|分)\s*[)）]/i, '').trim();
    return line.slice(0, 40) || '未命名軍表';
  }

  const css = '.ml{display:flex;flex-wrap:wrap;gap:4px 6px;align-items:center;margin:0 0 4px;font-size:13px}' +
    '.ml select{flex:1 1 120px;min-width:0;font:inherit;padding:4px;border-radius:6px;border:1px solid var(--line);background:var(--bg);color:var(--ink)}' +
    '.ml input{flex:1 1 80px;min-width:0;font:inherit;padding:4px 6px;border-radius:6px;border:1px solid var(--line);background:var(--bg);color:var(--ink)}' +
    '.ml button{font:inherit;font-size:13px;font-weight:400;padding:4px 10px;border-radius:6px;border:1px solid var(--line);background:var(--bg);color:var(--ink)}' +
    '.ml .mlm{color:var(--mute);font-size:12px;flex-basis:100%}';
  let cssDone = false;
  const boxes = [];

  function attach(ta, side) {
    if (!ta) return;
    if (!cssDone) { const s = document.createElement('style'); s.textContent = css; document.head.appendChild(s); cssDone = true; }
    const row = document.createElement('div');
    row.className = 'ml';
    row.innerHTML = '<select aria-label="我的軍表"></select><input placeholder="名稱（存的時候用）" aria-label="軍表名稱"><button type="button" data-a="save">存</button><button type="button" data-a="del">刪</button><span class="mlm"></span>';
    ta.parentNode.insertBefore(row, ta);
    const sel = row.querySelector('select'), name = row.querySelector('input'), msg = row.querySelector('.mlm');
    const box = {ta, side, sel, name, msg, synced: ta.value, delArm: 0};
    boxes.push(box);
    const say = (t) => { msg.textContent = t; clearTimeout(box.t); box.t = setTimeout(() => { msg.textContent = ''; }, 4000); };

    sel.onchange = () => {
      const it = load().find((x) => x.id === sel.value);
      if (!it) return;
      ta.value = it.text; name.value = it.name;
      sync(box);
      ta.dispatchEvent(new Event('input', {bubbles: true}));
      say('已載入「' + it.name + '」');
    };
    row.querySelector('[data-a=save]').onclick = () => {
      const text = ta.value;
      if (!text.trim()) { say('輸入框是空的，先貼軍表再存。'); return; }
      const nm = name.value.trim() || guessName(text), arr = load();
      let it = arr.find((x) => x.name === nm);
      if (it) { it.text = text; it.updated = Date.now(); } else { it = {id: 'L' + Date.now().toString(36), name: nm, text, updated: Date.now()}; arr.push(it); }
      if (!store(arr)) { say('存不進去（瀏覽器不允許儲存，例如無痕模式）。'); return; }
      name.value = nm; refresh(); sel.value = it.id;
      say('已存「' + nm + '」（存在這個瀏覽器）');
    };
    row.querySelector('[data-a=del]').onclick = () => {
      const arr = load(), i = arr.findIndex((x) => x.id === sel.value);
      if (i < 0) { say('先在左邊選一張已存的軍表。'); return; }
      if (Date.now() - box.delArm > 4000) { box.delArm = Date.now(); say('再按一次「刪」確定刪除「' + arr[i].name + '」'); return; }
      const nm = arr[i].name; arr.splice(i, 1); store(arr); box.delArm = 0;
      refresh(); say('已刪除「' + nm + '」');
    };
    ta.addEventListener('input', () => sync(box));
    const cur = get(CUR[side], null);
    if (cur !== null && cur !== ta.value) { ta.value = cur; box.synced = cur; }
    fill(box);
  }

  function fill(box) {
    const arr = load().sort((x, y) => x.name.localeCompare(y.name, 'zh-Hant'));
    const match = arr.find((x) => x.text === box.ta.value);
    box.sel.innerHTML = '<option value="">我的軍表（' + arr.length + ' 張）…</option>' + arr.map((x) => '<option value="' + esc(x.id) + '">' + esc(x.name) + '</option>').join('');
    box.sel.value = match ? match.id : '';
  }
  function refresh() { boxes.forEach(fill); }

  // 輸入框內容寫進共用的 key；其他分頁靠 storage 事件更新
  function sync(box) {
    if (box.ta.value === box.synced) return;
    box.synced = box.ta.value;
    put(CUR[box.side], box.ta.value);
    const match = load().find((x) => x.text === box.ta.value);
    box.sel.value = match ? match.id : '';
  }
  // 程式改輸入框（例如「放回上面的輸入框」、選 meta 表）不會觸發 input 事件，定時補一下
  setInterval(() => boxes.forEach(sync), 1000);
  window.addEventListener('storage', (e) => {
    if (e.key === KEY) refresh();
    boxes.forEach((box) => {
      if (e.key !== CUR[box.side] || e.newValue === null || e.newValue === box.ta.value) return;
      box.ta.value = e.newValue; box.synced = e.newValue;
      const match = load().find((x) => x.text === e.newValue);
      box.sel.value = match ? match.id : '';
    });
  });

  window.MyLists = {attach};
})();
