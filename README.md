# Cotización · Invitaciones Digitales con Código QR

Cotización (2 propuestas: **Sencilla** y **Pro**) para ofrecer invitaciones de
boda como página web con código QR, usando el dominio `109823.shop` (subdominios
ilimitados gratis, p. ej. `invitacion.109823.shop`).

## Archivos

| Archivo | Qué es |
|---|---|
| `Cotizacion-Invitaciones-QR.pdf` | **El entregable** — cotización lista (4 páginas, A4). |
| `fuente/cotizacion.html` | Plantilla editable (contenido, precios, textos). |
| `fuente/faces.css` | Tipografías (Cormorant Garamond, Great Vibes, Eczar) en base64. |
| `fuente/fonts/` | Fuentes originales `.woff2`. |
| `fuente/build.py` | Regenera el PDF desde el HTML. |

## Cómo editar precios o textos

1. Edita `fuente/cotizacion.html` (busca `899`, `1,999`, o los `<li>` de cada paquete).
2. Regenera el PDF:
   ```bash
   python3 fuente/build.py
   ```

## Resumen del modelo de costos

El único gasto real es el **dominio** (~$180 MXN/año, ya adquirido). Hosting, SSL,
código QR, formularios de confirmación (RSVP) y subdominios se resuelven con planes
**gratuitos**. Cada invitación adicional cuesta prácticamente $0, así que cada venta
es casi utilidad.

Precios de referencia (editables): **Sencilla $899 MXN** · **Pro $1,999 MXN**.
