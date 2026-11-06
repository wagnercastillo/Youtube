"""Diseña y guarda la voz del EP04 con ElevenLabs Voice Design (plan Pro).

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
    "narr": {
        "name": "Narradora energética (Puro Chisme)",
        "desc": ("Mujer mexicana joven de unos 25 años, voz brillante, sonriente y SÚPER energética, como una creadora de "
                 "contenido de TikTok contando el chisme más emocionante del día: ritmo rápido, mucha emoción, subidas de "
                 "tono y risas. Español mexicano nativo. Grabación de estudio, limpia y cercana."),
        "text": ("Ay, no sabes… te tengo un chisme del antiguo Egipto que te va a volar la cabeza. Cleopatra, la reina "
                 "más famosa de todas, vivió más cerca de nosotros que de las pirámides. ¿Cómo la ves? Y espérate, que "
                 "todavía hay más: cuando terminaron la Gran Pirámide, ¡todavía había mamuts vivos! Así como lo oyes."),
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
