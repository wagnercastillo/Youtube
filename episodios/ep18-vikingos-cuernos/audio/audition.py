"""Casting EP18 por rol: diseña candidatas, las mide y guarda la mejor de cada rol.

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
ROLES = {
 'narr':    ('¿Los vikingos usaban cascos con cuernos? ¡Mentira! Y el que se los puso ni siquiera era vikingo: era un diseñador de ópera.',
             {'caricaturista': 'Hombre mexicano de 30 años, caricaturista chismoso y bromista, voz clara y juvenil, rápida, con risa contenida, como contando un secreto mientras dibuja. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.',
              'dibujante': 'Hombre mexicano de 35 años, ilustrador pícaro y carismático, voz cálida y brillante, ritmo ágil con pausas de suspenso, muy expresivo. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.'}),
 'bjorn':   ('¡Dibújamelos, compadre! Bien grandotes, para que me tengan miedo. ¿Cero? ¿Y entonces cómo asusto a la gente?',
             {'grandote': 'Hombre mexicano de 40 años, guerrero grandote y bonachón, voz muy grave y retumbante, presumido pero ingenuo, cómico. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.',
              'ronco': 'Hombre mexicano de 45 años, voz ronca y fuerte de luchador, exagerado y berrinchudo como niño grande, divertido. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.'}),
 'doepler': ('¡Se veían divinos en el escenario! ¿Qué querían, que salieran con gorrito? El público quiere espectáculo.',
             {'vestuarista': 'Hombre mexicano de 55 años, diseñador de vestuario teatral, voz aguda, rápida y afectada, ofendido con elegancia, muy dramático. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.',
              'artista': 'Hombre mexicano de 60 años, artista de ópera vanidoso, voz nasal y cantarina, exagera cada palabra, cómico. Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida.'}),
}


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
    vf = ROOT / "audio/voices.json"
    ids = json.loads(vf.read_text(encoding="utf-8")) if vf.exists() else {}
    for role, (text, descs) in ROLES.items():
        if role in ids:
            continue
        cands = {}
        for key, desc in descs.items():
            if not (OUT / f"{key}.json").exists():
                d = post("/v1/text-to-voice/design", {"voice_description": desc, "model_id": "eleven_ttv_v3", "text": text,
                                                      "seed": 21, "guidance_scale": 5})
                meta = {}
                for k, p in enumerate(d["previews"]):
                    (OUT / f"{key}_{k}.mp3").write_bytes(base64.b64decode(p["audio_base_64"]))
                    meta[f"{key}_{k}"] = p["generated_voice_id"]
                (OUT / f"{key}.json").write_text(json.dumps(meta), encoding="utf-8")
            for name, gid in json.loads((OUT / f"{key}.json").read_text(encoding="utf-8")).items():
                cands[name] = (OUT / f"{name}.mp3", gid)
        rows = {n: metrics(p) for n, (p, _) in cands.items()}
        keys = ["pitch_var", "dyn", "bright"]
        z = {k: (np.mean([r[k] for r in rows.values()]), np.std([r[k] for r in rows.values()]) + 1e-9) for k in keys + ["secs"]}
        for n, r in rows.items():
            r["score"] = sum((r[k] - z[k][0]) / z[k][1] for k in keys) - (r["secs"] - z["secs"][0]) / z["secs"][1]
        ranked = sorted(rows.items(), key=lambda kv: -kv[1]["score"])
        print(f"== {role}")
        for n, r in ranked:
            print(f"{n:14} tono {r['pitch_var']:5.2f} f0 {r['f0']:4.0f} din {r['dyn']:5.2f} seg {r['secs']:5.2f} brillo {r['bright']:5.0f} score {r['score']:5.2f}")
        best = ranked[0][0]
        v = post("/v1/text-to-voice", {"voice_name": f"EP18 {role} ({best})", "voice_description": descs[best.rsplit('_', 1)[0]],
                                       "generated_voice_id": cands[best][1]})
        ids[role] = v["voice_id"]
        vf.write_text(json.dumps(ids, indent=1), encoding="utf-8")
        print(f"elegida {role}: {best} -> {v['voice_id']}")


if __name__ == "__main__":
    main()
