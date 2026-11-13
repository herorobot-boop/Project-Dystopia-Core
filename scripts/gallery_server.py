#!/usr/bin/env python3
"""out/raw を一覧表示するだけの軽量サーバ。"""
import html
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path("/workspace/Project-Dystopia-Core/out/raw")
EXTS = {".png", ".jpg", ".jpeg", ".webp", ".mp4", ".gif"}


def page() -> str:
    files = sorted((p for p in ROOT.iterdir() if p.suffix.lower() in EXTS),
                   key=lambda p: p.name, reverse=True) if ROOT.exists() else []
    cells = []
    for p in files:
        q = html.escape(p.name)
        if p.suffix.lower() == ".mp4":
            body = f'<video src="/f/{q}" controls muted loop playsinline></video>'
        else:
            body = f'<img src="/f/{q}" loading="lazy">'
        cells.append(f'<figure><a href="/f/{q}" target="_blank">{body}</a>'
                     f'<figcaption>{q}<br><a href="/del?name={q}">削除</a></figcaption></figure>')
    return f"""<!doctype html><meta name="viewport" content="width=device-width,initial-scale=1">
<title>out/raw ({len(files)})</title>
<style>body{{background:#111;color:#ddd;font:13px system-ui;margin:8px}}
.g{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:6px}}
img,video{{width:100%;border-radius:6px;display:block}}
figcaption{{font-size:10px;word-break:break-all}}</style>
<h3>out/raw — {len(files)} 件</h3><div class="g">{''.join(cells)}</div>"""


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        if u.path == "/":
            return self._send(200, page().encode())
        if u.path == "/del":
            n = parse_qs(u.query).get("name", [""])[0]
            t = ROOT / n
            if t.is_file():
                t.unlink()
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return
        if u.path.startswith("/f/"):
            t = ROOT / u.path[3:]
            if t.is_file():
                return self._send(200, t.read_bytes(), "application/octet-stream")
        return self._send(404, b"not found")


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    print(f"listening :{port}")
    ThreadingHTTPServer(("0.0.0.0", port), H).serve_forever()
