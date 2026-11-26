// 公開版（GitHub Pages 這類只放檔案的網站）用：沒有伺服器，計算程式（engine.py）用 Pyodide 直接在瀏覽器裡跑。
// 自己架 app.py 時這個檔不會被送出來，網頁會改用 /api/calc。
(() => {
  const PYODIDE = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/';
  const CODE = ['engine.py', 'tags.py', 'manual.py', 'zh_glossary.py', 'army.py'];
  const DATA = ['Last_update', 'Factions', 'Datasheets', 'Datasheets_models', 'Datasheets_wargear', 'Datasheets_abilities', 'Datasheets_keywords',
    'Datasheets_unit_composition', 'Datasheets_models_cost', 'Datasheets_options', 'Abilities', 'Detachments', 'Detachment_abilities', 'Stratagems', 'Enhancements'].map(f => f + '.csv').concat(['zh_units.json', 'zh_wargear.json', 'zh_dets.json', 'listcheck_bench.json', 'zh_scout.json', 'zh_sum.json', 'zh_comm.json']);
  let ready = null;
  // 背景先下載時沒有人看狀態；按「計算」後改成顯示在那一頁（2026-11-27 使用者選 C：先顯示畫面、背景下載）
  let say = () => {}, last = '';
  const tell = (s) => { last = s; say(s); };
  // 版本號（index.html 載入 browser.js?v=…）：程式和資料更新後，舊的瀏覽器快取不會被拿來用
  const V = ((document.currentScript && document.currentScript.src.match(/[?&]v=([^&]+)/)) || [])[1] || String(Date.now());

  async function boot(status) {
    status('正在下載計算程式和資料（第一次約 10 MB），請等一下…');
    await new Promise((ok, no) => {
      const s = document.createElement('script');
      s.src = PYODIDE + 'pyodide.js';
      s.onload = ok;
      s.onerror = () => no(new Error('下載不到 Pyodide，請確認網路後重新整理'));
      document.head.appendChild(s);
    });
    const py = await loadPyodide({ indexURL: PYODIDE });
    py.FS.mkdirTree('/app/data');
    const files = CODE.map(f => [f, '/app/' + f]).concat(DATA.map(f => ['data/' + f, '/app/data/' + f]));
    await Promise.all(files.map(async ([url, path]) => {
      const r = await fetch(url + '?v=' + V);
      if (!r.ok) throw new Error('下載不到 ' + url);
      py.FS.writeFile(path, new Uint8Array(await r.arrayBuffer()));
    }));
    // 各陣營手動標記的規則（rules/*.py，清單在 rules/index.json，bump.sh 產生）
    py.FS.mkdirTree('/app/rules');
    const ri = await fetch('rules/index.json?v=' + V);
    if (ri.ok) {
      await Promise.all((await ri.json()).map(async f => {
        const r = await fetch('rules/' + f + '?v=' + V);
        if (!r.ok) throw new Error('下載不到 rules/' + f);
        py.FS.writeFile('/app/rules/' + f, new Uint8Array(await r.arrayBuffer()));
      }));
    }
    py.runPython(`
import sys, json
sys.path.insert(0, '/app')
import engine
_db = engine.DB()
def _calc(s):
    return json.dumps(engine.api(json.loads(s), _db), ensure_ascii=False)
`);
    status('');
    return py.globals.get('_calc');
  }

  window.localCalc = async (req, status) => {
    say = status || (() => {});
    if (ready && last) say(last);
    ready = ready || boot(tell);
    let calc;
    try { calc = await ready; } catch (e) { ready = null; throw e; }
    try { return JSON.parse(calc(JSON.stringify(req))); } catch (e) {
      throw new Error(String(e.message || e).trim().split('\n').pop());
    }
  };
  // 首頁（最上層）打開後就在背景開始下載計算程式，等使用者貼好軍表按計算時通常已經好了
  if (window.parent === window) {
    const pre = () => { ready = ready || boot(tell); ready.catch(() => { ready = null; }); };
    if (document.readyState === 'complete') setTimeout(pre, 800); else window.addEventListener('load', () => setTimeout(pre, 800));
  }
})();
