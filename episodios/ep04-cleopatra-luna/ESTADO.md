# EP04 — "Cleopatra, más cerca de la Luna que de las pirámides" (2026-11-05)

Formato NUEVO (distinto de EP02/EP03): explicador con Manim, una narradora (sin personajes), línea del tiempo vertical
en papiro (Impact + Georgia, oro/lapislázuli/terracota). Render: renders/ep04-cleopatra-luna.mp4 (50.7 s, 1080×1920).
v3 (2026-11-05): narrador masculino elegido por casting medido (audio/audition.py → narr uiAksityc3aBuAQ4bjSW), mp3 44.1 kHz + EQ de presencia, estabilidad 0.0 (l2 en 0.5). Video 50.7 s. Música 64 s a 0.38
(≈12 dB bajo la voz) y 0.8 en la tarjeta final. Manim e index.html leen los tiempos de transcript.json (W/L por palabra):
si cambia la voz, solo se re-ejecuta el pipeline.

Datos (verificados): Gran Pirámide ≈ 2560 a.C.; Cleopatra muere 30 a.C.; Luna 1969 → 2530 vs 1998 años (sin año cero).
Últimos mamuts: isla de Wrangel, ≈ 2000–1650 a.C. (fechas por radiocarbono; las fuentes varían).
Voz verificada con Parakeet: coincide con el guion.

Pipeline:
1. `python -I audio/design_voices.py` → audio/voices.json (narr AgGhWpMLnU7pTuMeN2UG)
2. `~/.chatterbox-py/Scripts/python.exe -I audio/gen_audio_el.py` → assets/voz.wav, lines.json, transcript.json
3. `python -I audio/gen_music_sfx.py` → assets/music.mp3 (61 s), assets/sfx/el_*.mp3
4. `cd manim && ~/.manim-py/Scripts/manim.exe script.py EP04` → copiar media/videos/script/1920p30/EP04.mp4 a assets/manim.mp4
   (cada aparición está atada a una palabra con at(W(...)); se re-sincroniza sola)
5. `python -I audio/build.py` (subtítulos) + `python -I audio/build_index.py` (index.html y efectos) → `npm run render`
Sin temblores ni line boil.

## Para subir
Título: Cleopatra vivió más cerca de la LUNA que de las pirámides 🤯 #shorts
Descripción:
La Gran Pirámide se terminó por ahí del 2560 a.C. Cleopatra murió en el 30 a.C. Entre las dos: unos 2 500 años.
Entre Cleopatra y la llegada a la Luna (1969): menos de 2 000 🌙
Y cuando terminaron la pirámide… todavía había mamuts vivos en la isla de Wrangel, en el Ártico 🦣

¿Antigua para quién? 👇
📅 Shorts nuevos lunes, miércoles y viernes.

Fuentes:
• Encyclopaedia Britannica: Great Pyramid of Giza; Cleopatra
• Vartanyan et al., Nature (1993) y estudios posteriores sobre los mamuts de la isla de Wrangel

#historia #cleopatra #egipto #piramides #datoscuriosos #chisme #purochisme
Etiquetas: cleopatra, pirámides de egipto, gran pirámide de guiza, llegada a la luna, mamuts, historia antigua, datos curiosos, línea del tiempo
Lista: Chismes de la historia · No es para niños · Contenido alterado: No (animación)
