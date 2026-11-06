"""EP08: escribe compositions/stage.html (la historia de Onoda como chat de celular) e index.html, con tiempos por palabra.

  python -I audio/build_video.py     (después de gen_audio_el.py y build.py)

Formato chat (genérico, sin marca de ninguna app): burbujas que entran encadenadas con la narración, el chat se desplaza
para seguir el mensaje nuevo (la "cámara"), el volante de 1945 cae como papel y se transforma en burbuja, el contador de
años corre en la cabecera, y al final el chat vuelve al volante: "Visto 09/03/1974".
"""
import json
import math
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
    hits = [w for w in WORDS if ln["start"] - 0.05 <= w["start"] <= ln["end"] and norm(w["text"]).startswith(norm(word))]
    if len(hits) < k:
        raise SystemExit(f"'{word}' no está en {line}: {[w['text'] for w in WORDS if ln['start'] - 0.05 <= w['start'] <= ln['end']]}")
    return round(hits[k - 1]["start"] + d, 3)


END = round(LINES["l8"]["end"] + 0.9, 2)
TOTAL = round(END + CARD, 2)

# (id, kind, sender, text, time)  kind: in (to Onoda), out (Onoda), sys (centered pill), flyer (paper image bubble)
MSGS = [
    ("mA", "in", "Cuartel General ⭐", "Teniente Onoda: tenemos una misión para usted.", W("l1", "japon")),
    ("m0", "sys", "", "📍 Isla de Lubang, Filipinas · 1944", W("l1", "isla")),
    ("m1", "in", "Cuartel General ⭐", "Misión: resistir en la isla.", W("l1", "orden")),
    ("m2", "in", "Cuartel General ⭐", "Y escucha bien: NUNCA te rindas.", W("l1", "nunca")),
    ("m3", "out", "", "Entendido 🫡", W("l1", "rendirse", d=0.5)),
    ("m4", "flyer", "Aviso 📢", "LA GUERRA TERMINÓ EL 15 DE AGOSTO. ¡BAJEN DE LAS MONTAÑAS!", W("l2", "volantes")),
    ("m5", "out", "", "Ajá, sí, cómo no. Trampa del enemigo 🙄", W("l3", "trampa")),
    ("m6", "out", "", "Sigo en mi puesto 🌴", W("l3", "escondido")),
    ("m7", "in", "Familia ❤️", "Hijo, la guerra ya acabó. Regresa 🙏", W("l4", "diez")),
    ("m8", "sys", "", "Akatsu se rindió · Shimada ✝ · Kozuka ✝", W("l4", "companeros")),
    ("m9", "sys", "", "Ahora eres el único participante", W("l4", "solito")),
    ("m10", "in", "Norio Suzuki 🎒", "¡Hola! ¿Tú eres Onoda? La guerra terminó hace 29 años 😅", W("l5", "suzuki")),
    ("m11", "out", "", "Sin orden de mi comandante, no me rindo 🫡", W("l6", "sin")),
    ("m12", "sys", "", "El mayor Taniguchi (ahora librero 📚) se unió", W("l7", "librero")),
    ("m13", "in", "Mayor Taniguchi", "Teniente Onoda: queda relevado del servicio. 9 de marzo de 1974.", W("l7", "persona")),
]
C = {"l1": L("l1"), "l8": L("l8"), "y1945": W("l2", "termina"), "l4": L("l4"), "y1974": W("l5", "setenta"), "leyo": W("l8", "leyo"),
     "tarde": W("l8", "tarde"), "flyer": W("l2", "volantes"), "end": END}

TOP, BOTTOM, X0, W_BUB = 360, 1400, 48, 760  # chat viewport (captions live at y≈1530)


def height(kind, text, sender):
    if kind == "sys":
        return 74
    if kind == "flyer":
        return 470
    lines = max(1, math.ceil(len(text) / 24))
    return 36 + (40 if sender else 0) + lines * 56 + 34


def layout():
    y, rows = TOP + 30, []
    for mid, kind, sender, text, t in MSGS:
        h = height(kind, text, sender)
        rows.append((mid, kind, sender, text, t, y, h))
        y += h + 22
    return rows


def bubble_html(mid, kind, sender, text, y):
    if kind == "sys":
        return f'      <div id="{mid}" class="msg sys" style="top:{y}px"><span>{text}</span></div>'
    if kind == "flyer":
        return (f'      <div id="{mid}" class="msg in flyerb" style="top:{y}px"><div class="who">{sender}</div>'
                f'<div class="paper">{text}</div><div class="time">1945</div><div id="seen" class="seen">Visto 09/03/1974 ✓✓</div></div>')
    who = f'<div class="who">{sender}</div>' if sender else ""
    ticks = '<b class="ticks">✓✓</b>' if kind == "out" else ""
    return f'      <div id="{mid}" class="msg {kind}" style="top:{y}px">{who}<div class="txt">{text}</div><div class="time">{ticks}</div></div>'


def stage_html():
    rows = layout()
    html = "\n".join(bubble_html(m, k, s, tx, y) for m, k, s, tx, t, y, h in rows)
    tw, scroll = [], 0
    for mid, kind, sender, text, t, y, h in rows:
        bottom = y + h
        need = max(0, bottom - BOTTOM)
        if need > scroll:  # the "camera" follows the newest message: scroll first, the bubble lands just after
            tw.append(f'tl.to("#chat", {{ y: {-need}, duration: 0.35, ease: "power2.inOut" }}, {round(t - 0.12, 3)});')
            scroll = need
        if kind == "out":
            tw.append(f'tl.to("#typing", {{ opacity: 1, duration: 0.1 }}, {round(t - 0.7, 3)});')
            tw.append(f'tl.to("#typing", {{ opacity: 0, duration: 0.1 }}, {round(t - 0.05, 3)});')
        origin = {"out": "100% 100%", "in": "0% 100%", "sys": "50% 50%"}.get(kind, "0% 100%")
        if kind == "flyer":
            continue
        tw.append(f'tl.fromTo("#{mid}", {{ opacity: 0, scale: 0.5, transformOrigin: "{origin}" }}, '
                  f'{{ opacity: 1, scale: 1, duration: 0.28, ease: "back.out(1.8)" }}, {round(t, 3)});')
    # the 1945 flyer falls as paper, then shrinks into its chat bubble (object → next scene)
    fy = next(y for m, k, s, tx, t, y, h in rows if m == "m4")
    f0 = C["flyer"]
    tw += [
        f'tl.fromTo("#bigflyer", {{ opacity: 1, y: -1400, rotation: -14 }}, {{ opacity: 1, y: 0, rotation: 4, duration: 0.7, ease: "power2.out" }}, {round(f0 - 0.5, 3)});',
        f'tl.to("#bigflyer", {{ rotation: -2, duration: 0.3, ease: "sine.inOut" }}, {round(f0 + 0.2, 3)});',
        f'tl.to("#bigflyer", {{ scale: 0.42, x: -150, y: {fy - 760}, opacity: 0, duration: 0.45, ease: "power3.in" }}, {round(f0 + 1.3, 3)});',
        f'tl.fromTo("#m4", {{ opacity: 0, scale: 0.8, transformOrigin: "0% 0%" }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2)" }}, {round(f0 + 1.6, 3)});',
    ]
    # year counter in the header
    for a, b, t0, dur in [(1944, 1945, C["y1945"], 0.4), (1945, 1973, C["l4"], 6.5), (1973, 1974, C["y1974"], 0.4)]:
        tw.append(f'tl.to(YEAR, {{ v: {b}, duration: {dur}, ease: "none", onUpdate: showYear }}, {round(t0, 3)});')
    tw.append(f'tl.fromTo("#yearchip", {{ scale: 1 }}, {{ scale: 1.15, duration: 0.2, yoyo: true, repeat: 1 }}, {round(C["l4"], 3)});')
    # the payoff: the chat scrolls back up to the flyer, punches in, "Visto 09/03/1974"
    back = max(0, fy - 520)
    tw += [
        f'tl.to("#chat", {{ y: {-back}, duration: 0.6, ease: "power3.inOut" }}, {round(C["l8"], 3)});',
        f'tl.fromTo("#zoom", {{ scale: 1 }}, {{ scale: 1.18, transformOrigin: "30% 40%", duration: 0.6, ease: "power2.out" }}, {round(C["l8"] + 0.3, 3)});',
        f'tl.fromTo("#seen", {{ clipPath: "inset(0px 100% 0px 0px)" }}, {{ clipPath: "inset(0px 0% 0px 0px)", duration: 0.4, ease: "power3.out" }}, {round(C["leyo"], 3)});',
        f'tl.fromTo("#late span", {{ opacity: 0, scale: 3, rotation: 18 }}, {{ opacity: 1, scale: 1, rotation: -8, duration: 0.2, ease: "power4.in" }}, {round(C["tarde"], 3)});',
        f'tl.fromTo("#status2", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.15 }}, {round(C["leyo"], 3)});',
        'tl.fromTo("#h2", { clipPath: "inset(-30px 1200px -30px -30px)" }, { clipPath: "inset(-30px -30px -30px -30px)", duration: 0.3, ease: "power3.out" }, 0.05);',
        f'tl.fromTo("#hook", {{ clipPath: "inset(-30px -30px -30px -30px)" }}, {{ clipPath: "inset(-30px -30px -30px 1200px)", duration: 0.3, ease: "power3.in", immediateRender: false }}, {round(C["l1"] - 0.2, 3)});',
    ]
    return STAGE.replace("__MSGS__", html).replace("__TW__", "\n".join("    " + x for x in tw))


STAGE = r'''<template>
  <style>
    #root { position: absolute; inset: 0; overflow: hidden; font-family: "Archivo Black", sans-serif;
      background-color: #17352A;
      background-image: radial-gradient(ellipse 60px 26px at 30px 30px, #1F4535 98%, transparent 100%),
        radial-gradient(ellipse 26px 60px at 120px 110px, #1F4535 98%, transparent 100%),
        radial-gradient(ellipse 50px 20px at 170px 40px, #22503D 98%, transparent 100%);
      background-size: 220px 180px; }
    #view { position: absolute; inset: 0; clip-path: inset(345px 0px 470px 0px); }
    #zoom { position: absolute; inset: 0; }
    #chat { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
    .msg { position: absolute; max-width: 760px; padding: 22px 28px 14px; border: 6px solid #1B1B2F; border-radius: 28px;
      box-shadow: 6px 6px 0 #1B1B2F; opacity: 0; }
    .msg.in { left: 48px; background: #FFFFFF; border-bottom-left-radius: 6px; }
    .msg.out { right: 48px; background: #F2B33D; border-bottom-right-radius: 6px; }
    .msg .who { font-size: 30px; color: #C1440E; margin-bottom: 6px; }
    .msg .txt { font-family: "Inter", sans-serif; font-weight: 800; font-size: 44px; line-height: 1.25; color: #1B1B2F; }
    .msg .time { text-align: right; font-family: "Inter", sans-serif; font-weight: 700; font-size: 24px; color: #5B5B6E; margin-top: 4px; }
    .ticks { color: #0B3F73; font-weight: 900; }
    .msg.sys { left: 0; width: 1080px; max-width: none; padding: 0; border: 0; box-shadow: none; text-align: center; }
    .msg.sys span { display: inline-block; font-family: "Inter", sans-serif; font-weight: 800; font-size: 32px; color: #1B1B2F;
      background: #DCEFE3; border: 5px solid #1B1B2F; border-radius: 18px; padding: 10px 22px; }
    .flyerb { width: 560px; }
    .paper { margin: 6px 0; height: 330px; padding: 34px 30px; background: #F3E6C4; border: 4px solid #1B1B2F; transform: rotate(-2deg);
      font-size: 42px; line-height: 1.15; color: #7B1E1E; text-align: center; display: flex; align-items: center; }
    .seen { font-family: "Inter", sans-serif; font-weight: 900; font-size: 30px; color: #2C7FB8; clip-path: inset(0px 100% 0px 0px); }
    #bigflyer { position: absolute; left: 140px; top: 520px; width: 800px; height: 760px; padding: 70px 60px; background: #F3E6C4;
      border: 8px solid #1B1B2F; box-shadow: 14px 14px 0 rgba(0,0,0,0.35); font-size: 84px; line-height: 1.1; color: #7B1E1E;
      text-align: center; display: flex; flex-direction: column; justify-content: center; opacity: 0; }
    #bigflyer small { font-size: 40px; color: #1B1B2F; margin-top: 30px; }
    #head { position: absolute; left: 0; top: 0; width: 1080px; height: 200px; background: #1B1B2F; display: flex; align-items: center;
      padding: 40px 40px 0; gap: 26px; }
    #avatar { width: 120px; height: 120px; border-radius: 60px; background: #6E8B4E; border: 6px solid #F2B33D; flex: none; }
    #name { color: #FFFFFF; font-size: 44px; line-height: 1.1; }
    .status { position: absolute; left: 186px; top: 146px; font-family: "Inter", sans-serif; font-weight: 700; font-size: 30px; color: #A9C7B4; }
    #typing, #status2 { opacity: 0; color: #F2B33D; background: #1B1B2F; width: 700px; }
    #status2 { background: #1B1B2F; color: #7CFFB0; }
    #yearchip { position: absolute; left: 0; top: 222px; width: 1080px; text-align: center; }
    #yearchip span { display: inline-block; font-size: 72px; padding: 8px 34px 2px; background: #FFFFFF; color: #1B1B2F; border: 7px solid #1B1B2F;
      border-radius: 18px; box-shadow: 7px 7px 0 #1B1B2F; }
    #hook { position: absolute; left: 0; top: 560px; width: 1080px; }
    .tags { width: 1080px; text-align: center; margin-bottom: 26px; }
    .tags span { display: inline-block; white-space: nowrap; font-size: 64px; line-height: 1; padding: 16px 30px 10px; color: #1B1B2F;
      border: 8px solid #1B1B2F; border-radius: 18px; box-shadow: 8px 8px 0 #1B1B2F; }
    #h1 span { background: #FFFFFF; } #h2 span { background: #F2B33D; }
    #h2 { clip-path: inset(-30px 1200px -30px -30px); }
    #late { position: absolute; left: 0; top: 1150px; width: 1080px; text-align: center; }
    #late span { display: inline-block; font-size: 110px; color: #E63946; border: 14px solid #E63946; border-radius: 22px; padding: 10px 30px 2px;
      background: rgba(255,253,246,0.94); opacity: 0; }
  </style>
  <div id="root" data-composition-id="stage" data-width="1080" data-height="1920" data-layout-allow-overflow>
    <div id="view">
    <div id="zoom">
      <div id="chat">
__MSGS__
      </div>
    </div>
    </div>
    <div id="bigflyer" data-layout-allow-overlap>LA GUERRA TERMINÓ EL 15 DE AGOSTO<small>¡Bajen de las montañas!</small></div>
    <div id="head">
      <svg id="avatar" viewBox="0 0 120 120"><circle cx="60" cy="70" r="34" fill="#F2C9A0" stroke="#1B1B2F" stroke-width="5"/>
        <path d="M18 62 Q22 18 60 16 Q98 18 102 62 Z" fill="#5E6B3A" stroke="#1B1B2F" stroke-width="5"/>
        <rect x="14" y="58" width="92" height="10" rx="5" fill="#4A5530" stroke="#1B1B2F" stroke-width="4"/>
        <circle cx="48" cy="78" r="4" fill="#1B1B2F"/><circle cx="72" cy="78" r="4" fill="#1B1B2F"/>
        <path d="M48 94 Q60 90 72 94" stroke="#1B1B2F" stroke-width="4" fill="none"/></svg>
      <div id="name">Tte. Hiroo Onoda 🪖</div>
    </div>
    <div class="status">últ. vez en 1944 · sin señal</div>
    <div id="typing" class="status" data-layout-allow-overlap>escribiendo…</div>
    <div id="status2" class="status" data-layout-allow-overlap>en línea · por fin 😅</div>
    <div id="yearchip"><span>📅 <b id="year">1944</b></span></div>
    <div id="hook">
      <div id="h1" class="tags"><span>¿Y SI NADIE TE AVISA</span></div>
      <div id="h2" class="tags"><span>QUE LA GUERRA TERMINÓ?</span></div>
    </div>
    <div id="late"><span>¡29 AÑOS TARDE!</span></div>
  </div>
  <script>
    const YEAR = { v: 1944 };
    const yearEl = document.getElementById("year");
    function showYear() { yearEl.textContent = String(Math.round(YEAR.v)); }
    const tl = gsap.timeline({ paused: true });
__TW__
    window.__timelines["stage"] = tl;
  </script>
</template>
'''


def index_html():
    sfx = [("jungle", "el_jungle", 0.0, 3.0, 0.3)]
    for mid, kind, sender, text, t in MSGS:
        if kind == "out":
            sfx += [(f"typ-{mid}", "el_typing", t - 0.7, 0.8, 0.3), (f"snd-{mid}", "el_send", t, 0.5, 0.45)]
        elif kind in ("in", "sys"):
            sfx.append((f"ding-{mid}", "el_ding", t, 0.6, 0.45 if kind == "in" else 0.3))
    sfx += [("paper", "el_paper", C["flyer"] - 0.5, 1.5, 0.5), ("clock", "el_clock", C["l4"], 3.0, 0.4),
            ("steps", "el_footsteps", C["y1974"], 1.2, 0.35), ("back", "whoosh", C["l8"], 0.57, 0.4),
            ("late", "impact-bass-1", C["tarde"], 2.1, 0.4), ("tada", "el_tada", C["leyo"], 1.5, 0.45),
            ("end", "whoosh", END - 0.05, 0.57, 0.4), ("end-logo", "pop", END + 0.25, 0.72, 0.5), ("end-title", "sparkle", END + 0.55, 1.8, 0.35)]
    rows = [f'      <audio id="sfx-{i}" class="clip" src="assets/sfx/{f}.mp3" data-start="{round(max(t, 0), 3)}" data-duration="{d}" '
            f'data-track-index="{5 + k % 6}" data-volume="{v}"></audio>' for k, (i, f, t, d, v) in enumerate(sfx)]
    return f'''<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #17352A; }}
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
    (ROOT / "compositions/stage.html").write_text(stage_html(), encoding="utf-8")
    (ROOT / "index.html").write_text(index_html(), encoding="utf-8")
    print(f"stage + index: {TOTAL} s, end card at {END} s; cues {C}")
