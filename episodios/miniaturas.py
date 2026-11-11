"""Miniaturas verticales (1080x1920) para los Shorts publicados.

Uso:  python -I episodios/miniaturas.py [ep12 ep14 ...]   (sin argumentos: todas)
Para cada episodio: saca un cuadro del render con ffmpeg, lo encuadra (zoom + foco),
le pone el gancho en texto gigante y la marca, y lo captura con Chrome headless en
renders/miniatura.jpg (<2 MB). Luego arma renders/../miniaturas_hoja.jpg para revisarlas.

Regla de diseño: en la cuadricula de Shorts la miniatura mide ~150 px de ancho, asi que
una cara/objeto grande + 3-6 palabras enormes + logo pequeno. Nada de texto de subtitulos.
"""
import html
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
LOGO = (ROOT.parent / "marca" / "puro-chisme-800.png").as_uri()

# t = segundo del render; zoom/fx/fy = encuadre (foco en fraccion del cuadro);
# top = caja amarilla (1 linea); big = texto blanco gigante (<=3 lineas); sub = remate chico;
# emoji = sticker grande.
EPISODIOS = {
    "ep02-mexicas-sin-gallinas": dict(t=21.7, zoom=1.5, fx=0.45, fy=0.42, top="LOS MEXICAS", big="NUNCA VIERON UNA GALLINA", sub="¿entonces qué comían?", emoji="🐔"),
    "ep03-napoleon-bajito":      dict(t=28.0, zoom=1.6, fx=0.75, fy=0.58, top="¿NAPOLEÓN ERA BAJITO?", big="MENTIRA INGLESA", sub="medía 1.70 m", emoji="📏"),
    "ep04-cleopatra-luna":       dict(t=43.5, zoom=1.8, fx=0.5, fy=0.6, top="CLEOPATRA VIVIÓ", big="MÁS CERCA DE LA LUNA", sub="que de las pirámides", emoji="🌙"),
    "ep05-guerra-pasteles":      dict(t=36.0, zoom=1.8, fx=0.42, fy=0.3, top="¿UNA GUERRA…", big="POR PASTELES?", sub="le costó una pierna a Santa Anna", emoji="🥐"),
    "ep06-yucatan-subasta":      dict(t=25.5, zoom=1.3, fx=0.5, fy=0.48, top="YUCATÁN SE VENDÍA…", big="Y NADIE LO QUISO", sub="EE. UU., Inglaterra y España dijeron NO", emoji="🗺️"),
    "ep07-juicio-papa-muerto":   dict(t=2.5, zoom=1.6, fx=0.35, fy=0.45, top="DESENTERRARON AL PAPA", big="¡PARA JUZGARLO!", sub="Roma · año 897", emoji="💀"),
    "ep08-onoda-chat":           dict(t=15.5, zoom=1.35, fx=0.5, fy=0.45, top="LA GUERRA TERMINÓ EN 1945", big="NADIE LE AVISÓ", sub="y peleó 29 años más", emoji="📱"),
    "ep09-plaga-del-baile":      dict(t=21.5, zoom=2.4, fx=0.5, fy=0.78, top="ESTRASBURGO · 1518", big="BAILARON SEMANAS SIN PARAR", sub="nadie sabe por qué", emoji="💃"),
    "ep10-adidas-puma":          dict(t=8.0, zoom=1.3, fx=0.4, fy=0.5, top="SE ODIABAN TANTO…", big="ADIDAS vs PUMA", sub="dos hermanos, un pueblo partido", emoji="👟"),
    "ep10-diogenes-alejandro":   dict(t=34.3, zoom=1.5, fx=0.42, fy=0.55, top="A ALEJANDRO MAGNO", big="LE DIJO ¡QUÍTATE!", sub="me tapas el sol", emoji="☀️"),
    "ep11-guerra-del-cerdo":     dict(t=14.2, zoom=1.35, fx=0.5, fy=0.5, top="CASI UNA GUERRA", big="POR UN CERDO", sub="EE. UU. vs Inglaterra · 1859", emoji="🐷"),
    "ep12-torre-pisa":           dict(t=10.5, zoom=1.5, fx=0.5, fy=0.76, top="LA TORRE DE PISA", big="¡CHUECA DESDE EL INICIO!", sub="se hundía con 2 pisos", emoji="😳"),
    "ep13-vendio-torre-eiffel":  dict(t=1.5, zoom=1.25, fx=0.5, fy=0.6, top="VENDIÓ LA TORRE EIFFEL", big="¡DOS VECES!", sub="como chatarra · 1925", emoji="💸"),
    "ep14-garbo-espia":          dict(t=46.0, zoom=1.5, fx=0.4, fy=0.32, top="ENGAÑÓ A HITLER…", big="¡Y HITLER LO PREMIÓ!", sub="con la Cruz de Hierro", emoji="🎖️"),
    "ep15-otzi-noticiero":       dict(t=9.0, zoom=1.6, fx=0.5, fy=0.58, top="ÚLTIMA HORA", big="ASESINATO DE HACE 5,000 AÑOS", sub="flecha en el hombro", emoji="🧊"),
    "ep16-socrates-xantipa":     dict(t=17.5, zoom=1.4, fx=0.5, fy=0.5, top="LA ESPOSA DE SÓCRATES", big="¡LE ECHÓ UNA CUBETA!", sub="y él… la aguantó", emoji="💦"),
    "ep17-colon-tierra-plana":   dict(t=20.0, zoom=1.45, fx=0.42, fy=0.42, top="¿COLÓN DESCUBRIÓ QUE ERA REDONDA?", big="¡MENTIRA!", sub="ya se sabía hace 1,700 años", emoji=""),
    "ep18-vikingos-cuernos":     dict(t=3.9, zoom=1.3, fx=0.5, fy=0.34, top="¿LOS VIKINGOS USABAN CUERNOS?", big="NUNCA LOS USARON", sub="fue culpa de una ópera de 1876", emoji=""),
}

CSS = """
*{box-sizing:border-box;margin:0}
html,body{width:1080px;height:1920px;overflow:hidden;background:#1B1B2F}
body{position:relative;font-family:"Archivo Black","Arial Black",sans-serif;color:#fff}
#bg{position:absolute;left:%(left)dpx;top:%(top)dpx;width:%(w)dpx;height:%(h)dpx}
.shade{position:absolute;left:0;right:0;height:560px;background:linear-gradient(#1B1B2Fcc,#1B1B2F00)}
.shade.b{bottom:0;top:auto;height:720px;background:linear-gradient(#1B1B2F00,#1B1B2F 130px)}
.top{position:absolute;left:0;right:0;top:92px;text-align:center}
.top span{display:inline-block;max-width:1000px;background:#FFD23F;color:#1B1B2F;font-size:84px;line-height:1;
  padding:26px 40px 18px;border:10px solid #1B1B2F;box-shadow:16px 16px 0 #1B1B2F;transform:rotate(-2.5deg)}
.emoji{position:absolute;right:48px;top:250px;font-size:190px;line-height:1;transform:rotate(10deg);
  font-family:"Segoe UI Emoji","Apple Color Emoji",sans-serif;filter:drop-shadow(10px 10px 0 #1B1B2F)}
.big{position:absolute;left:40px;right:40px;bottom:400px;text-align:center;font-size:150px;line-height:.95;
  color:#fff;-webkit-text-stroke:18px #1B1B2F;paint-order:stroke fill;text-shadow:14px 14px 0 #1B1B2F}
.sub{position:absolute;left:40px;right:40px;bottom:290px;text-align:center;font-family:"Nunito",sans-serif;font-weight:900;
  font-size:62px;line-height:1.05;color:#FFD23F;-webkit-text-stroke:10px #1B1B2F;paint-order:stroke fill}
.brand{position:absolute;left:0;right:0;bottom:70px;display:flex;justify-content:center;align-items:center;gap:22px}
.brand img{width:150px;height:150px;border-radius:50%%;border:8px solid #1B1B2F;background:#E23E8B}
.brand span{background:#1B1B2F;color:#FFD23F;font-size:56px;padding:18px 34px 12px;border-radius:999px;transform:rotate(-2deg)}
"""

HTML = """<!doctype html><html lang="es"><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo+Black&family=Nunito:wght@900&display=swap">
<style>%(css)s</style></head><body>
<img id="bg" src="frame.png">
<div class="shade"></div><div class="shade b"></div>
<div class="top"><span>%(top)s</span></div>
<div class="emoji">%(emoji)s</div>
<div class="big" id="big">%(big)s</div>
<div class="sub">%(sub)s</div>
<div class="brand"><img src="%(logo)s"><span>PURO CHISME</span></div>
<script>
// Encoge el texto gigante hasta que quepa en 3 lineas (max 470 px de alto).
const b=document.getElementById('big');let s=150;
document.fonts.ready.then(()=>{while(b.offsetHeight>470&&s>80){s-=6;b.style.fontSize=s+'px'}});
</script></body></html>"""


def encuadre(zoom, fx, fy):
    w, h = round(1080 * zoom), round(1920 * zoom)
    left = min(0, max(1080 - w, round(540 - fx * w)))
    top = min(0, max(1920 - h, round(960 - fy * h)))
    return dict(w=w, h=h, left=left, top=top)


def miniatura(slug, cfg):
    ep = ROOT / slug
    mp4 = ep / "renders" / f"{slug}.mp4"
    out = ep / "renders" / "miniatura.jpg"
    if out.exists() and not (ep / "renders" / "miniatura_anterior.jpg").exists():
        shutil.copy(out, ep / "renders" / "miniatura_anterior.jpg")
    work = Path(tempfile.mkdtemp(prefix=f"mini_{slug[:4]}_"))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(cfg["t"]), "-i", str(mp4), "-frames:v", "1", str(work / "frame.png")], check=True)
    page = HTML % dict(css=CSS % encuadre(cfg["zoom"], cfg["fx"], cfg["fy"]), logo=LOGO,
                       **{k: html.escape(cfg[k]) for k in ("top", "big", "sub", "emoji")})
    (work / "mini.html").write_text(page, encoding="utf-8")
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--hide-scrollbars", "--window-size=1080,1920",
                    "--virtual-time-budget=10000", "--screenshot=" + str(work / "mini.png"), (work / "mini.html").as_uri()],
                   check=True, capture_output=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(work / "mini.png"), "-q:v", "3", str(out)], check=True)
    assert out.stat().st_size < 2_000_000, f"{out} > 2 MB"
    shutil.rmtree(work, ignore_errors=True)
    print(slug, out.stat().st_size // 1024, "KB")
    return out


def hoja(outs):
    """Hoja de contacto 4 columnas para revisar todas de un vistazo (al tamaño real de la cuadrícula ~270 px)."""
    n = len(outs)
    cols = 4
    rows = -(-n // cols)
    layout = "|".join(f"{(i % cols) * 270}_{(i // cols) * 480}" for i in range(n))
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for o in outs:
        cmd += ["-i", str(o)]
    scaled = "".join(f"[{i}:v]scale=270:480[s{i}];" for i in range(n))
    ins = "".join(f"[s{i}]" for i in range(n))
    cmd += ["-filter_complex", f"{scaled}{ins}xstack=inputs={n}:layout={layout}:fill=black", str(ROOT / "miniaturas_hoja.jpg")]
    subprocess.run(cmd, check=True)
    print("hoja:", ROOT / "miniaturas_hoja.jpg", f"({cols}x{rows})")


if __name__ == "__main__":
    pedidos = sys.argv[1:]
    slugs = [s for s in EPISODIOS if not pedidos or any(s.startswith(p) for p in pedidos)]
    outs = [miniatura(s, EPISODIOS[s]) for s in slugs]
    if not pedidos:
        hoja(outs)
