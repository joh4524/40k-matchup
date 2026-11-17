"""軍表對戰計算網頁的伺服器版（2026-11-15）。只接受 MATCHUP_ALLOW 裡的來源位址。
環境變數：MATCHUP_BIND 綁哪個位址（預設只有本機）、MATCHUP_PORT、MATCHUP_ALLOW 允許的來源位址（逗號分隔）。
不想架伺服器的話，把整個資料夾當靜態網站放出去也能用（browser.js 會在瀏覽器裡跑計算）。"""
import json, os, pathlib, sys, traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine

BIND = os.environ.get("MATCHUP_BIND", "127.0.0.1")
PORT = int(os.environ.get("MATCHUP_PORT", "8090"))
ALLOW = set(os.environ.get("MATCHUP_ALLOW", "127.0.0.1").split(","))
DBX = engine.DB()


class Handler(BaseHTTPRequestHandler):
    def allowed(self):
        return self.client_address[0] in ALLOW and self.headers.get("Host") == f"{BIND}:{PORT}"

    def reply(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else json.dumps(body, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if not self.allowed():
            return self.reply(403, {"error": "forbidden"})
        if self.path in ("/", "/index.html"):
            return self.reply(200, (HERE / "index.html").read_bytes(), "text/html; charset=utf-8")
        if self.path.split("?")[0] == "/meta.json" and (HERE / "meta" / "meta.json").exists():   # GT 前段代表表（tools/meta_build.py；只在這台，不進 git）
            return self.reply(200, (HERE / "meta" / "meta.json").read_bytes())
        self.reply(404, {"error": "not found"})

    def do_POST(self):
        if not self.allowed():
            return self.reply(403, {"error": "forbidden"})
        if self.path != "/api/calc":
            return self.reply(404, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length", "0"))
            if n > 200000:
                return self.reply(413, {"error": "太長"})
            req = json.loads(self.rfile.read(n))
            self.reply(200, engine.api(req, DBX))
        except Exception as e:
            traceback.print_exc()
            self.reply(500, {"error": f"{type(e).__name__}: {e}"})

    def log_message(self, *a):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer((BIND, PORT), Handler).serve_forever()
