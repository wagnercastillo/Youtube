---
name: produccion-nocturna
description: Producción nocturna autónoma de Puro Chisme — investiga, produce, renderiza, verifica y programa en YouTube los 3 Shorts del día siguiente (12 pm, 4 pm, 8 pm CDMX) sin preguntar nada. Úsala cuando la invoque el script nocturno (mac/nightly/run_nightly.sh) o cuando el dueño diga "haz los videos de mañana", "producción nocturna" o "/produccion-nocturna".
---

# Producción nocturna (sin supervisión)

Corres solo, de noche, sin nadie que conteste. **Nunca preguntes**: decide con las reglas del repo y deja todo anotado.
El dueño revisa por la mañana; cada video queda PRIVADO con `publishAt`, así que puede cancelarlo antes de que salga.

## 0. Antes de empezar
1. `git pull` en la raíz del repo. Lee `CLAUDE.md` completo y la memoria del proyecto (MEMORY.md y sus archivos).
2. Si existe `mac/nightly/PAUSA`, escribe en el reporte "pausado por el dueño" y termina.
3. Calcula la fecha objetivo = el día de hoy en CDMX (UTC−6) si aún no son las 11 am CDMX; si ya pasaron, mañana.
   Turnos: 12:00 pm = `T18:00:00Z`, 4:00 pm = `T22:00:00Z`, 8:00 pm = `T02:00:00Z` del día siguiente (UTC).
4. Revisa qué turnos de esa fecha ya están ocupados en `ideas/PUBLICADOS.md` (créalo si no existe: tabla
   fecha | turno | episodio | videoId | título). Solo llena los turnos libres (máximo 3 videos por noche).
5. Comprueba la conexión: `curl -s -o /dev/null -w "%{remote_ip}" https://youtube.googleapis.com/` debe responder una IP de
   Google (no 100.x). Si no, produce igual pero NO subas; anótalo en el reporte.

## 1. Elegir 3 temas distintos
- Lee los `SPEC.md`/`ESTADO.md` de los últimos 6 episodios e `ideas/PUBLICADOS.md` para no repetir tema, formato ni voz.
- Rota regiones (Europa, Asia, África, Oceanía, LatAm sin México, EE. UU.); México solo cada 4–5 videos.
- Cada uno de los 3 videos de la noche usa un FORMATO distinto entre sí y distinto de los 3 anteriores
  (caricatura 2D con diálogo, pinturas reales, Manim, mapa 3D, híbrido 3D+2D, chat de celular, pixel art, noticiero,
  transmisión deportiva, gráfica de bolsa, tienda en línea, tablero de detective, quiz… o uno nuevo).
- Opcional: `python -I research/outliers.py "<tema>" --days 30` para ver qué está pegando.
- **Verifica cada dato con WebSearch** (2 fuentes serias). Si un dato es discutido, dilo como "según algunas crónicas" o quítalo.
  El tema más fuerte de la noche va al turno de las 8 pm.

## 2. Producir cada episodio (pipeline de CLAUDE.md, referencia: el episodio más reciente de ese formato)
1. Carpeta `episodios/epNN-slug/` (siguiente número libre), copiando la estructura del episodio más parecido.
2. Guion 45–60 s: gancho ≤1.5 s con pregunta grande, tono de chisme, cierre que haga loop. Voces: `audio/voices.json`.
   ElevenLabs tiene límite de 10 voces propias: reutiliza voces aprobadas (narradores de EP04/EP05/EP06/EP07) en vez de
   diseñar nuevas; si diseñas, no borres voces existentes.
3. `gen_audio_el.py` → transcribe (`npx hyperframes transcribe assets/voz.wav -l es -d audio/tr`) y compara con el guion;
   regenera con stability 0.5 cualquier línea que se coma palabras. `gen_music_sfx.py`, `build.py`, `build_video.py`.
4. Aplica las 5 reglas de motion (máscara, encadenar, cámara sigue, transformar objeto, sync con W()) y las reglas
   "Nunca" (sin line boil ni temblor constante; música ≈12 dB bajo la voz).
5. `npx hyperframes check` sin errores → `snapshot` de 8–12 momentos y **míralos**; corrige textos cortados, solapes y
   escenas vacías → `npm run render` → renombra a `renders/<slug>.mp4` → `ffmpeg volumedetect` (media ≈ −14 a −16 dB).
6. Miniatura vertical 1080×1920 (`_thumb.html` + Chrome headless) en `renders/miniatura.jpg`.
7. `youtube_description.txt` (con fuentes), `youtube_tags.txt`, `ESTADO.md`.

## 3. Subir y programar
Desde `~/.claude/skills/youtube-uploader/scripts` (rutas de archivos, nunca texto multilínea en argumentos):
1. `npx ts-node youtube-upload.ts --video <mp4> --description-file <desc> --category 27 --privacy private --title "<título>"`
2. `npx ts-node update-video.ts <id> <desc> 27 <ISO del turno> <tags>` y `npx ts-node check-video.ts <id>`
   (debe decir private + publishAt correcto).
3. `npx ts-node set-thumbnail.ts <id> renders/miniatura.jpg` (si responde sin permisos, anótalo: el dueño la pone a mano).
4. Añade la fila a `ideas/PUBLICADOS.md` y la URL al `ESTADO.md` del episodio.
Si algo falla en un episodio, NO lo subas a medias: déjalo en su carpeta con el motivo en `ESTADO.md` y sigue con el siguiente.

## 4. Cerrar la noche
1. `git add -A && git commit` (mensaje: "nocturno AAAA-MM-DD: epNN, epNN, epNN") y `git push`. Nunca subas `.env` ni tokens.
2. Escribe `reportes/AAAA-MM-DD.md`: por video → título, formato, región, turno, URL, verificación de voz, volumen,
   miniatura (sí/no), y cualquier problema o decisión dudosa. Ese reporte es lo que el dueño lee al despertar.
3. Si aprendiste algo que sirva para las siguientes noches, actualiza la memoria del proyecto.

## Nunca
- Publicar público directo: siempre privado + `publishAt`.
- Borrar videos, voces o archivos del dueño; desactivar verificación TLS; poner claves en el repo o en el chat.
- Repetir tema o formato de los últimos videos; afirmar datos sin fuente.
