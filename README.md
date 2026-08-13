# Industrial Automation Business Intelligence Brief

Monitor diario de inteligencia competitiva para **automatización industrial**: virtual commissioning, digital twin, simulación de PLC/robots e intralogística.

Los módulos en Python recogen noticias de RSS, Google News y YouTube, filtran por palabras clave, evitan duplicados y generan reportes.

## Idioma

- **Documentación, PRs y comunicación del equipo:** español.
- **Código fuente:** inglés (nombres, comentarios, docstrings, logs y mensajes de consola).
- **Reportes generados** (Markdown, CSV, HTML): inglés, porque son la salida del producto.

## Qué genera

| Archivo | Contenido |
|---------|-----------|
| `business_intelligence_brief.md` | Reporte legible para GitHub |
| `business_intelligence_brief.csv` | Export estructurado |
| `docs/index.html` | Página estática (GitHub Pages) |
| `data/seen.json` | Historial de enlaces ya vistos (deduplicación) |
| `data/latest_by_topic.json` | Último artículo relevante por tema/competidor (respaldo) |

Cada tema o competidor muestra contenido cuando existe:

- **Artículos nuevos en esta corrida** → solo esos artículos
- **Sin artículos nuevos** → se muestra el último guardado en `latest_by_topic.json` (marcado como *last seen*)

Las marcas de tiempo (generación y `published` de cada artículo) usan **America/Mexico_City**, formato `YYYY-MM-DD HH:MM`, y se etiquetan `(Mexico City)`.

## Estructura del proyecto

- `competitor_monitor.py` — punto de entrada
- `config.py` — feeds, keywords, rutas de salida
- `datetime_utils.py` — helpers de zona horaria de Ciudad de México (`zoneinfo`)
- `feeds.py`, `filter.py`, `storage.py`, `collector.py`, `writers.py` — descarga, filtro, deduplicación, respaldo y escritura de reportes

## Cómo ejecutarlo en local

```bash
python -m pip install -r requirements.txt
python competitor_monitor.py
```

Requiere internet de salida (feeds externos). Para previsualizar la página:

```bash
python -m http.server 8000
# Abrir http://localhost:8000/docs/index.html
```

Una corrida local **modifica archivos rastreados**. Si solo estás probando el entorno, restáuralos después:

```bash
git checkout -- business_intelligence_brief.md business_intelligence_brief.csv docs/index.html data/seen.json data/latest_by_topic.json
```

## Automatización diaria en GitHub

Workflow: `.github/workflows/daily_business_brief.yml`

- Corre todos los días a las `12:00 UTC` (aprox. `06:00` en Ciudad de México)
- También se puede disparar a mano desde la pestaña Actions
- Input opcional `reset_seen`: vacía `data/seen.json` antes de generar
- Hace commit automático de los reportes y del estado en `data/`

## Cómo leer el brief

Abre `business_intelligence_brief.md` en el repositorio para ver el reporte más reciente.
