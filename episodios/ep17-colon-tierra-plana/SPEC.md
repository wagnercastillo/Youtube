# EP17-COLON-TIERRA-PLANA — "¿Colón descubrió que la Tierra era REDONDA? ¡Mentira!"
Formato NUEVO: COLLAGE DE RECORTES estilo Terry Gilliam (Monty Python): cabezas = retratos REALES de dominio público recortados
con tijera (borde blanco de 6–8 px, sombra dura), cuerpos pintados planos con contorno gordo, manos gigantes de cartón, mandíbula
= pedazo aparte que abre a bisagra con `steps(1)` (lip-sync directo desde mouth.json). Todo a saltos de 2–3 poses; cero easing
suave en los personajes (la cámara sí puede ser suave). Ver la tarjeta "Collage de recortes (Gilliam)" en marca/estilos-personajes.html.
Estructura NUEVA: CAREO. Una narradora chismosa confronta a dos "acusados": Colón (el de las cuentas malas) y Washington Irving
(el que inventó el mito en 1828). Región: Europa (España/Grecia/EE. UU.); nada de México.
Gancho del tipo ganador del canal: pregunta contraintuitiva / desmentir mito ("¿Napoleón era bajito?", "¿Los mexicas nunca vieron…?").

## Por qué este tema y este estilo (análisis, 2026-11-11)
- Los dos videos más vistos del canal son desmentidos de mito con pregunta en el título (EP03 Napoleón 2.6K, EP02 mexicas 1.6K).
  El mito de "Colón y la Tierra plana" se enseña en la escuela en todo LatAm, así que la pregunta pega al público MX/LatAm sin ser
  un tema mexicano (regla "temas mundiales").
- Payoff doble: (1) la Tierra redonda se sabía 1,700 años antes; (2) Colón se equivocó al revés: la creyó CHICA, y sobrevivió
  solo porque América estaba estorbando. Cierra en bucle con "¿tú también te lo creíste?".
- Estilo: el collage de retratos reales no se ha usado (EP05 usó pinturas enteras en museo, no recortes articulados). Encaja porque
  los dos acusados tienen retrato/foto real, y el estilo es cómico por sí mismo. Ya usados y por eso descartados: papel recortado
  dibujado (EP16), noticiero (EP15), tablero (EP14), tipografía (EP13), 3D (EP12), caricatura plana (EP11).

## GOAL
Hook en pantalla desde el cuadro 0: "¿COLÓN DESCUBRIÓ QUE LA TIERRA ERA REDONDA?" y a los ~1.2 s cae el sello de cartón "¡MENTIRA!".
El espectador aprende: (a) Eratóstenes midió la circunferencia de la Tierra hacia 240 a. C. (~40,000 km, le atinó);
(b) en la Edad Media los reyes posan con el orbe (bola del mundo) en la mano; el libro de texto universitario era "De sphaera" (esfera);
(c) Colón NO creía en una Tierra plana: la creía ~25 % más chica, con Asia enorme, y puso Japón a ~4,500 km de Canarias cuando
está a ~20,000 km; (d) la comisión de Salamanca le dijo que no por la DISTANCIA (se moriría de hambre), no por "plana";
(e) sobrevivió porque América estaba en medio; murió (1506) creyendo que había llegado a Asia; (f) el mito de la Tierra plana lo
popularizó la novela-biografía de Washington Irving en 1828.
Duración objetivo: voz 48–55 s + tarjeta final 4.5 s = 53–60 s.

## GUION (pegar en audio/gen_audio_el.py → SCRIPT; TEMPO 1.1; stability 0.0–0.3 según audición)
```python
SCRIPT = [
    ("l0", "narr",   "[excited] ¿Colón descubrió que la Tierra era redonda? ¡Mentira! Y lo peor: sus cuentas estaban tan mal… que casi se muere en el intento."),
    ("l1", "narr",   "[gossipy] Mil setecientos años ANTES de Colón, un griego llamado Eratóstenes ya había medido la Tierra con dos palos y una sombra. Y le atinó."),
    ("l2", "narr",   "[mischievously] En la Edad Media, los reyes posaban con una bola en la mano. ¿Y qué creen que era? El mundo. Redondo."),
    ("l3", "colon",  "[proud] ¡Exacto! Yo nunca dije que fuera plana. Yo dije que era CHIQUITA… y que Japón quedaba aquí nomás, a un pasito de España."),
    ("l4", "narr",   "[laughs] Y ahí estuvo el error. Colón calculó la Tierra una cuarta parte más chica… y Asia, enorme. Para él, Japón estaba a cuatro mil quinientos kilómetros. En realidad está a casi veinte mil."),
    ("l5", "narr",   "[whispers] Los sabios de Salamanca le dijeron que no… no porque la Tierra fuera plana, sino porque se iba a morir de hambre a medio camino."),
    ("l6", "colon",  "[defensive] ¡Y no me morí! Llegué a… bueno… a un lugar."),
    ("l7", "narr",   "[dramatic] Llegó porque América estaba estorbando en medio. Si no, se le acaba el agua a mitad del océano. Y hasta su muerte juró que había llegado a Asia."),
    ("l8", "narr",   "[gossipy] ¿Entonces quién inventó lo de la Tierra plana? Este señor: Washington Irving, un escritor gringo, en mil ochocientos veintiocho. Trescientos años después."),
    ("l9", "irving", "[smug] Era una NOVELA, querida. ¿Qué tiene de malo un poquito de drama?"),
    ("l10", "narr",  "[mischievously] Nada… solo que trescientos años después lo siguen enseñando en la escuela. ¿Tú también te lo creíste?"),
]
```
Reglas: cada línea es una toma. Si eleven_v3 se come palabras, regenerar esa línea con OVERRIDE (stability 0.5) como EP12.
Verificar con `npx hyperframes transcribe` (o Parakeet como EP14–16) y comparar palabra por palabra.

## VOCES (diseñar nuevas con audio/audition.py, regla del dueño 2026-11-07: no reutilizar; borrar antes voces de episodios ya renderizados si no hay slot)
```python
ROLES = {
 'narr':   ('¿Colón descubrió que la Tierra era redonda? ¡Mentira! Y lo peor: sus cuentas estaban tan mal que casi se muere en el intento.',
            {'maestra': 'Mujer mexicana de 35 años, maestra de historia chismosa, voz brillante, rápida y burlona, muy expresiva, como contando un secreto jugoso. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.',
             'comadre': 'Mujer mexicana de 40 años, voz de comadre que destapa escándalos, energética, picante y clara, ritmo ágil con pausas de suspenso. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.'}),
 'colon':  ('¡Exacto! Yo nunca dije que fuera plana. Yo dije que era chiquita, y que Japón quedaba aquí nomás, a un pasito de España.',
            {'presumido': 'Hombre mexicano de 45 años, navegante presumido y terco, voz nasal y engreída, se defiende con orgullo cómico. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.',
             'capitan': 'Hombre mexicano de 50 años, capitán vanidoso y teatral, voz ronca y potente, se ofende fácil, cómico. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.'}),
 'irving': ('Era una novela, querida. ¿Qué tiene de malo un poquito de drama? La gente quiere emoción, no fechas y números aburridos.',
            {'escritor': 'Hombre mexicano de 55 años, escritor elegante y cínico, voz suave, aterciopelada y condescendiente, sonríe al hablar. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.',
             'dandy': 'Hombre mexicano de 50 años, dandi presumido de teatro, voz melosa y afectada, muy seguro de sí mismo, divertido. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.'}),
}
```
Gana la candidata con más variación de tono y brillo (criterio de audition.py). Narradora MUJER a propósito: EP11–EP14 y EP16 tuvieron narrador hombre.

## ELENCO Y RECORTES (assets/recortes/)
Descargar de Wikimedia Commons con `curl -A "PuroChisme/1.0"` a una carpeta nueva vacía; comprobar en la página del archivo que es
dominio público (PD-old / CC0) y anotar autor+fuente en youtube_description.txt. Si una descarga falla o la licencia no es PD,
dibujar la cabeza como caricatura SVG con el mismo borde de cartón (no detener la producción).
| Personaje / objeto | Imagen base (Commons) | Uso |
|---|---|---|
| Colón | Sebastiano del Piombo, "Portrait of a Man, Said to be Christopher Columbus" (1519), Met Museum, CC0 | Cabeza recortada; mandíbula separada (corte horizontal a la altura de la boca); cuerpo pintado plano: jubón rojo, capa; mano gigante señalando |
| Washington Irving | Daguerrotipo de John Plumbe (1849, Library of Congress) o retrato de Mathew Brady (c. 1860), PD | Cabeza recortada con mandíbula; cuerpo de levita negra; pluma de ganso gigante; libro "1828" |
| Eratóstenes | Grabado del siglo XIX "Eratosthenes" (PD) o busto genérico dibujado | Solo l1; sostiene un palo; sombra; sol de cartón |
| Rey con orbe | Alberto Durero, "Carlomagno" (1512, Germanisches Nationalmuseum, PD) o retrato de Ricardo II (Westminster, c. 1395, PD) | l2: la mano gigante señala el orbe; el orbe hace MATCH CUT a la Tierra |
| Globo de Behaim (Erdapfel, 1492) | Reproducción desplegada de Ravenstein (1908, PD) o foto CC BY-SA (acreditar) | l3–l4: el mapa "sin América" con Japón pegado a Europa |
| Sabios de Salamanca | 3 siluetas con capucha dibujadas (no hace falta retrato) | l5: niegan con la cabeza a saltos |
| Mapa de fondo | Planisferio de Cantino (1502, PD) o pergamino generado en código | Fondos de l3–l7 |
| Barco | Carabela recortada de un grabado PD o dibujada | l7: navega y América se le atraviesa |
| Pizarrón escolar | Dibujado | l10: la frase del mito escrita con gis y unas tijeras de cartón la cortan |

## LOOK
Pergamino #E8D9B5 con manchas, bordes quemados; recortes con borde blanco #FFFFFF 7 px y sombra dura 6/8 px #00000055; cuerpos
planos: Colón rojo #B23A48 / dorado #C9A24A, Irving negro #1B1B2F / blanco; manos #E8C39E con contorno #2b1a10 4 px.
Tipografía: Archivo Black para títulos y sellos de cartón (texto siempre recortado con borde blanco, como pegado), Nunito 800 para
fuentes en pantalla. Sello "¡MENTIRA!" rosa #E23E8B, rotado −8°, cae con `steps(2)` y rebote de 1 cuadro.
Sin line boil, sin temblor constante, filtros con seed fijo. Un "clac" de papel por cada pieza que se pega.

## CÁMARA Y MOTION (reglas del canal)
1. Textos entran por máscara (clip-path wipe) o como recortes que caen; nunca fade plano.
2. Encadenar: cabeza → cuerpo → mano → bocadillo, cada una 0.12–0.2 s después de la anterior, con follow-through de 1 cuadro.
3. La cámara (GSAP sobre el escenario 1080×1920, anclada a W()/L()) se reencuadra sobre quien habla: Colón izq., Irving der., narradora = plano general.
4. Transformaciones: orbe del rey → Tierra (l2); Tierra chica de Colón → Tierra real que la engulle (l4); barco → América que se le atraviesa (l7); frase en pizarrón → cortada por tijeras → tarjeta final (l10).
5. Toda entrada anclada con W(line, word) / L(line) desde transcript.json; ninguna cifra tecleada a mano.

## SHOTS (anclar a palabras; tiempos solo como guía)
- l0 "Colón": cabeza de Colón sube desde abajo a saltos, mandíbula aletea. "Mentira": sello cae. "casi se muere": Colón se pone verde (recorte de cara alternativa, 2 cuadros) y una ola de cartón le pasa por encima.
- l1 "mil setecientos años": tira de calendario de cartón se desenrolla 240 a. C. → 1492. "Eratóstenes": entra con su palo; "sombra": el sol de cartón se desliza, la sombra del palo gira; "le atinó": etiqueta "≈ 40,000 km ✓".
- l2 "reyes": el rey con orbe entra deslizándose; "bola": mano gigante lo señala; "El mundo": el orbe crece y se convierte en la Tierra (match cut); "Redondo": sello verde "REDONDO ✓".
- l3 Colón habla (cámara a la izq.). "CHIQUITA": la Tierra se encoge con 2 saltos; "Japón": recorte "JAPÓN" pegado casi tocando España sobre el mapa de Behaim; "pasito": pasitos de huellas.
- l4 "cuarta parte más chica": dos Tierras lado a lado; "cuatro mil quinientos": tira de papel de 4,500 km se desdobla; "veinte mil": la tira real se desdobla 4× más larga y se sale de cuadro (cámara la sigue).
- l5 "Salamanca": tres encapuchados aparecen y niegan a saltos; "hambre": pan de cartón que se convierte en migas.
- l6 Colón defensivo; "un lugar": recorte "¿?" sobre una costa sin nombre.
- l7 "América estaba estorbando": barco navega hacia la izq. del mapa, América entra de golpe y lo bloquea (clac); "se le acaba el agua": barril vacío; "Asia": sello "ASIA" tachado en rojo, "1506 †" pequeño.
- l8 "Este señor": Irving entra desde la der. con su pluma; "1828": libro de cartón se abre; "Trescientos años": calendario de tiras 1492 → 1828 pasando a saltos.
- l9 Irving habla (cámara a la der.), se encoge de hombros con manos gigantes; Colón de reojo.
- l10 "escuela": pizarrón con "Colón descubrió que la Tierra era redonda"; "te lo creíste": tijeras de cartón cortan la frase → cae y revela la tarjeta final Puro Chisme (logo con ojos, "¿A poco no sabías este chisme?", "SÍGUENOS PARA MÁS").

## SONIDO
Voz 1.0. Eleven Music: "comic baroque harpsichord with pizzicato strings, playful, mischievous, 100 bpm, no vocals", ≈ −12 dB bajo la voz
(subir bajo la tarjeta final). SFX ElevenLabs: papel que se pega (clac), tijeras, sello, ola, gaviota, campanita de "✓". Solo en acciones visibles.

## FUENTES (mostrar al pie o en descripción)
- Eratóstenes y la medición de la Tierra: Britannica, "Eratosthenes"; Cleomedes, De motu circulari.
- Esfericidad conocida en la Edad Media: Johannes de Sacrobosco, De sphaera mundi (c. 1230); orbe/globus cruciger en retratos reales.
- Cálculo de Colón (Alfragano con millas cortas, Asia de Marino de Tiro/Toscanelli; Japón a ~2,400 millas náuticas de Canarias vs ~10,600 reales):
  Wikipedia "Christopher Columbus" (sección "Geographical considerations"); Britannica "Christopher Columbus".
- Comisión de Salamanca/Talavera rechazó por la distancia: Wikipedia "Myth of the flat Earth"; J. B. Russell, Inventing the Flat Earth (1991).
- Washington Irving, A History of the Life and Voyages of Christopher Columbus (1828) como origen del mito: ídem.
- Globo de Behaim (1492, sin América): Germanisches Nationalmuseum, "Erdapfel".
- Colón murió en 1506 creyendo haber llegado a Asia: Britannica.

## YOUTUBE
Título: ¿Colón descubrió que la Tierra era REDONDA? ¡Mentira! 🌍 Y casi se muere por un error de matemáticas
Descripción (youtube_description.txt):
```
¿Colón descubrió que la Tierra era redonda? ¡Mentira! 🌍 Y sus cuentas estaban tan mal que casi se muere en el intento.

1,700 años antes, Eratóstenes ya había medido la Tierra (y le atinó: ~40,000 km). En la Edad Media los reyes posaban con el mundo en la mano. Colón no creía que fuera plana: la creía una cuarta parte más chica y puso Japón a 4,500 km de España (está a casi 20,000). Salamanca le dijo que no por la distancia, no por "plana". Sobrevivió porque América estaba en medio… y murió jurando que había llegado a Asia. El mito de la Tierra plana lo inventó una novela de Washington Irving en 1828.

¿Tú también te lo creíste? 👇

Fuentes:
• Britannica, "Eratosthenes" y "Christopher Columbus"
• Sacrobosco, De sphaera mundi (c. 1230)
• J. B. Russell, Inventing the Flat Earth (1991) · Wikipedia "Myth of the flat Earth"
• Germanisches Nationalmuseum, globo de Behaim (1492)
Imágenes (dominio público): [completar: Piombo/Met CC0, Plumbe/LoC, Durero, Behaim/Ravenstein, Cantino]

#historia #colon #tierraplana #mitos #datoscuriosos #chisme #purochisme #shorts
```
Tags (youtube_tags.txt): cristóbal colón, tierra plana, mito, eratóstenes, 1492, descubrimiento de américa, edad media, washington irving, historia, datos curiosos, chisme histórico, historia animada, puro chisme, desmentido
Miniatura (episodios/miniaturas.py → EPISODIOS): top="¿COLÓN DESCUBRIÓ", big="QUE LA TIERRA ERA REDONDA?", sub="¡mentira de 1828!", emoji="🌍",
frame: el momento del sello "¡MENTIRA!" sobre la cara de Colón.
Subida: privada + publishAt en el siguiente slot libre (12/4/8 pm CDMX; revisar lo programado en ESTADO.md de EP14–EP16 y memoria calendario-publicacion).
Este es video fuerte: slot de 8 pm CDMX si está libre.

## CHECKLIST PARA PRODUCCIÓN (Opus)
1. Copiar la estructura del proyecto de ep16-socrates-xantipa (package.json, hyperframes.json, audio/*.py, AGENTS.md, CLAUDE.md) a esta carpeta; cargar la skill /hyperframes.
2. audio/audition.py con los ROLES de arriba → audio/voices.json (liberar slots borrando voces de episodios ya renderizados si hace falta).
3. audio/gen_audio_el.py con el SCRIPT de arriba → assets/voz.wav, lines.json, mouth.json, transcript.json. Transcribir y comparar.
4. Descargar recortes (tabla de arriba) a assets/recortes/ con licencia verificada; recortar borde con clip-path polygon dentado + borde blanco en código (no editar imágenes a mano); la mandíbula es la mitad inferior del mismo retrato.
5. audio/gen_music_sfx.py → música + SFX.
6. audio/build_video.py → compositions/stage.html + index.html (todo anclado con W()/L(); jaw por mouth.json con steps(1)); audio/build.py → captions.html.
7. npx hyperframes check; snapshot --at 1,5,12,25,40,50; revisar cuadros; npm run render → renders/ep17-colon-tierra-plana.mp4; medir loudness.
8. ESTADO.md (formato en la línea 1), youtube_description.txt (con créditos de imágenes), youtube_tags.txt, miniatura, subida privada + programación, actualizar memoria formatos-video y calendario-publicacion.
