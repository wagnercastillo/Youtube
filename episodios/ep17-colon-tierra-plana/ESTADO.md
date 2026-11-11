# EP17-COLON-TIERRA-PLANA — "¿Colón descubrió que la Tierra era REDONDA? ¡Mentira! 🌍" (2026-11-11)
Formato NUEVO: COLLAGE DE RECORTES estilo Gilliam (canvas). Cabezas = retratos reales de dominio público (Piombo/Met, Brady/LoC, Durero) recortados con borde de papel; mandíbula = mitad inferior del retrato, abre a bisagra en 3 poses desde mouth.json. Estructura: careo narradora vs Colón vs Irving. Voces nuevas: narr "comadre_0", colon "capitan_0", irving "dandy_0".
Pipeline: audition.py → gen_audio_el.py (TEMPO 1.25, OVERRIDE estabilidad 0.5 en l0 y l2) → gen_music_sfx.py → build.py → build_video.py → check → render.
Render: renders/ep17-colon-tierra-plana.mp4 (64.7 s, 1080×1920 30 fps, mean −16.1 dB, max −1.0 dB). Miniatura: renders/miniatura.jpg ("¡MENTIRA!").
Voz verificada con hyperframes transcribe (diferencias solo de formato de números).

Cambios vs SPEC: guion recortado de 238 a 172 palabras (v1 daba 93 s de voz); mismos 6 datos del GOAL. Eratóstenes, sabios, barco y América dibujados (sin imagen). Globo de Behaim y mapa de Cantino reemplazados por mapas dibujados.
Voces borradas para liberar slots (regla 2026-11-07): EP14 narr, EP14 aleman, EP15 reporter (audio cacheado en sus audio/el/).
Fuentes de imágenes: assets/recortes/fuentes.json.

## Para subir
Título: ¿Colón descubrió que la Tierra era REDONDA? ¡Mentira! 🌍
PENDIENTE: subida bloqueada 2026-11-11 14:30Z (TLS "self-signed certificate": VPN encendida). Apagar VPN y correr:
  cd ~/.claude/skills/youtube-uploader/scripts
  npx ts-node list-videos.ts   # ver slots ocupados
  npx ts-node youtube-upload.ts --video <ep>/renders/ep17-colon-tierra-plana.mp4 --title "¿Colón descubrió que la Tierra era REDONDA? ¡Mentira! 🌍" --description-file <ep>/youtube_description.txt --category 27 --privacy private
  npx ts-node update-video.ts <id> <ep>/youtube_description.txt 27 <ISO 02:00Z siguiente 8 pm libre> <ep>/youtube_tags.txt
  npx ts-node set-thumbnail.ts <id> <ep>/renders/miniatura.jpg
SUBIDO 2026-11-11: https://youtu.be/avW7wJMxa2o · publishAt 2026-11-12T02:00:00Z (8:00 pm CDMX mié 11) · tags + miniatura ok
