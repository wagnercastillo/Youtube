# EP05 — "¿Una guerra por pasteles?" (2026-11-06)

Formato NUEVO (distinto de EP02–EP04): pinturas reales de dominio público en una galería de museo (marco dorado, pared
burdeos, cartela con autor y año), Ken Burns lento sin temblores, y "LA CUENTA DEL CHISME": un ticket que imprime un renglón
por dato y cierra con "TOTAL: 1 PIERNA" + sello ¡PAGADO!. Narradora: comadre chismosa (casting medido, narr FD4Jk3fxMZePximsMP5M).
Render: renders/ep05-guerra-pasteles.mp4 (64.5 s, 1080×1920). Constantes de marca: gancho, subtítulos, tarjeta final.

Datos verificados: Remontel (Tacubaya, 1828) pidió 60 000 pesos por un local de < 1 000; Francia exigió 600 000 (1838),
bombardeó San Juan de Ulúa / Veracruz; Santa Anna perdió la pierna izquierda (5 dic 1838); funeral con honores (1842);
turba la desentierra (1844); su prótesis fue capturada por soldados de Illinois (1847) y está en el Illinois State Military Museum.
Imágenes y licencias: assets/img/CREDITS.md.

Pipeline:
1. `~/.chatterbox-py/Scripts/python.exe -I audio/audition.py` (casting; ya hecho)
2. `~/.chatterbox-py/Scripts/python.exe -I audio/gen_audio_el.py` (TEMPO 1.1 con atempo; l9 en estabilidad 0.5)
3. `python -I audio/gen_music_sfx.py` (música 68 s, efectos)
4. `python -I audio/build.py` (subtítulos) → `python -I audio/build_video.py` (stage.html + index.html atados a palabras)
5. `npm run check` → `npm run render`

## Para subir (archivos listos: youtube_description.txt, youtube_tags.txt)
Título: ¿Una GUERRA por PASTELES? 🥐💥 Le costó una pierna a Santa Anna
Categoría 27 · No es para niños · Contenido alterado: No · Lista: Chismes de la historia

Publicado 2026-11-06: https://youtu.be/GkWldQHAopY (público, categoría 27, es-419, 14 etiquetas).
