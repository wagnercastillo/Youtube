"""EP10: escribe compositions/stage.html (Diógenes vs Alejandro, caricatura estilo vasija griega) e index.html.

  python -I audio/build_video.py     (después de gen_audio_el.py y build.py)

Un canvas 1080×1920 se dibuja por cuadro desde hf-seek: mundo de Corinto en figuras rojas (terracota sobre negro, grecas),
cámara con llaves por palabra (sigue a quien habla), bocas desde mouth.json, el pollo desplumado se transforma en el sol,
la sombra de Alejandro tapa a Diógenes, pantalla dividida Babilonia / Corinto. Rótulos HTML con máscara (clip-path).
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


END = round(LINES["l9"]["end"] + 0.8, 2)
TOTAL = round(END + CARD, 2)
C = {
    "magno": W("l0", "magno"), "tipo": W("l0", "tipo"),
    "l1": L("l1"), "diogenes": W("l1", "diogenes"), "tinaja": W("l1", "tinaja"), "perro": W("l1", "perro"), "como": W("l1", "como"),
    "l2": L("l2"), "platon": W("l2", "platon"), "bipedo": W("l2", "bipedo"), "pollo": W("l2", "pollo"), "aqui": W("l2", "aqui"),
    "l3": L("l3"), "corinto": W("l3", "corinto"), "sol": W("l3", "sol"), "rey": W("l3", "rey"), "mundo": W("l3", "mundo"),
    "l4": L("l4"), "pideme": W("l4", "pideme"), "l5": L("l5"), "quitate": W("l5", "quitate"), "tapas": W("l5", "tapas"),
    "l6": L("l6"), "risa": W("l6", "risa"), "dijo": W("l6", "dijo"),
    "l7": L("l7"), "fuera": W("l7", "fuera"), "ser": W("l7", "ser"),
    "l8": L("l8"), "mismo": W("l8", "mismo"), "palacio": W("l8", "palacio"), "otro": W("l8", "otro"), "nada": W("l8", "nada"),
    "l9": L("l9"), "nadie": W("l9", "nadie"), "end": END,
}
BANNERS = [  # id, text, in, out
    ("b1", "DIÓGENES · FILÓSOFO GRIEGO", C["diogenes"], C["perro"] - 0.05),
    ("b2", "APODO: «EL PERRO» 🐶", C["perro"], C["l2"] - 0.15),
    ("b3", "PLATÓN · EL FAMOSO", C["platon"], C["pollo"] - 0.05),
    ("b4", "«¡AQUÍ ESTÁ TU HOMBRE!»", C["aqui"], C["l3"] - 0.15),
    ("b5", "CORINTO, GRECIA", C["corinto"], C["rey"] - 0.05),
    ("b6", "ALEJANDRO MAGNO 👑", C["rey"] + 0.3, C["l5"] - 0.1),
    ("b7", "323 a. C. · ¿EL MISMO DÍA?", C["mismo"], C["l9"] - 0.15),
    ("b8", "NADIE LE DECÍA QUE NO…", C["nadie"], C["end"] - 0.1),
]
SOURCES = [  # id, text, in, out
    ("s1", "Fuente: Plutarco, Vida de Alejandro, 14", C["l7"], C["l8"] - 0.1),
    ("s2", "Fuente: Diógenes Laercio, Vidas VI, 79", C["mismo"], C["l9"] - 0.15),
]
IN_CLIP, SHOW, OUT_CLIP = "inset(-30px 1200px -30px -30px)", "inset(-30px -30px -30px -30px)", "inset(-30px -30px -30px 1200px)"


def stage_html():
    banners = "\n".join(f'    <div id="{i}" class="ban"><span>{t}</span></div>' for i, t, _, _ in BANNERS)
    banners += "\n" + "\n".join(f'    <div id="{i}" class="src"><span>{t}</span></div>' for i, t, _, _ in SOURCES)
    tw = ['tl.fromTo("#h1", { clipPath: "' + IN_CLIP + '" }, { clipPath: "' + SHOW + '", duration: 0.3, ease: "power3.out" }, 0.03);',
          'tl.fromTo("#h2", { clipPath: "' + IN_CLIP + '" }, { clipPath: "' + SHOW + '", duration: 0.3, ease: "power3.out" }, 0.18);',
          f'tl.fromTo("#h3", {{ scale: 0, rotation: -14 }}, {{ scale: 1, rotation: -6, duration: 0.3, ease: "back.out(2.4)" }}, {C["tipo"]});',
          f'tl.fromTo("#hook", {{ clipPath: "{SHOW}" }}, {{ clipPath: "{OUT_CLIP}", duration: 0.3, ease: "power3.in", immediateRender: false }}, {round(C["l1"] - 0.05, 3)});',
          f'tl.fromTo("#h3", {{ clipPath: "{SHOW}" }}, {{ clipPath: "{OUT_CLIP}", duration: 0.3, ease: "power3.in", immediateRender: false }}, {round(C["l1"] + 0.05, 3)});']
    for i, _, a, b in BANNERS + SOURCES:
        tw += [f'tl.fromTo("#{i}", {{ clipPath: "{IN_CLIP}" }}, {{ clipPath: "{SHOW}", duration: 0.32, ease: "power3.out" }}, {round(a, 3)});',
               f'tl.fromTo("#{i}", {{ clipPath: "{SHOW}" }}, {{ clipPath: "{OUT_CLIP}", duration: 0.22, ease: "power3.in", immediateRender: false }}, {round(b, 3)});']
    q = C["quitate"]
    tw += [f'tl.fromTo("#stamp", {{ clipPath: "inset(0px 100% 0px 0px)", scale: 1.25 }}, {{ clipPath: "inset(0px 0% 0px 0px)", scale: 1, duration: 0.22, ease: "power4.out" }}, {q});',
           f'tl.fromTo("#stamp", {{ clipPath: "inset(0px 0% 0px 0px)" }}, {{ clipPath: "inset(0px 0px 0px 100%)", duration: 0.2, ease: "power3.in", immediateRender: false }}, {round(C["l6"] + 0.2, 3)});',
           f'tl.fromTo("#lblL", {{ clipPath: "{IN_CLIP}" }}, {{ clipPath: "{SHOW}", duration: 0.3, ease: "power3.out" }}, {C["palacio"]});',
           f'tl.fromTo("#lblR", {{ clipPath: "{IN_CLIP}" }}, {{ clipPath: "{SHOW}", duration: 0.3, ease: "power3.out" }}, {C["otro"]});',
           f'tl.fromTo(["#lblL", "#lblR"], {{ opacity: 1 }}, {{ opacity: 0, duration: 0.2, immediateRender: false }}, {round(C["l9"] - 0.15, 3)});']
    return (STAGE.replace("__C__", json.dumps(C)).replace("__M__", json.dumps(MOUTH, separators=(",", ":")))
            .replace("__BANNERS__", banners).replace("__TW__", "\n".join("    " + x for x in tw)))


STAGE = r'''<template>
  <style>
    #root { position: absolute; inset: 0; overflow: hidden; background: #1B120D; font-family: "Archivo Black", sans-serif; }
    #cv { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
    .ban { position: absolute; left: 0; top: 250px; width: 1080px; text-align: center; clip-path: inset(-30px 1200px -30px -30px); }
    .ban span { display: inline-block; max-width: 980px; font-size: 52px; line-height: 1.1; padding: 16px 28px 10px; background: #F3E2C3;
      color: #1A120C; border: 8px solid #1A120C; box-shadow: 8px 8px 0 #E2874A; letter-spacing: 1px; }
    #b2 span, #b6 span { background: #F2B33D; } #b4 span { background: #FFFFFF; } #b7 span { background: #C8372D; color: #FFFFFF; }
    .src { position: absolute; left: 270px; top: 1450px; width: 780px; text-align: center; clip-path: inset(-30px 1200px -30px -30px); }
    .src span { display: inline-block; font-family: "Nunito", sans-serif; font-weight: 800; font-size: 30px; padding: 6px 16px;
      background: rgba(26,18,12,0.85); color: #F3E2C3; border-radius: 10px; }
    #hook { position: absolute; left: 0; top: 230px; width: 1080px; }
    .tags { width: 1080px; text-align: center; margin-bottom: 22px; clip-path: inset(-30px 1200px -30px -30px); }
    .tags span { display: inline-block; white-space: nowrap; font-size: 66px; line-height: 1; padding: 16px 30px 10px; color: #1A120C;
      border: 8px solid #1A120C; box-shadow: 8px 8px 0 #E2874A; }
    #h1 span { background: #FFFFFF; } #h2 span { background: #F2B33D; }
    #h3 { position: absolute; left: 700px; top: 330px; transform-origin: 50% 50%; }
    #h3 span { display: inline-block; font-size: 120px; line-height: 1; padding: 14px 30px 4px; color: #FFFFFF; background: #C8372D;
      border: 10px solid #1A120C; }
    #stamp { position: absolute; left: 0; top: 330px; width: 1080px; text-align: center; clip-path: inset(0px 100% 0px 0px); }
    #stamp span { display: inline-block; font-size: 150px; line-height: 1; padding: 18px 40px 6px; color: #FFFFFF; background: #C8372D;
      border: 12px solid #1A120C; box-shadow: 12px 12px 0 #1A120C; transform: rotate(-4deg); }
    .lbl { position: absolute; top: 1180px; width: 540px; text-align: center; clip-path: inset(-30px 1200px -30px -30px); }
    .lbl span { display: inline-block; font-size: 46px; padding: 12px 22px 6px; background: #1A120C; color: #F2B33D; border: 6px solid #F3E2C3; }
    #lblL { left: 0; } #lblR { left: 540px; }
  </style>
  <div id="root" data-composition-id="stage" data-width="1080" data-height="1920">
    <canvas id="cv" width="1080" height="1920" data-layout-allow-overflow></canvas>
__BANNERS__
    <div id="hook">
      <div id="h1" class="tags"><span>NADIE LE DECÍA QUE NO</span></div>
      <div id="h2" class="tags"><span>A ALEJANDRO MAGNO…</span></div>
    </div>
    <div id="h3"><span>NO</span></div>
    <div id="stamp"><span>¡QUÍTATE!</span></div>
    <div id="lblL" class="lbl"><span>BABILONIA 👑</span></div>
    <div id="lblR" class="lbl"><span>CORINTO 🏺</span></div>
  </div>
  <script>
    const C = __C__;
    const M = __M__;
    const cv = document.getElementById("cv"), g = cv.getContext("2d");
    const clamp = (k) => Math.min(Math.max(k, 0), 1);
    const smooth = (k) => { k = clamp(k); return k * k * (3 - 2 * k); };
    const back = (k) => { k = clamp(k); const s = 1.7; return 1 + (s + 1) * Math.pow(k - 1, 3) + s * Math.pow(k - 1, 2); };
    const lerp = (a, b, k) => a + (b - a) * k;
    const mix = (c1, c2, k) => { const a = parseInt(c1.slice(1), 16), b = parseInt(c2.slice(1), 16);
      const r = Math.round(lerp(a >> 16, b >> 16, k)), gg = Math.round(lerp((a >> 8) & 255, (b >> 8) & 255, k)), bl = Math.round(lerp(a & 255, b & 255, k));
      return "rgb(" + r + "," + gg + "," + bl + ")"; };
    function track(keys, t) {  // keys: [time, dur, ...values]; eases from the previous key's values
      let i = 0;
      while (i + 1 < keys.length && t >= keys[i + 1][0]) i++;
      if (i === 0) return keys[0].slice(2);
      const cur = keys[i], prev = keys[i - 1], k = smooth((t - cur[0]) / cur[1]);
      const from = i >= 2 ? track(keys.slice(0, i), cur[0]) : prev.slice(2);
      return cur.slice(2).map((v, j) => lerp(from[j], v, k));
    }
    const mouth = (spk, t) => (M[spk] || [])[Math.floor(t * 30)] || 0;
    const blink = (t, seed) => ((t + seed) % 3.3) < 0.11;

    const INK = "#1A120C", TER = "#E2874A", TERD = "#B85F2E", CRE = "#F3E2C3", GOLD = "#F2B33D", RED = "#C8372D", BG = "#1B120D";
    const GROUND = 1250;
    const P = () => g.beginPath();
    const fill = (c) => { g.fillStyle = c; g.fill(); };
    const ink = (w) => { g.lineWidth = w || 7; g.strokeStyle = INK; g.lineJoin = "round"; g.lineCap = "round"; g.stroke(); };
    function ell(x, y, rx, ry, c, w, rot) { P(); g.ellipse(x, y, Math.abs(rx), Math.abs(ry), rot || 0, 0, Math.PI * 2); if (c) fill(c); if (w !== 0) ink(w); }
    function limb(x1, y1, x2, y2, w, c) {
      g.lineCap = "round"; P(); g.moveTo(x1, y1); g.lineTo(x2, y2);
      g.strokeStyle = INK; g.lineWidth = w + 12; g.stroke(); g.strokeStyle = c; g.lineWidth = w; g.stroke();
    }
    function line(pts, w, c) { P(); g.moveTo(pts[0], pts[1]); for (let i = 2; i < pts.length; i += 2) g.lineTo(pts[i], pts[i + 1]); g.lineWidth = w; g.strokeStyle = c || INK; g.lineCap = "round"; g.lineJoin = "round"; g.stroke(); }
    function mouthShape(x, y, w, v, smile) {
      if (v < 0.06) { P(); g.moveTo(x - w * 0.6, y); g.quadraticCurveTo(x, y + (smile || 8), x + w * 0.6, y); ink(6); return; }
      ell(x, y + 4, w * (0.55 + 0.35 * v), 5 + v * 22, "#5A1A12", 6);
      ell(x, y + 10 + v * 10, w * 0.3, 3 + v * 6, "#E05A5A", 0);
    }
    function eye(x, y, r, look, closed, half) {
      if (closed) { P(); g.moveTo(x - r, y); g.quadraticCurveTo(x, y + r * 0.7, x + r, y); ink(6); return; }
      ell(x, y, r, r * 1.1, "#FFFFFF", 5);
      ell(x + look * r * 0.4, y + 2, r * 0.5, r * 0.55, INK, 0);
      if (half) { P(); g.ellipse(x, y, r + 3, r * 1.1 + 3, 0, Math.PI, Math.PI * 2); fill(TER); ink(5); }
    }
    function meander(x0, x1, y, h, col) {  // greek key band
      g.fillStyle = BG; g.fillRect(x0, y, x1 - x0, h);
      const u = h * 0.9, s0 = Math.floor(x0 / u) * u;
      for (let x = s0; x < x1; x += u) line([x, y + h * 0.85, x, y + h * 0.15, x + u * 0.75, y + h * 0.15, x + u * 0.75, y + h * 0.65, x + u * 0.35, y + h * 0.65, x + u * 0.35, y + h * 0.42], h * 0.1, col);
      line([x0, y + 3, x1, y + 3], 6, col); line([x0, y + h - 3, x1, y + h - 3], 6, col);
    }

    // ---------- characters (local origin = feet on the ground) ----------
    function diogenes(x, t, arm, eyes, m) {  // sitting, facing left; arm 0..1 raises the right hand; returns hand position
      const y = GROUND, br = Math.sin(t * 2.1) * 4;
      ell(x - 95, y - 12, 46, 18, TER, 6); ell(x - 10, y - 12, 46, 18, TER, 6);
      P(); g.moveTo(x - 130, y - 10); g.quadraticCurveTo(x - 140, y - 215 + br, x - 10, y - 225 + br);
      g.quadraticCurveTo(x + 125, y - 215 + br, x + 115, y - 10); g.closePath(); fill(CRE); ink();
      line([x - 70, y - 190 + br, x - 20, y - 110, x + 80, y - 30], 5);
      line([x + 40, y - 200 + br, x + 70, y - 120], 5);
      const sx = x - 40, sy = y - 185 + br, a = lerp(0.35, 2.75, arm);
      const hx = sx - Math.sin(a) * 150, hy = sy + Math.cos(a) * 150;
      limb(sx, sy, hx, hy, 30, TER);
      const hx2 = x + 60, hy2 = y - 70;
      limb(x + 60, y - 175 + br, hx2, hy2, 30, TER);
      const X = x - 10, Y = y - 300 + br;
      ell(X + 56, Y + 4, 15, 22, TER, 6);
      ell(X, Y, 66, 72, TER, 7);
      P(); g.ellipse(X - 8, Y - 40, 34, 14, -0.3, Math.PI * 1.1, Math.PI * 1.8); g.lineWidth = 6; g.strokeStyle = "#F7B98A"; g.stroke();
      P(); g.moveTo(X - 66, Y + 8); g.quadraticCurveTo(X - 75, Y + 120, X - 20, Y + 175); g.quadraticCurveTo(X + 5, Y + 140, X + 25, Y + 160);
      g.quadraticCurveTo(X + 55, Y + 100, X + 58, Y + 30); g.quadraticCurveTo(X, Y + 60, X - 66, Y + 8); fill("#D9D2C3"); ink();
      line([X - 40, Y + 80, X - 30, Y + 140], 4, "#9A9384"); line([X + 10, Y + 80, X + 15, Y + 135], 4, "#9A9384");
      ell(X - 66, Y + 4, 22, 18, TER, 6);
      line([X - 52, Y - 34, X - 18, Y - 42], 9, "#D9D2C3"); line([X - 4, Y - 42, X + 26, Y - 34], 9, "#D9D2C3");
      const shut = eyes === "closed" || blink(t, 0.7);
      eye(X - 38, Y - 16, 13, -1, shut, false);
      eye(X + 8, Y - 16, 13, -1, shut || eyes === "one", false);
      mouthShape(X - 30, Y + 44, 30, m, 6);
      return [hx, hy];
    }
    function alexander(x, t, arm, m, walk, chinUp) {  // standing, facing right
      const y = GROUND, st = walk > 0 ? Math.sin(t * 9) : 0, bob = walk > 0 ? Math.abs(Math.sin(t * 9)) * 10 : Math.sin(t * 1.8) * 3;
      P(); g.moveTo(x - 45, y - 360 - bob); g.quadraticCurveTo(x - 190, y - 220, x - 150 - st * 10, y - 30); g.lineTo(x - 30, y - 60);
      g.closePath(); fill(RED); ink();
      limb(x - 25, y - 170, x - 30 + st * 30, y - 10, 30, TER); limb(x + 25, y - 170, x + 30 - st * 30, y - 10, 30, TER);
      ell(x - 30 + st * 30, y - 8, 30, 12, "#7A4A2A", 5); ell(x + 38 - st * 30, y - 8, 30, 12, "#7A4A2A", 5);
      P(); g.moveTo(x - 75, y - 230 - bob); g.lineTo(x + 75, y - 230 - bob); g.lineTo(x + 90, y - 150 - bob); g.lineTo(x - 90, y - 150 - bob); g.closePath(); fill(RED); ink();
      for (let k = -3; k <= 3; k++) line([x + k * 24, y - 220 - bob, x + k * 27, y - 156 - bob], 12, GOLD);
      P(); g.roundRect(x - 70, y - 360 - bob, 140, 140, 30); fill(GOLD); ink();
      line([x - 35, y - 320 - bob, x, y - 300 - bob, x + 35, y - 320 - bob], 5);
      limb(x - 55, y - 335 - bob, x - 75, y - 210 - bob, 28, TER);
      const a = lerp(0.25, 1.75, arm), sx = x + 55, sy = y - 335 - bob;
      limb(sx, sy, sx + Math.sin(a) * 150, sy + Math.cos(a) * 150, 28, TER);
      ell(sx + Math.sin(a) * 158, sy + Math.cos(a) * 158, 20, 20, TER, 6);
      const X = x + 8, Y = y - 440 - bob, tilt = chinUp ? -0.12 : 0;
      g.save(); g.translate(X, Y); g.rotate(tilt);
      for (let k = 0; k < 9; k++) ell(-50 + Math.cos(k * 0.75) * 10 - (k % 3) * 8, -40 + k * 9 - (k > 5 ? 20 : 0), 26, 24, GOLD, 5);
      ell(0, 0, 58, 64, TER, 7);
      for (let k = 0; k < 6; k++) ell(-40 + k * 15, -54 + Math.abs(k - 2.5) * 4, 20, 18, GOLD, 5);
      line([-55, -30, 50, -40], 8, "#3E7A3A"); for (let k = 0; k < 5; k++) ell(-45 + k * 22, -38 - k * 2, 9, 5, "#5FA055", 3, -0.6);
      eye(26, -8, 12, 1, blink(t, 1.9), true);
      line([12, -30, 42, -26], 8);
      P(); g.moveTo(52, -4); g.lineTo(68, 16); g.lineTo(50, 20); ink(6);
      mouthShape(32, 34, 26, m, 10);
      g.restore();
    }
    function soldier(x, s, t, i, laugh) {
      const ph = t * 13 + i * 1.7, lb = laugh * Math.abs(Math.sin(ph)) * 12, tilt = -laugh * (0.25 + 0.1 * Math.sin(ph));
      g.save(); g.translate(x, GROUND); g.scale(s, s);
      line([60, -40, 70 - lb * 0.3, -560], 9, "#7A4A2A"); P(); g.moveTo(70 - lb * 0.3, -600); g.lineTo(58, -555); g.lineTo(82, -555); g.closePath(); fill("#C9C3B5"); ink(5);
      limb(-20, -160, -22, -8, 26, TER); limb(20, -160, 22, -8, 26, TER);
      P(); g.roundRect(-55, -330 - lb, 110, 180, 24); fill(RED); ink();
      g.save(); g.translate(0, -390 - lb); g.rotate(tilt);
      ell(0, 0, 48, 52, TER, 7);
      P(); g.arc(0, -8, 54, Math.PI * 1.02, Math.PI * 1.98); g.lineTo(54, 10); g.lineTo(30, 10); g.lineTo(30, -12); g.lineTo(-30, -12); g.lineTo(-30, 10); g.lineTo(-54, 10); g.closePath(); fill(GOLD); ink(6);
      P(); g.moveTo(-50, -50); g.quadraticCurveTo(0, -120, 50, -50); g.lineWidth = 22; g.strokeStyle = RED; g.stroke();
      if (laugh > 0.1) mouthShape(14, 26, 24, 0.5 + 0.5 * Math.abs(Math.sin(ph)), 8); else mouthShape(14, 26, 22, 0, 4);
      eye(18, 2, 8, 1, laugh > 0.1, false);
      g.restore();
      ell(-30, -250 - lb, 70, 74, GOLD, 7); ell(-30, -250 - lb, 22, 22, RED, 5);
      g.restore();
    }
    function plato(x, t, m) {  // standing, facing left, points at the board
      const y = GROUND, b = Math.sin(t * 1.6) * 3;
      limb(x - 25, y - 170, x - 30, y - 10, 32, TER); limb(x + 25, y - 170, x + 30, y - 10, 32, TER);
      P(); g.moveTo(x - 95, y - 380 - b); g.quadraticCurveTo(x - 110, y - 200, x - 80, y - 120); g.lineTo(x + 95, y - 120); g.quadraticCurveTo(x + 110, y - 260, x + 85, y - 380 - b); g.closePath(); fill(CRE); ink();
      line([x - 80, y - 360, x + 60, y - 160], 5);
      limb(x - 70, y - 350 - b, x - 230, y - 400 - b + Math.sin(t * 3) * 10, 28, TER);
      line([x - 230, y - 400 - b, x - 330, y - 450 - b], 7, "#7A4A2A");
      const X = x - 5, Y = y - 470 - b;
      ell(X, Y, 64, 70, TER, 7);
      P(); g.moveTo(X - 62, Y - 4); g.quadraticCurveTo(X - 70, Y + 120, X, Y + 150); g.quadraticCurveTo(X + 70, Y + 120, X + 62, Y - 4); g.quadraticCurveTo(X, Y + 40, X - 62, Y - 4); fill("#5A3A22"); ink();
      P(); g.arc(X, Y - 10, 66, Math.PI * 1.05, Math.PI * 1.95); g.lineWidth = 26; g.strokeStyle = "#5A3A22"; g.stroke();
      ell(X - 60, Y + 6, 18, 15, TER, 6);
      eye(X - 30, Y - 14, 12, -1, blink(t, 2.4), true); eye(X + 12, Y - 14, 12, -1, blink(t, 2.4), true);
      mouthShape(X - 25, Y + 46, 26, m, 6);
    }
    function chicken(x, y, s, rot, col, rays) {
      g.save(); g.translate(x, y); g.rotate(rot); g.scale(s, s);
      if (rays > 0) for (let k = 0; k < 12; k++) { const a = k * Math.PI / 6; line([Math.cos(a) * 95, Math.sin(a) * 95, Math.cos(a) * (95 + 70 * rays), Math.sin(a) * (95 + 70 * rays)], 16, GOLD); }
      const body = mix("#F4A7A0", GOLD, rays);
      const legs = 1 - rays;
      if (legs > 0) { g.globalAlpha = legs; line([-20, 50, -26, 110, -40, 118], 8, "#E8A33A"); line([20, 50, 26, 110, 40, 118], 8, "#E8A33A"); g.globalAlpha = 1; }
      ell(0, 0, 90, 75, body, 7);
      if (legs > 0) { g.globalAlpha = legs; ell(70, -60, 30, 28, body, 6); P(); g.moveTo(96, -62); g.lineTo(122, -54); g.lineTo(96, -46); g.closePath(); fill("#E8A33A"); ink(4);
        ell(64, -92, 10, 14, RED, 4); ell(78, -92, 10, 14, RED, 4); eye(74, -64, 7, 1, true, false); g.globalAlpha = 1; }
      for (let k = 0; k < 7; k++) ell(-50 + (k * 37) % 90, -30 + (k * 23) % 60, 3, 3, mix("#C97B74", "#D9962A", rays), 0);
      g.restore();
    }
    function dog(x, y, s, m, wink, t) {  // Canela, the narrator: head + shoulders peeking from the bottom-left
      g.save(); g.translate(x, y); g.scale(s, s);
      const tilt = Math.sin(t * 2.3) * 0.06;
      g.rotate(tilt);
      P(); g.moveTo(-90, 40); g.quadraticCurveTo(0, -20, 90, 40); g.lineTo(100, 130); g.lineTo(-100, 130); g.closePath(); fill("#B5702F"); ink();
      for (let k = 0; k < 7; k++) ell(-60 + k * 20, 40 + Math.abs(k - 3) * -4 + 14, 9, 9, "#FFFFFF", 4);
      ell(-78, -60, 30, 62, "#6B3A1A", 7, 0.35); ell(78, -60, 30, 62, "#6B3A1A", 7, -0.35);
      ell(0, -70, 86, 80, "#C98A45", 7);
      ell(0, -36, 52, 38, "#F3E2C3", 6);
      ell(0, -60, 18, 13, INK, 0);
      eye(-34, -100, 13, 0, blink(t, 0.3), false);
      eye(34, -100, 13, 0, wink || blink(t, 0.3), false);
      mouthShape(0, -28, 30, m, 8);
      if (m > 0.4) ell(6, -8, 12, 14, "#E05A5A", 4);
      g.restore();
    }
    function sun(x, y, r, a, t) {
      g.globalAlpha = a;
      const gr = g.createRadialGradient(x, y, r * 0.5, x, y, r * 3.2); gr.addColorStop(0, "rgba(242,179,61,0.45)"); gr.addColorStop(1, "rgba(242,179,61,0)");
      g.fillStyle = gr; g.fillRect(x - r * 3.2, y - r * 3.2, r * 6.4, r * 6.4);
      for (let k = 0; k < 12; k++) { const an = k * Math.PI / 6 + t * 0.15; line([x + Math.cos(an) * r * 1.1, y + Math.sin(an) * r * 1.1, x + Math.cos(an) * r * 1.75, y + Math.sin(an) * r * 1.75], 16, GOLD); }
      ell(x, y, r, r, GOLD, 7);
      g.globalAlpha = 1;
    }
    function jar(x, y, s) {  // pithos lying on its side, mouth facing left
      g.save(); g.translate(x, y); g.scale(s, s);
      ell(0, 0, 270, 175, TER, 8);
      P(); g.ellipse(0, 0, 270, 175, 0, -0.9, 0.9); g.lineWidth = 34; g.strokeStyle = BG; g.stroke();
      for (let k = -2; k <= 2; k++) line([k * 60 - 20, -150 + Math.abs(k) * 12, k * 60 + 20, -150 + Math.abs(k) * 12], 8);
      line([-200, -60, 220, -60], 6); line([-200, 60, 220, 60], 6);
      ell(-262, 0, 44, 120, "#3A2418", 7);
      ell(-262, 0, 28, 100, BG, 0);
      g.restore();
    }
    function temple(x, s) {
      g.save(); g.translate(x, GROUND); g.scale(s, s); g.globalAlpha = 0.9;
      P(); g.moveTo(-260, -520); g.lineTo(0, -640); g.lineTo(260, -520); g.closePath(); fill("#3A2418"); g.lineWidth = 6; g.strokeStyle = "#5A3824"; g.stroke();
      g.fillStyle = "#3A2418"; g.fillRect(-270, -530, 540, 40);
      for (let k = 0; k < 6; k++) { g.fillStyle = "#33201A"; g.fillRect(-235 + k * 90, -490, 40, 490); }
      g.globalAlpha = 1; g.restore();
    }
    function board(x, y, t) {
      g.fillStyle = "#7A4A2A"; g.fillRect(x - 12, y - 12, 404, 274); ink(0);
      g.fillStyle = "#24392E"; g.fillRect(x, y, 380, 250);
      g.font = "italic bold 46px Georgia, serif"; g.fillStyle = "#F3E2C3"; g.textAlign = "left";
      const k = clamp((t - C.bipedo) / 1.0);
      if (t >= C.platon) g.fillText("HOMBRE =", x + 24, y + 70);
      if (k > 0) { g.save(); g.beginPath(); g.rect(x, y + 90, 380 * k, 150); g.clip(); g.fillText("BÍPEDO", x + 24, y + 140); g.fillText("SIN PLUMAS", x + 24, y + 200); g.restore(); }
      if (t >= C.aqui) { const q = smooth((t - C.aqui) / 0.25); line([x + 20, y + 20, x + 20 + 340 * q, y + 20 + 210 * q], 14, RED); if (q >= 1) line([x + 360, y + 20, x + 360 - 340 * smooth((t - C.aqui - 0.25) / 0.25), y + 20 + 210 * smooth((t - C.aqui - 0.25) / 0.25)], 14, RED); }
    }
    function feathers(cx, cy, t0, t) {
      const k = t - t0; if (k < 0 || k > 2.2) return;
      for (let i = 0; i < 14; i++) {
        const a = i * 2.39, sp = 260 + (i * 53) % 200;
        const fx = cx + Math.cos(a) * sp * Math.min(k, 0.6) + Math.sin(k * 3 + i) * 30, fy = cy + Math.sin(a) * sp * Math.min(k, 0.6) * 0.8 + k * k * 120;
        g.globalAlpha = clamp(1 - k / 2.2); ell(fx, fy, 22, 9, "#FFFFFF", 4, a + k * 2); g.globalAlpha = 1;
      }
    }

    // ---------- keys (all times are narration words) ----------
    const CAM = [[0, 1, 560, 960, 1.0], [C.magno, 1.4, 560, 920, 1.12], [C.tipo, 0.4, 1520, 1010, 1.12], [C.l1 + 0.3, 2.5, 1450, 1000, 1.32],
      [C.perro, 0.6, 1470, 990, 1.38], [C.l2 - 0.15, 0.35, 2900, 960, 1.0], [C.pollo, 0.6, 3120, 930, 1.12], [C.l3 - 0.1, 0.35, 1300, 940, 0.92],
      [C.rey, 2.2, 1220, 940, 0.92], [C.l4 - 0.1, 0.45, 1200, 860, 1.42], [C.l5 - 0.1, 0.3, 1450, 990, 1.9], [C.l6 - 0.05, 0.4, 1140, 980, 0.86],
      [C.dijo, 0.5, 1130, 900, 1.15], [C.l7 + 0.2, 1.4, 1120, 880, 1.25], [C.l9 - 0.1, 0.01, 560, 960, 1.0]];
    const ALEX = [[0, 1, 520, 0.3], [C.rey, 2.0, 1080, 0.3], [C.l4 - 0.05, 0.35, 1080, 1], [C.l5, 0.3, 1080, 0.15], [C.dijo, 0.3, 1080, 1.15],
      [C.l7 + 0.5, 1.0, 900, 0.4], [C.l9 - 0.1, 0.01, 520, 0.3]];
    const DIO = [[0, 1, 1460, 0], [C.l2 - 0.15, 0.01, 3330, 0], [C.pollo - 0.2, 0.3, 3330, 1], [C.l3 - 0.1, 0.01, 1460, 0], [C.l4, 1, 1460, 0]];

    function world(t) {
      const [cx, cy, z] = track(CAM, t);
      let shx = 0, shy = 0;
      const qk = t - C.quitate;
      if (qk >= 0 && qk < 0.4) { const d = (1 - qk / 0.4) * 22; shx = Math.sin(qk * 90) * d; shy = Math.cos(qk * 70) * d; }
      g.setTransform(z, 0, 0, z, 540 - cx * z + shx, 860 - cy * z + shy);
      // sky band: dark vase body with a soft warm glow once the sun is up
      g.fillStyle = BG; g.fillRect(-1000, -800, 6000, 2100);
      [-60, 820, 2100, 2650, 3500].forEach((x, i) => temple(x, 0.8 + (i % 2) * 0.15));
      g.fillStyle = "#6B3A22"; g.fillRect(-1000, GROUND, 6000, 1400);
      meander(-1000, 5000, GROUND, 52, TER);
      for (let k = 0; k < 40; k++) ell(-900 + k * 150, GROUND + 140 + (k % 3) * 60, 30, 8, "#5A301B", 0);

      // sun: appears from the chicken morph and sits right above where Alexander will stand
      const sunOn = t >= C.l3 + 0.85, SX = 1080, SY = 380;
      if (sunOn) sun(SX, SY, 80, 1, t);

      // army + Alexander
      const [ax, arm] = track(ALEX, t);
      const walking = t > C.rey && t < C.rey + 2.0;
      const laugh = t >= C.risa - 0.4 && t < C.dijo + 0.2 ? 1 : 0;
      const sold = [[-200, 0.82], [-330, 0.8], [-460, 0.78], [-590, 0.76], [-270, 0.9], [-410, 0.88], [-550, 0.86]];
      sold.forEach(([dx, s], i) => soldier(ax + dx + (walking ? Math.sin(t * 9 + i) * 6 : 0), s, t, i, laugh));
      const chin = t >= C.l4 - 0.1 && t < C.l5 + 0.3;
      alexander(ax, t, arm, mouth("alejandro", t), walking ? 1 : 0, chin);

      // Diogenes and his jar (or at Plato's academy during l2)
      const [dx, darm] = track(DIO, t);
      if (dx < 2500) jar(dx + 330, GROUND - 175, 1);
      let eyes = "open";
      if (t >= C.sol && t < C.quitate) eyes = "closed";
      if (t >= C.quitate && t < C.l6) eyes = "one";
      const [hx, hy] = diogenes(dx, t, darm, eyes, mouth("diogenes", t));
      // Alexander's shadow over Diogenes while he blocks the sun
      const sh = t >= C.rey + 1.8 && t < C.l7 + 0.9 ? smooth((t - C.rey - 1.8) / 0.4) * (1 - smooth((t - C.l7 - 0.5) / 0.4)) : 0;
      if (sh > 0) { const sg = g.createRadialGradient(dx - 20, GROUND - 200, 60, dx - 20, GROUND - 200, 260); sg.addColorStop(0, "rgba(8,5,3," + (0.55 * sh) + ")"); sg.addColorStop(1, "rgba(8,5,3,0)"); g.fillStyle = sg; g.fillRect(dx - 300, GROUND - 480, 560, 480); }

      // Plato's academy
      if (t >= C.l2 - 0.4 && t < C.l3 + 0.2) {
        board(2420, 640, t);
        plato(2900, t, mouth("narr", t) * 0);
      }
      // plucked chicken held up by Diogenes, then thrown to the table
      if (t >= C.pollo - 0.2 && t < C.l3) {
        const up = smooth((t - C.pollo + 0.2) / 0.3);
        chicken(hx, hy - 40, 0.9 * up, Math.sin(t * 8) * 0.15, "#F4A7A0", 0);
        feathers(hx, hy - 40, C.pollo, t);
      }
      g.setTransform(1, 0, 0, 1, 0, 0);
      // morph: the chicken flies up and becomes the sun (screen space, from the hand to the sun's screen spot)
      if (t >= C.l3 - 0.1 && t < C.l3 + 0.9) {
        const k = smooth((t - C.l3 + 0.1) / 0.95);
        const sx = 540 + (SX - cx) * z, sy = 860 + (SY - cy) * z;
        chicken(lerp(560, sx, k), lerp(820, sy, k) - Math.sin(k * Math.PI) * 160, lerp(0.9, 0.85 * z, k), k * 6.28, null, k);
      }
    }

    function split(t) {
      const k = smooth((t - C.l8) / 0.45);
      g.setTransform(1, 0, 0, 1, 0, 0);
      // left: Babylon palace (blue glazed bricks, gold), right: Corinth jar at sunset
      g.save(); P(); g.rect(0, 0, 540, 1920 * k); g.clip();
      g.fillStyle = "#1F3F7A"; g.fillRect(0, 0, 540, 1920);
      for (let r = 0; r < 40; r++) for (let c = 0; c < 8; c++) { g.fillStyle = (r + c) % 2 ? "#2B57A6" : "#24498C"; g.fillRect(c * 70 + (r % 2) * 35 - 35, 380 + r * 34, 68, 32); }
      for (let c = 0; c < 4; c++) { g.fillStyle = GOLD; g.fillRect(40 + c * 130, 520, 40, 700); ell(60 + c * 130, 520, 40, 18, GOLD, 5); }
      g.fillStyle = "#5A1E1E"; g.fillRect(70, 1080, 400, 160); ink(0);
      const glow = t >= C.palacio ? 1 : 0.5;
      g.globalAlpha = glow; P(); g.moveTo(170, 1060); g.lineTo(190, 960); g.lineTo(230, 1020); g.lineTo(270, 940); g.lineTo(310, 1020); g.lineTo(350, 960); g.lineTo(370, 1060); g.closePath(); fill(GOLD); ink(); g.globalAlpha = 1;
      if (t >= C.otro) { g.fillStyle = "rgba(0,0,0," + 0.45 * smooth((t - C.otro) / 0.4) + ")"; g.fillRect(0, 0, 540, 1920); }
      g.restore();
      g.save(); P(); g.rect(540, 1920 * (1 - k), 540, 1920); g.clip();
      const gr = g.createLinearGradient(0, 300, 0, 1250); gr.addColorStop(0, "#3B1F4A"); gr.addColorStop(0.6, "#C8572D"); gr.addColorStop(1, "#F2B33D");
      g.fillStyle = gr; g.fillRect(540, 0, 540, 1920);
      sun(810, 1120, 70, 1, t);
      g.fillStyle = "#3A2418"; g.fillRect(540, 1180, 540, 740);
      jar(870, 1060, 0.62);
      g.restore();
      line([540, 0, 540, 1920 * k], 10, "#F3E2C3");
    }

    function draw(t) {
      g.setTransform(1, 0, 0, 1, 0, 0);
      g.clearRect(0, 0, 1080, 1920);
      if (t >= C.l8 && t < C.l9 - 0.1) { world(t); split(t); } else world(t);
      g.setTransform(1, 0, 0, 1, 0, 0);
      // Canela the narrator: pops up on "el Perro", ducks while Alexander or Diogenes speak
      const speak = (t >= C.l4 - 0.1 && t < C.l6) || (t >= C.l7 - 0.05 && t < C.l8);
      const pop = back((t - C.perro) / 0.45), duck = speak ? 1 : 0;
      if (t >= C.perro) {
        const dy = lerp(0, 330, smooth(duck));
        dog(170, 1440 + (1 - pop) * 330 + dy, 0.95, mouth("narr", t), t >= C.nadie + 0.6, t);
      }
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
    sfx = [("fanfare", "el_fanfare", 0.05, 1.6, 0.3), ("whip1", "whoosh", C["tipo"] - 0.1, 0.57, 0.35), ("bark", "el_bark", C["como"], 0.6, 0.45),
           ("whip2", "whoosh", C["l2"] - 0.2, 0.57, 0.35), ("chicken", "el_chicken", C["pollo"], 1.0, 0.45), ("feathers", "el_feathers", C["pollo"] + 0.15, 0.8, 0.4),
           ("shimmer", "el_shimmer", C["l3"] + 0.3, 1.2, 0.4), ("march", "el_march", C["rey"], 2.0, 0.4), ("fanfare2", "el_fanfare", C["l4"] - 0.3, 1.6, 0.25),
           ("scratch", "el_scratch", C["quitate"] - 0.05, 0.8, 0.45), ("laugh", "el_laugh", C["risa"] - 0.4, 2.0, 0.4),
           ("gong", "el_gong", C["mismo"], 2.0, 0.35), ("whip3", "whoosh", C["l9"] - 0.15, 0.57, 0.35),
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
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #1B120D; }}
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
