#!/usr/bin/env python3
"""Regenera la cotización en PDF a partir de cotizacion.html + faces.css.

Uso:
    python3 fuente/build.py
Requiere Chromium (headless). Ajusta CHROME si tu ruta es distinta.
"""
import base64, pathlib, subprocess, shutil, os

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent

# 1) (Re)genera faces.css embebiendo las fuentes en base64 (por si cambian)
FUENTES = {
    "Vibes:400": "GreatVibes.woff2",
    "Corm:400":  "Cormorant400.woff2",
    "Corm:500":  "Cormorant500.woff2",
    "Corm:600":  "Cormorant600.woff2",
    "Eczar:400": "Eczar400.woff2",
    "Eczar:600": "Eczar600.woff2",
}
def b64(nombre):
    return base64.b64encode((AQUI / "fonts" / nombre).read_bytes()).decode()

faces = []
for clave, archivo in FUENTES.items():
    fam, peso = clave.split(":")
    faces.append(
        f"@font-face{{font-family:'{fam}';"
        f"src:url(data:font/woff2;base64,{b64(archivo)}) format('woff2');"
        f"font-weight:{peso};font-display:block;}}"
    )
(AQUI / "faces.css").write_text("\n".join(faces))

# 2) Inyecta las fuentes dentro del HTML
html = (AQUI / "cotizacion.html").read_text()
html = html.replace("/*FACES*/", (AQUI / "faces.css").read_text())
final = AQUI / "cotizacion_final.html"
final.write_text(html)

# 3) Imprime a PDF con Chromium
CHROME = os.environ.get("CHROME") or shutil.which("chromium") or shutil.which("google-chrome") \
    or "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
salida = RAIZ / "Cotizacion-Invitaciones-QR.pdf"
subprocess.run([
    CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
    f"--print-to-pdf={salida}", final.as_uri(),
], check=True)
print("PDF generado en:", salida)
