# EP01 — "Tu cerebro sin dormir" (serie "Un día en tu cuerpo")

GOAL:    the viewer laughs at Neuro buried in trash, learns that one night without sleep raises beta-amyloid (~5%, PNAS 2018), and leaves thinking "I'm going to sleep tonight".
OUTPUT:  HyperFrames, 1080 x 1920, 30 fps, Spanish voice + burned-in captions.
TIME:    31.5 s x 30 = 945 frames. The voice is the clock (assets/lines.json, transcript.json).

LOOK:    thick-outline cartoon.
         ground #FFD6E0 (brain wall) with brain folds #F9B3C6 18 px, no outline; floor #F28CA8 from y=1150 with a 10 px ink line.
         ink #1B1B2F: every character outline 10–14 px, round joins; props 8 px.
         Neuro #FF8FAB with folds #E06C8E. Glía (astrocyte, a star cell) #3EC6C1, orange cap #FF8C42.
         Accent #FFD23F: the active caption word, the header highlight, the "+5%" sticker. Purple #9B5DE5 only for beta-amyloid.
         Type: Archivo Black (header 110 px, captions 76 px max, uppercase), Nunito 800 for the source note (30 px).
         Hard cartoon shadow: 8 px offset in ink, no blur. Line boil: displacement 2.5 px, 12 times a second, seeded.
OBJECTS: brain = cloud of lobes with folds and a central fissure, eyes, mouth; astrocyte = star with 6 rounded arms;
         trash = dark green bags #4A7C59 with ties + purple goo; jar = glass jar with a lid and goo inside; key = yellow key; pillow = white with seams.
MOTION:  entrances back.out(1.6) 0.35 s (playful, damping ~0.5); exits power3.in 0.2 s; camera power2.inOut 0.6 s; iris power3.inOut 0.45 s.
         Neuro's moods change in 0.25 s with anticipation (squash 0.92 → 1.04 → 1). Blink every 3.1 s, 0.12 s. Lip sync from voice RMS (assets/mouth.json).
SHOTS:   0.0–2.6   Neuro alone, yelling, shaking, in trash with flies; header already on screen (frame 0 = thumbnail). Bass impact at 0.05.
         2.6–7.5   Glía pops in from the right with a broom (pop), Neuro slides left; she sweeps while she talks.
         7.5–10.4  Neuro confused: question marks, head tilt.
         10.4–15.1 Iris from Neuro's head into the brain: 3 working neurons drop purple goo; "BETA-AMILOIDE" sticker at 13.9 (pop).
         15.1–18.4 Iris closes; Neuro scared: sweat, shiver, tiny pupils.
         18.4–23.8 Colour flood to yellow: a jar of goo; "1 NOCHE SIN DORMIR" at 20.9; goo rises; "+5%" slams at 22.9 (ping); source note under the jar.
         23.8–27.0 Back to the room: Neuro exhausted (eyelids, bags), thought bubble with a key and "?" at 26.3.
         27.0–31.5 Glía offers a pillow (28.4, sparkle); Neuro looks at the camera at 29.6; hold to the end.
SOUND:   voice; effects only on visible actions (impact, pop x2, ping, sparkle). No music (no source without HeyGen sign-in).
BANNED:  dark void, glow, gradients, glass cards, everything centred and still, text that moves while read, fade+slide-up on everything, floating particles as decoration.
QA:      frames 0.0 (thumbnail), 3.5, 8.5, 12.5, 14.5, 16.5, 21.5, 23.2, 26.5, 30.5: header readable, characters read as a brain and a star cell, captions readable at 360 px, nothing in the bottom 590 px except floor and trash.
