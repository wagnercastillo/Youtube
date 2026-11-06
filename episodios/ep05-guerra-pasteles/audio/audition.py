"""Casting de narrador: diseña candidatas, las mide y guarda la mejor como "narr".

  ~/.chatterbox-py/Scripts/python.exe -I audio/audition.py

Métrica de energía (sobre la misma frase de prueba): variación de tono (semitonos), dinámica de volumen,
velocidad (menos segundos = más rápido) y brillo (centroide espectral). La voz de Totola (aprobada por el
usuario en EP02) y la narradora anterior entran como referencia. Muestras en audio/audition/.
"""
import base64
import json
import urllib.error
import urllib.request
from pathlib import Path

import librosa
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "audio" / "audition"
TEXT = ("¡No manches! ¿Sabías que Francia le declaró la guerra a México por culpa de unos pasteles? "
        "¡Así como lo oyes! Y espérate, que lo mejor viene después: ¡a Santa Anna le hicieron un funeral… "
        "a su pierna! ¿Cómo la ves?")
DESCS = {
    "comadre": ("Mujer mexicana de 35 años, voz brillante, potente y súper expresiva, comadre chismosa que cuenta el chisme "
                "del siglo con risas, asombro y mucha energía, ritmo rápido. Español mexicano nativo. Grabación de estudio nítida."),
    "conductora": ("Conductora mexicana de 28 años de un programa de espectáculos, voz clara, chispeante y muy enérgica, "
                   "exagera las sorpresas y se ríe. Español mexicano nativo. Grabación de estudio nítida."),
    "abuelita": ("Abuelita mexicana de 70 años muy pícara y vivaz, voz cálida pero llena de energía y picardía, cuenta "
                 "chismes de antes con emoción y carcajadas. Español mexicano nativo. Grabación de estudio nítida."),
}
REFS = {"totola_ref": "C6N4cAUUGz4weG5XHekn", "ep04_male": "uiAksityc3aBuAQ4bjSW"}


def api_key():
    for d in [ROOT, *ROOT.parents]:
        env = d / ".env"
        if env.exists():
            for ln in env.read_text(encoding="utf-8").splitlines():
                if ln.strip().startswith("ELEVENLABS_API_KEY="):
                    return ln.split("=", 1)[1].strip().strip("\"'")
    raise SystemExit("falta ELEVENLABS_API_KEY")


def post(path, body, raw=False):
    req = urllib.request.Request("https://api.elevenlabs.io" + path, data=json.dumps(body).encode(),
                                 headers={"xi-api-key": api_key(), "Content-Type": "application/json"})
    try:
        data = urllib.request.urlopen(req, timeout=240).read()
    except urllib.error.HTTPError as e:
        raise SystemExit(f"ElevenLabs {e.code} {path}: {e.read()[:400]!r}")
    return data if raw else json.loads(data)


def metrics(path):
    y, sr = librosa.load(path, sr=22050, mono=True)
    y, _ = librosa.effects.trim(y, top_db=35)
    f0, voiced, _ = librosa.pyin(y, fmin=70, fmax=600, sr=sr)
    f0 = f0[voiced & ~np.isnan(f0)]
    semis = 12 * np.log2(f0 / np.median(f0))
    rms = librosa.feature.rms(y=y)[0]
    db = 20 * np.log10(rms[rms > 0.01] + 1e-9)
    cent = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    return {"pitch_var": float(np.std(semis)), "f0": float(np.median(f0)), "dyn": float(np.std(db)),
            "secs": len(y) / sr, "bright": float(np.median(cent))}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    cands = {}  # name -> (mp3 path, generated_voice_id or None)
    for key, desc in DESCS.items():
        if not (OUT / f"{key}_0.mp3").exists():
            d = post("/v1/text-to-voice/design", {"voice_description": desc, "model_id": "eleven_ttv_v3", "text": TEXT,
                                                  "seed": 21, "guidance_scale": 5})
            meta = {}
            for k, p in enumerate(d["previews"]):
                (OUT / f"{key}_{k}.mp3").write_bytes(base64.b64decode(p["audio_base_64"]))
                meta[f"{key}_{k}"] = p["generated_voice_id"]
            (OUT / f"{key}.json").write_text(json.dumps(meta), encoding="utf-8")
        for name, gid in json.loads((OUT / f"{key}.json").read_text(encoding="utf-8")).items():
            cands[name] = (OUT / f"{name}.mp3", gid)
    for name, vid in REFS.items():
        f = OUT / f"{name}.mp3"
        if not f.exists():
            f.write_bytes(post(f"/v1/text-to-speech/{vid}?output_format=mp3_44100_128",
                               {"text": TEXT, "model_id": "eleven_v3", "language_code": "es", "voice_settings": {"stability": 0.5}}, raw=True))
        cands[name] = (f, None)

    rows = {n: metrics(p) for n, (p, _) in cands.items()}
    keys = ["pitch_var", "dyn", "bright"]
    z = {k: (np.mean([r[k] for r in rows.values()]), np.std([r[k] for r in rows.values()]) + 1e-9) for k in keys + ["secs"]}
    for n, r in rows.items():
        r["score"] = sum((r[k] - z[k][0]) / z[k][1] for k in keys) - (r["secs"] - z["secs"][0]) / z["secs"][1]
    ranked = sorted(rows.items(), key=lambda kv: -kv[1]["score"])
    print(f"{'voz':14} {'tono±st':>8} {'f0':>6} {'dinám':>6} {'seg':>6} {'brillo':>7} {'score':>6}")
    for n, r in ranked:
        print(f"{n:14} {r['pitch_var']:8.2f} {r['f0']:6.0f} {r['dyn']:6.2f} {r['secs']:6.2f} {r['bright']:7.0f} {r['score']:6.2f}")
    (OUT / "ranking.json").write_text(json.dumps(ranked, indent=1), encoding="utf-8")

    best = next(n for n, _ in ranked if cands[n][1])  # best designed candidate (refs are not new voices)
    v = post("/v1/text-to-voice", {"voice_name": f"Narrador Puro Chisme ({best})", "voice_description": DESCS[best.rsplit('_', 1)[0]],
                                   "generated_voice_id": cands[best][1]})
    vf = ROOT / "audio/voices.json"
    ids = json.loads(vf.read_text(encoding="utf-8")) if vf.exists() else {}
    ids["narr"] = v["voice_id"]
    (ROOT / "audio/voices.json").write_text(json.dumps(ids, indent=1), encoding="utf-8")
    print(f"elegida: {best} -> {v['voice_id']}")


if __name__ == "__main__":
    main()
