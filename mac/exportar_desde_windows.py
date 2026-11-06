"""Empaqueta lo que NO está en GitHub para pasarlo a la Mac mini. Corre en la computadora vieja (Windows):

  python -I mac/exportar_desde_windows.py

Crea en el Escritorio:
  puro-chisme-claude.zip     → skills de Claude Code (sin node_modules ni claves), memoria del proyecto, CLAUDE.md/RTK.md
                               globales, settings.json de referencia y la lista de plugins.
  puro-chisme-SECRETOS.zip   → .env del repo, research/.env, .env y token OAuth del youtube-uploader.
                               Pásalo SOLO por USB/AirDrop y bórralo después. Nunca a GitHub, correo ni chat.
"""
import json
import sys
import zipfile
from pathlib import Path

HOME = Path.home()
CLAUDE = HOME / ".claude"
REPO = Path(__file__).resolve().parent.parent
DESK = next((p for p in [HOME / "Desktop", HOME / "OneDrive" / "Desktop", HOME / "Escritorio"] if p.exists()), HOME)
SECRET_NAMES = {".env", ".youtube-token.json"}
SKIP_DIRS = {"node_modules", "__pycache__", ".git"}


def memory_dir():
    for d in (CLAUDE / "projects").iterdir():
        if d.name.lower().endswith("github-youtube") and (d / "memory").exists():
            return d / "memory"
    return None


def add_tree(z, src, arc, secrets):
    for f in src.rglob("*"):
        if not f.is_file() or SKIP_DIRS & set(f.relative_to(src).parts):
            continue
        is_secret = f.name in SECRET_NAMES
        if is_secret == secrets:
            z.write(f, f"{arc}/{f.relative_to(src).as_posix()}")


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    out = DESK / "puro-chisme-claude.zip"
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        add_tree(z, CLAUDE / "skills", "skills", secrets=False)
        mem = memory_dir()
        if mem:
            add_tree(z, mem, "memory", secrets=False)
        for name in ["CLAUDE.md", "RTK.md", "settings.json"]:
            if (CLAUDE / name).exists():
                z.write(CLAUDE / name, f"global/{name}")
        plugins = CLAUDE / "plugins" / "installed_plugins.json"
        settings = json.loads((CLAUDE / "settings.json").read_text(encoding="utf-8")) if (CLAUDE / "settings.json").exists() else {}
        z.writestr("plugins.json", json.dumps({
            "enabledPlugins": settings.get("enabledPlugins", {}),
            "extraKnownMarketplaces": settings.get("extraKnownMarketplaces", {}),
            "installed": list(json.loads(plugins.read_text(encoding="utf-8")).get("plugins", {})) if plugins.exists() else [],
        }, indent=1))
    print(f"ok {out} ({out.stat().st_size // 1024} KB)")

    sec = DESK / "puro-chisme-SECRETOS.zip"
    with zipfile.ZipFile(sec, "w", zipfile.ZIP_DEFLATED) as z:
        for f, arc in [(REPO / ".env", "repo/.env"), (REPO / "research" / ".env", "repo/research/.env")]:
            if f.exists():
                z.write(f, arc)
        add_tree(z, CLAUDE / "skills" / "youtube-uploader", "skills/youtube-uploader", secrets=True)
    print(f"ok {sec} — contiene CLAVES: pásalo solo por USB/AirDrop y bórralo después")


if __name__ == "__main__":
    main()
