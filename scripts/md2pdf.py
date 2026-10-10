"""Convert a kich-ban.md into a phone-sized PDF via headless Chrome/Edge.

Usage: python md2pdf.py <kich-ban.md> <out.pdf> ["Title"]
Boxes: [CLIP …] blue · 🟨 yellow · 🟦 green · "Bài học rút ra:" purple · [SỬA SỐ]/[KIỂM] red tag.
Each "## N." / "## KẾT" / "## PHỤ LỤC" heading starts a new page.
"""
import html as htmlmod
import os
import pathlib
import re
import subprocess
import sys

import markdown

SRC = pathlib.Path(sys.argv[1]).resolve()
OUT_PDF = pathlib.Path(sys.argv[2]).resolve()
TITLE = sys.argv[3] if len(sys.argv) > 3 else SRC.stem

BROWSERS = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
BROWSER = next((b for b in BROWSERS if os.path.exists(b)), None)
if not BROWSER:
    print("Không tìm thấy Chrome/Edge để in PDF.")
    sys.exit(1)

md_text = SRC.read_text(encoding="utf-8")
body = markdown.markdown(md_text, extensions=["tables", "sane_lists"])

body = re.sub(
    r"<p><code>\[CLIP ([^<]*)\]</code>(.*?)</p>",
    lambda m: '<div class="clip"><span class="clipname">CLIP %s</span>%s</div>'
    % (htmlmod.escape(htmlmod.unescape(m.group(1))), m.group(2)),
    body, flags=re.S,
)
body = re.sub(r"<p>🟨\s*(.*?)</p>", r'<div class="me">\1</div>', body, flags=re.S)
body = re.sub(r"<p>🟦\s*(.*?)</p>", r'<div class="cta">\1</div>', body, flags=re.S)
body = re.sub(
    r"<p><strong>(Bài học rút ra|Ghi vào sổ):</strong>(.*?)</p>",
    r'<div class="note"><span class="notelabel">\1</span>\2</div>',
    body, flags=re.S,
)
body = re.sub(r"<h2>(?=(\d+\.|KẾT|PHỤ LỤC))", '<h2 class="pb">', body)
body = re.sub(r"<code>\[(SỬA SỐ|KIỂM)\]</code>", r'<span class="tag">\1</span>', body)

css = """
@page { size: 120mm 213mm; margin: 9mm 8mm 10mm 8mm; }
* { box-sizing: border-box; }
body { font-family: 'Be Vietnam Pro', 'Segoe UI', Roboto, Arial, sans-serif; font-size: 12.2pt; line-height: 1.5; color: #1a1a1a; margin: 0; }
h1 { font-size: 17pt; line-height: 1.25; margin: 0 0 6pt; page-break-after: avoid; }
h2 { font-size: 14.5pt; line-height: 1.25; margin: 0 0 8pt; padding: 8pt 0 6pt; border-top: 2.5pt solid #1a1a1a; page-break-after: avoid; }
h2.pb { page-break-before: always; }
h3 { font-size: 12.5pt; margin: 12pt 0 4pt; page-break-after: avoid; }
p { margin: 0 0 8pt; orphans: 2; widows: 2; }
em { font-style: italic; color: #333; }
hr { border: 0; border-top: 1px solid #ccc; margin: 10pt 0; }
ul, ol { padding-left: 16pt; margin: 0 0 8pt; }
li { margin-bottom: 3pt; }
table { border-collapse: collapse; width: 100%; font-size: 9pt; margin: 0 0 10pt; }
th, td { border: 1px solid #bbb; padding: 3pt 4pt; vertical-align: top; text-align: left; }
th { background: #eee; }
tr { page-break-inside: avoid; }
code { font-family: Consolas, monospace; font-size: 10pt; background: #f0f0f0; padding: 0 2pt; }
.clip { background: #e8f1ff; border-left: 4pt solid #2f6fdb; padding: 6pt 8pt; margin: 8pt 0 10pt; font-size: 10.5pt; color: #1b3a6b; page-break-inside: avoid; }
.clipname { display: block; font-weight: 700; font-family: Consolas, monospace; font-size: 10.5pt; margin-bottom: 2pt; }
.me { background: #fff5c2; border-left: 4pt solid #e0a800; padding: 6pt 8pt; margin: 8pt 0 10pt; font-size: 10.8pt; page-break-inside: avoid; }
.cta { background: #e6f7ee; border-left: 4pt solid #1f9d55; padding: 6pt 8pt; margin: 8pt 0 10pt; font-size: 10.8pt; page-break-inside: avoid; }
.note { background: #f3eefc; border-left: 4pt solid #7b4fd6; padding: 6pt 8pt; margin: 8pt 0 10pt; font-weight: 600; page-break-inside: avoid; }
.notelabel { display: inline-block; font-size: 9pt; letter-spacing: .5pt; text-transform: uppercase; color: #7b4fd6; margin-right: 6pt; }
.tag { display: inline-block; background: #d93025; color: #fff; font-size: 9pt; font-weight: 700; padding: 0 4pt; border-radius: 3pt; }
"""

html_doc = (
    "<!doctype html><html lang='vi'><head><meta charset='utf-8'><title>%s</title><style>%s</style></head><body>%s</body></html>"
    % (htmlmod.escape(TITLE), css, body)
)
html_path = OUT_PDF.with_suffix(".html")
html_path.write_text(html_doc, encoding="utf-8")

res = subprocess.run([
    BROWSER, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
    "--print-to-pdf=%s" % str(OUT_PDF), html_path.as_uri(),
], capture_output=True, text=True, timeout=180)
if OUT_PDF.exists():
    try:
        import pypdfium2 as pdfium
        n = len(pdfium.PdfDocument(str(OUT_PDF)))
    except Exception:
        n = "?"
    print(f"PDF: {OUT_PDF} ({OUT_PDF.stat().st_size} bytes, {n} trang)")
else:
    print("In PDF thất bại:", res.stderr[-1500:])
    sys.exit(1)
