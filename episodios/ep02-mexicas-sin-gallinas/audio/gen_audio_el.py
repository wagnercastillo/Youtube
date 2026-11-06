"""Voz del EP02 con ElevenLabs (reemplaza a Chatterbox, que sonaba robótico).

  ~/.chatterbox-py/Scripts/python.exe -I audio/gen_audio_el.py

Voz a velocidad natural, líneas seguidas. Después: python -I audio/remap.py (mueve los tiempos
de las escenas de la voz vieja a la nueva) y python -I audio/build.py.
Salidas (assets/): voz.wav, lines.json, mouth.json; transcript.json con los tiempos de ElevenLabs.
Las respuestas de la API quedan en audio/el/ y no se vuelven a pedir.
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
OUT, CACHE = ROOT / "assets", ROOT / "audio" / "el_v3"
SR, FPS = 24000, 30
VOICE = {"crono": "yG52fI8LU4PPVgvtNLWz",   # Crono: Voice Design, mexicano CDMX 22-28
         "totola": "C6N4cAUUGz4weG5XHekn"}  # Totola: Voice Design, mexicana 30-40
MODEL = "eleven_v3"  # actúa las etiquetas [excited], [laughs]...; v2 leía plano
SETTINGS = {"stability": 0.5}  # v3: 0 creativo, 0.5 natural, 1 robusto

# Guion v2 (2026-11-05): una sola cadena causa→efecto, cierra en el título.
# id, personaje, texto con etiquetas de actuación (no salen en subtítulos)
SCRIPT = [
    ("l0", "crono", "[excited] ¡Llegué a Tenochtitlan, año 1500! A ver, unos huevos de gallina para desayunar."),
    ("l1", "totola", "[laughs] ¿Gallina? Aquí no hay. [sarcastic] Las gallinas llegan con los españoles… en veinte años."),
    ("l2", "crono", "[confused] ¿Y entonces qué huevos comen aquí?"),
    ("l3", "totola", "[proudly] Los míos, mi rey. En náhuatl, huevo se dice totoltetl: piedra de guajolota. Porque parece piedrita."),
    ("l4", "crono", "[excited] ¡Perfecto! Me das dos, ¿no?"),
    ("l5", "totola", "[offended] ¡Ni lo sueñes! Si tienes hambre, ve al lago: hay ahuautle, huevos de chinche de agua."),
    ("l6", "crono", "[disgusted] ¿Huevos de insecto? ¡Guácala!"),
    ("l7", "totola", "[matter-of-fact] Guácala nada. Hoy le dicen caviar mexicano, y el kilo cuesta unos cincuenta dólares."),
    ("l8", "crono", "[thinking] Mmm… mejor los tuyos. [mischievously] Total, eres una gallina, ¿no?"),
    ("l9", "totola", "[outraged] ¡Eso mismo dijeron los españoles! «Gallina de la tierra». [shouting] ¡Qué falta de respeto!"),
]
GAP, LEAD = 0.12, 0.12  # mismo ritmo que la versión Chatterbox


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
            f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE[spk]}/with-timestamps?output_format=pcm_24000",
            data=json.dumps({"text": text, "model_id": MODEL, "voice_settings": SETTINGS,
                             "language_code": "es", "seed": 11}).encode(),
            headers={"xi-api-key": api_key(), "Content-Type": "application/json"})
        try:
            f.write_bytes(urllib.request.urlopen(req).read())
        except urllib.error.HTTPError as e:
            raise SystemExit(f"ElevenLabs {e.code} en línea {i}: {e.read()[:400]!r}")
    d = json.loads(f.read_text(encoding="utf-8"))
    pcm = np.frombuffer(base64.b64decode(d["audio_base64"]), dtype="<i2").astype("float32") / 32768
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
    return (max(idx[0] - 240, 0), min(idx[-1] + 480, len(x))) if len(idx) else (0, len(x))


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
    mouth = {"fps": FPS, "crono": [0.0] * nf, "totola": [0.0] * nf}
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

    sf.write(OUT / "voz.wav", track, SR)
    (OUT / "lines.json").write_text(json.dumps(lines, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "mouth.json").write_text(json.dumps(mouth), encoding="utf-8")
    (ROOT / "transcript.json").write_text(json.dumps(words, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"voz.wav {len(track) / SR:.2f}s, {len(words)} palabras")


if __name__ == "__main__":
    main()
