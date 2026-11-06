"""EP06: escribe compositions/stage.html (mapa 3D de México en Three.js + subasta) e index.html, con tiempos atados a palabras.

  python -I audio/build_video.py     (después de gen_audio_el.py, build.py y build_geo.py)

Three.js 0.159 (UMD, cargado en index.html) se dibuja SOLO desde el evento hf-seek: cada cuadro es función del tiempo.
Sin temblores: la península se mueve con interpolaciones suaves entre poses clave.
"""
import json
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WORDS = json.loads((ROOT / "transcript.json").read_text(encoding="utf-8"))
LINES = {l["id"]: l for l in json.loads((ROOT / "assets/lines.json").read_text(encoding="utf-8"))}
SHAPES = (ROOT / "assets/geo/mexico_shapes.json").read_text(encoding="utf-8")
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


END = round(LINES["l8"]["end"] + 0.9, 2)
TOTAL = round(END + CARD, 2)
C = {  # cues used by the 3D scene and the overlays
    "sep": W("l1", "separo"), "rep": W("l1", "republica"), "war": W("l2", "castas"), "merida": W("l2", "merida"),
    "offer": W("l3", "soberania"), "us": W("l3", "estados"), "uk": W("l3", "inglaterra"), "es": W("l3", "espana"),
    "ukno": W("l4", "nada"), "esno": W("l4", "nada", 2), "polk": W("l5", "polk"), "usno": W("l5", "aceptaron"),
    "nobody": W("l6", "nadie"), "back": W("l7", "volvio"), "aug": W("l7", "agosto"), "sold": W("l8", "vendida"),
    "l1": L("l1"), "l3": L("l3"), "l7": L("l7"), "end": END,
}

FLAGS = {
    "us": '<rect width="60" height="40" fill="#B22234"/>' + "".join(
        f'<rect y="{i * 40 / 13:.2f}" width="60" height="{40 / 13:.2f}" fill="#FFFFFF"/>' for i in range(1, 13, 2)) +
          '<rect width="26" height="21.5" fill="#3C3B6E"/>' + "".join(
        f'<circle cx="{4 + (i % 4) * 6}" cy="{4 + (i // 4) * 6}" r="1.4" fill="#FFF"/>' for i in range(12)),
    "uk": '<rect width="60" height="40" fill="#012169"/><path d="M0 0L60 40M60 0L0 40" stroke="#FFF" stroke-width="8"/>'
          '<path d="M0 0L60 40M60 0L0 40" stroke="#C8102E" stroke-width="3"/><path d="M30 0V40M0 20H60" stroke="#FFF" stroke-width="12"/>'
          '<path d="M30 0V40M0 20H60" stroke="#C8102E" stroke-width="7"/>',
    "es": '<rect width="60" height="40" fill="#AA151B"/><rect y="10" width="60" height="20" fill="#F1BF00"/>',
}
BIDDERS = [("us", "EE. UU."), ("uk", "INGLATERRA"), ("es", "ESPAÑA")]


def stage_html():
    cards = "\n".join(
        f'      <div id="bd-{k}" class="bd"><svg viewBox="0 0 60 40" class="flag">{FLAGS[k]}</svg><b>{name}</b>'
        f'<div id="no-{k}" class="no">NO</div></div>' for k, name in BIDDERS)
    tw = [
        f'tl.fromTo("#hdr", {{ y: 0 }}, {{ y: -420, duration: 0.3, ease: "power3.in" }}, {C["l1"] - 0.1});',
        f'tl.fromTo("#tag", {{ opacity: 1 }}, {{ opacity: 0, duration: 0.2 }}, {C["l1"] - 0.1});',
        f'tl.fromTo("#chip-rep", {{ opacity: 0, y: -30 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(2)" }}, {C["rep"]});',
        f'tl.to("#chip-rep", {{ opacity: 0, duration: 0.2 }}, {C["war"] - 0.2});',
        f'tl.fromTo("#chip-war", {{ opacity: 0, y: -30 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(2)" }}, {C["war"]});',
        f'tl.fromTo("#merida", {{ opacity: 0, scale: 0.4 }}, {{ opacity: 1, scale: 1, duration: 0.3, ease: "back.out(2)" }}, {C["merida"]});',
        f'tl.to(["#chip-war", "#merida"], {{ opacity: 0, duration: 0.2 }}, {C["l3"] - 0.1});',
        f'tl.fromTo("#tag", {{ opacity: 0, scale: 0.5 }}, {{ opacity: 1, scale: 1, duration: 0.35, ease: "back.out(2)", immediateRender: false }}, {C["offer"]});',
        f'tl.fromTo("#bd-us", {{ opacity: 0, y: -60 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(2)" }}, {C["us"]});',
        f'tl.fromTo("#bd-uk", {{ opacity: 0, y: -60 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(2)" }}, {C["uk"]});',
        f'tl.fromTo("#bd-es", {{ opacity: 0, y: -60 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(2)" }}, {C["es"]});',
        f'tl.fromTo("#no-uk", {{ opacity: 0, scale: 2.5, rotation: 20 }}, {{ opacity: 1, scale: 1, rotation: -12, duration: 0.2, ease: "power4.in" }}, {C["ukno"]});',
        f'tl.fromTo("#no-es", {{ opacity: 0, scale: 2.5, rotation: 20 }}, {{ opacity: 1, scale: 1, rotation: -12, duration: 0.2, ease: "power4.in" }}, {C["esno"]});',
        f'tl.fromTo("#chip-polk", {{ opacity: 0, y: -30 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(2)" }}, {C["polk"]});',
        f'tl.fromTo("#no-us", {{ opacity: 0, scale: 2.5, rotation: 20 }}, {{ opacity: 1, scale: 1, rotation: -12, duration: 0.2, ease: "power4.in" }}, {C["usno"]});',
        f'tl.to("#chip-polk", {{ opacity: 0, duration: 0.2 }}, {C["nobody"]});',
        f'tl.to("#tag", {{ opacity: 0, duration: 0.2 }}, {C["back"] - 0.1});',
        f'tl.fromTo("#chip-aug", {{ opacity: 0, y: -30 }}, {{ opacity: 1, y: 0, duration: 0.3, ease: "back.out(2)" }}, {C["aug"]});',
        f'tl.to(["#bd-us", "#bd-uk", "#bd-es"], {{ opacity: 0, duration: 0.3 }}, {C["sold"] - 0.3});',
        f'tl.fromTo("#sold span", {{ opacity: 0, scale: 3, rotation: 20 }}, {{ opacity: 1, scale: 1, rotation: -8, duration: 0.22, ease: "power4.in" }}, {C["sold"]});',
    ]
    return f'''<template>
  <style>
    #root {{ position: absolute; inset: 0; overflow: hidden; background: #0B4F6C; font-family: "Archivo Black", sans-serif; }}
    #gl {{ position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }}
    .tags {{ position: absolute; left: 0; width: 1080px; text-align: center; }}
    .tags span {{ display: inline-block; font-size: 92px; line-height: 1; padding: 14px 30px 10px; color: #1B1B2F;
      border: 8px solid #1B1B2F; border-radius: 18px; box-shadow: 8px 8px 0 #1B1B2F; }}
    #hdr {{ position: absolute; left: 0; top: 0; width: 1080px; height: 360px; }}
    #h1 {{ top: 70px; }} #h1 span {{ background: #FFFFFF; }}
    #h2 {{ top: 198px; }} #h2 span {{ background: #FFD23F; }}
    #tag {{ position: absolute; left: 0; top: 0; width: 330px; margin-left: -165px; text-align: center; transform-origin: 50% 100%; }}
    #tag span {{ display: inline-block; font-size: 54px; padding: 10px 22px 6px; background: #E63946; color: #FFFFFF;
      border: 7px solid #1B1B2F; border-radius: 14px; box-shadow: 7px 7px 0 #1B1B2F; transform: rotate(-6deg); }}
    #bids {{ position: absolute; left: 40px; top: 110px; width: 1000px; display: flex; justify-content: space-between; }}
    .bd {{ position: relative; width: 300px; padding: 16px 10px 12px; background: #FFFDF6; border: 7px solid #1B1B2F; border-radius: 18px;
      box-shadow: 7px 7px 0 #1B1B2F; text-align: center; opacity: 0; }}
    .bd .flag {{ width: 180px; height: 120px; display: block; margin: 0 auto 8px; border: 4px solid #1B1B2F; }}
    .bd b {{ font-weight: 400; font-size: 38px; color: #1B1B2F; }}
    .no {{ position: absolute; left: 50%; top: 26px; margin-left: -85px; width: 170px; font-size: 70px; line-height: 1; color: #E63946;
      border: 9px solid #E63946; border-radius: 16px; background: rgba(255,253,246,0.88); opacity: 0; }}
    .chip {{ position: absolute; left: 0; width: 1080px; top: 1360px; text-align: center; opacity: 0; }}
    .chip span {{ display: inline-block; font-size: 46px; padding: 12px 24px 8px; background: #FFD23F; color: #1B1B2F;
      border: 7px solid #1B1B2F; border-radius: 14px; box-shadow: 7px 7px 0 #1B1B2F; }}
    #chip-war span {{ background: #E63946; color: #FFFFFF; }}
    #chip-polk {{ top: 420px; }} #chip-polk span {{ background: #FFFFFF; font-size: 40px; }}
    #merida {{ position: absolute; left: 0; top: 0; width: 240px; margin-left: -120px; text-align: center; opacity: 0; }}
    #merida span {{ display: inline-block; font-size: 40px; padding: 6px 16px 4px; background: #FFFFFF; color: #1B1B2F;
      border: 6px solid #1B1B2F; border-radius: 12px; }}
    #sold {{ position: absolute; left: 0; top: 330px; width: 1080px; text-align: center; }}
    #sold span {{ display: inline-block; font-size: 120px; color: #2BB673; border: 14px solid #2BB673; border-radius: 22px; padding: 10px 34px 4px;
      background: rgba(255,253,246,0.92); opacity: 0; }}
  </style>
  <div id="root" data-composition-id="stage" data-width="1080" data-height="1920">
    <canvas id="gl" width="1080" height="1920"></canvas>
    <div id="tag"><span>SE VENDE</span></div>
    <div id="merida"><span>📍 Mérida</span></div>
    <div id="bids">
{cards}
    </div>
    <div id="chip-rep" class="chip"><span>REPÚBLICA DE YUCATÁN · 1841</span></div>
    <div id="chip-war" class="chip"><span>GUERRA DE CASTAS · 1847</span></div>
    <div id="chip-polk" class="chip"><span>Presidente Polk → Congreso de EE. UU., 1848</span></div>
    <div id="chip-aug" class="chip"><span>17 AGO 1848: VUELVE A MÉXICO</span></div>
    <div id="sold"><span>¡VENDIDA!</span></div>
    <div id="hdr">
      <div id="h1" class="tags"><span>¿QUIÉN DA MÁS</span></div>
      <div id="h2" class="tags"><span>POR YUCATÁN?</span></div>
    </div>
  </div>
  <script>
    const C = {json.dumps(C)};
    const GEO = {SHAPES};
    const lerp = (a, b, k) => a + (b - a) * k;
    const smooth = (k) => (k <= 0 ? 0 : k >= 1 ? 1 : k * k * (3 - 2 * k));
    const backOut = (k) => {{ const s = 1.4; k = Math.min(Math.max(k, 0), 1) - 1; return k * k * ((s + 1) * k + s) + 1; }};

    // ---- poses: [time, values...] ; each key eases in over `dur` seconds from the previous pose ----
    function track(keys, t, dur, ease) {{
      let i = 0;
      while (i + 1 < keys.length && t >= keys[i + 1][0]) i++;
      const cur = keys[i];
      if (i === 0) return cur.slice(1);
      const k = (ease || smooth)((t - cur[0]) / dur), prev = keys[i - 1];
      return cur.slice(1).map((v, j) => lerp(prev[j + 1], v, k));
    }}
    //        t           dx    dy    z     tilt  roll
    const PEN = [[0, 0, 0, 0, 0, 0], [C.sep, 0.9, 0.35, 0, 0, 0], [C.offer, 0.9, 0.35, 3.2, -0.25, 0.06],
      [C.nobody, 0.9, 0.35, 2.1, -0.1, 0.16], [C.back, 0, 0, 0, 0, 0]];
    //          t        x     y     dist  height
    // [t, x, y, dist, height, lookZ] — peninsula ≈ x 9..13, y -6..-2.5; the whole south-east ≈ x 0..13
    const CAM = [[0, 11.0, -4.2, 14, 12, 0.5], [C.l1, 6.5, -3.0, 30, 24, 0], [C.war, 11.0, -4.0, 15, 12, 0.5],
      [C.l3, 11.2, -3.8, 19, 15, 1.6], [C.nobody, 11.0, -4.0, 18, 14, 1.2], [C.l7, 6.5, -3.0, 30, 24, 0], [C.sold, 11.0, -4.2, 15, 12, 0.5]];

    const canvas = document.getElementById("gl");
    const renderer = new THREE.WebGLRenderer({{ canvas, antialias: true, preserveDrawingBuffer: true }});
    renderer.setPixelRatio(1);
    renderer.setSize(1080, 1920, false);
    const scene = new THREE.Scene();
    scene.background = new THREE.Color("#0B4F6C");
    const camera = new THREE.PerspectiveCamera(38, 1080 / 1920, 0.1, 200);
    scene.add(new THREE.HemisphereLight("#FFF6E5", "#0B4F6C", 1.1));
    const key = new THREE.DirectionalLight("#FFE2B8", 1.6); key.position.set(-8, -12, 20); scene.add(key);
    const rim = new THREE.DirectionalLight("#9AD7FF", 0.6); rim.position.set(12, 14, 8); scene.add(rim);

    const sea = new THREE.Mesh(new THREE.PlaneGeometry(120, 120), new THREE.MeshStandardMaterial({{ color: "#13708F", roughness: 0.9 }}));
    sea.position.z = -0.05; scene.add(sea);
    const gridPts = [];
    for (let v = -40; v <= 40; v += 2.5) {{ gridPts.push(-60, v, 0, 60, v, 0, v, -60, 0, v, 60, 0); }}
    const grid = new THREE.LineSegments(new THREE.BufferGeometry().setAttribute("position", new THREE.Float32BufferAttribute(gridPts, 3)),
      new THREE.LineBasicMaterial({{ color: "#2D8FB0", transparent: true, opacity: 0.55 }}));
    grid.position.z = -0.03; scene.add(grid);

    function landGroup(rings, color, depth) {{
      const g = new THREE.Group();
      const mat = new THREE.MeshStandardMaterial({{ color, roughness: 0.75 }});
      const edge = new THREE.LineBasicMaterial({{ color: "#1B1B2F" }});
      for (const r of rings) {{
        const shape = new THREE.Shape(r.map((p) => new THREE.Vector2(p[0], p[1])));
        const geo = new THREE.ExtrudeGeometry(shape, {{ depth, bevelEnabled: false }});
        g.add(new THREE.Mesh(geo, mat));
        const top = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(r.map((p) => new THREE.Vector3(p[0], p[1], depth + 0.01))), edge);
        g.add(top);
      }}
      g.userData.mat = mat;
      return g;
    }}
    const mex = landGroup(GEO.mex, "#E8D3A9", 0.45); scene.add(mex);
    // the peninsula lives in a pivot at its centroid so it can lift and tilt in place
    const penPts = GEO.pen.flat();
    const pc = penPts.reduce((a, p) => [a[0] + p[0] / penPts.length, a[1] + p[1] / penPts.length], [0, 0]);
    const pivot = new THREE.Group(); pivot.position.set(pc[0], pc[1], 0); scene.add(pivot);
    const pen = landGroup(GEO.pen, "#F2A541", 0.55); pen.position.set(-pc[0], -pc[1], 0); pivot.add(pen);
    const shadow = new THREE.Mesh(new THREE.CircleGeometry(2.4, 40), new THREE.MeshBasicMaterial({{ color: "#062F40", transparent: true, opacity: 0 }}));
    shadow.position.set(pc[0], pc[1], 0.02); shadow.scale.set(1.25, 0.8, 1); scene.add(shadow);
    const K = Math.cos(23.5 * Math.PI / 180);
    const MERIDA = new THREE.Vector3((-89.62 + 102) * K, 20.97 - 23.5, 0.6);
    const GOLD = new THREE.Color("#F2A541"), RED = new THREE.Color("#E63946");

    function toScreen(v) {{
      const p = v.clone().project(camera);
      return [(p.x + 1) / 2 * 1080, (1 - p.y) / 2 * 1920];
    }}
    function place(id, v, dy) {{
      const [x, y] = toScreen(v);
      const el = document.getElementById(id);
      el.style.left = Math.min(Math.max(x, 190), 890) + "px"; el.style.top = (y + dy) + "px";  // keep tags inside the frame
    }}

    function render(t) {{
      const [dx, dy, z, tilt, roll] = track(PEN, t, 0.8, (k) => (t >= C.back ? backOut(k) : smooth(k)));
      pivot.position.set(pc[0] + dx, pc[1] + dy, z);
      pivot.rotation.set(tilt, 0, roll);
      shadow.position.set(pc[0] + dx, pc[1] + dy, 0.02);
      shadow.material.opacity = Math.min(z / 3.2, 1) * 0.3;
      const war = t >= C.war && t < C.l3 ? Math.sin(Math.min((t - C.war) / 0.4, 1) * Math.PI / 2) : (t >= C.l3 && t < C.l3 + 0.4 ? 1 - (t - C.l3) / 0.4 : 0);
      pen.userData.mat.color.copy(GOLD).lerp(RED, war * 0.85);
      const [cx, cy, dist, h, lz] = track(CAM, t, 1.0);
      camera.position.set(cx, cy - dist, h);
      camera.up.set(0, 0, 1);
      camera.lookAt(cx, cy, lz);
      camera.updateMatrixWorld();
      renderer.render(scene, camera);
      place("tag", new THREE.Vector3(pc[0] + dx, pc[1] + dy + 0.8, z + 1.0), -120);
      place("merida", MERIDA, -80);
    }}

    window.__hf = window.__hf || {{}};
    window.__hf.buildReady = window.__hf.buildReady || {{}};
    window.__hf.buildReady["map3d"] = (async () => {{
      await renderer.compileAsync(scene, camera);
      render(0);
    }})();
    window.addEventListener("hf-seek", (e) => render(e.detail.time));

    const tl = gsap.timeline({{ paused: true }});
    {chr(10).join("    " + x for x in tw).strip()}
    window.__timelines["stage"] = tl;
  </script>
</template>
'''


def index_html():
    sfx = [("gavel0", "el_gavel", 0.15, 1.0, 0.5), ("sep", "el_rumble", C["sep"], 1.5, 0.45), ("war", "impact-bass-1", C["war"], 2.1, 0.4),
           ("lift", "el_rumble", C["offer"], 1.5, 0.5), ("us", "pop", C["us"], 0.72, 0.45), ("uk", "pop", C["uk"], 0.72, 0.45),
           ("es", "pop", C["es"], 0.72, 0.45), ("ukno", "el_buzzer", C["ukno"], 1.0, 0.4), ("esno", "el_buzzer", C["esno"], 1.0, 0.4),
           ("roll", "el_drumroll", C["polk"], 2.0, 0.35), ("usno", "el_buzzer", C["usno"], 1.0, 0.45),
           ("laugh", "el_crowd_laugh", C["nobody"], 1.8, 0.35), ("back", "whoosh", C["back"], 0.57, 0.4),
           ("sold", "el_gavel", C["sold"], 1.0, 0.6), ("end", "whoosh", END - 0.05, 0.57, 0.4),
           ("end-logo", "pop", END + 0.25, 0.72, 0.5), ("end-title", "sparkle", END + 0.55, 1.8, 0.35)]
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
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #0B4F6C; }}
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
