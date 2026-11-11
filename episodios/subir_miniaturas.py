"""Sube renders/miniatura.jpg a YouTube para cada episodio con video id; idempotente (marca renders/.miniatura_subida).

Uso: python -I episodios/subir_miniaturas.py        (reintenta solo las pendientes; la API limita miniaturas por dia)
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = Path.home() / ".claude" / "skills" / "youtube-uploader" / "scripts"
VIDEOS = {
    "ep02-mexicas-sin-gallinas": "dHAw-I9apCA", "ep03-napoleon-bajito": "qFrFHyuc5XY", "ep04-cleopatra-luna": "Qc5h3AWFZUA",
    "ep05-guerra-pasteles": "GkWldQHAopY", "ep06-yucatan-subasta": "-0FNeL8xsq8", "ep07-juicio-papa-muerto": "LpFhBIDnlKs",
    "ep08-onoda-chat": "IzUKGpuf30k", "ep09-plaga-del-baile": "56edefRgceM", "ep10-adidas-puma": "pDipjdlz8tI",
    "ep10-diogenes-alejandro": "Vbu5ML0NVdM", "ep11-guerra-del-cerdo": "CVLi2mJlFSg", "ep12-torre-pisa": "svm_fQwD5jk",
    "ep13-vendio-torre-eiffel": "mHEE-qgFfuI", "ep14-garbo-espia": "YHejqjAuR8A", "ep15-otzi-noticiero": "XCPbJgqM-Rc",
    "ep16-socrates-xantipa": "93dwScPP1go",
}

if __name__ == "__main__":
    pendientes = 0
    for slug, vid in VIDEOS.items():
        marca = ROOT / slug / "renders" / ".miniatura_subida"
        jpg = ROOT / slug / "renders" / "miniatura.jpg"
        if marca.exists() or not jpg.exists():
            continue
        r = subprocess.run(["npx.cmd", "ts-node", "set-thumbnail.ts", vid, str(jpg)], cwd=SCRIPTS, capture_output=True, text=True)
        out = (r.stdout + r.stderr).strip().splitlines()[-1] if (r.stdout + r.stderr).strip() else "?"
        print(slug, vid, out[:90])
        if r.returncode == 0 and out.startswith("ok"):
            marca.write_text(vid)
        else:
            pendientes += 1
            if "too many thumbnails" in out:
                break  # cuota diaria: reintentar mas tarde
    sys.exit(1 if pendientes else 0)
