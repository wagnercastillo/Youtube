"""Pone los datos de voz en la escena y genera compositions/captions.html.

  python -I audio/build.py           (después de gen_audio.py y de transcribe)
  python -I audio/build.py --selftest
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIX = {"Oye,": "¡Oye!", "Tenoctitán": "Tenochtitlan", "Náhuatl,": "náhuatl,", "Totoltel,": "totoltetl:",
       "Guajolota.": "guajolota.", "¿Piedra": "¿Piedra", "Guajolota?": "guajolota?", "agua,": "agua:",
       "Ahuautle.": "ahuautle.", "50": "50", "¡Gallina,": "¡Gallina!", "¿Gallina,": "¡Gallina!"}  # errores del transcriptor, corregidos contra el guion


def fix_words(words):
    """El transcriptor se comió "caviar" dentro de "dicen" y partió mal el final."""
    out = []
    for k, w in enumerate(words):
        nxt = words[k + 1]["text"] if k + 1 < len(words) else ""
        if w["text"] == "dicen" and w["end"] - w["start"] > 0.8 and nxt != "caviar":
            mid = round(w["start"] + 0.4, 3)
            out += [{**w, "end": mid}, {**w, "text": "caviar", "start": mid}]
        else:
            out.append(w)
    # "qué falta de respeto" se escribe con ¡…!: une las 4 palabras en la corrección de "respeto?"
    for i, w in enumerate(out):
        if w["text"] == "respeto?" and i >= 3 and out[i - 3]["text"] == "qué":
            out[i - 3:i + 1] = [{**out[i - 3], "text": "¡Qué"}, out[i - 2], out[i - 1], {**w, "text": "respeto!"}]
            break
    return out
MAX_WORDS, GAP_BREAK = 3, 0.15


def speaker_of(w, lines):
    for ln in lines:
        if ln["start"] - 0.3 <= w["start"] <= ln["end"] + 0.1:
            return ln["speaker"], ln["id"]
    return lines[-1]["speaker"], lines[-1]["id"]


def group_words(words, lines):
    groups, cur = [], []
    for i, w in enumerate(words):
        w = {**w, "text": FIX.get(w["text"].strip(), w["text"].strip())}
        w["speaker"], w["line"] = speaker_of(w, lines)
        if cur and (len(cur) >= MAX_WORDS or w["line"] != cur[-1]["line"]
                    or w["start"] - cur[-1]["end"] >= GAP_BREAK):
            groups.append(cur)
            cur = []
        cur.append(w)
        if re.search(r"[.?!…,]$", w["text"]):
            groups.append(cur)
            cur = []
    if cur:
        groups.append(cur)
    out = []
    for k, g in enumerate(groups):
        start = max(g[0]["start"] - 0.05, 0.12)
        nxt = groups[k + 1][0]["start"] - 0.05 if k + 1 < len(groups) else g[-1]["end"] + 1.5
        end = min(g[-1]["end"] + 0.3, nxt)
        out.append({"start": round(start, 3), "end": round(max(end, g[-1]["end"]), 3),
                    "speaker": g[0]["speaker"], "words": g})
    for a, b in zip(out, out[1:]):  # one group on screen at a time
        a["end"] = min(a["end"], b["start"])
    return out


def captions_html(groups):
    rows, tweens = [], []
    for gi, g in enumerate(groups):
        spans = " ".join(
            f'<span id="cw{gi}_{wi}" class="cw">{w["text"].upper()}</span>' for wi, w in enumerate(g["words"]))
        dur = round(g["end"] - g["start"], 3)
        rows.append(f'    <div id="cg{gi}" class="cg {g["speaker"]} clip" data-start="{g["start"]}" '
                    f'data-duration="{dur}"><div class="cin">{spans}</div></div>')
        tweens.append(f'    tl.fromTo("#cg{gi} .cin", {{ scale: 0.7 }}, {{ scale: 1, duration: 0.16, ease: "back.out(2.2)" }}, {g["start"]});')
        for wi, w in enumerate(g["words"]):
            tweens.append(f'    tl.fromTo("#cw{gi}_{wi}", {{ color: "var(--base)", scale: 1 }}, {{ color: "#FFD23F", scale: 1.1, duration: 0.06, ease: "power2.out" }}, {round(w["start"], 3)});')
            tweens.append(f'    tl.to("#cw{gi}_{wi}", {{ color: "var(--base)", scale: 1, duration: 0.08, ease: "power2.in" }}, {round(max(w["end"] - 0.04, w["start"] + 0.07), 3)});')
    return f"""<template>
  <style>
    #root {{ position: absolute; inset: 0; pointer-events: none; }}
    .cg {{ position: absolute; left: 0; top: 1400px; width: 1080px; text-align: center; overflow: visible; }}
    .cin {{ display: inline-block; font-family: "Archivo Black", sans-serif; font-size: 78px; line-height: 1.05;
      max-width: 940px; letter-spacing: 1px; transform-origin: 50% 60%; }}
    .cw {{ display: inline-block; color: var(--base); -webkit-text-stroke: 16px #1B1B2F; paint-order: stroke fill;
      text-shadow: 0 7px 0 #1B1B2F; margin: 0 6px; }}
    .crono {{ --base: #FFFFFF; }}
    .totola {{ --base: #FFE3C2; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="1080" data-height="1920">
{chr(10).join(rows)}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{chr(10).join(tweens)}
    window.__timelines["captions"] = tl;
  </script>
</template>
"""


def inject(stage_path, data):
    src = stage_path.read_text(encoding="utf-8")
    new = re.sub(r"/\*DATA-START\*/.*?/\*DATA-END\*/",
                 lambda _: "/*DATA-START*/" + json.dumps(data, separators=(",", ":")) + "/*DATA-END*/",
                 src, count=1, flags=re.S)
    assert new != src or "/*DATA-START*/" in src
    stage_path.write_text(new, encoding="utf-8")


def selftest():
    lines = [{"id": "l0", "speaker": "neuro", "start": 0, "end": 2},
             {"id": "l1", "speaker": "glia", "start": 2.2, "end": 5}]
    words = [{"text": t, "start": s, "end": s + 0.3} for t, s in
             [("Uno", 0.1), ("dos", 0.5), ("tres", 0.9), ("cuatro.", 1.3), ("Hola,", 2.3), ("midio", 2.8)]]
    g = group_words(words, lines)
    assert [len(x["words"]) for x in g] == [3, 1, 1, 1], [len(x["words"]) for x in g]
    assert g[0]["start"] == 0.12 and g[-1]["speaker"] == "glia" and g[-1]["words"][0]["text"] == "midió"
    assert all(a["end"] <= b["start"] for a, b in zip(g, g[1:]))
    print("selftest ok")


def main():
    if "--selftest" in sys.argv:
        return selftest()
    words = fix_words(json.loads((ROOT / "transcript.json").read_text(encoding="utf-8")))
    lines = json.loads((ROOT / "assets/lines.json").read_text(encoding="utf-8"))
    mouth = json.loads((ROOT / "assets/mouth.json").read_text(encoding="utf-8"))
    groups = group_words(words, lines)
    (ROOT / "compositions/captions.html").write_text(captions_html(groups), encoding="utf-8")
    inject(ROOT / "compositions/stage.html", {"mouth": mouth})
    print(f"{len(groups)} grupos de subtítulos, boca: {len(mouth['crono'])} frames")


if __name__ == "__main__":
    main()
