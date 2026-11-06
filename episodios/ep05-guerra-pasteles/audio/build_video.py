"""EP05: escribe compositions/stage.html e index.html con todos los tiempos atados a palabras de transcript.json.

  python -I audio/build_video.py        (después de gen_audio_el.py y build.py)

Formato: galería de museo con pinturas reales (Ken Burns lento, sin temblores) + "la cuenta del chisme",
un ticket que imprime una línea por dato.
"""
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORDS = json.loads((ROOT / "transcript.json").read_text(encoding="utf-8"))
LINES = {l["id"]: l for l in json.loads((ROOT / "assets/lines.json").read_text(encoding="utf-8"))}
CARD = 4.2
MUSIC_VOL, MUSIC_END_VOL = 0.4, 0.8


def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if c.isalnum() and not unicodedata.combining(c))


def L(line, d=0.0):
    return round(LINES[line]["start"] + d, 3)


def W(line, word, k=1, d=0.0):
    ln = LINES[line]
    hits = [w for w in WORDS if ln["start"] - 0.05 <= w["start"] <= ln["end"] and norm(w["text"]) == norm(word)]
    return round(hits[k - 1]["start"] + d, 3)


END = round(LINES["l9"]["end"] + 0.9, 2)  # room for the ¡PAGADO! stamp to be read
TOTAL = round(END + CARD, 2)

# ---- paintings: (id, file, start, plaque) — each holds until the next one ----
SCENES = [
    ("p0", "pasteleria", 0.0, "Caricatura francesa de una pastelería · Charles Pacot, c. 1830"),
    ("p1", "luisfelipe", L("l3", -0.1), "Luis Felipe I, rey de Francia · Franz X. Winterhalter, 1839"),
    ("p2", "ulua", L("l4", -0.1), "Bombardeo de San Juan de Ulúa, 1838 · Théodore Gudin, 1839"),
    ("p3", "veracruz", L("l5", -0.1), "Ataque a Veracruz, 5 de diciembre de 1838 · Pharamond Blanchard, 1840"),
    ("p4", "santaanna", L("l6", -0.1), "Antonio López de Santa Anna · Manuel Paris, siglo XIX"),
    ("p5", "pasteleria", L("l9", -0.1), "Caricatura francesa de una pastelería · Charles Pacot, c. 1830"),
]
# Ken Burns per painting: (from scale, to scale, from x%, to x%, from y%, to y%)
KB = {"p0": (1.0, 1.12, 0, 0, 0, -3), "p1": (1.05, 1.18, 0, 0, 4, -2), "p2": (1.0, 1.15, -6, 6, 0, 0),
      "p3": (1.05, 1.2, 4, -4, 0, 2), "p4": (1.0, 1.15, 0, 2, 2, -3), "p5": (1.2, 1.0, 0, 0, -3, 0)}

# ---- the bill: (label, value, time) ----
BILL = [
    ("Valor del local", "&lt; $1 000", W("l2", "mil")),
    ("Remontel pide", "$60 000", W("l2", "sesenta")),
    ("Francia exige", "$600 000", W("l3", "seiscientos")),
    ("Bombardeo", "1838", W("l4", "bombardeo")),
    ("Pierna de Santa Anna", "−1", W("l5", "pierna")),
    ("Funeral de la pierna", "1842", W("l6", "funeral")),
    ("Turba la saca", "1844", W("l7", "desenterro")),
    ("Prótesis", "Illinois", W("l8", "illinois")),
]
T_TOTAL = W("l9", "pierna")


def stage_html():
    imgs = "\n".join(
        f'        <div id="{sid}" class="pt"><img id="{sid}i" src="assets/img/{f}.jpg" alt="" /></div>' for sid, f, _, _ in SCENES)
    plaques = "\n".join(f'      <div id="{sid}q" class="plq">{txt}</div>' for sid, _, _, txt in SCENES)
    rows = "\n".join(f'        <div id="b{k}" class="row"><span>{a}</span><b>{v}</b></div>' for k, (a, v, _) in enumerate(BILL))
    tw = []
    for k, (sid, _, t0, _) in enumerate(SCENES):
        t1 = SCENES[k + 1][2] if k + 1 < len(SCENES) else END
        s0, s1, x0, x1, y0, y1 = KB[sid]
        if k:
            tw.append(f'    tl.fromTo("#{sid}", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.45, ease: "power2.inOut" }}, {t0});')
            tw.append(f'    tl.fromTo("#{sid}q", {{ opacity: 0, y: 20 }}, {{ opacity: 1, y: 0, duration: 0.35, ease: "power2.out" }}, {t0 + 0.3});')
            tw.append(f'    tl.to("#{SCENES[k - 1][0]}q", {{ opacity: 0, duration: 0.2 }}, {t0});')
        tw.append(f'    tl.fromTo("#{sid}i", {{ scale: {s0}, xPercent: {x0}, yPercent: {y0} }}, '
                  f'{{ scale: {s1}, xPercent: {x1}, yPercent: {y1}, duration: {round(t1 - t0 + 0.45, 3)}, ease: "none" }}, {t0});')
    for k, (_, _, t) in enumerate(BILL):
        tw.append(f'    tl.fromTo("#b{k}", {{ opacity: 0, x: -24 }}, {{ opacity: 1, x: 0, duration: 0.25, ease: "power3.out" }}, {t});')
    tw.append(f'    tl.fromTo("#bill", {{ y: 1300 }}, {{ y: 0, duration: 0.45, ease: "power3.out" }}, {round(BILL[0][2] - 0.5, 3)});')
    tw.append(f'    tl.fromTo("#btot", {{ opacity: 0, scale: 1.6 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {T_TOTAL});')
    tw.append(f'    tl.fromTo("#paid span", {{ opacity: 0, scale: 3, rotation: 20 }}, {{ opacity: 1, scale: 1, rotation: -12, duration: 0.22, ease: "power4.in" }}, {round(T_TOTAL + 0.5, 3)});')
    tw.append(f'    tl.fromTo("#hdr", {{ y: 0 }}, {{ y: -420, duration: 0.3, ease: "power3.in" }}, {L("l1", -0.1)});')
    for t in (W("l4", "bombardeo"), W("l5", "canonazo")):  # cannon flash: one bright frame, no shake
        tw.append(f'    tl.fromTo("#flash", {{ opacity: 0.85 }}, {{ opacity: 0, duration: 0.35, ease: "power2.out", immediateRender: false }}, {t});')
    tw.append(f'    tl.fromTo("#leg", {{ opacity: 0, scale: 0.4, rotation: -30 }}, {{ opacity: 1, scale: 1, rotation: -8, duration: 0.35, ease: "back.out(2)" }}, {W("l8", "repuesto")});')
    tw.append(f'    tl.to("#leg", {{ opacity: 0, duration: 0.25 }}, {L("l9", -0.1)});')
    return f'''<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #4A1C24; font-family: "Archivo Black", sans-serif; }}
    #wall {{ position: absolute; inset: 0; background: #4A1C24; }}
    #wain {{ position: absolute; left: 0; right: 0; top: 1300px; bottom: 0; background: #3A151C; border-top: 10px solid #C9A24A; }}
    #frame {{ position: absolute; left: 70px; top: 300px; width: 940px; height: 880px; background: #1B1B2F;
      border: 26px solid #C9A24A; outline: 6px solid #8C6A23; box-shadow: 0 24px 0 rgba(0,0,0,0.35); overflow: hidden; }}
    .pt {{ position: absolute; inset: 0; opacity: 0; }}
    #p0 {{ opacity: 1; }}
    .pt img {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transform-origin: 50% 50%; }}
    .plq {{ position: absolute; left: 110px; top: 1215px; width: 860px; padding: 12px 18px; background: #F3E7C9; color: #3A2A10;
      border: 4px solid #8C6A23; font-family: "Nunito", sans-serif; font-weight: 800; font-size: 30px; line-height: 1.2; text-align: center; opacity: 0; }}
    #p0q {{ opacity: 1; }}
    #flash {{ position: absolute; inset: 0; background: #FFF4D6; opacity: 0; }}
    #bill {{ position: absolute; left: 520px; top: 720px; width: 510px; padding: 18px 22px 26px; background: #FFFDF6; color: #1B1B2F;
      font-family: "Courier New", monospace; font-weight: 700; box-shadow: 10px 10px 0 rgba(0,0,0,0.4); transform: rotate(-2deg);
      clip-path: polygon(0 0, 100% 0, 100% 97%, 95% 100%, 90% 97%, 85% 100%, 80% 97%, 75% 100%, 70% 97%, 65% 100%, 60% 97%, 55% 100%, 50% 97%, 45% 100%, 40% 97%, 35% 100%, 30% 97%, 25% 100%, 20% 97%, 15% 100%, 10% 97%, 5% 100%, 0 97%); }}
    #bill h3 {{ margin: 0 0 10px; font-family: "Archivo Black", sans-serif; font-weight: 400; font-size: 30px; text-align: center; letter-spacing: 1px; }}
    #bill .row {{ display: flex; justify-content: space-between; gap: 10px; font-size: 28px; line-height: 1.4; border-bottom: 2px dashed #B9B2A0; opacity: 0; }}
    #bill .row b {{ white-space: nowrap; }}
    #btot {{ display: flex; justify-content: space-between; margin-top: 10px; font-family: "Archivo Black", sans-serif; font-size: 30px; color: #C2272D; opacity: 0; }}
    #paid {{ position: absolute; left: 560px; top: 880px; width: 400px; text-align: center; }}
    #paid span {{ display: inline-block; font-size: 64px; color: #C2272D; border: 8px solid #C2272D; border-radius: 14px; padding: 6px 18px 2px;
      background: rgba(255,253,246,0.85); opacity: 0; }}
    #leg {{ position: absolute; left: 120px; top: 420px; width: 300px; height: 420px; opacity: 0; }}
    .tag {{ position: absolute; left: 0; width: 1080px; text-align: center; }}
    .tag span {{ display: inline-block; font-size: 92px; line-height: 1; padding: 14px 30px 10px; color: #1B1B2F;
      border: 8px solid #1B1B2F; border-radius: 18px; box-shadow: 8px 8px 0 #1B1B2F; }}
    #hdr {{ position: absolute; left: 0; top: 0; width: 1080px; height: 330px; }}
    #h1 {{ top: 40px; }} #h1 span {{ background: #FFFFFF; }}
    #h2 {{ top: 168px; }} #h2 span {{ background: #FFD23F; }}
  </style>
  <div id="root" data-composition-id="stage" data-width="1080" data-height="1920">
    <div id="wall"></div>
    <div id="wain"></div>
    <div id="frame">
{imgs}
      <div id="flash"></div>
    </div>
{plaques}
    <svg id="leg" viewBox="0 0 300 420">
      <path d="M110 20 H190 L182 250 Q182 300 210 330 L270 350 Q290 360 280 385 L120 385 Q100 380 104 350 L112 250 Z"
        fill="#C9915A" stroke="#1B1B2F" stroke-width="10" stroke-linejoin="round" />
      <path d="M112 90 H188 M112 160 H186" stroke="#8C5A2B" stroke-width="8" />
      <rect x="20" y="395" width="260" height="22" rx="6" fill="#FFD23F" stroke="#1B1B2F" stroke-width="6" />
    </svg>
    <div id="bill">
      <h3>LA CUENTA DEL CHISME</h3>
{rows}
      <div id="btot"><span>TOTAL</span><span>1 PIERNA</span></div>
    </div>
    <div id="paid"><span>¡PAGADO!</span></div>
    <div id="hdr">
      <div id="h1" class="tag"><span>¿UNA GUERRA</span></div>
      <div id="h2" class="tag"><span>POR PASTELES?</span></div>
    </div>
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tw)}
    window.__timelines["stage"] = tl;
  </script>
</template>
'''


def index_html():
    sfx = [("reg1", "el_register", W("l2", "sesenta"), 1.0, 0.5), ("reg2", "el_register", W("l3", "seiscientos"), 1.0, 0.55),
           ("cannon1", "el_cannon", W("l4", "bombardeo"), 1.8, 0.55), ("cannon2", "el_cannon", W("l5", "canonazo"), 1.8, 0.6),
           ("taps", "el_taps", W("l6", "funeral"), 2.5, 0.35), ("crowd", "el_crowd", W("l7", "turba"), 1.8, 0.4),
           ("leg", "pop", W("l8", "repuesto"), 0.72, 0.5), ("total", "impact-bass-1", T_TOTAL, 2.1, 0.45),
           ("end", "whoosh", END - 0.05, 0.57, 0.4), ("end-logo", "pop", END + 0.25, 0.72, 0.5), ("end-title", "pop", END + 0.55, 0.72, 0.45)]
    sfx += [(f"tick{k}", "el_receipt", t, 0.8, 0.3) for k, (_, _, t) in enumerate(BILL) if k not in (1, 2)]
    for _, _, t, _ in SCENES[1:]:
        sfx.append((f"sw{len(sfx)}", "whoosh-short", round(t, 3), 0.57, 0.3))
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
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #4A1C24; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL}" data-width="1080" data-height="1920">
      <div id="stage" data-composition-id="stage" data-composition-src="compositions/stage.html"
        data-start="0" data-duration="{END}" data-track-index="0" data-track-kind="graphics"
        data-width="1080" data-height="1920" style="z-index: 1"></div>
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


if __name__ == "__main__":
    (ROOT / "compositions/stage.html").write_text(stage_html(), encoding="utf-8")
    (ROOT / "index.html").write_text(index_html(), encoding="utf-8")
    print(f"stage + index: {TOTAL} s, end card at {END} s, bill times {[b[2] for b in BILL]}")
