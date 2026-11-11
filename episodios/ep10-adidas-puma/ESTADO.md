# EP10 — "Adidas y Puma: hermanos que se odiaban" (2026-11-07)

**v2 (2026-11-07, Windows):** el owner vio la v1 repetitiva y básica → `blender/escena.py` reescrito con 6 sets separados
(gancho con focos, lavandería interior con rayos de luz, estadio 1936 con público, pueblo de noche en guerra + refugio
interior, pueblo de día partido, cementerio con niebla y luna) + cortes de cámara, materiales artesanales (veta, fieltro,
relieve), cielo degradado por escena, motion blur (apagado en los cortes), cejas/parpadeos. Voz, música, SFX y rótulos sin
cambios. Skills instaladas (arjun988/blender-skills): camera-cinematography, lighting, stop-motion-craft-style,
set-dressing, animation, compositing. Render Blender 5.2 EEVEE en RTX 5070: ~1.75 s/cuadro (~55 min).
Formato NUEVO: primer video hecho en BLENDER. Diorama de juguete 3D (EEVEE): pueblo miniatura sobre una tabla redonda partida
por un río (norte = Adi/azul, sur = Rudi/rojo), muñequitos de madera tipo peg, profundidad de campo tipo tilt-shift. Todo
desde código (`blender/escena.py`) y anclado a palabras con W()/L(): la cámara viaja casa-lavandería → estadio (Owens, 4 oros)
→ refugio (bombardeo) → la tabla se parte en dos y suben las fábricas → bares/panaderías/canchas por bando → cementerio de
noche (tumbas en extremos opuestos) → amanece, las mitades se juntan, partido mixto (2009). Sin logos de marca.
Encima, en HyperFrames: gancho desde el cuadro 0, rótulos tipo etiqueta con máscara (clip-path), subtítulos, tarjeta final.
Estructura: narradora comadre + diálogo de los hermanos en el refugio.
Voces (ElevenLabs en 10/10, se reutilizan): narradora comadre EP05 (FD4Jk3fxMZePximsMP5M), Adi = Gillray EP03
(KWetGUahnofEBz9CSrjF), Rudi = Napoleón EP03 (1YKZME5DvAy6a7RWNPMw). TEMPO 1.17 (guion de 74 s → 61.3 s).
Voz verificada con `hyperframes transcribe`: coincide con el guion.

Datos verificados: taller en la lavandería de la madre (años 20, Herzogenaurach); Owens usó spikes Dassler en Berlín 1936 y
ganó 4 oros; pleito en el refugio durante un bombardeo (1943 según la mayoría; Adi dijo que hablaba de los aviones — versión
disputada, por eso "juraba"); separación 1948 (Adidas registrada en 1949; Puma empezó como "Ruda"); cada uno a un lado del
río Aurach; pueblo dividido (bares, panaderías, clubes de fútbol) = "town of bent necks"; tumbas en extremos opuestos del
cementerio; partido de reconciliación entre empleados en 2009 (Día Internacional de la Paz).

## Pipeline
1. `~/.chatterbox-py/bin/python -I audio/gen_audio_el.py` → assets/voz.wav, lines.json, mouth.json, transcript.json
2. `python3 -I audio/gen_music_sfx.py` (polka bávara + SFX) · `python3 -I audio/build.py` (subtítulos)
3. `blender -b -P blender/escena.py -- still 0.5,20,40` (revisar) → `-- render` (PNG en blender/frames, ~1.3 s/cuadro en M4)
4. `ffmpeg -framerate 30 -i blender/frames/f%05d.png -c:v libx264 -pix_fmt yuv420p -crf 16 assets/blender.mp4`
5. `python3 -I audio/build_index.py` → compositions/overlay.html + index.html · `npm run check` · `npm run render`

## Para subir (youtube_description.txt, youtube_tags.txt)
Título: Dos hermanos se odiaron tanto… que crearon Adidas y Puma 👟💔
Render: renders/ep10-adidas-puma.mp4 (v2, 65.4 s, mean −14.8 dB, max −1.1 dB). Pendiente: subir privado y programar (falta token OAuth en este Mac).

SUBIDO 2026-11-07 (cola): https://youtu.be/pDipjdlz8tI · publishAt 2026-11-10T18:00:00Z · update ok
Miniatura v2 (2026-11-11, episodios/miniaturas.py) SUBIDA por API con set-thumbnail.ts.
