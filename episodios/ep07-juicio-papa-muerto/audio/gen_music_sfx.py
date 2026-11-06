"""Música (Eleven Music) y efectos (Sound Effects) del EP07. Cachea: no repite lo que ya existe.

  python -I audio/gen_music_sfx.py
"""
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

MUSIC = ("Comedic gothic courtroom underscore: pizzicato strings, church organ stabs, harpsichord, sneaky bassoon, playful "
         "spooky tempo 120 bpm, like a dark comedy cartoon trial, no vocals. A dramatic organ chord hit in the middle, a "
         "splashy comic section, then a triumphant choir-like brass ending.")
MUSIC_MS = 64000
SFX = {
    "organ": ("Dramatic church organ chord sting, spooky and comedic", 2.0),
    "gavel": ("Single heavy wooden judge gavel bang", 1.0),
    "dig": ("Shovel digging into dirt, two quick scoops", 1.2),
    "creak": ("Old coffin lid creaking open slowly", 1.5),
    "gasp": ("Small crowd gasping in shock inside a church", 1.5),
    "splash": ("Big comedic splash of something falling into a river", 1.5),
    "bones": ("Cartoon bones rattling and clattering", 1.0),
    "crowd": ("Angry medieval crowd shouting and booing", 2.0),
    "bars": ("Heavy iron jail cell door slamming shut", 1.2),
    "fanfare": ("Short triumphant royal trumpet fanfare", 2.0),
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
