#!/usr/bin/env python3
"""Genera pases de invitado con QR personalizado (uno por invitado/familia).

Cada invitado recibe un QR ÚNICO (?pase=<token>) que se escanea en la entrada
para el check-in en vivo (plan Premium).

Uso:
    python3 fuente/pases_qr.py [lista.csv]

CSV con columnas:  nombre,mesa,pases   (encabezado incluido). Ej:
    nombre,mesa,pases
    Familia Ramírez,1,4
    Ana & Luis,1,2

Salida (en la raíz del repo):
    Pases-QR-personalizados.pdf   -> un pase por página (A6, para imprimir)
    Pases-QR-A4-imprimir.pdf      -> 4 pases por hoja A4 + guías de corte
    pases-tokens.csv              -> nombre,mesa,pases,token,url  (tu lista de check-in)

Requiere: segno, pymupdf (fitz) y Chromium headless.
"""
import csv, io, base64, hashlib, pathlib, subprocess, os, sys
import segno, fitz

AQUI = pathlib.Path(__file__).resolve().parent
RAIZ = AQUI.parent
BASE_URL = "https://monucaapps.github.io/invitacion-demo/"   # a dónde apunta cada QR
SALT = "jm2027"                                              # cambia por evento
CHROME = os.environ.get("CHROME") or "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# ---- fuentes y arte (base64) ----
def b64(p): return base64.b64encode(pathlib.Path(p).read_bytes()).decode()
FUENTES = {"Vibes:400":"GreatVibes.woff2","Corm:400":"Cormorant400.woff2","Corm:500":"Cormorant500.woff2",
           "Corm:600":"Cormorant600.woff2","Eczar:400":"Eczar400.woff2","Eczar:600":"Eczar600.woff2"}
faces = "\n".join(
    f"@font-face{{font-family:'{k.split(':')[0]}';src:url(data:font/woff2;base64,{b64(AQUI/'fonts'/v)}) format('woff2');font-weight:{k.split(':')[1]};font-display:block;}}"
    for k, v in FUENTES.items())
assets = ":root{--art-border:url(data:image/png;base64," + b64(AQUI/"art"/"border_full.png") + ");}"

CARD_CSS = """:root{--cream:#FAF6EA;--cream2:#F4ECD8;--terra:#BC6242;--terra-d:#9E4E31;--olive:#7C8352;--slate:#7E8CA0;--ink:#4A4038;--ink-soft:#6E6357;--line:#E4D8BF;}
*{box-sizing:border-box;margin:0;padding:0;}
@page{size:105mm 148mm;margin:0;}
html,body{background:#fff;}
body{font-family:'Corm',serif;color:var(--ink);-webkit-print-color-adjust:exact;print-color-adjust:exact;}
.card{position:relative;width:105mm;height:148mm;overflow:hidden;background:radial-gradient(120% 80% at 50% 0%,#FFFDF7 0%,var(--cream) 60%,var(--cream2) 120%);}
.frame{position:absolute;inset:4mm;background:var(--art-border) no-repeat center;background-size:100% 100%;}
.inner{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center;padding:15mm 13mm;}
.eyebrow{font-family:'Eczar',serif;text-transform:uppercase;letter-spacing:.34em;font-size:7.5px;color:var(--olive);}
.names{font-family:'Vibes',cursive;color:var(--terra);font-size:30px;line-height:.9;margin:2px 0 1px;}
.date{font-family:'Corm',serif;color:var(--ink);font-size:10px;letter-spacing:.2em;font-weight:500;padding-left:.2em;}
.qrtile{width:35mm;height:35mm;background:#fff;border:1px solid var(--line);border-radius:9px;padding:2mm;margin:4.5mm 0 4mm;box-shadow:0 5px 14px rgba(150,110,70,.14);display:flex;}
.qrtile img{width:100%;height:100%;image-rendering:pixelated;}
.pase{font-family:'Eczar',serif;text-transform:uppercase;letter-spacing:.24em;font-size:7px;color:var(--olive);margin-bottom:1px;}
.guest{font-family:'Corm',serif;font-weight:600;color:var(--terra-d);font-size:19px;line-height:1.05;}
.mesa{font-family:'Eczar',serif;font-size:8.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--ink-soft);margin-top:3px;}
.cta{font-family:'Corm',serif;font-style:italic;font-size:10px;color:var(--slate);margin-top:4mm;}"""
A4CSS = "<style>@page{size:A4;margin:0;}body{margin:0;background:#fff}.sheet{width:210mm;height:297mm;display:grid;grid-template-columns:105mm 105mm;grid-template-rows:148.5mm 148.5mm;}.sheet .card{width:105mm!important;height:148.5mm!important;outline:.2mm dashed #d9cdb0;outline-offset:-.1mm;}</style>"
HEAD = f"<!DOCTYPE html><html lang=es><head><meta charset=utf-8><style>{faces}</style><style>{assets}</style><style>{CARD_CSS}</style>"

def token(nombre, i): return hashlib.sha1(f"{nombre}|{i}|{SALT}".encode()).hexdigest()[:8]
def qr_datauri(url):
    q = segno.make(url, error="h"); b = io.BytesIO()
    q.save(b, kind="png", scale=16, border=2, dark="#463A31", light="#FFFFFF")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()
def card_div(n, m, p, tok):
    plural = "pase" if str(p) == "1" else "pases"
    return ('<div class="card"><div class="frame"></div><div class="inner">'
            '<div class="eyebrow">Nuestra Boda</div><div class="names">Janeth&nbsp;&amp;&nbsp;Miguel</div>'
            '<div class="date">27 · 03 · 2027</div>'
            f'<div class="qrtile"><img src="{qr_datauri(BASE_URL + "?pase=" + tok)}"></div>'
            f'<div class="pase">Pase de invitado</div><div class="guest">{n}</div>'
            f'<div class="mesa">Mesa {m} · {p} {plural}</div>'
            '<div class="cta">Presenta este código al llegar</div></div></div>')
def render(html, name):
    tmp = AQUI / (name + ".html"); tmp.write_text(html); out = AQUI / (name + ".pdf")
    subprocess.run([CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    f"--print-to-pdf={out}", tmp.as_uri()], check=True, stderr=subprocess.DEVNULL)
    tmp.unlink()
    return out

def main():
    csv_path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else AQUI / "invitados-ejemplo.csv"
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    guests = [(r["nombre"].strip(), r["mesa"].strip(), r["pases"].strip()) for r in rows]

    # A6: un pase por página (render por tarjeta + merge — robusto)
    merged = fitz.open()
    tokens = []
    for i, (n, m, p) in enumerate(guests):
        tok = token(n, i); tokens.append((n, m, p, tok, BASE_URL + "?pase=" + tok))
        merged.insert_pdf(fitz.open(render(HEAD + "</head><body>" + card_div(n, m, p, tok) + "</body></html>", f"_pc_{i}")))
    merged.save(str(RAIZ / "Pases-QR-personalizados.pdf")); merged.close()

    # A4: 4 pases por hoja + guías de corte
    cards = [card_div(n, m, p, token(n, i)) for i, (n, m, p) in enumerate(guests)]
    m4 = fitz.open()
    for k in range(0, len(cards), 4):
        m4.insert_pdf(fitz.open(render(HEAD + A4CSS + "</head><body><div class='sheet'>" + "".join(cards[k:k+4]) + "</div></body></html>", f"_ps_{k}")))
    m4.save(str(RAIZ / "Pases-QR-A4-imprimir.pdf")); m4.close()

    # lista de check-in (token -> invitado)
    with (RAIZ / "pases-tokens.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f); w.writerow(["nombre", "mesa", "pases", "token", "url"]); w.writerows(tokens)

    # limpieza de PDFs temporales
    for tmp in AQUI.glob("_p*.pdf"): tmp.unlink()
    print(f"{len(guests)} pases -> Pases-QR-personalizados.pdf ({len(guests)} pág.) + Pases-QR-A4-imprimir.pdf + pases-tokens.csv")

if __name__ == "__main__":
    main()
