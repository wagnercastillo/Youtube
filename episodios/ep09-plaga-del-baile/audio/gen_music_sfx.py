"""Música (Eleven Music) y efectos (Sound Effects) del EP09. Cachea: no repite lo que ya existe.

  python -I audio/gen_music_sfx.py
"""
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

MUSIC = ("8-bit chiptune medieval dance tune, square wave lute melody, tambourine and drum, catchy and frantic, tempo 120 bpm, "
         "retro video game level music, no vocals. Gets faster and more chaotic in the middle, a short power-down slowdown, "
         "then a calm church-organ chiptune ending.")
MUSIC_MS = 60000
SFX = {
    "coin": ("Retro 8-bit video game coin pickup sound", 0.6),
    "levelup": ("Retro 8-bit video game level up jingle", 1.5),
    "powerdown": ("Retro 8-bit video game power down, energy draining", 1.5),
    "gameover": ("Retro 8-bit video game over jingle, short", 2.0),
    "start": ("Retro 8-bit video game start jingle", 1.2),
    "crowd8": ("Retro 8-bit crowd cheering sound effect", 1.5),
    "bell": ("Church bell single toll, retro 8-bit style", 1.5),
    "glitch": ("Retro 8-bit glitch mystery sound", 1.0),
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
