"""Música (Eleven Music) y efectos (Sound Effects) del EP17. Cachea: no repite lo que ya existe.

  python -I audio/gen_music_sfx.py
"""
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

MUSIC = ('Comic baroque harpsichord with pizzicato strings, playful and mischievous, 100 bpm, no vocals. Light bassoon accents, '
         'a sneaky middle section, a small triumphant flourish near the end.')
MUSIC_MS = 70000
SFX = {
    "clac": ('Loud slap of a thick cardboard sheet hitting a wooden table, crisp paper thwack', 0.6),
    "scissors": ('Scissors cutting paper, two quick snips', 0.8),
    "stamp": ('Loud punchy cartoon impact thud, like a judge gavel bang', 0.7),
    "wave": ('Ocean wave crashing, short', 1.2),
    "gulls": ('Seagulls calling over the sea, short', 1.5),
    "ding": ('Small bright bell ding, correct answer', 0.7),
    "buzz": ('Wrong answer buzzer, cartoon', 0.8),
    "crash": ('Wooden ship bumping into land, comic crunch', 1.0),
    "gasp": ('Small crowd gasp in surprise', 1.2),
    "chalk": ('Chalk writing quickly on a blackboard', 1.2),
}


def api_key():
    for d in [ROOT, *ROOT.parents]:
        env = d / ".env"
        if env.exists():
            for ln in env.read_text(encoding="utf-8").splitlines():
                if ln.strip().startswith("ELEVENLABS_API_KEY="):
                    return ln.split("=", 1)[1].strip().strip("\"'")
    raise SystemExit("falta ELEVENLABS_API_KEY en .env")


def post(path, body, dest):
    if dest.exists():
        return print(f"ya existe {dest.name}")
    req = urllib.request.Request("https://api.elevenlabs.io" + path, data=json.dumps(body).encode(),
                                 headers={"xi-api-key": api_key(), "Content-Type": "application/json"})
    try:
        dest.write_bytes(urllib.request.urlopen(req, timeout=300).read())
        print(f"ok {dest.name} {dest.stat().st_size // 1024} KB")
    except urllib.error.HTTPError as e:
        print(f"ElevenLabs {e.code} {path}: {e.read()[:400]!r}")


def main():
    (OUT / "sfx").mkdir(parents=True, exist_ok=True)
    post("/v1/music?output_format=mp3_44100_128", {"prompt": MUSIC, "music_length_ms": MUSIC_MS,
                                                   "model_id": "music_v1", "force_instrumental": True},
         OUT / "music.mp3")
    for name, (text, dur) in SFX.items():
        post("/v1/sound-generation?output_format=mp3_44100_128",
             {"text": text, "duration_seconds": dur, "prompt_influence": 0.5}, OUT / "sfx" / f"el_{name}.mp3")


if __name__ == "__main__":
    main()
