"""Música (Eleven Music) y efectos (Sound Effects) del EP14. Cachea: no repite lo que ya existe.

  python -I audio/gen_music_sfx.py
"""
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

MUSIC = ('1940s spy noir jazz, sneaky walking upright bass, vibraphone, muted trumpet stabs, brushed snare, mysterious and playful, tempo 104 bpm, no vocals. Builds tension in the middle with a military snare, a triumphant brass hit, then a cheeky sly ending.')
MUSIC_MS = 52000
SFX = {
    "type": ('Old typewriter typing burst with bell', 1.2),
    "morse": ('Morse code radio beeps, vintage radio static', 1.5),
    "stamp": ('Rubber stamp thump on paper', 0.6),
    "pin": ('Push pin pressed into cork board, small click', 0.5),
    "flash": ('Old camera flash bulb pop', 0.8),
    "paper": ('Paper document slide on desk', 0.8),
    "medal": ('Metal medal clink and short fanfare', 1.5),
    "sting": ('Dramatic spy movie sting, short', 1.5),
    "cash": ('Coins and cash register', 0.8),
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
