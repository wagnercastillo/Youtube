# EP10 — "Le dijo QUÍTATE a Alejandro Magno" (2026-11-07)

Ver SPEC.md. Pipeline:
1. `~/.chatterbox-py/Scripts/python.exe -I audio/gen_audio_el.py` (TEMPO 1.1; cache audio/el/)
2. `python -I audio/gen_music_sfx.py` → `python -I audio/build.py` → `python -I audio/build_video.py`
3. `npm run check` → `npm run render` → renombrar a renders/ep10-diogenes-alejandro.mp4

Render: renders/ep10-diogenes-alejandro.mp4 (62.9 s, 1080×1920, mean −15.4 dB, max −1.0 dB). Miniatura: renders/miniatura.jpg (cuadro 34.3 s, "¡QUÍTATE!").
Verificación de voz: transcripción Parakeet (audio/tr/) coincide con el guion palabra por palabra.

Datos verificados (Diógenes Laercio VI, trad. Hicks; Plutarco, Alejandro 14): tinaja (6.23), "el Perro" (6.60), pollo
desplumado a Platón (6.40), "quítate, me tapas el sol" en el Craneo de Corinto (6.38), burlas de los acompañantes y
"si no fuera Alejandro, sería Diógenes" (Plutarco 14; DL 6.32), muerte el mismo día (DL 6.79, según Demetrio → "dicen que").

## Para subir (youtube_description.txt, youtube_tags.txt)
Título: Le dijo QUÍTATE a Alejandro Magno 😳☀️
2026-11-07 00:25Z: la API respondió "The user has exceeded the number of videos they may upload" (límite diario del canal).
PENDIENTE: subir cuando se libere (~24 h) y programar en el siguiente turno libre (previsto: 2026-11-07T18:00:00Z = sáb 12 pm CDMX,
si ya pasó, el siguiente libre):
  cd ~/.claude/skills/youtube-uploader/scripts
  npx ts-node youtube-upload.ts --video <ep>/renders/ep10-diogenes-alejandro.mp4 --description-file <ep>/youtube_description.txt --category 27 --privacy private --title "Le dijo QUÍTATE a Alejandro Magno 😳☀️"
  npx ts-node update-video.ts <id> <ep>/youtube_description.txt 27 <ISO> <ep>/youtube_tags.txt
