"""Música (Eleven Music) y efectos (Sound Effects) del EP08. Cachea: no repite lo que ya existe.

  python -I audio/gen_music_sfx.py
"""
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

MUSIC = ("Playful comedic suspense underscore with taiko drums, shakuhachi flute, marimba and pizzicato strings, a ticking "
         "clock feel, tempo 112 bpm, light jungle adventure mood, no vocals. A long building section in the middle as years "
         "pass, a sudden stop, then a warm triumphant ending.")
MUSIC_MS = 62000
SFX = {
    "ding": ("Short soft phone message notification ding", 0.6),
    "send": ("Short phone message sent swoosh", 0.5),
    "typing": ("Fast phone keyboard typing clicks, short", 0.8),
    "paper": ("Paper leaflets fluttering down from the sky", 1.5),
    "clock": ("Fast clock ticking, time passing quickly", 3.0),
    "jungle": ("Jungle ambience with birds and insects, short", 3.0),
    "footsteps": ("Footsteps walking through jungle leaves", 1.2),
    "tada": ("Short comedic victory chime", 1.5),
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
