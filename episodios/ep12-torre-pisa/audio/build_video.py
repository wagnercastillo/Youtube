"""EP12: escribe compositions/stage.html (la Torre de Pisa cuenta su chisme, 3D con three.js) e index.html.

  python -I audio/build_video.py     (después de gen_audio_el.py y build.py)

Escena three.js (toon shading, sombras) dibujada por cuadro desde hf-seek: la torre se construye piso por piso, se hunde en el
suelo blando (corte visible), banderas de la guerra, contador de años, torre fantasma que se cae, pisos curvos, plomo y tierra,
turistas empujándola y guiño final. Cara de la torre con boca desde mouth.json. Cámara orbital anclada a palabras.
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
C = {
    "chueca": W("l0", "chueca"), "terminaran": W("l0", "terminaran"),
    "l1": L("l1"), "pisa": W("l1", "pisa"), "mil": W("l1", "mil"),
    "l2": L("l2"), "cinco": W("l2", "cinco"), "dos": W("l2", "dos"), "hundiendo": W("l2", "hundiendo"), "suelo": W("l2", "suelo"),
    "l3": L("l3"), "guerra": W("l3", "guerra"), "genova": W("l3", "genova"), "lucca": W("l3", "lucca"), "florencia": W("l3", "florencia"), "cien": W("l3", "cien"),
    "l4": L("l4"), "salvo": W("l4", "salvo"), "asento": W("l4", "asento"), "corrido": W("l4", "corrido"), "caigo": W("l4", "caigo"),
    "l5": L("l5"), "pisos": W("l5", "pisos"), "altos": W("l5", "altos"), "curvita": W("l5", "curvita"),
    "l6": L("l6"), "grados": W("l6", "grados"), "cerraron": W("l6", "cerraron"),
    "l7": L("l7"), "plomo": W("l7", "plomo"), "tierra": W("l7", "tierra"), "enderezaron": W("l7", "enderezaron"),
    "l8": L("l8"), "poquito": W("l8", "poquito"), "quien": W("l8", "quien"), "derechita": W("l8", "derechita"), "end": END,
}
BANNERS = [
    ("b1", "TORRE DE PISA · DESDE 1173", C["pisa"], C["l2"] - 0.1),
    ("b2", "1178: CON 2 PISOS… ¡SE HUNDE!", C["dos"], C["l3"] - 0.1),
    ("b3", "PISA VS. GÉNOVA, LUCCA Y FLORENCIA", C["guerra"], C["cien"] - 0.05),
    ("b4", "OBRA EN PAUSA: CASI 100 AÑOS", C["cien"], C["l4"] - 0.1),
    ("b5", "LA TIERRA SE ASENTÓ", C["asento"], C["corrido"] - 0.05),
    ("b6", "SIN LA PAUSA… ¡SE CAE!", C["corrido"], C["l5"] - 0.1),
    ("b7", "PISOS MÁS ALTOS DE UN LADO", C["altos"], C["l6"] - 0.1),
    ("b8", "1990: 5.5° · ¡CERRADA!", C["grados"], C["l7"] - 0.1),
    ("b9", "870 TONELADAS DE PLOMO", C["plomo"], C["enderezaron"] - 0.05),
    ("b10", "2001: 3.97° · SIGUE CHUECA", C["enderezaron"], C["l8"] + 0.6),
    ("b11", "¿DERECHITA? ¡JAMÁS!", C["derechita"], C["end"] - 0.1),
]
SOURCES = [("s1", "Fuente: Wikipedia, «Leaning Tower of Pisa»", C["l6"], C["l8"] - 0.1)]
IN_CLIP, SHOW, OUT_CLIP = "inset(-30px 1200px -30px -30px)", "inset(-30px -30px -30px -30px)", "inset(-30px -30px -30px 1200px)"


def stage_html():
    banners = "\n".join(f'    <div id="{i}" class="ban"><span>{t}</span></div>' for i, t, _, _ in BANNERS)
    banners += "\n" + "\n".join(f'    <div id="{i}" class="src"><span>{t}</span></div>' for i, t, _, _ in SOURCES)
    tw = ['tl.fromTo("#h1", { clipPath: "' + IN_CLIP + '" }, { clipPath: "' + SHOW + '", duration: 0.3, ease: "power3.out" }, 0.03);',
          'tl.fromTo("#h2", { clipPath: "' + IN_CLIP + '" }, { clipPath: "' + SHOW + '", duration: 0.3, ease: "power3.out" }, 0.18);',
          f'tl.fromTo("#hook", {{ clipPath: "{SHOW}" }}, {{ clipPath: "{OUT_CLIP}", duration: 0.3, ease: "power3.in", immediateRender: false }}, {round(C["l1"] - 0.05, 3)});']
    for i, _, a, b in BANNERS + SOURCES:
        tw += [f'tl.fromTo("#{i}", {{ clipPath: "{IN_CLIP}" }}, {{ clipPath: "{SHOW}", duration: 0.32, ease: "power3.out" }}, {round(a, 3)});',
               f'tl.fromTo("#{i}", {{ clipPath: "{SHOW}" }}, {{ clipPath: "{OUT_CLIP}", duration: 0.22, ease: "power3.in", immediateRender: false }}, {round(b, 3)});']
    return (STAGE.replace("__C__", json.dumps(C)).replace("__M__", json.dumps(MOUTH, separators=(",", ":")))
            .replace("__BANNERS__", banners).replace("__TW__", "\n".join("    " + x for x in tw)))


STAGE = r'''<template>
  <style>
    #root { position: absolute; inset: 0; overflow: hidden; background: #9FD8F2; font-family: "Archivo Black", sans-serif; }
    #gl { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
    .ban { position: absolute; left: 0; top: 250px; width: 1080px; text-align: center; clip-path: inset(-30px 1200px -30px -30px); }
    .ban span { display: inline-block; max-width: 1000px; font-size: 50px; line-height: 1.1; padding: 16px 28px 10px; background: #FFFFFF;
      color: #1B1B2F; border: 8px solid #1B1B2F; border-radius: 18px; box-shadow: 8px 8px 0 #1B1B2F; }
    #b2 span, #b6 span, #b8 span { background: #E63946; color: #FFFFFF; } #b4 span, #b9 span { background: #FFD23F; } #b11 span { background: #2BB673; color: #FFFFFF; }
    .src { position: absolute; left: 0; top: 1455px; width: 1080px; text-align: center; clip-path: inset(-30px 1200px -30px -30px); }
    .src span { display: inline-block; font-family: "Nunito", sans-serif; font-weight: 800; font-size: 30px; padding: 6px 16px; background: rgba(27,27,47,0.85); color: #FFFFFF; border-radius: 10px; }
    #hook { position: absolute; left: 0; top: 230px; width: 1080px; }
    .tags { width: 1080px; text-align: center; margin-bottom: 24px; clip-path: inset(-30px 1200px -30px -30px); }
    .tags span { display: inline-block; white-space: nowrap; font-size: 70px; line-height: 1; padding: 16px 30px 10px; color: #1B1B2F; border: 8px solid #1B1B2F; border-radius: 18px; box-shadow: 8px 8px 0 #1B1B2F; }
    #h1 span { background: #FFFFFF; } #h2 span { background: #FFD23F; }
    #hud { position: absolute; right: 40px; top: 480px; text-align: right; }
    #hud div { display: inline-block; font-size: 54px; padding: 10px 22px 4px; background: #1B1B2F; color: #FFD23F; border-radius: 14px; margin-bottom: 12px; }
  </style>
  <div id="root" data-composition-id="stage" data-width="1080" data-height="1920">
    <canvas id="gl" width="1080" height="1920" data-layout-allow-overflow></canvas>
__BANNERS__
    <div id="hook">
      <div id="h1" class="tags"><span>¿CHUECA DESDE ANTES</span></div>
      <div id="h2" class="tags"><span>DE TERMINARLA?</span></div>
    </div>
    <div id="hud"><div id="yr">1173</div><br><div id="ang">0.0°</div></div>
  </div>
  <script>
    const C = __C__;
    const M = __M__;
    const clamp = (k) => Math.min(Math.max(k, 0), 1);
    const smooth = (k) => { k = clamp(k); return k * k * (3 - 2 * k); };
    const back = (k) => { k = clamp(k); const s = 1.7; return 1 + (s + 1) * Math.pow(k - 1, 3) + s * Math.pow(k - 1, 2); };
    const lerp = (a, b, k) => a + (b - a) * k;
    function track(keys, t) {
      let i = 0;
      while (i + 1 < keys.length && t >= keys[i + 1][0]) i++;
      if (i === 0) return keys[0].slice(2);
      const cur = keys[i], k = smooth((t - cur[0]) / cur[1]);
      const from = i >= 2 ? track(keys.slice(0, i), cur[0]) : keys[0].slice(2);
      return cur.slice(2).map((v, j) => lerp(from[j], v, k));
    }
    const mouth = (t) => (M.narr || [])[Math.floor(t * 30)] || 0;
    const rnd = (i) => { const x = Math.sin(i * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

    const canvas = document.getElementById("gl");
    const R = new THREE.WebGLRenderer({ canvas, antialias: true, preserveDrawingBuffer: true });
    R.setPixelRatio(1); R.setSize(1080, 1920, false); R.outputEncoding = THREE.sRGBEncoding;
    R.shadowMap.enabled = true; R.shadowMap.type = THREE.PCFSoftShadowMap;
    const S = new THREE.Scene();
    const SKY = new THREE.Color("#9FD8F2"); S.background = SKY.clone();
    const cam = new THREE.PerspectiveCamera(38, 1080 / 1920, 0.1, 200);
    const grad = new THREE.DataTexture(new Uint8Array([105, 105, 105, 255, 170, 170, 170, 255, 225, 225, 225, 255]), 3, 1, THREE.RGBAFormat);
    grad.minFilter = grad.magFilter = THREE.NearestFilter; grad.needsUpdate = true;
    const toon = (c, extra) => new THREE.MeshToonMaterial(Object.assign({ color: c, gradientMap: grad }, extra || {}));
    const hemi = new THREE.HemisphereLight(0xffffff, 0x6f9a5c, 0.5); S.add(hemi);
    const sun = new THREE.DirectionalLight(0xffffff, 0.85); sun.position.set(8, 16, 10); sun.castShadow = true;
    sun.shadow.mapSize.set(2048, 2048); Object.assign(sun.shadow.camera, { left: -14, right: 14, top: 14, bottom: -14, near: 1, far: 60 }); S.add(sun);
    const mesh = (geo, mat, parent, x, y, z) => { const m = new THREE.Mesh(geo, mat); m.position.set(x || 0, y || 0, z || 0); m.castShadow = true; m.receiveShadow = true; (parent || S).add(m); return m; };

    // ground (turns see-through to reveal the soft soil) + piazza
    const groundMat = toon("#4FA34A", { transparent: true, opacity: 1 });
    const ground = mesh(new THREE.CircleGeometry(60, 64), groundMat); ground.rotation.x = -Math.PI / 2; ground.castShadow = false;
    const path = mesh(new THREE.PlaneGeometry(3, 40), toon("#D9C9A8", { transparent: true })); path.rotation.x = -Math.PI / 2; path.position.set(0, 0.01, 12); path.castShadow = false;
    const clay = mesh(new THREE.SphereGeometry(3.2, 32, 16), toon("#9C6B43")); clay.scale.set(1, 0.45, 1); clay.position.y = -1.3;
    const rock = mesh(new THREE.CylinderGeometry(9, 9, 0.4, 32), toon("#6B4A33")); rock.position.y = -3.2;
    // cathedral and baptistery in the back
    const duomo = new THREE.Group(); S.add(duomo); duomo.position.set(-10, 0, -12);
    mesh(new THREE.BoxGeometry(9, 3.2, 3.5), toon("#F4EFE6"), duomo, 0, 1.6, 0); const roof = mesh(new THREE.CylinderGeometry(0.01, 2.2, 9, 4, 1), toon("#C8553D"), duomo, 0, 3.6, 0); roof.rotation.z = Math.PI / 2; roof.scale.set(1, 1, 0.6);
    mesh(new THREE.SphereGeometry(1.4, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), toon("#C8553D"), duomo, 1, 4.2, 0); mesh(new THREE.CylinderGeometry(1.4, 1.4, 0.8, 24), toon("#F4EFE6"), duomo, 1, 3.8, 0);
    const bapt = new THREE.Group(); S.add(bapt); bapt.position.set(11, 0, -16);
    mesh(new THREE.CylinderGeometry(2.6, 2.8, 3.2, 28), toon("#F4EFE6"), bapt, 0, 1.6, 0); mesh(new THREE.SphereGeometry(2.4, 24, 12, 0, Math.PI * 2, 0, Math.PI / 2), toon("#C8553D"), bapt, 0, 3.2, 0);
    [[-6, 6], [7, 4], [-8, -4], [9, -6], [-4, 9]].forEach(([x, z]) => { mesh(new THREE.CylinderGeometry(0.15, 0.2, 1.2, 8), toon("#8B5A3C"), S, x, 0.6, z); mesh(new THREE.SphereGeometry(0.9, 12, 8), toon("#4E9A43"), S, x, 1.7, z); });

    // ---- the tower: pivot group (lean) → floors; face on the 3rd floor ----
    const pivot = new THREE.Group(); S.add(pivot);
    const marble = toon("#F3ECDD"), marbleD = toon("#CFC3AC"), shadowArch = toon("#9C8F78");
    const floors = [];
    const FH = 0.92, N = 8;
    for (let i = 0; i < N; i++) {
      const g = new THREE.Group(); pivot.add(g);
      const top = i === N - 1, r = top ? 0.72 : 1.0, h = i === 0 ? 1.25 : top ? 0.8 : FH;
      mesh(new THREE.CylinderGeometry(r * 0.9, r * 0.9, h, 28), shadowArch, g, 0, h / 2, 0);
      if (!top) for (let k = 0; k < 18; k++) { const a = k / 18 * Math.PI * 2; mesh(new THREE.CylinderGeometry(0.05, 0.05, h - 0.12, 6), marble, g, Math.cos(a) * r, h / 2, Math.sin(a) * r); }
      else mesh(new THREE.CylinderGeometry(r, r, h, 28), marble, g, 0, h / 2, 0);
      mesh(new THREE.CylinderGeometry(r + 0.12, r + 0.12, 0.12, 28), marbleD, g, 0, h - 0.06, 0);
      if (i === 0) mesh(new THREE.CylinderGeometry(r + 0.05, r + 0.05, h, 28), marble, g, 0, h / 2, 0);
      g.userData = { h, base: 0 };
      floors.push(g);
    }
    let acc = 0; floors.forEach((g) => { g.userData.base = acc; acc += g.userData.h; });
    // face (diva tower): eyes with lashes, pupils, cheeks, mouth
    const face = new THREE.Group(); floors[0].add(face); face.position.set(0, 0.68, 1.03);
    const white = new THREE.MeshBasicMaterial({ color: 0xffffff }), black = new THREE.MeshBasicMaterial({ color: 0x1b1b2f }), pink = new THREE.MeshBasicMaterial({ color: 0xf28b82 }), red = new THREE.MeshBasicMaterial({ color: 0x8a1f2b });
    const eyes = [-0.28, 0.28].map((x) => { const e = new THREE.Group(); face.add(e); e.position.set(x, 0.12, 0);
      new THREE.Mesh(new THREE.SphereGeometry(0.17, 16, 12), white).position.set(0, 0, 0); e.add(new THREE.Mesh(new THREE.SphereGeometry(0.17, 16, 12), white));
      const p = new THREE.Mesh(new THREE.SphereGeometry(0.085, 12, 8), black); p.position.set(0, -0.01, 0.12); e.add(p);
      for (let k = -1; k <= 1; k++) { const l = new THREE.Mesh(new THREE.BoxGeometry(0.03, 0.12, 0.02), black); l.position.set(k * 0.08 + (x > 0 ? 0.03 : -0.03), 0.2, 0.06); l.rotation.z = -k * 0.4; e.add(l); }
      return e; });
    [-0.46, 0.46].forEach((x) => { const c = new THREE.Mesh(new THREE.CircleGeometry(0.1, 16), pink); c.position.set(x, -0.12, 0.02); face.add(c); });
    const mouthM = new THREE.Mesh(new THREE.SphereGeometry(0.16, 16, 10), red); mouthM.position.set(0, -0.26, 0.02); face.add(mouthM);

    // ghost tower that falls (what would have happened without the pause)
    const ghost = new THREE.Group(); S.add(ghost); const gm = new THREE.MeshBasicMaterial({ color: 0xe63946, transparent: true, opacity: 0.45 });
    let gy = 0; for (let i = 0; i < N; i++) { const h = i === 0 ? 1.25 : i === N - 1 ? 0.8 : FH; const m = new THREE.Mesh(new THREE.CylinderGeometry(i === N - 1 ? 0.72 : 1, i === N - 1 ? 0.72 : 1, h, 20), gm); m.position.y = gy + h / 2; gy += h; ghost.add(m); }
    ghost.visible = false;

    // war banners (Pisa, Genova, Lucca, Firenze) on poles around the tower
    function flagTex(kind) { const c = document.createElement("canvas"); c.width = 128; c.height = 96; const x = c.getContext("2d");
      const W = "#FFFFFF", Rd = "#D62828";
      if (kind === 0) { x.fillStyle = Rd; x.fillRect(0, 0, 128, 96); x.fillStyle = W; x.fillRect(54, 10, 20, 76); x.fillRect(24, 38, 80, 20); }
      if (kind === 1) { x.fillStyle = W; x.fillRect(0, 0, 128, 96); x.fillStyle = Rd; x.fillRect(52, 0, 24, 96); x.fillRect(0, 36, 128, 24); }
      if (kind === 2) { x.fillStyle = W; x.fillRect(0, 0, 128, 48); x.fillStyle = Rd; x.fillRect(0, 48, 128, 48); }
      if (kind === 3) { x.fillStyle = W; x.fillRect(0, 0, 128, 96); x.fillStyle = Rd; x.beginPath(); x.ellipse(64, 40, 12, 26, 0, 0, Math.PI * 2); x.fill(); x.beginPath(); x.ellipse(40, 50, 10, 20, -0.7, 0, Math.PI * 2); x.fill(); x.beginPath(); x.ellipse(88, 50, 10, 20, 0.7, 0, Math.PI * 2); x.fill(); x.fillRect(36, 66, 56, 8); }
      const t = new THREE.CanvasTexture(c); t.encoding = THREE.sRGBEncoding; return t; }
    const flags = [[-5, 3], [5, 3], [-5, -3.5], [5, -3.5]].map(([x, z], k) => { const g = new THREE.Group(); S.add(g); g.position.set(x, 0, z);
      mesh(new THREE.CylinderGeometry(0.06, 0.06, 4, 8), toon("#6B4423"), g, 0, 2, 0);
      const f = mesh(new THREE.PlaneGeometry(1.8, 1.35, 8, 1), new THREE.MeshBasicMaterial({ map: flagTex(k), side: THREE.DoubleSide }), g, 0.95, 3.3, 0); f.castShadow = false;
      g.scale.setScalar(0.001); return { g, f }; });
    // lead weights and extracted soil (on the raised +x side)
    const lead = []; for (let k = 0; k < 6; k++) lead.push(mesh(new THREE.BoxGeometry(0.9, 0.35, 1.6), toon("#5A5F6B"), S, 1.9, 0, 0));
    const dirt = []; for (let k = 0; k < 14; k++) dirt.push(mesh(new THREE.BoxGeometry(0.28, 0.28, 0.28), toon("#8B5A3C"), S, 0, -5, 0));
    // caution ring
    const tape = mesh(new THREE.TorusGeometry(3.2, 0.07, 8, 48), toon("#FFD23F"), S, 0, 0.9, 0); tape.rotation.x = Math.PI / 2; tape.visible = false;
    // tourists pushing the tower (the classic photo)
    const tourists = [[-3.4, 2.4, "#E63946"], [3.6, 2.6, "#2B4C9B"], [-2.4, 3.8, "#FFD23F"], [2.8, 4.0, "#2BB673"]].map(([x, z, c], k) => {
      const g = new THREE.Group(); S.add(g); g.position.set(x, 0, z);
      mesh(new THREE.CapsuleGeometry(0.28, 0.6, 4, 8), toon(c), g, 0, 0.75, 0); mesh(new THREE.SphereGeometry(0.26, 16, 12), toon("#F5C9A0"), g, 0, 1.55, 0);
      const arm = mesh(new THREE.CapsuleGeometry(0.08, 0.6, 4, 6), toon("#F5C9A0"), g, 0, 1.15, 0); arm.userData.k = k;
      g.userData.arm = arm; g.lookAt(0, 0, 0); g.visible = false; return g; });

    // ---------- keys (all anchored to words) ----------
    const CAM = [[0, 1, 0.3, 0.12, 6.5, 1.0], [C.terminaran, 0.8, 0.0, 0.1, 5.5, 0.9], [C.l1, 1.2, -0.45, 0.32, 17, 3.2],
      [C.hundiendo - 0.2, 0.7, 0.15, 0.03, 9.5, 0.8], [C.l3, 0.8, 0.85, 0.55, 22, 2.2], [C.cien, 1.5, 1.45, 0.45, 22, 2.2],
      [C.l4, 0.7, 0.25, 0.04, 10, 0.9], [C.corrido - 0.1, 0.6, -0.2, 0.25, 19, 3.5], [C.l5, 0.8, 0.05, 0.12, 15, 4.6],
      [C.curvita, 0.6, 0.0, 0.1, 13, 4.4], [C.l6, 0.7, 0.55, 0.28, 16, 4], [C.plomo - 0.2, 0.7, 0.9, 0.22, 12, 1.8],
      [C.enderezaron, 0.6, 0.3, 0.18, 14, 3.4], [C.l8, 0.8, 0.12, 0.12, 16, 3.4], [C.derechita - 0.2, 0.6, 0.05, 0.06, 5.2, 0.85]];
    // tilt in degrees (true values on the HUD; drawn 1.6× so it reads on a phone)
    const TILT = [[0, 1, 0], [C.hundiendo, 1.2, 1.6], [C.l5, 1, 3.2], [C.l6, 1.2, 5.5], [C.enderezaron - 0.3, 1.2, 3.97]];
    const BUILD = [0, C.mil, C.mil + 0.5, C.dos, C.pisos, C.pisos + 0.45, C.altos, C.altos + 0.5];  // floor k appears at BUILD[k]

    function setYear(t) {
      let y = 1173;
      if (t >= C.cinco) y = 1178;
      if (t >= C.cien) y = Math.round(lerp(1178, 1272, smooth((t - C.cien) / 2.0)));
      if (t >= C.l5) y = 1272;
      if (t >= C.l6) y = 1990;
      if (t >= C.enderezaron) y = 2001;
      if (t >= C.l8) y = 2026;
      document.getElementById("yr").textContent = String(y);
    }

    function render(t) {
      setYear(t);
      // tower build + lean + curve
      const [tiltDeg] = track(TILT, t), lean = tiltDeg * 1.6 * Math.PI / 180;
      document.getElementById("ang").textContent = tiltDeg.toFixed(tiltDeg > 3.9 && tiltDeg < 4.05 ? 2 : 1) + "°";
      pivot.rotation.z = lean;
      const sinkY = -0.35 * smooth((t - C.hundiendo) / 1.2) + 0.12 * smooth((t - C.tierra) / 1.0);
      pivot.position.y = sinkY;
      const curve = smooth((t - C.altos) / 1.0);
      floors.forEach((g, k) => {
        const a = smooth((t - BUILD[k]) / 0.45), b = back((t - BUILD[k]) / 0.45);
        g.visible = t >= BUILD[k] || k === 0;
        const ck = k >= 3 ? (k - 2) : 0;
        g.position.set(-curve * 0.012 * ck * ck * 0 , g.userData.base + (1 - a) * 3.5, 0);
        g.rotation.z = -curve * 0.035 * ck;
        g.position.x = curve * 0.05 * ck * ck * 0.5;
        g.scale.set(1, k === 0 ? 1 : lerp(0.6, 1, b), 1);
      });
      // face
      const m = mouth(t), bl = ((t + 0.4) % 3.4) < 0.12;
      mouthM.scale.set(1 + m * 0.4, 0.25 + m * 1.3, 0.4);
      eyes.forEach((e, k) => { const wink = k === 1 && t >= C.derechita + 0.35 && t < C.derechita + 1.0; e.scale.y = bl || wink ? 0.12 : 1; });
      // ground see-through while we look at the soil
      const xr = smooth((t - C.hundiendo + 0.3) / 0.5) * (1 - smooth((t - C.corrido + 0.2) / 0.5)) + smooth((t - C.tierra + 0.2) / 0.4) * (1 - smooth((t - C.l8) / 0.5));
      groundMat.opacity = 1 - 0.62 * xr; path.material.opacity = 1 - 0.62 * xr;
      clay.visible = xr > 0.01; rock.visible = xr > 0.01;
      const settle = smooth((t - C.asento) / 0.9);
      clay.scale.set(1, lerp(0.45, 0.3, settle), 1); clay.material.color.set(settle > 0.5 ? "#7A5233" : "#9C6B43");
      // war banners + time passing
      const fT = [C.guerra, C.genova, C.lucca, C.florencia];
      flags.forEach(({ g, f }, k) => { const s = back((t - fT[k]) / 0.4) * (1 - smooth((t - C.l4) / 0.4)); g.scale.setScalar(Math.max(s, 0.001));
        f.rotation.y = Math.sin(t * 3 + k) * 0.25; });
      const days = t >= C.cien && t < C.l4 ? (t - C.cien) * 3.2 : 0;
      sun.position.set(Math.cos(days * Math.PI * 2) * 14, 10 + Math.sin(days * Math.PI * 2) * 8, 10);
      S.background.copy(SKY).lerp(new THREE.Color("#3B4A7A"), t >= C.cien && t < C.l4 ? 0.5 + 0.5 * Math.sin(days * Math.PI * 2 - 1.5) : 0);
      // ghost falls
      const gk = t - C.corrido;
      ghost.visible = gk > 0 && t < C.l5 - 0.1;
      if (ghost.visible) { const fall = smooth((t - C.corrido - 0.5) / 1.0); ghost.rotation.z = lean - fall * 1.45; gm.opacity = 0.6 * (1 - smooth((t - C.caigo - 0.6) / 0.5)); ghost.position.y = sinkY; }
      // tape (closed 1990)
      tape.visible = t >= C.cerraron && t < C.l8; tape.scale.setScalar(back((t - C.cerraron) / 0.4));
      // lead drops one block after another; soil cubes fly out from under the raised side
      lead.forEach((b, k) => { const k0 = C.plomo + k * 0.12, d = smooth((t - k0) / 0.35); b.visible = t >= k0; b.position.y = lerp(9, 0.18 + k * 0.36, d); b.position.x = 1.9; });
      dirt.forEach((d, k) => { const k0 = C.tierra + k * 0.06, u = t - k0; d.visible = u > 0 && u < 1.6;
        if (d.visible) { const vx = 1.5 + rnd(k) * 3, vz = (rnd(k + 9) - 0.5) * 4, vy = 4 + rnd(k + 3) * 3; d.position.set(1.2 + vx * u, -0.6 + vy * u - 4.9 * u * u, vz * u); d.rotation.set(u * 5, u * 3, 0); } });
      // tourists
      tourists.forEach((g, k) => { const k0 = C.poquito + k * 0.15; g.visible = t >= k0; const s = back((t - k0) / 0.4); g.scale.setScalar(Math.max(s, 0.001));
        const arm = g.userData.arm; arm.rotation.x = -Math.PI / 2 + Math.sin(t * 2 + k) * 0.05; arm.position.z = 0.45; });
      const flash = t >= C.quien && ((t - C.quien) % 0.45) < 0.06 && t < C.quien + 1.4;
      hemi.intensity = flash ? 1.3 : 0.5;
      // camera
      const [az, el, dist, ty] = track(CAM, t);
      cam.position.set(Math.sin(az) * Math.cos(el) * dist, ty + Math.sin(el) * dist, Math.cos(az) * Math.cos(el) * dist);
      cam.lookAt(0, ty, 0);
      R.render(S, cam);
    }
    render(0);
    window.addEventListener("hf-seek", (e) => render(e.detail.time));

    const tl = gsap.timeline({ paused: true });
__TW__
    window.__timelines["stage"] = tl;
  </script>
</template>
'''


def index_html():
    sfx = [("build0", "el_build", C["mil"], 1.5, 0.4), ("build1", "el_build", C["dos"] - 0.1, 1.5, 0.35), ("sink", "el_sink", C["hundiendo"], 1.5, 0.45),
           ("war", "el_war", C["guerra"], 2.0, 0.35), ("clock", "el_clock", C["cien"], 2.0, 0.4), ("crash", "el_crash", C["caigo"], 2.0, 0.4),
           ("build2", "el_build", C["pisos"], 1.5, 0.35), ("creak", "el_creak", C["curvita"], 1.2, 0.45), ("alarm", "el_alarm", C["cerraron"], 1.0, 0.35),
           ("thud", "el_thud", C["plomo"] + 0.3, 1.0, 0.45), ("thud2", "el_thud", C["plomo"] + 0.65, 1.0, 0.4), ("camera", "el_camera", C["quien"], 1.0, 0.45),
           ("ding", "el_ding", C["derechita"] + 0.35, 0.6, 0.45),
           ("end", "whoosh", END - 0.05, 0.57, 0.4), ("end-logo", "pop", END + 0.25, 0.72, 0.5), ("end-title", "sparkle", END + 0.55, 1.8, 0.35)]
    rows = [f'      <audio id="sfx-{i}" class="clip" src="assets/sfx/{f}.mp3" data-start="{round(t, 3)}" data-duration="{d}" '
            f'data-track-index="{5 + k % 6}" data-volume="{v}"></audio>' for k, (i, f, t, d, v) in enumerate(sfx)]
    return f'''<!doctype html>
<html lang="es">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=1080, height=1920" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/three@0.149.0/build/three.min.js"></script>
    <style>
      * {{ margin: 0; padding: 0; box-sizing: border-box; }}
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #9FD8F2; }}
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
