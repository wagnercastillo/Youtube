"""EP17: escribe compositions/stage.html (Colón y la Tierra plana como COLLAGE DE RECORTES estilo Gilliam) e index.html.

  python -I audio/build_video.py     (después de gen_audio_el.py y build.py)

Canvas 1080×1920 por cuadro. Cabezas = retratos reales de dominio público (assets/recortes/, ver fuentes.json) recortados con
"tijera": polígono fijo con borde blanco de papel y sombra dura. La mandíbula es la mitad inferior del mismo retrato y abre a
bisagra en 3 poses (cerrada / media / abierta) según mouth.json, sin intermedios. Los personajes se mueven a saltos (2–3 poses);
solo la cámara y los cambios de hoja son suaves. Rótulos HTML con máscara. Todo anclado a palabras con W()/L().
"""
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORDS = json.loads((ROOT / "transcript.json").read_text(encoding="utf-8"))
LINES = {l["id"]: l for l in json.loads((ROOT / "assets/lines.json").read_text(encoding="utf-8"))}
MOUTH = json.loads((ROOT / "assets/mouth.json").read_text(encoding="utf-8"))
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


END = round(LINES["l10"]["end"] + 0.9, 2)
TOTAL = round(END + CARD, 2)
C = {"colon": W("l0", "colon"), "mentira": W("l0", "mentira"), "cuentas": W("l0", "cuentas"), "muere": W("l0", "muere"),
     "l1": L("l1"), "mil": W("l1", "mil"), "griego": W("l1", "griego"), "palo": W("l1", "palo"), "sombra": W("l1", "sombra"), "atino": W("l1", "atino"),
     "l2": L("l2"), "reyes": W("l2", "reyes"), "mundo": W("l2", "mundo"), "redondo": W("l2", "redondo"),
     "l3": L("l3"), "plana": W("l3", "plana"), "chiquita": W("l3", "chiquita"), "japon": W("l3", "japon"), "nomas": W("l3", "nomas"),
     "l4": L("l4"), "error": W("l4", "error"), "cuarta": W("l4", "cuarta"), "japon4": W("l4", "japon"), "cuatro": W("l4", "cuatro"), "veinte": W("l4", "veinte"),
     "l5": L("l5"), "salamanca": W("l5", "salamanca"), "no5": W("l5", "no"), "hambre": W("l5", "hambre"),
     "l6": L("l6"), "mori": W("l6", "mori"), "lugar": W("l6", "lugar"),
     "l7": L("l7"), "america": W("l7", "america"), "murio": W("l7", "murio"), "asia": W("l7", "asia"),
     "l8": L("l8"), "plana8": W("l8", "plana"), "escritor": W("l8", "escritor"), "washington": W("l8", "washington"), "mil8": W("l8", "mil"),
     "l9": L("l9"), "novela": W("l9", "novela"), "drama": W("l9", "drama"),
     "l10": L("l10"), "escuela": W("l10", "escuela"), "tu": W("l10", "tu"), "creiste": W("l10", "creiste"), "end": END}
BANNERS = [
    ("b1", "ERATÓSTENES · c. 240 a. C.", C["griego"], C["l2"] - 0.1),
    ("b2", "FUENTE: SACROBOSCO, «DE SPHAERA» (c. 1230)", C["reyes"], C["l3"] - 0.1),
    ("b3", "CRISTÓBAL COLÓN · 1492", C["l3"] + 0.1, C["l4"] - 0.1),
    ("b4", "JAPÓN: 4,500 km (COLÓN) · ~20,000 km (REAL)", C["cuatro"], C["l5"] - 0.1),
    ("b5", "SALAMANCA: «QUEDA DEMASIADO LEJOS»", C["salamanca"], C["l6"] - 0.1),
    ("b6", "MURIÓ EN 1506 JURANDO QUE ERA ASIA", C["murio"], C["l8"] - 0.1),
    ("b7", "W. IRVING, «VIDA Y VIAJES DE COLÓN», 1828", C["washington"], C["l10"] - 0.1),
    ("b8", "¿TÚ TAMBIÉN TE LO CREÍSTE?", C["tu"], C["end"] - 0.1),
]
IN_CLIP, SHOW, OUT_CLIP = "inset(-30px 1200px -30px -30px)", "inset(-30px -30px -30px -30px)", "inset(-30px -30px -30px 1200px)"


def stage_html():
    ban = "\n".join(f'    <div id="{i}" class="ban"><span>{t}</span></div>' for i, t, _, _ in BANNERS)
    tw = ['tl.fromTo("#t1", { clipPath: "' + IN_CLIP + '" }, { clipPath: "' + SHOW + '", duration: 0.3, ease: "power3.out" }, 0.0);',
          'tl.fromTo("#t2", { clipPath: "' + IN_CLIP + '" }, { clipPath: "' + SHOW + '", duration: 0.3, ease: "power3.out" }, 0.15);',
          f'tl.to("#title", {{ clipPath: "{OUT_CLIP}", duration: 0.3, ease: "power3.in" }}, {round(C["l1"] - 0.15, 3)});']
    for i, _, a, b in BANNERS:
        tw += [f'tl.fromTo("#{i}", {{ clipPath: "{IN_CLIP}" }}, {{ clipPath: "{SHOW}", duration: 0.3, ease: "power3.out" }}, {round(a, 3)});',
               f'tl.fromTo("#{i}", {{ clipPath: "{SHOW}" }}, {{ clipPath: "{OUT_CLIP}", duration: 0.22, ease: "power3.in", immediateRender: false }}, {round(b, 3)});']
    return (STAGE.replace("__C__", json.dumps(C)).replace("__M__", json.dumps(MOUTH, separators=(",", ":")))
            .replace("__BAN__", ban).replace("__TW__", "\n".join("    " + x for x in tw)))


STAGE = r'''<template>
  <style>
    #root { position: absolute; inset: 0; overflow: hidden; background: #E8D9B5; font-family: "Archivo Black", sans-serif; }
    #cv { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
    .src { position: absolute; left: -4000px; top: 0; width: 10px; height: 10px; }
    .ban { position: absolute; left: 0; top: 250px; width: 1080px; text-align: center; clip-path: inset(-30px 1200px -30px -30px); }
    .ban span { display: inline-block; max-width: 1000px; font-size: 42px; line-height: 1.1; padding: 16px 28px 10px; background: #FFFFFF; color: #2B1A10;
      border: 5px solid #2B1A10; box-shadow: 10px 12px 0 rgba(40,20,10,0.35); rotate: -1.5deg; }
    #b2 span, #b7 span { font-family: "Nunito", sans-serif; font-weight: 900; font-size: 34px; }
    #b4 span { background: #FFD23F; } #b8 span { background: #E23E8B; color: #FFFFFF; font-size: 54px; }
    #title { position: absolute; left: 0; top: 200px; width: 1080px; text-align: center; }
    .tt { clip-path: inset(-30px 1200px -30px -30px); margin-bottom: 14px; }
    .tt span { display: inline-block; font-size: 62px; line-height: 1.02; padding: 18px 30px 10px; color: #2B1A10; background: #FFFFFF;
      border: 6px solid #2B1A10; box-shadow: 10px 12px 0 rgba(40,20,10,0.4); }
    #t1 span { rotate: -2deg; } #t2 span { font-size: 70px; background: #FFD23F; rotate: 1.5deg; }
  </style>
  <div id="root" data-composition-id="stage" data-width="1080" data-height="1920" data-layout-allow-overflow>
    <canvas id="cv" width="1080" height="1920"></canvas>
    <img id="im-colon" class="src" src="assets/recortes/colon_head.jpg" alt="" />
    <img id="im-irving" class="src" src="assets/recortes/irving_head.jpg" alt="" />
    <img id="im-rey" class="src" src="assets/recortes/rey_fig.jpg" alt="" />
__BAN__
    <div id="title"><div id="t1" class="tt"><span>¿COLÓN DESCUBRIÓ QUE</span></div><div id="t2" class="tt"><span>LA TIERRA ERA REDONDA?</span></div></div>
  </div>
  <script>
    const C = __C__;
    const M = __M__;
    const cv = document.getElementById("cv"), g = cv.getContext("2d");
    const IMG = { colon: document.getElementById("im-colon"), irving: document.getElementById("im-irving"), rey: document.getElementById("im-rey") };
    const ok = (im) => im && im.complete && im.naturalWidth > 0;
    const clamp = (k) => Math.min(Math.max(k, 0), 1);
    const smooth = (k) => { k = clamp(k); return k * k * (3 - 2 * k); };
    const lerp = (a, b, k) => a + (b - a) * k;
    const mouth = (spk, t) => (M[spk] || [])[Math.floor(t * 30)] || 0;
    const rnd = (i) => { const x = Math.sin(i * 91.7 + 13.1) * 43758.5; return x - Math.floor(x); };
    const INK = "#2B1A10", SKIN = "#E8C39E";
    // cut-out motion: no in-betweens. pop = 0 → 0.6 → 1.15 → 1 on single frames; step = n hard poses over dur
    const pop = (t, t0) => { const d = t - t0; return d < 0 ? 0 : d < 0.067 ? 0.6 : d < 0.134 ? 1.15 : 1; };
    const step = (t, t0, dur, n) => clamp(Math.floor((t - t0) / dur * n + 1e-6) / n);

    // ---- paper primitives ----
    const poly = (pts) => () => { g.beginPath(); pts.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.closePath(); };
    const blob = (cx, cy, rx, ry, seed, n) => () => { g.beginPath(); n = n || 26;
      for (let i = 0; i <= n; i++) { const a = i / n * Math.PI * 2, j = 1 + (rnd(seed + i) - 0.5) * 0.06; const x = cx + Math.cos(a) * rx * j, y = cy + Math.sin(a) * ry * j; i ? g.lineTo(x, y) : g.moveTo(x, y); } g.closePath(); };
    function cut(build, fill, o) {  // shadow, white paper rim, flat colour, fat ink outline
      o = o || {}; g.save(); g.translate(9, 12); build(); g.fillStyle = "rgba(40,20,10,0.3)"; g.fill(); g.restore();
      build(); g.lineJoin = "round"; if (o.rim !== 0) { g.lineWidth = o.rim || 16; g.strokeStyle = "#FFFFFF"; g.stroke(); }
      g.fillStyle = fill; g.fill(); if (o.ink !== 0) { g.lineWidth = o.ink || 5; g.strokeStyle = INK; g.stroke(); }
    }
    function txt(s, x, y, size, c, align) { g.font = "900 " + size + "px 'Arial Black', Arial"; g.textAlign = align || "center"; g.fillStyle = c; g.fillText(s, x, y); }
    function label(s, x, y, size, bg, fg, rot, k) {  // text glued on a paper strip
      if (k === 0) return; g.save(); g.translate(x, y); g.rotate(rot || 0); g.scale(k || 1, k || 1);
      g.font = "900 " + size + "px 'Arial Black', Arial"; const w = g.measureText(s).width + size * 0.9, h = size * 1.35;
      cut(poly([[-w / 2, -h / 2], [w / 2, -h / 2 + 3], [w / 2 - 4, h / 2], [-w / 2 + 3, h / 2 - 2]]), bg, { ink: 4, rim: 12 });
      txt(s, 0, size * 0.36, size, fg); g.restore();
    }
    function stamp(s, x, y, size, col, rot, k) {
      if (!k) return; g.save(); g.translate(x, y); g.rotate(rot); g.scale(k, k);
      g.font = "900 " + size + "px 'Arial Black', Arial"; const w = g.measureText(s).width + size * 0.8, h = size * 1.4;
      cut(poly([[-w / 2, -h / 2], [w / 2, -h / 2], [w / 2, h / 2], [-w / 2, h / 2]]), "#FFFFFF", { ink: 0, rim: 14 });
      g.lineWidth = 10; g.strokeStyle = col; g.strokeRect(-w / 2 + 12, -h / 2 + 12, w - 24, h - 24); txt(s, 0, size * 0.36, size, col); g.restore();
    }
    function hand(x, y, ang, s) {  // giant cardboard pointing hand, finger along +x
      g.save(); g.translate(x, y); g.rotate(ang); g.scale(s, s);
      cut(poly([[-130, -50], [-60, -50], [-60, 50], [-130, 50]]), "#FFFFFF", { ink: 5, rim: 10 });
      cut(poly([[-62, -44], [10, -50], [30, -36], [160, -34], [172, -20], [160, -6], [40, -4], [46, 14], [40, 30], [44, 44], [-62, 48]]), SKIN, { ink: 5, rim: 12 });
      g.beginPath(); g.moveTo(0, 14); g.lineTo(38, 14); g.moveTo(0, 30); g.lineTo(36, 30); g.lineWidth = 4; g.strokeStyle = INK; g.stroke();
      g.restore();
    }

    // ---- real-portrait heads: scissor-cut polygon, jaw = lower slice of the same photo, 3 hinge poses ----
    const HEAD = {
      colon: { w: 440, h: 390, jaw: 268, hinge: [175, 268], poly: [[18, 118], [55, 42], [165, 12], [318, 18], [425, 86], [402, 168], [382, 248], [372, 318], [318, 366], [232, 376], [182, 336], [150, 292], [72, 262], [22, 196]] },
      irving: { w: 460, h: 490, jaw: 380, hinge: [88, 380], poly: [[58, 96], [138, 36], [272, 26], [400, 70], [446, 168], [440, 300], [414, 398], [362, 466], [252, 488], [142, 470], [92, 404], [70, 304], [48, 202]] },
    };
    function shape(H) { g.beginPath(); H.poly.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.closePath(); }
    function slice(H, im, y0, y1, tint) {
      g.save(); g.beginPath(); g.rect(-40, y0, H.w + 80, y1 - y0); g.clip();
      shape(H); g.lineJoin = "round"; g.lineWidth = 18; g.strokeStyle = "#FFFFFF"; g.stroke();
      shape(H); g.clip(); if (ok(im)) g.drawImage(im, 0, 0, H.w, H.h); else { g.fillStyle = "#B89A78"; g.fillRect(0, 0, H.w, H.h); }
      if (tint) { g.fillStyle = "rgba(90,170,60,0.45)"; g.fillRect(0, 0, H.w, H.h); }
      g.fillStyle = "#FFFFFF"; g.fillRect(0, y0 === -40 ? H.jaw - 5 : H.jaw, H.w, 5); g.restore();
    }
    function head(key, x, y, s, open, tint) {
      const H = HEAD[key], im = IMG[key], q = open < 0.08 ? 0 : open < 0.45 ? 0.5 : 1;
      g.save(); g.translate(x, y); g.scale(s, s); g.translate(-H.w / 2, -H.h / 2);
      g.save(); g.translate(11, 14); shape(H); g.fillStyle = "rgba(40,20,10,0.32)"; g.fill(); g.restore();
      if (q) { g.save(); shape(H); g.clip(); g.fillStyle = "#3A0E12"; g.fillRect(0, H.jaw - 4, H.w, 60); g.restore(); }
      slice(H, im, -40, H.jaw, tint);
      g.save(); g.translate(H.hinge[0], H.hinge[1]); g.rotate(q * 0.13); g.translate(-H.hinge[0], -H.hinge[1] - q * 10);
      slice(H, im, H.jaw, H.h + 40, tint); g.restore();
      g.restore();
    }

    // ---- cast (x,y = bottom centre) ----
    function colon(x, y, s, t, o) {
      o = o || {}; g.save(); g.translate(x, y); g.scale(s, s);
      const b = o.still ? 0 : (Math.floor(t * 2.5) % 2) * 5;
      cut(poly([[-175, 0], [-145, -330 + b], [145, -330 + b], [175, 0]]), "#B23A48", { ink: 6 });
      cut(poly([[-145, -330 + b], [-50, -330 + b], [-110, 0], [-175, 0]]), "#2E2A2A", { ink: 6, rim: 10 });
      cut(poly([[50, -330 + b], [145, -330 + b], [175, 0], [110, 0]]), "#2E2A2A", { ink: 6, rim: 10 });
      cut(poly([[-60, -340 + b], [60, -340 + b], [40, -270 + b], [-40, -270 + b]]), "#F4F1E8", { ink: 5, rim: 10 });
      for (let k = 0; k < 4; k++) cut(blob(0, -230 + k * 50 + b, 9, 9, 40 + k, 10), "#C9A24A", { ink: 3, rim: 4 });
      if (o.hand !== undefined) hand(120, -220 + b, o.hand, 0.9);
      head("colon", 8, -500 + b, 0.82, o.mute ? 0 : mouth("colon", t), o.green);
      g.restore();
    }
    function irving(x, y, s, t, o) {
      o = o || {}; g.save(); g.translate(x, y); g.scale(s, s);
      const b = (Math.floor(t * 2.2) % 2) * 5, sh = o.shrug ? -28 : 0;
      cut(poly([[-170, 0], [-150, -330 + b + sh], [150, -330 + b + sh], [170, 0]]), "#1B1B2F", { ink: 6 });
      cut(poly([[-55, -340 + b], [55, -340 + b], [30, -150 + b], [0, -120 + b], [-30, -150 + b]]), "#F4F1E8", { ink: 5, rim: 10 });
      cut(poly([[-40, -330 + b], [40, -330 + b], [0, -290 + b]]), "#1B1B2F", { ink: 4, rim: 6 });
      if (o.quill) { g.save(); g.translate(-150, -260 + b); g.rotate(-0.5); cut(poly([[0, 0], [30, -200], [70, -260], [40, -120], [8, 10]]), "#F4F1E8", { ink: 4, rim: 10 }); g.restore(); }
      if (o.shrug) { hand(-160, -300 + b, -2.6, 0.75); hand(160, -300 + b, -0.55, 0.75); }
      head("irving", 0, -540 + b, 0.74, o.mute ? 0 : mouth("irving", t));
      g.restore();
    }
    function eratos(x, y, s, t) {
      g.save(); g.translate(x, y); g.scale(s, s);
      cut(poly([[-150, 0], [-120, -330], [120, -330], [150, 0]]), "#F2EEE3", { ink: 6 });
      cut(poly([[-120, -330], [60, -330], [-80, 0], [-150, 0]]), "#C9A24A", { ink: 5, rim: 10 });
      cut(blob(0, -420, 80, 92, 300), SKIN, { ink: 6 });
      cut(blob(0, -350, 78, 62, 310), "#D8D4CC", { ink: 5, rim: 10 });
      for (let k = 0; k < 7; k++) cut(blob(-70 + k * 23, -500 + Math.abs(k - 3) * 8, 14, 9, 320 + k, 8), "#5E8C3A", { ink: 3, rim: 4 });
      [-28, 28].forEach((dx) => { g.beginPath(); g.arc(dx, -430, 8, 0, 7); g.fillStyle = INK; g.fill(); });
      g.beginPath(); g.moveTo(-22, -378); g.lineTo(22, -378); g.lineWidth = 6; g.strokeStyle = INK; g.stroke();
      g.restore();
    }
    function sage(x, y, s, shake, seed) {
      g.save(); g.translate(x, y); g.scale(s, s);
      cut(poly([[-130, 0], [-100, -300], [100, -300], [130, 0]]), "#5A3E2B", { ink: 6 });
      g.save(); g.translate(shake, 0); cut(blob(0, -380, 95, 110, seed), "#5A3E2B", { ink: 6 }); cut(blob(0, -360, 58, 70, seed + 9), "#2A1A10", { ink: 0, rim: 0 });
      [-20, 20].forEach((dx) => { g.beginPath(); g.arc(dx, -370, 7, 0, 7); g.fillStyle = "#FFE9B0"; g.fill(); }); g.restore();
      g.restore();
    }
    function earth(x, y, r, seed) {
      g.save(); g.translate(x, y);
      cut(blob(0, 0, r, r, seed || 700, 40), "#3C7DC4", { ink: 6, rim: 16 });
      g.save(); blob(0, 0, r, r, seed || 700, 40)(); g.clip();
      for (let k = 0; k < 6; k++) cut(blob((rnd(k + 710) - 0.5) * r * 1.3, (rnd(k + 720) - 0.5) * r * 1.3, r * (0.18 + rnd(k + 730) * 0.22), r * (0.14 + rnd(k + 740) * 0.2), 750 + k * 13, 16), "#6AAF5A", { ink: 4, rim: 0 });
      g.restore(); g.restore();
    }
    function ship(x, y, s, tilt) {
      g.save(); g.translate(x, y); g.rotate(tilt || 0); g.scale(s, s);
      cut(poly([[-170, -60], [170, -60], [130, 20], [-130, 20]]), "#7A4A2A", { ink: 6 });
      g.fillStyle = INK; g.fillRect(-6, -330, 12, 270); g.fillRect(-106, -260, 10, 200);
      cut(poly([[-90, -320], [90, -320], [100, -120], [-100, -120]]), "#F4F1E8", { ink: 5, rim: 10 });
      cut(poly([[-170, -250], [-110, -250], [-110, -110], [-170, -110]]), "#F4F1E8", { ink: 4, rim: 8 });
      g.fillStyle = "#B5332A"; g.fillRect(-12, -300, 24, 160); g.fillRect(-60, -238, 120, 24);
      g.restore();
    }
    function sea(t, y) {
      for (let r = 0; r < 3; r++) cut(() => { g.beginPath(); g.moveTo(-60, 2000); const yy = y + r * 90, ph = (Math.floor(t * 4) % 2) * 30;
        for (let x = -60; x <= 1140; x += 60) g.lineTo(x, yy + ((x / 60 + r) % 2 ? 22 : -22) + (x % 120 ? ph * 0 : 0)); g.lineTo(1140, 2000); g.closePath(); },
        ["#3C7DC4", "#2F6AAE", "#25588F"][r], { ink: 5, rim: 10 });
    }

    // ---- backgrounds ----
    function parchment(c1, c2) {
      const gr = g.createRadialGradient(540, 900, 200, 540, 960, 1150); gr.addColorStop(0, c1 || "#EFE3C4"); gr.addColorStop(1, c2 || "#B89466");
      g.fillStyle = gr; g.fillRect(-400, -400, 1880, 2720);
      for (let k = 0; k < 14; k++) { g.beginPath(); g.ellipse(rnd(k + 1) * 1080, rnd(k + 30) * 1920, 40 + rnd(k + 60) * 120, 30 + rnd(k + 90) * 80, rnd(k) * 3, 0, 7); g.fillStyle = "rgba(120,80,30,0.06)"; g.fill(); }
    }
    function meridians() { g.strokeStyle = "rgba(90,60,30,0.18)"; g.lineWidth = 3; for (let k = 0; k < 9; k++) { g.beginPath(); g.moveTo(k * 135, 0); g.lineTo(k * 135, 1920); g.stroke(); } for (let k = 0; k < 15; k++) { g.beginPath(); g.moveTo(0, k * 135); g.lineTo(1080, k * 135); g.stroke(); } }

    // ---- scenes ----
    function sceneHook(t) {
      parchment(); meridians();
      const rise = t < C.colon ? 0 : step(t, C.colon, 0.24, 3);
      colon(540, lerp(2400, 1500, rise), 1.25, t, { green: t >= C.muere, hand: t >= C.cuentas ? -0.4 : undefined });
      stamp("¡MENTIRA!", 540, 760, 120, "#E23E8B", -0.14, pop(t, C.mentira));
      if (t >= C.muere) { const k = step(t, C.muere, 0.6, 6); cut(() => { g.beginPath(); const x0 = lerp(-900, 1100, k); g.moveTo(x0 - 600, 2000);
        for (let i = 0; i < 9; i++) g.lineTo(x0 - 600 + i * 120, 1500 + (i % 2 ? -110 : 60)); g.lineTo(x0 + 600, 2000); g.closePath(); }, "#3C7DC4", { ink: 6 }); }
    }
    function sceneEratos(t) {
      parchment("#F6E7C1", "#C99A5B");
      const su = t < C.sombra ? 0 : step(t, C.sombra, 0.9, 3);
      cut(blob(lerp(860, 300, su), 420, 90, 90, 401), "#FFD23F", { ink: 6 });
      cut(poly([[-60, 1240], [1140, 1220], [1140, 2000], [-60, 2000]]), "#C9A26B", { ink: 6 });
      const strip = t < C.mil ? 0 : step(t, C.mil, 0.45, 3);
      if (strip) label(strip < 1 ? "1492" : "240 a. C.", 540, 600, 70, "#FFFFFF", "#B5332A", -0.05, pop(t, C.mil));
      const e = t < C.griego ? 0 : 1;
      eratos(lerp(-300, 380, e === 0 ? 0 : step(t, C.griego, 0.2, 2)), 1300, 0.95, t);
      if (t >= C.palo) { const k = pop(t, C.palo); g.save(); g.translate(720, 1240); g.scale(k, k); cut(poly([[-10, 0], [-10, -330], [10, -330], [10, 0]]), "#7A4A2A", { ink: 4, rim: 8 }); g.restore();
        const ang = lerp(-0.9, 0.9, su); g.save(); g.translate(720, 1240); g.rotate(ang * 0.3); g.fillStyle = "rgba(40,20,10,0.55)"; g.fillRect(0, -8, 260 - su * 120, 16); g.restore(); }
      if (t >= C.atino) { earth(820, 900, 120, 700); label("≈ 40,000 km ✓", 760, 1110, 52, "#2E9E5B", "#FFFFFF", 0.05, pop(t, C.atino)); }
    }
    function sceneOrb(t) {
      parchment("#F2E2BD", "#A87F4E");
      const im = IMG.rey, k = t < C.reyes ? 0 : step(t, C.reyes, 0.24, 3), x = lerp(-700, 300, k);
      const grow = t < C.redondo ? 0 : smooth((t - C.redondo) / 0.5);
      g.save(); g.translate(x, 380);
      const P = poly([[10, 6], [520, 0], [534, 900], [4, 910]]);
      cut(P, "#B89A78", { ink: 0, rim: 18 }); g.save(); P(); g.clip(); if (ok(im)) g.drawImage(im, 0, 0, 540, 915); g.restore();
      g.restore();
      const ox = x + 397, oy = 380 + 586;
      if (t >= C.mundo) hand(ox + 330, oy + 30, Math.PI, 1.0 * pop(t, C.mundo));
      if (t >= C.mundo) earth(lerp(ox, 600, grow), lerp(oy, 900, grow), lerp(60, 260, grow), 700);
      stamp("REDONDO ✓", 560, 1290, 80, "#2E9E5B", -0.08, pop(t, C.redondo + 0.15));
    }
    function sceneSmall(t) {  // Colón: "era CHIQUITA" — the Earth shrinks in two hops, Japan glued next to Spain
      parchment(); meridians();
      const sh = t < C.chiquita ? 0 : step(t, C.chiquita, 0.3, 2), r = lerp(230, 150, sh);
      earth(630, 720, r, 700);
      if (t >= C.japon) { label("ESPAÑA", 560, 720, 40, "#FFFFFF", INK, -0.04, 1); label("JAPÓN", 700, 660, 40, "#FFD23F", INK, 0.06, pop(t, C.japon));
        for (let k = 0; k < 3; k++) if (t >= C.japon + 0.15 * k) cut(blob(600 + k * 30, 690 - k * 10, 9, 13, 770 + k, 8), INK, { ink: 0, rim: 4 }); }
      colon(330, 1500, 1.05, t, { hand: t >= C.plana && t < C.japon ? -0.2 : (t >= C.japon ? -0.6 : undefined) });
      stamp("PLANA ✗", 330, 520, 64, "#B5332A", 0.1, t >= C.plana && t < C.chiquita ? pop(t, C.plana) : 0);
    }
    function sceneDist(t) {  // two Earths, then the 4,500 km strip vs the real ~20,000 km strip that runs off the page
      parchment("#F2E2BD", "#B89466"); meridians();
      const two = pop(t, C.cuarta);
      if (t < C.cuatro) { earth(330, 760, 230, 700); label("REAL", 330, 1060, 50, "#FFFFFF", INK, -0.04, 1);
        if (two) { g.save(); g.translate(790, 790); g.scale(two, two); earth(0, 0, 172, 700); g.restore(); label("COLÓN: −25 %", 790, 1060, 46, "#FFD23F", INK, 0.05, two); }
        stamp("ERROR", 540, 520, 90, "#B5332A", -0.1, t >= C.error && t < C.cuarta ? pop(t, C.error) : 0);
        return; }
      const pan = t < C.veinte ? 0 : smooth((t - C.veinte - 0.2) / 1.2) * 900;
      g.save(); g.translate(-pan, 0);
      label("ESPAÑA", 140, 640, 44, "#FFFFFF", INK, -0.05, 1);
      const a = step(t, C.cuatro, 0.3, 3);
      cut(poly([[120, 720], [120 + 300 * a, 716], [120 + 300 * a, 790], [120, 794]]), "#FFD23F", { ink: 5 });
      if (a >= 1) { label("JAPÓN SEGÚN COLÓN", 330, 880, 36, "#FFD23F", INK, 0.04, 1); txt("4,500 km", 270, 775, 40, INK); }
      if (t >= C.veinte) { const b = step(t, C.veinte, 0.9, 6);
        cut(poly([[120, 1060], [120 + 1320 * b, 1056], [120 + 1320 * b, 1130], [120, 1134]]), "#E23E8B", { ink: 5 });
        txt("~20,000 km", 120 + 660 * b, 1115, 44, "#FFFFFF"); if (b >= 1) label("JAPÓN DE VERDAD", 1360, 1220, 40, "#FFFFFF", INK, -0.04, 1); }
      g.restore();
    }
    function sceneSalamanca(t) {
      parchment("#E9D5AE", "#8E6A3E");
      cut(poly([[80, 1200], [80, 560], [300, 420], [540, 360], [780, 420], [1000, 560], [1000, 1200]]), "#C9A26B", { ink: 6 });
      for (let k = 0; k < 3; k++) cut(poly([[180 + k * 280, 1200], [180 + k * 280, 780], [260 + k * 280, 700], [340 + k * 280, 780], [340 + k * 280, 1200]]), "#8B6A45", { ink: 5, rim: 10 });
      const shake = t >= C.no5 ? ((Math.floor((t - C.no5) * 6) % 2) ? 16 : -16) : 0;
      for (let k = 0; k < 3; k++) { const e = t < C.salamanca ? 0 : step(t, C.salamanca + k * 0.12, 0.14, 2); if (e) sage(260 + k * 280, lerp(1900, 1550, e), 0.95, shake * (k % 2 ? -1 : 1), 820 + k * 7); }
      if (t >= C.hambre) { const k = step(t, C.hambre, 0.6, 3);
        if (k < 1) cut(blob(540, 560, 140 * (1 - k * 0.6), 80 * (1 - k * 0.6), 860, 18), "#D9A25B", { ink: 5 });
        for (let i = 0; i < 9 * k; i++) cut(blob(440 + rnd(i + 870) * 200, 560 + rnd(i + 880) * 140 * k, 12, 10, 890 + i, 8), "#D9A25B", { ink: 3, rim: 4 }); }
    }
    function sceneDefend(t) {
      parchment(); sea(t, 1150);
      cut(poly([[700, 1150], [760, 1000], [900, 960], [1120, 980], [1120, 1200]]), "#6AAF5A", { ink: 5 });
      if (t >= C.lugar) label("¿?", 800, 880, 90, "#FFFFFF", "#B5332A", 0.08, pop(t, C.lugar));
      colon(380, 1500, 1.1, t, { hand: t >= C.mori ? -0.05 : undefined });
    }
    function sceneBlock(t) {  // the ship sails west and America slams in its way
      parchment("#DDEBF2", "#8FB3C9"); cut(blob(860, 380, 80, 80, 940), "#FFD23F", { ink: 5 });
      const hit = t >= C.america + 0.35, k = hit ? 1 : step(t, C.l7, Math.max(C.america + 0.35 - C.l7, 0.4), 6);
      const am = t < C.america ? 0 : step(t, C.america, 0.2, 2);
      if (am) cut(poly([[-80, 600], [140, 640], [200, 820], [150, 1000], [230, 1150], [180, 1400], [-80, 1400]]), "#6AAF5A", { ink: 6 });
      if (am) label("AMÉRICA", 90, 900, 46, "#FFFFFF", INK, -0.1, am);
      ship(lerp(1000, 380, k), 1180, 0.85, hit ? -0.12 : 0);
      sea(t, 1180);
      if (t >= C.asia) { stamp("ASIA", 700, 640, 110, "#B5332A", 0.06, pop(t, C.asia)); if (t >= C.asia + 0.25) { g.save(); g.translate(700, 640); g.rotate(0.06);
        g.beginPath(); g.moveTo(-190, 60); g.lineTo(190, -60); g.lineWidth = 18; g.strokeStyle = "#B5332A"; g.stroke(); g.restore(); label("1506 †", 820, 820, 40, "#FFFFFF", INK, 0.05, pop(t, C.asia + 0.3)); } }
    }
    function sceneIrving(t, talk) {
      parchment("#EFE3C4", "#A88457");
      const e = t < C.escritor ? 0 : step(t, C.escritor, 0.24, 3);
      if (!talk && t >= C.mil8) { const k = pop(t, C.mil8); g.save(); g.translate(300, 820); g.rotate(-0.08); g.scale(k, k);
        cut(poly([[-230, -160], [0, -140], [0, 170], [-230, 150]]), "#8E1F2F", { ink: 6 }); cut(poly([[0, -140], [230, -160], [230, 150], [0, 170]]), "#8E1F2F", { ink: 6 });
        cut(poly([[-200, -130], [-10, -115], [-10, 140], [-200, 125]]), "#F4F1E8", { ink: 4, rim: 0 }); cut(poly([[10, -115], [200, -130], [200, 125], [10, 140]]), "#F4F1E8", { ink: 4, rim: 0 });
        txt("1828", -105, 20, 66, "#8E1F2F"); txt("COLÓN", 105, 0, 40, INK); txt("(novela)", 105, 50, 30, "#B5332A"); g.restore(); }
      if (!talk && t >= C.plana8 && t < C.escritor) label("¿PLANA?", 540, 700, 80, "#FFFFFF", "#B5332A", -0.05, pop(t, C.plana8));
      if (talk) colon(250, 1520, 0.8, t, { mute: true, still: true });
      irving(talk ? 700 : lerp(1500, 800, e), 1520, 1.05, t, { quill: !talk, shrug: talk && t >= C.drama });
      if (talk) stamp("NOVELA", 700, 560, 84, "#8E1F2F", 0.08, pop(t, C.novela));
    }
    function sceneBoard(t) {
      parchment();
      cut(poly([[60, 420], [1020, 420], [1020, 1240], [60, 1240]]), "#7A4A2A", { ink: 6 });
      g.fillStyle = "#2F4F3A"; g.fillRect(90, 450, 900, 760);
      const cutK = t < C.creiste ? 0 : step(t, C.creiste, 0.5, 5), fall = t < C.creiste + 0.55 ? 0 : smooth((t - C.creiste - 0.55) / 0.5);
      const wr = t < C.escuela ? 0 : clamp((t - C.escuela) / 0.9);
      const rows = ["Colón descubrió", "que la Tierra", "era redonda"];
      rows.forEach((s, i) => { g.save(); g.beginPath(); g.rect(90, 450, 900 * clamp(wr * 3 - i), 760); g.clip();
        if (fall && i === 2) { g.translate(0, fall * 700); g.rotate(fall * 0.25); }
        g.font = "700 76px 'Comic Sans MS', 'Segoe Print', cursive"; g.textAlign = "center"; g.fillStyle = "#F3F1E6"; g.fillText(s, 540, 620 + i * 190); g.restore(); });
      if (t >= C.creiste) { g.setLineDash([22, 16]); g.beginPath(); g.moveTo(110, 960); g.lineTo(110 + 860 * cutK, 960); g.lineWidth = 6; g.strokeStyle = "#FFD23F"; g.stroke(); g.setLineDash([]);
        const sx = 110 + 860 * cutK, o = (Math.floor(t * 8) % 2) ? 0.35 : 0.1;
        g.save(); g.translate(sx, 960); [o, -o].forEach((a) => { g.save(); g.rotate(a); cut(poly([[0, -8], [170, -4], [170, 4], [0, 8]]), "#C8CDD3", { ink: 4, rim: 8 }); cut(blob(-40, 0, 34, 24, 990 + (a > 0 ? 1 : 2), 12), "#E23E8B", { ink: 4, rim: 8 }); g.restore(); }); g.restore(); }
    }

    function cam(t) {  // camera re-frames on whoever talks (smooth); scenes themselves move in hard steps
      const K = [[0, 540, 960, 1], [C.cuentas, 540, 1020, 1.06], [C.l1, 540, 960, 1], [C.l3, 420, 1000, 1.08], [C.l4, 540, 960, 1],
                 [C.l6, 440, 1020, 1.1], [C.l7, 540, 960, 1], [C.l9, 600, 1000, 1.06], [C.l10, 540, 900, 1.04]];
      let i = 0; while (i + 1 < K.length && t >= K[i + 1][0]) i++;
      const a = K[i], p = i ? K[i - 1] : a, k = smooth((t - a[0]) / 0.45);
      return [lerp(p[1], a[1], k), lerp(p[2], a[2], k), lerp(p[3], a[3], k)];
    }
    function draw(t) {
      g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, 1080, 1920);
      const S = [[0, sceneHook], [C.l1, sceneEratos], [C.l2, sceneOrb], [C.l3, sceneSmall], [C.l4, sceneDist], [C.l5, sceneSalamanca],
                 [C.l6, sceneDefend], [C.l7, sceneBlock], [C.l8, (u) => sceneIrving(u, false)], [C.l9, (u) => sceneIrving(u, true)], [C.l10, sceneBoard]];
      let i = 0; while (i + 1 < S.length && t >= S[i + 1][0] - 0.1) i++;
      const [cx, cy, z] = cam(t);
      const view = (fn) => { g.save(); g.translate(540, 960); g.scale(z, z); g.translate(-cx, -cy); fn(t); g.restore(); };
      const t0 = S[i][0] - 0.1, k = i ? smooth((t - t0) / 0.3) : 1;
      if (k < 1) { view(S[i - 1][1]); g.save(); g.translate(0, 1920 * (1 - k)); g.rotate(-0.05 * (1 - k)); g.shadowColor = "rgba(40,20,10,0.4)"; g.shadowBlur = 0; g.shadowOffsetY = -14;
        g.fillStyle = "#E8D9B5"; g.fillRect(-60, 0, 1200, 1980); g.shadowColor = "transparent"; g.beginPath(); g.rect(-60, 0, 1200, 1980); g.clip(); view(S[i][1]); g.restore(); }
      else view(S[i][1]);
    }
    draw(0);
    Object.values(IMG).forEach((im) => im.addEventListener("load", () => draw(0)));
    window.addEventListener("hf-seek", (e) => draw(e.detail.time));

    const tl = gsap.timeline({ paused: true });
__TW__
    window.__timelines["stage"] = tl;
  </script>
</template>
'''


def index_html():
    sfx = [("clac0", "el_clac", C["colon"] + 0.05, 0.5, 0.45), ("stamp0", "el_stamp", C["mentira"], 0.6, 0.55), ("buzz0", "el_buzz", C["mentira"] + 0.1, 0.8, 0.25),
           ("wave0", "el_wave", C["muere"], 1.2, 0.4),
           ("w1", "whoosh", C["l1"] - 0.15, 0.57, 0.3), ("clac1", "el_clac", C["mil"], 0.5, 0.4), ("clac1b", "el_clac", C["griego"], 0.5, 0.4),
           ("clac1c", "el_clac", C["palo"], 0.5, 0.4), ("ding1", "el_ding", C["atino"], 0.7, 0.45),
           ("w2", "whoosh", C["l2"] - 0.15, 0.57, 0.3), ("clac2", "el_clac", C["reyes"], 0.5, 0.4), ("clac2b", "el_clac", C["mundo"], 0.5, 0.4),
           ("stamp2", "el_stamp", C["redondo"] + 0.15, 0.6, 0.5), ("ding2", "el_ding", C["redondo"] + 0.2, 0.7, 0.35),
           ("w3", "whoosh", C["l3"] - 0.15, 0.57, 0.3), ("buzz3", "el_buzz", C["plana"], 0.8, 0.25), ("clac3", "el_clac", C["japon"], 0.5, 0.45),
           ("w4", "whoosh", C["l4"] - 0.15, 0.57, 0.3), ("stamp4", "el_stamp", C["error"], 0.6, 0.45), ("clac4", "el_clac", C["cuarta"], 0.5, 0.4),
           ("clac4b", "el_clac", C["cuatro"], 0.5, 0.4), ("w4b", "whoosh", C["veinte"] + 0.2, 0.57, 0.35),
           ("w5", "whoosh", C["l5"] - 0.15, 0.57, 0.3), ("clac5", "el_clac", C["salamanca"], 0.5, 0.4), ("gasp5", "el_gasp", C["hambre"], 1.2, 0.3),
           ("w6", "whoosh", C["l6"] - 0.15, 0.57, 0.3), ("gulls6", "el_gulls", C["l6"], 1.5, 0.25), ("clac6", "el_clac", C["lugar"], 0.5, 0.4),
           ("w7", "whoosh", C["l7"] - 0.15, 0.57, 0.3), ("crash7", "el_crash", C["america"] + 0.3, 1.0, 0.5), ("stamp7", "el_stamp", C["asia"], 0.6, 0.5),
           ("w8", "whoosh", C["l8"] - 0.15, 0.57, 0.3), ("clac8", "el_clac", C["escritor"], 0.5, 0.4), ("clac8b", "el_clac", C["mil8"], 0.5, 0.45),
           ("w9", "whoosh", C["l9"] - 0.15, 0.57, 0.3), ("stamp9", "el_stamp", C["novela"], 0.6, 0.45),
           ("w10", "whoosh", C["l10"] - 0.15, 0.57, 0.3), ("chalk10", "el_chalk", C["escuela"], 1.2, 0.35), ("sc10", "el_scissors", C["creiste"], 0.8, 0.5),
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
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #E8D9B5; }}
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
    print(f"stage + index: {TOTAL} s, end card at {END} s")
