"""EP11: escribe compositions/stage.html (la Guerra del Cerdo, caricatura plana estilo EP03 mejorada) e index.html.

  python -I audio/build_video.py     (después de gen_audio_el.py y build.py)

Canvas 1080×1920 dibujado por cuadro desde hf-seek (sin line boil). Escenas: mapa de la isla → (zoom-morph) granja → (barrido)
costa con soldados y barcos → (zoom-morph) isla compartida + káiser → (barrido) tumba del cerdo. Personajes con caminata,
cambios de ánimo, bocas desde mouth.json; cámara por palabra. Rótulos HTML con máscara (clip-path).
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
C = {
    "inglaterra": W("l0", "inglaterra"), "guerra0": W("l0", "guerra"), "cerdo0": W("l0", "cerdo"),
    "l1": L("l1"), "mil": W("l1", "mil"), "paises": W("l1", "paises"), "suya": W("l1", "suya"),
    "l2": L("l2"), "granjero": W("l2", "granjero"), "cutlar": W("l2", "cutlar"), "papas": W("l2", "papas"), "pum": W("l2", "pum"),
    "l3": L("l3"), "diez": W("l3", "diez"), "l4": L("l4"), "compania": W("l4", "compania"), "cien": W("l4", "cien"),
    "l5": L("l5"), "arrestarlo": W("l5", "arrestarlo"), "soldados": W("l5", "soldados"),
    "l6": L("l6"), "barcos": W("l6", "barcos"), "agosto": W("l6", "agosto"), "cuatro": W("l6", "cuatrocientos"), "dosmil": W("l6", "dos"),
    "l7": L("l7"), "almirante": W("l7", "almirante"), "l8": L("l8"), "pleito": W("l8", "pleito"), "cerdo8": W("l8", "cerdo"),
    "l9": L("l9"), "doce": W("l9", "doce"), "kaiser": W("l9", "kaiser"), "estados": W("l9", "estados"),
    "l10": L("l10"), "uno": W("l10", "uno"), "cerdo10": W("l10", "cerdo"), "end": END,
}
C["l8end"] = round(LINES["l8"]["end"], 3)
BANNERS = [  # id, text, in, out
    ("b1", "ISLA SAN JUAN · 1859", C["mil"] - 0.2, C["paises"] - 0.05),
    ("b1b", "¿DE QUIÉN ERA? ¡DE LOS DOS!", C["paises"], C["l2"] - 0.1),
    ("b2", "LYMAN CUTLAR · GRANJERO", C["cutlar"], C["pum"] - 0.05),
    ("b3", "OFERTA: $10", C["diez"], C["l4"] - 0.05),
    ("b4", "CHARLES GRIFFIN · CÍA. INGLESA", C["l4"] + 0.1, C["cien"] - 0.05),
    ("b5", "¡QUIERO $100!", C["cien"], C["l5"] - 0.2),
    ("b6", "AMENAZA: ARRESTAR A CUTLAR", C["arrestarlo"], C["soldados"] - 0.05),
    ("b7", "EE. UU. MANDA SOLDADOS", C["soldados"], C["l6"] - 0.05),
    ("b8", "INGLATERRA MANDA BARCOS DE GUERRA", C["barcos"], C["cuatro"] - 0.05),
    ("b9", "ALMIRANTE ROBERT BAYNES", C["almirante"], C["l8"] + 1.2),
    ("b10", "12 AÑOS COMPARTIENDO LA ISLA", C["doce"], C["kaiser"] - 0.05),
    ("b11", "ÁRBITRO: EL KÁISER GUILLERMO I", C["kaiser"], C["l10"] - 0.15),
    ("b12", "BAJAS DE LA GUERRA: 1 CERDO", C["uno"], C["end"] - 0.1),
]
SOURCES = [
    ("s1", "Fuente: NPS, San Juan Island National Historical Park", C["agosto"], C["l7"] + 1.0),
    ("s2", "Fuente: NPS · Wikipedia, «Pig War (1859)»", C["doce"], C["l10"] - 0.15),
]
IN_CLIP, SHOW, OUT_CLIP = "inset(-30px 1200px -30px -30px)", "inset(-30px -30px -30px -30px)", "inset(-30px -30px -30px 1200px)"


def stage_html():
    banners = "\n".join(f'    <div id="{i}" class="ban"><span>{t}</span></div>' for i, t, _, _ in BANNERS)
    banners += "\n" + "\n".join(f'    <div id="{i}" class="src"><span>{t}</span></div>' for i, t, _, _ in SOURCES)
    tw = ['tl.fromTo("#h1", { clipPath: "' + IN_CLIP + '" }, { clipPath: "' + SHOW + '", duration: 0.3, ease: "power3.out" }, 0.03);',
          'tl.fromTo("#h2", { clipPath: "' + IN_CLIP + '" }, { clipPath: "' + SHOW + '", duration: 0.3, ease: "power3.out" }, 0.18);',
          f'tl.fromTo("#h2 span", {{ scale: 1 }}, {{ scale: 1.12, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out" }}, {C["cerdo0"]});',
          f'tl.fromTo("#hook", {{ clipPath: "{SHOW}" }}, {{ clipPath: "{OUT_CLIP}", duration: 0.3, ease: "power3.in", immediateRender: false }}, {round(C["l1"] - 0.05, 3)});']
    for i, _, a, b in BANNERS + SOURCES:
        tw += [f'tl.fromTo("#{i}", {{ clipPath: "{IN_CLIP}" }}, {{ clipPath: "{SHOW}", duration: 0.32, ease: "power3.out" }}, {round(a, 3)});',
               f'tl.fromTo("#{i}", {{ clipPath: "{SHOW}" }}, {{ clipPath: "{OUT_CLIP}", duration: 0.22, ease: "power3.in", immediateRender: false }}, {round(b, 3)});']
    p = C["pum"]
    tw += [f'tl.fromTo("#pum", {{ scale: 0, rotation: -20 }}, {{ scale: 1, rotation: -8, duration: 0.25, ease: "back.out(2.6)" }}, {p});',
           f'tl.to("#pum", {{ scale: 0, duration: 0.18, ease: "power3.in" }}, {round(p + 1.1, 3)});',
           f'tl.fromTo("#vsL", {{ clipPath: "{IN_CLIP}" }}, {{ clipPath: "{SHOW}", duration: 0.3, ease: "power3.out" }}, {C["cuatro"]});',
           f'tl.fromTo("#vsV", {{ scale: 0 }}, {{ scale: 1, duration: 0.25, ease: "back.out(2.5)" }}, {round(C["cuatro"] + 0.6, 3)});',
           f'tl.fromTo("#vsR", {{ clipPath: "inset(-30px -30px -30px 1200px)" }}, {{ clipPath: "{SHOW}", duration: 0.3, ease: "power3.out" }}, {C["dosmil"]});',
           f'tl.fromTo("#vs", {{ clipPath: "{SHOW}" }}, {{ clipPath: "{OUT_CLIP}", duration: 0.25, ease: "power3.in", immediateRender: false }}, {round(C["l7"] - 0.05, 3)});']
    return (STAGE.replace("__C__", json.dumps(C)).replace("__M__", json.dumps(MOUTH, separators=(",", ":")))
            .replace("__BANNERS__", banners).replace("__TW__", "\n".join("    " + x for x in tw)))


STAGE = r'''<template>
  <style>
    #root { position: absolute; inset: 0; overflow: hidden; background: #8ED9F0; font-family: "Archivo Black", sans-serif; }
    #cv { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
    .ban { position: absolute; left: 0; top: 250px; width: 1080px; text-align: center; clip-path: inset(-30px 1200px -30px -30px); }
    .ban span { display: inline-block; max-width: 1000px; font-size: 50px; line-height: 1.1; padding: 16px 28px 10px; background: #FFFFFF;
      color: #1B1B2F; border: 8px solid #1B1B2F; border-radius: 18px; box-shadow: 8px 8px 0 #1B1B2F; }
    #b1b span, #b3 span, #b7 span, #b10 span { background: #FFD23F; } #b5 span, #b6 span, #b12 span { background: #E63946; color: #FFFFFF; }
    #b8 span, #b11 span { background: #2B4C9B; color: #FFFFFF; }
    .src { position: absolute; left: 0; top: 1455px; width: 1080px; text-align: center; clip-path: inset(-30px 1200px -30px -30px); }
    .src span { display: inline-block; font-family: "Nunito", sans-serif; font-weight: 800; font-size: 30px; padding: 6px 16px;
      background: rgba(27,27,47,0.85); color: #FFFFFF; border-radius: 10px; }
    #hook { position: absolute; left: 0; top: 230px; width: 1080px; }
    .tags { width: 1080px; text-align: center; margin-bottom: 24px; clip-path: inset(-30px 1200px -30px -30px); }
    .tags span { display: inline-block; white-space: nowrap; font-size: 68px; line-height: 1; padding: 16px 30px 10px; color: #1B1B2F;
      border: 8px solid #1B1B2F; border-radius: 18px; box-shadow: 8px 8px 0 #1B1B2F; }
    #h1 span { background: #FFFFFF; } #h2 span { background: #FFD23F; font-size: 96px; }
    #pum { position: absolute; left: 600px; top: 520px; }
    #pum span { display: inline-block; font-size: 130px; line-height: 1; padding: 14px 30px 4px; color: #1B1B2F; background: #FFD23F;
      border: 10px solid #1B1B2F; border-radius: 24px; box-shadow: 10px 10px 0 #1B1B2F; }
    #vs { position: absolute; left: 0; top: 250px; width: 1080px; height: 260px; }
    #vsL, #vsR { position: absolute; top: 0; width: 470px; text-align: center; clip-path: inset(-30px 1200px -30px -30px); }
    #vsL { left: 20px; } #vsR { left: 590px; }
    #vsL span, #vsR span { display: block; font-size: 96px; line-height: 1; padding: 18px 10px 8px; border: 8px solid #1B1B2F; border-radius: 20px;
      box-shadow: 8px 8px 0 #1B1B2F; color: #FFFFFF; }
    #vsL span { background: #2B4C9B; } #vsR span { background: #E63946; }
    #vsL small, #vsR small { display: block; font-size: 34px; margin-top: 6px; }
    #vsV { position: absolute; left: 470px; top: 40px; width: 140px; text-align: center; }
    #vsV span { display: inline-block; font-size: 64px; color: #1B1B2F; background: #FFD23F; border: 8px solid #1B1B2F; border-radius: 50%; width: 120px; height: 120px; line-height: 112px; }
  </style>
  <div id="root" data-composition-id="stage" data-width="1080" data-height="1920">
    <canvas id="cv" width="1080" height="1920" data-layout-allow-overflow></canvas>
__BANNERS__
    <div id="hook">
      <div id="h1" class="tags"><span>EE. UU. VS. INGLATERRA…</span></div>
      <div id="h2" class="tags"><span>¡POR UN CERDO!</span></div>
    </div>
    <div id="pum"><span>¡PUM!</span></div>
    <div id="vs">
      <div id="vsL"><span>461<small>GRINGOS · 14 CAÑONES</small></span></div>
      <div id="vsV"><span>VS</span></div>
      <div id="vsR"><span>2,140<small>INGLESES · 5 BARCOS</small></span></div>
    </div>
  </div>
  <script>
    const C = __C__;
    const M = __M__;
    const cv = document.getElementById("cv"), g = cv.getContext("2d");
    const clamp = (k) => Math.min(Math.max(k, 0), 1);
    const smooth = (k) => { k = clamp(k); return k * k * (3 - 2 * k); };
    const back = (k) => { k = clamp(k); const s = 1.8; return 1 + (s + 1) * Math.pow(k - 1, 3) + s * Math.pow(k - 1, 2); };
    const lerp = (a, b, k) => a + (b - a) * k;
    function track(keys, t) {
      let i = 0;
      while (i + 1 < keys.length && t >= keys[i + 1][0]) i++;
      if (i === 0) return keys[0].slice(2);
      const cur = keys[i], k = smooth((t - cur[0]) / cur[1]);
      const from = i >= 2 ? track(keys.slice(0, i), cur[0]) : keys[0].slice(2);
      return cur.slice(2).map((v, j) => lerp(from[j], v, k));
    }
    const moving = (keys, t) => { for (let i = 1; i < keys.length; i++) if (t >= keys[i][0] && t < keys[i][0] + keys[i][1] && keys[i][2] !== keys[i - 1][2]) return true; return false; };
    const mouth = (spk, t) => (M[spk] || [])[Math.floor(t * 30)] || 0;
    const blink = (t, seed) => ((t + seed) % 3.1) < 0.11;

    const INK = "#1B1B2F", SKIN = "#F5C9A0", CHEEK = "#F28B82", SKY = "#8ED9F0", GRASS = "#7CC46A", GRASSD = "#5DA34E", SEA = "#3FA7D6";
    const P = () => g.beginPath();
    const fill = (c) => { g.fillStyle = c; g.fill(); };
    const ink = (w) => { g.lineWidth = w || 8; g.strokeStyle = INK; g.lineJoin = "round"; g.lineCap = "round"; g.stroke(); };
    function ell(x, y, rx, ry, c, w, rot) { P(); g.ellipse(x, y, Math.abs(rx), Math.abs(ry), rot || 0, 0, Math.PI * 2); if (c) fill(c); if (w !== 0) ink(w); }
    function rr(x, y, w, h, r, c, lw) { P(); g.roundRect(x, y, w, h, r); if (c) fill(c); if (lw !== 0) ink(lw); }
    function limb(x1, y1, x2, y2, w, c) { g.lineCap = "round"; P(); g.moveTo(x1, y1); g.lineTo(x2, y2); g.strokeStyle = INK; g.lineWidth = w + 14; g.stroke(); g.strokeStyle = c; g.lineWidth = w; g.stroke(); }
    function line(pts, w, c) { P(); g.moveTo(pts[0], pts[1]); for (let i = 2; i < pts.length; i += 2) g.lineTo(pts[i], pts[i + 1]); g.lineWidth = w; g.strokeStyle = c || INK; g.lineCap = "round"; g.lineJoin = "round"; g.stroke(); }
    function shadow(x, y, rx) { g.fillStyle = "rgba(27,27,47,0.18)"; P(); g.ellipse(x, y + 4, rx, rx * 0.18, 0, 0, Math.PI * 2); g.fill(); }
    function txt(s, x, y, size, c, align) { g.font = "900 " + size + "px 'Arial Black', Arial, sans-serif"; g.textAlign = align || "center"; g.fillStyle = c || INK; g.fillText(s, x, y); }
    function mouthShape(x, y, w, v, smile) {
      if (v < 0.06) { P(); g.moveTo(x - w * 0.55, y); g.quadraticCurveTo(x, y + (smile === undefined ? 10 : smile), x + w * 0.55, y); ink(7); return; }
      ell(x, y + 4, w * (0.5 + 0.35 * v), 6 + v * 24, "#7A1F2B", 7);
      ell(x, y + 12 + v * 10, w * 0.28, 4 + v * 6, "#F28B82", 0);
    }

    // ---------- generic cartoon person (feet at x,y; faces right; f = -1 faces left) ----------
    function person(o, t) {
      const s = o.s || 1, f = o.f || 1, ph = o.walk ? t * 10 : 0, sw = o.walk ? Math.sin(ph) : 0, bob = o.walk ? Math.abs(Math.sin(ph)) * 12 : Math.sin(t * 1.9 + (o.seed || 0)) * 3;
      shadow(o.x, o.y, 90 * s);
      g.save(); g.translate(o.x, o.y); g.scale(s * f, s);
      limb(-24, -150, -26 + sw * 34, -14, 34, o.pants); limb(24, -150, 26 - sw * 34, -14, 34, o.pants);
      ell(-20 + sw * 34, -10, 34, 15, o.shoes || INK, 6); ell(32 - sw * 34, -10, 34, 15, o.shoes || INK, 6);
      const B = -bob;
      const arm = (side, a, front) => {
        const sx = side * 50, sy = -305 + B, L = 140;
        const hx = sx + Math.sin(a) * L * (side > 0 ? 1 : -1) * -1 * -1, hy = sy + Math.cos(a) * L;
        const X = side > 0 ? sx + Math.sin(a) * L : sx - Math.sin(a) * L;
        limb(sx, sy, X, hy, 28, o.sleeve || o.shirt); ell(X, hy, 18, 18, SKIN, 6);
        return [X, hy];
      };
      const back = arm(-1, o.armL || 0.15);
      rr(-62, -335 + B, 124, 200, 34, o.shirt, 8);
      if (o.torso) o.torso(B);
      const hand = arm(1, o.armR || 0.15);
      if (o.prop) o.prop(hand[0], hand[1], o.armR || 0.15);
      g.save(); g.translate(0, -425 + B);
      if (o.hairBack) o.hairBack();
      ell(-80, 6, 16, 22, SKIN, 7);
      ell(0, 0, 88, 92, SKIN, 8);
      ell(-46, 34, 18, 12, CHEEK, 0); ell(50, 34, 18, 12, CHEEK, 0);
      const mood = o.mood || 0, look = o.look === undefined ? 0.6 : o.look, closed = blink(t, o.seed || 0) || o.closed;
      [[-26, -12], [34, -12]].forEach(([ex, ey], k) => {
        if (closed) { P(); g.moveTo(ex - 15, ey); g.quadraticCurveTo(ex, ey + 10, ex + 15, ey); ink(7); }
        else if (o.x_eyes) { line([ex - 12, ey - 12, ex + 12, ey + 12], 8); line([ex + 12, ey - 12, ex - 12, ey + 12], 8); }
        else { ell(ex, ey, 16, 19, "#FFFFFF", 6); ell(ex + look * 6, ey + 3, 8, 9, INK, 0); }
        const d = mood * 11 * (k === 0 ? 1 : -1);  // angry (mood>0): inner ends low; worried (mood<0): inner ends high
        line([ex - 18, ey - 34 - d, ex + 18, ey - 34 + d], 9);
      });
      ell(10, 14, 14, 11, "#E8A57E", 6);
      if (o.mustache) o.mustache();
      mouthShape(6, 50, 40, o.m || 0, o.smile);
      if (o.hat) o.hat();
      g.restore();
      g.restore();
    }

    // ---------- props and characters ----------
    function rifle(hx, hy, a) { const dx = Math.sin(a), dy = Math.cos(a); line([hx - dx * 70, hy - dy * 70, hx + dx * 170, hy + dy * 170], 16, "#8B5A3C"); line([hx + dx * 60, hy + dy * 60, hx + dx * 190, hy + dy * 190], 9, "#4A4A5A"); }
    function bill(hx, hy) { g.save(); g.translate(hx + 20, hy - 30); g.rotate(-0.15); rr(-10, -30, 130, 64, 8, "#8FD18A", 6); txt("$10", 55, 15, 38, "#1E5A2A"); g.restore(); }
    const CUTLAR = (o) => Object.assign({ shirt: "#D64545", sleeve: "#D64545", pants: "#3D6FB6", shoes: "#6B4423",
      torso: (B) => { line([-40, -330 + B, -40, -160 + B], 14, "#3D6FB6"); line([40, -330 + B, 40, -160 + B], 14, "#3D6FB6"); rr(-50, -250 + B, 100, 110, 14, "#3D6FB6", 7); line([-62, -290 + B, 62, -290 + B], 4, "#A83232"); line([-62, -200 + B, 62, -200 + B], 4, "#A83232"); },
      hat: () => { ell(0, -70, 150, 30, "#E8C15A", 8); rr(-70, -150, 140, 86, 30, "#E8C15A", 8); line([-70, -82, 70, -82], 12, "#B5452A"); },
      mustache: () => { for (let k = 0; k < 9; k++) ell(-50 + k * 14, 66 + (k % 2) * 8, 3, 3, "#6B4423", 0); } }, o);
    const GRIFFIN = (o) => Object.assign({ shirt: "#FFFFFF", sleeve: "#FFFFFF", pants: "#5B5B6E", shoes: INK,
      torso: (B) => { rr(-56, -330 + B, 112, 150, 26, "#3F7A4F", 7); line([0, -330 + B, 0, -190 + B], 5); ell(0, -320 + B, 18, 10, "#E63946", 5); },
      hairBack: () => { ell(-84, 30, 22, 46, "#E0662A", 7); ell(84, 30, 22, 46, "#E0662A", 7); },
      hat: () => { ell(0, -74, 120, 22, "#6B4423", 8); P(); g.ellipse(0, -84, 74, 70, 0, Math.PI, Math.PI * 2); fill("#6B4423"); ink(8); line([-72, -90, 72, -90], 10, INK); } }, o);
    const BAYNES = (o) => Object.assign({ shirt: "#1E2E5C", sleeve: "#1E2E5C", pants: "#FFFFFF", shoes: INK,
      torso: (B) => { for (let k = 0; k < 4; k++) ell(-16, -300 + B + k * 40, 7, 7, "#FFD23F", 4); for (let k = 0; k < 4; k++) ell(16, -300 + B + k * 40, 7, 7, "#FFD23F", 4);
        ell(-62, -322 + B, 34, 14, "#FFD23F", 6); ell(62, -322 + B, 34, 14, "#FFD23F", 6); },
      hairBack: () => { ell(-78, 40, 26, 50, "#F2F2F2", 7); ell(78, 40, 26, 50, "#F2F2F2", 7); },
      hat: () => { P(); g.moveTo(-150, -50); g.quadraticCurveTo(0, -190, 150, -50); g.quadraticCurveTo(0, -90, -150, -50); fill(INK); ink(6); ell(0, -96, 16, 16, "#FFD23F", 5); } }, o);
    const SOLDIER = (o) => Object.assign({ shirt: "#2B4C9B", sleeve: "#2B4C9B", pants: "#5B7BC4", shoes: INK, s: 0.62,
      torso: (B) => { line([-62, -280 + B, 62, -280 + B], 8, "#F2F2F2"); line([-62, -170 + B, 62, -170 + B], 10, "#1B1B2F"); },
      hat: () => { rr(-80, -150, 160, 90, 14, "#2B4C9B", 8); rr(-90, -70, 180, 20, 6, INK, 0); ell(0, -120, 14, 12, "#FFD23F", 4); },
      prop: (hx, hy, a) => rifle(hx, hy, a) }, o);

    function pig(x, y, s, t, mode, face) {  // mode: "eat" | "look" | "dead" | "ghost"
      face = face || 1;
      g.save();
      if (mode === "dead") { shadow(x, y, 100 * s); g.translate(x, y - 150 * s); g.scale(s * face, -s); }
      else { if (mode !== "ghost") shadow(x, y, 100 * s); g.translate(x, y); g.scale(s * face, s); }
      const pink = mode === "ghost" ? "rgba(255,255,255,0.85)" : "#F7A8B8", pinkD = mode === "ghost" ? "rgba(220,220,235,0.9)" : "#EE8AA2";
      const chew = mode === "eat" ? Math.abs(Math.sin(t * 9)) : 0, wob = mode === "eat" ? Math.sin(t * 9) * 3 : 0;
      [[-60, 1], [-25, -1], [35, 1], [65, -1]].forEach(([lx, k]) => limb(lx, -60, lx + (mode === "ghost" ? k * 8 : 0), -8, 22, pink));
      P(); g.moveTo(-98, -98); g.bezierCurveTo(-140, -130, -140, -70, -115, -80); g.bezierCurveTo(-100, -90, -120, -110, -128, -96); ink(7);
      ell(0, -90, 108, 74, pink, 8);
      ell(-20, -60, 50, 18, pinkD, 0);
      g.save(); g.translate(90, -112 + wob);
      P(); g.moveTo(-30, -40); g.lineTo(-18, -84); g.lineTo(4, -48); g.closePath(); fill(pinkD); ink(7);
      P(); g.moveTo(16, -44); g.lineTo(40, -82); g.lineTo(46, -38); g.closePath(); fill(pinkD); ink(7);
      ell(0, 0, 58, 54, pink, 8);
      ell(46, 10, 26, 22, pinkD, 7); ell(40, 10, 5, 7, INK, 0); ell(54, 10, 5, 7, INK, 0);
      if (mode === "dead") { line([4, -24, 22, -6], 7); line([22, -24, 4, -6], 7); line([-28, -24, -10, -6], 7); line([-10, -24, -28, -6], 7); }
      else { const sh = mode === "ghost" ? false : blink(t, 1.3); const wink = mode === "ghost" && t >= C.cerdo10 + 0.3;
        if (sh) { line([2, -14, 22, -14], 6); line([-30, -14, -10, -14], 6); }
        else { ell(14, -16, 11, 13, "#FFFFFF", 5); ell(17, -14, 5, 6, INK, 0); if (wink) line([-32, -16, -8, -16], 7); else { ell(-18, -16, 11, 13, "#FFFFFF", 5); ell(-15, -14, 5, 6, INK, 0); } } }
      if (mode === "eat") { ell(24, 40, 14, 4 + chew * 9, "#7A1F2B", 5); if (chew < 0.5) ell(60, 44, 16, 12, "#C9A26B", 5); }
      else { P(); g.moveTo(10, 36); g.quadraticCurveTo(26, 46, 40, 34); ink(6); }
      g.restore();
      if (mode === "ghost") { g.globalAlpha = 1; ell(90, -205, 60, 14, null, 0); P(); g.ellipse(90, -205, 60, 14, 0, 0, Math.PI * 2); g.lineWidth = 10; g.strokeStyle = "#FFD23F"; g.stroke();
        const fl = Math.sin(t * 8) * 0.3; ell(-30, -150, 50, 22, "rgba(255,255,255,0.9)", 6, -0.6 + fl); }
      g.restore();
    }

    function flag(x, y, s, kind, t, lower) {  // kind: "us" | "uk"; lower 0..1 slides the flag down the pole
      g.save(); g.translate(x, y); g.scale(s, s);
      line([0, 0, 0, -320], 10, "#6B4423"); ell(0, -324, 10, 10, "#FFD23F", 5);
      const fy = -310 + lower * 250, wv = (k) => Math.sin(t * 4 + k) * 8;
      g.save(); P(); g.moveTo(4, fy); g.quadraticCurveTo(70, fy - 12 + wv(0), 150, fy + wv(1)); g.lineTo(150, fy + 100 + wv(1)); g.quadraticCurveTo(70, fy + 88 + wv(0), 4, fy + 100); g.closePath();
      g.save(); g.clip();
      if (kind === "us") { for (let k = 0; k < 7; k++) { g.fillStyle = k % 2 ? "#FFFFFF" : "#E63946"; g.fillRect(0, fy - 20 + k * 18, 160, 18); } g.fillStyle = "#2B4C9B"; g.fillRect(0, fy - 20, 66, 66);
        for (let k = 0; k < 6; k++) ell(14 + (k % 3) * 20, fy + 4 + Math.floor(k / 3) * 22, 4, 4, "#FFFFFF", 0); }
      else { g.fillStyle = "#2B4C9B"; g.fillRect(0, fy - 20, 160, 140); line([0, fy - 10, 160, fy + 110], 22, "#FFFFFF"); line([160, fy - 10, 0, fy + 110], 22, "#FFFFFF");
        line([0, fy - 10, 160, fy + 110], 8, "#E63946"); line([160, fy - 10, 0, fy + 110], 8, "#E63946"); g.fillStyle = "#FFFFFF"; g.fillRect(56, fy - 20, 40, 140); g.fillRect(0, fy + 30, 160, 40);
        g.fillStyle = "#E63946"; g.fillRect(64, fy - 20, 24, 140); g.fillRect(0, fy + 38, 160, 24); }
      g.restore(); ink(7); g.restore(); g.restore();
    }
    function island(cx, cy, s) {
      g.save(); g.translate(cx, cy); g.scale(s, s);
      const pts = [[-330, -40], [-250, -260], [-60, -300], [80, -380], [260, -250], [330, -40], [250, 180], [60, 300], [-140, 240], [-300, 150]];
      const path = (k) => { P(); g.moveTo((pts[0][0] + pts[9][0]) / 2 * k, (pts[0][1] + pts[9][1]) / 2 * k);
        for (let i = 0; i < pts.length; i++) { const a = pts[i], b = pts[(i + 1) % pts.length]; g.quadraticCurveTo(a[0] * k, a[1] * k, (a[0] + b[0]) / 2 * k, (a[1] + b[1]) / 2 * k); } g.closePath(); };
      path(1.08); fill("#F2D98A"); ink(8);
      path(0.96); fill(GRASS); ink(6);
      [[-180, -120], [-120, 60], [150, -150], [190, 60], [-20, -220], [40, 160]].forEach(([x, y]) => { ell(x, y, 34, 30, GRASSD, 6); line([x, y + 28, x, y + 46], 8, "#6B4423"); });
      g.restore();
    }
    function tent(x, y, s, c) { g.save(); g.translate(x, y); g.scale(s, s); P(); g.moveTo(-60, 0); g.lineTo(0, -80); g.lineTo(60, 0); g.closePath(); fill(c); ink(6); line([0, -80, 0, 0], 5); g.restore(); }
    function sea(x0, x1, y, t) { g.fillStyle = SEA; g.fillRect(x0, y, x1 - x0, 4000);
      for (let r = 0; r < 8; r++) for (let x = x0 - 200 + ((t * 30 + r * 70) % 200); x < x1; x += 200) { P(); g.moveTo(x, y + 60 + r * 90); g.quadraticCurveTo(x + 30, y + 40 + r * 90, x + 60, y + 60 + r * 90); g.lineWidth = 6; g.strokeStyle = "#A8E1F5"; g.stroke(); } }
    function ship(x, y, s, t, i) {
      const bob = Math.sin(t * 2 + i) * 8, rk = Math.sin(t * 1.6 + i) * 0.03;
      g.save(); g.translate(x, y + bob); g.rotate(rk); g.scale(s, s);
      P(); g.moveTo(-260, -60); g.lineTo(260, -60); g.lineTo(200, 40); g.lineTo(-210, 40); g.closePath(); fill("#7A4A2A"); ink(8);
      g.fillStyle = INK; g.fillRect(-230, -38, 450, 24); for (let k = 0; k < 8; k++) { g.fillStyle = "#F2F2F2"; g.fillRect(-210 + k * 54, -34, 26, 16); }
      [-140, 0, 140].forEach((mx, k) => { line([mx, -60, mx, -380 + k * 20], 10, "#6B4423");
        P(); g.moveTo(mx - 80, -340 + k * 20); g.quadraticCurveTo(mx + 10, -300 + k * 20, mx - 80, -130); g.lineTo(mx + 80, -130); g.quadraticCurveTo(mx + 110, -240, mx + 80, -340 + k * 20); g.closePath(); fill("#FFFFFF"); ink(6); });
      g.save(); g.translate(0, -392); g.scale(0.5, 0.5); g.fillStyle = "#2B4C9B"; g.fillRect(0, 0, 150, 90); line([0, 0, 150, 90], 18, "#FFFFFF"); line([150, 0, 0, 90], 18, "#FFFFFF"); g.fillStyle = "#E63946"; g.fillRect(60, 0, 30, 90); g.fillRect(0, 32, 150, 26); g.restore();
      g.restore();
    }
    function cannon(x, y, s, a) { g.save(); g.translate(x, y); g.scale(s, s); g.save(); g.translate(0, -60); g.rotate(-a); rr(-20, -26, 170, 52, 22, "#3A3A4A", 7); g.restore(); ell(-10, -40, 44, 44, "#8B5A3C", 7); ell(-10, -40, 10, 10, INK, 0); g.restore(); }
    function cloud(x, y, s) { g.save(); g.translate(x, y); g.scale(s, s); [[-60, 0, 50], [0, -20, 64], [60, 0, 50]].forEach(([a, b, r]) => ell(a, b, r, r * 0.8, "#FFFFFF", 0)); g.fillStyle = "#FFFFFF"; g.fillRect(-100, 0, 200, 34); g.restore(); }

    // ---------- scenes ----------
    function sceneMap(t, mode) {  // mode "hook" (two flags, pig) or "years" (camps, calendar, káiser stamp)
      g.fillStyle = SEA; g.fillRect(-2000, -2000, 5080, 5920);
      for (let r = 0; r < 14; r++) for (let k = 0; k < 7; k++) { const x = k * 170 + ((r * 60 + t * 25) % 170) - 90, y = 520 + r * 95; P(); g.moveTo(x, y); g.quadraticCurveTo(x + 25, y - 16, x + 50, y); g.lineWidth = 6; g.strokeStyle = "#7FC8E8"; g.stroke(); }
      island(540, 1000, 1.15);
      if (mode === "hook") {
        const up = smooth((t - C.paises) / 0.4);
        flag(250, 1150, 0.9, "us", t, 0); flag(800, 870, 0.9, "uk", t, 0);
        const p = back((t - C.cerdo0) / 0.4), sc = 0.38 + 0.18 * p;
        pig(540, 1060, sc, t, t < C.cerdo0 ? "eat" : "look");
        if (t >= C.cerdo0) { g.save(); g.translate(600, 1060 - 230 * sc); g.scale(p, p); txt("!", 0, 0, 120, "#E63946"); g.restore(); }
        if (up > 0) { g.globalAlpha = up; rr(110, 1180, 260, 80, 20, "#FFFFFF", 7); txt("¡MÍA!", 240, 1240, 50, "#2B4C9B"); rr(700, 690, 260, 80, 20, "#FFFFFF", 7); txt("¡MÍA!", 830, 750, 50, "#E63946"); g.globalAlpha = 1; }
      } else {
        tent(380, 1240, 0.9, "#9DB4E8"); tent(470, 1250, 0.8, "#9DB4E8"); tent(640, 790, 0.9, "#F2A0A0"); tent(730, 800, 0.8, "#F2A0A0");
        const drop = smooth((t - C.estados - 0.2) / 0.6);
        flag(250, 1150, 0.9, "us", t, 0); flag(800, 870, 0.9, "uk", t, drop);
        // calendar flipping 1860 → 1872
        const yr = Math.min(1872, 1860 + Math.max(0, Math.floor((t - C.doce) / 0.11)));
        rr(760, 470, 260, 230, 20, "#FFFFFF", 8); g.fillStyle = "#E63946"; g.fillRect(764, 474, 252, 60); txt("AÑO", 890, 520, 38, "#FFFFFF"); txt(String(t >= C.doce ? yr : 1860), 890, 650, 84);
        // káiser Guillermo I pops up and stamps
        if (t >= C.kaiser - 0.1) {
          const k = back((t - C.kaiser + 0.1) / 0.5), kx = 830, ky = 1460 + (1 - k) * 600;
          g.save(); g.translate(kx, ky);
          rr(-170, -150, 340, 300, 60, "#2B3A5C", 8); ell(-120, -130, 50, 20, "#FFD23F", 6); ell(120, -130, 50, 20, "#FFD23F", 6);
          ell(0, -300, 120, 126, SKIN, 8); ell(-60, -255, 24, 15, CHEEK, 0); ell(60, -255, 24, 15, CHEEK, 0);
          ell(-108, -250, 50, 74, "#F2F2F2", 7); ell(108, -250, 50, 74, "#F2F2F2", 7);
          P(); g.moveTo(-90, -246); g.quadraticCurveTo(0, -300, 90, -246); g.quadraticCurveTo(0, -260, -90, -246); fill("#F2F2F2"); ink(7);
          ell(-40, -320, 16, 18, "#FFFFFF", 6); ell(-38, -316, 8, 9, INK, 0); ell(40, -320, 16, 18, "#FFFFFF", 6); ell(42, -316, 8, 9, INK, 0);
          line([-62, -352, -18, -346], 9); line([18, -346, 62, -352], 9);
          P(); g.ellipse(0, -400, 120, 70, 0, Math.PI, Math.PI * 2); fill("#2B2B3A"); ink(8); line([-120, -400, 120, -400], 12, "#FFD23F");
          P(); g.moveTo(-14, -462); g.lineTo(0, -540); g.lineTo(14, -462); g.closePath(); fill("#FFD23F"); ink(6); ell(0, -430, 22, 22, "#FFD23F", 6);
          const press = t >= C.estados ? smooth((t - C.estados) / 0.15) : 0, hy = lerp(-120, 40, press);
          g.restore();
          g.save(); g.translate(620, 1010 + hy * 0); g.restore();
        }
        if (t >= C.estados) {
          const k = back((t - C.estados) / 0.3);
          g.save(); g.translate(540, 1000); g.rotate(-0.15); g.scale(1.6 - 0.6 * k, 1.6 - 0.6 * k); g.globalAlpha = clamp(k);
          P(); g.roundRect(-230, -80, 460, 160, 24); g.lineWidth = 16; g.strokeStyle = "#E63946"; g.stroke(); txt("EE. UU.", 0, 40, 110, "#E63946");
          g.restore(); g.globalAlpha = 1;
        }
      }
    }

    const CUT = [[0, 1, -260, 0.15], [C.granjero, 1.3, 270, 0.15], [C.papas, 0.35, 270, 1.45], [C.l3 - 0.1, 0.35, 270, 1.15], [C.l4 + 0.2, 0.4, 230, 0.3]];
    const GRI = [[0, 1, 1400, 0.15, 0.15], [C.l4 - 0.4, 0.9, 820, 0.15, 0.4], [C.cien, 0.25, 820, 2.6, 2.6]];
    const FCAM = [[0, 1, 560, 980, 1.0], [C.granjero, 0.8, 470, 960, 1.08], [C.papas, 0.5, 600, 990, 1.18], [C.pum, 0.25, 540, 960, 1.0],
      [C.l3 - 0.1, 0.4, 380, 890, 1.22], [C.l4 - 0.1, 0.5, 700, 890, 1.18], [C.cien, 0.3, 560, 930, 1.04]];
    function sceneFarm(t) {
      const [cx, cy, z] = track(FCAM, t);
      g.save(); g.translate(540, 960); g.scale(z, z); g.translate(-cx, -cy);
      g.fillStyle = SKY; g.fillRect(-1000, -1000, 3080, 3920);
      cloud(150 + t * 6, 560, 1); cloud(820 + t * 4, 470, 0.8);
      g.fillStyle = GRASS; g.fillRect(-1000, 1100, 3080, 2000); line([-1000, 1100, 2080, 1100], 8);
      // cabin
      rr(-260, 760, 300, 340, 6, "#B5774A", 8); P(); g.moveTo(-290, 770); g.lineTo(-110, 620); g.lineTo(70, 770); g.closePath(); fill("#8B4A2B"); ink(8);
      for (let k = 0; k < 6; k++) line([-260, 800 + k * 50, 40, 800 + k * 50], 5, "#8B5A3C"); rr(-160, 960, 90, 140, 8, "#6B4423", 7);
      // fence
      for (let k = 0; k < 12; k++) rr(120 + k * 90, 980, 22, 130, 6, "#E8D2A6", 6); line([110, 1010, 1200, 1010], 14, "#E8D2A6"); line([110, 1060, 1200, 1060], 14, "#E8D2A6");
      // potato patch
      for (let r = 0; r < 3; r++) for (let k = 0; k < 6; k++) { const x = 340 + k * 120 + r * 30, y = 1170 + r * 70; ell(x, y, 46, 20, "#8B5A3C", 6); const eaten = r === 0 && k > 1 && k < 4 && t > C.l2 + 0.3; if (!eaten) { ell(x - 12, y - 24, 16, 22, GRASSD, 5, -0.4); ell(x + 12, y - 24, 16, 22, GRASSD, 5, 0.4); } }
      const dead = t >= C.pum + 0.12;
      pig(640, 1190, 0.95, t, dead ? "dead" : "eat");
      if (t >= C.pum && t < C.pum + 0.25) { const k = (t - C.pum) / 0.25; g.globalAlpha = 1 - k; ell(470, 830, 60 + 120 * k, 60 + 120 * k, "#FFF4B0", 0); g.globalAlpha = 1; }
      const [ux, ua] = track(CUT, t), cm = mouth("cutlar", t);
      const cutAngry = t >= C.l3 - 0.1 && t < C.l4 + 0.2 ? 1 : 0;
      person(CUTLAR({ x: ux, y: 1250, s: 1, armR: ua, armL: 0.2, walk: moving(CUT, t), m: cm, mood: cutAngry, seed: 0.4, look: 0.7,
        prop: (hx, hy, a) => (t < C.l3 - 0.1 ? rifle(hx, hy, a) : bill(hx, hy)) }), t);
      if (t >= C.l4 - 0.4) { const [gx, ga, gb] = track(GRI, t);
        person(GRIFFIN({ x: gx, y: 1250, s: 1, f: -1, armR: ga, armL: gb, walk: moving(GRI, t), m: mouth("griffin", t), mood: 1, seed: 1.1, look: 0.7 }), t); }
      g.restore();
    }

    const SCAM = [[0, 1, 700, 960, 1.0], [C.soldados, 0.8, 560, 960, 0.92], [C.barcos - 0.1, 0.7, 1950, 940, 0.82], [C.cuatro - 0.2, 0.8, 1150, 820, 0.48],
      [C.l7, 0.7, 1150, 1000, 0.8], [C.almirante, 0.6, 1420, 920, 1.05], [C.l8 - 0.05, 0.5, 1440, 870, 1.3], [C.cerdo8 - 0.1, 0.5, 1150, 920, 0.62]];
    function sceneShore(t) {
      const [cx, cy, z] = track(SCAM, t);
      g.save(); g.translate(540, 960); g.scale(z, z); g.translate(-cx, -cy);
      g.fillStyle = SKY; g.fillRect(-2000, -2000, 6000, 6000);
      cloud(200, 420, 1.2); cloud(1300, 320, 1); cloud(2400, 450, 1.3);
      sea(1350, 4000, 1110, t);
      g.fillStyle = "#F2D98A"; P(); g.moveTo(-2000, 1110); g.lineTo(1550, 1110); g.quadraticCurveTo(1450, 1500, 1200, 3000); g.lineTo(-2000, 3000); g.closePath(); g.fill(); ink(8);
      g.fillStyle = GRASS; P(); g.moveTo(-2000, 1110); g.lineTo(1180, 1110); g.quadraticCurveTo(1080, 1500, 900, 3000); g.lineTo(-2000, 3000); g.closePath(); g.fill(); ink(8);
      const ships = [[1800, 1230, 0.8], [2300, 1190, 0.72], [2750, 1250, 0.85], [2100, 1400, 0.95], [2650, 1450, 0.9]];
      ships.forEach(([sx, sy, ss], i) => { const k = smooth((t - C.barcos - i * 0.25) / 1.4); if (k > 0) ship(sx + (1 - k) * 1600, sy, ss, t, i); });
      const lower = smooth((t - C.cerdo8) / 0.6), aim = lerp(1.45, 0.3, lower);
      cannon(260, 1180, 0.9, lerp(0.25, -0.05, lower)); cannon(640, 1220, 0.9, lerp(0.25, -0.05, lower));
      // Cutlar, worried, with the handcuffs floating over him
      person(CUTLAR({ x: 880, y: 1230, s: 0.9, f: -1, armR: 0.2, armL: 0.2, mood: -1, seed: 0.4, look: 0.8, m: 0, smile: -6 }), t);
      if (t >= C.arrestarlo && t < C.barcos) { const k = back((t - C.arrestarlo) / 0.4); g.save(); g.translate(880, 560 + Math.sin(t * 3) * 10); g.scale(k, k);
        ell(-40, 0, 36, 36, null, 0); P(); g.arc(-40, 0, 36, 0, Math.PI * 2); g.lineWidth = 14; g.strokeStyle = "#9A9AAE"; g.stroke(); P(); g.arc(40, 0, 36, 0, Math.PI * 2); g.stroke();
        line([-4, 0, 4, 0], 10, "#9A9AAE"); g.restore(); }
      const marchT = C.soldados;
      for (let i = 0; i < 7; i++) {
        const k = smooth((t - marchT - i * 0.18) / 1.8), x = lerp(-700 - i * 120, 60 + (i % 4) * 160, k), y = 1200 + Math.floor(i / 4) * 130;
        if (t < marchT - 0.2) continue;
        person(SOLDIER({ x, y, armR: t > C.barcos ? aim : 0.3, armL: 0.2, walk: k > 0 && k < 1, seed: i * 0.7, look: 0.8, mood: t > C.barcos && t < C.cerdo8 + 0.6 ? 1 : 0, closed: false }), t);
      }
      // Baynes rows in and steps on the beach
      if (t >= C.almirante - 0.2) {
        const k = smooth((t - C.almirante + 0.2) / 0.9), bx = lerp(1900, 1430, k);
        person(BAYNES({ x: bx, y: 1230, s: 0.95, f: -1, armR: t >= C.l8 + 0.4 && t < C.cerdo8 + 0.5 ? 1.7 : 0.2, armL: 0.15, walk: k > 0 && k < 1, m: mouth("baynes", t), mood: -0.4, seed: 2.2, look: 0.6, smile: 6 }), t);
      }
      g.restore();
    }
    function sceneGrave(t) {
      g.fillStyle = "#BFE6F5"; g.fillRect(0, 0, 1080, 1920);
      cloud(200, 520, 1); cloud(860, 440, 0.8);
      P(); g.moveTo(-50, 1300); g.quadraticCurveTo(540, 980, 1130, 1300); g.lineTo(1130, 1920); g.lineTo(-50, 1920); g.closePath(); fill(GRASS); ink(8);
      rr(400, 900, 280, 300, 120, "#B9B9C8", 8); txt("AQUÍ YACE", 540, 1010, 40); txt("EL CERDO", 540, 1070, 44); txt("1859", 540, 1140, 46, "#5B5B6E");
      [[360, 1200], [720, 1195], [430, 1215], [660, 1218]].forEach(([x, y], i) => { line([x, y, x, y - 50], 6, GRASSD); ell(x, y - 60, 18, 18, ["#E63946", "#FFD23F", "#F28B82", "#FFFFFF"][i], 5); });
      flag(250, 1290, 0.6, "us", t, 0.55); flag(830, 1290, 0.6, "uk", t, 0.55);
      if (t >= C.uno) { const k = smooth((t - C.uno) / 1.0); pig(470, 1150 - k * 330 + Math.sin(t * 2.5) * 10, 0.9, t, "ghost"); }
    }

    function draw(t) {
      g.setTransform(1, 0, 0, 1, 0, 0);
      g.clearRect(0, 0, 1080, 1920);
      const W1 = 0.35;
      if (t < C.l2) { sceneMap(t, "hook"); return; }
      if (t < C.l2 + 0.6) {  // zoom-morph: the pig on the map becomes the pig in the farm
        const k = smooth((t - C.l2) / 0.6);
        g.save(); g.translate(540, 1060); g.scale(1 + k * 5, 1 + k * 5); g.translate(-540, -1060); sceneMap(t, "hook"); g.restore();
        g.save(); g.globalAlpha = k; g.translate(540, 960); g.scale(lerp(0.4, 1, k), lerp(0.4, 1, k)); g.translate(-540, -960); sceneFarm(t); g.restore(); g.globalAlpha = 1; return;
      }
      const whip = (t0, a, b) => { const k = smooth((t - t0) / W1); g.save(); g.translate(-1080 * k, 0); a(t); g.restore(); g.save(); g.translate(1080 * (1 - k), 0); b(t); g.restore(); };
      if (t < C.l5 - 0.15) return sceneFarm(t);
      if (t < C.l5 - 0.15 + W1) return whip(C.l5 - 0.15, sceneFarm, sceneShore);
      if (t < C.l9) return sceneShore(t);
      if (t < C.l9 + 0.6) {  // zoom-out morph: the shore shrinks into the island on the map
        const k = smooth((t - C.l9) / 0.6);
        g.save(); g.translate(540, 1000); g.scale(lerp(3, 1, k), lerp(3, 1, k)); g.translate(-540, -1000); sceneMap(t, "years"); g.restore();
        g.save(); g.globalAlpha = 1 - k; g.translate(540, 1000); g.scale(lerp(1, 0.2, k), lerp(1, 0.2, k)); g.translate(-540, -1000); sceneShore(t); g.restore(); g.globalAlpha = 1; return;
      }
      if (t < C.l10 - 0.15) return sceneMap(t, "years");
      if (t < C.l10 - 0.15 + W1) return whip(C.l10 - 0.15, (u) => sceneMap(u, "years"), sceneGrave);
      if (t < C.end - 0.05) return sceneGrave(t);
      sceneMap(t, "hook");
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
    sfx = [("oink", "el_oink", 0.1, 1.2, 0.4), ("bugle", "el_bugle", C["cerdo0"], 1.5, 0.3), ("whoosh1", "whoosh", C["l2"] - 0.05, 0.57, 0.35),
           ("oink2", "el_oink", C["papas"] - 0.6, 1.2, 0.35), ("shot", "el_shot", C["pum"], 0.8, 0.55), ("squeal", "el_squeal", C["pum"] + 0.1, 0.8, 0.4),
           ("cash", "el_cash", C["diez"], 0.8, 0.4), ("cash2", "el_cash", C["cien"], 0.8, 0.45), ("whoosh2", "whoosh", C["l5"] - 0.2, 0.57, 0.35),
           ("drum", "el_drum", C["soldados"], 2.0, 0.4), ("horn", "el_horn", C["barcos"] + 0.3, 2.0, 0.4), ("bugle2", "el_bugle", C["cuatro"], 1.5, 0.3),
           ("deflate", "el_deflate", C["l8end"] - 0.1, 2.0, 0.4), ("whoosh3", "whoosh", C["l9"], 0.57, 0.3), ("stamp", "el_stamp", C["estados"], 0.6, 0.55),
           ("whoosh4", "whoosh", C["l10"] - 0.2, 0.57, 0.3), ("harp", "el_harp", C["uno"], 1.5, 0.45),
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
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #8ED9F0; }}
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
