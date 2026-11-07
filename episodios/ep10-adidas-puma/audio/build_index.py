"""EP10: escribe compositions/overlay.html (gancho y rótulos con máscara) e index.html (video de Blender + audio), con tiempos por palabra.

  python -I audio/build_index.py     (después de gen_audio_el.py y build.py; el video sale de blender/escena.py)

El diorama 3D se renderiza en Blender (assets/blender.mp4, mudo). Aquí van encima: el gancho desde el cuadro 0, rótulos
estilo etiqueta de juguete revelados con clip-path, subtítulos, tarjeta final, voz, música y efectos atados a palabras.
"""
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORDS = json.loads((ROOT / "transcript.json").read_text(encoding="utf-8"))
LINES = {l["id"]: l for l in json.loads((ROOT / "assets/lines.json").read_text(encoding="utf-8"))}
CARD = 4.2
MUSIC_VOL, MUSIC_END_VOL = 0.38, 0.8  # music ≈ 12 dB under the voice; louder under the end card


def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if c.isalnum() and not unicodedata.combining(c))


def L(line, d=0.0):
    return round(LINES[line]["start"] + d, 3)


def W(line, word, k=1, d=0.0):
    ln = LINES[line]
    hits = [w for w in WORDS if ln["start"] - 0.05 <= w["start"] <= ln["end"] and norm(w["text"]) == norm(word)]
    return round(hits[k - 1]["start"] + d, 3)


END = round(LINES["l10"]["end"] + 0.45, 2)  # same formula as blender/escena.py
TOTAL = round(END + CARD, 2)

BANNERS = [  # id, text, color class, in, out
    ("b1", "ALEMANIA · AÑOS 20", "", W("l1", "alemania"), W("l1", "lavanderia", d=-0.15)),
    ("b2", "TALLER: LA LAVANDERÍA DE MAMÁ", "", W("l1", "lavanderia"), L("l2", -0.05)),
    ("b3", "BERLÍN 1936 · JESSE OWENS", "", W("l2", "jesse"), W("l2", "cuatro", d=-0.12)),
    ("b4", "4 MEDALLAS DE ORO 🥇", "gold", W("l2", "cuatro"), L("l3", -0.05)),
    ("b5", "SEGUNDA GUERRA MUNDIAL", "dark", W("l3", "guerra"), W("l3", "refugio", d=-0.15)),
    ("b6", "MISMO REFUGIO… 😬", "dark", W("l3", "refugio"), L("l4", -0.05)),
    ("b7", "¿LOS AVIONES… O ÉL? 🤔", "", W("l6", "aviones"), L("l7", -0.05)),
    ("b8", "1948: SE SEPARAN 💔", "", W("l7", "separan"), W("l7", "adidas", d=-0.4)),
    ("b9", "ADI → ADIDAS", "blue", W("l7", "adidas", d=-0.3), W("l7", "puma", d=-0.3)),
    ("b10", "RUDI → PUMA", "red", W("l7", "puma", d=-0.25), L("l8", -0.05)),
    ("b11", "UN PUEBLO, DOS BANDOS", "", W("l8", "dos"), W("l8", "antes", d=-0.15)),
    ("b12", "«EL PUEBLO DE LOS CUELLOS DOBLADOS»", "", W("l8", "miraban"), L("l9", -0.05)),
    ("b13", "RUDI † 1974 · ADI † 1978", "dark", W("l9", "enterrados"), L("l10", -0.05)),
    ("b14", "2009: EL PARTIDO DE LA PAZ ⚽", "gold", W("l10", "partido", d=-0.1), END - 0.15),
]
IN_CLIP, SHOW, OUT_CLIP = "inset(-30px 1200px -30px -30px)", "inset(-30px -30px -30px -30px)", "inset(-30px -30px -30px 1200px)"


def overlay_html():
    banners = "\n".join(f'    <div id="{i}" class="ban {c}"><span>{t}</span></div>' for i, t, c, _, _ in BANNERS)
    tw = [f'tl.fromTo("#h1", {{ clipPath: "{IN_CLIP}" }}, {{ clipPath: "{SHOW}", duration: 0.28, ease: "power3.out" }}, 0);',
          f'tl.fromTo("#h2", {{ clipPath: "{IN_CLIP}" }}, {{ clipPath: "{SHOW}", duration: 0.3, ease: "power3.out" }}, {W("l0", "son", d=-0.1)});',
          f'tl.fromTo("#h2 span", {{ rotation: 0 }}, {{ rotation: -3, duration: 0.25, ease: "back.out(3)" }}, {W("l0", "odiaban")});',
          f'tl.fromTo("#hook", {{ clipPath: "{SHOW}" }}, {{ clipPath: "{OUT_CLIP}", duration: 0.3, ease: "power3.in", immediateRender: false }}, {L("l1", -0.2)});']
    for i, _, _, a, b in BANNERS:
        tw += [f'tl.fromTo("#{i}", {{ clipPath: "{IN_CLIP}" }}, {{ clipPath: "{SHOW}", duration: 0.32, ease: "power3.out" }}, {a});',
               f'tl.fromTo("#{i} span", {{ y: 18 }}, {{ y: 0, duration: 0.36, ease: "back.out(2.4)" }}, {round(a + 0.12, 3)});',
               f'tl.fromTo("#{i}", {{ clipPath: "{SHOW}" }}, {{ clipPath: "{OUT_CLIP}", duration: 0.22, ease: "power3.in", immediateRender: false }}, {round(b, 3)});']
    return OVERLAY.replace("__BANNERS__", banners).replace("__TW__", "\n".join("    " + x for x in tw))


OVERLAY = r'''<template>
  <style>
    #root { position: absolute; inset: 0; overflow: hidden; pointer-events: none; font-family: "Archivo Black", sans-serif; }
    .ban { position: absolute; left: 0; top: 300px; width: 1080px; text-align: center; clip-path: inset(-30px 1200px -30px -30px); }
    .ban span { display: inline-block; max-width: 980px; font-size: 52px; line-height: 1.1; padding: 16px 30px 10px; background: #FFFFFF;
      color: #1B1B2F; border: 8px solid #1B1B2F; border-radius: 26px; box-shadow: 0 10px 0 #1B1B2F; letter-spacing: 1px; }
    .gold span { background: #FFD23F; } .blue span { background: #2F6FD6; color: #FFFFFF; } .red span { background: #D6402F; color: #FFFFFF; }
    .dark span { background: #1B1B2F; color: #FFD23F; border-color: #FFD23F; box-shadow: 0 10px 0 #000000; }
    #hook { position: absolute; left: 0; top: 150px; width: 1080px; }
    .tags { width: 1080px; text-align: center; margin-bottom: 24px; clip-path: inset(-30px 1200px -30px -30px); }
    .tags span { display: inline-block; white-space: nowrap; font-size: 56px; line-height: 1; padding: 16px 28px 10px; color: #1B1B2F;
      border: 9px solid #1B1B2F; border-radius: 30px; box-shadow: 0 12px 0 #1B1B2F; }
    #h1 span { background: #FFFFFF; } #h2 span { background: #FFD23F; }
    #h1 .a { color: #2F6FD6; } #h1 .p { color: #D6402F; }
  </style>
  <div id="root" data-composition-id="overlay" data-width="1080" data-height="1920">
__BANNERS__
    <div id="hook">
      <div id="h1" class="tags"><span>¿<b class="a">ADIDAS</b> Y <b class="p">PUMA</b>…</span></div>
      <div id="h2" class="tags"><span>HERMANOS QUE SE ODIABAN?</span></div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({ paused: true });
__TW__
    window.__timelines["overlay"] = tl;
  </script>
</template>
'''

SFX = [  # id, file, start, duration, volume
    ("toy", "el_toy", 0.05, 1.0, 0.35), ("sqA", "el_squeak", W("l0", "adidas"), 0.6, 0.5),
    ("sqR", "el_squeak", W("l0", "puma"), 0.6, 0.5), ("hate", "el_scratch", W("l0", "odiaban"), 0.8, 0.4),
    ("crane", "whoosh", L("l1", 0.0), 0.57, 0.35), ("hopA", "pop", W("l1", "adi"), 0.72, 0.4),
    ("hopR", "pop", W("l1", "rudi"), 0.72, 0.4), ("shoes", "sparkle", W("l1", "zapatos"), 1.0, 0.35),
    ("crowd", "el_stadium", W("l2", "jesse"), 2.0, 0.4), ("gold", "sparkle", W("l2", "cuatro"), 1.0, 0.45),
    ("siren", "el_siren", W("l3", "guerra", d=-0.1), 2.5, 0.35), ("bomb", "el_bomb", W("l3", "bombardeo"), 1.5, 0.55),
    ("shelter", "pop", W("l3", "mismo"), 0.72, 0.35), ("gasp", "el_gasp", L("l5", -0.1), 1.0, 0.35),
    ("snap", "impact-bass-1", L("l5", 0.0), 2.1, 0.35), ("planes", "whoosh", W("l6", "aviones", d=-0.2), 0.57, 0.35),
    ("rip", "el_rip", W("l7", "separan"), 0.8, 0.55), ("split", "impact-bass-1", W("l7", "separan", d=0.1), 2.1, 0.45),
    ("fA", "pop", W("l7", "adidas"), 0.72, 0.45), ("fR", "pop", W("l7", "puma"), 0.72, 0.45),
    ("bars", "pop", W("l8", "bares"), 0.72, 0.4), ("bakery", "pop", W("l8", "panaderias"), 0.72, 0.4),
    ("whis1", "el_whistle", W("l8", "futbol"), 1.0, 0.3), ("necks", "whoosh-short", W("l8", "miraban"), 0.57, 0.35),
    ("wind", "el_wind", L("l9", 0.0), 2.0, 0.45), ("join", "whoosh", W("l10", "paces", d=-0.1), 0.57, 0.35),
    ("cheer", "el_stadium", W("l10", "partido"), 2.0, 0.4), ("whis2", "el_whistle", W("l10", "futbol"), 1.0, 0.4),
    ("end", "whoosh", END - 0.05, 0.57, 0.4), ("end-logo", "pop", END + 0.25, 0.72, 0.5), ("end-title", "pop", END + 0.55, 0.72, 0.45),
]


def index_html():
    rows = [f'      <audio id="sfx-{i}" class="clip" src="assets/sfx/{f}.mp3" data-start="{round(t, 2)}" data-duration="{d}" '
            f'data-track-index="{6 + k % 3}" data-volume="{v}"></audio>' for k, (i, f, t, d, v) in enumerate(SFX)]
    return f'''<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #F3D9A8; }}
      #diorama {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
      <video id="diorama" class="clip" src="assets/blender.mp4" data-start="0" data-duration="{END}" data-track-index="0" muted playsinline style="z-index: 0"></video>
      <div id="overlay" data-composition-id="overlay" data-composition-src="compositions/overlay.html"
        data-start="0" data-duration="{END}" data-track-index="1" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index: 1"></div>
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html"
        data-start="0" data-duration="{END}" data-track-index="2" data-track-kind="captions"
        data-width="1080" data-height="1920" style="z-index: 2"></div>
      <div id="endcard" data-composition-id="endcard" data-composition-src="compositions/endcard.html"
        data-start="{round(END - 0.05, 2)}" data-duration="{CARD}" data-track-index="3" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index: 3"></div>

      <audio id="vo" class="clip" src="assets/voz.wav" data-start="0" data-track-index="4" data-volume="1"></audio>
      <audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="5" data-volume="{MUSIC_VOL}" data-fade-out="0.15"></audio>
      <audio id="music-end" class="clip" src="assets/music.mp3" data-start="{END}" data-media-start="{END}" data-duration="{round(CARD - 0.05, 2)}" data-track-index="9" data-volume="{MUSIC_END_VOL}" data-fade-in="0.15" data-fade-out="0.6"></audio>
{chr(10).join(rows)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
'''


def main():
    (ROOT / "compositions/overlay.html").write_text(overlay_html(), encoding="utf-8")
    (ROOT / "index.html").write_text(index_html(), encoding="utf-8")
    print(f"index.html: {TOTAL} s, end card at {END} s, {len(BANNERS)} rótulos, {len(SFX)} sfx")


if __name__ == "__main__":
    main()
