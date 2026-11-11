"""Shorts health per channel (last 90 days) from the YouTube Data API v3: uploads, views of those uploads, share ≥1M,
median, best/median (outlier) and how English the titles are. Input: the CSVs of yt_niches.py / outliers.py.

  python -I canal_stats.py canales_20261108_en.csv outliers_20261107_en.csv --out canal_stats_en.csv
  python -I canal_stats.py --selftest

Note: "views_90d" = current views of the videos uploaded in the last 90 days (the API has no per-period views).
Cuota: ~2 unidades por canal.
"""
import argparse
import csv
import re
import statistics
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))  # python -I drops the script dir
from outliers import api_key, get  # noqa: E402  same key loading and HTTP helper


def chunks(xs, n=50):
    return [xs[i:i + n] for i in range(0, len(xs), n)]


def secs(iso):
    m = re.fullmatch(r"P(?:\d+D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    return 0 if not m else int(m[1] or 0) * 3600 + int(m[2] or 0) * 60 + int(m[3] or 0)


def ascii_share(titles):
    txt = "".join(re.sub(r"[\s\d\W_]", "", t) for t in titles)
    return round(sum(c.isascii() for c in txt) / len(txt), 2) if txt else 0.0


def summarize(vids, now):
    """vids: [(published datetime, views, seconds, title)] → stats over Shorts (≤180 s) of the last 90 days."""
    recent = [v for v in vids if v[0] >= now - timedelta(days=90) and v[2] <= 180]
    views = [v[1] for v in recent]
    med = statistics.median(views) if views else 0
    weeks = 90 / 7
    return dict(shorts_90d=len(recent), por_semana=round(len(recent) / weeks, 1), views_90d=sum(views), mediana=int(med),
                n_1m=sum(x >= 1_000_000 for x in views), pct_1m=round(sum(x >= 1_000_000 for x in views) / len(views), 2) if views else 0,
                mejor_x_mediana=round(max(views) / med, 1) if views and med else 0, ingles=ascii_share([v[3] for v in vids]),
                ultimo=max((v[0] for v in vids), default=now).date().isoformat())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csvs", nargs="*")
    ap.add_argument("--out", default="canal_stats.csv")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    key = api_key()
    chans, vids_to_resolve = set(), set()
    for f in a.csvs:
        for r in csv.DictReader(open(HERE / f, encoding="utf-8-sig")):
            if "/channel/" in r.get("url", ""):
                chans.add(r["url"].rsplit("/", 1)[1])
            elif "/shorts/" in r.get("url", ""):
                vids_to_resolve.add(r["url"].rsplit("/", 1)[1])
    for c in chunks(sorted(vids_to_resolve)):
        for it in get("videos", key, part="snippet", id=",".join(c)).get("items", []):
            chans.add(it["snippet"]["channelId"])
    now = datetime.now(timezone.utc)
    rows = []
    for c in chunks(sorted(chans)):
        for ch in get("channels", key, part="snippet,statistics,contentDetails", id=",".join(c)).get("items", []):
            up = ch["contentDetails"]["relatedPlaylists"]["uploads"]
            items = get("playlistItems", key, part="contentDetails", playlistId=up, maxResults=50).get("items", [])
            ids = [i["contentDetails"]["videoId"] for i in items]
            vids = []
            for v in get("videos", key, part="snippet,statistics,contentDetails", id=",".join(ids)).get("items", []) if ids else []:
                vids.append((datetime.fromisoformat(v["snippet"]["publishedAt"].replace("Z", "+00:00")),
                             int(v["statistics"].get("viewCount", 0)), secs(v["contentDetails"].get("duration")), v["snippet"]["title"]))
            sn, st = ch["snippet"], ch["statistics"]
            rows.append(dict(canal=sn["title"], url=f"https://youtube.com/channel/{ch['id']}",
                             creado=sn["publishedAt"][:10], pais=sn.get("country", ""), subs=int(st.get("subscriberCount", 0)),
                             **summarize(vids, now)))
    rows.sort(key=lambda r: r["views_90d"], reverse=True)
    with open(HERE / a.out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows[:40]:
        print(f"{r['views_90d']:>12,} {r['shorts_90d']:>3} sh {r['por_semana']:>4}/sem 1M:{r['n_1m']:>3} en:{r['ingles']} "
              f"{r['creado']} {r['subs']:>9,} {r['canal']}")
    print("CSV:", HERE / a.out)


def selftest():
    now = datetime(2026, 11, 7, tzinfo=timezone.utc)
    d = lambda n: now - timedelta(days=n)
    s = summarize([(d(1), 2_000_000, 40, "Hello"), (d(10), 100, 50, "Hola"), (d(100), 9, 40, "old"), (d(5), 500, 600, "long")], now)
    assert s["shorts_90d"] == 2 and s["n_1m"] == 1 and s["views_90d"] == 2_000_100, s
    assert secs("PT1M5S") == 65 and secs("PT45S") == 45
    assert ascii_share(["Hello", "नमस्ते"]) < 0.6
    print("selftest ok")


if __name__ == "__main__":
    sys.exit(main())
