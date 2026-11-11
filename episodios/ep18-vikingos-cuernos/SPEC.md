# EP18-VIKINGOS-CUERNOS — "¿Los vikingos usaban cascos con CUERNOS? ¡Mentira!"
Formato NUEVO: CUADERNO DE DIBUJO A MANO (skill `hand-drawn-canvas-animation`, Canvas 2D, poses dibujadas enteras, no rig de
óvalos). Primer episodio dibujado "a lápiz y tinta" del canal. Idea central: **lo que es mito se dibuja a LÁPIZ (se puede borrar);
lo que está comprobado se pasa a TINTA (ya no se borra).** La mano del dibujante entra a cuadro con lápiz, goma y plumón rojo.
Estructura NUEVA: EL DIBUJO DISCUTE CON SU DIBUJANTE. Un caricaturista chismoso (narrador) dibuja a Björn, un vikingo que EXIGE
sus cuernos; el narrador se los borra con evidencia. Cameo: Carl Emil Doepler, el vestuarista que los hizo famosos en 1876.
Región: Escandinavia / Alemania; nada de México.
Gancho del tipo ganador (memoria ganchos-ganadores): pregunta contraintuitiva + "¡Mentira!" sobre un mito escolar.

## Por qué este tema y este estilo (2026-11-11)
- EP03 (Napoleón bajito, 2.6K) y EP02 (mexicas sin gallinas, 1.6K) son los únicos claramente arriba de la base ~1.2K: desmentido de
  mito con pregunta en el título. "Vikingos con cuernos" lo tiene TODO el público (caricaturas, disfraces, logos), no hace falta
  saber historia para engancharse.
- Payoff doble: (1) el único casco vikingo casi completo no tiene cuernos; (2) los cuernos los hizo famosos un DISEÑADOR DE
  VESTUARIO de ópera en 1876, ~800 años después de los vikingos. Cierra en bucle: "¿tú también los dibujabas así?" y la mano
  vuelve a dibujarle los cuernos… y los borra otra vez.
- Estilo: el dibujo a mano encaja porque el mito se BORRA literalmente en pantalla (el acto de corregir es la animación).
  Ya usados y descartados: collage Gilliam (EP17), papel recortado (EP16), noticiero (EP15), tablero (EP14), tipografía (EP13),
  3D (EP12), caricatura plana SVG (EP11), pixel art (EP09), chat (EP08).

## GOAL
Hook en pantalla desde el cuadro 0: "¿LOS VIKINGOS USABAN CASCOS CON CUERNOS?" rotulado a mano (path lettering, no fuente web) sobre
Björn a lápiz CON cuernos; a ~1.3 s, la mano tacha con plumón rojo y escribe "¡MENTIRA!".
El espectador aprende: (a) el casco de Gjermundbu (Noruega, hallado en 1943, siglo X) es el único casco vikingo casi completo y no
tiene cuernos; (b) en batalla los cuernos estorbarían (opinión de historiadores, dicho como tal); (c) sí existen cascos con cuernos
en Escandinavia, los de Veksø (Dinamarca), pero son de la Edad de Bronce (~900 a. C.), unos 1,700 años antes de los vikingos, y
probablemente ceremoniales; (d) la imagen la popularizó Carl Emil Doepler, vestuarista del estreno de "El anillo del nibelungo" de
Wagner en Bayreuth, 1876 (antes ya la pintaban artistas románticos como Gustav Malmström).
Duración objetivo: voz 46–54 s + tarjeta final 4.5 s = 50–59 s.

## GUION (pegar en audio/gen_audio_el.py → SCRIPT; TEMPO 1.1; stability 0.0–0.3 según audición)
```python
SCRIPT = [
    ("l0", "narr",    "[excited] ¿Los vikingos usaban cascos con cuernos? ¡Mentira! Y el que se los puso… ni siquiera era vikingo."),
    ("l1", "bjorn",   "[proud] ¡Dibújamelos, compadre! Bien grandotes, para que me tengan miedo."),
    ("l2", "narr",    "[mischievously] Ahorita te los borro. En mil novecientos cuarenta y tres, en Noruega, desenterraron el único casco vikingo casi completo que existe. ¿Y cuántos cuernos tenía? Cero."),
    ("l3", "bjorn",   "[confused] ¿Cero? ¿Y entonces cómo asusto a la gente?"),
    ("l4", "narr",    "[laughs] Con el hacha, Björn. Además, los historiadores dicen que en plena batalla unos cuernos serían puro estorbo."),
    ("l5", "narr",    "[gossipy] Ojo: sí hay cascos con cuernos en Dinamarca… pero son de la Edad de Bronce. Mil setecientos años antes de los vikingos. Y eran para ceremonias, no para pelear."),
    ("l6", "narr",    "[dramatic] ¿Entonces quién los hizo famosos? Un diseñador de vestuario. Alemania, mil ochocientos setenta y seis: se estrena la ópera de Wagner, y Carl Emil Doepler les pone cuernos a sus guerreros."),
    ("l7", "doepler", "[smug] ¡Se veían divinos en el escenario! ¿Qué querían, que salieran con gorrito?"),
    ("l8", "narr",    "[mischievously] Y desde entonces, caricaturas, películas y disfraces… todos con cuernos. ¿Y tú? ¿También los dibujabas así?"),
]
```
Reglas: cada línea es una toma. Si eleven_v3 se come palabras (ojo con "Gjermundbu": NO se dice en voz, solo en pantalla), regenerar
esa línea con OVERRIDE (stability 0.5) como EP12/EP17. Verificar con `npx hyperframes transcribe` y comparar palabra por palabra.
"Björn" debe sonar "Biorn"; si sale raro, escribirlo "Biorn" solo en el texto de voz (el subtítulo conserva "Björn").

## VOCES (audio/audition.py; slots 10/10 → borrar antes voces de episodios ya renderizados y subidos, p. ej. EP14/EP15)
```python
ROLES = {
 'narr':    ('¿Los vikingos usaban cascos con cuernos? ¡Mentira! Y el que se los puso ni siquiera era vikingo.',
             {'caricaturista': 'Hombre mexicano de 30 años, caricaturista chismoso y bromista, voz clara y juvenil, rápida, con risa contenida, como contando un secreto mientras dibuja. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.',
              'dibujante': 'Hombre mexicano de 35 años, ilustrador pícaro y carismático, voz cálida y brillante, ritmo ágil con pausas de suspenso, muy expresivo. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.'}),
 'bjorn':   ('¡Dibújamelos, compadre! Bien grandotes, para que me tengan miedo. ¿Cero? ¿Y entonces cómo asusto a la gente?',
             {'grandote': 'Hombre mexicano de 40 años, guerrero grandote y bonachón, voz muy grave y retumbante, presumido pero ingenuo, cómico. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.',
              'ronco': 'Hombre mexicano de 45 años, voz ronca y fuerte de luchador, exagerado y berrinchudo como niño grande, divertido. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.'}),
 'doepler': ('¡Se veían divinos en el escenario! ¿Qué querían, que salieran con gorrito? El público quiere espectáculo.',
             {'vestuarista': 'Hombre mexicano de 55 años, diseñador de vestuario teatral, voz aguda, rápida y afectada, ofendido con elegancia, muy dramático. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.',
              'artista': 'Hombre mexicano de 60 años, artista de ópera vanidoso, voz nasal y cantarina, exagera cada palabra, cómico. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.'}),
}
```
Narrador HOMBRE a propósito (EP17 tuvo narradora). Doepler debe contrastar con Irving de EP17 (allí "dandy" meloso): aquí agudo y rápido.

## BRIEF DE LA SKILL (references/brief-template.md)
```text
Subject and emotional/action beat: un vikingo dibujado exige cuernos; la evidencia se los borra; acaba resignado con gorrito.
Duration; aspect; resolution: voz ~50 s (cues de transcript.json); 9:16; 1080×1920.
Drawing reference: caricatura de cuaderno de dibujante (bocetos de animador, líneas de construcción visibles en el lápiz).
Material reference: grafito sobre papel de sketchbook marfil + tinta china con pincel; acento único plumón rojo.
Look: pencil (mito) → ink (evidencia) · riso 2 tintas (l5, lámina de museo) · screen (l6–l7, cartel de ópera 1876).
Techniques: whole cels + assisted inbetweens; sin fotos (Gjermundbu y Veksø dibujados a tinta, no fotos con licencia dudosa).
Mixing looks, story reason: cada época se imprime en su medio (cuaderno → lámina de museo → cartel de teatro). Lo que cruza cada
  cambio: EL CASCO (mismo dibujo, misma posición en pantalla) — el casco de Björn pasa a tinta (l2), le crecen cuernos riso (l5),
  y esos cuernos se los pone Doepler al cantante del cartel (l6).
Palette/material bindings: papel #F2EADB (diente del papel = paper, fijo); grafito #4B4B52; tinta #1B1A20; rojo #D7263D (plumón,
  objeto); riso oro #E3A72F + azul #2A5DB0 (lámina); cartel crema #EFE4C8 / rojo #B5212F / negro (screen, solid).
Mark language: lápiz = pasadas finas interrumpidas + líneas de construcción; tinta = contorno con presión y punta afilada,
  achurado que sigue la forma del casco; zonas tranquilas en el fondo (el texto vive en los huecos).
Cast: Björn (barbón, trenzas, panza, silueta de pera; vistas 3/4 y frente; expresiones: orgulloso, confundido, berrinche,
  resignado con gorrito); la MANO del dibujante (lápiz / goma / plumón, 3 dibujos de agarre); Doepler (bigote de manubrio,
  monóculo, cinta métrica al cuello; frente; expresiones: ofendido, coqueto); cantante de ópera del cartel (silueta).
Drawing method: whole cels (cels.js, drawCel material pencil|ink); inbetweens asistidos solo en formas que corresponden.
Exposure: 24 fps; personajes en twos, berrinche de Björn en ones (l3), holds largos en lectura de texto; cámara en ones.
Hardest action: la GOMA borra los cuernos (l2 "Cero"): contacto goma-papel plantado, 3 pasadas de vaivén, migas que caen y
  rebotan una vez, el trazo del cuerno se aclara por pasada (no fade: máscara de borrado que sigue el recorrido de la goma);
  Björn hace "¿eh?" mirando hacia arriba a su casco.
Camera: dolly suave a quien habla (Björn izq., narrador = la mano / plano general, Doepler der.); sin temblor; un único
  sacudón ≤0.4 s en l3 (berrinche, cambio de humor).
Closing: la mano le vuelve a dibujar cuernos a Björn… duda… los borra; las migas de la goma se juntan y forman el logo →
  tarjeta final Puro Chisme (HyperFrames).
External sources/licences: ninguna imagen externa; todo dibujado en código.
```

## CUES (todo anclado con W(line, word) / L(line) desde transcript.json; tiempos solo como guía)
- **l0** (lápiz) cuadro 0: Björn a lápiz con cuernos enormes + rótulo "¿LOS VIKINGOS USABAN CASCOS CON CUERNOS?" (ya escrito).
  W(l0,"Mentira"): la mano entra con plumón rojo, tacha los cuernos con una X y escribe "¡MENTIRA!" (trazo revelado por máscara
  a lo largo del recorrido). W(l0,"vikingo"): la mano deja un "?" junto a una silueta de sombrero de copa (siembra a Doepler).
- **l1** (cámara a Björn): Björn infla el pecho, se señala los cuernos; W(l1,"grandotes"): el lápiz los hace el doble (redibujo, no escala).
- **l2** W(l2,"borro"): entra la goma. W(l2,"Noruega"): mini mapa a tinta de Noruega se dibuja en la esquina con punto rojo
  "1943". W(l2,"único"): el casco de Björn se pasa a TINTA: casco redondo con guarda-ojos (anteojera) tipo Gjermundbu, achurado;
  rótulo pequeño "Casco de Gjermundbu · siglo X". W(l2,"Cero"): LA GOMA BORRA LOS CUERNOS (acción difícil, ver brief); número
  "0" grande en rojo.
- **l3** (ones) Björn berrinche: patalea en 4 dibujos, se jala la barba; sacudón 0.4 s.
- **l4** W(l4,"hacha"): la mano le dibuja un hacha a tinta en un trazo; W(l4,"estorbo"): viñeta mini: un cuerno se atora en
  una rama/escudo y Björn gira cómicamente (3 dibujos), etiqueta "opinión de historiadores".
- **l5** TRANSICIÓN a RISO: la página gira como hoja de cuaderno y debajo hay una lámina de museo a 2 tintas; el casco ocupa
  la misma posición. W(l5,"Dinamarca"): par de cascos de Veksø (cuernos curvos, "ojos" y pico) se imprimen plancha por plancha
  (oro, luego azul, con registro estable). W(l5,"Bronce"): línea del tiempo a pincel: "~900 a. C." ←— 1,700 años —→ "793 d. C.
  vikingos" (la flecha se estira, la cámara la sigue). W(l5,"ceremonias"): sello "CEREMONIAL" en oro.
- **l6** TRANSICIÓN a SCREEN: los cuernos riso se desprenden de la lámina y vuelan a un cartel de teatro 1876 ("BAYREUTH 1876 ·
  DER RING DES NIBELUNGEN") que se arma por capas sólidas. W(l6,"vestuario"): cinta métrica se desenrolla y escribe el rótulo.
  W(l6,"Doepler"): Doepler entra a cuadro (der.) con tijeras y le pone los cuernos al cantante del cartel (contacto plantado).
- **l7** (cámara a Doepler) monóculo que brilla, se abanica con un boceto; W(l7,"gorrito"): aparece un gorrito tejido flotando.
- **l8** regreso al CUADERNO a lápiz: W(l8,"caricaturas"/"películas"/"disfraces"): tres viñetas rápidas de vikingos genéricos con
  cuernos (diseños originales, nada de personajes de marcas existentes) que se tachan en rojo una tras otra. W(l8,"dibujabas"):
  Björn con el gorrito tejido de l7, resignado; la mano le vuelve a dibujar cuernos… se detiene… y los borra. Migas → logo →
  tarjeta final Puro Chisme (logo con ojos que se asoman, "PURO CHISME", "¿A poco no sabías este chisme?", "SÍGUENOS PARA MÁS").

## REGLAS DEL CANAL APLICADAS
- Sin line boil: el lápiz/tinta se genera con seed fijo por dibujo; un dibujo sostenido conserva sus trazos (invariante de la skill).
  Nada de `boil()`. Sin temblor salvo el sacudón de l3.
- Máscara: rótulos y sellos se revelan siguiendo el trazo (stroke reveal) o con wipe; nunca fade.
- Encadenar: mano → trazo → reacción de Björn → rótulo, cada uno 0.1–0.2 s después del anterior.
- Cámara sigue: Björn izq. / mano centro / Doepler der.; dolly a la línea del tiempo en l5.
- Transformar objeto: casco lápiz → casco tinta (l2); casco → cascos de Veksø (l5); cuernos → cartel de ópera (l6); migas → logo (l8).
- Subtítulos de palabra resaltada en y≈1530 (HyperFrames, como siempre): la acción del dibujo vive en y < 1400.

## SONIDO
Voz 1.0. Eleven Music: "playful nordic folk with pizzicato strings, frame drum and tin whistle, cheeky and bouncy, 105 bpm,
no vocals" ≈ −12 dB bajo la voz (subir bajo la tarjeta final). SFX ElevenLabs: lápiz rasgando papel, goma frotando, plumón,
hoja de cuaderno que gira, sello, cuerno vikingo corto (solo en l0 al tachar, irónico), pataleo, tijeras, aplauso de teatro (l7).
Solo en acciones visibles.

## FUENTES (al pie del cuadro en l2/l5/l6 en letra pequeña y en la descripción)
- Casco de Gjermundbu (hallado en 1943, Buskerud, Noruega; siglo X; Museo de Historia Cultural, Oslo): Wikipedia «Gjermundbu helmet».
- Ausencia de cuernos en cascos vikingos y origen del mito: Wikipedia «Horned helmet»; Roberta Frank, "The Invention of the Viking
  Horned Helmet" (2000).
- Cascos de Veksø (Dinamarca, Edad de Bronce, ~900 a. C.; hallados en 1942): Nationalmuseet (Museo Nacional de Dinamarca);
  Vandkilde et al., Praehistorische Zeitschrift (2022).
- Carl Emil Doepler y el vestuario del primer "Anillo del nibelungo" en Bayreuth, 1876: Wikipedia «Carl Emil Doepler»; Frank (2000).
- Era vikinga desde 793 (Lindisfarne): Britannica «Viking».
Antes de producir: Opus abre cada fuente y confirma fechas (1942/1943, ~900 a. C., 1876). Si alguna no cuadra, corregir el guion.

## YOUTUBE
Título: ¿Los vikingos usaban cascos con CUERNOS? ¡Mentira! ⚔️ Se los puso un diseñador de ópera
Descripción (youtube_description.txt):
```
¿Los vikingos usaban cascos con cuernos? ¡Mentira! ⚔️ Y el que se los puso ni siquiera era vikingo.

El único casco vikingo casi completo que existe (Gjermundbu, Noruega, hallado en 1943) no tiene cuernos. Sí hay cascos con cuernos en Dinamarca… pero son de la Edad de Bronce, unos 1,700 años antes de los vikingos, y eran ceremoniales. ¿Quién los hizo famosos? Carl Emil Doepler, el vestuarista del estreno de "El anillo del nibelungo" de Wagner en 1876.

¿Tú también los dibujabas así? 👇

Fuentes:
• Museo de Historia Cultural de Oslo — casco de Gjermundbu
• Museo Nacional de Dinamarca — cascos de Veksø (Vandkilde et al., 2022)
• Roberta Frank, "The Invention of the Viking Horned Helmet" (2000)
• Britannica, "Viking"
Animación dibujada a mano en código. Sin imágenes de terceros.

#historia #vikingos #mitos #datoscuriosos #chisme #purochisme #shorts
```
Tags (youtube_tags.txt): vikingos, cascos con cuernos, mito, vikingos cuernos, historia vikinga, noruega, wagner, ópera, edad de bronce, historia, datos curiosos, chisme histórico, historia animada, puro chisme, desmentido
Miniatura (episodios/miniaturas.py → EPISODIOS): top="¿LOS VIKINGOS USABAN", big="CASCOS CON CUERNOS?", sub="¡mentira de ópera!",
emoji="⚔️", frame: W(l0,"Mentira") + 0.6 s (X roja sobre los cuernos).
Subida: privada + publishAt en el siguiente slot libre (revisar memoria calendario-publicacion). Video fuerte → 8 pm CDMX si está libre.

## CHECKLIST PARA PRODUCCIÓN (Opus)
1. Copiar estructura de ep17-colon-tierra-plana (package.json, hyperframes.json, audio/*.py, AGENTS.md, CLAUDE.md, tarjeta final);
   cargar /hyperframes y /hand-drawn-canvas-animation.
2. Copiar a `film/`: core.js, studio.js, cels.js, materials.js de la skill + scripts/render.mjs y package.json; `npm i --no-audit --no-fund`.
   Estudiar `examples/sketchbook-bird.html` (cels enteros + hoja de exposición) antes de dibujar a Björn.
3. audio/audition.py (ROLES) → voices.json; audio/gen_audio_el.py (SCRIPT) → voz.wav, lines.json, transcript.json. Transcribir y comparar.
4. `audio/build_video.py` escribe `film/vikingos.html` inyectando los cues W()/L() entre `/*DATA-START*/…/*DATA-END*/` (editar el .py,
   no su salida). Duración del film = fin de l8 + 0.3 s (la tarjeta final la pone HyperFrames).
5. PRIMERO la toma difícil (l2 goma borrando cuernos): `CHROME="/c/Program Files/Google/Chrome/Application/chrome.exe" node film/render.mjs
   film/vikingos.html --strip <frame>,24` y `--only <frame>`; corregir contacto/espaciado antes de seguir.
6. Resto de tomas; `--grid 24` para revisar; render completo → copiar el mp4 a `assets/dibujo.mp4` (24 fps; index.html lo reproduce
   muted como EP04 con manim.mp4; HyperFrames entrega a 30 fps).
7. gen_music_sfx.py → build.py (captions) → check → snapshot --at 1,5,12,25,40,50 → npm run render → renders/ep18-vikingos-cuernos.mp4;
   medir loudness (objetivo mean ≈ −16 dB, max ≈ −1 dB como EP17).
8. ESTADO.md (formato en la línea 1), youtube_description.txt, youtube_tags.txt, miniatura, subida privada + programación;
   actualizar memorias formatos-video, calendario-publicacion y ganchos-ganadores.
