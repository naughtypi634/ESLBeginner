#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ESLBeginner · 可视化编辑器（在浏览器里边看边改，保存后自动生成 HTML / PDF）

用法:
    .venv/bin/python build/visual_editor.py                          # 默认编辑 21-Modal Verbs.md
    .venv/bin/python build/visual_editor.py "20-Zero First Conditional.md"
    .venv/bin/python build/visual_editor.py --port 9000

然后打开 http://127.0.0.1:8765

功能:
    - Markdown 源码 + 实时预览（与 PDF 使用同一套渲染样式）
    - 可视化编辑：直接点击预览里的文字修改，支持加粗、表格加行/删行/上下移
    - 保存前自动备份到 build/backups/
    - 保存并生成 PDF：复用 MD/_gen_beginner_series.py 的渲染管线

安全说明: 只监听 127.0.0.1（本机），不对外网开放。
"""

import argparse
import json
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

ROOT = Path(__file__).resolve().parent.parent
MD_DIR = ROOT / "MD"
PDF_DIR = ROOT / "PDF"
BACKUP_DIR = ROOT / "build" / "backups"
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(MD_DIR))
import _gen_beginner_series as gen  # noqa: E402  (复用项目的 md_to_html / export_pdf)

DEFAULT_FILE = "21-Modal Verbs.md"
CURRENT_DEFAULT = DEFAULT_FILE


def render_page(markdown: str, title: str = "Preview") -> str:
    """用与 PDF 完全相同的样式渲染完整 HTML 页面。"""
    body = gen.md_to_html(markdown)
    return (
        "<!DOCTYPE html><html lang='zh-CN'><head><meta charset='UTF-8'>"
        f"<title>{gen.esc(title)}</title><style>{gen.CSS}</style></head><body>"
        f"<div class='page'>{body}</div></body></html>"
    )


class EditorHandler(BaseHTTPRequestHandler):
    server_version = "ESLEditor/1.0"

    def log_message(self, fmt, *args):
        print(f"[editor] {self.address_string()} {fmt % args}", flush=True)

    def _send(self, body: bytes, content_type: str, status: int = 200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, status: int = 200):
        self._send(json.dumps(obj, ensure_ascii=False).encode("utf-8"),
                   "application/json; charset=utf-8", status)

    def _html(self, text: str, status: int = 200):
        self._send(text.encode("utf-8"), "text/html; charset=utf-8", status)

    def _safe_md_name(self, raw):
        name = unquote(raw or "")
        name = Path(name).name  # 只取文件名，防止路径穿越
        if not name.endswith(".md") or not (MD_DIR / name).exists():
            return None
        return name

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            return self._html(EDITOR_HTML)
        if url.path == "/api/files":
            names = sorted(p.name for p in MD_DIR.glob("*.md"))
            return self._json({"ok": True, "files": names, "default": CURRENT_DEFAULT})
        if url.path == "/api/doc":
            name = self._safe_md_name(parse_qs(url.query).get("file", [""])[0])
            if not name:
                return self._json({"ok": False, "error": "文件不存在"}, 404)
            text = (MD_DIR / name).read_text(encoding="utf-8")
            return self._json({"ok": True, "file": name, "markdown": text})
        if url.path == "/api/pdf":
            name = self._safe_md_name(parse_qs(url.query).get("file", [""])[0])
            if not name:
                return self._json({"ok": False, "error": "文件不存在"}, 404)
            pdf = PDF_DIR / Path(name).with_suffix(".pdf")
            if not pdf.exists():
                return self._json({"ok": False, "error": "PDF 尚未生成"}, 404)
            self.send_response(200)
            self.send_header("Content-Type", "application/pdf")
            self.send_header("Content-Disposition", f'attachment; filename="{pdf.name}"')
            self.send_header("Content-Length", str(pdf.stat().st_size))
            self.end_headers()
            self.wfile.write(pdf.read_bytes())
            return
        return self._json({"ok": False, "error": "not found"}, 404)

    def do_POST(self):
        url = urlparse(self.path)
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length) if length else b""
        try:
            data = json.loads(raw.decode("utf-8"))
        except Exception:
            return self._json({"ok": False, "error": "JSON 解析失败"}, 400)

        if url.path == "/api/render":
            markdown = data.get("markdown", "")
            title = data.get("title", "Preview")
            return self._json({"ok": True, "html": render_page(markdown, title)})

        if url.path == "/api/save":
            name = self._safe_md_name(data.get("file", ""))
            markdown = data.get("markdown", "")
            if not name:
                return self._json({"ok": False, "error": "文件不存在"}, 404)
            if not isinstance(markdown, str):
                return self._json({"ok": False, "error": "markdown 必须是文本"}, 400)

            md_path = MD_DIR / name
            stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            backup = BACKUP_DIR / f"{Path(name).stem}-{stamp}.md"
            backup.write_text(md_path.read_text(encoding="utf-8"), encoding="utf-8")
            md_path.write_text(markdown, encoding="utf-8")

            build = bool(data.get("build"))
            html_ok = pdf_ok = False
            html_error = pdf_error = None
            if build:
                html_path = MD_DIR / f"_{Path(name).stem}.html"
                pdf_path = PDF_DIR / Path(name).with_suffix(".pdf")
                try:
                    html_path.write_text(gen.build_html(name), encoding="utf-8")
                    html_ok = True
                except Exception as exc:  # noqa: BLE001
                    html_error = str(exc)
                try:
                    pdf_ok = gen.export_pdf(html_path, pdf_path)
                    if not pdf_ok:
                        pdf_error = "Playwright 不可用（请用 .venv/bin/python 启动）"
                except Exception as exc:  # noqa: BLE001
                    pdf_error = str(exc)

            return self._json({
                "ok": True,
                "file": name,
                "backup": str(backup.relative_to(ROOT)),
                "html_ok": html_ok,
                "pdf_ok": pdf_ok,
                "html_error": html_error,
                "pdf_error": pdf_error,
            })

        return self._json({"ok": False, "error": "not found"}, 404)


def main():
    global CURRENT_DEFAULT
    ap = argparse.ArgumentParser(description="ESLBeginner 可视化编辑器")
    ap.add_argument("file", nargs="?", default=DEFAULT_FILE,
                    help="要编辑的 Markdown 文件名，默认 21-Modal Verbs.md")
    ap.add_argument("--port", type=int, default=8765, help="监听端口，默认 8765")
    args = ap.parse_args()

    name = Path(args.file).name
    if not name.endswith(".md") or not (MD_DIR / name).exists():
        print(f"文件不存在: {args.file}", file=sys.stderr)
        sys.exit(1)
    CURRENT_DEFAULT = name

    server = ThreadingHTTPServer(("127.0.0.1", args.port), EditorHandler)
    print(f"ESLBeginner 可视化编辑器已启动:")
    print(f"  打开 http://127.0.0.1:{args.port}")
    print(f"  当前文件: {name}")
    print("  按 Ctrl+C 停止")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止。")


EDITOR_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ESLBeginner 可视化编辑器</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: -apple-system, "Segoe UI", "Microsoft YaHei", "PingFang SC", sans-serif; background: #eef1f4; color: #1f2933; height: 100vh; display: flex; flex-direction: column; }
  header { background: #14263b; color: #fff; padding: 10px 16px; display: flex; align-items: center; gap: 14px; flex-wrap: wrap; }
  header h1 { font-size: 16px; font-weight: 700; white-space: nowrap; }
  .controls { display: flex; align-items: center; gap: 10px; margin-left: auto; flex-wrap: wrap; }
  select, button { font-size: 13px; padding: 6px 10px; border-radius: 6px; border: 1px solid #cbd5e1; background: #fff; cursor: pointer; }
  button.primary { background: #1d5fa8; color: #fff; border-color: #1d5fa8; }
  button.ghost { background: #f1f5f9; }
  #status { color: #ffd479; font-size: 12px; max-width: 460px; overflow-wrap: anywhere; }
  #status.err { color: #ff9b9b; }
  #pdfLink { display: none; color: #7dd3fc; font-size: 13px; }
  .tabs { display: flex; gap: 4px; padding: 8px 16px 0; background: #e2e8f0; }
  .tabs button { border-bottom-left-radius: 0; border-bottom-right-radius: 0; border-bottom: none; }
  .tabs button.active { background: #fff; font-weight: 700; }
  .panes { flex: 1; display: flex; min-height: 0; padding: 8px 16px 16px; gap: 10px; }
  .pane { flex: 1; display: flex; flex-direction: column; gap: 8px; min-width: 0; }
  #mdPane { flex-direction: row; }
  .hidden { display: none !important; }
  textarea { flex: 1; min-width: 0; resize: none; border: 1px solid #cbd5e1; border-radius: 8px; padding: 10px; font: 13px/1.6 ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; outline: none; }
  textarea:focus { border-color: #1d5fa8; }
  iframe { flex: 1; min-width: 0; border: 1px solid #cbd5e1; border-radius: 8px; background: #fff; width: 100%; }
  #visualToolbar { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
  #visualToolbar .tip { font-size: 12px; color: #64748b; }
</style>
</head>
<body>
<header>
  <h1>📝 ESLBeginner 可视化编辑器</h1>
  <div class="controls">
    <select id="fileSel" title="选择要编辑的 Markdown 文件"></select>
    <button id="reloadBtn" class="ghost">↻ 重新加载</button>
    <button id="saveMdBtn" class="ghost">保存 Markdown</button>
    <button id="saveBtn" class="primary">💾 保存并生成 PDF</button>
    <a id="pdfLink" href="#">下载 PDF</a>
    <span id="status"></span>
  </div>
</header>
<div class="tabs">
  <button id="tabMd" class="active">Markdown 源码</button>
  <button id="tabVisual">可视化编辑</button>
</div>
<div class="panes">
  <div id="mdPane" class="pane">
    <textarea id="mdText" spellcheck="false" placeholder="左侧改 Markdown，右侧实时预览"></textarea>
    <iframe id="previewMd" title="实时预览"></iframe>
  </div>
  <div id="visualPane" class="pane hidden">
    <div id="visualToolbar">
      <button id="boldBtn" class="ghost"><b>B</b> 加粗</button>
      <button id="addRowBtn" class="ghost">＋ 表格加行</button>
      <button id="delRowBtn" class="ghost">－ 删行</button>
      <button id="upRowBtn" class="ghost">↑ 行上移</button>
      <button id="downRowBtn" class="ghost">↓ 行下移</button>
      <span class="tip">直接点击预览里的文字就能改；改完点右上角「保存并生成 PDF」</span>
    </div>
    <iframe id="previewVisual" title="可视化编辑区"></iframe>
  </div>
</div>
<script>
const $ = id => document.getElementById(id);
const fileSel = $('fileSel');
const mdTa = $('mdText');
const iframeMd = $('previewMd');
const iframeVis = $('previewVisual');
let currentFile = '';
let lastHtml = '';

function setStatus(msg, isErr) {
  const el = $('status');
  el.textContent = msg;
  el.classList.toggle('err', !!isErr);
}

async function api(url, body) {
  const opt = body
    ? { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) }
    : {};
  const res = await fetch(url, opt);
  const data = await res.json();
  if (!data.ok) throw new Error(data.error || '请求失败');
  return data;
}

async function loadFiles() {
  const data = await api('/api/files');
  data.files.forEach(f => {
    const o = document.createElement('option');
    o.value = f;
    o.textContent = f;
    fileSel.appendChild(o);
  });
  const q = new URLSearchParams(location.search).get('file');
  if (q && data.files.includes(q)) fileSel.value = q;
  else if (data.files.includes(data.default)) fileSel.value = data.default;
  else fileSel.value = data.files[0];
}

async function render() {
  const data = await api('/api/render', { markdown: mdTa.value, title: currentFile || 'Preview' });
  lastHtml = data.html;
  iframeMd.srcdoc = lastHtml;
  if (!$('tabVisual').classList.contains('active')) return;
  iframeVis.srcdoc = lastHtml;
}

async function loadDoc() {
  const data = await api('/api/doc?file=' + encodeURIComponent(fileSel.value));
  currentFile = data.file;
  mdTa.value = data.markdown;
  setStatus('已加载 ' + currentFile);
  await render();
}

let renderTimer = null;
mdTa.addEventListener('input', () => {
  clearTimeout(renderTimer);
  renderTimer = setTimeout(render, 350);
});

$('reloadBtn').addEventListener('click', () => {
  if (mdTa.value !== '') {
    mdTa.value = '';
    mdTa.placeholder = '确认放弃未保存的修改？再点一次「重新加载」';
    return;
  }
  loadDoc();
});
mdTa.addEventListener('focus', () => { mdTa.placeholder = '左侧改 Markdown，右侧实时预览'; });

function setActiveTab(tabId, paneId) {
  ['tabMd', 'tabVisual'].forEach(t => $(t).classList.toggle('active', t === tabId));
  $('mdPane').classList.toggle('hidden', paneId !== 'mdPane');
  $('visualPane').classList.toggle('hidden', paneId !== 'visualPane');
}

$('tabMd').addEventListener('click', () => {
  if (!$('tabVisual').classList.contains('active')) return;
  mdTa.value = serializeVisual();
  render();
  setActiveTab('tabMd', 'mdPane');
});

$('tabVisual').addEventListener('click', () => {
  setActiveTab('tabVisual', 'visualPane');
  iframeVis.srcdoc = lastHtml;
});

iframeVis.addEventListener('load', () => {
  try { iframeVis.contentDocument.designMode = 'on'; } catch (e) { /* 忽略 */ }
});

function visualDoc() { return iframeVis.contentDocument; }
function focusVisual() { try { iframeVis.contentWindow.focus(); } catch (e) { /* 忽略 */ } }

function inlineText(node) {
  let out = '';
  node.childNodes.forEach(n => {
    if (n.nodeType === Node.TEXT_NODE) out += n.textContent;
    else if (n.nodeName === 'BR') out += ' ';
    else if (n.nodeName === 'B' || n.nodeName === 'STRONG') out += '**' + inlineText(n) + '**';
    else if (n.nodeName === 'I' || n.nodeName === 'EM') out += '*' + inlineText(n) + '*';
    else if (n.nodeName === 'A') out += n.textContent;
    else out += inlineText(n);
  });
  return out.replace(/\\s+/g, ' ').trim();
}

function tableMd(table) {
  const lines = [];
  [...table.querySelectorAll('tr')].forEach((tr, idx) => {
    const cells = [...tr.querySelectorAll('th, td')].map(c => inlineText(c));
    lines.push('| ' + cells.join(' | ') + ' |');
    if (idx === 0) lines.push('| ' + cells.map(() => '---').join(' | ') + ' |');
  });
  return lines.join('\\n');
}

function serializeVisual() {
  const doc = visualDoc();
  if (!doc || !doc.body || !doc.body.children.length) return mdTa.value;
  const blocks = [];
  doc.body.childNodes.forEach(n => {
    if (n.nodeType !== Node.ELEMENT_NODE) return;
    const tag = n.tagName;
    if (tag === 'H1') blocks.push('# ' + inlineText(n));
    else if (tag === 'H2') blocks.push('## ' + inlineText(n));
    else if (tag === 'H3') blocks.push('### ' + inlineText(n));
    else if (tag === 'H4') blocks.push('#### ' + inlineText(n));
    else if (tag === 'H5') blocks.push('##### ' + inlineText(n));
    else if (tag === 'H6') blocks.push('###### ' + inlineText(n));
    else if (tag === 'HR') blocks.push('---');
    else if (tag === 'TABLE') blocks.push(tableMd(n));
    else if (tag === 'P' || tag === 'DIV' || tag === 'UL' || tag === 'OL') blocks.push(inlineText(n));
  });
  return blocks.join('\\n\\n').replace(/\\n{3,}/g, '\\n\\n') + '\\n';
}

function currentRow() {
  const doc = visualDoc();
  if (!doc) return null;
  const sel = doc.getSelection();
  if (!sel || !sel.anchorNode) return null;
  let node = sel.anchorNode;
  while (node && node !== doc.body && node.nodeName !== 'TR') node = node.parentNode;
  return node && node.nodeName === 'TR' ? node : null;
}

$('boldBtn').addEventListener('click', () => {
  focusVisual();
  try { visualDoc().execCommand('bold'); } catch (e) { /* 忽略 */ }
});

$('addRowBtn').addEventListener('click', () => {
  const tr = currentRow();
  if (!tr) return setStatus('请先点击表格里的某一行', true);
  const table = tr.closest('table');
  if (!table || !table.rows.length) return;
  const cols = table.rows[0].cells.length;
  const doc = visualDoc();
  const nr = doc.createElement('tr');
  for (let i = 0; i < cols; i++) {
    const c = doc.createElement('td');
    c.innerHTML = '&nbsp;';
    nr.appendChild(c);
  }
  tr.after(nr);
});

$('delRowBtn').addEventListener('click', () => {
  const tr = currentRow();
  if (!tr) return setStatus('请先点击要删除的行', true);
  tr.remove();
});

$('upRowBtn').addEventListener('click', () => {
  const tr = currentRow();
  if (!tr || !tr.previousElementSibling) return;
  tr.parentNode.insertBefore(tr, tr.previousElementSibling);
});

$('downRowBtn').addEventListener('click', () => {
  const tr = currentRow();
  if (!tr || !tr.nextElementSibling) return;
  tr.parentNode.insertBefore(tr.nextElementSibling, tr);
});

async function doSave(build) {
  const activeVisual = $('tabVisual').classList.contains('active');
  const markdown = activeVisual ? serializeVisual() : mdTa.value;
  if (!markdown.trim()) return setStatus('内容为空，未保存', true);
  setStatus('正在保存…');
  try {
    const data = await api('/api/save', { file: currentFile, markdown, build });
    mdTa.value = markdown;
    await render();
    let msg = '已保存 ' + data.file;
    if (data.backup) msg += ' · 备份 ' + data.backup;
    if (build) {
      msg += ' · HTML ' + (data.html_ok ? '✓' : '✗') + ' · PDF ' + (data.pdf_ok ? '✓' : '✗');
      if (data.pdf_ok) {
        $('pdfLink').style.display = '';
        $('pdfLink').href = '/api/pdf?file=' + encodeURIComponent(currentFile);
      }
    }
    setStatus(msg);
    if (data.html_error) setStatus('HTML 生成失败: ' + data.html_error, true);
    if (data.pdf_error) setStatus('PDF 生成失败: ' + data.pdf_error, true);
  } catch (e) {
    setStatus('保存失败: ' + e.message, true);
  }
}

$('saveMdBtn').addEventListener('click', () => doSave(false));
$('saveBtn').addEventListener('click', () => doSave(true));

(async function init() {
  try {
    await loadFiles();
    await loadDoc();
  } catch (e) {
    setStatus('初始化失败: ' + e.message, true);
  }
})();
</script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
