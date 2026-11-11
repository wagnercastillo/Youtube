"""Casting del anfitrión fijo de Puro Chisme: 5 personajes × 3 previews de ElevenLabs Voice Design.

  ~/.chatterbox-py/Scripts/python.exe -I marca/anfitriones/audition.py          (genera previews y ranking)
  ~/.chatterbox-py/Scripts/python.exe -I marca/anfitriones/audition.py --save mironc_1   (guarda la elegida)

Las previews NO ocupan espacio de voz (límite 10); solo --save crea la voz. Cachea en voces/ (borra un .json para regenerar).
Métrica de "llama la atención": variación de tono, dinámica de volumen, brillo y velocidad (z-scores dentro de cada personaje).
"""
import base64
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

import librosa
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE / "voces"
TAIL = " Español mexicano nativo, sin acento extranjero. Grabación de estudio nítida."
HOSTS = {
    "miron": ("El Mirón",
              "Hombre mexicano de 30 años, voz rasposa, traviesa y cómplice; empieza en susurro y explota de emoción, ritmo rápido, muy expresivo y carismático." + TAIL,
              "¡Psst! ¡Oye, tú! Sí, tú… acércate tantito, que lo que vi detrás de esta barda no lo vas a creer. ¿Listo para el chisme?"),
    "locutor": ("El Locutor de Radio Chisme",
                "Locutor de radio AM mexicano de 50 años, voz grave, resonante y potente, enérgica, entonación de anuncio de radio clásico, sonrisa en la voz." + TAIL,
                "¡Buenas, buenas, mi gente! Están sintonizando Radio Chisme, la única estación donde la historia viene con todo y escándalo. ¡Agárrense!"),
    "merolico": ("El Merolico",
                 "Vendedor ambulante mexicano de 40 años, pregonero de mercado, voz potente y un poco nasal, habla muy rápido y cantadito, carismático y gracioso." + TAIL,
                 "¡Pásele, pásele, marchanta! Hoy traigo chisme fresquecito de hace quinientos años, ¡calientito y bien verificado! ¡Ándele, que se acaba!"),
    "tecolote": ("El Tecolote",
                 "Hombre mexicano de 60 años, voz grave, misteriosa y aterciopelada, habla pausado con picardía, tono de complicidad nocturna, pausas de suspenso." + TAIL,
                 "Uuuh… yo de noche no duermo, ¿eh? Yo observo. Y esta noche vi algo que los libros de historia no te quieren contar. ¿Te lo cuento?"),
    "calacas": ("Don Calacas",
                "Anciano mexicano de 75 años, voz aguda, chillona y risueña, se ríe a carcajadas mientras cuenta, mucha energía, cómico y exagerado." + TAIL,
                "¡Ay, no, no, no! Yo estuve ahí, ¿eh? Hace como trescientos años, pero me acuerdo clarito. Y lo que pasó ese día… ¡fue un escándalo!"),
}


def api_key():
    for d in HERE.parents:
        env = d / ".env"
        if env.exists():
            for ln in env.read_text(encoding="utf-8").splitlines():
                if ln.strip().startswith("ELEVENLABS_API_KEY="):
                    return ln.split("=", 1)[1].strip().strip("\"'")
    raise SystemExit("falta ELEVENLABS_API_KEY")


def post(path, body):
    req = urllib.request.Request("https://api.elevenlabs.io" + path, data=json.dumps(body).encode(),
                                 headers={"xi-api-key": api_key(), "Content-Type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=240).read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"ElevenLabs {e.code} {path}: {e.read()[:400]!r}")


def metrics(path):
    y, sr = librosa.load(path, sr=22050, mono=True)
    y, _ = librosa.effects.trim(y, top_db=35)
    f0, voiced, _ = librosa.pyin(y, fmin=60, fmax=600, sr=sr)
    f0 = f0[voiced & ~np.isnan(f0)]
    rms = librosa.feature.rms(y=y)[0]
    return {"pitch_var": float(np.std(12 * np.log2(f0 / np.median(f0)))), "f0": float(np.median(f0)),
            "dyn": float(np.std(20 * np.log10(rms[rms > 0.01] + 1e-9))), "secs": len(y) / sr,
            "bright": float(np.median(librosa.feature.spectral_centroid(y=y, sr=sr)[0]))}


def design():
    OUT.mkdir(exist_ok=True)
    rank = {}
    for key, (name, desc, text) in HOSTS.items():
        meta_f = OUT / f"{key}.json"
        if not meta_f.exists():
            assert len(text) >= 100, f"{key}: la frase de prueba necesita ≥100 caracteres"
            d = post("/v1/text-to-voice/design", {"voice_description": desc, "model_id": "eleven_ttv_v3", "text": text,
                                                  "seed": 7, "guidance_scale": 5})
            meta = {}
            for k, p in enumerate(d["previews"]):
                (OUT / f"{key}_{k}.mp3").write_bytes(base64.b64decode(p["audio_base_64"]))
                meta[f"{key}_{k}"] = p["generated_voice_id"]
            meta_f.write_text(json.dumps(meta, indent=1), encoding="utf-8")
        meta = json.loads(meta_f.read_text(encoding="utf-8"))
        rows = {n: metrics(OUT / f"{n}.mp3") for n in meta}
        ks = ["pitch_var", "dyn", "bright"]
        z = {k: (np.mean([r[k] for r in rows.values()]), np.std([r[k] for r in rows.values()]) + 1e-9) for k in ks + ["secs"]}
        for r in rows.values():
            r["score"] = round(sum((r[k] - z[k][0]) / z[k][1] for k in ks) - (r["secs"] - z["secs"][0]) / z["secs"][1], 2)
        rank[key] = sorted(rows.items(), key=lambda kv: -kv[1]["score"])
        print(f"== {name}")
        for n, r in rank[key]:
            print(f"  {n:12} tono {r['pitch_var']:5.2f} f0 {r['f0']:4.0f} din {r['dyn']:5.2f} seg {r['secs']:5.2f} brillo {r['bright']:5.0f} score {r['score']:5.2f}")
    (OUT / "ranking.json").write_text(json.dumps({k: [[n, r] for n, r in v] for k, v in rank.items()}, indent=1), encoding="utf-8")


def save(preview):
    key = preview.rsplit("_", 1)[0]
    gid = json.loads((OUT / f"{key}.json").read_text(encoding="utf-8"))[preview]
    v = post("/v1/text-to-voice", {"voice_name": f"Anfitrión {HOSTS[key][0]}", "voice_description": HOSTS[key][1], "generated_voice_id": gid})
    (HERE / "voz_elegida.json").write_text(json.dumps({"host": key, "preview": preview, "voice_id": v["voice_id"]}, indent=1), encoding="utf-8")
    print("guardada", preview, "->", v["voice_id"])


if __name__ == "__main__":
    save(sys.argv[2]) if "--save" in sys.argv else design()
