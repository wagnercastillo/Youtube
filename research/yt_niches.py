"""Encuentra canales jóvenes que crecen rápido por nicho, con la YouTube Data API v3.

Por cada tema busca los videos más vistos de los últimos N días, junta sus canales
y se queda con los creados hace poco. Un nicho con muchos canales nuevos y con
muchas vistas por día está creciendo.

Uso:
  set YOUTUBE_API_KEY=...   (o ponla en research/.env)
  python yt_niches.py "curiosidades" "historia animada" "finanzas personales" --shorts --region MX
  python yt_niches.py --selftest

Cuota: ~102 unidades por tema (de 10 000 gratis al día) → ~90 temas al día.
"""
import argparse
import csv
import json
import os
import statistics
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

API = "https://www.googleapis.com/youtube/v3/"
HERE = Path(__file__).parent


def api_key():
    env = HERE / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            k, _, v = line.partition("=")
            if k.strip() == "YOUTUBE_API_KEY" and v.strip():
                return v.strip()
    return os.environ.get("YOUTUBE_API_KEY") or sys.exit("Falta YOUTUBE_API_KEY (variable o research/.env)")


def get(endpoint, key, **params):
    url = API + endpoint + "?" + urllib.parse.urlencode({**params, "key": key})
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def chunks(xs, n=50):
    return [xs[i : i + n] for i in range(0, len(xs), n)]


def parse_date(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def score_channel(ch, now):
    """Edad del canal y velocidad de crecimiento (por día de vida)."""
    stats, created = ch["statistics"], parse_date(ch["snippet"]["publishedAt"])
    age = max((now - created).days, 1)
    views = int(stats.get("viewCount", 0))
    subs = int(stats.get("subscriberCount", 0)) if not stats.get("hiddenSubscriberCount") else 0
    return {
        "canal": ch["snippet"]["title"],
        "url": f"https://youtube.com/channel/{ch['id']}",
        "edad_dias": age,
        "subs": subs,
        "vistas": views,
        "videos": int(stats.get("videoCount", 0)),
        "vistas_dia": round(views / age),
        "subs_dia": round(subs / age, 1),
    }


def niche_summary(topic, young, total):
    vd = [c["vistas_dia"] for c in young]
    return {
        "nicho": topic,
        "canales_en_top": total,
        "canales_nuevos": len(young),
        "pct_nuevos": round(100 * len(young) / total) if total else 0,
        "mediana_vistas_dia_nuevos": round(statistics.median(vd)) if vd else 0,
    }


def research(topic, key, a, now):
    since = (now - timedelta(days=a.days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    params = dict(part="snippet", q=topic, type="video", order="viewCount",
                  publishedAfter=since, maxResults=50, relevanceLanguage=a.lang)
    if a.region:
        params["regionCode"] = a.region
    if a.shorts:
        params["videoDuration"] = "short"
    items = get("search", key, **params).get("items", [])  # 100 unidades
    ids = list({it["snippet"]["channelId"] for it in items})
    chans = []
    for ch_ids in chunks(ids):  # 1 unidad por bloque de 50
        chans += get("channels", key, part="snippet,statistics", id=",".join(ch_ids)).get("items", [])
    scored = [score_channel(c, now) for c in chans]
    young = sorted((c for c in scored if c["edad_dias"] <= a.max_age),
                   key=lambda c: c["vistas_dia"], reverse=True)
    return niche_summary(topic, young, len(scored)), [{"nicho": topic, **c} for c in young]


def selftest():
    now = datetime(2026, 11, 5, tzinfo=timezone.utc)
    ch = {"id": "X", "snippet": {"title": "T", "publishedAt": "2026-10-06T00:00:00Z"},
          "statistics": {"viewCount": "3000000", "subscriberCount": "30000", "videoCount": "40"}}
    s = score_channel(ch, now)
    assert s["edad_dias"] == 30 and s["vistas_dia"] == 100000 and s["subs_dia"] == 1000.0, s
    hidden = {**ch, "statistics": {**ch["statistics"], "hiddenSubscriberCount": True}}
    assert score_channel(hidden, now)["subs"] == 0
    summ = niche_summary("n", [s, {**s, "vistas_dia": 10}], 4)
    assert summ["pct_nuevos"] == 50 and summ["mediana_vistas_dia_nuevos"] == 50005, summ
    assert niche_summary("n", [], 0)["pct_nuevos"] == 0
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("topics", nargs="*")
    ap.add_argument("--days", type=int, default=30, help="ventana de videos recientes")
    ap.add_argument("--max-age", type=int, default=180, help="edad máxima del canal en días")
    ap.add_argument("--lang", default="es")
    ap.add_argument("--region", help="MX, ES, US, CO, AR...")
    ap.add_argument("--shorts", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")  # Windows console default cp1252 breaks on ≤/á
    if a.selftest:
        return selftest()
    if not a.topics:
        ap.error("indica al menos un tema")

    key, now = api_key(), datetime.now(timezone.utc)
    summaries, rows = [], []
    for t in a.topics:
        s, r = research(t, key, a, now)
        summaries.append(s)
        rows += r
    summaries.sort(key=lambda s: (s["canales_nuevos"], s["mediana_vistas_dia_nuevos"]), reverse=True)

    print(f"\nNichos (canales de ≤{a.max_age} días en el top de los últimos {a.days} días):")
    for s in summaries:
        print(f"  {s['nicho']:<28} nuevos {s['canales_nuevos']:>2}/{s['canales_en_top']:<2} "
              f"({s['pct_nuevos']:>3}%)  mediana {s['mediana_vistas_dia_nuevos']:>9,} vistas/día")
    print("\nCanales nuevos más rápidos:")
    for c in sorted(rows, key=lambda c: c["vistas_dia"], reverse=True)[:15]:
        print(f"  {c['vistas_dia']:>9,}/día  {c['edad_dias']:>3}d  {c['subs']:>8,} subs  [{c['nicho']}] {c['canal']}  {c['url']}")

    out = HERE / f"canales_{now:%Y%m%d}.csv"
    if rows:
        with open(out, "w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
        print(f"\nCSV: {out}")


if __name__ == "__main__":
    main()
