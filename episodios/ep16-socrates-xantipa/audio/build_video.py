"""EP16: escribe compositions/stage.html (Sócrates y Xantipa como TELENOVELA en PAPEL RECORTADO) e index.html.

  python -I audio/build_video.py     (después de gen_audio_el.py y build.py)

Canvas 1080×1920 por cuadro. Todo es "cartulina recortada": cada figura lleva borde blanco de papel y sombra desplazada; los
bordes tienen un dentado fijo (sembrado por posición, no tiembla). Títeres con articulaciones (brazos que giran), bocas desde
mouth.json, zooms de golpe de telenovela en los momentos dramáticos, la cubeta, el manto arrancado, el caballo bravo que se
transforma en Xantipa, la noche antes de la ejecución y el cierre "¿VILLANA?". Rótulos HTML con máscara.
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
C = {"esposa": W("l0", "esposa"), "cubeta": W("l0", "cubeta"),
     "l1": L("l1"), "atenas": W("l1", "atenas"), "preguntas": W("l1", "preguntas"), "cobrar": W("l1", "cobrar"),
     "l2": L("l2"), "hijos": W("l2", "hijos"), "calle": W("l2", "calle"),
     "l3": L("l3"), "rego": W("l3", "regan"), "agua": W("l3", "agua"), "tranquilito": W("l3", "tranquilito"),
     "l4": L("l4"), "truenos": W("l4", "truenos"), "lluvia": W("l4", "lluvia"),
     "l5": L("l5"), "arranco": W("l5", "arranco"), "plaza": W("l5", "plaza"), "caso": W("l5", "caso"),
     "l6": L("l6"), "caballo": W("l6", "caballo"), "aguanto": W("l6", "aguanto"),
     "l7": L("l7"), "amigos": W("l7", "amigos"), "platon": W("l7", "platon"), "noche": W("l7", "noche"),
     "l8": L("l8"), "villana": W("l8", "villana"), "marido": W("l8", "marido"), "end": END}
BANNERS = [
    ("b1", "ATENAS, SIGLO V a. C.", C["atenas"], C["preguntas"]),
    ("b2", "COBRABA: $0", C["cobrar"], C["l2"] - 0.1),
    ("b3", "«¡LOS TRUENOS… Y LUEGO LA LLUVIA!»", C["truenos"], C["l5"] - 0.1),
    ("b4", "CAPÍTULO 2: EL MANTO", C["l5"] + 0.1, C["caso"] - 0.05),
    ("b5", "FUENTE: DIÓGENES LAERCIO II · JENOFONTE", C["l6"], C["l7"] - 0.1),
    ("b6", "PLATÓN (FEDÓN): ELLA ESTABA A SU LADO", C["platon"], C["l8"] - 0.1),
    ("b7", "¿VILLANA… O VÍCTIMA?", C["villana"], C["end"] - 0.1),
]
IN_CLIP, SHOW, OUT_CLIP = "inset(-30px 1200px -30px -30px)", "inset(-30px -30px -30px -30px)", "inset(-30px -30px -30px 1200px)"


def stage_html():
    ban = "\n".join(f'    <div id="{i}" class="ban"><span>{t}</span></div>' for i, t, _, _ in BANNERS)
    tw = ['tl.fromTo("#t1", { clipPath: "' + IN_CLIP + '" }, { clipPath: "' + SHOW + '", duration: 0.35, ease: "power3.out" }, 0.03);',
          'tl.fromTo("#t2", { clipPath: "' + IN_CLIP + '" }, { clipPath: "' + SHOW + '", duration: 0.35, ease: "power3.out" }, 0.2);',
          f'tl.to("#title", {{ clipPath: "{OUT_CLIP}", duration: 0.3, ease: "power3.in" }}, {round(C["l1"] - 0.1, 3)});',
          f'tl.fromTo("#cont", {{ clipPath: "{IN_CLIP}" }}, {{ clipPath: "{SHOW}", duration: 0.35, ease: "power3.out" }}, {C["marido"]});']
    for i, _, a, b in BANNERS:
        tw += [f'tl.fromTo("#{i}", {{ clipPath: "{IN_CLIP}" }}, {{ clipPath: "{SHOW}", duration: 0.32, ease: "power3.out" }}, {round(a, 3)});',
               f'tl.fromTo("#{i}", {{ clipPath: "{SHOW}" }}, {{ clipPath: "{OUT_CLIP}", duration: 0.22, ease: "power3.in", immediateRender: false }}, {round(b, 3)});']
    return (STAGE.replace("__C__", json.dumps(C)).replace("__M__", json.dumps(MOUTH, separators=(",", ":")))
            .replace("__BAN__", ban).replace("__TW__", "\n".join("    " + x for x in tw)))


STAGE = r'''<template>
  <style>
    #root { position: absolute; inset: 0; overflow: hidden; background: #6B1E3A; font-family: "Archivo Black", sans-serif; }
    #cv { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
    .ban { position: absolute; left: 0; top: 250px; width: 1080px; text-align: center; clip-path: inset(-30px 1200px -30px -30px); }
    .ban span { display: inline-block; max-width: 1000px; font-size: 48px; line-height: 1.1; padding: 16px 30px 10px; background: #FFF4E0; color: #6B1E3A;
      border: 6px dashed #6B1E3A; box-shadow: 10px 12px 0 rgba(0,0,0,0.3); rotate: -2deg; }
    #b2 span, #b7 span { background: #FFD23F; } #b5 span { font-family: "Nunito", sans-serif; font-weight: 900; font-size: 34px; }
    #title { position: absolute; left: 0; top: 230px; width: 1080px; text-align: center; }
    .tt { clip-path: inset(-30px 1200px -30px -30px); margin-bottom: 18px; }
    .tt span { display: inline-block; font-size: 64px; line-height: 1; padding: 18px 34px 10px; color: #FFF4E0; background: #B0123F; border: 8px solid #FFF4E0; box-shadow: 10px 12px 0 rgba(0,0,0,0.35); }
    #t2 span { font-size: 92px; background: #FFF4E0; color: #B0123F; border-color: #B0123F; rotate: 2deg; }
    #cont { position: absolute; left: 0; top: 1300px; width: 1080px; text-align: center; clip-path: inset(-30px 1200px -30px -30px); }
    #cont span { display: inline-block; font-size: 58px; color: #FFF4E0; background: #1B1B2F; padding: 12px 30px 6px; rotate: -3deg; }
  </style>
  <div id="root" data-composition-id="stage" data-width="1080" data-height="1920" data-layout-allow-overflow>
    <canvas id="cv" width="1080" height="1920"></canvas>
__BAN__
    <div id="title"><div id="t1" class="tt"><span>LA ESPOSA DEL FILÓSOFO</span></div><div id="t2" class="tt"><span>¡XANTIPA!</span></div></div>
    <div id="cont"><span>CONTINUARÁ…</span></div>
  </div>
  <script>
    const C = __C__;
    const M = __M__;
    const cv = document.getElementById("cv"), g = cv.getContext("2d");
    const clamp = (k) => Math.min(Math.max(k, 0), 1);
    const smooth = (k) => { k = clamp(k); return k * k * (3 - 2 * k); };
    const back = (k) => { k = clamp(k); const s = 1.8; return 1 + (s + 1) * Math.pow(k - 1, 3) + s * Math.pow(k - 1, 2); };
    const lerp = (a, b, k) => a + (b - a) * k;
    const mouth = (spk, t) => (M[spk] || [])[Math.floor(t * 30)] || 0;
    const rnd = (i) => { const x = Math.sin(i * 91.7 + 13.1) * 43758.5; return x - Math.floor(x); };
    const INK = "#2B1B24";

    // paper cut-out: shadow, white paper rim, colour; jagged edges are fixed (seeded), never animated
    function paper(build, color, rim) {
      g.save(); g.translate(9, 12); build(); g.fillStyle = "rgba(30,10,20,0.28)"; g.fill(); g.restore();
      build(); g.lineJoin = "round"; g.lineWidth = rim === undefined ? 14 : rim; g.strokeStyle = "#FFF8EC"; g.stroke(); g.fillStyle = color; g.fill();
    }
    const blob = (cx, cy, rx, ry, seed, n) => () => { g.beginPath(); n = n || 28;
      for (let i = 0; i <= n; i++) { const a = i / n * Math.PI * 2, j = 1 + (rnd(seed + i) - 0.5) * 0.05; const x = cx + Math.cos(a) * rx * j, y = cy + Math.sin(a) * ry * j; i ? g.lineTo(x, y) : g.moveTo(x, y); } g.closePath(); };
    const poly = (pts) => () => { g.beginPath(); pts.forEach(([x, y], i) => (i ? g.lineTo(x, y) : g.moveTo(x, y))); g.closePath(); };
    function txt(s, x, y, size, c) { g.font = "900 " + size + "px 'Arial Black', Arial"; g.textAlign = "center"; g.fillStyle = c; g.fillText(s, x, y); }
    function mouthAt(x, y, w, v) { if (v < 0.06) { g.beginPath(); g.moveTo(x - w / 2, y); g.quadraticCurveTo(x, y + 8, x + w / 2, y); g.lineWidth = 6; g.strokeStyle = INK; g.stroke(); return; }
      blob(x, y + 4, w * (0.45 + 0.3 * v), 6 + v * 20, 7, 14)(); g.fillStyle = "#5A0F22"; g.fill(); }
    function arm(sx, sy, ang, len, col, s) { const hx = sx + Math.sin(ang) * len, hy = sy + Math.cos(ang) * len;
      paper(() => { g.beginPath(); g.moveTo(sx, sy); g.lineTo(hx, hy); g.lineWidth = 34; }, col, 0);
      g.beginPath(); g.moveTo(sx, sy); g.lineTo(hx, hy); g.lineCap = "round"; g.lineWidth = 46; g.strokeStyle = "#FFF8EC"; g.stroke(); g.lineWidth = 32; g.strokeStyle = col; g.stroke();
      paper(blob(hx, hy, 20, 20, s, 10), "#E8B48F", 8); return [hx, hy]; }

    // ---- puppets (feet at x,y) ----
    function socrates(x, y, s, t, o) {
      o = o || {}; g.save(); g.translate(x, y); g.scale(s * (o.f || 1), s);
      const m = mouth("socrates", t), b = Math.sin(t * 1.6) * 3, wet = o.wet || 0;
      paper(poly([[-110, 0], [-95, -300 + b], [95, -300 + b], [110, 0]]), o.cloak === false ? "#E9DCC0" : "#7E8C4F");
      if (o.cloak !== false) paper(poly([[-95, -300 + b], [60, -300 + b], [-60, -40], [-110, -40]]), "#E9DCC0", 8);
      const hand = arm(80, -270 + b, o.arm || 0.4, 150, "#E9DCC0", 3);
      paper(blob(0, -400 + b, 98, 104, 11), "#E8B48F");
      paper(blob(0, -320 + b, 92, 70, 21), wet ? "#BFD8E6" : "#F2F0EA", 10);
      paper(blob(4, -386 + b, 34, 26, 31, 12), "#D9946E", 6);
      [-36, 36].forEach((dx) => { if (o.closed || ((t + 0.7) % 3.4) < 0.12) { g.beginPath(); g.moveTo(dx - 14, -420 + b); g.lineTo(dx + 14, -420 + b); g.lineWidth = 7; g.strokeStyle = INK; g.stroke(); }
        else { paper(blob(dx, -420 + b, 15, 17, 41 + dx, 10), "#FFFFFF", 4); g.beginPath(); g.arc(dx + 3, -418 + b, 7, 0, 7); g.fillStyle = INK; g.fill(); } });
      mouthAt(2, -344 + b, 40, m);
      if (wet) for (let k = 0; k < 6; k++) paper(blob(-80 + k * 32, -470 + b + ((t * 120 + k * 40) % 160), 9, 14, 51 + k, 8), "#7EC8F0", 4);
      g.restore(); return hand;
    }
    function xantipa(x, y, s, t, o) {
      o = o || {}; g.save(); g.translate(x, y); g.scale(s * (o.f || 1), s);
      const m = mouth("xantipa", t), b = Math.sin(t * 2.2) * 3, angry = o.angry === undefined ? 1 : o.angry;
      paper(poly([[-120, 0], [-90, -310 + b], [90, -310 + b], [120, 0]]), "#C2185B");
      paper(poly([[-90, -310 + b], [90, -310 + b], [70, -250 + b], [-70, -250 + b]]), "#FFD23F", 8);
      arm(-80, -280 + b, o.armL === undefined ? -0.5 : o.armL, 150, "#C2185B", 5); const hand = arm(80, -280 + b, o.arm === undefined ? 0.5 : o.arm, 150, "#C2185B", 6);
      paper(blob(0, -520 + b, 70, 60, 61), "#2B1B24", 10);
      paper(blob(0, -410 + b, 92, 100, 71), "#E8B48F");
      paper(blob(-96, -400 + b, 40, 90, 81, 14), "#2B1B24", 8); paper(blob(96, -400 + b, 40, 90, 91, 14), "#2B1B24", 8);
      paper(blob(-88, -360 + b, 10, 10, 95, 8), "#FFD23F", 4); paper(blob(88, -360 + b, 10, 10, 96, 8), "#FFD23F", 4);
      [-34, 34].forEach((dx, k) => { if (((t + 1.3) % 3.0) < 0.11 || o.tear) { g.beginPath(); g.moveTo(dx - 14, -420 + b); g.quadraticCurveTo(dx, -410 + b, dx + 14, -420 + b); g.lineWidth = 7; g.strokeStyle = INK; g.stroke(); }
        else { paper(blob(dx, -420 + b, 16, 18, 101 + k, 10), "#FFFFFF", 4); g.beginPath(); g.arc(dx, -416 + b, 8, 0, 7); g.fillStyle = INK; g.fill(); }
        const d = angry * 12 * (k ? -1 : 1); g.beginPath(); g.moveTo(dx - 20, -452 + b - d); g.lineTo(dx + 20, -452 + b + d); g.lineWidth = 10; g.strokeStyle = INK; g.stroke(); });
      paper(blob(-50, -380 + b, 18, 10, 111, 8), "#F28B82", 0); paper(blob(50, -380 + b, 18, 10, 112, 8), "#F28B82", 0);
      mouthAt(0, -352 + b, 44, m);
      if (o.tear) paper(blob(-30, -380 + b + ((t * 40) % 60), 9, 14, 121, 8), "#7EC8F0", 4);
      g.restore(); return hand;
    }
    function crowd(t, gasp) { for (let k = 0; k < 9; k++) { const x = 60 + k * 120, y = 1380 + (k % 2) * 40, j = gasp ? Math.abs(Math.sin(t * 9 + k)) * 18 : 0;
      paper(blob(x, y - j, 52, 58, 200 + k), ["#E8B48F", "#D9946E", "#C98A62"][k % 3]); paper(poly([[x - 60, y + 40 - j], [x + 60, y + 40 - j], [x + 70, y + 160], [x - 70, y + 160]]), ["#7E8C4F", "#4F6D8C", "#B06A3B"][k % 3], 8);
      if (gasp) { g.beginPath(); g.ellipse(x, y + 18 - j, 10, 14, 0, 0, 7); g.fillStyle = INK; g.fill(); } } }
    function columns(col) { for (let k = 0; k < 4; k++) { const x = 90 + k * 300; paper(poly([[x - 50, 1200], [x - 40, 420], [x + 40, 420], [x + 50, 1200]]), col || "#F3E9D2", 10); paper(poly([[x - 70, 420], [x + 70, 420], [x + 60, 380], [x - 60, 380]]), "#E2D4B5", 8); } }
    function bg(c1, c2) { const gr = g.createLinearGradient(0, 0, 0, 1920); gr.addColorStop(0, c1); gr.addColorStop(1, c2); g.fillStyle = gr; g.fillRect(-300, -300, 1680, 2520);
      for (let k = 0; k < 40; k++) { g.fillStyle = "rgba(255,255,255,0.04)"; g.fillRect(rnd(k) * 1080, rnd(k + 50) * 1920, 6, 6); } }
    function ground(c) { paper(poly([[-40, 1180], [1120, 1150], [1120, 2000], [-40, 2000]]), c, 10); }
    function zoomAt(cx, cy, z, fn) { g.save(); g.translate(cx, cy); g.scale(z, z); g.translate(-cx, -cy); fn(); g.restore(); }
    const punch = (t, t0) => 1 + 0.25 * (1 - smooth((t - t0) / 0.5)) * (t >= t0 ? 1 : 0);  // telenovela snap zoom: jump in, ease back

    function sceneTitle(t) {
      bg("#8E1238", "#3D0A1E");
      for (let k = 0; k < 8; k++) paper(blob(80 + k * 135, 1780 + (k % 2) * 30, 60, 50, 300 + k), "#D81B60", 10);
      const z = punch(t, C.esposa);
      zoomAt(540, 1100, z, () => {
        socrates(330, 1400, 1.0, t, {}); xantipa(760, 1400, 1.0, t, { f: -1, arm: 1.2 });
        if (t >= C.cubeta) { const k = back((t - C.cubeta) / 0.4); g.save(); g.translate(700, 760); g.scale(k, k); paper(poly([[-80, -60], [80, -60], [60, 70], [-60, 70]]), "#9AA4AE"); paper(blob(0, -60, 80, 18, 401), "#4FA3D9", 6); g.restore(); }
      });
    }
    function sceneAgora(t) {
      bg("#F6C177", "#E07A5F"); paper(blob(840, 340, 110, 110, 501), "#FFE08A", 10); columns(); ground("#C9A26B");
      socrates(540, 1300, 1.05, t, { arm: t > C.preguntas ? 2.4 : 0.5 });
      const q = ["?", "¿?", "?!"]; for (let k = 0; k < 3; k++) { const kk = back((t - C.preguntas - k * 0.2) / 0.35); if (kk > 0) { g.save(); g.translate(260 + k * 280, 640 - (k % 2) * 80); g.scale(kk, kk); paper(blob(0, 0, 80, 70, 520 + k), "#FFFFFF", 8); txt(q[k], 0, 26, 70, "#B0123F"); g.restore(); } }
      if (t >= C.cobrar) { const kk = back((t - C.cobrar) / 0.4); g.save(); g.translate(820, 980); g.scale(kk, kk); paper(blob(0, 0, 80, 80, 530), "#FFD23F", 10); txt("$", 0, 28, 80, "#8E6A10"); g.beginPath(); g.moveTo(-70, -70); g.lineTo(70, 70); g.lineWidth = 16; g.strokeStyle = "#B0123F"; g.stroke(); g.restore(); }
      crowd(t, false);
    }
    function sceneHome(t) {  // Xantipa scolds at the door, kids peek
      bg("#F4A261", "#B5523B"); paper(poly([[120, 1180], [120, 520], [960, 520], [960, 1180]]), "#E9C46A", 10); paper(poly([[80, 540], [540, 330], [1000, 540]]), "#A44A3F", 10);
      paper(poly([[700, 1180], [700, 760], [900, 760], [900, 1180]]), "#6D4C3D", 10); ground("#9C6644");
      const z = punch(t, C.l2);
      zoomAt(420, 1000, z, () => xantipa(420, 1350, 1.1, t, { arm: 2.7, armL: -2.6 }));
      if (t >= C.hijos) for (let k = 0; k < 2; k++) { const kk = back((t - C.hijos - k * 0.15) / 0.35); g.save(); g.translate(760 + k * 110, 1260); g.scale(kk * 0.45, kk * 0.45);
        paper(blob(0, -420, 90, 96, 600 + k), "#E8B48F"); paper(poly([[-90, -330], [90, -330], [100, 0], [-100, 0]]), ["#4F6D8C", "#7E8C4F"][k]); g.beginPath(); g.arc(-30, -430, 10, 0, 7); g.arc(30, -430, 10, 0, 7); g.fillStyle = INK; g.fill(); g.restore(); }
    }
    function sceneSplash(t) {  // the bucket, thunder, the calm reply
      const storm = t >= C.rego;
      bg(storm ? "#5C6B8A" : "#F6C177", storm ? "#2E3A55" : "#E07A5F"); columns("#D9D2C0"); ground("#8C7A5B");
      if (storm && t < C.l5) { const fl = ((t - C.rego) % 1.3) < 0.08; if (fl) { g.fillStyle = "rgba(255,255,255,0.5)"; g.fillRect(0, 0, 1080, 1920); }
        paper(poly([[600, 300], [520, 520], [600, 520], [500, 760], [680, 470], [600, 470], [680, 300]]), "#FFE066", 8); }
      const throwK = smooth((t - C.agua) / 0.4), wet = t >= C.agua + 0.3 ? 1 : 0;
      xantipa(800, 1350, 1.0, t, { f: -1, arm: lerp(0.4, 2.2, throwK), angry: 1 });
      if (t >= C.agua - 0.3 && t < C.agua + 0.6) { g.save(); g.translate(lerp(700, 520, throwK), lerp(820, 700, throwK)); g.rotate(-throwK * 1.6); paper(poly([[-70, -50], [70, -50], [55, 60], [-55, 60]]), "#9AA4AE"); g.restore(); }
      if (t >= C.agua && t < C.agua + 0.9) for (let k = 0; k < 14; k++) { const u = (t - C.agua) / 0.9; paper(blob(520 - 200 * u + k * 22 - 140, 700 + u * 500 + (k % 4) * 30, 18, 26, 700 + k, 8), "#4FA3D9", 5); }
      const z = t >= C.l4 ? punch(t, C.l4) : 1;
      zoomAt(330, 1000, z, () => socrates(330, 1350, 1.0, t, { wet, closed: t >= C.tranquilito && t < C.l4 }));
      if (t >= C.lluvia) for (let k = 0; k < 30; k++) paper(blob((k * 97) % 1080, ((t - C.lluvia) * 900 + k * 173) % 1300 + 300, 6, 18, 800 + k, 6), "#7EC8F0", 3);
    }
    function sceneCloak(t) {
      bg("#F6C177", "#E07A5F"); columns(); ground("#C9A26B");
      const yank = smooth((t - C.arranco - 0.2) / 0.5);
      socrates(380, 1300, 1.0, t, { cloak: t < C.arranco + 0.2 });
      xantipa(760, 1300, 1.0, t, { f: -1, arm: lerp(0.6, 2.4, yank) });
      if (t >= C.arranco + 0.2) { g.save(); g.translate(lerp(380, 760, yank), lerp(1060, 620, yank)); g.rotate(yank * 2.5); paper(poly([[-100, -120], [100, -110], [60, 120], [-90, 110]]), "#7E8C4F"); g.restore(); }
      crowd(t, t >= C.plaza);
    }
    function sceneHorse(t) {  // the spirited horse… becomes Xantipa (morph)
      bg("#BFE3C0", "#6FA36B"); ground("#7FB069");
      socrates(250, 1350, 0.9, t, { arm: 1.6 });
      const mk = smooth((t - C.aguanto) / 0.6);
      g.save(); g.translate(720, 1350); const rear = Math.sin(clamp((t - C.caballo) / 0.6) * Math.PI) * 0.35;
      g.globalAlpha = 1 - mk; g.rotate(-rear); g.scale(1 - mk * 0.5, 1 - mk * 0.5);
      paper(poly([[-200, -380], [-300, -300], [-280, -180], [-210, -300]]), "#2B1B24", 8);
      paper(blob(0, -330, 210, 120, 900), "#8B5A3C"); paper(poly([[110, -400], [170, -540], [280, -520], [230, -330]]), "#8B5A3C");
      paper(poly([[150, -560], [300, -600], [330, -500], [250, -470]]), "#8B5A3C"); paper(poly([[110, -420], [150, -560], [190, -560], [140, -400]]), "#2B1B24", 8);
      paper(poly([[180, -580], [190, -630], [210, -585]]), "#8B5A3C", 6); [-150, -60, 60, 150].forEach((lx, k) => paper(poly([[lx - 20, -240], [lx + 20, -240], [lx + 18 + (k < 2 ? -30 * rear : 0), 0], [lx - 18, 0]]), "#7A4A2A", 8));
      g.beginPath(); g.arc(255, -560, 9, 0, 7); g.fillStyle = INK; g.fill(); g.restore(); g.globalAlpha = 1;
      if (mk > 0) { g.save(); g.globalAlpha = mk; xantipa(720, 1350, lerp(0.5, 1.0, mk), t, { f: -1, arm: 2.4, armL: -2.4 }); g.restore(); g.globalAlpha = 1; }
    }
    function sceneNight(t) {
      bg("#1F2A4A", "#0B1022"); for (let k = 0; k < 25; k++) paper(blob(rnd(k + 900) * 1080, rnd(k + 950) * 700, 5, 5, 960 + k, 6), "#FFF4C2", 2);
      paper(blob(860, 360, 90, 90, 990), "#FFF4C2", 10);
      ground("#2E2A3A"); for (let k = 0; k < 7; k++) paper(poly([[80 + k * 150, 400], [100 + k * 150, 400], [100 + k * 150, 1200], [80 + k * 150, 1200]]), "#4A4A5E", 6);
      socrates(380, 1350, 0.95, t, { closed: true }); xantipa(720, 1350, 0.95, t, { f: -1, angry: -0.6, tear: true, arm: 1.2 });
      paper(blob(560, 1260, 24, 40, 995), "#FFD23F", 6);
    }
    function sceneVote(t) {
      bg("#8E1238", "#3D0A1E");
      const k1 = back((t - C.l8) / 0.4), k2 = back((t - C.villana) / 0.4);
      g.save(); g.translate(300, 1250); g.scale(k1, k1); paper(poly([[-220, -720], [220, -720], [220, 60], [-220, 60]]), "#FFF4E0"); xantipa(0, 40, 0.8, t, { angry: 0.5 }); txt("ELLA", 0, -640, 60, "#B0123F"); g.restore();
      g.save(); g.translate(780, 1250); g.scale(k2, k2); paper(poly([[-220, -720], [220, -720], [220, 60], [-220, 60]]), "#FFF4E0"); socrates(0, 40, 0.8, t, {}); txt("ÉL", 0, -640, 60, "#B0123F"); g.restore();
      if (t >= C.marido) { const k = back((t - C.marido) / 0.4); g.save(); g.translate(540, 760); g.scale(k, k); paper(blob(0, 0, 90, 90, 1100), "#FFD23F", 10); txt("?", 0, 34, 110, "#B0123F"); g.restore(); }
    }

    function draw(t) {
      g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, 1080, 1920);
      const S = [[0, sceneTitle], [C.l1, sceneAgora], [C.l2, sceneHome], [C.l3, sceneSplash], [C.l5, sceneCloak], [C.l6, sceneHorse], [C.l7, sceneNight], [C.l8, sceneVote]];
      let i = 0; while (i + 1 < S.length && t >= S[i + 1][0] - 0.12) i++;
      const t0 = S[i][0] - 0.12, k = i ? smooth((t - t0) / 0.35) : 1;
      if (k < 1) { g.save(); g.translate(-1080 * k, 0); g.rotate(-0.04 * k); S[i - 1][1](t); g.restore(); g.save(); g.translate(1080 * (1 - k), 0); g.rotate(0.04 * (1 - k)); S[i][1](t); g.restore(); }
      else S[i][1](t);
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
    sfx = [("chan0", "el_chan", 0.05, 1.5, 0.4), ("zoom0", "el_zoom", C["esposa"], 0.6, 0.35), ("splash0", "el_splash", C["cubeta"] + 0.2, 1.0, 0.35),
           ("w1", "whoosh", C["l1"] - 0.15, 0.57, 0.3), ("laugh1", "el_laugh", C["preguntas"] + 0.3, 1.5, 0.25),
           ("w2", "whoosh", C["l2"] - 0.15, 0.57, 0.3), ("zoom2", "el_zoom", C["l2"], 0.6, 0.35), ("w3", "whoosh", C["l3"] - 0.15, 0.57, 0.3),
           ("thunder", "el_thunder", C["rego"], 1.5, 0.45), ("splash", "el_splash", C["agua"], 1.0, 0.5), ("chan4", "el_chan", C["l4"], 1.5, 0.35),
           ("w5", "whoosh", C["l5"] - 0.15, 0.57, 0.3), ("rip", "el_rip", C["arranco"] + 0.2, 0.8, 0.5), ("gasp", "el_gasp", C["plaza"], 1.2, 0.4),
           ("w6", "whoosh", C["l6"] - 0.15, 0.57, 0.3), ("neigh", "el_neigh", C["caballo"], 1.2, 0.45), ("w7", "whoosh", C["l7"] - 0.15, 0.57, 0.3),
           ("violin", "el_violin", C["platon"], 2.0, 0.45), ("w8", "whoosh", C["l8"] - 0.15, 0.57, 0.3), ("chan8", "el_chan", C["marido"], 1.5, 0.4),
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
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #6B1E3A; }}
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
