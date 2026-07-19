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
(RAIZ / "demo").mkdir(exist_ok=True)
(RAIZ / "demo" / "index.html").write_text(demo_page)
print("HTML: demo/index.html")
