# AGENTS.md

Guía de contexto para agentes de IA. Consulta este archivo antes de explorar el repositorio completo.

## Qué es este proyecto

Monitor diario de inteligencia competitiva en **automatización industrial** (virtual commissioning, digital twin, simulación PLC/robots, intralogistics). Un único script Python recopila noticias de feeds RSS, Google News y YouTube, filtra por palabras clave, evita duplicados y genera informes.

**Script principal:** `competitor_monitor.py`  
**Automatización:** GitHub Actions (`.github/workflows/daily_business_brief.yml`) — corre diario a las 12:00 UTC (~06:00 Ciudad de México) y puede dispararse manualmente.

## Estructura del repositorio

```
competitor_monitor.py          # Lógica completa del job (único archivo de código)
requirements.txt               # feedparser>=6.0.11
.github/workflows/
  daily_business_brief.yml     # CI: instala deps, ejecuta script, commitea outputs
data/
  seen.json                    # Historial de links vistos (deduplicación)
docs/
  index.html                   # Página estática estilizada (GitHub Pages)
business_intelligence_brief.md # Informe legible en Markdown
business_intelligence_brief.csv# Exportación estructurada
README.md                      # Documentación para humanos
```

No hay tests, linter ni configuración de formateo.

## Flujo de datos

1. **Carga** `data/seen.json` — dict `{ "section:topic": [link, ...] }`.
2. **Recorre dos grupos de feeds:**
   - `COMPETITOR_FEEDS` — NVIDIA, RoboDK, Siemens, Visual Components, Rockwell/Emulate3D, AnyLogic, F.EE.
   - `BUSINESS_KEYWORD_FEEDS` — Virtual Commissioning, Digital Twin, PLC Simulation, Robot Simulation, Intralogistics Simulation (vía Google News RSS).
3. **Por cada entrada:** salta si el link ya está en `seen`, descarta si título+resumen no contienen ninguna de `KEYWORDS`.
4. **Escribe outputs** con solo las entradas **nuevas** de esta ejecución (no un histórico acumulado).
5. **Persiste** `seen.json` actualizado.

## Fuentes y filtrado

- Feeds directos de blog RSS, feeds de canal YouTube (`/feeds/videos.xml`) y búsquedas Google News RSS.
- `_fetch_feed()` hace fetch manual con SSL bypass, descompresión gzip/deflate y parseo con `feedparser`.
- `KEYWORDS` incluye: virtual commissioning, digital twin, simulation, factory, robot, plc, automation, opc ua, industrial, intralogistics, material handling, tia portal, omniverse.
- Para añadir un competidor o tema: editar los dicts `COMPETITOR_FEEDS` / `BUSINESS_KEYWORD_FEEDS` al inicio de `competitor_monitor.py`.

## Outputs generados

| Archivo | Formato | Contenido |
|---------|---------|-----------|
| `business_intelligence_brief.md` | Markdown | Secciones Business Keywords / Competitors, agrupadas por topic |
| `business_intelligence_brief.csv` | CSV | columnas: section, topic, title, summary, published, link, source_url |
| `docs/index.html` | HTML estático | Misma info con UI dark-mode; enlaces a .md y .csv |
| `data/seen.json` | JSON | Estado de deduplicación (mutado en cada run) |

Si no hay artículos nuevos, los informes dicen *"No new relevant articles found."*

## Ejecución local

```bash
python -m pip install -r requirements.txt
python competitor_monitor.py
```

Requiere acceso a internet (feeds externos). Vista previa de la página:

```bash
python -m http.server 8000
# Abrir http://localhost:8000/docs/index.html
```

## CI / GitHub Actions

Workflow: `Daily Business Intelligence Brief`

- **Schedule:** `0 12 * * *` (UTC)
- **Manual dispatch:** input `reset_seen` (boolean) — vacía `data/seen.json` antes de generar
- **Commit automático** de: `business_intelligence_brief.md`, `.csv`, `data/seen.json`, `docs/index.html`
- Mensaje de commit: `chore: update daily business intelligence brief`

## Gotchas importantes para agentes

1. **Ejecutar el script modifica archivos trackeados.** Si solo pruebas el entorno, restaura después:
   ```bash
   git checkout -- business_intelligence_brief.md business_intelligence_brief.csv docs/index.html data/seen.json
   ```
2. **`seen.json` ya tiene historial extenso** — un run normal suele reportar `0 new posts`. Para ver output poblado, resetea temporalmente (`echo "{}" > data/seen.json`), ejecuta y restaura (o usa `reset_seen` en Actions).
3. **No hay capa de abstracción** — todo vive en un solo script procedural (~400 líneas). No busques paquetes, módulos ni API.
4. **No commitear cambios de datos accidentales** — los outputs se actualizan automáticamente por CI; cambios manuales al brief suelen ser ruido.
5. **`data/latest_by_topic.json`** existe en el repo pero **no es usado** por el script actual; ignóralo salvo que se integre explícitamente.

## Tareas comunes

| Tarea | Dónde actuar |
|-------|--------------|
| Añadir competidor / feed | `COMPETITOR_FEEDS` en `competitor_monitor.py` |
| Añadir tema de negocio | `BUSINESS_KEYWORD_FEEDS` |
| Ajustar filtro de relevancia | lista `KEYWORDS` |
| Cambiar estilo HTML | bloque CSS inline en `competitor_monitor.py` (~línea 319) |
| Cambiar horario CI | cron en `daily_business_brief.yml` |
| Cambiar dependencias | `requirements.txt` |
