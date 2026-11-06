"""Casting EP07 por rol (narr, esteban, diacono): diseña candidatas, las mide y guarda la mejor de cada rol.

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
ROLES = {  # role -> (test line, {candidate: description}); each role is cast on its own line
    "narr": ("¿Sabías que una vez sentaron a un papa MUERTO en el banquillo de los acusados? ¡Lo vistieron, lo sentaron en un trono… "
             "y le hicieron un juicio! Ay, no, no, no… ¡en Roma ni muerto te salvas del chisme!",
             {"reportera": ("Reportera de espectáculos mexicana de 30 años, voz brillante, rápida y chismosa, cuenta el chisme con "
                            "asombro y risas, muy expresiva y teatral. Español mexicano nativo. Grabación de estudio nítida."),
              "comadre": ("Señora mexicana de 45 años contando un chisme jugoso en la tienda de la esquina, voz cálida, picara, rápida, "
                          "con exclamaciones y suspiros dramáticos. Español mexicano nativo. Grabación de estudio nítida.")}),
    "esteban": ("¡Formoso! ¡Eras obispo de Porto y te hiciste papa! ¡Eso está prohibido! ¿Qué tienes que decir en tu defensa? ¿Nada? ¡Culpable! ¡CULPABLE!",
                {"papa_furioso": ("Hombre mayor de 60 años, voz grave y ronca, furioso y teatral, grita como un villano de telenovela "
                                  "mexicana, con mucha rabia exagerada y cómica. Español mexicano nativo. Grabación de estudio nítida."),
                 "juez": ("Juez mexicano de 55 años, voz potente y autoritaria, se enoja y grita con dramatismo exagerado, tono cómico. "
                          "Español mexicano nativo. Grabación de estudio nítida.")}),
    "diacono": ("Eh… ¿que… soy inocente? Digo… dice que… es inocente, su santidad. Ay, Dios mío, ¿por qué siempre me toca a mí hablar por los muertos?",
                {"nervioso": ("Joven mexicano de 22 años, voz aguda y temblorosa, muy nervioso y asustado, tartamudea, cómico. "
                              "Español mexicano nativo. Grabación de estudio nítida."),
                 "monaguillo": ("Monaguillo mexicano de 25 años, voz suave y chillona, nervioso, habla rápido y con miedo, tono "
                                "cómico. Español mexicano nativo. Grabación de estudio nítida.")}),
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
        v = post("/v1/text-to-voice", {"voice_name": f"EP07 {role} ({best})", "voice_description": descs[best.rsplit('_', 1)[0]],
                                       "generated_voice_id": cands[best][1]})
        ids[role] = v["voice_id"]
        vf.write_text(json.dumps(ids, indent=1), encoding="utf-8")
        print(f"elegida {role}: {best} -> {v['voice_id']}")


if __name__ == "__main__":
    main()
