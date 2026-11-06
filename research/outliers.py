"""Shorts "outliers": videos recientes con muchas más vistas que suscriptores tiene su canal (el tema/estilo pegó, no el canal).

  python -I outliers.py "historia" "datos curiosos" --days 30 --region MX
  python -I outliers.py --selftest

Cuota: ~101 unidades por búsqueda + 1 por cada 50 videos/canales. Escribe outliers_<fecha>.csv.
"""
import argparse
import csv
import json
import os
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
    return os.environ.get("YOUTUBE_API_KEY") or sys.exit("Falta YOUTUBE_API_KEY")


def get(endpoint, key, **params):
    url = API + endpoint + "?" + urllib.parse.urlencode({**params, "key": key}, doseq=True)
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r)


def score(views, subs):
    """Vistas por suscriptor, suavizado para que canales de 0 subs no exploten."""
    return views / max(subs, 1000)


def main():
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # -I ignores PYTHONIOENCODING on Windows
    ap = argparse.ArgumentParser()
    ap.add_argument("topics", nargs="*")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--region", default="MX")
    ap.add_argument("--top", type=int, default=25)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        assert score(1_000_000, 10_000) == 100 and score(50_000, 0) == 50
        return print("selftest ok")
    key = api_key()
    after = (datetime.now(timezone.utc) - timedelta(days=a.days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    vids = {}
    for q in a.topics:
        r = get("search", key, part="snippet", q=q + " #shorts", type="video", videoDuration="short", order="viewCount",
                publishedAfter=after, regionCode=a.region, relevanceLanguage="es", maxResults=50)
        for it in r.get("items", []):
            vids[it["id"]["videoId"]] = q
    ids = list(vids)
    stats, chans = {}, {}
    for i in range(0, len(ids), 50):
        r = get("videos", key, part="snippet,statistics", id=",".join(ids[i:i + 50]))
        for v in r["items"]:
            stats[v["id"]] = v
    cids = list({v["snippet"]["channelId"] for v in stats.values()})
    for i in range(0, len(cids), 50):
        r = get("channels", key, part="statistics", id=",".join(cids[i:i + 50]))
        for c in r["items"]:
            chans[c["id"]] = int(c["statistics"].get("subscriberCount", 0))
    rows = []
    for vid, v in stats.items():
        views = int(v["statistics"].get("viewCount", 0))
        subs = chans.get(v["snippet"]["channelId"], 0)
        rows.append({"tema": vids[vid], "titulo": v["snippet"]["title"], "canal": v["snippet"]["channelTitle"],
                     "vistas": views, "subs": subs, "x_subs": round(score(views, subs), 1),
                     "url": f"https://youtube.com/shorts/{vid}"})
    rows.sort(key=lambda r: -r["x_subs"])
    out = HERE / f"outliers_{datetime.now():%Y%m%d}.csv"
    with out.open("w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows[:a.top]:
        print(f"{r['x_subs']:>8}x  {r['vistas']:>11,} vistas  {r['subs']:>9,} subs  [{r['tema']}] {r['titulo'][:80]}  — {r['canal']}")
    print("CSV:", out)


if __name__ == "__main__":
    main()
