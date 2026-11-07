"""EP14: escribe compositions/stage.html (Garbo, el espía condecorado por los dos bandos; TABLERO DE DETECTIVE) e index.html.

  python -I audio/build_video.py     (después de gen_audio_el.py y build.py)

Un tablero de corcho de 2400×4400 (HTML + SVG) por el que viaja la cámara (pan/zoom del tablero con GSAP, anclado a palabras).
Polaroids con caricaturas SVG, documentos a máquina, hilo rojo que se tiende entre chinchetas (stroke-dashoffset), sellos que
impactan, la red de 27 espías falsos, el mapa del Canal (Normandía real vs. Calais falso) y las dos medallas.
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
    "hitler": W("l0", "hitler"), "medalla": W("l0", "medalla"),
    "l1": L("l1"), "juan": W("l1", "juan"), "ingleses1": W("l1", "ingleses"), "rechazaron": W("l1", "rechazaron"),
    "l2": L("l2"), "nazis": W("l2", "nazis"), "lisboa": W("l2", "lisboa"), "guia": W("l2", "guia"), "revistas": W("l2", "revistas"), "noticieros": W("l2", "noticieros"),
    "l3": L("l3"), "queremos": W("l3", "queremos"), "garbo": W("l3", "garbo"),
    "l4": L("l4"), "veintisiete": W("l4", "veintisiete"), "falsos": W("l4", "falsos"), "pagaban": W("l4", "pagaban"),
    "l5": L("l5"), "mil": W("l5", "mil"), "convencio": W("l5", "convencio"), "normandia": W("l5", "normandia"), "distraccion": W("l5", "distraccion"),
    "l6": L("l6"), "cruz": W("l6", "cruz"), "l7": L("l7"), "rey": W("l7", "rey"), "condecoro": W("l7", "condecoro"),
    "l8": L("l8"), "bandos": W("l8", "bandos"), "nunca": W("l8", "nunca"), "end": END,
}

FACE = '''<svg viewBox="0 0 200 200" class="face"><rect width="200" height="200" fill="{bg}"/>
<path d="M30 200 Q30 140 100 132 Q170 140 170 200 Z" fill="{suit}"/><path d="M86 136 L100 170 L114 136 Z" fill="#FFFFFF"/><path d="M96 140 L100 166 L104 140 Z" fill="#B3262E"/>
<circle cx="100" cy="88" r="46" fill="#F2C9A0"/><path d="M54 80 Q58 34 100 36 Q146 36 148 78 Q132 56 100 58 Q72 58 54 80 Z" fill="#2B1D16"/>
<circle cx="82" cy="88" r="5" fill="#1B1B2F"/>{eye2}<path d="M80 110 Q100 104 120 110" stroke="#2B1D16" stroke-width="7" fill="none" stroke-linecap="round"/>
<path d="M84 120 Q100 {smile} 116 120" stroke="#7A1F2B" stroke-width="5" fill="none" stroke-linecap="round"/></svg>'''
GARBO = FACE.format(bg="#D8E4EC", suit="#3A4A5E", eye2='<path d="M110 88 Q118 82 126 88" stroke="#1B1B2F" stroke-width="5" fill="none" stroke-linecap="round"/>', smile=130)
GHOST = '<svg viewBox="0 0 100 120" class="face"><rect width="100" height="120" fill="#E9E1D0"/><path d="M14 120 Q14 82 50 76 Q86 82 86 120 Z" fill="#5E574C"/><circle cx="50" cy="48" r="24" fill="#5E574C"/><text x="50" y="58" font-size="30" text-anchor="middle" fill="#FFFFFF" font-family="Archivo Black">?</text></svg>'
IRON = '''<svg viewBox="0 0 200 260" class="medal"><path d="M70 0 H130 L120 60 H80 Z" fill="#1B1B2F"/><path d="M80 0 H90 L86 60 H82 Z M110 0 H120 L118 60 H114 Z" fill="#FFFFFF"/><path d="M92 0 H108 L106 60 H94 Z" fill="#C8102E"/>
<path d="M100 70 L118 120 L170 106 L134 150 L170 194 L118 180 L100 230 L82 180 L30 194 L66 150 L30 106 L82 120 Z" fill="#1B1B2F" stroke="#E8E8E8" stroke-width="8" stroke-linejoin="round"/><text x="100" y="164" font-size="30" text-anchor="middle" fill="#E8E8E8" font-family="Archivo Black">1939</text></svg>'''
MBE = '''<svg viewBox="0 0 200 260" class="medal"><path d="M70 0 H130 L120 60 H80 Z" fill="#E6A2B4"/><path d="M80 0 H86 L84 60 H82 Z M114 0 H120 L118 60 H116 Z" fill="#9A9AA6"/>
<path d="M100 74 C116 74 120 100 112 116 C130 108 156 112 156 130 C156 148 130 152 112 144 C120 160 116 186 100 186 C84 186 80 160 88 144 C70 152 44 148 44 130 C44 112 70 108 88 116 C80 100 84 74 100 74 Z" fill="#D9D9E0" stroke="#7A7A88" stroke-width="5"/>
<circle cx="100" cy="130" r="22" fill="#C8102E" stroke="#FFD23F" stroke-width="5"/><path d="M86 66 L92 50 L100 60 L108 50 L114 66 Z" fill="#FFD23F" stroke="#7A5A10" stroke-width="3"/></svg>'''
MAP = '''<svg viewBox="0 0 900 700" class="map"><rect width="900" height="700" fill="#BFD9E6"/>
<path d="M120 0 L520 0 L560 120 L470 200 L520 290 L380 330 L300 300 L160 320 L200 220 L120 160 Z" fill="#EAD9B0" stroke="#5A4A2A" stroke-width="5"/>
<path d="M0 520 L260 470 L330 500 L420 460 L560 470 L640 400 L700 380 L900 330 L900 700 L0 700 Z" fill="#EAD9B0" stroke="#5A4A2A" stroke-width="5"/>
<text x="330" y="170" font-size="40" text-anchor="middle" fill="#5A4A2A" font-family="Archivo Black">INGLATERRA</text><text x="560" y="620" font-size="40" text-anchor="middle" fill="#5A4A2A" font-family="Archivo Black">FRANCIA</text>
<circle cx="360" cy="492" r="14" fill="#2B8A3E"/><text x="300" y="540" font-size="30" fill="#2B8A3E" font-family="Archivo Black">NORMANDÍA</text>
<circle cx="690" cy="392" r="14" fill="#C8102E"/><text x="640" y="450" font-size="30" fill="#C8102E" font-family="Archivo Black">CALAIS</text>
<path id="arReal" pathLength="1" d="M300 300 Q320 400 352 470" stroke="#2B8A3E" stroke-width="16" fill="none" stroke-linecap="butt" stroke-dasharray="1" stroke-dashoffset="1"/>
<path id="arFake" pathLength="1" d="M470 220 Q620 280 680 372" stroke="#C8102E" stroke-width="30" fill="none" stroke-linecap="butt" stroke-dasharray="1" stroke-dashoffset="1"/></svg>'''

# items: id, x, y, w, h, rot, inner html, class
ITEMS = [
    ("pGarbo", 960, 300, 480, 560, -3, f'<div class="ph">{GARBO}</div><div class="cap">JUAN PUJOL</div>', "pola"),
    ("mIron0", 1450, 380, 260, 340, 6, IRON, "medw"),
    ("dRej", 380, 1080, 640, 380, 4, '<h3>EMBAJADA BRITÁNICA</h3><p>Solicitud de: J. Pujol<br>Quiere ser espía.</p>', "doc"),
    ("dLis", 1150, 1650, 520, 300, -4, '<h3>LISBOA, 1941</h3><p>Agente alemán «ALARIC»<br>(Pujol)</p>', "doc"),
    ("iGuia", 200, 1980, 420, 300, -6, '<div class="book">GUÍA TURÍSTICA<br>DE GRAN BRETAÑA</div>', "prop"),
    ("iRev", 680, 2120, 360, 280, 5, '<div class="book mag">REVISTAS</div>', "prop"),
    ("iCine", 1110, 2080, 400, 300, -3, '<div class="book reel">NOTICIERO<br>DEL CINE 🎞</div>', "prop"),
    ("dRep", 1650, 1980, 560, 420, 3, '<h3>«INFORME DESDE LONDRES»</h3><p>Barcos… tropas…<br>(lo copió de una guía)</p>', "doc"),
    ("dMi5", 1500, 2560, 640, 360, -3, f'<div class="ph sm">{GARBO}</div><h3>MI5 · AGENTE «GARBO»</h3>', "doc file"),
    ("dNet", 260, 2620, 1100, 860, 0, "".join(f'<div class="ag">{GHOST}</div>' for _ in range(27)), "net"),
    ("dPay", 1500, 3020, 560, 260, 4, '<h3>NÓMINA ALEMANA</h3><p>27 agentes · pagados ✔</p>', "doc"),
    ("dMap", 760, 3560, 900, 700, -2, MAP, "mapw"),
    ("dTel", 260, 4280, 640, 420, -4, f'<h3>TELEGRAMA · 29-VII-1944</h3><p>«El Führer le concede<br>la Cruz de Hierro»</p>', "doc tel"),
    ("mIron", 960, 4300, 260, 340, -5, IRON, "medw"),
    ("mMbe", 1560, 4300, 260, 340, 5, MBE, "medw"),
    ("dMbe", 1340, 4680, 720, 220, 3, '<h3>REY JORGE VI · 25-XI-1944</h3><p>Miembro de la Orden del Imperio Británico</p>', "doc"),
]
STAMPS = [  # id, x, y, text, color, rot, time
    ("sRej", 470, 1300, "RECHAZADO", "#C8102E", -12, "rechazaron"),
    ("sFake", 1700, 2300, "FALSO", "#C8102E", -14, "guia"),
    ("sHire", 1560, 2820, "CONTRATADO", "#2B8A3E", 8, "queremos"),
    ("sAll", 420, 3200, "¡TODOS FALSOS!", "#C8102E", -8, "falsos"),
    ("sDis", 900, 4090, "«SOLO UNA DISTRACCIÓN»", "#C8102E", -6, "distraccion"),
]
PINS = {"pGarbo": (1200, 330), "mIron0": (1580, 400), "dRej": (700, 1100), "dLis": (1410, 1670), "iGuia": (410, 2000), "iRev": (860, 2140),
        "iCine": (1310, 2100), "dRep": (1930, 2000), "dMi5": (1820, 2580), "dPay": (1780, 3040), "dMap": (1210, 3580), "dTel": (580, 4300),
        "mIron": (1090, 4320), "mMbe": (1690, 4320)}
STRINGS = [  # from, to, time key
    ("pGarbo", "mIron0", "medalla"), ("pGarbo", "dRej", "ingleses1"), ("dRej", "dLis", "nazis"), ("iGuia", "dRep", "guia"), ("iRev", "dRep", "revistas"),
    ("iCine", "dRep", "noticieros"), ("dRep", "dMi5", "queremos"), ("dMi5", "dPay", "pagaban"), ("dPay", "dMap", "mil"),
    ("dMap", "dTel", "cruz"), ("dTel", "mIron", "cruz"), ("dMap", "mMbe", "rey"), ("pGarbo", "mMbe", "bandos"),
]
# camera: time key → (center x, center y, zoom)
CAM = [(0, 1200, 900, 1.0), ("l1", 760, 1260, 1.0), ("l2", 1250, 1820, 0.95), ("guia", 1220, 2200, 0.55), ("l3", 1760, 2700, 0.92),
       ("l4", 1150, 3060, 0.55), ("l5", 1210, 3900, 0.95), ("normandia", 1190, 3900, 1.05), ("l6", 900, 4470, 0.82), ("l7", 1650, 4620, 0.95),
       ("l8", 1200, 2600, 0.3), ("nunca", 1200, 900, 1.0)]


def tweens():
    t, a = [], None
    a = t.append
    T = lambda k: k if isinstance(k, (int, float)) else C[k]
    # camera: board moves so (cx, cy) lands at screen (540, 900)
    for i, (k, cx, cy, z) in enumerate(CAM):
        x, y = round(540 - cx * z, 1), round(900 - cy * z, 1)
        if i == 0:
            a(f'tl.set("#board", {{ x: {x}, y: {y}, scale: {z} }}, 0);')
        else:
            dur = 0.9 if k in ("l8",) else 0.7
            a(f'tl.to("#board", {{ x: {x}, y: {y}, scale: {z}, duration: {dur}, ease: "power3.inOut" }}, {round(T(k) - 0.15, 3)});')
    # items drop on the board (pinned) as they are mentioned
    ITEM_T = {"pGarbo": 0.05, "mIron0": "medalla", "dRej": "juan", "dLis": "lisboa", "iGuia": "guia", "iRev": "revistas", "iCine": "noticieros",
              "dRep": "guia", "dMi5": "queremos", "dNet": "l4", "dPay": "pagaban", "dMap": "mil", "dTel": "l6", "mIron": "cruz", "mMbe": "rey", "dMbe": "condecoro"}
    for i, *_ in ITEMS:
        tt = T(ITEM_T[i]) if i != "pGarbo" else 0.05
        a(f'tl.fromTo("#{i}", {{ scale: 1.35, opacity: 0, y: -40 }}, {{ scale: 1, opacity: 1, y: 0, duration: 0.35, ease: "power3.out" }}, {round(tt, 3)});')
    for k in range(27):  # the fake network fills in, one agent after another
        a(f'tl.fromTo("#dNet .ag:nth-child({k + 1})", {{ scale: 0 }}, {{ scale: 1, duration: 0.18, ease: "back.out(2)" }}, {round(C["veintisiete"] + k * 0.045, 3)});')
    for i, *_rest, key in STAMPS:
        a(f'tl.fromTo("#{i}", {{ scale: 2.6, opacity: 0 }}, {{ scale: 1, opacity: 0.92, duration: 0.18, ease: "power4.in" }}, {C[key]});')
    for n, (f, to, key) in enumerate(STRINGS):
        a(f'tl.fromTo("#st{n}", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: 0.5, ease: "power2.out" }}, {round(C[key] + 0.15, 3)});')
    a(f'tl.fromTo("#arReal", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: 0.6, ease: "power2.out" }}, {C["normandia"]});')
    a(f'tl.fromTo("#arFake", {{ strokeDashoffset: 1 }}, {{ strokeDashoffset: 0, duration: 0.6, ease: "power2.out" }}, {round(C["distraccion"] - 0.4, 3)});')
    # hook + outro overlays
    for i, tt in (("h1", 0.03), ("h2", 0.2)):
        a(f'tl.fromTo("#{i}", {{ clipPath: "inset(-30px 100% -30px -30px)" }}, {{ clipPath: "inset(-30px -30px -30px -30px)", duration: 0.32, ease: "power3.out" }}, {tt});')
    a(f'tl.to("#hook", {{ clipPath: "inset(-30px -30px -30px 1200px)", duration: 0.3, ease: "power3.in" }}, {round(C["l1"] - 0.1, 3)});')
    a(f'tl.fromTo("#o1", {{ clipPath: "inset(-30px 100% -30px -30px)" }}, {{ clipPath: "inset(-30px -30px -30px -30px)", duration: 0.32, ease: "power3.out" }}, {C["bandos"]});')
    a(f'tl.to("#o1", {{ clipPath: "inset(-30px -30px -30px 1200px)", duration: 0.25, ease: "power3.in" }}, {round(C["nunca"] - 0.1, 3)});')
    a(f'tl.fromTo("#src", {{ opacity: 0 }}, {{ opacity: 1, duration: 0.3 }}, {C["l5"]});')
    a(f'tl.to("#src", {{ opacity: 0, duration: 0.3 }}, {C["l8"]});')
    return t


def stage_html():
    items = "\n".join(f'      <div id="{i}" class="it {cls}" style="left:{x}px;top:{y}px;width:{w}px;height:{h}px;rotate:{r}deg">{inner}</div>'
                      for i, x, y, w, h, r, inner, cls in ITEMS)
    stamps = "\n".join(f'      <div id="{i}" class="stamp" data-layout-allow-overlap style="left:{x}px;top:{y}px;color:{c};border-color:{c};rotate:{r}deg">{txt}</div>'
                       for i, x, y, txt, c, r, _ in STAMPS)
    pins = "".join(f'<circle cx="{x}" cy="{y}" r="16" fill="#C8102E" stroke="#6E0A12" stroke-width="5"/>' for x, y in PINS.values())
    strings = "".join(f'<path id="st{n}" pathLength="1" d="M{PINS[f][0]} {PINS[f][1]} Q{(PINS[f][0] + PINS[to][0]) / 2} {(PINS[f][1] + PINS[to][1]) / 2 + 60} {PINS[to][0]} {PINS[to][1]}" class="yarn"/>'
                      for n, (f, to, _) in enumerate(STRINGS))
    return (STAGE.replace("__ITEMS__", items).replace("__STAMPS__", stamps).replace("__PINS__", pins).replace("__STRINGS__", strings)
            .replace("__TW__", "\n".join("    " + x for x in tweens())))


STAGE = r'''<template>
  <style>
    #root { position: absolute; inset: 0; overflow: hidden; background: #8A6440; font-family: "Archivo Black", sans-serif; }
    #board { position: absolute; left: 0; top: 0; width: 2400px; height: 5600px; transform-origin: 0 0;
      background-color: #C49A6C; background-image: radial-gradient(#B08558 2px, transparent 2.5px), radial-gradient(#D4AC80 1.5px, transparent 2px);
      background-size: 26px 26px, 34px 34px; background-position: 0 0, 13px 17px; box-shadow: inset 0 0 0 40px #6B4423; }
    .it { position: absolute; z-index: 1; box-shadow: 10px 14px 0 rgba(40,25,10,0.35); }
    .pola { background: #FFFFFF; padding: 22px 22px 0; } .pola .ph { width: 100%; height: 420px; } .cap { font-size: 46px; color: #1B1B2F; text-align: center; padding-top: 22px; }
    .face { width: 100%; height: 100%; display: block; }
    .doc { background: #F3EAD3; padding: 30px 36px; font-family: "Courier New", monospace; color: #2B2B2B; }
    .doc h3 { font-family: "Courier New", monospace; font-weight: 900; font-size: 40px; margin-bottom: 18px; border-bottom: 4px solid #2B2B2B; padding-bottom: 8px; }
    .doc p { font-size: 38px; line-height: 1.25; font-weight: 700; }
    .file { background: #E8C98A; } .file .ph { width: 160px; height: 160px; float: right; margin-left: 20px; border: 6px solid #FFFFFF; }
    .tel { background: #FFF6C8; }
    .prop { background: transparent; box-shadow: none; }
    .book { width: 100%; height: 100%; background: #2B4C9B; color: #FFFFFF; font-size: 44px; line-height: 1.1; display: flex; align-items: center; justify-content: center;
      text-align: center; border: 8px solid #1B1B2F; border-radius: 10px; box-shadow: 10px 14px 0 rgba(40,25,10,0.35); }
    .mag { background: #E63946; } .reel { background: #1B1B2F; }
    .medw { background: transparent; box-shadow: none; } .medal { width: 100%; height: 100%; filter: drop-shadow(8px 10px 0 rgba(40,25,10,0.35)); }
    .net { background: #F3EAD3; padding: 30px; display: grid; grid-template-columns: repeat(9, 1fr); gap: 14px; }
    .ag { background: #FFFFFF; padding: 6px; height: 240px; } .ag .face { height: 100%; }
    .mapw { background: #FFFFFF; padding: 16px; } .map { width: 100%; height: 100%; display: block; }
    .stamp { position: absolute; z-index: 5; font-size: 88px; border: 12px solid; border-radius: 18px; padding: 10px 28px 0; background: rgba(243,234,211,0.55); white-space: nowrap; }
    #yarn { position: absolute; z-index: 6; left: 0; top: 0; width: 2400px; height: 5000px; overflow: visible; pointer-events: none; }
    .yarn { fill: none; stroke: #D7263D; stroke-width: 9; stroke-linecap: butt; stroke-dasharray: 1; stroke-dashoffset: 1; }
    #hook, #o1 { position: absolute; left: 0; top: 1080px; width: 1080px; }
    .tags { width: 1080px; text-align: center; margin-bottom: 22px; clip-path: inset(-30px 100% -30px -30px); }
    .tags span { display: inline-block; white-space: nowrap; font-size: 74px; line-height: 1; padding: 16px 30px 10px; color: #1B1B2F; border: 8px solid #1B1B2F; box-shadow: 10px 10px 0 #1B1B2F; }
    #h1 span { background: #FFFFFF; } #h2 span { background: #E63946; color: #FFFFFF; }
    #o1 { top: 260px; clip-path: inset(-30px 100% -30px -30px); text-align: center; } #o1 span { background: #FFD23F; }
    #src { position: absolute; left: 0; top: 1455px; width: 1080px; text-align: center; opacity: 0; }
    #src span { display: inline-block; font-family: "Nunito", sans-serif; font-weight: 800; font-size: 30px; padding: 6px 16px; background: rgba(27,27,47,0.85); color: #FFFFFF; border-radius: 10px; }
  </style>
  <div id="root" data-composition-id="stage" data-width="1080" data-height="1920" data-layout-allow-overflow data-layout-allow-overlap>
    <div id="board">
__ITEMS__
__STAMPS__
      <svg id="yarn" viewBox="0 0 2400 5000">__STRINGS____PINS__</svg>
    </div>
    <div id="hook">
      <div id="h1" class="tags"><span>ENGAÑÓ A HITLER…</span></div>
      <div id="h2" class="tags"><span>¡Y HITLER LO PREMIÓ!</span></div>
    </div>
    <div id="o1" class="tags"><span>CONDECORADO POR LOS DOS BANDOS</span></div>
    <div id="src"><span>Fuente: Wikipedia «Juan Pujol García» · MI5</span></div>
  </div>
  <script>
    const tl = gsap.timeline({ paused: true });
__TW__
    window.__timelines["stage"] = tl;
  </script>
</template>
'''


def index_html():
    sfx = [("sting", "el_sting", 0.05, 1.5, 0.35), ("pin0", "el_pin", 0.1, 0.5, 0.4), ("medal0", "el_medal", C["medalla"], 1.5, 0.3),
           ("type1", "el_type", C["juan"], 1.2, 0.35), ("stamp1", "el_stamp", C["rechazaron"], 0.6, 0.5), ("paper", "el_paper", C["lisboa"], 0.8, 0.4),
           ("flash", "el_flash", C["guia"], 0.8, 0.35), ("stamp2", "el_stamp", C["guia"] + 0.05, 0.6, 0.45), ("stamp3", "el_stamp", C["queremos"], 0.6, 0.5),
           ("morse", "el_morse", C["l4"], 1.5, 0.35), ("stamp4", "el_stamp", C["falsos"], 0.6, 0.5), ("cash", "el_cash", C["pagaban"], 0.8, 0.4),
           ("sting2", "el_sting", C["normandia"], 1.5, 0.35), ("stamp5", "el_stamp", C["distraccion"], 0.6, 0.5), ("morse2", "el_morse", C["l6"] - 0.2, 1.5, 0.3),
           ("medal1", "el_medal", C["cruz"], 1.5, 0.4), ("medal2", "el_medal", C["rey"], 1.5, 0.4), ("w", "whoosh", C["l8"] - 0.15, 0.57, 0.35),
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
      html, body {{ margin: 0; width: 1080px; height: 1920px; overflow: hidden; background: #8A6440; }}
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
