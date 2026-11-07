# Plan: créditos ElevenLabs y bancos de voces/música/SFX

Fecha: 2026-11-07 · Estado: **propuesta, pendiente de revisión del dueño**

## 1. Situación actual

- Plan actual: 38,201 créditos, usados 27,309 → **quedan 10,892**.
- Meta de publicación: 3 Shorts/día = **~90 episodios/mes**.
- Costo por episodio con el flujo actual (medido en EP10–EP16):

| Concepto | Uso | Créditos aprox. |
|---|---|---|
| Diálogo `eleven_v3` (1 crédito/carácter) | 800–990 caracteres | ~900 |
| Regenerar líneas que se comen palabras | ~10–20 % | ~150 |
| Diseño de voces (`audition.py`, ~9 candidatas) | | ~1,000–1,500 ⚠️ estimado |
| Efectos de sonido (~9 por episodio, ~9 s en total) | | ~400 |
| Música Eleven Music (52 s) | | ~800–1,500 ⚠️ estimado |
| **Total** | | **~3,000–4,500** |

⚠️ Las cifras de voces y música son estimaciones. La llave del `.env` no tiene permiso `user_read`, así que
no se puede leer el saldo por API. Para medirlo bien: anotar el saldo en el panel antes y después de un episodio.

## 2. ¿Alcanza el plan Creator (110k créditos/mes, $9 el primer mes y luego $19.99)?

| Escenario | Créditos/episodio | 90 episodios/mes | ¿Alcanza? |
|---|---|---|---|
| Flujo actual | ~3,500 | ~315,000 | ❌ solo ~31 episodios (≈1/día) |
| Con bancos (solo se paga el diálogo) | ~1,100 | ~99,000 | ✅ margen ~11k |

**Conclusión:** Creator sirve **solo si** se usan bancos. El margen es justo: si hay un mes con muchas
regeneraciones, se cubre con pay-as-you-go o recortando los guiones a ~800 caracteres.

## 3. Bancos que ya existen (ya están pagados)

### Voces: 18 IDs únicos en EP03–EP16

Ya se reutilizan entre episodios (por ejemplo, `uiAk…` narra EP04, EP08 y EP11).

| Voice ID | Usada en (rol) |
|---|---|
| `uiAksityc3aBuAQ4bjSW` | EP04 narr, EP08 narr, EP11 narr |
| `FD4Jk3fxMZePximsMP5M` | EP05 narr, EP10 narr |
| `ZDGUr0IFu8PtJsGTXKMS` | EP06 narr, EP09 narr |
| `7tb7K85NPMWqZuDlU3FW` | EP07 narr, EP12 narr |
| `yG52fI8LU4PPVgvtNLWz` | EP13 narr |
| `9iXyYHvduoLnd9KkiilS` | EP14 narr |
| `WIw1Bk6Fk0FlBXsOTG7R` | EP16 narr |
| `9i91rBp5kZ8nzrFweGhq` | EP15 conductor de noticiero |
| `Ll2YU9FpalgnaTLaqPF4` | EP15 reportera |
| `1YKZME5DvAy6a7RWNPMw` | EP03 Napoleón, EP10 Alejandro |
| `KWetGUahnofEBz9CSrjF` | EP03 Gillray, EP10 Diógenes, EP11 Baynes |
| `hxwrwnllvWvQ1SpVlrT8` | EP07 Esteban, EP11 Cutlar |
| `P7sGVTAsIMNCtEMBYHYe` | EP07 diácono, EP11 Griffin |
| `J9W3jDFirY7HHnCPjuJ3` | EP14 alemán |
| `S4mafYwumBuASkqvF3aW` | EP16 Xantipa |
| `kg6irbmBsy8cg7PRlF9Z` | EP16 Sócrates |
| `AgGhWpMLnU7pTuMeN2UG` | EP04 narr_calm (candidata descartada, ¿borrar?) |
| `7dqhaR1V8mlQJRZ8d1Gk` | EP04 narr_dull (candidata descartada, ¿borrar?) |

**Pendiente:** confirmar que siguen vivas en la cuenta (el límite de voces guardadas puede haber borrado
algunas) y apuntar para cada una: género, edad, energía y tipo de personaje.

### Música: 14 pistas de Eleven Music (`episodios/epNN/assets/music.mp3`)

| Pista | Estilo |
|---|---|
| EP03 | Cartoon siglo XVIII: clavecín, pizzicato, fagot |
| EP04 | Documental misterioso egipcio: oud, ney |
| EP05 | México-Francia s. XIX: acordeón musette + trompeta de mariachi |
| EP06 | Subasta energética con trova yucateca: requinto, marimba |
| EP07 | Tribunal gótico cómico: órgano, clavecín |
| EP08 | Suspenso japonés: taiko, shakuhachi |
| EP09 | Chiptune 8-bit medieval |
| EP10 | Grecia antigua cómica: lira, bouzouki |
| EP11 | Frontera 1850: banjo, violín, marcha militar |
| EP12 | Tarantela italiana: mandolina, acordeón |
| EP13 | Gypsy jazz París años 20 |
| EP14 | Jazz noir de espías años 40 |
| EP15 | Noticiero urgente + suspenso tipo CSI |
| EP16 | Telenovela melodramática |

### Efectos de sonido: ~9 por episodio en `episodios/epNN/assets/sfx/`

Hay que revisarlos y quedarse con los genéricos (sello, flash, monedas, papel, golpe dramático…).

## 4. Fuentes fuera de ElevenLabs

| Fuente | Costo | Riesgo de Content ID / monetización | Uso |
|---|---|---|---|
| **Biblioteca de audio de YouTube** (Studio) | Gratis | El más bajo (aprobada por YouTube) | **Primera opción** para música y efectos |
| Eleven Music (pistas existentes) | Ya pagadas | Bajo (licencia comercial en plan de pago) | Rotar las 14 |
| Freesound (solo **CC0**) | Gratis | Bajo si es CC0; CC-BY obliga a dar crédito | Efectos puntuales |
| Epidemic Sound / Artlist | ~$10–17/mes | Muy bajo, con licencia que protege el canal | Opcional si se quiere más calidad |
| Suno (plan de pago) | ~$10/mes | Medio (a veces hay reclamos) | Solo para algo muy específico |
| Pixabay | Gratis | **Medio–alto**: algunos usuarios suben pistas con Content ID | **Evitar** |

ElevenLabs no tiene sustituto para el **diálogo** (voces mexicanas expresivas con `eleven_v3`). Ahí es donde
deben ir los créditos.

## 5. ¿Salen buenos videos con un banco de voces?

Sí. Lo que se reutiliza es la *voz*, no el audio: cada episodio genera diálogo nuevo con su guion y sus
etiquetas de emoción. Las voces del banco son las que ganaron los auditions, o sea, las mejores.

Para cumplir la regla de que ningún video sea igual:
- 2–3 voces por episodio, sacadas de 16–18, dan cientos de combinaciones.
- Registrar en `ideas/PUBLICADOS.md` qué voces usó cada episodio y no repetir la misma pareja en 7 días.
- Diseñar una voz nueva solo cuando el personaje lo pida (niño, anciano, acento regional): ~1–1.5k créditos
  y se agrega al banco.
- Opcional: una narradora recurrente como "voz del canal" para reforzar la marca.

## 6. Plan de implementación (cuando se apruebe)

1. **Revisar voces:** pedir una llave con `voices_read` (o revisar el panel), confirmar qué IDs siguen vivos
   y borrar las descartadas (`narr_calm`, `narr_dull`).
2. **Crear `banco/`:**
   - `banco/voces.json`: ID, nombre, género, edad, energía, roles sugeridos, episodios donde se usó.
   - `banco/musica/`: las 14 pistas + selección de la Biblioteca de YouTube, con `musica.json` (mood, bpm, origen y licencia).
   - `banco/sfx/`: efectos genéricos deduplicados, con `sfx.json`.
3. **Cambiar el pipeline:**
   - `gen_audio_el.py` toma las voces de `banco/voces.json` en lugar de llamar a `audition.py`.
   - `gen_music_sfx.py` busca primero en el banco y solo genera si no hay nada adecuado.
4. **Actualizar `produccion-nocturna/SKILL.md`** con la regla "banco primero" y el control de no repetir voces.
5. **Subir a Creator** y medir el costo real de 3 episodios para confirmar ~1,100 créditos por episodio.

## 7. Decisiones pendientes del dueño

- [ ] ¿Subir a Creator ahora?
- [ ] ¿Usar la Biblioteca de audio de YouTube como fuente principal de música y efectos?
- [ ] ¿Queremos una narradora fija como "voz del canal"?
- [ ] ¿Pagar Epidemic Sound o basta con lo gratis?
