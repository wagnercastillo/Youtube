"""Música (Eleven Music) y efectos (Sound Effects) del EP04. Cachea: no repite lo que ya existe.

  python -I audio/gen_music_sfx.py
"""
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

MUSIC = ("Comedic 19th century Mexican-French underscore: playful accordion musette waltz feel crossed with a cheeky "
         "mariachi trumpet, pizzicato strings, light snare marching taps, mischievous gossip mood, 120 bpm, no vocals. "
         "A dramatic cannon-like hit section in the middle, a mock-solemn funeral march moment, then a bright comic ending.")
MUSIC_MS = 68000
SFX = {
    "register": ("Old cash register ka-ching, comedic", 1.0),
    "cannon": ("Single old naval cannon boom with short echo", 1.8),
    "crowd": ("Short angry crowd shouting, 19th century mob", 1.8),
    "taps": ("Short solemn military bugle funeral call, comedic", 2.5),
    "receipt": ("Receipt printer printing a short line, cartoon", 0.8),
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
