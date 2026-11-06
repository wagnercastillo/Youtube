# EP06 — "¿Quién da más por Yucatán?" (2026-11-06)

Formato NUEVO: primer video 3D del canal. Mapa de México extruido en Three.js 0.159 dentro de HyperFrames (dibujado solo desde
hf-seek, determinista: dos seeks al mismo segundo difieren ≤1 nivel en pocos píxeles). Estructura: SUBASTA ("¡Se vende península!")
con un merolico (casting medido, narr ZDGUr0IFu8PtJsGTXKMS); postores con banderas y sellos NO; cierre ¡VENDIDA! con mazo.
Tema elegido por research/outliers.py: las historias de MAPAS DE MÉXICO son el grupo de Shorts que más supera a su canal.
Render: renders/ep06-yucatan-subasta.mp4 (50.4 s).

Datos verificados: República de Yucatán (1841); Guerra de Castas (1847, rebeldes cerca de Mérida en 1848); ofrecimiento de
soberanía a EE. UU., Inglaterra y España (25 mar 1848); mensaje de Polk al Congreso (29 abr 1848), nadie aceptó;
reincorporación a México (17 ago 1848) con ayuda para la guerra.

Pipeline: audition.py → gen_audio_el.py → gen_music_sfx.py → build_geo.py (geoBoundaries → assets/geo/mexico_shapes.json)
→ build.py (subtítulos) → build_video.py (stage 3D + index, tiempos por palabra) → npm run check → npm run render.

## Para subir (youtube_description.txt, youtube_tags.txt)
Título: Yucatán se ofreció a otros países… y NADIE lo quiso 🗺️🔨

Subido 2026-11-06 y PROGRAMADO: https://youtu.be/-0FNeL8xsq8 · se publica 2026-11-07T01:00:00Z (hoy 7:00 pm CDMX / 8:00 pm Ecuador).
