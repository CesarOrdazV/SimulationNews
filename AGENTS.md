# AGENTS.md

Guía de contexto para agentes de IA. Lee este archivo antes de explorar el repositorio.

## Idioma

- **Comunicación con el equipo, PRs y documentación** (`README.md`, este archivo): español.
- **Código fuente:** inglés. Incluye identificadores, comentarios, docstrings, logs y mensajes de consola.
- **Salida generada** (Markdown, CSV, HTML del brief): inglés. No traduzcas esas cadenas salvo que te lo pidan.

No mezcles español en el código. Si encuentras logs o comentarios en español, corrígelos a inglés.

## Qué es este proyecto

Monitor diario de inteligencia competitiva para **automatización industrial** (virtual commissioning, digital twin, simulación de PLC/robots, intralogística). Módulos Python recogen noticias de RSS, Google News y YouTube, filtran por keywords, deduplican entradas y generan reportes.

**Punto de entrada:** `competitor_monitor.py` (`main()`)
**Automatización:** GitHub Actions (`.github/workflows/daily_business_brief.yml`) — corre diario a las 12:00 UTC (~06:00 Ciudad de México) y se puede disparar a mano.

## Layout del repositorio

```
competitor_monitor.py          # Orquesta load → collect → write
config.py                      # Feeds, keywords, rutas, etiquetas de sección
feeds.py                       # Descarga de feeds y extracción de texto
filter.py                      # Relevancia por keywords
storage.py                     # Carga/guarda seen.json y latest_by_topic.json
collector.py                   # Iteración de grupos, deduplicación, fallback
datetime_utils.py              # Helpers America/Mexico_City
writers.py                     # Escritores CSV, Markdown y HTML
requirements.txt               # feedparser>=6.0.11
.github/workflows/
  daily_business_brief.yml     # CI: instala deps, corre el script, commitea
data/
  seen.json                    # Historial de enlaces (deduplicación)
  latest_by_topic.json         # Último artículo relevante por section:topic
docs/
  index.html                   # Página estática (GitHub Pages)
business_intelligence_brief.md # Reporte Markdown
business_intelligence_brief.csv# Export CSV
README.md                      # Documentación para humanos
```

No hay suite de tests, linter ni formatter configurados.

## Flujo de datos

1. **Cargar** `data/seen.json` — dict `{ "section:topic": [link, ...] }`.
2. **Cargar** `data/latest_by_topic.json` — dict `{ "section:topic": { campos del artículo... } }`.
3. **Iterar dos grupos de feeds:**
   - `COMPETITOR_FEEDS` — NVIDIA, RoboDK, Siemens Digital Industries, Visual Components, Rockwell Automation, AnyLogic, F.EE / fescreen-sim.
   - `BUSINESS_KEYWORD_FEEDS` — Virtual Commissioning, Digital Twin Manufacturing, PLC Simulation, Robot Simulation, Intralogistics Simulation (Google News RSS).
4. **Por cada entrada:** descartar si title+summary no contienen ninguna de `KEYWORDS`; actualizar `latest_by_topic` si el artículo es más reciente; no marcar como "nuevo" si el link ya está en `seen`.
5. **Normalizar timestamps** con `datetime_utils.py` (`America/Mexico_City`, formato `YYYY-MM-DD HH:MM`) para `published` y la hora de generación.
6. **Armar filas de display** con `build_display_items()`:
   - temas con artículos nuevos → mostrar **solo** esos
   - temas sin artículos nuevos → mostrar el último guardado en `latest_by_topic.json` (marcado como fallback)
7. **Escribir salidas** a partir de las filas de display (no es un historial acumulado de todos los artículos pasados).
8. **Persistir** `seen.json` y `latest_by_topic.json` actualizados.

## Fecha y hora

- Todas las marcas de tiempo visibles usan **`America/Mexico_City`** (`zoneinfo` de la stdlib; sin deps extra).
- Helpers en `datetime_utils.py`: `format_mexico_now()`, `format_entry_published()`, `format_mexico_datetime()`, `is_published_newer()`.
- Formato `YYYY-MM-DD HH:MM` (sin segundos). Los encabezados Markdown/HTML etiquetan la zona como `(Mexico City)`.
- Los valores RSS `published` / `updated` se convierten desde struct times de feedparser (UTC) a hora local de Ciudad de México en `collector.py`.

## Fuentes y filtrado

- Feeds RSS de blogs, canales de YouTube (`/feeds/videos.xml`) y búsquedas RSS de Google News.
- `fetch_feed()` descarga a mano con bypass SSL, descompresión gzip/deflate y parseo con `feedparser`.
- `KEYWORDS` incluye: virtual commissioning, digital twin, simulation, factory, robot, robotics, plc, automation, opc ua, industrial, intralogistics, material handling, tia portal, omniverse.
- Para agregar un competidor o tema: edita `COMPETITOR_FEEDS` / `BUSINESS_KEYWORD_FEEDS` en `config.py`.

## Salidas generadas

| Archivo | Formato | Contenido |
|---------|---------|-----------|
| `business_intelligence_brief.md` | Markdown | Encabezado `Generated: … (Mexico City)`; secciones Business Keywords / Competitors, agrupadas por tema; filas fallback marcadas _(last seen)_ |
| `business_intelligence_brief.csv` | CSV | columnas: section, topic, title, summary, published, link, source_url (`published` en hora de Ciudad de México) |
| `docs/index.html` | HTML estático | Encabezado `Updated: … (Mexico City)`; mismos datos con UI dark-mode; filas fallback etiquetadas "Last seen" |
| `data/seen.json` | JSON | Estado de deduplicación (se muta en cada corrida) |
| `data/latest_by_topic.json` | JSON | Artículo más reciente por tema (se muta en cada corrida) |

Si un tema no tiene artículos nuevos ni un último artículo guardado, se omite. Si el brief queda vacío, los reportes dicen *"No relevant articles available."*

## Cómo correrlo en local

```bash
python -m pip install -r requirements.txt
python competitor_monitor.py
```

Requiere internet de salida (feeds externos). Vista previa de la página:

```bash
python -m http.server 8000
# Abrir http://localhost:8000/docs/index.html
```

## CI / GitHub Actions

Workflow: `Daily Business Intelligence Brief`

- **Schedule:** `0 12 * * *` (UTC)
- **Dispatch manual:** input `reset_seen` (boolean) — vacía `data/seen.json` antes de generar
- **Auto-commit** de: `business_intelligence_brief.md`, `.csv`, `data/seen.json`, `data/latest_by_topic.json`, `docs/index.html`
- Mensaje de commit: `chore: update daily business intelligence brief`

## Gotchas importantes

1. **Correr el script muta archivos rastreados.** Si solo pruebas el entorno, restaura después:
   ```bash
   git checkout -- business_intelligence_brief.md business_intelligence_brief.csv docs/index.html data/seen.json data/latest_by_topic.json
   ```
2. **`seen.json` ya tiene historial amplio** — una corrida normal suele reportar `0 new posts`, pero los temas siguen mostrando su último artículo vía `latest_by_topic.json`. Para forzar un dump de "nuevos", vacía seen (`echo "{}" > data/seen.json`), corre, y restaura (o usa `reset_seen` en Actions).
3. **Layout modular** — la lógica está en módulos planos en la raíz; `competitor_monitor.py` solo orquesta.
4. **No commitees cambios accidentales de datos** — las salidas las actualiza el CI; editar el brief a mano suele ser ruido.

## Tareas comunes

| Tarea | Dónde cambiar |
|-------|----------------|
| Agregar competidor / feed | `COMPETITOR_FEEDS` en `config.py` |
| Agregar tema de negocio | `BUSINESS_KEYWORD_FEEDS` en `config.py` |
| Ajustar filtro de relevancia | lista `KEYWORDS` en `config.py` |
| Cambiar la descarga de feeds | `feeds.py` |
| Cambiar recolección / dedup / fallback | `collector.py` |
| Cambiar zona horaria / formato de fecha | `datetime_utils.py` |
| Cambiar estilos HTML | bloque CSS inline en `writers.py` |
| Cambiar horario del CI | cron en `daily_business_brief.yml` |
| Cambiar dependencias | `requirements.txt` |
