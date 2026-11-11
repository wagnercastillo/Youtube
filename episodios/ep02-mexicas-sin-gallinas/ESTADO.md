# Estado EP02 (2026-11-05)

Hecho: guion v2, voces, escenas, subtítulos, SFX, revisión, render (renders/ep02-mexicas-sin-gallinas.mp4, 50 s).

Guion v2 (aprobado): Crono llega a Tenochtitlan en 1500 y pide huevos de gallina → no hay, llegan con los
españoles → comen huevos de guajolota (totoltetl = piedra de guajolota) → Totola no le da los suyos, lo manda
al lago por ahuautle → caviar mexicano ~50 USD/kg → "eres una gallina" → "¡eso dijeron los españoles!
Gallina de la tierra". Texto con etiquetas de actuación en audio/gen_audio_el.py (SCRIPT).

Voces: ElevenLabs Voice Design (plan gratis, guardadas en la cuenta): Crono yG52fI8LU4PPVgvtNLWz,
Totola C6N4cAUUGz4weG5XHekn. Modelo eleven_v3.

Pipeline voz (en orden):
1. `~/.chatterbox-py/Scripts/python.exe -I audio/gen_audio_el.py`  (cache en audio/el_v3/; borrar para regenerar)
2. `python -I audio/remap.py`  (escenas desde audio/bak/*.html.txt; ANCHORS y EVENTS = qué pasa en qué palabra)
3. `python -I audio/build.py`  (subtítulos + boca)

Respaldo voz vieja: audio/voz_chatterbox.wav, assets/lines_chatterbox.json, audio/transcript_chatterbox.json.
Pendiente: música.

2026-11-05 (tarde): inicio reencuadrado (Crono centrado, cámara 1.2; sale a la izquierda en 4.6 s), cierre a dos personajes
(cámara 1.1 en 45.88 s) y tarjeta final "PURO CHISME" 48.55–52 s. Duración 52 s.
OJO: remap.py parte de audio/bak/*.html.txt (versión anterior) y BORRA estos cambios. Respaldo previo en
audio/bak/stage_pre_endcard.html.txt; si se regenera la voz, actualizar los bak con stage.html actual antes de remap.
Miniatura v2 (2026-11-11, episodios/miniaturas.py) SUBIDA por API con set-thumbnail.ts.
