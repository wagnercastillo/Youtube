"""EP13: escribe compositions/stage.html (Victor Lustig vende la Torre Eiffel; motion graphics + tipografía cinética) e index.html.

  python -I audio/build_video.py     (después de gen_audio_el.py y build.py)

Todo es HTML/SVG animado con GSAP (sin canvas). Estética art déco 1925 (azul noche, crema, oro, rojo). Doctrina de movimiento
(motion-doctrine): una sola corriente (todo corte sale a la IZQUIERDA y entra desde la derecha a media velocidad, sin
crossfade), la Torre Eiffel como hilo conductor (se dibuja en el gancho, vive en el periódico y vuelve al final para el bucle),
causa → efecto (sellos que impactan, billetes que vuelan al montón), pausa antes del clímax en "es secreto", sin balanceo idle.
Cada entrada está anclada a una palabra con W().
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
    "vendio": W("l0", "vendio"), "intento": W("l0", "intento"), "eiffel": W("l0", "eiffel"), "otra0": W("l0", "otra"),
    "l1": L("l1"), "paris": W("l1", "paris"), "mil": W("l1", "mil"), "victor": W("l1", "victor"), "periodico": W("l1", "periodico"), "carisimo": W("l1", "carisimo"),
    "l2": L("l2"), "funcionario": W("l2", "funcionario"), "chatarreros": W("l2", "chatarreros"), "hotel": W("l2", "hotel"),
    "l3": L("l3"), "secreto": W("l3", "secreto"), "vender": W("l3", "vender"), "chatarra": W("l3", "chatarra"),
    "l4": L("l4"), "andre": W("l4", "andre"), "fortuna": W("l4", "fortuna"), "soborno": W("l4", "soborno"),
    "l5": L("l5"), "huye": W("l5", "huye"), "verguenza": W("l5", "verguenza"), "denuncia": W("l5", "denuncia"),
    "l6": L("l6"), "regresa": W("l6", "regresa"), "otra": W("l6", "otra"), "denuncian": W("l6", "denuncian"), "escapa": W("l6", "escapa"),
    "l7": L("l7"), "billetes": W("l7", "billetes"), "alcatraz": W("l7", "alcatraz"),
    "l8": L("l8"), "torre": W("l8", "torre"), "suya": W("l8", "suya"), "end": END,
}

TOWER = ('<svg viewBox="0 0 200 400" class="tw"><path pathLength="1" d="M100 8 L107 60 L113 140 L130 222 L151 302 L184 392 L140 392 '
         'Q100 322 60 392 L16 392 L49 302 L70 222 L87 140 L93 60 Z M86 140 H114 M68 222 H132 M47 302 H153 M93 60 H107 '
         'M87 140 L113 222 M113 140 L87 222 M70 222 L130 302 M130 222 L70 302 M100 8 V0"/></svg>')
MAN = ('<svg viewBox="0 0 200 300" class="man"><path d="M60 300 Q60 170 100 160 Q140 170 140 300 Z" fill="#F5E6C8"/>'
       '<circle cx="100" cy="120" r="38" fill="#F5E6C8"/><rect x="58" y="70" width="84" height="16" rx="8" fill="#D4A73C"/>'
       '<path d="M70 72 Q72 34 100 34 Q128 34 130 72 Z" fill="#D4A73C"/><path d="M82 130 Q100 122 118 130" stroke="#14213D" stroke-width="7" fill="none" stroke-linecap="round"/>'
       '<rect x="66" y="80" width="68" height="7" fill="#C8102E"/></svg>')
TOPHAT = ('<svg viewBox="0 0 120 200" class="th"><path d="M30 200 Q30 120 60 112 Q90 120 90 200 Z" fill="#F5E6C8"/><circle cx="60" cy="86" r="26" fill="#F5E6C8"/>'
          '<rect x="30" y="54" width="60" height="10" fill="#D4A73C"/><rect x="40" y="14" width="40" height="44" fill="#D4A73C"/></svg>')
RUNNER = ('<svg viewBox="0 0 220 260" class="run"><circle cx="128" cy="44" r="26" fill="#F5E6C8"/><rect x="96" y="12" width="66" height="10" rx="5" fill="#D4A73C"/>'
          '<path d="M108 14 Q110 -6 130 -6 Q150 -6 152 14 Z" fill="#D4A73C"/><path d="M118 74 L96 150" stroke="#F5E6C8" stroke-width="30" stroke-linecap="round"/>'
          '<path d="M96 150 L50 196 L20 190 M96 150 L130 210 L110 250" stroke="#F5E6C8" stroke-width="20" fill="none" stroke-linecap="round" stroke-linejoin="round"/>'
          '<path d="M112 90 L60 110 M112 90 L170 80" stroke="#F5E6C8" stroke-width="16" stroke-linecap="round"/><rect x="160" y="62" width="50" height="38" rx="6" fill="#D4A73C"/></svg>')
BILL = '<div class="bill"><b>₣</b><span>1000</span><b>₣</b></div>'
SHIP = ('<svg viewBox="0 0 320 180" class="ship"><path d="M10 110 H310 L270 170 H50 Z" fill="#F5E6C8"/><rect x="80" y="70" width="160" height="40" fill="#F5E6C8"/>'
        '<rect x="120" y="20" width="34" height="52" fill="#C8102E"/><rect x="176" y="20" width="34" height="52" fill="#C8102E"/>'
        '<circle cx="110" cy="90" r="8" fill="#14213D"/><circle cx="160" cy="90" r="8" fill="#14213D"/><circle cx="210" cy="90" r="8" fill="#14213D"/></svg>')
ISLAND = ('<svg viewBox="0 0 600 300" class="isl"><path d="M0 250 Q80 150 200 170 Q300 120 420 160 Q540 150 600 250 Z" fill="#D4A73C"/>'
          '<rect x="180" y="100" width="240" height="80" fill="#F5E6C8"/><rect x="200" y="120" width="20" height="30" fill="#14213D"/><rect x="240" y="120" width="20" height="30" fill="#14213D"/>'
          '<rect x="280" y="120" width="20" height="30" fill="#14213D"/><rect x="320" y="120" width="20" height="30" fill="#14213D"/><rect x="360" y="120" width="20" height="30" fill="#14213D"/>'
          '<rect x="440" y="40" width="26" height="130" fill="#F5E6C8"/><path d="M432 40 H474 L453 14 Z" fill="#C8102E"/></svg>')
CUFFS = ('<svg viewBox="0 0 240 120" class="cuffs"><circle cx="60" cy="60" r="44" fill="none" stroke="#B9C2CF" stroke-width="16"/>'
         '<circle cx="180" cy="60" r="44" fill="none" stroke="#B9C2CF" stroke-width="16"/><path d="M104 60 H136" stroke="#B9C2CF" stroke-width="10" stroke-dasharray="8 6"/></svg>')
GLASSES = ('<svg viewBox="0 0 200 200" class="gls"><path d="M40 20 H90 L80 90 Q65 110 50 90 Z M65 100 V170 M45 172 H85" stroke="#D4A73C" stroke-width="8" fill="#F5E6C8"/>'
           '<path d="M110 20 H160 L150 90 Q135 110 120 90 Z M135 100 V170 M115 172 H155" stroke="#D4A73C" stroke-width="8" fill="#F5E6C8"/></svg>')

BEATS = f'''
    <section id="B0" class="beat">
      <div id="k0a" class="kt sm" style="top:300px">ESTE HOMBRE VENDIÓ</div>
      <div id="k0b" class="kt big gold" style="top:390px">LA TORRE EIFFEL</div>
      <div id="t0" style="position:absolute;left:330px;top:600px;width:420px;height:840px">{TOWER}</div>
      <div id="s0a" class="stamp" style="left:250px;top:930px">VENDIDA</div>
      <div id="s0b" class="stamp red" style="left:120px;top:1230px">¡Y OTRA VEZ!</div>
    </section>
    <section id="B1" class="beat">
      <div id="k1a" class="kt huge" style="top:330px">PARÍS</div>
      <div id="k1b" class="kt huge gold" style="top:500px">1925</div>
      <div id="np" class="paper" style="left:110px;top:720px">
        <div class="mast">LE JOURNAL</div>
        <div class="np-row"><div id="t1" class="np-tower">{TOWER}</div>
          <div id="k1c" class="np-head">¡MANTENER LA TORRE CUESTA CARÍSIMO!</div></div>
      </div>
      <div id="lus" style="position:absolute;left:660px;top:1040px;width:280px;height:390px">{MAN}</div>
      <div id="k1d" class="tag" style="left:90px;top:1150px">VICTOR LUSTIG<small>ESTAFADOR</small></div>
    </section>
    <section id="B2" class="beat">
      <div id="badge" class="badge" style="left:120px;top:360px"><small>MINISTERIO DE CORREOS Y TELÉGRAFOS</small>SUBDIRECTOR GENERAL<em>V. LUSTIG</em></div>
      <div id="s2" class="stamp red sm" style="left:640px;top:600px">FALSO</div>
      <div id="k2a" class="kt mid" style="top:770px">CITA A 5 CHATARREROS</div>
      {''.join(f'<div id="th{k}" class="thw" style="left:{110 + k * 180}px;top:880px">{TOPHAT}</div>' for k in range(5))}
      <div id="k2b" class="kt mid gold" style="top:1180px">EN UN HOTEL DE LUJO</div>
      <div id="gl" style="position:absolute;left:440px;top:1260px;width:200px;height:200px">{GLASSES}</div>
    </section>
    <section id="B3" class="beat">
      <div id="k3a" class="kt huge dim" style="top:420px">SHHH…</div>
      <div id="k3b" class="kt mid" style="top:700px">EL GOBIERNO VA A VENDER</div>
      <div id="k3c" class="kt mid" style="top:800px">LA TORRE…</div>
      <div id="k3d" class="kt big red" style="top:960px">¡COMO CHATARRA!</div>
      <div id="t3" style="position:absolute;left:400px;top:1110px;width:200px;height:400px">{TOWER}</div>
      <div id="tag3" class="price" style="left:600px;top:1180px">CHATARRA</div>
    </section>
    <section id="B4" class="beat">
      <div id="k4a" class="tag" style="left:90px;top:380px">ANDRÉ POISSON<small>CHATARRERO</small></div>
      <div id="po" class="thw" style="left:700px;top:330px;width:240px;height:400px">{TOPHAT}</div>
      <div id="k4b" class="kt big gold" style="top:800px">UNA FORTUNA</div>
      {''.join(f'<div id="bl{k}" class="billw" style="left:{300 + (k % 2) * 30}px;top:{1180 - k * 34}px">{BILL}</div>' for k in range(6))}
      <div id="s4" class="stamp red" style="left:560px;top:1150px">+ SOBORNO</div>
    </section>
    <section id="B5" class="beat">
      <div id="k5a" class="kt big" style="top:380px">LUSTIG HUYE</div>
      <div id="rn" style="position:absolute;left:420px;top:560px;width:300px;height:360px">{RUNNER}</div>
      <div id="k5b" class="kt big red" style="top:980px">VERGÜENZA</div>
      <div id="k5c" class="kt mid" style="top:1150px">POISSON NI LO DENUNCIA</div>
      <div id="x5" class="strike" style="left:150px;top:1196px"></div>
    </section>
    <section id="B6" class="beat">
      <div id="k6a" class="kt huge gold" style="top:360px">¡REGRESA!</div>
      <div id="k6b" class="kt mid" style="top:600px">A VENDERLA… OTRA VEZ</div>
      <div id="s6" class="stamp red" style="left:200px;top:760px">DENUNCIADO</div>
      <div id="sh" style="position:absolute;left:380px;top:1020px;width:320px;height:180px">{SHIP}</div>
      <div id="k6c" class="kt mid gold" style="top:1230px">ESCAPA A EE. UU.</div>
    </section>
    <section id="B7" class="beat">
      <div id="k7a" class="kt big" style="top:380px">BILLETES FALSOS</div>
      {''.join(f'<div id="fb{k}" class="billw usd" style="left:{180 + k * 150}px;top:{560 + (k % 2) * 40}px"><div class="bill"><b>$</b><span>100</span><b>$</b></div></div>' for k in range(4))}
      <div id="cf" style="position:absolute;left:420px;top:800px;width:240px;height:120px">{CUFFS}</div>
      <div id="isl" style="position:absolute;left:240px;top:980px;width:600px;height:300px">{ISLAND}</div>
      <div id="k7b" class="kt huge gold" style="top:1260px">ALCATRAZ</div>
      <div id="bars" class="bars"></div>
    </section>
    <section id="B8" class="beat">
      <div id="k8a" class="kt sm" style="top:300px">SI TE VENDEN</div>
      <div id="k8b" class="kt big gold" style="top:390px;font-size:82px">LA TORRE EIFFEL…</div>
      <div id="t8" style="position:absolute;left:330px;top:600px;width:420px;height:840px">{TOWER}</div>
      <div id="s8" class="stamp red" style="left:200px;top:1000px">¿ES SUYA?</div>
    </section>
'''

SEAMS = ["l1", "l2", "l3", "l4", "l5", "l6", "l7", "l8"]  # beat k+1 enters at L(seam)


def tweens():
    t = []
    a = t.append
    cut = [0] + [C[s] - 0.05 for s in SEAMS]
    for k in range(1, 9):
        a(f'tl.set("#B{k}", {{ x: 1200 }}, 0);')
    for k, c in enumerate(cut[1:], start=1):  # exit LEFT with power3.in, the next beat picks up mid-flight with power3.out
        a(f'tl.to("#B{k - 1}", {{ x: -1200, duration: 0.3, ease: "power3.in" }}, {round(c - 0.3, 3)});')
        a(f'tl.fromTo("#B{k}", {{ x: 620 }}, {{ x: 0, duration: 0.5, ease: "power3.out", immediateRender: false }}, {round(c, 3)});')
        a(f'tl.to("#rays", {{ rotation: {k * 9}, duration: 0.8, ease: "power3.out" }}, {round(c - 0.3, 3)});')

    def wipe(sel, at, dx=90, dur=0.45):
        a(f'tl.fromTo("{sel}", {{ clipPath: "inset(-30px 100% -30px -30px)", x: {dx} }}, {{ clipPath: "inset(-30px -30px -30px -30px)", x: 0, duration: {dur}, ease: "power4.out" }}, {round(at, 3)});')

    def stamp(sel, at):
        a(f'tl.fromTo("{sel}", {{ scale: 2.4, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.2, ease: "power4.in" }}, {round(at, 3)});')

    def pop(sel, at, dur=0.4):
        a(f'tl.fromTo("{sel}", {{ scale: 0, y: 40 }}, {{ scale: 1, y: 0, duration: {dur}, ease: "back.out(1.6)" }}, {round(at, 3)});')

    def draw(sel, at, dur=1.0):
        a(f'tl.fromTo("{sel} path", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: {dur}, ease: "power2.inOut" }}, {round(at, 3)});')

    # B0 hook (text on screen from frame 0)
    wipe("#k0a", 0.03); wipe("#k0b", 0.16); a('tl.fromTo("#t0 path", { strokeDashoffset: 1 }, { strokeDashoffset: 0, duration: 0.9, ease: "power2.out" }, 0);'); stamp("#s0a", C["eiffel"] + 0.35); stamp("#s0b", C["intento"])
    # B1
    wipe("#k1a", C["paris"]); wipe("#k1b", C["mil"]); pop("#lus", C["victor"]); wipe("#k1d", C["victor"] + 0.15)
    a(f'tl.fromTo("#np", {{ x: 700, rotation: 8 }}, {{ x: 0, rotation: -2, duration: 0.5, ease: "power3.out" }}, {C["periodico"]});')
    draw("#t1", C["periodico"] + 0.2, 0.8); wipe("#k1c", C["carisimo"] - 0.4, 40, 0.7)
    # B2
    a(f'tl.fromTo("#badge", {{ x: 700, rotation: 6 }}, {{ x: 0, rotation: -3, duration: 0.5, ease: "power3.out" }}, {C["funcionario"]});')
    stamp("#s2", C["funcionario"] + 0.9); wipe("#k2a", C["chatarreros"] - 0.2)
    for k in range(5):
        pop(f"#th{k}", C["chatarreros"] + 0.08 * k, 0.35)
    wipe("#k2b", C["hotel"]); pop("#gl", C["hotel"] + 0.2)
    # B3 — stillness before the climax: the screen dims on "secreto", then the sale lands
    a(f'tl.fromTo("#dim", {{ opacity: 0 }}, {{ opacity: 0.55, duration: 0.3 }}, {C["secreto"]});')
    a(f'tl.to("#dim", {{ opacity: 0, duration: 0.25 }}, {round(C["chatarra"] - 0.1, 3)});')
    wipe("#k3a", C["secreto"]); wipe("#k3b", C["vender"] - 0.3); wipe("#k3c", C["vender"] + 0.3)
    stamp("#k3d", C["chatarra"]); draw("#t3", C["l3"] + 0.2, 0.9)
    a(f'tl.fromTo("#tag3", {{ rotation: -60, transformOrigin: "0% 0%", opacity: 0 }}, {{ rotation: 12, opacity: 1, duration: 0.5, ease: "back.out(1.5)" }}, {round(C["vender"] + 0.4, 3)});')
    # B4 — money flies in from the right and stacks (cause → effect)
    wipe("#k4a", C["l4"] + 0.05); pop("#po", C["l4"] + 0.15); wipe("#k4b", C["fortuna"])
    for k in range(6):
        a(f'tl.fromTo("#bl{k}", {{ x: 900, rotation: 25, opacity: 0 }}, {{ x: 0, rotation: {(-1) ** k * 4}, opacity: 1, duration: 0.35, ease: "power3.out" }}, {round(C["fortuna"] + 0.25 + k * 0.08, 3)});')
    stamp("#s4", C["soborno"])
    # B5 — Lustig runs out LEFT (the current), shame, the complaint gets struck out
    wipe("#k5a", C["huye"] - 0.2)
    a(f'tl.fromTo("#rn", {{ x: 0 }}, {{ x: -1000, duration: 0.9, ease: "power2.in" }}, {round(C["huye"] + 0.2, 3)});')
    stamp("#k5b", C["verguenza"]); wipe("#k5c", C["denuncia"] - 0.5)
    a(f'tl.fromTo("#x5", {{ scaleX: 0, transformOrigin: "0% 50%" }}, {{ scaleX: 1, duration: 0.25, ease: "power3.out" }}, {round(C["denuncia"] + 0.1, 3)});')
    # B6
    wipe("#k6a", C["regresa"]); wipe("#k6b", C["otra"] - 0.2); stamp("#s6", C["denuncian"])
    a(f'tl.fromTo("#sh", {{ x: 600 }}, {{ x: -260, duration: 2.0, ease: "power1.inOut" }}, {round(C["escapa"] - 0.2, 3)});')
    wipe("#k6c", C["escapa"])
    # B7
    wipe("#k7a", C["l7"] + 0.05)
    for k in range(4):
        pop(f"#fb{k}", C["l7"] + 0.3 + k * 0.1, 0.3)
    pop("#cf", C["billetes"] + 0.9, 0.3)
    a(f'tl.fromTo("#isl", {{ x: 700 }}, {{ x: 0, duration: 0.5, ease: "power3.out" }}, {round(C["alcatraz"] - 0.4, 3)});')
    stamp("#k7b", C["alcatraz"])
    a(f'tl.fromTo("#bars", {{ y: -2000 }}, {{ y: 0, duration: 0.35, ease: "power4.in" }}, {round(C["alcatraz"] + 0.5, 3)});')
    # B8 — the tower returns: same framing as the hook (loop)
    wipe("#k8a", C["l8"]); wipe("#k8b", C["l8"] + 0.2); a(f'tl.fromTo("#t8 path", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: 0.9, ease: "power2.out" }}, {C["l8"]});'); stamp("#s8", C["suya"])
    return t


STAGE = r'''<template>
  <style>
    #root { position: absolute; inset: 0; overflow: hidden; background: #14213D; font-family: "Archivo Black", sans-serif; }
    #rays { position: absolute; left: -660px; top: 360px; width: 2400px; height: 2400px; opacity: 0.1; }
    .frame { position: absolute; inset: 40px; border: 6px solid #D4A73C; border-radius: 10px; opacity: 0.5; }
    .frame::after { content: ""; position: absolute; inset: 14px; border: 2px solid #D4A73C; border-radius: 6px; }
    .beat { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; }
    .kt { position: absolute; left: 0; width: 1080px; text-align: center; color: #F5E6C8; line-height: 1; letter-spacing: 1px; }
    .sm { font-size: 60px; } .mid { font-size: 62px; } .big { font-size: 94px; } .huge { font-size: 160px; } .kt { white-space: nowrap; }
    .gold { color: #D4A73C; } .red { color: #E63946; } .dim { color: #8FA0C0; }
    .kt { text-shadow: 6px 6px 0 #0B1426; }
    .tw { width: 100%; height: 100%; overflow: visible; }
    .tw path { fill: none; stroke: #D4A73C; stroke-width: 7; stroke-linejoin: round; stroke-linecap: round; stroke-dasharray: 1; stroke-dashoffset: 0; }
    .stamp { position: absolute; font-size: 96px; color: #F5E6C8; border: 10px solid #F5E6C8; border-radius: 16px; padding: 14px 30px 4px; transform: rotate(-8deg); }
    .stamp.red { color: #E63946; border-color: #E63946; background: rgba(20,33,61,0.85); }
    .stamp.sm { font-size: 70px; }
    .paper { position: absolute; width: 860px; height: 380px; background: #F5E6C8; border: 6px solid #0B1426; box-shadow: 14px 14px 0 #0B1426; padding: 18px 28px; }
    .mast { font-size: 58px; color: #14213D; border-bottom: 6px double #14213D; text-align: center; padding-bottom: 6px; }
    .np-row { display: flex; gap: 20px; margin-top: 16px; } .np-tower { width: 120px; height: 240px; flex: none; }
    .np-tower .tw path { stroke: #14213D; }
    .np-head { font-size: 56px; line-height: 1.05; color: #14213D; }
    .tag { position: absolute; font-size: 64px; color: #14213D; background: #D4A73C; padding: 16px 28px 8px; border: 6px solid #0B1426; box-shadow: 10px 10px 0 #0B1426; }
    .tag small { display: block; font-family: "Nunito", sans-serif; font-weight: 800; font-size: 34px; margin-top: 4px; }
    .man, .th, .run, .ship, .isl, .cuffs, .gls { width: 100%; height: 100%; overflow: visible; }
    .thw { position: absolute; width: 140px; height: 230px; }
    .badge { position: absolute; width: 840px; height: 300px; background: #F5E6C8; border: 6px solid #0B1426; box-shadow: 12px 12px 0 #0B1426; padding: 26px 36px;
      font-size: 60px; color: #14213D; line-height: 1.1; }
    .badge small { display: block; font-family: "Nunito", sans-serif; font-weight: 900; font-size: 30px; color: #C8102E; margin-bottom: 10px; }
    .badge em { display: block; font-style: normal; font-size: 48px; color: #6B6B6B; margin-top: 18px; }
    .price { position: absolute; font-size: 50px; color: #14213D; background: #F5E6C8; padding: 10px 22px 4px; border: 5px solid #0B1426; border-radius: 0 14px 14px 0; }
    .billw { position: absolute; width: 420px; height: 190px; }
    .bill { width: 100%; height: 100%; background: #8DBF8B; border: 6px solid #0B1426; border-radius: 10px; display: flex; align-items: center; justify-content: space-between;
      padding: 0 26px; font-size: 64px; color: #1E4D2B; box-shadow: 8px 8px 0 #0B1426; }
    .usd { width: 300px; height: 140px; } .usd .bill { font-size: 48px; }
    .strike { position: absolute; width: 780px; height: 14px; background: #E63946; }
    .bars { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;
      background: repeating-linear-gradient(90deg, transparent 0 120px, rgba(185,194,207,0.9) 120px 140px); transform: translateY(-2000px); }
    #dim { position: absolute; inset: 0; background: #000000; opacity: 0; }
  </style>
  <div id="root" data-composition-id="stage" data-width="1080" data-height="1920" data-layout-allow-overflow data-layout-allow-overlap>
    <svg id="rays" viewBox="-100 -100 200 200">__RAYS__</svg>
    <div class="frame"></div>
    <div id="dim"></div>
__BEATS__
  </div>
  <script>
    const tl = gsap.timeline({ paused: true });
__TW__
    window.__timelines["stage"] = tl;
  </script>
</template>
'''


def stage_html():
    import math
    rays = "".join(f'<path d="M0 0 L{100 * math.cos(math.radians(a - 3)):.1f} {100 * math.sin(math.radians(a - 3)):.1f} '
                   f'L{100 * math.cos(math.radians(a + 3)):.1f} {100 * math.sin(math.radians(a + 3)):.1f} Z" fill="#D4A73C"/>' for a in range(0, 360, 15))
    return STAGE.replace("__RAYS__", rays).replace("__BEATS__", BEATS).replace("__TW__", "\n".join("    " + x for x in tweens()))


def index_html():
    sfx = [("type0", "el_type", 0.1, 1.2, 0.35), ("ding0", "el_ding", C["eiffel"] + 0.35, 0.6, 0.4), ("ding1", "el_ding", C["otra0"], 0.6, 0.45),
           ("w1", "whoosh", C["l1"] - 0.35, 0.57, 0.3), ("paper", "el_paper", C["periodico"], 0.8, 0.45), ("type1", "el_type", C["carisimo"] - 0.4, 1.2, 0.35),
           ("w2", "whoosh", C["l2"] - 0.35, 0.57, 0.3), ("ding2", "el_ding", C["funcionario"] + 0.9, 0.6, 0.4), ("glass", "el_glass", C["hotel"] + 0.2, 1.0, 0.4),
           ("w3", "whoosh", C["l3"] - 0.35, 0.57, 0.3), ("shh", "el_shh", C["secreto"] - 0.1, 0.8, 0.45), ("ding3", "el_ding", C["chatarra"], 0.6, 0.45),
           ("w4", "whoosh", C["l4"] - 0.35, 0.57, 0.3), ("cash", "el_cash", C["fortuna"] + 0.3, 0.8, 0.45), ("ding4", "el_ding", C["soborno"], 0.6, 0.45),
           ("w5", "whoosh", C["l5"] - 0.35, 0.57, 0.3), ("run", "el_run", C["huye"] + 0.2, 1.2, 0.45),
           ("w6", "whoosh", C["l6"] - 0.35, 0.57, 0.3), ("whistle", "el_whistle", C["denuncian"], 1.0, 0.35),
           ("w7", "whoosh", C["l7"] - 0.35, 0.57, 0.3), ("cuffs", "el_cuffs", C["billetes"] + 0.9, 0.6, 0.5), ("clang", "el_clang", C["alcatraz"] + 0.8, 1.5, 0.45),
           ("w8", "whoosh", C["l8"] - 0.35, 0.57, 0.3), ("ding8", "el_ding", C["suya"], 0.6, 0.45),
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
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #14213D; }}
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
