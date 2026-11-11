# Estado EP03 (2026-11-05)

Hecho: guion, voces nuevas (ElevenLabs Voice Design por API), voz, música (Eleven Music), efectos (ElevenLabs SFX),
escenas, subtítulos, revisión, render → renders/ep03-napoleon-bajito.mp4 (47 s, 1080×1920).

Pipeline (en orden):
1. `python -I audio/design_voices.py`  (ya hecho: audio/voices.json → napo 1YKZME5DvAy6a7RWNPMw, gill KWetGUahnofEBz9CSrjF)
2. `~/.chatterbox-py/Scripts/python.exe -I audio/gen_audio_el.py`  (cache audio/el/; el guion está en SCRIPT)
3. `python -I audio/gen_music_sfx.py`  (assets/music.mp3, assets/sfx/el_*.mp3)
4. `python -I audio/build.py`  (subtítulos + boca)
Si cambia la voz, los tiempos de compositions/stage.html (flips, pops, CAM, NKEYS/GKEYS) e index.html (sfx) se ajustan a mano.

Notas: la cuenta de ElevenLabs rechazó pcm_44100 ("solo Pro"), así que la voz va a 24 kHz.
Verificación: la voz se transcribió con Parakeet y coincide palabra por palabra con el guion.

## Para subir
Título: ¿Napoleón era BAJITO? 🤔 El chisme que inventaron los ingleses #shorts
Descripción:
Napoleón medía 5 pies 2 pulgadas… pero pulgadas FRANCESAS 📏 En realidad medía cerca de 1.68 m, normal para un francés de su época.
El mito lo regaron las caricaturas británicas, como las de James Gillray ("Little Boney"). Y "le petit caporal" era un apodo de cariño de sus soldados.

¿Te sabías este chisme? 👇
📅 Shorts nuevos lunes, miércoles y viernes.

Fuentes:
• Encyclopaedia Britannica, "Was Napoleon short?"
• History.com, "Napoleon complex"

#historia #napoleon #datoscuriosos #chisme #purochisme #historiauniversal
Etiquetas: napoleón, napoleon bonaparte, historia, francia, mitos de la historia, datos curiosos, chisme histórico, historia animada
Lista: Chismes de la historia · No es para niños · Contenido alterado: No (animación)
Miniatura v2 (2026-11-11, episodios/miniaturas.py) SUBIDA por API con set-thumbnail.ts.
