"""Cola de subidas a YouTube: sube cada episodio privado y lo programa (publishAt). Idempotente: un episodio subido deja
renders/.subido con su id y no se vuelve a subir. Si YouTube responde con el límite diario de subidas, se detiene y la
siguiente corrida (Programador de tareas, cada hora) sigue donde se quedó.

  python -I episodios/subir_cola.py            (sube lo pendiente)
  python -I episodios/subir_cola.py --selftest
"""
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

EPS = Path(__file__).resolve().parent
UP = Path.home() / ".claude/skills/youtube-uploader/scripts"
TSNODE = UP / "node_modules/ts-node/dist/bin.js"  # node directo: el shim de npx en Windows pierde argumentos con acentos
LOG = EPS / "subida_cola.log"
# (carpeta, título, publishAt UTC). CDMX = UTC−6: 18Z = 12 pm, 20Z = 2 pm, 22Z = 4 pm, 03Z = 9 pm (EP08 sale a las 7 pm = 01Z)
QUEUE = [
    ("ep10-diogenes-alejandro", "Le dijo QUÍTATE a Alejandro Magno 😳☀️", "2026-11-07T18:00:00Z"),
    ("ep13-vendio-torre-eiffel", "Vendió la TORRE EIFFEL… ¡y quiso venderla OTRA VEZ! 🗼💸", "2026-11-07T20:00:00Z"),
    ("ep12-torre-pisa", "¡Estoy CHUECA desde antes de que me terminaran! 🇮🇹😳", "2026-11-07T22:00:00Z"),
    ("ep11-guerra-del-cerdo", "¡Casi una GUERRA por un CERDO! 🐷💥 (1859)", "2026-11-08T03:00:00Z"),
    ("ep07-juicio-papa-muerto", "Desenterraron a un papa… ¡para JUZGARLO! 💀⚖️", "2026-11-08T18:00:00Z"),  # re-subida: el dueño borró la anterior
    ("ep15-otzi-noticiero", "¡ÚLTIMA HORA! Hallan un ASESINATO de hace 5,000 años 🧊🏹", "2026-11-09T18:00:00Z"),
    ("ep16-socrates-xantipa", "Sócrates vs su ESPOSA: ¡le echó una cubeta de agua! 💦🏛️", "2026-11-09T22:00:00Z"),
    ("ep14-garbo-espia", "Engañó a HITLER… ¡y Hitler le dio una MEDALLA! 🕵️🎖️", "2026-11-10T02:00:00Z"),
    ("ep10-adidas-puma", "Dos hermanos se odiaron tanto… que crearon Adidas y Puma 👟💔", "2026-11-10T18:00:00Z"),  # v2 Blender
]


def when(slot, now):
    """The planned slot, or (if it is too close or already past) the next whole hour + 1 h."""
    t = dt.datetime.fromisoformat(slot.replace("Z", "+00:00"))
    if t >= now + dt.timedelta(minutes=45):
        return slot
    nxt = now.replace(minute=0, second=0, microsecond=0) + dt.timedelta(hours=2)
    return nxt.strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg):
    with LOG.open("a", encoding="utf-8") as f:
        f.write(f"{dt.datetime.now(dt.timezone.utc):%Y-%m-%dT%H:%M:%SZ} {msg}\n")
    print(msg)


def ts(*args):
    r = subprocess.run(["node", str(TSNODE), *args], cwd=UP, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return r.returncode, r.stdout + r.stderr


def main():
    for ep, title, slot in QUEUE:
        d = EPS / ep
        mark = d / "renders/.subido"
        if mark.exists():
            continue
        now = dt.datetime.now(dt.timezone.utc)
        code, out = ts("youtube-upload.ts", "--video", str(d / f"renders/{ep}.mp4"), "--description-file", str(d / "youtube_description.txt"),
                       "--category", "27", "--privacy", "private", "--title", title)
        m = re.search(r"Video ID: (\S+)", out)
        if not m:
            return log(f"{ep}: subida falló (reintento en 1 h): " + " | ".join(out.strip().splitlines()[-2:]))
        vid = m.group(1)
        mark.write_text(vid, encoding="utf-8")
        at = when(slot, dt.datetime.now(dt.timezone.utc))
        code, out2 = ts("update-video.ts", vid, str(d / "youtube_description.txt"), "27", at, str(d / "youtube_tags.txt"))
        log(f"{ep}: https://youtu.be/{vid} programado {at} ({'ok' if code == 0 else 'ERROR update: ' + out2.strip()[-200:]})")
        with (d / "ESTADO.md").open("a", encoding="utf-8") as f:
            f.write(f"\nSUBIDO {now:%Y-%m-%d} (cola): https://youtu.be/{vid} · publishAt {at} · update {'ok' if code == 0 else 'ERROR'}\n")


def selftest():
    u = lambda s: dt.datetime.fromisoformat(s)
    assert when("2026-11-07T18:00:00Z", u("2026-11-07T14:05:00+00:00")) == "2026-11-07T18:00:00Z"
    assert when("2026-11-07T18:00:00Z", u("2026-11-07T17:30:00+00:00")) == "2026-11-07T19:00:00Z"
    print("selftest ok")


if __name__ == "__main__":
    selftest() if "--selftest" in sys.argv else main()
