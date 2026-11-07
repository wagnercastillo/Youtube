"""Sube el EP10 privado y lo programa en el primer turno libre. Lo lanza el Programador de tareas cada hora;
si YouTube sigue con el límite diario de subidas, sale y reintenta en la siguiente hora. Cuando sube, deja renders/.subido.

  python -I audio/subir_programado.py            (manual)
  python -I audio/subir_programado.py --selftest
"""
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

EP = Path(__file__).resolve().parent.parent
UP = Path.home() / ".claude/skills/youtube-uploader/scripts"
TSNODE = UP / "node_modules/ts-node/dist/bin.js"  # node directo: el shim de npx en Windows pierde argumentos con acentos
TITLE = "Le dijo QUÍTATE a Alejandro Magno 😳☀️"
MARK, LOG = EP / "renders/.subido", EP / "audio/subida.log"
# 12 pm / 4 pm CDMX; las 8 pm (02:00Z) chocan con EP08/EP09 ya programados a las 01:00Z
SLOTS = ["2026-11-07T18:00:00Z", "2026-11-07T22:00:00Z", "2026-11-08T18:00:00Z", "2026-11-08T22:00:00Z",
         "2026-11-09T18:00:00Z", "2026-11-09T22:00:00Z", "2026-11-10T18:00:00Z"]


def pick_slot(now):
    for s in SLOTS:
        if dt.datetime.fromisoformat(s.replace("Z", "+00:00")) >= now + dt.timedelta(minutes=45):
            return s
    return None


def log(msg):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%dT%H:%M:%SZ} {msg}\n")


def ts(*args):
    r = subprocess.run(["node", str(TSNODE), *args], cwd=UP, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


def main():
    if MARK.exists():
        return
    now = dt.datetime.now(dt.timezone.utc)
    slot = pick_slot(now)
    if not slot:
        return log("sin turno libre en SLOTS; no se sube")
    code, out = ts("youtube-upload.ts", "--video", str(EP / "renders/ep10-diogenes-alejandro.mp4"),
                   "--description-file", str(EP / "youtube_description.txt"), "--category", "27", "--privacy", "private",
                   "--title", TITLE)
    m = re.search(r"Video ID: (\S+)", out)
    if not m:
        return log("subida falló (se reintenta en 1 h): " + " | ".join(out.strip().splitlines()[-2:]))
    vid = m.group(1)
    MARK.write_text(vid, encoding="utf-8")
    code, out2 = ts("update-video.ts", vid, str(EP / "youtube_description.txt"), "27", slot, str(EP / "youtube_tags.txt"))
    log(f"subido https://youtu.be/{vid}; programado {slot}: " + " ".join(out2.split()))
    with (EP / "ESTADO.md").open("a", encoding="utf-8") as f:
        f.write(f"\nSUBIDO {now:%Y-%m-%d} (tarea programada): https://youtu.be/{vid} · publishAt {slot} · update: {'ok' if code == 0 else 'ERROR, revisar'}\n")


def selftest():
    u = lambda s: dt.datetime.fromisoformat(s)
    assert pick_slot(u("2026-11-07T13:00:00+00:00")) == "2026-11-07T18:00:00Z"
    assert pick_slot(u("2026-11-07T17:30:00+00:00")) == "2026-11-07T22:00:00Z"
    assert pick_slot(u("2026-11-11T00:00:00+00:00")) is None
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
