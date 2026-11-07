"""Música (Eleven Music) y efectos (Sound Effects) del EP13. Cachea: no repite lo que ya existe.

  python -I audio/gen_music_sfx.py
"""
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

MUSIC = ('1920s Paris gypsy jazz swing, sneaky con-man caper, clarinet and muted trumpet, upright bass, brushed drums, accordion touches, tempo 132 bpm, no vocals. Playful and mischievous, a tense pause in the middle, then a cheeky finish.')
MUSIC_MS = 48000
SFX = {
    "paper": ('Newspaper page rustle and flip', 0.8),
    "type": ('Old typewriter typing burst with bell', 1.2),
    "glass": ('Champagne cork pop and glasses clink', 1.0),
    "shh": ('Soft whisper shush', 0.8),
    "cash": ('Old cash register cha-ching', 0.8),
    "run": ('Cartoon footsteps running away fast', 1.2),
    "whistle": ('Police whistle blowing', 1.0),
    "cuffs": ('Handcuffs clicking shut', 0.6),
    "clang": ('Heavy prison cell door slam clang', 1.5),
    "ding": ('Cartoon ding', 0.6),
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
