"""Voz del EP18 con ElevenLabs Pro (voces diseñadas en audio/design_voices.py).

  ~/.chatterbox-py/Scripts/python.exe -I audio/gen_audio_el.py   (luego python -I audio/build.py)

Salidas (assets/): voz.wav, lines.json, mouth.json; transcript.json con los tiempos de ElevenLabs.
Las respuestas de la API quedan en audio/el/ y no se vuelven a pedir (borrar para regenerar).
"""
import base64
import json
import re
import urllib.error
import urllib.request
from pathlib import Path

import numpy as np
import soundfile as sf

ROOT = Path(__file__).resolve().parent.parent
OUT, CACHE = ROOT / "assets", ROOT / "audio" / "el"
SR, FPS = 44100, 30
VOICE = json.loads((ROOT / "audio" / "voices.json").read_text(encoding="utf-8"))  # narr, bjorn, doepler
MODEL = "eleven_v3"
SETTINGS = {"stability": 0.0}  # v3 "Creative": the most expressive; the transcript check catches slips

# Guion v1 (2026-11-11): vikingos sin cuernos. Fuentes en SPEC.md.
SCRIPT = [
    ("l0", "narr",    "[excited] ¿Los vikingos usaban cascos con cuernos? ¡Mentira! Y el que se los puso… ni siquiera era vikingo."),
    ("l1", "bjorn",   "[proud] ¡Dibújamelos, compadre! Bien grandotes, para que me tengan miedo."),
    ("l2", "narr",    "[mischievously] Ahorita te los borro. En mil novecientos cuarenta y tres, en Noruega, desenterraron el único casco vikingo casi completo que existe. ¿Y cuántos cuernos tenía? Cero."),
    ("l3", "bjorn",   "[confused] ¿Cero? ¿Y entonces cómo asusto a la gente?"),
    ("l4", "narr",    "[laughs] Con el hacha, Björn. Además, los historiadores dicen que en plena batalla unos cuernos serían puro estorbo."),
    ("l5", "narr",    "[gossipy] Ojo: sí hay cascos con cuernos en Dinamarca… pero son de la Edad de Bronce. Mil setecientos años antes de los vikingos. Y eran para ceremonias, no para pelear."),
    ("l6", "narr",    "[dramatic] ¿Entonces quién los hizo famosos? Un diseñador de vestuario. Alemania, mil ochocientos setenta y seis: se estrena la ópera de Wagner, y Carl Emil Doepler les pone cuernos a sus guerreros."),
    ("l7", "doepler", "[smug] ¡Se veían divinos en el escenario! ¿Qué querían, que salieran con gorrito?"),
    ("l8", "narr",    "[mischievously] Y desde entonces, caricaturas, películas y disfraces… todos con cuernos. ¿Y tú? ¿También los dibujabas así?"),
]
OVERRIDE = {}  # line index -> voice_settings for lines that slip in creative mode
TEMPO = 1.25  # set >1 to speed up a slow voice: speed up without changing pitch (atempo), times scaled below
GAP, LEAD = 0.14, 0.15

def api_key():
    for d in [ROOT, *ROOT.parents]:
        env = d / ".env"
        if env.exists():
            for ln in env.read_text(encoding="utf-8").splitlines():
                if ln.strip().startswith("ELEVENLABS_API_KEY="):
                    return ln.split("=", 1)[1].strip().strip("\"'")
    raise SystemExit("falta ELEVENLABS_API_KEY en .env")


def tts(i, spk, text):
    f = CACHE / f"{i:02d}_{spk}.json"
    if not f.exists():
        req = urllib.request.Request(
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE[spk]}/with-timestamps?output_format=mp3_44100_128",
            data=json.dumps({"text": text, "model_id": MODEL, "voice_settings": OVERRIDE.get(i, SETTINGS),
                             "language_code": "es", "seed": 11}).encode(),
            headers={"xi-api-key": api_key(), "Content-Type": "application/json"})
        try:
            f.write_bytes(urllib.request.urlopen(req).read())
        except urllib.error.HTTPError as e:
            raise SystemExit(f"ElevenLabs {e.code} en línea {i}: {e.read()[:400]!r}")
    d = json.loads(f.read_text(encoding="utf-8"))
    mp3 = f.with_suffix(".mp3")
    mp3.write_bytes(base64.b64decode(d["audio_base64"]))
    pcm, _ = sf.read(mp3, dtype="float32")  # 44.1 kHz mp3: 24 kHz PCM cut the highs and sounded dull
    pcm = pcm.mean(axis=1) if pcm.ndim > 1 else pcm
    return pcm, d["alignment"]


def words_of(al):
    """Caracteres con tiempo → palabras {text,start,end}."""
    out, cur = [], None
    tag = False
    for ch, s, e in zip(al["characters"], al["character_start_times_seconds"], al["character_end_times_seconds"]):
        if ch in "[]":  # etiquetas de actuación: fuera de los subtítulos
            tag = ch == "["
            cur = None
            continue
        if tag or ch in "«»":
            continue
        if ch.isspace():
            cur = None
            continue
        if cur is None:
            cur = {"text": "", "start": s, "end": e}
            out.append(cur)
        cur["text"] += ch
        cur["end"] = e
    return out


def trim_bounds(x, thresh=0.01):
    idx = np.where(np.abs(x) > thresh)[0]
    return (max(idx[0] - 441, 0), min(idx[-1] + 882, len(x))) if len(idx) else (0, len(x))


def mouth_envelope(x):
    hop = SR // FPS
    n = int(np.ceil(len(x) / hop))
    rms = np.array([np.sqrt(np.mean(x[k * hop:(k + 1) * hop] ** 2) + 1e-12) for k in range(n)])
    ref = np.percentile(rms[rms > 0.005], 90) if np.any(rms > 0.005) else 1
    env = np.clip((rms - 0.012) / (ref - 0.012), 0, 1)
    return np.convolve(env, [0.25, 0.5, 0.25], mode="same")


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    script = [{"id": i, "speaker": spk, "text": " ".join(re.sub(r"\[[^\]]*\]", "", t).replace("«", "").replace("»", "").split()), "tagged": t}
              for i, spk, t in SCRIPT]

    clips = []
    for i, ln in enumerate(script):
        pcm, al = tts(i, ln["speaker"], ln["tagged"])
        a, b = trim_bounds(pcm)
        clips.append((ln, pcm[a:b] * (0.89 / max(np.max(np.abs(pcm[a:b])), 1e-6)), al, a / SR))

    total = LEAD + sum(len(c) / SR + GAP for _, c, _, _ in clips)
    track = np.zeros(int(total * SR) + SR // 2, dtype="float32")
    nf = int(np.ceil(len(track) / (SR // FPS)))
    mouth = {"fps": FPS, **{k: [0.0] * nf for k in VOICE}}
    lines, words, t0 = [], [], LEAD
    for ln, clip, al, off in clips:
        s = int(t0 * SR)
        track[s:s + len(clip)] += clip
        f0 = int(round(t0 * FPS))
        for k, v in enumerate(mouth_envelope(clip)):
            if f0 + k < nf:
                mouth[ln["speaker"]][f0 + k] = round(float(v), 3)
        dur = len(clip) / SR
        for w in words_of(al):
            words.append({"id": f"w{len(words)}", "text": w["text"],
                          "start": round(t0 + max(w["start"] - off, 0), 3), "end": round(t0 + min(w["end"] - off, dur), 3)})
        lines.append({**{k: v for k, v in ln.items() if k != "tagged"}, "start": round(t0, 3), "end": round(t0 + dur, 3)})
        print(f"{ln['id']} {ln['speaker']:6} {dur:.2f}s")
        t0 += dur + GAP

    raw = ROOT / "audio" / "voz_raw.wav"
    sf.write(raw, track, SR)
    # presence: high-pass, +3 dB at 3.5 kHz, air shelf, gentle compression, peak at -1 dB
    import subprocess
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(raw), "-af",
                    f"atempo={TEMPO},highpass=f=80,equalizer=f=3500:t=q:w=1.2:g=3,highshelf=f=9000:g=2,"
                    "acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2,alimiter=limit=0.89",
                    str(OUT / "voz.wav")], check=True)
    for ln in lines:
        ln["start"], ln["end"] = round(ln["start"] / TEMPO, 3), round(ln["end"] / TEMPO, 3)
    for w in words:
        w["start"], w["end"] = round(w["start"] / TEMPO, 3), round(w["end"] / TEMPO, 3)
    (OUT / "lines.json").write_text(json.dumps(lines, ensure_ascii=False, indent=1), encoding="utf-8")
    for k in VOICE:  # mouth frames follow the sped-up audio too
        src = mouth[k]
        mouth[k] = [src[min(int(round(f * TEMPO)), len(src) - 1)] for f in range(int(len(src) / TEMPO))]
    (OUT / "mouth.json").write_text(json.dumps(mouth), encoding="utf-8")
    (ROOT / "transcript.json").write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"voz.wav {len(track) / SR / TEMPO:.2f}s, {len(words)} palabras")


if __name__ == "__main__":
    main()
