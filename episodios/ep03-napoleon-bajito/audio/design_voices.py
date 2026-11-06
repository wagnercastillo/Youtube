"""Diseña y guarda las voces del EP03 con ElevenLabs Voice Design (plan Pro).

  python -I audio/design_voices.py

Pide 3 propuestas por personaje (eleven_ttv_v3), guarda las muestras en audio/voices/ y crea la
voz con la primera propuesta. Los ids quedan en audio/voices.json; si ya existen, no repite nada.
"""
import base64
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "audio" / "voices"
IDS = ROOT / "audio" / "voices.json"

# Español mexicano nativo: las voces con acento extranjero sonaron "robóticas" al usuario (EP02).
CAST = {
    "napo": {
        "name": "Napoleón (Puro Chisme)",
        "desc": ("Hombre mexicano de unos 40 años, voz de barítono teatral, altanera y muy expresiva, habla español "
                 "mexicano nativo con energía dramática, como un actor de doblaje de caricaturas haciendo de un "
                 "emperador ofendido. Grabación de estudio, limpia y cercana."),
        "text": ("¡¿Otra vez me dibujaste chiquito?! ¡Esto es una ofensa para todo el imperio! Mido un metro sesenta "
                 "y ocho, ¿me oíste? Normal para un francés de mi época. ¡Y mis soldados me dicen el cabito de cariño, "
                 "no por bajito! Ya verás cuando le cuente esto a Josefina."),
    },
    "gill": {
        "name": "Gillray (Puro Chisme)",
        "desc": ("Hombre mexicano de unos 55 años, voz un poco rasposa, burlona y pícara, tono relajado de chismoso "
                 "que disfruta molestar, habla español mexicano nativo, como un actor de doblaje de caricaturas. "
                 "Grabación de estudio, limpia y cercana."),
        "text": ("Ay, Napoleón, no te enojes… yo nomás dibujo lo que vende. Mides cinco pies con dos pulgadas, eso lo "
                 "dijo tu propio médico. Además siempre andas rodeado de tus guardias gigantes; junto a ellos pareces "
                 "llavero. Bueno, bueno, ya entendí… pero el chisme ya se regó."),
    },
}


def api_key():
    for d in [ROOT, *ROOT.parents]:
        env = d / ".env"
        if env.exists():
            for ln in env.read_text(encoding="utf-8").splitlines():
                if ln.strip().startswith("ELEVENLABS_API_KEY="):
                    return ln.split("=", 1)[1].strip().strip("\"'")
    raise SystemExit("falta ELEVENLABS_API_KEY en .env")


def post(path, body):
    req = urllib.request.Request("https://api.elevenlabs.io" + path, data=json.dumps(body).encode(),
                                 headers={"xi-api-key": api_key(), "Content-Type": "application/json"})
    try:
        return json.loads(urllib.request.urlopen(req, timeout=180).read())
    except urllib.error.HTTPError as e:
        raise SystemExit(f"ElevenLabs {e.code} {path}: {e.read()[:500]!r}")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    ids = json.loads(IDS.read_text(encoding="utf-8")) if IDS.exists() else {}
    for who, c in CAST.items():
        if who in ids:
            print(f"{who}: ya existe {ids[who]}")
            continue
        d = post("/v1/text-to-voice/design", {"voice_description": c["desc"], "model_id": "eleven_ttv_v3",
                                              "text": c["text"], "seed": 7})
        previews = d["previews"]
        for k, p in enumerate(previews):
            (OUT / f"{who}_{k}.mp3").write_bytes(base64.b64decode(p["audio_base_64"]))
        v = post("/v1/text-to-voice", {"voice_name": c["name"], "voice_description": c["desc"],
                                       "generated_voice_id": previews[0]["generated_voice_id"]})
        ids[who] = v["voice_id"]
        IDS.write_text(json.dumps(ids, indent=1), encoding="utf-8")
        print(f"{who}: {len(previews)} propuestas, guardada {ids[who]}")


if __name__ == "__main__":
    main()
