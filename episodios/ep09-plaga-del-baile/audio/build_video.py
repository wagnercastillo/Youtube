"""EP09: escribe compositions/stage.html (la plaga del baile como videojuego pixel art) e index.html, con tiempos por palabra.

  python -I audio/build_video.py     (después de gen_audio_el.py y build.py)

Un canvas de 180×320 se dibuja por cuadro desde hf-seek y se escala ×6 con image-rendering: pixelated. Cámara que recorre la
calle (sigue a Troffea, luego a la multitud y al escenario), flechas de ritmo al compás de 120 bpm, contador de bailarines,
barra de ENERGÍA que se vacía, el escenario se transforma en la capilla de San Vito, y "¿CONTINUAR?" al final.
Rótulos HTML con máscara (clip-path); todo atado a palabras de la narración.
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
    hits = [w for w in WORDS if ln["start"] - 0.05 <= w["start"] <= ln["end"] and norm(w["text"]).startswith(norm(word))]
    if len(hits) < k:
        raise SystemExit(f"'{word}' no está en {line}: {[w['text'] for w in WORDS if ln['start'] - 0.05 <= w['start'] <= ln['end']]}")
    return round(hits[k - 1]["start"] + d, 3)


END = round(LINES["l8"]["end"] + 0.9, 2)
TOTAL = round(END + CARD, 2)
C = {
    "l1": L("l1"), "troffea": W("l1", "troffea"), "bailar1": W("l1", "bailar"), "l2": L("l2"), "dias": W("l2", "dias"),
    "l3": L("l3"), "decenas": W("l3", "decenas"), "agosto": W("l3", "agosto"), "cuatro": W("l3", "cuatrocientas"),
    "l4": L("l4"), "sangre": W("l4", "sangre"), "mas": W("l4", "mas"), "l5": L("l5"), "musicos": W("l5", "musicos"),
    "escenario": W("l5", "escenario"), "l6": L("l6"), "agotados": W("l6", "agotados"), "desmayados": W("l6", "desmayados"),
    "l7": L("l7"), "santuario": W("l7", "santuario"), "septiembre": W("l7", "septiembre"), "apago": W("l7", "apago"),
    "l8": L("l8"), "nadie": W("l8", "nadie"), "end": END,
}
BANNERS = [  # id, text, in, out
    ("b1", "NIVEL 1 · ESTRASBURGO 1518", C["l1"] + 0.1, C["l2"] - 0.1),
    ("b2", "JUGADORA 1: FRAU TROFFEA", C["troffea"], C["l3"] - 0.1),
    ("b4", "DIAGNÓSTICO: «SANGRE CALIENTE»", C["sangre"], C["mas"] - 0.1),
    ("b4b", "CURA: ¡BAILAR MÁS! 🎶", C["mas"], C["l5"] + 0.6),
    ("b5", "POWER-UP: MÚSICOS + ESCENARIO", C["musicos"], C["l6"]),
    ("b7", "NIVEL FINAL: SANTUARIO DE SAN VITO", C["santuario"], C["l8"]),
    ("b8", "CAUSA: ??? · NADIE LO SABE", C["nadie"], C["end"] - 0.15),
]
IN_CLIP, SHOW, OUT_CLIP = "inset(-30px 1200px -30px -30px)", "inset(-30px -30px -30px -30px)", "inset(-30px -30px -30px 1200px)"


def stage_html():
    banners = "\n".join(f'    <div id="{i}" class="ban"><span>{t}</span></div>' for i, t, _, _ in BANNERS)
    tw = ['tl.fromTo("#h2", { clipPath: "' + IN_CLIP + '" }, { clipPath: "' + SHOW + '", duration: 0.3, ease: "power3.out" }, 0.05);',
          f'tl.fromTo("#hook", {{ clipPath: "{SHOW}" }}, {{ clipPath: "{OUT_CLIP}", duration: 0.3, ease: "power3.in", immediateRender: false }}, {C["l1"] - 0.2});']
    for i, _, a, b in BANNERS:
        tw += [f'tl.fromTo("#{i}", {{ clipPath: "{IN_CLIP}" }}, {{ clipPath: "{SHOW}", duration: 0.32, ease: "power3.out" }}, {round(a, 3)});',
               f'tl.fromTo("#{i}", {{ clipPath: "{SHOW}" }}, {{ clipPath: "{OUT_CLIP}", duration: 0.22, ease: "power3.in", immediateRender: false }}, {round(b, 3)});']
    tw.append(f'tl.fromTo("#cont", {{ opacity: 0, scale: 2 }}, {{ opacity: 1, scale: 1, duration: 0.25, ease: "back.out(2)" }}, {round(C["nadie"] + 0.4, 3)});')
    return STAGE.replace("__C__", json.dumps(C)).replace("__BANNERS__", banners).replace("__TW__", "\n".join("    " + x for x in tw))


STAGE = r'''<template>
  <style>
    #root { position: absolute; inset: 0; overflow: hidden; background: #1A1033; font-family: "Archivo Black", sans-serif; }
    #px { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; image-rendering: pixelated; }
    .ban { position: absolute; left: 0; top: 330px; width: 1080px; text-align: center; clip-path: inset(-30px 1200px -30px -30px); }
    .ban span { display: inline-block; max-width: 980px; font-size: 50px; line-height: 1.1; padding: 14px 26px 8px; background: #1B1B2F; color: #FFE14D;
      border: 8px solid #FFFFFF; box-shadow: 8px 8px 0 #000000; letter-spacing: 1px; }
    #b4b span, #b5 span { color: #7CFFB0; }
    #b8 span { color: #FF6B8B; }
    #hook { position: absolute; left: 0; top: 560px; width: 1080px; }
    .tags { width: 1080px; text-align: center; margin-bottom: 26px; }
    .tags span { display: inline-block; white-space: nowrap; font-size: 70px; line-height: 1; padding: 16px 30px 10px; color: #1B1B2F;
      border: 8px solid #1B1B2F; box-shadow: 8px 8px 0 #000000; }
    #h1 span { background: #FFFFFF; } #h2 span { background: #FFE14D; }
    #h2 { clip-path: inset(-30px 1200px -30px -30px); }
    #cont { position: absolute; left: 0; top: 1150px; width: 1080px; text-align: center; opacity: 0; }
    #cont span { display: inline-block; font-size: 64px; padding: 14px 30px 8px; background: #000000; color: #FFFFFF; border: 8px solid #FFE14D; }
  </style>
  <div id="root" data-composition-id="stage" data-width="1080" data-height="1920">
    <canvas id="px" width="180" height="320"></canvas>
__BANNERS__
    <div id="hook">
      <div id="h1" class="tags"><span>¿Y SI NO PUDIERAS</span></div>
      <div id="h2" class="tags"><span>DEJAR DE BAILAR?</span></div>
    </div>
    <div id="cont"><span>¿CONTINUAR? ▶ SÍ</span></div>
  </div>
  <script>
    const C = __C__;
    const cv = document.getElementById("px"), g = cv.getContext("2d");
    g.imageSmoothingEnabled = false;
    const clamp = (k) => Math.min(Math.max(k, 0), 1);
    const smooth = (k) => { k = clamp(k); return k * k * (3 - 2 * k); };
    const lerp = (a, b, k) => a + (b - a) * k;
    const since = (t, a) => t - a;
    const BEAT = 0.5;  // 120 bpm
    function track(keys, t) {
      let i = 0;
      while (i + 1 < keys.length && t >= keys[i + 1][0]) i++;
      if (i === 0) return keys[0].slice(2);
      const cur = keys[i], prev = keys[i - 1], k = smooth((t - cur[0]) / cur[1]);
      return cur.slice(2).map((v, j) => lerp(prev[j + 2], v, k));
    }
    function R(x, y, w, h, c) { g.fillStyle = c; g.fillRect(Math.round(x), Math.round(y), w, h); }

    // tiny 3×5 pixel font for the HUD
    const FONT = { "0": "111101101101111", "1": "010110010010111", "2": "111001111100111", "3": "111001111001111", "4": "101101111001001",
      "5": "111100111001111", "6": "111100111101111", "7": "111001001001001", "8": "111101111101111", "9": "111101111001111",
      "A": "010101111101101", "B": "110101110101110", "C": "011100100100011", "D": "110101101101110", "E": "111100110100111",
      "F": "111100110100100", "G": "011100101101011", "I": "111010010010111", "L": "100100100100111", "N": "101111111111101",
      "O": "010101101101010", "P": "110101110100100", "R": "110101110101101", "S": "011100010001110", "T": "111010010010010",
      "V": "101101101101010", "Y": "101101010010010", "M": "101111111101101", "U": "101101101101111", "K": "101101110101101",
      "!": "010010010000010", ":": "000010000010000", " ": "000000000000000", "?": "110001010000010", "X": "101101010101101", "H": "101101111101101" };
    function text(s, x, y, c, sc) {
      sc = sc || 1;
      for (const ch of s) { const f = FONT[ch] || FONT[" "]; for (let i = 0; i < 15; i++) if (f[i] === "1") R(x + (i % 3) * sc, y + Math.floor(i / 3) * sc, sc, sc, c); x += 4 * sc; }
    }

    // a dancer: rectangles, two poses keyed to the beat; tired = slumped, out = lying down
    function dancer(x, y, col, ph, tired, out) {
      const skin = "#F2C9A0", ink = "#1B1B2F";
      if (out) { R(x - 5, y - 3, 10, 3, col); R(x + 5, y - 3, 3, 3, skin); R(x - 7, y - 2, 2, 2, ink); return; }
      const up = ph % 2 === 0, b = tired ? 1 : (up ? -1 : 0);
      R(x - 2, y - 13 + b, 4, 4, skin); R(x - 2, y - 14 + b, 4, 1, "#6D4C2F");
      R(x - 3, y - 9 + b, 6, 6, col);
      if (tired) { R(x - 4, y - 7, 1, 4, skin); R(x + 3, y - 7, 1, 4, skin); }
      else if (up) { R(x - 4, y - 13 + b, 1, 4, skin); R(x + 3, y - 13 + b, 1, 4, skin); }
      else { R(x - 5, y - 8, 2, 1, skin); R(x + 3, y - 10, 2, 1, skin); }
      if (up && !tired) { R(x - 3, y - 3, 1, 3, ink); R(x + 2, y - 4, 2, 2, ink); } else { R(x - 2, y - 3, 1, 3, ink); R(x + 1, y - 3, 1, 3, ink); }
    }

    const COLS = ["#E63946", "#2C7FB8", "#2BB673", "#F2B33D", "#9B5DE5", "#FF6B8B", "#00BBF9", "#F15BB5"];
    // camera x (world 0..420) and zoom
    const CAM = [[0, 1, 30, 1.3], [C.l1, 0.8, 0, 1], [C.troffea, 0.6, 0, 2.4], [C.l3, 0.8, 60, 1], [C.l5, 0.9, 200, 1], [C.l7, 0.9, 240, 1], [C.l8, 0.8, 120, 1]];

    function count(t) {
      if (t < C.bailar1) return 0;
      if (t < C.decenas) return 1;
      if (t < C.agosto) return Math.round(lerp(1, 40, smooth(since(t, C.decenas) / 1.2)));
      if (t < C.santuario) return Math.round(lerp(40, 400, smooth(since(t, C.cuatro) / 1.0)));
      return Math.round(lerp(400, 0, smooth(since(t, C.apago) / 1.2)));
    }

    function world(t, cx, z) {
      const beat = Math.floor(t / BEAT), ph = beat;
      const dancing = t >= C.bailar1 && t < C.apago;
      const tired = t >= C.agotados && t < C.santuario;
      g.save();
      g.translate(90, 230); g.scale(z, z); g.translate(-90 - cx, -230);
      // sky + cathedral spire (parallax)
      R(cx - 60, -40, 400, 300, "#2B1E5C");
      for (let i = 0; i < 30; i++) R(((i * 37) % 400) + cx * 0.5 - 40, 50 + (i * 23) % 60, 1, 1, "#FFE14D");
      R(cx * 0.6 + 120, 70, 14, 160, "#4A3B7A"); R(cx * 0.6 + 124, 40, 6, 30, "#4A3B7A"); R(cx * 0.6 + 126, 30, 2, 10, "#4A3B7A");
      // half-timbered houses
      for (let i = -1; i < 12; i++) {
        const hx = i * 44, hh = 70 + (i % 3) * 14;
        R(hx, 230 - hh, 40, hh, i % 2 ? "#F3E6C4" : "#E9D3A6");
        R(hx, 230 - hh, 40, 3, "#5A3A22"); R(hx, 230 - hh / 2, 40, 2, "#5A3A22"); R(hx + 19, 230 - hh, 2, hh, "#5A3A22");
        for (let k = 0; k < 6; k++) R(hx + 4 + k * 6, 230 - hh - 6 + Math.abs(3 - k) * 2, 6, 6 - Math.abs(3 - k) * 2, "#B5452A");
        R(hx + 6, 230 - hh + 10, 8, 8, (t > C.l4 && t < C.l7 && (i + beat) % 3 === 0) ? "#FFE14D" : "#2C3E66");
        R(hx + 26, 230 - hh + 10, 8, 8, "#2C3E66");
      }
      // cobblestones
      R(cx - 60, 230, 400, 90, "#6B6478");
      for (let i = 0; i < 80; i++) R((i * 13) % 400 + Math.floor(cx / 400) * 400 - 40, 234 + (i * 7) % 20, 5, 2, "#7D7590");
      // stage → chapel of St Vitus (the stage morphs into the chapel)
      const st = smooth(since(t, C.escenario) / 0.5), ch = smooth(since(t, C.santuario) / 0.6);
      if (st > 0) {
        const sx = 250, sw = 70;
        if (ch < 1) { R(sx, 230 - 14 * st, sw, 14 * st, "#8A5A2B"); R(sx, 230 - 14 * st, sw, 2, "#5A3A22"); }
        if (ch > 0) {
          const hh = 60 * ch;
          R(sx + 5, 230 - hh, sw - 10, hh, "#D9D2C3");
          for (let r = 0; r < 14; r++) R(sx + 2 + r * 2.2, 230 - hh - r * 2 * ch, sw - 4 - r * 4.4, 2, "#8C3B2E");
          R(sx + sw / 2 - 1, 230 - hh - 34 * ch, 2, 10, "#FFE14D"); R(sx + sw / 2 - 4, 230 - hh - 31 * ch, 8, 2, "#FFE14D");
          R(sx + sw / 2 - 6, 230 - 22 * ch, 12, 22 * ch, "#5A3A22");
        }
        if (ch < 0.5 && t >= C.musicos) for (let m = 0; m < 3; m++) {  // musicians on the stage
          const mx = sx + 14 + m * 20, my = 230 - 14;
          R(mx - 2, my - 12, 4, 4, "#F2C9A0"); R(mx - 3, my - 8, 6, 8, ["#7B1E1E", "#1E4D7B", "#2E6B2E"][m]);
          if (m === 0) R(mx + 3, my - 6 + (beat % 2), 4, 4, "#C9A13B");
          if (m === 1) R(mx + 3, my - 10, 6, 1, "#E9E2CF");
          if (m === 2) R(mx - 7, my - 6, 4, 5, "#8A5A2B");
        }
      }
      // dancers
      const n = count(t), shown = Math.max(Math.min(n, 44), t >= C.l1 ? 1 : 0);
      for (let k = 0; k < shown; k++) {
        const row = Math.floor(k / 11), col = k % 11;
        const x = k === 0 ? 90 : 40 + col * 22 + (row % 2) * 11 + row * 6, y = 238 + row * 6;
        const toChapel = smooth(since(t, C.santuario) / 1.5);
        const fx = lerp(x, 265 + (k % 6) * 8, toChapel * (k < 18 ? 1 : 0));
        if (k >= 18 && toChapel > 0.5) continue;
        const out = tired && t >= C.desmayados && k % 3 === 1;
        dancer(fx, y, COLS[k % COLS.length], dancing ? ph + (k % 2) : 1, tired || !dancing, out);
      }
      g.restore();
    }

    function hud(t) {
      R(0, 0, 180, 30, "#000000"); R(0, 30, 180, 1, "#FFFFFF");
      text("BAILARINES:", 4, 4, "#FFFFFF"); text(String(count(t)), 50, 4, "#FFE14D");
      let e = 1;
      if (t >= C.l6) e = lerp(1, 0.08, smooth(since(t, C.l6) / 2.2));
      if (t >= C.santuario) e = lerp(0.08, 1, smooth(since(t, C.santuario) / 1.5));
      text("ENERGIA", 4, 14, "#FFFFFF");
      R(34, 14, 60, 6, "#3A3A44"); R(34, 14, Math.round(58 * e), 6, e < 0.3 ? "#E63946" : "#2BB673");
      text("1518", 150, 4, "#7CFFB0");
      const lvl = t < C.l3 ? "1" : t < C.l5 ? "2" : t < C.l7 ? "3" : "X";
      text("NIVEL " + lvl, 130, 14, "#FFFFFF");
    }

    // rhythm arrows rise to the target row while people dance
    const DIRS = ["#FF6B8B", "#00BBF9", "#7CFFB0", "#FFE14D"];
    function arrow(x, y, d, c) {
      const pts = [[0, -3], [-3, 0], [3, 0], [-1, 0], [1, 0]];
      if (d === 0) { R(x - 1, y - 3, 3, 7, c); R(x - 3, y - 1, 7, 2, c); R(x - 2, y - 2, 5, 1, c); }
      if (d === 1) { R(x - 1, y - 3, 3, 7, c); R(x - 3, y + 1, 7, 2, c); R(x - 2, y + 3, 5, 1, c); }
      if (d === 2) { R(x - 3, y - 1, 7, 3, c); R(x - 3, y - 3, 2, 7, c); }
      if (d === 3) { R(x - 3, y - 1, 7, 3, c); R(x + 2, y - 3, 2, 7, c); }
    }
    function rhythm(t) {
      if (t < C.bailar1 || t >= C.apago) return;
      const ty = 44;
      for (let d = 0; d < 4; d++) { R(52 + d * 22 - 5, ty - 5, 11, 11, "#1B1B2F"); arrow(52 + d * 22, ty, d, "#555577"); }
      const b0 = Math.floor(t / BEAT);
      for (let k = b0 - 1; k < b0 + 6; k++) {
        const d = (k * 7 + 3) % 4, y = ty + (k * BEAT - t) * 60;
        if (y < ty - 2 || y > 220) continue;
        arrow(52 + d * 22, y, d, DIRS[d]);
      }
      const hit = t - b0 * BEAT;
      if (hit < 0.22) { const words = t > C.l6 && t < C.santuario ? "MISS" : (b0 % 3 ? "PERFECT!" : "GREAT!"); text(words, 70, 56, t > C.l6 && t < C.santuario ? "#E63946" : "#FFE14D"); }
    }

    function draw(t) {
      g.clearRect(0, 0, 180, 320);
      const [cx, z] = track(CAM, t);
      world(t, cx, z);
      rhythm(t);
      hud(t);
      if (t >= C.nadie) { const q = Math.floor(t * 6) % 2; text("???", 66, 120, q ? "#FF6B8B" : "#FFE14D", 4); }
    }
    draw(0);
    window.addEventListener("hf-seek", (e) => draw(e.detail.time));

    const tl = gsap.timeline({ paused: true });
__TW__
    window.__timelines["stage"] = tl;
  </script>
</template>
'''


def index_html():
    sfx = [("start", "el_start", 0.05, 1.2, 0.4), ("coin1", "el_coin", C["bailar1"], 0.6, 0.45), ("crowd", "el_crowd8", C["cuatro"], 1.5, 0.4),
           ("level2", "el_levelup", C["l3"], 1.5, 0.35), ("coin2", "el_coin", C["mas"], 0.6, 0.45), ("level3", "el_levelup", C["escenario"], 1.5, 0.4),
           ("power", "el_powerdown", C["l6"] + 0.4, 1.5, 0.45), ("over", "el_gameover", C["desmayados"], 2.0, 0.35),
           ("bell", "el_bell", C["santuario"], 1.5, 0.45), ("glitch", "el_glitch", C["nadie"], 1.0, 0.45),
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
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #1A1033; }}
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
