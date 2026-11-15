// 公開版（GitHub Pages 這類只放檔案的網站）用：沒有伺服器，計算程式（engine.py）用 Pyodide 直接在瀏覽器裡跑。
// 自己架 app.py 時這個檔不會被送出來，網頁會改用 /api/calc。
(() => {
  const PYODIDE = 'https://cdn.jsdelivr.net/pyodide/v0.26.4/full/';
  const CODE = ['engine.py', 'tags.py', 'manual.py', 'zh_glossary.py'];
  const DATA = ['Last_update', 'Factions', 'Datasheets', 'Datasheets_models', 'Datasheets_wargear', 'Datasheets_abilities', 'Datasheets_keywords',
    'Datasheets_unit_composition', 'Datasheets_models_cost', 'Datasheets_options', 'Abilities', 'Detachments', 'Detachment_abilities', 'Stratagems'].map(f => f + '.csv').concat(['zh_units.json', 'zh_wargear.json']);
  let ready = null;

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
      const r = await fetch(url);
      if (!r.ok) throw new Error('下載不到 ' + url);
      py.FS.writeFile(path, new Uint8Array(await r.arrayBuffer()));
    }));
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
    ready = ready || boot(status || (() => {}));
    let calc;
    try { calc = await ready; } catch (e) { ready = null; throw e; }
    try { return JSON.parse(calc(JSON.stringify(req))); } catch (e) {
      throw new Error(String(e.message || e).trim().split('\n').pop());
    }
  };
})();
