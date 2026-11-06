"""EP07: escribe compositions/stage.html (basílica 3D en Three.js + personajes 2D dibujados en canvas) e index.html.

  python -I audio/build_video.py     (después de gen_audio_el.py y build.py)

Híbrido 3D/2D: el escenario (columnas, alfombra, trono, ataúd, rosetón) es Three.js; los personajes son planos con
CanvasTexture que se redibujan en cada cuadro (boca con mouth.json, gestos por tiempo) y miran a la cámara.
Todo se dibuja SOLO desde hf-seek; cada valor es función del tiempo. Temblor solo como ráfaga de ≤0.5 s.
Reglas de motion: textos con máscara (clip-path), movimientos encadenados, cámara que sigue a quien importa,
el ataúd se transforma en trono y la alfombra en el río Tíber, cada entrada anclada a una palabra (W/L).
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
        raise SystemExit(f"palabra '{word}' no está en {line}: {[w['text'] for w in WORDS if ln['start'] - 0.05 <= w['start'] <= ln['end']]}")
    return round(hits[k - 1]["start"] + d, 3)


END = round(LINES["l10"]["end"] + 0.8, 2)
TOTAL = round(END + CARD, 2)
C = {
    "muerto": W("l0", "muerto"), "l1": L("l1"), "roma": W("l1", "roma"), "dig": W("l1", "desenterrar"), "nueve": W("l1", "nueve"),
    "vistio": W("l2", "vistio"), "trono": W("l2", "trono"), "juicio": W("l2", "juicio"),
    "l3": L("l3"), "porto": W("l3", "porto"), "l4": L("l4"), "diacono": W("l4", "diacono"), "l5": L("l5"), "l5e": LINES["l5"]["end"],
    "l6": L("l6"), "culpable": W("l6", "culpable"),
    "l7": L("l7"), "anularon": W("l7", "anularon"), "dedos": W("l7", "dedos"), "tiraron": W("l7", "tiraron"), "tiber": W("l7", "tiber"),
    "l8": L("l8"), "indigno": W("l8", "indigno"), "carcel": W("l8", "carcel"), "estrang": W("l8", "estrangularon"),
    "l9": L("l9"), "rescataron": W("l9", "rescataron"), "honores": W("l9", "honores"),
    "l10": L("l10"), "chisme": W("l10", "chisme"), "end": END,
}

CHIPS = [  # id, text, in, out
    ("chip-roma", "ROMA · AÑO 897", C["roma"], C["nueve"] - 0.15),
    ("chip-nueve", "☠ 9 MESES MUERTO", C["nueve"], C["vistio"] - 0.15),
    ("chip-sinodo", "EL SÍNODO DEL CADÁVER", C["juicio"], C["porto"] - 0.15),
    ("chip-porto", "Obispo de Porto → papa: ¡prohibido!", C["porto"], C["l4"]),
    ("chip-anul", "TODOS SUS ACTOS: ANULADOS", C["anularon"], C["tiber"] - 0.15),
    ("chip-tiber", "🌊 AL RÍO TÍBER", C["tiber"], C["l8"]),
    ("chip-carcel", "AGO 897: ESTEBAN VI, PRESO Y ESTRANGULADO", C["carcel"], C["l9"]),
    ("chip-honor", "Reenterrado en San Pedro con honores", C["honores"], C["end"] - 0.2),
]
IN_CLIP, OUT_CLIP, CLIP_SHOW = "inset(-30px 1200px -30px -30px)", "inset(-30px -30px -30px 1200px)", "inset(-30px -30px -30px -30px)"


def reveal(sel, t, dur=0.35):
    return f'tl.fromTo("{sel}", {{ clipPath: "{IN_CLIP}" }}, {{ clipPath: "{CLIP_SHOW}", duration: {dur}, ease: "power3.out" }}, {round(t, 3)});'


def hide(sel, t, dur=0.25):
    return f'tl.fromTo("{sel}", {{ clipPath: "{CLIP_SHOW}" }}, {{ clipPath: "{OUT_CLIP}", duration: {dur}, ease: "power3.in", immediateRender: false }}, {round(t, 3)});'


STAGE = r'''<template>
  <style>
    #root { position: absolute; inset: 0; overflow: hidden; background: #140E0A; font-family: "Archivo Black", sans-serif; }
    #gl { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
    .tags { position: absolute; left: 0; width: 1080px; text-align: center; }
    .tags span { display: inline-block; white-space: nowrap; font-size: 86px; line-height: 1; padding: 16px 32px 10px; color: #1B1B2F;
      border: 8px solid #1B1B2F; border-radius: 18px; box-shadow: 8px 8px 0 #1B1B2F; }
    #h1 { top: 120px; } #h1 span { background: #FFFFFF; }
    #h2 { top: 278px; clip-path: inset(-30px 1200px -30px -30px); } #h2 span { background: #F2B33D; }
    .chip { position: absolute; left: 0; width: 1080px; top: 170px; text-align: center; clip-path: inset(-30px 1200px -30px -30px); }
    .chip span { display: inline-block; max-width: 960px; font-size: 52px; line-height: 1.1; padding: 14px 28px 10px; background: #F2B33D;
      color: #1B1B2F; border: 7px solid #1B1B2F; border-radius: 14px; box-shadow: 7px 7px 0 #1B1B2F; }
    #chip-sinodo span { background: #7B1E1E; color: #FFFFFF; font-size: 64px; }
    #chip-porto span, #chip-carcel span { background: #FFFFFF; font-size: 44px; }
    #chip-tiber span { background: #2C7FB8; color: #FFFFFF; }
    #chip-honor span { background: #FFF3C4; font-size: 46px; }
    #stamp { position: absolute; left: 0; top: 520px; width: 1080px; text-align: center; }
    #stamp span { display: inline-block; font-size: 150px; line-height: 1; color: #E63946; border: 16px solid #E63946; border-radius: 24px;
      padding: 14px 36px 4px; background: rgba(255,253,246,0.92); opacity: 0; }
  </style>
  <div id="root" data-composition-id="stage" data-width="1080" data-height="1920">
    <canvas id="gl" width="1080" height="1920"></canvas>
__CHIPS__
    <div id="stamp"><span>¡CULPABLE!</span></div>
    <div id="hdr">
      <div id="h1" class="tags"><span>¿UN PAPA MUERTO</span></div>
      <div id="h2" class="tags"><span>EN UN JUICIO?</span></div>
    </div>
  </div>
  <script>
    const C = __C__;
    const MOUTH = __MOUTH__;
    const lerp = (a, b, k) => a + (b - a) * k;
    const clamp = (k) => Math.min(Math.max(k, 0), 1);
    const smooth = (k) => { k = clamp(k); return k * k * (3 - 2 * k); };
    const backOut = (k) => { const s = 1.6; k = clamp(k) - 1; return k * k * ((s + 1) * k + s) + 1; };
    const since = (t, a) => t - a;
    const win = (t, a, b) => t >= a && t < b;
    const mouthAt = (who, t) => { const a = MOUTH[who] || []; return a[Math.max(0, Math.round(t * 30))] || 0; };

    // keys: [time, dur, ...values]; each key eases in over its own dur from the previous pose
    function track(keys, t, ease) {
      let i = 0;
      while (i + 1 < keys.length && t >= keys[i + 1][0]) i++;
      const cur = keys[i];
      if (i === 0) return cur.slice(2);
      const k = (ease || smooth)((t - cur[0]) / cur[1]), prev = keys[i - 1];
      return cur.slice(2).map((v, j) => lerp(prev[j + 2], v, k));
    }

    // ---- camera: [t, dur, px, py, pz, lx, ly, lz] — always framing whoever matters ----
    const CAM = [
      [0, 1, 0.0, 2.2, -1.2, 0.0, 1.7, -6.2],
      [C.l1, 0.6, 0.0, 2.6, 2.0, 0.0, 6.2, -10],
      [C.dig - 0.3, 0.7, 0.0, 2.3, 2.6, 0.0, 0.6, -1.5],
      [C.vistio, 0.6, 0.0, 2.2, 1.6, 0.0, 1.6, -1.5],
      [C.trono, 0.8, 0.0, 2.4, 0.4, 0.0, 1.6, -6.0],
      [C.juicio, 0.7, 0.0, 3.3, 4.2, 0.0, 1.6, -5.0],
      [C.l3, 0.5, -1.2, 2.0, -0.6, -3.0, 1.8, -4.2],
      [C.l4, 0.8, 0.6, 2.0, -3.4, 1.3, 1.5, -7.2],
      [C.l5, 0.5, 1.4, 1.9, -2.4, 0.5, 1.5, -6.6],
      [C.l6, 0.25, -1.7, 1.9, -1.6, -3.0, 2.0, -4.2],
      [C.l7, 0.7, 0.0, 2.4, 0.6, 0.0, 1.5, -6.0],
      [C.dedos - 0.2, 0.5, 0.9, 1.9, -3.6, 0.7, 1.6, -6.0],
      [C.tiraron, 0.9, 0.0, 2.3, 4.6, 0.0, 0.3, 0.2],
      [C.l8, 0.8, 0.0, 3.0, 5.4, 0.0, 1.6, -3.0],
      [C.carcel - 0.2, 0.5, -1.4, 2.0, -0.8, -3.0, 1.6, -4.2],
      [C.l9, 0.7, 0.0, 2.1, 4.2, 0.0, 0.4, 1.0],
      [C.honores - 0.2, 0.8, 0.0, 2.3, -1.4, 0.0, 1.8, -6.2],
      [C.l10, 0.9, 0.0, 3.3, 4.4, 0.0, 1.6, -5.0],
    ];
    // ---- Formoso (feet x, y, z, tilt) ----
    const FORM = [
      [0, 1, 0, 0.5, -6.0, 0],
      [C.l1, 0.05, 0, -3.6, -1.5, 0],
      [C.dig + 0.6, 0.7, 0, 0.0, -1.5, 0],
      [C.trono, 0.6, 0, 0.5, -6.0, 0],
      [C.tiraron, 0.6, 0, 0.0, -0.4, -0.5],
      [C.tiber, 0.5, 0, -1.0, 1.4, -0.35],
      [C.rescataron, 0.6, 0, 0.0, 1.4, 0],
      [C.honores, 0.8, 0, 0.5, -6.0, 0],
    ];
    // ---- coffin → throne back (x, y, z, rotX, gold) ----
    const COF = [
      [0, 1, 0, 1.4, -6.95, -Math.PI / 2, 1],
      [C.l1, 0.05, 0, -2.0, -1.5, 0, 0],
      [C.dig, 0.7, 0, 0.26, -1.5, 0, 0],
      [C.trono, 0.6, 0, 1.4, -6.95, -Math.PI / 2, 1],
    ];

    const canvas = document.getElementById("gl");
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
    renderer.setPixelRatio(1);
    renderer.setSize(1080, 1920, false);
    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#140E0A");
    scene.fog = new THREE.Fog("#140E0A", 9, 22);
    const camera = new THREE.PerspectiveCamera(46, 1080 / 1920, 0.1, 60);
    const hemi = new THREE.HemisphereLight("#FFE9C7", "#2A1A10", 1.0); scene.add(hemi);
    const key = new THREE.DirectionalLight("#FFD9A0", 1.2); key.position.set(-4, 8, 6); scene.add(key);
    const candleL = new THREE.PointLight("#FF9A3C", 6, 9, 1.6); candleL.position.set(-1.8, 2.2, -5.2); scene.add(candleL);
    const candleR = new THREE.PointLight("#FF9A3C", 6, 9, 1.6); candleR.position.set(1.8, 2.2, -5.2); scene.add(candleR);
    const glory = new THREE.PointLight("#FFE38A", 0, 10, 1.4); glory.position.set(0, 3.6, -4.6); scene.add(glory);

    function canvasTex(w, h, draw) {
      const c = document.createElement("canvas"); c.width = w; c.height = h;
      draw(c.getContext("2d"), w, h);
      const tx = new THREE.CanvasTexture(c); tx.colorSpace = THREE.SRGBColorSpace;
      return tx;
    }
    const std = (color, extra) => new THREE.MeshStandardMaterial(Object.assign({ color, roughness: 0.8 }, extra || {}));

    // floor: marble checker
    const floorTex = canvasTex(512, 512, (g) => {
      for (let i = 0; i < 8; i++) for (let j = 0; j < 8; j++) { g.fillStyle = (i + j) % 2 ? "#CDBB98" : "#8A735A"; g.fillRect(i * 64, j * 64, 64, 64); }
    });
    floorTex.wrapS = floorTex.wrapT = THREE.RepeatWrapping; floorTex.repeat.set(3, 5);
    const floor = new THREE.Mesh(new THREE.PlaneGeometry(14, 26), std("#FFFFFF", { map: floorTex, roughness: 0.55 }));
    floor.rotation.x = -Math.PI / 2; floor.position.z = -2; scene.add(floor);
    // walls
    for (const sx of [-1, 1]) {
      const wall = new THREE.Mesh(new THREE.PlaneGeometry(26, 10), std("#4A3526"));
      wall.position.set(sx * 6.5, 5, -2); wall.rotation.y = -sx * Math.PI / 2; scene.add(wall);
    }
    const back = new THREE.Mesh(new THREE.PlaneGeometry(14, 12), std("#3E2B1F")); back.position.set(0, 6, -10); scene.add(back);
    // rose window (stained glass)
    const roseTex = canvasTex(512, 512, (g) => {
      const cols = ["#C62828", "#1565C0", "#F2B33D", "#2E7D32", "#6A1B9A", "#E65100"];
      g.translate(256, 256);
      for (let r = 3; r >= 1; r--) for (let k = 0; k < 12; k++) {
        g.beginPath(); g.moveTo(0, 0); g.arc(0, 0, r * 80, k * Math.PI / 6, (k + 1) * Math.PI / 6); g.closePath();
        g.fillStyle = cols[(k + r) % cols.length]; g.fill(); g.lineWidth = 10; g.strokeStyle = "#1B1B2F"; g.stroke();
      }
      g.beginPath(); g.arc(0, 0, 245, 0, Math.PI * 2); g.lineWidth = 18; g.stroke();
    });
    const rose = new THREE.Mesh(new THREE.CircleGeometry(2.2, 48), new THREE.MeshBasicMaterial({ map: roseTex }));
    rose.position.set(0, 6.2, -9.95); scene.add(rose);
    // columns
    for (const sx of [-1, 1]) for (const z of [2.5, -0.5, -3.5, -6.5]) {
      const col = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.4, 7, 24), std("#D8C8A8"));
      col.position.set(sx * 4.6, 3.5, z); scene.add(col);
      const cap = new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.35, 1.1), std("#C2B08C")); cap.position.set(sx * 4.6, 7.1, z); scene.add(cap);
      const base = new THREE.Mesh(new THREE.BoxGeometry(1.0, 0.3, 1.0), std("#C2B08C")); base.position.set(sx * 4.6, 0.15, z); scene.add(base);
    }
    // dais
    const dais = new THREE.Mesh(new THREE.BoxGeometry(3.6, 0.5, 2.4), std("#6B4B33")); dais.position.set(0, 0.25, -6.6); scene.add(dais);
    // candles
    const flames = [];
    for (const [x, z] of [[-1.8, -5.6], [1.8, -5.6], [-2.4, -6.6], [2.4, -6.6]]) {
      const st = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.1, 1.6, 12), std("#B8912E", { metalness: 0.6 })); st.position.set(x, 0.8 + 0.5, z); scene.add(st);
      const cd = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.07, 0.35, 12), std("#FFF6E0")); cd.position.set(x, 2.25, z); scene.add(cd);
      const fl = new THREE.Mesh(new THREE.SphereGeometry(0.08, 12, 12), new THREE.MeshBasicMaterial({ color: "#FFC24A" }));
      fl.scale.set(1, 1.9, 1); fl.position.set(x, 2.55, z); scene.add(fl); flames.push(fl);
    }
    // carpet → river (the carpet morphs into the Tiber)
    const carpetGeo = new THREE.PlaneGeometry(1.8, 11, 1, 60);
    const carpetBase = carpetGeo.attributes.position.array.slice();
    const carpetMat = std("#8E1B1B", { roughness: 0.7 });
    const carpet = new THREE.Mesh(carpetGeo, carpetMat); carpet.rotation.x = -Math.PI / 2; carpet.position.set(0, 0.015, -0.2); scene.add(carpet);
    const RED = new THREE.Color("#8E1B1B"), BLUE = new THREE.Color("#2C7FB8");

    // coffin that becomes the throne back
    const coffin = new THREE.Group(); scene.add(coffin);
    const cofMat = std("#5A3A22");
    const cofBox = new THREE.Mesh(new THREE.BoxGeometry(1.25, 0.5, 2.6), cofMat); coffin.add(cofBox);
    const lidPivot = new THREE.Group(); lidPivot.position.set(-0.62, 0.25, 0); coffin.add(lidPivot);
    const lid = new THREE.Mesh(new THREE.BoxGeometry(1.25, 0.12, 2.6), std("#6E4A2C")); lid.position.set(0.62, 0.06, 0); lidPivot.add(lid);
    const cross = new THREE.Mesh(new THREE.BoxGeometry(0.16, 0.04, 1.2), std("#F2B33D", { metalness: 0.5 })); cross.position.set(0.62, 0.13, 0); lidPivot.add(cross);
    const cross2 = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.04, 0.16), std("#F2B33D", { metalness: 0.5 })); cross2.position.set(0.62, 0.13, -0.3); lidPivot.add(cross2);
    const seat = new THREE.Mesh(new THREE.BoxGeometry(1.5, 0.6, 1.0), std("#B8912E", { metalness: 0.4 })); seat.position.set(0, 0.8, -6.25); scene.add(seat);
    const WOOD = new THREE.Color("#5A3A22"), GOLD = new THREE.Color("#C9A13B");

    // jail bars that drop in front of Esteban
    const bars = new THREE.Group(); scene.add(bars);
    for (let i = 0; i < 7; i++) { const b = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 3.6, 10), std("#3A3A44", { metalness: 0.8, roughness: 0.4 })); b.position.set(-0.9 + i * 0.3, 1.8, 0); bars.add(b); }
    for (const y of [0.4, 3.3]) { const h = new THREE.Mesh(new THREE.BoxGeometry(2.1, 0.12, 0.12), std("#3A3A44", { metalness: 0.8 })); h.position.set(0, y, 0); bars.add(h); }

    // splash droplets + confetti (seeded, deterministic)
    let seed = 7; const rnd = () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };
    const drops = [];
    for (let i = 0; i < 16; i++) { const d = new THREE.Mesh(new THREE.SphereGeometry(0.07, 8, 8), new THREE.MeshBasicMaterial({ color: "#CFEFFF" })); d.userData = { a: (i / 16) * Math.PI * 2, v: 1.6 + rnd() * 1.6, up: 2.5 + rnd() * 2 }; scene.add(d); drops.push(d); }
    const confetti = [], CONF = ["#F2B33D", "#FFFFFF", "#E63946", "#2C7FB8", "#2BB673"];
    for (let i = 0; i < 70; i++) { const p = new THREE.Mesh(new THREE.PlaneGeometry(0.12, 0.2), new THREE.MeshBasicMaterial({ color: CONF[i % 5], side: THREE.DoubleSide })); p.userData = { x: (rnd() - 0.5) * 5, z: -6 + (rnd() - 0.5) * 3.5, y0: 5 + rnd() * 3, sp: 1.0 + rnd() * 0.8, rot: rnd() * 6 }; scene.add(p); confetti.push(p); }
    const halo = new THREE.Mesh(new THREE.TorusGeometry(0.42, 0.06, 12, 40), new THREE.MeshBasicMaterial({ color: "#FFD54A" })); halo.rotation.x = Math.PI / 2; scene.add(halo);

    // ---------- 2D characters: canvas planes that face the camera ----------
    const INK = "#1B1B2F";
    function sprite(w, h, pw, ph) {
      const c = document.createElement("canvas"); c.width = w; c.height = h;
      const tx = new THREE.CanvasTexture(c); tx.colorSpace = THREE.SRGBColorSpace;
      const mat = new THREE.MeshBasicMaterial({ map: tx, transparent: true, alphaTest: 0.05, side: THREE.DoubleSide });
      const geo = new THREE.PlaneGeometry(pw, ph); geo.translate(0, ph / 2, 0);
      const mesh = new THREE.Mesh(geo, mat); scene.add(mesh);
      const sh = new THREE.Mesh(new THREE.CircleGeometry(pw * 0.32, 32), new THREE.MeshBasicMaterial({ color: "#000000", transparent: true, opacity: 0.35 }));
      sh.rotation.x = -Math.PI / 2; sh.scale.set(1, 0.45, 1); scene.add(sh);
      return { c, g: c.getContext("2d"), tx, mat, mesh, sh };
    }
    function ell(g, x, y, rx, ry, fill, lw) { g.beginPath(); g.ellipse(x, y, rx, ry, 0, 0, Math.PI * 2); if (fill) { g.fillStyle = fill; g.fill(); } if (lw) { g.lineWidth = lw; g.strokeStyle = INK; g.stroke(); } }
    function poly(g, pts, fill, lw) { g.beginPath(); g.moveTo(pts[0][0], pts[0][1]); for (const p of pts.slice(1)) g.lineTo(p[0], p[1]); g.closePath(); if (fill) { g.fillStyle = fill; g.fill(); } if (lw !== 0) { g.lineWidth = lw || 9; g.strokeStyle = INK; g.lineJoin = "round"; g.stroke(); } }
    function tiara(g, x, y, s) {
      g.save(); g.translate(x, y); g.scale(s, s);
      g.beginPath(); g.moveTo(-58, 0); g.quadraticCurveTo(-62, -120, 0, -150); g.quadraticCurveTo(62, -120, 58, 0); g.closePath();
      g.fillStyle = "#FBF7EC"; g.fill(); g.lineWidth = 9; g.strokeStyle = INK; g.stroke();
      for (const yy of [-12, -55, -98]) { g.fillStyle = "#E3B23C"; g.fillRect(-60 + Math.abs(yy) * 0.12, yy - 9, 120 - Math.abs(yy) * 0.24, 16); g.strokeRect(-60 + Math.abs(yy) * 0.12, yy - 9, 120 - Math.abs(yy) * 0.24, 16); }
      ell(g, 0, -160, 12, 12, "#E3B23C", 6); g.restore();
    }
    function mouthShape(g, x, y, w, open, fill) {
      g.beginPath(); g.ellipse(x, y, w, 5 + open * 34, 0, 0, Math.PI * 2); g.fillStyle = fill || "#5A1414"; g.fill(); g.lineWidth = 8; g.strokeStyle = INK; g.stroke();
      if (open > 0.15) { g.fillStyle = "#FFFFFF"; g.fillRect(x - w * 0.6, y - 5 - open * 34 + 4, w * 1.2, 10); }
    }

    const formoso = sprite(512, 768, 2.0, 3.0);
    function drawFormoso(t) {
      const { g } = formoso; g.clearRect(0, 0, 512, 768);
      const jaw = win(t, C.l5 - 0.05, C.l5e + 0.1) ? mouthAt("diacono", t) : 0;
      const dressed = t < C.l1 ? 1 : smooth(since(t, C.vistio) / 0.35);
      const cape = t < C.l1 ? 1 : smooth(since(t, C.vistio + 0.2) / 0.35);
      const tiaraIn = t < C.l1 ? 1 : backOut(since(t, C.vistio + 0.4) / 0.45);
      const wet = win(t, C.tiber, C.honores) ? 1 : 0;
      // robe
      poly(g, [[160, 430], [352, 430], [410, 750], [102, 750]], dressed > 0.01 ? "#F4EFE0" : "#8C8574");
      if (dressed > 0.01) { g.fillStyle = "#E3B23C"; g.fillRect(238, 440, 36, 300); g.strokeStyle = INK; g.lineWidth = 6; g.strokeRect(238, 440, 36, 300); }
      // cape slides down from above
      if (cape > 0.01) { g.save(); g.translate(0, (1 - cape) * -220); g.globalAlpha = cape; ell(g, 256, 440, 140, 70, "#B71C1C", 9); g.restore(); }
      // skull-ish head
      ell(g, 256, 300, 88, 100, wet ? "#9DB6A4" : "#B5BFA0", 10);
      ell(g, 220, 288, 22, 27, "#3A4A36"); ell(g, 292, 288, 22, 27, "#3A4A36");
      const wink = since(t, C.chisme) > 0 && since(t, C.chisme) < 1.6;
      ell(g, 220, 292, 5, 5, "#E9F2C8");
      if (wink) { g.beginPath(); g.moveTo(276, 292); g.quadraticCurveTo(292, 280, 308, 292); g.lineWidth = 8; g.strokeStyle = "#E9F2C8"; g.stroke(); }
      else ell(g, 292, 292, 5, 5, "#E9F2C8");
      g.fillStyle = INK; g.fillRect(248, 318, 5, 14); g.fillRect(260, 318, 5, 14);
      mouthShape(g, 256, 360, 34, jaw, "#2A2420");
      for (const [x, y] of [[196, 225], [230, 212], [300, 222]]) { g.beginPath(); g.moveTo(x, y); g.lineTo(x - 8, y - 30); g.lineWidth = 5; g.strokeStyle = "#E8E2CF"; g.stroke(); }
      if (wet) for (const [x, y] of [[170, 260], [340, 300], [210, 410]]) ell(g, x, y + ((t * 60) % 30), 6, 10, "#8FD3FF", 4);
      // blessing hand with three fingers — the fingers vanish with a puff on "dedos"
      const fingers = t < C.dedos || t >= C.honores ? 1 : 0;
      ell(g, 392, 450, 30, 34, "#B5BFA0", 8);
      if (fingers) for (let k = 0; k < 3; k++) { g.beginPath(); g.roundRect(370 + k * 16, 380, 14, 56, 7); g.fillStyle = "#B5BFA0"; g.fill(); g.lineWidth = 6; g.strokeStyle = INK; g.stroke(); }
      const puff = since(t, C.dedos);
      if (puff > 0 && puff < 0.7) for (let k = 0; k < 6; k++) { const a = k * Math.PI / 3, r = 30 + puff * 120; g.globalAlpha = 1 - puff / 0.7; ell(g, 392 + Math.cos(a) * r, 400 + Math.sin(a) * r, 16, 16, "#FFFFFF", 5); g.globalAlpha = 1; }
      if (tiaraIn > 0.01 && !win(t, C.tiraron, C.honores)) tiara(g, 256, 215 - (1 - tiaraIn) * 260, 1.0);
      formoso.tx.needsUpdate = true;
    }

    const esteban = sprite(512, 768, 2.0, 3.0);
    function drawEsteban(t) {
      const { g } = esteban; g.clearRect(0, 0, 512, 768);
      const m = mouthAt("esteban", t);
      const rage = win(t, C.l3, C.l7) ? 1 : 0.4;
      const point = win(t, C.l3, C.l4) ? smooth(since(t, C.l3) / 0.25) : 0;
      const bang = since(t, C.culpable), gav = bang > 0 && bang < 0.9 ? Math.sin(Math.min(bang / 0.18, 1) * Math.PI / 2) : 0;
      poly(g, [[170, 440], [342, 440], [400, 750], [112, 750]], "#B71C1C");
      ell(g, 256, 450, 120, 52, "#FBF7EC", 8);
      g.fillStyle = "#E3B23C"; g.fillRect(246, 520, 20, 90); g.fillRect(220, 545, 72, 20);
      // pointing arm (right) and gavel arm (left)
      g.save(); g.translate(340, 480); g.rotate(lerp(0.9, -0.5, point)); g.beginPath(); g.roundRect(-14, -14, 150, 30, 14); g.fillStyle = "#B71C1C"; g.fill(); g.lineWidth = 8; g.strokeStyle = INK; g.stroke();
      ell(g, 150, 0, 22, 20, "#F2B38A", 7); g.beginPath(); g.roundRect(160, -6, 44, 13, 6); g.fillStyle = "#F2B38A"; g.fill(); g.stroke(); g.restore();
      g.save(); g.translate(172, 480); g.rotate(lerp(-2.3, -0.6, gav)); g.beginPath(); g.roundRect(-14, -14, 140, 30, 14); g.fillStyle = "#B71C1C"; g.fill(); g.lineWidth = 8; g.strokeStyle = INK; g.stroke();
      g.fillStyle = "#7A4A24"; g.fillRect(118, -60, 14, 120); g.strokeRect(118, -60, 14, 120); g.fillRect(96, -84, 58, 36); g.strokeRect(96, -84, 58, 36); g.restore();
      const skin = rage > 0.5 ? "#E8806A" : "#F2B38A";
      ell(g, 256, 320, 92, 100, skin, 10);
      ell(g, 222, 300, 20, 22, "#FFFFFF", 6); ell(g, 290, 300, 20, 22, "#FFFFFF", 6);
      ell(g, 228, 304, 8, 9, INK); ell(g, 284, 304, 8, 9, INK);
      g.lineWidth = 13; g.strokeStyle = INK; g.beginPath(); g.moveTo(196, 262 - rage * 4); g.lineTo(244, 278 + rage * 6); g.moveTo(316, 262 - rage * 4); g.lineTo(268, 278 + rage * 6); g.stroke();
      ell(g, 256, 335, 14, 12, "#D9705A", 6);
      mouthShape(g, 256, 375, 36, m);
      tiara(g, 256, 236, 0.95);
      esteban.tx.needsUpdate = true;
    }

    const diacono = sprite(512, 768, 1.7, 2.6);
    function drawDiacono(t) {
      const { g } = diacono; g.clearRect(0, 0, 512, 768);
      const m = mouthAt("diacono", t);
      poly(g, [[190, 450], [322, 450], [360, 750], [152, 750]], "#2B2B3A");
      ell(g, 256, 455, 80, 30, "#FFFFFF", 7);
      ell(g, 256, 330, 82, 92, "#F5C8A0", 10);
      g.beginPath(); g.ellipse(256, 270, 86, 50, 0, Math.PI, 0); g.lineWidth = 26; g.strokeStyle = "#6D4C2F"; g.stroke();
      ell(g, 226, 322, 24, 28, "#FFFFFF", 6); ell(g, 288, 322, 24, 28, "#FFFFFF", 6);
      ell(g, 226, 330, 9, 10, INK); ell(g, 288, 330, 9, 10, INK);
      g.lineWidth = 10; g.strokeStyle = INK; g.beginPath(); g.moveTo(200, 286); g.lineTo(240, 278); g.moveTo(312, 286); g.lineTo(272, 278); g.stroke();
      mouthShape(g, 256, 385, 26, m);
      for (let k = 0; k < 2; k++) { const ph = (t * 0.9 + k * 0.5) % 1; g.globalAlpha = 1 - ph; ell(g, 180 + k * 150, 300 + ph * 90, 9, 14, "#8FD3FF", 4); g.globalAlpha = 1; }
      diacono.tx.needsUpdate = true;
    }

    const crowd = sprite(1024, 384, 9.0, 3.4);
    crowd.sh.visible = false;
    function drawCrowd(t) {
      const { g } = crowd; g.clearRect(0, 0, 1024, 384);
      for (let i = 0; i < 11; i++) {
        const x = 50 + i * 92, bob = Math.sin(t * 7 + i * 1.7) * 8, y = 220 + (i % 2) * 30 + bob;
        poly(g, [[x - 46, 384], [x - 34, y + 60], [x + 34, y + 60], [x + 46, 384]], "#2A1E2E", 0);
        ell(g, x, y + 20, 36, 40, "#2A1E2E");
        if (i % 3 === 0) { g.fillStyle = "#3B2A1A"; g.fillRect(x + 30, y - 70, 10, 130); ell(g, x + 35, y - 84, 16, 26 + Math.sin(t * 14 + i) * 5, "#FF9A3C"); ell(g, x + 35, y - 80, 8, 14, "#FFE38A"); }
        if (i % 3 === 1) { g.lineWidth = 8; g.strokeStyle = "#2A1E2E"; g.beginPath(); g.moveTo(x - 40, y - 60); g.lineTo(x - 40, y + 50); g.moveTo(x - 58, y - 60); g.lineTo(x - 58, y - 30); g.lineTo(x - 22, y - 30); g.lineTo(x - 22, y - 60); g.stroke(); }
      }
      crowd.tx.needsUpdate = true;
    }

    function face(sp, x, y, z, tilt) {
      sp.mesh.position.set(x, y, z);
      sp.mesh.rotation.set(0, Math.atan2(camera.position.x - x, camera.position.z - z), tilt || 0);
      sp.sh.position.set(x, Math.max(y, 0) + 0.02, z);
      sp.sh.material.opacity = y < -0.2 ? 0 : 0.35;
    }

    function render(t) {
      // camera with a ≤0.5 s decaying burst on the shouts
      const [px, py, pz, lx, ly, lz] = track(CAM, t);
      let sh = 0;
      for (const a of [C.l3, C.culpable]) { const s = since(t, a); if (s > 0 && s < 0.45) sh += 0.06 * (1 - s / 0.45) * Math.sin(s * 70); }
      camera.position.set(px + sh, py + sh * 0.6, pz);
      camera.lookAt(lx, ly, lz);
      camera.updateMatrixWorld();

      // lights: whisper dims the church, honours bathe it in gold
      const dim = win(t, C.l4, C.l6) ? smooth(since(t, C.l4) / 0.4) : (win(t, C.l6, C.l6 + 0.4) ? 1 - since(t, C.l6) / 0.4 : 0);
      const gold = smooth(since(t, C.honores) / 0.6);
      hemi.intensity = lerp(1.0, 0.45, dim) + gold * 0.5;
      glory.intensity = gold * 14;
      flames.forEach((f, i) => f.scale.set(1, 1.8 + Math.sin(t * 11 + i * 2) * 0.25, 1));

      // carpet → Tiber river and back
      const river = win(t, C.tiraron - 0.4, C.rescataron + 0.6) ? smooth(since(t, C.tiraron - 0.4) / 0.6) * (1 - smooth(since(t, C.rescataron) / 0.6)) : 0;
      carpetMat.color.copy(RED).lerp(BLUE, river);
      const pos = carpetGeo.attributes.position;
      for (let i = 0; i < pos.count; i++) {
        const bx = carpetBase[i * 3], by = carpetBase[i * 3 + 1];
        pos.setX(i, bx * (1 + river * 1.6));
        pos.setZ(i, river * 0.04 * Math.sin(by * 2.6 + t * 5));
      }
      pos.needsUpdate = true; carpetGeo.computeVertexNormals(); carpet.position.y = 0.015 + river * 0.08;

      // coffin rises, opens, then flies to the dais and becomes the throne
      const [cx, cy, cz, crx, cg] = track(COF, t);
      coffin.position.set(cx, cy, cz); coffin.rotation.set(crx, 0, 0);
      cofMat.color.copy(WOOD).lerp(GOLD, cg);
      const open = win(t, C.dig + 0.35, C.trono) ? backOut(since(t, C.dig + 0.35) / 0.4) : 0;
      lidPivot.rotation.z = open * 1.9;
      lid.visible = cross.visible = cross2.visible = cg < 0.5;
      const seatIn = t < C.l1 ? 1 : backOut(since(t, C.trono + 0.4) / 0.4);
      seat.scale.setScalar(Math.max(seatIn, 0.001)); seat.visible = seatIn > 0.01;

      // characters
      const [fx, fy, fz, ftilt] = track(FORM, t);
      drawFormoso(t); face(formoso, fx, fy, fz, ftilt);
      drawEsteban(t); face(esteban, -3.0, 0, -4.2, 0);
      const darkE = smooth(since(t, C.estrang) / 0.5);
      esteban.mat.color.setScalar(lerp(1, 0.18, darkE));
      const peek = win(t, C.l4, C.l6 + 0.6) ? smooth(since(t, C.l4) / 0.4) : 0;
      diacono.mesh.visible = diacono.sh.visible = !win(t, C.l1, C.trono + 0.3); drawDiacono(t); face(diacono, lerp(0.75, 1.55, peek), 0.5, -7.2, lerp(0, -0.12, peek));
      const rise = win(t, C.indigno - 0.2, C.l9 + 0.3) ? backOut(since(t, C.indigno - 0.2) / 0.5) * (1 - smooth(since(t, C.l9) / 0.3)) : 0;
      crowd.mesh.visible = rise > 0.01;
      if (rise > 0.01) { drawCrowd(t); crowd.mesh.position.set(0, lerp(-1.5, 0.75, rise), 0.8); crowd.mesh.scale.setScalar(0.5); crowd.mesh.rotation.set(-0.1, 0, 0); }
      const drop = since(t, C.carcel);
      bars.position.set(-3.0, drop > 0 ? lerp(6, 0, backOut(drop / 0.3)) : 30, -3.7);

      // splash on the Tiber + confetti and halo for the honours
      const sp = since(t, C.tiber);
      drops.forEach((d) => {
        const vis = sp > 0 && sp < 1.1; d.visible = vis;
        if (vis) d.position.set(Math.cos(d.userData.a) * d.userData.v * sp, 0.1 + d.userData.up * sp - 4.9 * sp * sp, 1.4 + Math.sin(d.userData.a) * d.userData.v * sp * 0.6);
      });
      const hs = since(t, C.honores);
      confetti.forEach((p) => {
        const u = p.userData; p.visible = hs > 0;
        if (hs > 0) { p.position.set(u.x + Math.sin(hs * 2 + u.rot) * 0.3, u.y0 - u.sp * hs * 1.6, u.z); p.rotation.set(hs * 3 + u.rot, hs * 2, 0); }
      });
      halo.visible = hs > 0.1;
      halo.position.set(0, 3.5, -6.0); halo.scale.setScalar(backOut(hs / 0.5));

      renderer.render(scene, camera);
    }

    window.__hf = window.__hf || {};
    window.__hf.buildReady = window.__hf.buildReady || {};
    window.__hf.buildReady["basilica3d"] = (async () => {
      await renderer.compileAsync(scene, camera);
      render(0);
    })();
    window.addEventListener("hf-seek", (e) => render(e.detail.time));

    const tl = gsap.timeline({ paused: true });
__TW__
    window.__timelines["stage"] = tl;
  </script>
</template>
'''


def stage_html():
    chips = "\n".join(f'    <div id="{i}" class="chip"><span>{txt}</span></div>' for i, txt, _, _ in CHIPS)
    tw = [reveal("#h2", 0.05, 0.3), hide("#h1", C["l1"] - 0.15), hide("#h2", C["l1"] - 0.05)]
    for i, _, a, b in CHIPS:
        tw += [reveal(f"#{i}", a), hide(f"#{i}", b)]
    tw += [
        f'tl.fromTo("#stamp span", {{ opacity: 0, scale: 3, rotation: 18 }}, {{ opacity: 1, scale: 1, rotation: -8, duration: 0.2, ease: "power4.in" }}, {C["culpable"]});',
        f'tl.to("#stamp span", {{ opacity: 0, scale: 0.8, duration: 0.25 }}, {C["l7"] - 0.1});',
    ]
    js_mouth = {k: v for k, v in MOUTH.items() if k != "fps" and k != "narr"}
    return (STAGE.replace("__CHIPS__", chips).replace("__C__", json.dumps(C))
            .replace("__MOUTH__", json.dumps(js_mouth, separators=(",", ":")))
            .replace("__TW__", "\n".join("    " + x for x in tw)))


def index_html():
    sfx = [("organ0", "el_organ", 0.1, 2.0, 0.45), ("dig", "el_dig", C["dig"], 1.2, 0.5), ("creak", "el_creak", C["dig"] + 0.35, 1.5, 0.45),
           ("dress", "whoosh-short", C["vistio"], 0.4, 0.4), ("throne", "whoosh", C["trono"], 0.57, 0.4), ("gavel1", "el_gavel", C["juicio"], 1.0, 0.5),
           ("organ1", "el_organ", C["l3"], 2.0, 0.35), ("gasp", "el_gasp", C["diacono"], 1.5, 0.35), ("bones", "el_bones", C["l5"], 1.0, 0.4),
           ("gavel2", "el_gavel", C["culpable"], 1.0, 0.65), ("impact", "impact-bass-1", C["culpable"], 2.1, 0.4),
           ("poof", "pop", C["dedos"], 0.72, 0.5), ("slide", "whoosh", C["tiraron"], 0.57, 0.4), ("splash", "el_splash", C["tiber"], 1.5, 0.55),
           ("crowd", "el_crowd", C["indigno"], 2.0, 0.4), ("bars", "el_bars", C["carcel"], 1.2, 0.5),
           ("rise", "riser", C["rescataron"] - 0.3, 1.0, 0.3), ("fanfare", "el_fanfare", C["honores"], 2.0, 0.45),
           ("end", "whoosh", END - 0.05, 0.57, 0.4), ("end-logo", "pop", END + 0.25, 0.72, 0.5), ("end-title", "sparkle", END + 0.55, 1.8, 0.35)]
    rows = [f'      <audio id="sfx-{i}" class="clip" src="assets/sfx/{f}.mp3" data-start="{round(t, 3)}" data-duration="{d}" '
            f'data-track-index="{5 + k % 6}" data-volume="{v}"></audio>' for k, (i, f, t, d, v) in enumerate(sfx)]
    return f'''<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.159.0/build/three.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #140E0A; }}
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
