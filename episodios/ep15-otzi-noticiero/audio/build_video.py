"""EP15: escribe compositions/stage.html (Ötzi como NOTICIERO de TV) e index.html.

  python -I audio/build_video.py     (después de gen_audio_el.py y build.py)

Canvas 1080×1920 por cuadro (estudio, enlace en pantalla dividida, reportera en la nieve, rayos X estilo CSI, tablero del caso)
+ gráficos de televisión en HTML con máscara: ÚLTIMA HORA, EN VIVO, rótulos inferiores, cintillo. Bocas desde mouth.json.
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


END = round(LINES["l8"]["end"] + 0.9, 2)
TOTAL = round(END + CARD, 2)
C = {"congelado": W("l0", "congelado"), "cinco0": W("l0", "cinco"),
     "l1": L("l1"), "reportera": W("l1", "reportera"), "l2": L("l2"), "turistas": W("l2", "turistas"), "cuerpo": W("l2", "cuerpo"), "frontera": W("l2", "frontera"),
     "l3": L("l3"), "alpinista": W("l3", "alpinista"), "taladro": W("l3", "taladro"), "l4": L("l4"),
     "l5": L("l5"), "cinco5": W("l5", "cinco"), "bautizaron": W("l5", "bautizaron"), "l6": L("l6"),
     "l7": L("l7"), "rayos": W("l7", "rayos"), "flecha": W("l7", "flecha"), "asesinaron": W("l7", "asesinaron"),
     "l8": L("l8"), "cabra": W("l8", "cabra"), "quien": W("l8", "quien"), "nadie": W("l8", "nadie"), "seguiremos": W("l8", "seguiremos"), "end": END}
GFX = [  # id, html, class, in, out
    ("gBreak", "ÚLTIMA HORA", "break", 0.05, C["l1"] - 0.1),
    ("gL1", "<b>HOMBRE CONGELADO EN LOS ALPES</b><i>¡LLEVABA MÁS DE 5,000 AÑOS!</i>", "lower", C["congelado"], C["l1"] - 0.1),
    ("gL2", "<b>19 DE SEPTIEMBRE DE 1991</b><i>ALPES DE ÖTZTAL · FRONTERA AUSTRIA–ITALIA</i>", "lower red", C["l2"] + 0.2, C["l3"] - 0.1),
    ("gL3", "<b>¿ALPINISTA RECIENTE?</b><i>LO SACARON… ¡CON TALADRO!</i>", "lower", C["alpinista"], C["l4"] - 0.1),
    ("gL5", "<b>ÖTZI · EL HOMBRE DE HIELO</b><i>VIVIÓ HACE MÁS DE 5,000 AÑOS</i>", "lower red", C["cinco5"], C["l6"] - 0.1),
    ("gL7", "<b>2001 · RAYOS X</b><i>PUNTA DE FLECHA EN EL HOMBRO IZQUIERDO</i>", "lower red", C["rayos"], C["l8"] - 0.1),
    ("gL8", "<b>ÚLTIMA COMIDA: CABRA MONTÉS</b><i>CASO ABIERTO · ¿QUIÉN LO MATÓ?</i>", "lower", C["cabra"], C["end"] - 0.15),
    ("gStamp", "¡ASESINATO!", "stamp", C["asesinaron"], C["l8"] - 0.1),
]
IN_CLIP, SHOW, OUT_CLIP = "inset(-40px 1200px -40px -40px)", "inset(-40px -40px -40px -40px)", "inset(-40px -40px -40px 1200px)"


def stage_html():
    gfx = "\n".join(f'    <div id="{i}" class="g {cls}"><span>{h}</span></div>' for i, h, cls, _, _ in GFX)
    tw = []
    for i, _, cls, a, b in GFX:
        if cls == "stamp":
            tw.append(f'tl.fromTo("#{i}", {{ scale: 2.4, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.2, ease: "power4.in" }}, {a});')
            tw.append(f'tl.to("#{i}", {{ opacity: 0, duration: 0.2 }}, {round(b, 3)});')
            continue
        tw.append(f'tl.fromTo("#{i}", {{ clipPath: "{IN_CLIP}" }}, {{ clipPath: "{SHOW}", duration: 0.35, ease: "power3.out" }}, {round(a, 3)});')
        tw.append(f'tl.fromTo("#{i}", {{ clipPath: "{SHOW}" }}, {{ clipPath: "{OUT_CLIP}", duration: 0.25, ease: "power3.in", immediateRender: false }}, {round(b, 3)});')
    tw.append(f'tl.fromTo("#tick span", {{ x: 0 }}, {{ x: -2600, duration: {END}, ease: "none" }}, 0);')
    return (STAGE.replace("__C__", json.dumps(C)).replace("__M__", json.dumps(MOUTH, separators=(",", ":")))
            .replace("__GFX__", gfx).replace("__TW__", "\n".join("    " + x for x in tw)))


STAGE = r'''<template>
  <style>
    #root { position: absolute; inset: 0; overflow: hidden; background: #0E1F3D; font-family: "Archivo Black", sans-serif; }
    #cv { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
    #logo { position: absolute; left: 40px; top: 60px; font-size: 40px; color: #FFFFFF; background: #D7263D; padding: 10px 18px 4px; border-radius: 8px; }
    #logo small { font-family: "Nunito", sans-serif; font-weight: 900; font-size: 22px; display: block; color: #FFE0E4; }
    #live { position: absolute; right: 40px; top: 70px; font-size: 38px; color: #FFFFFF; background: #000000; padding: 8px 18px 2px; border-radius: 8px; }
    #live b { color: #FF3B4E; }
    .g { position: absolute; left: 0; width: 1080px; clip-path: inset(-40px 1200px -40px -40px); }
    .break { top: 220px; text-align: center; } .break span { display: inline-block; font-size: 92px; color: #FFFFFF; background: #D7263D; padding: 16px 40px 8px; border: 8px solid #FFFFFF; }
    .lower { top: 1250px; } .lower span { display: block; margin: 0 40px; background: #FFFFFF; border-left: 22px solid #1E5AA8; padding: 14px 26px 10px; box-shadow: 10px 10px 0 rgba(0,0,0,0.35); }
    .lower.red span { border-left-color: #D7263D; }
    .lower b { display: block; font-weight: normal; font-size: 50px; color: #0E1F3D; line-height: 1.05; }
    .lower i { display: block; font-style: normal; font-family: "Nunito", sans-serif; font-weight: 900; font-size: 32px; color: #D7263D; margin-top: 6px; }
    .stamp { top: 420px; text-align: center; clip-path: none; opacity: 0; } .stamp span { display: inline-block; font-size: 130px; color: #FF3B4E; border: 14px solid #FF3B4E; border-radius: 20px; padding: 10px 34px 0; transform: rotate(-8deg); background: rgba(0,0,0,0.35); }
    #tick { position: absolute; left: 0; top: 1830px; width: 1080px; height: 70px; background: #FFD23F; overflow: hidden; white-space: nowrap; }
    #tick b { position: absolute; left: 0; top: 0; height: 70px; z-index: 2; background: #D7263D; color: #FFFFFF; font-size: 34px; line-height: 74px; padding: 0 20px; }
    #tick span { position: absolute; left: 260px; top: 0; font-size: 34px; line-height: 74px; color: #0E1F3D; }
  </style>
  <div id="root" data-composition-id="stage" data-width="1080" data-height="1920" data-layout-allow-overflow>
    <canvas id="cv" width="1080" height="1920"></canvas>
    <div id="logo">PCN<small>PURO CHISME NOTICIAS</small></div>
    <div id="live"><b>●</b> EN VIVO</div>
__GFX__
    <div id="tick" data-layout-allow-overlap><b>ÚLTIMA HORA</b><span>ÖTZI, EL HOMBRE DE HIELO · HALLADO EN 1991 EN LOS ALPES DE ÖTZTAL · VIVIÓ HACE MÁS DE 5,000 AÑOS · RAYOS X REVELAN UNA FLECHA EN SU HOMBRO · SU MOMIA SE EXHIBE EN BOLZANO, ITALIA · FUENTE: WIKIPEDIA «ÖTZI» · MUSEO ARQUEOLÓGICO DEL TIROL DEL SUR · </span></div>
  </div>
  <script>
    const C = __C__;
    const M = __M__;
    const cv = document.getElementById("cv"), g = cv.getContext("2d");
    const clamp = (k) => Math.min(Math.max(k, 0), 1);
    const smooth = (k) => { k = clamp(k); return k * k * (3 - 2 * k); };
    const lerp = (a, b, k) => a + (b - a) * k;
    const mouth = (spk, t) => (M[spk] || [])[Math.floor(t * 30)] || 0;
    const blink = (t, s) => ((t + s) % 3.2) < 0.11;
    const INK = "#1B1B2F", SKIN = "#F2C9A0";
    const P = () => g.beginPath();
    const fill = (c) => { g.fillStyle = c; g.fill(); };
    const ink = (w) => { g.lineWidth = w || 7; g.strokeStyle = INK; g.lineJoin = "round"; g.lineCap = "round"; g.stroke(); };
    function ell(x, y, rx, ry, c, w, r) { P(); g.ellipse(x, y, Math.abs(rx), Math.abs(ry), r || 0, 0, Math.PI * 2); if (c) fill(c); if (w !== 0) ink(w); }
    function rr(x, y, w, h, r, c, lw) { P(); g.roundRect(x, y, w, h, r); if (c) fill(c); if (lw !== 0) ink(lw); }
    function line(p, w, c) { P(); g.moveTo(p[0], p[1]); for (let i = 2; i < p.length; i += 2) g.lineTo(p[i], p[i + 1]); g.lineWidth = w; g.strokeStyle = c || INK; g.lineCap = "round"; g.lineJoin = "round"; g.stroke(); }
    function limb(x1, y1, x2, y2, w, c) { line([x1, y1, x2, y2], w + 12, INK); line([x1, y1, x2, y2], w, c); }
    function mouthShape(x, y, w, v) {
      if (v < 0.06) { P(); g.moveTo(x - w * 0.5, y); g.quadraticCurveTo(x, y + 9, x + w * 0.5, y); ink(6); return; }
      ell(x, y + 4, w * (0.5 + 0.3 * v), 6 + v * 22, "#7A1F2B", 6); ell(x, y + 12 + v * 9, w * 0.25, 3 + v * 5, "#F28B82", 0);
    }
    function eyes(x, y, t, s, look, wide) { const sh = blink(t, s);
      [[-32, 0], [32, 0]].forEach(([dx]) => { if (sh) { P(); g.moveTo(x + dx - 14, y); g.quadraticCurveTo(x + dx, y + 9, x + dx + 14, y); ink(6); }
        else { ell(x + dx, y, 15 * wide, 18 * wide, "#FFFFFF", 5); ell(x + dx + look * 5, y + 2, 7, 8, INK, 0); } }); }

    // ---- anchor: man behind the desk (upper body) ----
    function anchor(cx, cy, s, t, mood) {
      g.save(); g.translate(cx, cy); g.scale(s, s);
      const m = mouth("anchor", t), b = Math.sin(t * 1.7) * 3;
      rr(-170, -40 + b, 340, 360, 70, "#22314F", 8);
      P(); g.moveTo(-40, -40 + b); g.lineTo(0, 80 + b); g.lineTo(40, -40 + b); g.closePath(); fill("#FFFFFF"); ink(5);
      P(); g.moveTo(-14, -30 + b); g.lineTo(14, -30 + b); g.lineTo(8, 70 + b); g.lineTo(0, 86 + b); g.lineTo(-8, 70 + b); g.closePath(); fill("#D7263D"); ink(4);
      ell(-106, -128 + b, 22, 30, SKIN, 7); ell(106, -128 + b, 22, 30, SKIN, 7);
      ell(0, -130 + b, 104, 116, SKIN, 8);
      P(); g.moveTo(-104, -150 + b); g.quadraticCurveTo(-96, -262 + b, 0, -252 + b); g.quadraticCurveTo(96, -262 + b, 104, -150 + b); g.quadraticCurveTo(70, -214 + b, 0, -208 + b); g.quadraticCurveTo(-70, -214 + b, -104, -150 + b); fill("#9AA0AA"); ink(7);
      ell(-58, -86 + b, 20, 12, "#F28B82", 0); ell(58, -86 + b, 20, 12, "#F28B82", 0);
      eyes(0, -140 + b, t, 0.3, 0, mood === "wow" ? 1.25 : 1);
      line([-52, -178 + b - (mood === "wow" ? 10 : 0), -14, -172 + b], 9); line([14, -172 + b, 52, -178 + b - (mood === "wow" ? 10 : 0)], 9);
      ell(0, -110 + b, 14, 11, "#E2A27C", 5);
      mouthShape(0, -64 + b, 52, m);
      g.restore();
    }
    function studio(t, zoom, dim) {
      g.save(); g.translate(540, 900); g.scale(zoom, zoom); g.translate(-540, -900);
      const gr = g.createLinearGradient(0, 0, 0, 1920); gr.addColorStop(0, "#123A73"); gr.addColorStop(1, "#0A1A35"); g.fillStyle = gr; g.fillRect(-400, -400, 1880, 2720);
      for (let k = 0; k < 9; k++) line([-200 + k * 180, 300, -200 + k * 180, 1150], 3, "rgba(255,255,255,0.08)");
      for (let k = 0; k < 6; k++) line([-200, 320 + k * 150, 1300, 320 + k * 150], 3, "rgba(255,255,255,0.08)");
      ell(540, 560, 330, 330, null, 0); P(); g.arc(540, 560, 300, 0, Math.PI * 2); g.lineWidth = 6; g.strokeStyle = "rgba(120,190,255,0.35)"; g.stroke();
      line([240, 560, 840, 560], 4, "rgba(120,190,255,0.35)"); line([540, 260, 540, 860], 4, "rgba(120,190,255,0.35)");
      anchor(540, 980, 1.25, t, t >= C.l4 && t < C.l5 ? "wow" : "");
      rr(80, 1110, 920, 240, 26, "#1E2E5C", 8); g.font = "900 70px 'Arial Black', Arial"; g.fillStyle = "#FFD23F"; g.textAlign = "center"; g.fillText("ÚLTIMA HORA", 540, 1270); rr(80, 1110, 920, 50, 20, "#1E5AA8", 0); g.font = "900 40px 'Arial Black', Arial"; g.fillStyle = "#FFFFFF"; g.textAlign = "center"; g.fillText("PCN NOTICIAS", 540, 1150);
      if (dim) { g.fillStyle = "rgba(0,0,0," + dim + ")"; g.fillRect(-400, -400, 1880, 2720); }
      g.restore();
    }
    // ---- field: snowy Alps, reporter with mic, iceman in the ice ----
    function reporter(cx, cy, s, t) {
      g.save(); g.translate(cx, cy); g.scale(s, s);
      const m = mouth("reporter", t), b = Math.sin(t * 2.1) * 3;
      rr(-150, -30 + b, 300, 380, 90, "#D7263D", 8); line([0, -20 + b, 0, 340], 5, "#9E1B2C");
      P(); g.arc(0, -120 + b, 140, Math.PI * 0.85, Math.PI * 2.15); g.lineWidth = 40; g.strokeStyle = "#F5F1E8"; g.stroke();
      ell(0, -120 + b, 100, 110, SKIN, 8);
      P(); g.moveTo(-100, -150 + b); g.quadraticCurveTo(0, -300 + b, 100, -150 + b); g.closePath(); fill("#2B4C9B"); ink(7); ell(0, -262 + b, 26, 26, "#FFFFFF", 6);
      P(); g.moveTo(-96, -140 + b); g.quadraticCurveTo(-120, -40 + b, -80, 0 + b); ink(0); g.fillStyle = "#6B3A1A";
      ell(-60, -76 + b, 20, 12, "#F28B82", 0); ell(60, -76 + b, 20, 12, "#F28B82", 0);
      eyes(0, -130 + b, t, 1.1, 0.5, 1); ell(0, -100 + b, 12, 10, "#E2A27C", 5);
      mouthShape(0, -56 + b, 50, m);
      limb(110, 60 + b, 170, -30 + b, 34, "#D7263D"); rr(150, -110 + b, 44, 110, 12, INK, 0); ell(172, -120 + b, 34, 34, "#3A3A4A", 6);
      rr(140, -80 + b, 64, 40, 6, "#D7263D", 0); g.font = "900 22px 'Arial Black', Arial"; g.fillStyle = "#FFFFFF"; g.textAlign = "center"; g.fillText("PCN", 172, -52 + b);
      g.restore();
    }
    function iceman(x, y, s, t) {
      g.save(); g.translate(x, y); g.scale(s, s);
      ell(0, 0, 260, 70, "rgba(170,220,245,0.85)", 6);
      P(); g.moveTo(-200, -10); g.quadraticCurveTo(-120, -60, 0, -50); g.quadraticCurveTo(140, -50, 200, -20); g.quadraticCurveTo(120, 20, -200, 20); g.closePath(); fill("#8A5A3A"); ink(6);
      ell(-210, -18, 44, 36, "#8A5A3A", 6); line([-226, -26, -214, -20], 5); line([-196, -26, -184, -20], 5); line([-216, -4, -196, -4], 5);
      g.restore();
    }
    function snow(t, x0, w) { for (let i = 0; i < 70; i++) { const sx = x0 + ((i * 137.5) % w), sy = ((i * 211 + t * (60 + (i % 5) * 18)) % 1900); ell(sx + Math.sin(t + i) * 12, sy, 5, 5, "rgba(255,255,255,0.85)", 0); } }
    function field(t, opt) {
      g.fillStyle = "#9FD3F0"; g.fillRect(0, 0, 1080, 1920);
      P(); g.moveTo(-50, 900); g.lineTo(180, 420); g.lineTo(380, 800); g.lineTo(600, 330); g.lineTo(860, 760); g.lineTo(1130, 470); g.lineTo(1130, 1920); g.lineTo(-50, 1920); g.closePath(); fill("#7A8DA6"); ink(8);
      P(); g.moveTo(140, 500); g.lineTo(180, 420); g.lineTo(225, 500); g.lineTo(200, 480); g.lineTo(170, 510); g.closePath(); fill("#FFFFFF");
      P(); g.moveTo(545, 440); g.lineTo(600, 330); g.lineTo(660, 440); g.lineTo(620, 420); g.lineTo(580, 450); g.closePath(); fill("#FFFFFF");
      P(); g.moveTo(-50, 1000); g.quadraticCurveTo(540, 880, 1130, 990); g.lineTo(1130, 1920); g.lineTo(-50, 1920); g.closePath(); fill("#F4F8FB"); ink(8);
      if (opt.ice) iceman(360, 1120, 0.85, t);
      if (opt.tourists) { [[150, 1070, "#2BB673"], [600, 1080, "#FFD23F"]].forEach(([x, y, c], k) => { rr(x - 22, y - 120, 44, 90, 20, c, 6); ell(x, y - 140, 24, 24, SKIN, 6); line([x + 20, y - 100, x + 70, y - 60 - k * 10], 10); line([x - 10, y - 30, x - 12, y], 10); line([x + 10, y - 30, x + 12, y], 10); }); }
      if (opt.drill) { const sh = t > C.taladro && t < C.taladro + 0.5 ? Math.sin(t * 90) * 6 : 0; g.save(); g.translate(560 + sh, 1050); rr(-30, -170, 60, 130, 10, "#FFD23F", 6); line([0, -40, 0, 30], 12, "#5A5F6B"); line([-60, -150, 60, -150], 14, INK); g.restore(); }
      if (opt.dating) { const k = smooth((t - C.cinco5) / 0.8); g.save(); g.translate(540, 560); g.scale(k, k); rr(-300, -110, 600, 220, 30, "rgba(14,31,61,0.92)", 8); g.font = "900 120px 'Arial Black', Arial"; g.fillStyle = "#FFD23F"; g.textAlign = "center"; g.fillText("+5,000", 0, 30); g.font = "900 44px 'Arial Black', Arial"; g.fillStyle = "#FFFFFF"; g.fillText("AÑOS", 0, 90); g.restore(); }
      reporter(opt.rx || 800, 1250, 0.95, t);
      snow(t, 0, 1080);
    }
    // ---- X-ray (CSI) ----
    function xray(t) {
      g.fillStyle = "#04121F"; g.fillRect(0, 0, 1080, 1920);
      for (let k = 0; k < 20; k++) line([0, 200 + k * 80, 1080, 200 + k * 80], 2, "rgba(80,200,255,0.12)");
      const glow = "rgba(150,230,255,0.9)";
      g.save(); g.translate(540, 900);
      ell(0, -360, 110, 130, null, 0); P(); g.ellipse(0, -360, 110, 130, 0, 0, Math.PI * 2); g.lineWidth = 10; g.strokeStyle = glow; g.stroke();
      line([0, -230, 0, 300], 18, glow);
      for (let k = 0; k < 7; k++) { P(); g.ellipse(0, -130 + k * 52, 190 - k * 8, 34, 0, Math.PI * 0.05, Math.PI * 0.95); g.lineWidth = 10; g.strokeStyle = glow; g.stroke(); P(); g.ellipse(0, -130 + k * 52, 190 - k * 8, 34, 0, Math.PI * 1.05, Math.PI * 1.95); g.stroke(); }
      line([-40, -190, -260, -170, -310, 150], 16, glow); line([40, -190, 260, -170, 310, 150], 16, glow);
      ell(-250, -180, 40, 40, null, 0); P(); g.arc(-250, -180, 44, 0, Math.PI * 2); g.lineWidth = 8; g.stroke();
      const hit = smooth((t - C.flecha) / 0.4);
      if (hit > 0) { g.save(); g.translate(-210, -140); g.rotate(-0.7); g.globalAlpha = hit; P(); g.moveTo(0, -40); g.lineTo(24, 20); g.lineTo(-24, 20); g.closePath(); fill("#FF3B4E");
        P(); g.arc(0, 0, 70 + Math.sin(t * 6) * 6, 0, Math.PI * 2); g.lineWidth = 8; g.strokeStyle = "#FF3B4E"; g.stroke(); g.restore(); g.globalAlpha = 1; }
      g.restore();
      const sy = 200 + ((t - C.l7) / 1.6 % 1) * 1300; if (t < C.flecha + 0.5) { line([0, sy, 1080, sy], 8, "rgba(120,255,200,0.8)"); }
      g.font = "900 40px 'Arial Black', Arial"; g.fillStyle = "#7CFFC8"; g.textAlign = "left"; g.fillText("ESCÁNER · ÖTZI · 2001", 60, 300);
    }
    function caseBoard(t) {
      studio(t, 1.0, 0);
      const k = smooth((t - C.quien) / 0.5);
      if (k > 0) { g.save(); g.translate(540, 520); g.scale(k, k); rr(-330, -150, 660, 300, 24, "#FFFFFF", 8); g.font = "900 64px 'Arial Black', Arial"; g.fillStyle = "#D7263D"; g.textAlign = "center";
        g.fillText("¿QUIÉN LO MATÓ?", 0, -30); g.font = "900 44px 'Arial Black', Arial"; g.fillStyle = INK; g.fillText(t >= C.nadie ? "SOSPECHOSO: ???" : "INVESTIGANDO…", 0, 70); g.restore(); }
    }

    function draw(t) {
      g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, 1080, 1920);
      if (t < C.reportera) return studio(t, lerp(1.0, 1.08, smooth(t / 5)), 0);
      if (t < C.l2 - 0.05) {  // split screen: anchor left, reporter right (TV link)
        const k = smooth((t - C.reportera) / 0.4);
        g.save(); P(); g.rect(0, 0, 1080 - 540 * k, 1920); g.clip(); studio(t, 1, 0); g.restore();
        g.save(); P(); g.rect(1080 - 540 * k, 0, 540 * k, 1920); g.clip(); g.translate(1080 - 540 * k - 270, 0); field(t, { ice: false, rx: 540 }); g.restore();
        line([1080 - 540 * k, 0, 1080 - 540 * k, 1920], 10, "#FFFFFF"); return;
      }
      if (t < C.l4) return field(t, { ice: true, tourists: t >= C.turistas && t < C.l3, drill: t >= C.l3 });
      if (t < C.l5) return studio(t, 1.15, 0);
      if (t < C.l6) return field(t, { ice: true, dating: true });
      if (t < C.l7) return studio(t, lerp(1.1, 1.35, smooth((t - C.l6) / 1.6)), 0.35);
      if (t < C.l8) return xray(t);
      caseBoard(t);
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
    sfx = [("breaking", "el_breaking", 0.05, 1.5, 0.4), ("w1", "el_whoosh", C["reportera"], 0.6, 0.35), ("wind", "el_wind", C["l2"], 2.0, 0.3),
           ("ticker", "el_ticker", C["l2"] + 0.2, 1.0, 0.3), ("drill", "el_drill", C["taladro"], 1.2, 0.45), ("w2", "el_whoosh", C["l4"], 0.6, 0.3),
           ("hit", "el_hit", C["cinco5"], 1.2, 0.4), ("w3", "el_whoosh", C["l6"], 0.6, 0.3), ("scan", "el_scan", C["l7"] + 0.1, 1.5, 0.4),
           ("hit2", "el_hit", C["asesinaron"], 1.2, 0.45), ("w4", "el_whoosh", C["l8"], 0.6, 0.3), ("hit3", "el_hit", C["quien"], 1.2, 0.35),
           ("outro", "el_outro", C["seguiremos"], 1.5, 0.35),
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
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #0E1F3D; }}
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
