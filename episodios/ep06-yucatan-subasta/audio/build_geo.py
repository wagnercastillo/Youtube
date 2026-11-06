"""Proyecta y simplifica los estados de México (geoBoundaries, CC BY 3.0 IGO) para el mapa 3D.

  python -I audio/build_geo.py   → assets/geo/mexico_shapes.json  {pen: [rings], mex: [rings], bounds}
"pen" = la península (Yucatán, Campeche, Quintana Roo), que en 1848 era todo Yucatán.
"""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PEN = {"Yucatan", "Campeche", "Quintana Roo"}
LAT0, LON0 = 23.5, -102.0
K = math.cos(math.radians(LAT0))


def proj(p):
    return [round((p[0] - LON0) * K, 4), round(p[1] - LAT0, 4)]


def area(r):
    return abs(sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(r, r[1:] + r[:1]))) / 2


def dp(pts, tol):  # Douglas-Peucker on an open polyline
    if len(pts) < 3:
        return pts
    a, b = pts[0], pts[-1]
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1e-9
    i, dm = 0, -1.0
    for k, p in enumerate(pts[1:-1], 1):
        d = abs(dy * p[0] - dx * p[1] + b[0] * a[1] - b[1] * a[0]) / n
        if d > dm:
            i, dm = k, d
    if dm > tol:
        return dp(pts[:i + 1], tol)[:-1] + dp(pts[i:], tol)
    return [a, b]


def simplify_ring(ring, tol):
    ring = ring[:-1] if ring[0] == ring[-1] else ring
    far = max(range(len(ring)), key=lambda k: (ring[k][0] - ring[0][0]) ** 2 + (ring[k][1] - ring[0][1]) ** 2)
    return dp(ring[:far + 1], tol)[:-1] + dp(ring[far:] + [ring[0]], tol)[:-1]


def main():
    g = json.loads((ROOT / "assets/geo/mex_adm1_simplified.geojson").read_text(encoding="utf-8"))
    out = {"pen": [], "mex": []}
    for f in g["features"]:
        geom = f["geometry"]
        polys = geom["coordinates"] if geom["type"] == "MultiPolygon" else [geom["coordinates"]]
        for poly in polys:
            ring = [proj(p) for p in poly[0]]
            if area(ring) < 0.02:  # drop small islands
                continue
            ring = simplify_ring(ring, 0.02)
            if len(ring) >= 4:
                out["pen" if f["properties"]["shapeName"] in PEN else "mex"].append(ring)
    pts = [p for k in ("pen", "mex") for r in out[k] for p in r]
    out["bounds"] = [min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts)]
    (ROOT / "assets/geo/mexico_shapes.json").write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    print("rings", len(out["pen"]), len(out["mex"]), "points", len(pts), "bounds", out["bounds"])


if __name__ == "__main__":
    main()
