"""Mueve los tiempos de las escenas de la voz Chatterbox (guion v1) a la voz ElevenLabs (guion v2).

  python -I audio/remap.py            (después de gen_audio_el.py, antes de build.py)
  python -I audio/remap.py --selftest

Anclas: inicio y fin de cada línea + ANCHORS (palabras clave); entre anclas, lineal. EVENTS fija tweens a una palabra.
Siempre parte de las copias audio/bak/*.html.txt, así se puede correr las veces que haga falta.
"""
import json
import re
import shutil
import unicodedata
import sys
from bisect import bisect_right
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build import fix_words  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TAIL = 0.6  # segundos de cierre después de la última palabra


# Guion v2: mismas 10 líneas en el mismo orden, otras palabras. Anclas = la palabra vieja en la que
# pasaba algo en pantalla -> la palabra nueva donde debe pasar ("palabra#2" = segunda aparición).
ANCHORS = {
    "l1": [("llegaron", "llegan")],                                   # sticker IMPORTADAS
    "l3": [("de", "los"), ("en", "en"), ("totoltel", "totoltetl"),   # huevo, tarjeta, título
           ("piedra", "piedra"), ("guajolota", "guajolota")],         # TŌTOLIN + TETL = HUEVO
    "l5": [("ahuautle", "ahuautle")],
    "l7": [("caviar", "caviar"), ("mexicano", "mexicano"), ("50", "cincuenta")],
    "l9": [("gallina", "gallina"), ("gallina#2", "que")],             # sello, furia
}
# Eventos que el guion nuevo mueve a otra palabra: inicio de la línea del tween -> (línea, palabra, ajuste s)
EVENTS = {
    'tl.fromTo("#st-lake", { clipPath: "inset(100%': ("l5", "lago", -0.2),
    'tl.fromTo("#st-roe"': ("l5", "huevos", 0.0),
    'tl.fromTo("#st-axa"': ("l5", "chinche", 0.0),
    'id="sfx-lake"': ("l5", "lago", -0.25),
    'tl.fromTo("#totola", { y: 0 }': ("l3", "los", -0.2),      # salto 0.15 s + caída: pone el huevo
    'tl.fromTo("#totola", { y: -60 }': ("l3", "los", -0.05),
    'tl.fromTo("#st-egg"': ("l3", "los", -0.15),
    'id="sfx-egg"': ("l3", "los", -0.15),
    'tl.fromTo("#st-stamp span", { scale: 3.2': ("l9", "gallina", -0.22),  # cae justo en "Gallina"
    'tl.fromTo("#st-stamp span", { x: 0 }': ("l9", "gallina", 0.0),
    'id="sfx-stamp"': ("l9", "gallina", -0.04),
    'id="sfx-riser"': ("l9", "gallina", -1.6),
}


def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if c.isalnum() and not unicodedata.combining(c))


def by_line(lines, words, margin):
    out = {ln["id"]: [] for ln in lines}
    for w in words:  # la última línea que ya empezó
        i = max([k for k, ln in enumerate(lines) if ln["start"] - margin <= w["start"]] or [0])
        out[lines[i]["id"]].append(w)
    return out


def find(words, key):
    key, _, nth = key.partition("#")
    hits = [w for w in words if norm(w["text"]) == key]
    return hits[int(nth or 1) - 1]


def knots(old_lines, old_words, new_lines, new_words):
    ow_by = by_line(old_lines, old_words, 0.4)  # el transcriptor viejo adelanta hasta 0.4 s
    nw_by = by_line(new_lines, new_words, 0.05)
    pts = [(0.0, 0.0)]
    for ol, nl in zip(old_lines, new_lines):
        pts += [(ol["start"], nl["start"]), (ol["end"], nl["end"])]
        for o, n in ANCHORS.get(ol["id"], []):
            pts.append((find(ow_by[ol["id"]], o)["start"], find(nw_by[nl["id"]], n)["start"]))
    pts = sorted(set(pts))
    clean = [pts[0]]
    for p in pts[1:]:  # monótona en las dos columnas
        if p[0] > clean[-1][0] and p[1] >= clean[-1][1]:
            clean.append(p)
        else:
            print(f"  ancla descartada {p}")
    return clean


def event_times(new_lines, new_words):
    nw_by = by_line(new_lines, new_words, 0.05)
    return {k: round(find(nw_by[ln], w)["start"] + off, 2) for k, (ln, w, off) in EVENTS.items()}


def make_map(pts):
    xs = [p[0] for p in pts]

    def f(t):
        if t >= xs[-1]:
            return t + pts[-1][1] - pts[-1][0]
        i = bisect_right(xs, t) - 1
        (x0, y0), (x1, y1) = pts[i], pts[i + 1]
        return y0 + (y1 - y0) * (t - x0) / (x1 - x0)
    return f


def num(f, m):
    return f"{round(f(float(m)), 2):g}"


def apply_events(src, ev):
    out = []
    for ln in src.splitlines(keepends=True):
        for prefix, t in ev.items():
            if prefix in ln and ln.lstrip().startswith("tl."):
                ln = re.sub(r", ([\d.]+)\);(\s*)$", lambda m: f", {t:g});{m[2]}", ln)
            elif prefix in ln and "data-start=" in ln:
                ln = re.sub(r'data-start="[\d.]+"', f'data-start="{t:g}"', ln)
        out.append(ln)
    return "".join(out)


def remap_stage(src, f, dur):
    src = re.sub(r"const DUR = [\d.]+", f"const DUR = {dur:g}", src)
    out = []
    for ln in src.splitlines(keepends=True):
        s = ln.lstrip()
        if s.startswith(("const CKEYS", "const TKEYS")):
            ln = re.sub(r"\[([\d.]+), \"", lambda m: f"[{num(f, m[1])}, \"", ln)
        elif s.startswith("const CLOSE"):
            ln = re.sub(r"\[([\d.]+), ([\d.]+)\]", lambda m: f"[{num(f, m[1])}, {num(f, m[2])}]", ln)
        elif s.startswith(("const CAM", "[")) and re.search(r"\[[\d.]+, [\d.]+, \d+, \d+\]", ln):
            ln = re.sub(r"\[([\d.]+), ([\d.]+), (\d+), (\d+)\]", lambda m: f"[{num(f, m[1])}, {m[2]}, {m[3]}, {m[4]}]", ln)
        elif s.startswith("tl.") and "onUpdate" not in s:
            ln = re.sub(r", ([\d.]+)\);(\s*)$", lambda m: f", {num(f, m[1])});{m[2]}", ln)
        out.append(ln)
    return "".join(out)


def remap_index(src, f, dur):
    src = re.sub(r'data-duration="42\.3"', f'data-duration="{dur:g}"', src)
    return re.sub(r'(id="sfx-[^"]+"[^>]*data-start=")([\d.]+)"', lambda m: f'{m[1]}{num(f, m[2])}"', src)


def selftest():
    ANCHORS["t0"] = [("b", "c")]
    pts = knots([{"id": "t0", "start": 0, "end": 4}], [{"text": "a", "start": 0, "end": 1}, {"text": "¡B!", "start": 2, "end": 3}],
                [{"id": "t0", "start": 0, "end": 2}], [{"text": "c,", "start": 1, "end": 1.5}])
    f = make_map(pts)
    assert f(1) == 0.5 and f(2) == 1 and f(3) == 1.5 and f(5) == 3, [f(x) for x in (1, 2, 3, 5)]
    st = remap_stage('const DUR = 42.3\n    tl.to("#a", { x: 1 }, 2);\n    const CKEYS = [[0, "a"], [4, "b"]];\n', f, 3)
    assert "}, 1);" in st and '[2, "b"]' in st and "DUR = 3" in st, st
    print("selftest ok")


def main():
    if "--selftest" in sys.argv:
        return selftest()
    load = lambda p: json.loads((ROOT / p).read_text(encoding="utf-8"))
    old_words = fix_words(load("audio/transcript_chatterbox.json"))
    new_lines = load("assets/lines.json")
    f = make_map(knots(load("assets/lines_chatterbox.json"), old_words, new_lines, load("transcript.json")))
    ev = event_times(new_lines, load("transcript.json"))
    dur = round(new_lines[-1]["end"] + TAIL + 1.0, 1)  # el final furioso se queda ~1.6 s
    for name, fn in [("compositions/stage.html", remap_stage), ("index.html", remap_index)]:
        cur, bak = ROOT / name, ROOT / "audio" / "bak" / (Path(name).name + ".txt")
        if not bak.exists():
            shutil.copy(cur, bak)
        cur.write_text(apply_events(fn(bak.read_text(encoding="utf-8"), f, dur), ev), encoding="utf-8")
    print(f"remap ok, dur {dur} s; ejemplos: 5.42 ->{f(5.42):.2f}, 18.65->{f(18.65):.2f}, 37.5->{f(37.5):.2f}")


if __name__ == "__main__":
    main()
