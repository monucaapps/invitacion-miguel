#!/usr/bin/env python3
"""Regenera los PDFs de cotización y el HTML de la invitación demo.

Genera:
  - Cotizacion-Cliente.pdf   (para el cliente · 3 planes, sin costos internos)
  - Cotizacion-Interna.pdf    (tu copia · incluye conceptos y costos)
  - demo/invitacion-demo.html (invitación de demostración, autónoma)

Uso:  python3 fuente/build.py
Requiere Chromium (headless). Ajusta CHROME si tu ruta es distinta.
"""
import base64, pathlib, subprocess, shutil, os

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent

# 1) faces.css — fuentes en base64
FUENTES = {
    "Vibes:400": "GreatVibes.woff2", "Corm:400": "Cormorant400.woff2",
    "Corm:500": "Cormorant500.woff2", "Corm:600": "Cormorant600.woff2",
    "Eczar:400": "Eczar400.woff2", "Eczar:600": "Eczar600.woff2",
}
def b64(p): return base64.b64encode(pathlib.Path(p).read_bytes()).decode()
faces = []
for clave, arch in FUENTES.items():
    fam, peso = clave.split(":")
    faces.append(f"@font-face{{font-family:'{fam}';src:url(data:font/woff2;base64,{b64(AQUI/'fonts'/arch)}) format('woff2');font-weight:{peso};font-display:block;}}")
faces_css = "\n".join(faces)
(AQUI / "faces.css").write_text(faces_css)

# 2) assets.css — arte acuarela real (marco + esquinas) en base64
ART = AQUI / "art"
assets = ":root{\n"
assets += f"  --art-border:url(data:image/png;base64,{b64(ART/'border_full.png')});\n"
for n in ["tl", "tr", "bl", "br"]:
    assets += f"  --art-{n}:url(data:image/png;base64,{b64(ART/('c_'+n+'.png'))});\n"
assets += "}\n"
(AQUI / "assets.css").write_text(assets)

CHROME = os.environ.get("CHROME") or shutil.which("chromium") or shutil.which("google-chrome") \
    or "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

def render_pdf(src_html, out_pdf):
    html = pathlib.Path(src_html).read_text().replace("/*FACES*/", faces_css).replace("/*ASSETS*/", assets)
    tmp = AQUI / ("_" + pathlib.Path(src_html).stem + "_final.html")
    tmp.write_text(html)
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out_pdf}", tmp.as_uri()], check=True)
    print("PDF:", out_pdf)

render_pdf(AQUI / "cotizacion_cliente.html", RAIZ / "Cotizacion-Cliente.pdf")
render_pdf(AQUI / "cotizacion.html",         RAIZ / "Cotizacion-Interna.pdf")

# 3) invitación demo autónoma
demo = pathlib.Path(AQUI / "invitacion_demo.html").read_text().replace("/*FACES*/", faces_css).replace("/*ASSETS*/", assets)
demo_page = "<!doctype html><html lang=es><head><meta charset=utf-8><meta name=viewport content=\"width=device-width,initial-scale=1\"><title>Janeth & Miguel</title></head><body>" + demo + "</body></html>"
# La invitación demo va en /docs para GitHub Pages ("Deploy from a branch")
docs = RAIZ / "docs"; docs.mkdir(exist_ok=True)
(docs / "index.html").write_text(demo_page)
(docs / ".nojekyll").write_text("")
print("HTML: docs/index.html")

# 4) Tarjeta QR imprimible (apunta a la invitación publicada)
URL_INVITACION = "https://monucaapps.github.io/invitacion-demo/"
try:
    import segno, io, base64
    qr = segno.make(URL_INVITACION, error="h")   # alta corrección para impresión
    buf = io.BytesIO(); qr.save(buf, kind="png", scale=20, border=2, dark="#463A31", light="#FFFFFF")
    qr_b64 = base64.b64encode(buf.getvalue()).decode()
    card = (AQUI / "tarjeta_qr.html").read_text() \
        .replace("/*FACES*/", faces_css).replace("/*ASSETS*/", assets).replace("/*QR*/", qr_b64)
    tmp = AQUI / "_tarjeta_final.html"; tmp.write_text(card)
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={RAIZ/'Tarjeta-QR.pdf'}", tmp.as_uri()], check=True)
    # Hoja A4 con 4 tarjetas (2x2 = A4) y guías de corte
    head = card.split("<body>")[0]
    body_card = card.split("<body>")[1].split("</body>")[0].strip()
    a4css = ("<style>@page{size:A4;margin:0;}body{margin:0;}"
             ".sheet{width:210mm;height:297mm;display:grid;grid-template-columns:105mm 105mm;grid-template-rows:148.5mm 148.5mm;}"
             ".sheet .card{width:105mm!important;height:148.5mm!important;page-break-after:auto!important;"
             "outline:0.2mm dashed #d9cdb0;outline-offset:-0.1mm;}</style>")
    a4 = head + a4css + "</head><body><div class='sheet'>" + body_card*4 + "</div></body></html>"
    tmp2 = AQUI / "_tarjeta_a4_final.html"; tmp2.write_text(a4)
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={RAIZ/'Tarjetas-QR-A4-imprimir.pdf'}", tmp2.as_uri()], check=True)
    print("PDF: Tarjeta-QR.pdf  +  Tarjetas-QR-A4-imprimir.pdf")
except ImportError:
    print("segno no instalado; omito tarjeta QR  (pip install segno)")
