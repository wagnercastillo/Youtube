"""Escribe index.html con los efectos atados a palabras de transcript.json (una voz nueva re-sincroniza todo).

  python -I audio/build_index.py
"""
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORDS = json.loads((ROOT / "transcript.json").read_text(encoding="utf-8"))
LINES = {l["id"]: l for l in json.loads((ROOT / "assets/lines.json").read_text(encoding="utf-8"))}
MUSIC_VOL, MUSIC_END_VOL, CARD = 0.38, 0.8, 4.55  # music ≈ 12 dB under the voice; louder under the end card


def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if c.isalnum() and not unicodedata.combining(c))


def L(line, d=0.0):
    return LINES[line]["start"] + d


def W(line, word, k=1, d=0.0):
    ln = LINES[line]
    hits = [w for w in WORDS if ln["start"] - 0.05 <= w["start"] <= ln["end"] and norm(w["text"]) == norm(word)]
    return hits[k - 1]["start"] + d


END = round(LINES["l9"]["end"] + 0.45, 2)
TOTAL = round(END + CARD, 2)
SFX = [("chalk1", "el_chalk", L("l1", 0.6), 0.8, 0.45), ("date1", "pop", W("l1", "dos"), 0.72, 0.4),
       ("cleo", "pop", L("l2"), 0.72, 0.5), ("seg1", "el_chalk", W("l3", "entre"), 0.8, 0.45),
       ("g1", "el_ding", W("l3", "dos"), 1.0, 0.4), ("moon", "el_rocket", W("l4", "luna", d=-0.05), 1.2, 0.4),
       ("g2", "el_ding", W("l4", "menos"), 1.0, 0.4), ("arrow", "whoosh-short", W("l5", "cerca", d=-0.05), 0.57, 0.4),
       ("clear", "whoosh", L("l6"), 0.57, 0.35), ("bar1", "pop", W("l6", "piramide"), 0.72, 0.45),
       ("bar2", "pop", W("l6", "ella", 2), 0.72, 0.45), ("mammoth", "el_mammoth", W("l7", "mamuts"), 1.5, 0.5),
       ("isla", "pop", W("l8", "isla"), 0.72, 0.4), ("seg3", "el_chalk", W("l8", "siglos"), 0.8, 0.45),
       ("out", "whoosh", W("l9", "eso", d=-0.05), 0.57, 0.35), ("q", "impact-bass-1", W("l9", "antigua", 2), 2.1, 0.45),
       ("end", "whoosh", END - 0.05, 0.57, 0.4), ("end-logo", "pop", END + 0.25, 0.72, 0.5), ("end-title", "pop", END + 0.55, 0.72, 0.45)]
rows = [f'      <audio id="sfx-{i}" class="clip" src="assets/sfx/{f}.mp3" data-start="{round(t, 2)}" data-duration="{d}" '
        f'data-track-index="{5 + k % 3}" data-volume="{v}"></audio>' for k, (i, f, t, d, v) in enumerate(SFX)]

html = f'''<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #EFE0BC; }}
      #manim {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
      <video id="manim" class="clip" src="assets/manim.mp4" data-start="0" data-duration="{END}" data-track-index="0" muted playsinline style="z-index: 0"></video>
      <div id="captions" data-composition-id="captions" data-composition-src="compositions/captions.html"
        data-start="0" data-duration="{END}" data-track-index="2" data-track-kind="captions"
        data-width="1080" data-height="1920" style="z-index: 2"></div>
      <div id="endcard" data-composition-id="endcard" data-composition-src="compositions/endcard.html"
        data-start="{round(END - 0.05, 2)}" data-duration="{CARD}" data-track-index="1" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index: 3"></div>

      <audio id="vo" class="clip" src="assets/voz.wav" data-start="0" data-track-index="3" data-volume="1"></audio>
      <audio id="music" class="clip" src="assets/music.mp3" data-start="0" data-duration="{END}" data-track-index="4" data-volume="{MUSIC_VOL}" data-fade-out="0.15"></audio>
      <audio id="music-end" class="clip" src="assets/music.mp3" data-start="{END}" data-media-start="{END}" data-duration="{round(CARD - 0.05, 2)}" data-track-index="8" data-volume="{MUSIC_END_VOL}" data-fade-in="0.15" data-fade-out="0.6"></audio>
{chr(10).join(rows)}
    </div>
    <script>
      window.__timelines = window.__timelines || {{}};
      window.__timelines["main"] = gsap.timeline({{ paused: true }});
    </script>
  </body>
</html>
'''
(ROOT / "index.html").write_text(html, encoding="utf-8")
print(f"index.html: {TOTAL} s, end card at {END} s, {len(SFX)} sfx")
