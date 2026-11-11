"""EP18: cues del film dibujado a mano (film/cues.js) e index.html.

  python -I audio/build_video.py     (después de gen_audio_el.py y build.py)
  luego: cd film && CHROME=... node render.mjs vikingos.html --out out  → copiar out/vikingos.mp4 a assets/dibujo.mp4

El film (film/vikingos.html, skill hand-drawn-canvas-animation, 24 fps) lee window.CUES: cada entrada está anclada a una
palabra con W()/L() desde transcript.json, así que una voz nueva re-sincroniza sola. index.html reproduce assets/dibujo.mp4
muted y pone encima subtítulos, tarjeta final, voz, música y SFX.
"""
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORDS = json.loads((ROOT / "transcript.json").read_text(encoding="utf-8"))
LINES = {l["id"]: l for l in json.loads((ROOT / "assets/lines.json").read_text(encoding="utf-8"))}
MOUTH = json.loads((ROOT / "assets/mouth.json").read_text(encoding="utf-8"))
CARD = 4.4
MUSIC_VOL, MUSIC_END_VOL = 0.4, 0.8


def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if c.isalnum() and not unicodedata.combining(c))


def L(line, d=0.0, end=False):
    return round(LINES[line]["end" if end else "start"] + d, 3)


def W(line, word, k=1, d=0.0):
    ln = LINES[line]
    hits = [w for w in WORDS if ln["start"] - 0.05 <= w["start"] <= ln["end"] and norm(w["text"]).startswith(norm(word))]
    if len(hits) < k:
        raise SystemExit(f"'{word}' no está en {line}: {[w['text'] for w in WORDS if ln['start'] - 0.05 <= w['start'] <= ln['end']]}")
    return round(hits[k - 1]["start"] + d, 3)


END = round(LINES["l8"]["end"] + 1.0, 2)
TOTAL = round(END + CARD, 2)
C = {
    "mentira": W("l0", "mentira"), "puso": W("l0", "puso"), "vikingo": W("l0", "vikingo", 2),
    "l1": L("l1"), "grandotes": W("l1", "grandotes"), "miedo": W("l1", "miedo"),
    "l2": L("l2"), "borro": W("l2", "borro"), "noruega": W("l2", "noruega"), "unico": W("l2", "unico"),
    "cuantos": W("l2", "cuantos"), "cero": W("l2", "cero"),
    "l3": L("l3"), "asusto": W("l3", "asusto"), "l3e": L("l3", end=True),
    "l4": L("l4"), "hacha": W("l4", "hacha"), "historiadores": W("l4", "historiadores"), "batalla": W("l4", "batalla"),
    "estorbo": W("l4", "estorbo"),
    "l5": L("l5"), "cascos5": W("l5", "cascos"), "dinamarca": W("l5", "dinamarca"), "bronce": W("l5", "bronce"), "mil5": W("l5", "mil"),
    "antes": W("l5", "antes"), "ceremonias": W("l5", "ceremonias"), "pelear": W("l5", "pelear"),
    "l6": L("l6"), "famosos": W("l6", "famosos"), "vestuario": W("l6", "vestuario"), "alemania": W("l6", "alemania"),
    "wagner": W("l6", "wagner"), "carl": W("l6", "carl"), "doepler": W("l6", "doepler"), "guerreros": W("l6", "guerreros"),
    "l7": L("l7"), "divinos": W("l7", "divinos"), "gorrito": W("l7", "gorrito"),
    "l8": L("l8"), "caricaturas": W("l8", "caricaturas"), "peliculas": W("l8", "peliculas"), "disfraces": W("l8", "disfraces"),
    "cuernos8": W("l8", "cuernos"), "tu": W("l8", "tu"), "dibujabas": W("l8", "dibujabas"), "l8e": L("l8", end=True),
    "end": END,
}
SPK = {l["id"]: [l["speaker"], l["start"], l["end"]] for l in LINES.values()}


def cues_js():
    return ("// generado por audio/build_video.py — no editar\n"
            f"window.CUES = {json.dumps(C)};\nwindow.SPK = {json.dumps(SPK)};\n"
            f"window.MOUTH = {json.dumps(MOUTH, separators=(',', ':'))};\n")


def index_html():
    sfx = [("horn0", "el_horn", 0.15, 1.4, 0.3), ("mk0", "el_marker", C["mentira"], 0.8, 0.6), ("buzz0", "el_buzz", C["mentira"] + 0.35, 0.8, 0.25),
           ("pen0", "el_pencil", C["vikingo"] - 0.2, 1.2, 0.45),
           ("pen1", "el_pencil", C["grandotes"], 1.2, 0.5),
           ("er2", "el_eraser", C["borro"] - 0.1, 1.2, 0.35), ("pen2", "el_pencil", C["noruega"], 1.2, 0.4),
           ("pen2b", "el_pencil", C["unico"], 1.2, 0.45), ("er2b", "el_eraser", C["cero"] - 0.25, 1.2, 0.65), ("st2", "el_stamp", C["cero"] + 0.75, 0.7, 0.45),
           ("stomp3", "el_stomp", C["l3"] + 0.3, 1.4, 0.5),
           ("axe4", "el_axe", C["hacha"], 0.8, 0.5), ("buzz4", "el_buzz", C["estorbo"] + 0.1, 0.8, 0.25),
           ("pg5", "el_page", C["l5"] - 0.35, 0.8, 0.55), ("st5", "el_stamp", C["dinamarca"], 0.7, 0.35), ("st5b", "el_stamp", C["dinamarca"] + 0.45, 0.7, 0.3),
           ("w5", "whoosh", C["mil5"], 0.57, 0.35), ("st5c", "el_stamp", C["ceremonias"], 0.7, 0.45), ("ding5", "el_ding", C["ceremonias"] + 0.15, 0.7, 0.3),
           ("pg6", "el_page", C["l6"] - 0.3, 0.8, 0.5), ("w6", "whoosh", C["l6"] + 0.1, 0.57, 0.35), ("st6", "el_stamp", C["alemania"], 0.7, 0.35),
           ("sc6", "el_scissors", C["doepler"] + 0.3, 0.8, 0.5), ("gasp6", "el_gasp", C["guerreros"], 1.2, 0.3),
           ("ap7", "el_applause", C["divinos"], 1.8, 0.35), ("pop7", "pop", C["gorrito"], 0.72, 0.45),
           ("pg8", "el_page", C["l8"] - 0.3, 0.8, 0.5), ("mk8a", "el_marker", C["caricaturas"] + 0.3, 0.8, 0.45),
           ("mk8b", "el_marker", C["peliculas"] + 0.3, 0.8, 0.45), ("mk8c", "el_marker", C["disfraces"] + 0.3, 0.8, 0.45),
           ("pen8", "el_pencil", C["dibujabas"], 1.2, 0.45), ("er8", "el_eraser", C["l8e"] + 0.15, 1.2, 0.5),
           ("end", "whoosh", END - 0.05, 0.57, 0.4), ("end-logo", "pop", END + 0.25, 0.72, 0.5), ("end-title", "sparkle", END + 0.55, 1.8, 0.35)]
    rows = [f'      <audio id="sfx-{i}" class="clip" src="assets/sfx/{f}.mp3" data-start="{round(t, 3)}" data-duration="{d}" '
            f'data-track-index="{5 + k % 6}" data-volume="{v}"></audio>' for k, (i, f, t, d, v) in enumerate(sfx)]
    return f'''<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #F2EADB; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
      <video id="dibujo" class="clip" src="assets/dibujo.mp4" data-start="0" data-duration="{END}" data-track-index="0" muted playsinline style="z-index: 0"></video>
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html"
        data-start="0" data-duration="{END}" data-track-index="2" data-track-kind="captions"
        data-width="1080" data-height="1920" style="z-index: 2"></div>
      <div id="endcard" data-composition-id="endcard" data-composition-src="compositions/endcard.html"
        data-start="{round(END - 0.05, 2)}" data-duration="{CARD}" data-track-index="1" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index: 3"></div>

      <audio id="vo" class="clip" src="assets/voz.wav" data-start="0" data-track-index="3" data-volume="1"></audio>
      <audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="4" data-volume="{MUSIC_VOL}" data-fade-out="0.15"></audio>
      <audio id="music-end" class="clip" src="assets/music.mp3" data-start="{END}" data-media-start="{END}" data-duration="{round(CARD - 0.05, 2)}" data-track-index="12" data-volume="{MUSIC_END_VOL}" data-fade-in="0.15" data-fade-out="0.6"></audio>
{chr(10).join(rows)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
'''


if __name__ == "__main__":
    (ROOT / "film/cues.js").write_text(cues_js(), encoding="utf-8")
    (ROOT / "index.html").write_text(index_html(), encoding="utf-8")
    print(f"cues + index: {TOTAL} s, film {END} s, end card at {END} s")
