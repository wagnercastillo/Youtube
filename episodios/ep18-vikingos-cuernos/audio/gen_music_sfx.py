"""Música (Eleven Music) y efectos (Sound Effects) del EP18. Cachea: no repite lo que ya existe.

  python -I audio/gen_music_sfx.py
"""
import json
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets"

MUSIC = ('Playful nordic folk with pizzicato strings, frame drum, tin whistle and a bouncy tuba, cheeky and mischievous, 105 bpm, '
         'no vocals. A sneaky quiet middle, a mock-heroic opera flourish in the second half, a small triumphant ending.')
MUSIC_MS = 70000
SFX = {
    "pencil": ('Pencil sketching quickly on paper, scratchy graphite strokes, close up', 1.2),
    "eraser": ('Rubber eraser rubbing hard on paper, three quick back and forth strokes', 1.2),
    "marker": ('Felt tip marker squeaking on paper, quick X mark', 0.8),
    "page": ('Notebook page flipping over, crisp paper turn', 0.8),
    "horn": ('Short comic viking war horn blast, deflated at the end', 1.4),
    "stomp": ('Cartoon tantrum, heavy feet stomping on wooden floor four times', 1.4),
    "applause": ('Small theatre audience applause, short', 1.8),
    "stamp": ('Loud punchy cartoon impact thud, like a judge gavel bang', 0.7),
    "ding": ('Small bright bell ding, correct answer', 0.7),
    "buzz": ('Wrong answer buzzer, cartoon', 0.8),
    "gasp": ('Small crowd gasp in surprise', 1.2),
    "scissors": ('Scissors cutting paper, two quick snips', 0.8),
    "axe": ('Cartoon axe swoosh and thunk into wood', 0.8),
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
