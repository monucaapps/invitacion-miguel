# Invitaciones Digitales con Código QR

Material para ofrecer invitaciones de boda como página web con código QR, usando el
dominio `109823.shop` (subdominios ilimitados gratis, p. ej. `invitacion.109823.shop`).

## Entregables

| Archivo | Para quién | Qué es |
|---|---|---|
| `Cotizacion-Cliente.pdf` | **El cliente** | 3 propuestas (Sencilla / Pro / Premium). **No** muestra costos internos. |
| `Cotizacion-Interna.pdf` | **Tú (Jorge)** | Lo mismo + página de conceptos y costos reales (margen). No compartir. |
| `demo/invitacion-demo.html` | Demo | Invitación de demostración autónoma (ábrela en el navegador). |

**Liga demo en vivo:** publicada como artifact en claude.ai (incluye el mapa de mesas
con check-in en vivo del plan Premium).

## Precios (editables)

| Plan | Precio | Incluye |
|---|---|---|
| **Sencilla** | $1,200 MXN | Portada, cuenta regresiva, evento, mapa, música, QR + enlace. |
| **Pro** | $2,800 MXN | + RSVP con panel, galería, mesa de regalos, itinerario, tarjeta física QR. |
| **Premium** | $3,600 MXN | + Mapa de mesas y **check-in en vivo**: QR por invitado, hora de llegada, alta manual en puerta, tablero en vivo. |

## Diseño floral

El arte acuarela es **exactamente** el del ejemplo de la boda Janeth & Miguel
(extraído de `Janeth_C_tarjetas.pdf`): marco completo en portadas/hero y esquinas
suavizadas en páginas de contenido. Assets en `fuente/art/`.

## Cómo editar y regenerar

1. Edita el contenido/precios en `fuente/cotizacion_cliente.html` y `fuente/cotizacion.html`
   (invitación demo en `fuente/invitacion_demo.html`).
2. Regenera todo:
   ```bash
   python3 fuente/build.py
   ```
   Genera los dos PDF y `demo/invitacion-demo.html`. Requiere Chromium headless.

## Modelo de costos (interno)

El único gasto real es el **dominio** (~$180 MXN/año, ya adquirido). Hosting, SSL, QR,
RSVP, check-in (Firebase/Supabase plan gratuito) y subdominios = **$0**. Cada venta es
casi utilidad pura.
