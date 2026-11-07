"""EP10: diorama de juguete (Blender, EEVEE) — Adidas vs Puma, los hermanos Dassler.

  blender -b -P blender/escena.py -- still 0,15,25        # cuadros sueltos a 50 % en blender/stills/ (para revisar)
  blender -b -P blender/escena.py -- render [desde hasta]  # PNG 1080×1920 en blender/frames/ (salta los que ya existen)
  blender -b -P blender/escena.py -- save                  # guarda blender/escena.blend para abrirlo a mano

Todo se construye desde código: un pueblo miniatura sobre una tabla redonda, partido por un río (norte = Adi/azul,
sur = Rudi/rojo). Cada movimiento se ancla a una palabra con W(línea, palabra) leída de transcript.json, así que una voz
nueva re-sincroniza sola. Sin logos de marca: solo colores y los nombres (los rótulos van en HTML).
"""
import json
import math
import random
import sys
import unicodedata
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parent.parent
WORDS = json.loads((ROOT / "transcript.json").read_text(encoding="utf-8"))
LINES = {l["id"]: l for l in json.loads((ROOT / "assets/lines.json").read_text(encoding="utf-8"))}
MOUTH = json.loads((ROOT / "assets/mouth.json").read_text(encoding="utf-8"))
FPS = 30
END = round(LINES["l10"]["end"] + 0.45, 2)  # the end card (HTML, opaque) covers everything after this
LAST = int(END * FPS) + 6
random.seed(10)


def norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if c.isalnum() and not unicodedata.combining(c))


def L(line, d=0.0):
    return LINES[line]["start"] + d


def W(line, word, k=1, d=0.0):
    ln = LINES[line]
    hits = [w for w in WORDS if ln["start"] - 0.05 <= w["start"] <= ln["end"] and norm(w["text"]) == norm(word)]
    return hits[k - 1]["start"] + d


def F(t):
    return round(t * FPS)


# ---------------------------------------------------------------- keyframes
PREF = bpy.context.preferences.edit


def key(owner, path, t, value, interp="BEZIER", index=-1):
    """Keyframe at time t (s). interp: BEZIER (ease), BACK (overshoot), LINEAR, CONSTANT."""
    PREF.keyframe_new_interpolation_type = interp
    setattr(owner, path, value) if index < 0 else getattr(owner, path).__setitem__(index, value)
    owner.keyframe_insert(path, frame=F(t), index=index)


def pop(ob, t, dur=0.35, s=1.0):
    """Scale 0 → s with overshoot, starting at t."""
    key(ob, "scale", t - 0.01, (0, 0, 0), "BACK")
    key(ob, "scale", t + dur, (s, s, s), "BEZIER")


def unpop(ob, t, dur=0.25, s=1.0):
    key(ob, "scale", t, (s, s, s), "BEZIER")
    key(ob, "scale", t + dur, (0, 0, 0), "BEZIER")


def move(ob, t0, t1, loc, interp="BEZIER"):
    key(ob, "location", t0, tuple(ob.location), interp)
    key(ob, "location", t1, loc, "BEZIER")


def hop(ob, t0, t1, loc, h=0.8):
    """Arc jump from current location to loc."""
    a = tuple(ob.location)
    mid = ((a[0] + loc[0]) / 2, (a[1] + loc[1]) / 2, max(a[2], loc[2]) + h)
    key(ob, "location", t0, a)
    key(ob, "location", (t0 + t1) / 2, mid)
    key(ob, "location", t1, loc, "BACK")


def turn(ob, t0, t1, rz):
    key(ob, "rotation_euler", t0, ob.rotation_euler[2], index=2)
    key(ob, "rotation_euler", t1, rz, "BACK", index=2)


# ---------------------------------------------------------------- scene, materials, primitives
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 0, LAST
    sc.eevee.taa_render_samples = 24
    for attr, v in (("use_shadows", True), ("use_raytracing", True), ("use_fast_gi", True)):
        if hasattr(sc.eevee, attr):
            setattr(sc.eevee, attr, v)
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Punchy"
    except TypeError:
        pass
    return sc


MATS = {}


def mat(name, rgb, rough=0.38, coat=0.35, emit=0.0):
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    for nm in ("Coat Weight", "Clearcoat"):
        if nm in b.inputs:
            b.inputs[nm].default_value = coat
            break
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1)
        b.inputs["Emission Strength"].default_value = emit
    MATS[name] = m
    return m


def hexrgb(h):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)


def C(h, **kw):
    return mat(h, hexrgb(h), **kw)


def finish(ob, m, parent=None, bevel=0.0, smooth=True):
    ob.data.materials.append(m)
    if bevel:
        mod = ob.modifiers.new("bevel", "BEVEL")
        mod.width, mod.segments = bevel, 3
    if smooth and hasattr(ob.data, "polygons"):
        for p in ob.data.polygons:
            p.use_smooth = True
    if parent:
        ob.parent = parent
    return ob


def cube(name, loc, size, m, parent=None, bevel=0.04, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name, ob.scale = name, size
    bpy.ops.object.transform_apply(scale=True)
    return finish(ob, m, parent, bevel, smooth=False)


def cyl(name, loc, r, h, m, parent=None, bevel=0.03, verts=32, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=h, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    return finish(ob, m, parent, bevel)


def cone(name, loc, r1, h, m, parent=None, verts=32, r2=0.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r1, radius2=r2, depth=h, location=loc, rotation=rot)
    ob = bpy.context.object
    ob.name = name
    return finish(ob, m, parent, 0.0, smooth=verts > 8)


def ball(name, loc, r, m, parent=None, scale=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=32, ring_count=16, radius=r, location=loc)
    ob = bpy.context.object
    ob.name, ob.scale = name, scale
    return finish(ob, m, parent)


def empty(name, loc=(0, 0, 0), parent=None):
    ob = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.parent = parent
    return ob


def build_root(name, loc, parent, scale=1.0, rz=0.0):
    """Empty that holds a prop, for popping the whole thing at once."""
    r = empty(name, loc, parent)
    r.rotation_euler[2] = rz
    r.scale = (scale,) * 3
    return r


# ---------------------------------------------------------------- props
SKIN = "#F2C29B"
INK = "#1B1B2F"


def peg(name, body, loc, parent=None, skin=SKIN, hair="#5A3A22", rz=0.0, s=1.0, cap=None, arms=True):
    """Toy peg person (~0.95 tall). Returns root; root['parts'] hold mouth/arm/head for animation."""
    r = build_root(name, loc, parent, s, rz)
    cyl(name + "_body", (0, 0, 0.28), 0.2, 0.56, C(body), r, bevel=0.06)
    head = empty(name + "_neck", (0, 0, 0.56), r)
    ball(name + "_head", (0, 0, 0.2), 0.2, C(skin, rough=0.5, coat=0.1), head)
    ball(name + "_hair", (0, 0.02, 0.27), 0.195, C(hair, rough=0.6, coat=0.0), head, scale=(1.03, 1.03, 0.62))
    if cap:
        cyl(name + "_cap", (0, 0, 0.37), 0.2, 0.08, C(cap), head, bevel=0.02)
        cube(name + "_visor", (0, -0.2, 0.34), (0.26, 0.14, 0.03), C(cap), head, bevel=0.01)
    for sx in (-1, 1):
        ball(f"{name}_eye{sx}", (0.075 * sx, -0.175, 0.23), 0.032, C(INK, coat=0.6), head)
    mouth = ball(name + "_mouth", (0, -0.185, 0.12), 0.045, C("#7A2230", coat=0.2), head, scale=(1.3, 0.5, 0.25))
    arm_r = arm_l = None
    if arms:
        arm_r = empty(name + "_armR", (0.21, 0, 0.48), r)
        cyl(name + "_armRm", (0, 0, -0.17), 0.055, 0.34, C(body), arm_r, bevel=0.02)
        ball(name + "_handR", (0, 0, -0.35), 0.06, C(skin, rough=0.5, coat=0.1), arm_r)
        arm_l = empty(name + "_armL", (-0.21, 0, 0.48), r)
        cyl(name + "_armLm", (0, 0, -0.17), 0.055, 0.34, C(body), arm_l, bevel=0.02)
        ball(name + "_handL", (0, 0, -0.35), 0.06, C(skin, rough=0.5, coat=0.1), arm_l)
    r["head"], r["mouth"] = head.name, mouth.name
    r["armR"], r["armL"] = (arm_r.name if arm_r else ""), (arm_l.name if arm_l else "")
    return r


def part(root, k):
    return bpy.data.objects[root[k]]


def house(name, loc, parent, wall, roof, s=1.0, rz=0.0):
    r = build_root(name, loc, parent, s, rz)
    cube(name + "_w", (0, 0, 0.4), (0.9, 0.8, 0.8), C(wall, rough=0.6, coat=0.1), r)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.78, depth=0.5, location=(0, 0, 1.05), rotation=(0, 0, math.pi / 4))
    rf = bpy.context.object
    rf.name, rf.scale = name + "_r", (1.0, 0.95, 1)
    finish(rf, C(roof, rough=0.5), r, smooth=False)
    cube(name + "_door", (0, -0.405, 0.2), (0.22, 0.03, 0.38), C("#6B4226", rough=0.6), r, bevel=0.01)
    for sx in (-1, 1):
        cube(f"{name}_win{sx}", (0.28 * sx, -0.405, 0.52), (0.18, 0.03, 0.18), C("#FFE7A3", emit=0.6), r, bevel=0.01)
    return r


def tree(name, loc, parent, s=1.0):
    r = build_root(name, loc, parent, s)
    cyl(name + "_t", (0, 0, 0.18), 0.06, 0.36, C("#7A4E2D", rough=0.7), r, bevel=0.0, verts=12)
    cone(name + "_c", (0, 0, 0.62), 0.32, 0.7, C("#3E8E4A", rough=0.55), r, verts=24)
    return r


def shoe(name, loc, parent, color, stripe, s=1.0, rz=0.0):
    """Generic toy sneaker (no brand marks): sole + upper + toe + a single side band in the brother's color."""
    r = build_root(name, loc, parent, s, rz)
    cube(name + "_sole", (0, 0, 0.04), (0.28, 0.62, 0.08), C("#F4F1EA", rough=0.5), r, bevel=0.035)
    cube(name + "_up", (0, 0.08, 0.17), (0.26, 0.42, 0.2), C(color), r, bevel=0.07)
    ball(name + "_toe", (0, -0.17, 0.11), 0.13, C(color), r, scale=(1.0, 1.25, 0.75))
    cube(name + "_band", (0, 0.06, 0.17), (0.268, 0.1, 0.16), C(stripe), r, bevel=0.03)
    for i in range(3):
        cube(f"{name}_lace{i}", (0, -0.06 + i * 0.07, 0.27), (0.16, 0.02, 0.02), C("#FFFFFF"), r, bevel=0.005)
    return r


def plane_toy(name, loc, parent):
    r = build_root(name, loc, parent, 1.0)
    cyl(name + "_f", (0, 0, 0), 0.12, 1.1, C("#6E7B5A", rough=0.5), r, rot=(0, math.pi / 2, 0))
    cube(name + "_w", (0.05, 0, 0), (0.28, 1.4, 0.04), C("#5B6849", rough=0.5), r, bevel=0.02)
    cube(name + "_tail", (-0.48, 0, 0.12), (0.14, 0.4, 0.03), C("#5B6849", rough=0.5), r, bevel=0.01)
    cyl(name + "_prop", (0.58, 0, 0), 0.2, 0.02, C("#2B2B2B"), r, rot=(0, math.pi / 2, 0), verts=6)
    return r


def goal(name, loc, parent, rz=0.0):
    r = build_root(name, loc, parent, 1.0, rz)
    white = C("#FFFFFF")
    for sx in (-1, 1):
        cyl(f"{name}_p{sx}", (0.35 * sx, 0, 0.18), 0.025, 0.36, white, r, bevel=0.0, verts=10)
    cyl(name + "_bar", (0, 0, 0.36), 0.025, 0.72, white, r, bevel=0.0, verts=10, rot=(0, math.pi / 2, 0))
    return r


def pitch(name, loc, parent, size=(1.8, 1.2)):
    r = build_root(name, loc, parent, 1.0)
    cube(name + "_g", (0, 0, 0.02), (size[0], size[1], 0.04), C("#4FAE57", rough=0.7, coat=0.0), r, bevel=0.01)
    w = C("#FFFFFF", rough=0.6)
    cube(name + "_mid", (0, 0, 0.045), (0.03, size[1] - 0.1, 0.01), w, r, bevel=0.0)
    cyl(name + "_c", (0, 0, 0.045), 0.18, 0.01, w, r, bevel=0.0)
    cyl(name + "_c2", (0, 0, 0.048), 0.15, 0.012, C("#4FAE57", rough=0.7, coat=0.0), r, bevel=0.0)
    goal(name + "_g1", (-size[0] / 2 + 0.08, 0, 0.04), r, rz=math.pi / 2)
    goal(name + "_g2", (size[0] / 2 - 0.08, 0, 0.04), r, rz=math.pi / 2)
    return r


def tomb(name, loc, parent, color):
    r = build_root(name, loc, parent, 1.0)
    cube(name + "_s", (0, 0, 0.32), (0.42, 0.14, 0.64), C("#9AA0A6", rough=0.7, coat=0.0), r, bevel=0.06)
    ball(name + "_top", (0, 0, 0.64), 0.21, C("#9AA0A6", rough=0.7, coat=0.0), r, scale=(1, 0.33, 0.7))
    cube(name + "_band", (0, -0.075, 0.3), (0.3, 0.02, 0.07), C(color), r, bevel=0.01)
    cube(name + "_dirt", (0, -0.42, 0.03), (0.42, 0.62, 0.06), C("#6B4A2E", rough=0.8, coat=0.0), r, bevel=0.03)
    return r


def factory(name, loc, parent, color):
    r = build_root(name, loc, parent, 1.0)
    cube(name + "_b", (0, 0, 0.5), (1.5, 0.9, 1.0), C(color, rough=0.45), r)
    for i in range(3):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.5 + i * 0.5, 0, 1.12))
        t = bpy.context.object
        t.name, t.scale, t.rotation_euler = f"{name}_saw{i}", (0.5, 0.88, 0.32), (0.0, 0.0, 0.0)
        bpy.ops.object.transform_apply(scale=True)
        t.data.vertices[0].co.z = t.data.vertices[2].co.z = 0.0  # one side down: saw-tooth roof
        finish(t, C("#F4F1EA", rough=0.5), r, smooth=False)
    cyl(name + "_ch", (0.6, 0.25, 1.5), 0.11, 1.0, C("#8B4B3B", rough=0.6), r, verts=16)
    for i in range(4):
        cube(f"{name}_win{i}", (-0.55 + i * 0.37, -0.455, 0.55), (0.22, 0.02, 0.3), C("#FFE7A3", emit=0.5), r, bevel=0.01)
    smoke = [ball(f"{name}_smk{i}", (0.6, 0.25, 2.1 + i * 0.28), 0.14 + i * 0.04, C("#E9E6E0", rough=0.9, coat=0.0), r)
             for i in range(3)]
    return r, smoke


# ---------------------------------------------------------------- the diorama
def build():
    sc = reset()
    world = bpy.data.worlds.new("W")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[1].default_value = 1.0

    stage = empty("STAGE")
    north = empty("NORTH", parent=stage)  # Adi's half
    south = empty("SOUTH", parent=stage)  # Rudi's half

    # wooden board + grass, split in two halves by the river (y=0)
    for half, sgn in ((north, 1), (south, -1)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=8.5, depth=0.5, location=(0, 0, -0.25))
        b = bpy.context.object
        b.name = f"board{sgn}"
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.bisect(plane_co=(0, 0.55 * sgn, 0), plane_no=(0, -sgn, 0), clear_outer=True, use_fill=True)
        bpy.ops.object.mode_set(mode="OBJECT")
        finish(b, C("#B07A47", rough=0.55, coat=0.2), half, bevel=0.06, smooth=False)
        bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=8.2, depth=0.08, location=(0, 0, 0.04))
        g = bpy.context.object
        g.name = f"grass{sgn}"
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.bisect(plane_co=(0, 0.75 * sgn, 0), plane_no=(0, -sgn, 0), clear_outer=True, use_fill=True)
        bpy.ops.object.mode_set(mode="OBJECT")
        finish(g, C("#7BC86C" if sgn > 0 else "#86C766", rough=0.75, coat=0.0), half, smooth=False)
    river = cube("river", (0, 0, -0.08), (17.2, 1.4, 0.2), C("#3FA7D6", rough=0.12, coat=0.6), stage, bevel=0.0)
    river_root = river
    bridge = build_root("bridge", (0, 0, 0), stage)
    cube("bridge_deck", (0, 0, 0.12), (1.3, 1.9, 0.12), C("#C98F55", rough=0.5), bridge, bevel=0.03)
    for sx in (-1, 1):
        cube(f"bridge_rail{sx}", (0.6 * sx, 0, 0.32), (0.08, 1.9, 0.08), C("#8E5A30", rough=0.5), bridge, bevel=0.02)

    # town: houses and trees on both halves
    rng = random.Random(4)
    for half, sgn, walls, roof in ((north, 1, ("#F7E7C6", "#EAD9F2", "#D9ECF7"), "#2F6FD6"),
                                   (south, -1, ("#F7E7C6", "#F7D9D2", "#F2EBD0"), "#D6402F")):
        for i, (x, y) in enumerate([(-6.0, 4.5), (-5.2, 6.0), (0.8, 6.6), (5.8, 5.6), (6.6, 4.0)]):
            house(f"h{sgn}_{i}", (x, y * sgn, 0.08), half, walls[i % 3], roof, s=0.8 + rng.random() * 0.25, rz=rng.uniform(-0.2, 0.2))
        for i, (x, y) in enumerate([(-4.6, 7.0), (2.6, 7.3), (7.4, 2.6), (-7.4, 4.0), (4.0, 7.0)]):
            tree(f"t{sgn}_{i}", (x, y * sgn, 0.08), half, s=0.8 + rng.random() * 0.5)

    o = {"stage": stage, "north": north, "south": south, "bridge": bridge, "river": river_root, "bg": bg, "world": world}

    # Dassler home with the laundry tub and a clothesline (north, west)
    o["home"] = house("home", (-3.4, 3.2, 0.08), north, "#FFF1D6", "#8A5A3C", s=1.25)
    tub = build_root("tub", (-3.4, 2.15, 0.08), north)
    cyl("tub_b", (0, 0, 0.17), 0.36, 0.34, C("#A9B4BE", rough=0.3, coat=0.6), tub, bevel=0.04)
    cyl("tub_w", (0, 0, 0.3), 0.32, 0.04, C("#CFEAF7", rough=0.1, coat=0.8), tub, bevel=0.0)
    o["tub"] = tub
    line = build_root("line", (-3.4, 3.2, 0.08), north)
    for sx in (-1, 1):
        cyl(f"pole{sx}", (1.15 * sx, -1.4, 0.45), 0.03, 0.9, C("#6B4226"), line, bevel=0.0, verts=8)
    cyl("rope", (0, -1.4, 0.86), 0.008, 2.3, C("#EEEEEE"), line, bevel=0.0, verts=6, rot=(0, math.pi / 2, 0))
    for i, col in enumerate(("#FFFFFF", "#F2B33D", "#9FD3FF", "#FFB0A0")):
        cube(f"cloth{i}", (-0.75 + i * 0.5, -1.4, 0.7), (0.3, 0.02, 0.32), C(col, rough=0.8, coat=0.0), line, bevel=0.01)
    o["line"] = line
    o["mini"] = [shoe(f"mini{i}", (-3.9 + i * 0.33, 1.55, 0.09), north, "#F4F1EA", ("#2F6FD6", "#D6402F")[i % 2], s=0.42, rz=-0.3)
                 for i in range(4)]

    # stadium: oval track with a runner and four gold medals (north, east, back)
    st = build_root("stadium", (3.2, 4.4, 0.08), north)
    bpy.ops.mesh.primitive_torus_add(major_radius=1.35, minor_radius=0.28, location=(0, 0, 0.02))
    tr = bpy.context.object
    tr.name, tr.scale = "track", (1.45, 0.8, 0.12)
    finish(tr, C("#C8553D", rough=0.8, coat=0.0), st)
    cube("infield", (0, 0, 0.02), (2.9, 1.0, 0.04), C("#5DBB63", rough=0.8, coat=0.0), st, bevel=0.2)
    for sx in (-1, 1):
        cube(f"stand{sx}", (0, 1.45 * sx, 0.18), (3.6, 0.45, 0.36), C("#E8E1D1", rough=0.6), st, bevel=0.04)
    o["stadium"] = st
    runner_path = empty("runner_path", (0, 0, 0.0), st)
    o["runner_path"] = runner_path
    o["runner"] = peg("owens", "#FFFFFF", (1.95, 0, 0.04), runner_path, skin="#6B4430", hair="#1E1410", s=0.9)
    o["medals"] = []
    for i in range(4):
        m = build_root(f"medal{i}", (-0.9 + i * 0.6, -0.2, 1.7), st)
        cyl(f"medal{i}_d", (0, 0, 0), 0.2, 0.05, C("#F2B33D", rough=0.2, coat=0.8), m, rot=(math.pi / 2, 0, 0))
        cyl(f"medal{i}_r", (0, 0.01, 0.0), 0.12, 0.06, C("#E09A1F", rough=0.25, coat=0.8), m, rot=(math.pi / 2, 0, 0))
        o["medals"].append(m)

    # bomb shelter (north, east, front): concrete bunker open toward the camera, lamp inside
    bk = build_root("bunker", (3.4, 1.9, 0.08), north)
    grey = C("#8C9096", rough=0.75, coat=0.0)
    cube("bk_back", (0, 0.55, 0.55), (2.2, 0.15, 1.1), grey, bk)
    for sx in (-1, 1):
        cube(f"bk_side{sx}", (1.05 * sx, 0, 0.55), (0.15, 1.2, 1.1), grey, bk)
    cube("bk_roof", (0, 0, 1.15), (2.4, 1.3, 0.16), grey, bk)
    cube("bk_floor", (0, 0, 0.02), (2.1, 1.1, 0.04), C("#5E5A55", rough=0.9, coat=0.0), bk, bevel=0.0)
    cube("bk_bench", (0, 0.3, 0.16), (1.7, 0.3, 0.12), C("#7A5232", rough=0.6), bk, bevel=0.02)
    bulb = ball("bk_bulb", (0, 0.1, 0.98), 0.06, C("#FFE7A3", emit=8.0), bk)
    lamp = bpy.data.lights.new("bk_lamp", "POINT")
    lamp.energy, lamp.color, lamp.shadow_soft_size = 60, (1.0, 0.82, 0.55), 0.1
    lo = bpy.data.objects.new("bk_lamp", lamp)
    bpy.context.scene.collection.objects.link(lo)
    lo.parent, lo.location = bk, (0, 0, 0.85)
    o["bunker"], o["lamp"], o["bulb"] = bk, lamp, bulb

    # factories that rise after the split: Adi (north, blue) and Rudi (south, red)
    o["fA"], o["smkA"] = factory("fA", (-1.0, 3.0, 0.08), north, "#2F6FD6")
    o["fR"], o["smkR"] = factory("fR", (-1.0, -3.0, 0.08), south, "#D6402F")
    o["fR"].rotation_euler[2] = math.pi  # windows face the river
    o["shoeA"] = shoe("shoeA", (0.35, 1.85, 0.09), north, "#F4F1EA", "#2F6FD6", s=0.75, rz=0.4)
    o["shoeR"] = shoe("shoeR", (0.35, -1.85, 0.09), south, "#F4F1EA", "#D6402F", s=0.75, rz=-0.4 + math.pi)

    # each half's bars, bakeries and football pitch + townspeople
    o["awn"] = []
    for half, sgn, col in ((north, 1, "#2F6FD6"), (south, -1, "#D6402F")):
        for i, (x, y) in enumerate(((-5.3, 2.3), (-6.8, 2.1))):
            hb = house(f"shop{sgn}_{i}", (x, y * sgn, 0.08), half, "#FFF6E6", col, s=0.95, rz=0 if sgn > 0 else math.pi)
            aw = build_root(f"awn{sgn}_{i}", (0, -0.5, 0.6), hb)
            for k in range(4):
                cube(f"awn{sgn}_{i}_{k}", (-0.34 + k * 0.23, 0, 0), (0.23, 0.3, 0.06),
                     C(col if k % 2 == 0 else "#FFFFFF", rough=0.5), aw, bevel=0.01, rot=(0.45, 0, 0))
            sign = build_root(f"sign{sgn}_{i}", (0, -0.47, 1.0), hb)
            if i == 0:  # bar: a beer mug
                cyl(f"mug{sgn}", (0, 0, 0), 0.12, 0.24, C("#F2B33D", rough=0.2, coat=0.6), sign, bevel=0.02)
                cyl(f"foam{sgn}", (0, 0, 0.14), 0.13, 0.07, C("#FFFFFF", rough=0.6), sign, bevel=0.03)
            else:  # bakery: a pretzel
                bpy.ops.mesh.primitive_torus_add(major_radius=0.13, minor_radius=0.04, location=(0, 0, 0), rotation=(math.pi / 2, 0, 0))
                pz = bpy.context.object
                pz.name = f"pretzel{sgn}"
                finish(pz, C("#B5651D", rough=0.4), sign)
            o["awn"].append((aw, sign))
    o["pitchA"] = pitch("pitchA", (5.6, 2.2, 0.08), north)
    o["pitchR"] = pitch("pitchR", (5.6, -2.2, 0.08), south)
    o["folk"] = []
    rng = random.Random(7)
    for half, sgn, body in ((north, 1, "#2F6FD6"), (south, -1, "#D6402F")):
        for i, (x, y) in enumerate([(-6.6, 1.15), (-6.0, 0.95), (-5.4, 1.2), (-4.8, 1.0), (-4.2, 1.25), (-7.2, 1.6)]):
            f = peg(f"folk{sgn}_{i}", body, (x, y * sgn, 0.08), half, rz=(0 if sgn > 0 else math.pi) + rng.uniform(-0.6, 0.6),
                    s=0.62, hair=rng.choice(("#5A3A22", "#2B1D12", "#C9A15B", "#8A8A8A")), arms=False)
            o["folk"].append(f)

    # cemetery: two tombstones at opposite ends of the board
    o["tombA"] = tomb("tombA", (-7.7, 1.2, 0.08), north, "#2F6FD6")
    o["tombR"] = tomb("tombR", (7.7, -1.2, 0.08), south, "#D6402F")

    # planes, bomb puffs, final peace pitch over the river, ball
    o["planes"] = [plane_toy(f"plane{i}", (-12, 2.0 + i * 1.2, 4.2 + i * 0.4), stage) for i in range(3)]
    o["puffs"] = [ball(f"puff{i}", (x, y, 0.3), 0.5, C("#B9B4AA", rough=0.95, coat=0.0), stage)
                  for i, (x, y) in enumerate([(5.2, 4.0), (1.5, 5.6), (6.0, 0.9), (-1.6, 5.5)])]
    o["peace"] = pitch("peace", (0, 0, 0.3), stage, size=(3.4, 2.3))
    o["ballx"] = ball("soccer", (0, 0, 1.4), 0.12, C("#FFFFFF", rough=0.4), stage)
    o["mixed"] = [peg(f"mix{i}", ("#2F6FD6", "#D6402F")[i % 2], ((-1.2 + i * 0.48), (0.5 if i % 2 else -0.5), 0.34), stage,
                      rz=(math.pi / 2 if i % 2 else -math.pi / 2), s=0.55, arms=False) for i in range(6)]

    # the brothers: Adi (blue, flat cap) and Rudi (red, slicked hair)
    o["adi"] = peg("adi", "#2F6FD6", (-0.35, 0, 0.24), stage, hair="#3B2A1A", cap="#3A4A5C", rz=-math.pi / 2)
    o["rudi"] = peg("rudi", "#D6402F", (0.35, 0, 0.24), stage, hair="#1E1410", rz=math.pi / 2)

    # light + camera rig
    sun_d = bpy.data.lights.new("sun", "SUN")
    sun_d.energy, sun_d.angle, sun_d.color = 3.2, math.radians(8), (1.0, 0.95, 0.86)
    sun = bpy.data.objects.new("sun", sun_d)
    sc.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(48), math.radians(12), math.radians(-35))
    o["sun"] = sun_d
    rig = empty("RIG")
    tgt = empty("TGT")
    cam_d = bpy.data.cameras.new("cam")
    cam_d.lens = 42
    cam_d.dof.use_dof = True
    cam_d.dof.focus_object = tgt
    cam_d.dof.aperture_fstop = 0.35
    cam = bpy.data.objects.new("cam", cam_d)
    sc.collection.objects.link(cam)
    cam.parent = rig
    tt = cam.constraints.new("TRACK_TO")
    tt.target, tt.track_axis, tt.up_axis = tgt, "TRACK_NEGATIVE_Z", "UP_Y"
    sc.camera = cam
    o["rig"], o["tgt"], o["cam"] = rig, tgt, cam
    return sc, o


# ---------------------------------------------------------------- animation (all anchored to words)
def shot(o, t0, t1, cam, tgt, lens=None):
    move(o["cam"], t0, t1, cam)
    move(o["tgt"], t0, t1, tgt)
    if lens:
        d = o["cam"].data
        key(d, "lens", t0, d.lens)
        key(d, "lens", t1, lens)


def shake(o, t, dur=0.4, amp=0.08):
    """Short camera burst on a mood change (≤0.5 s, channel rule)."""
    rig = o["rig"]
    key(rig, "location", t, (0, 0, 0), "LINEAR")
    n = 6
    for i in range(1, n):
        a = amp * (1 - i / n)
        key(rig, "location", t + dur * i / n, (random.uniform(-a, a), random.uniform(-a, a), random.uniform(-a, a)), "LINEAR")
    key(rig, "location", t + dur, (0, 0, 0), "BEZIER")


def sky(o, t0, t1, col, sun_e, sun_col, strength=1.0):
    bg, sd = o["bg"], o["sun"]
    for t, c, e, sc_, st in ((t0, None, None, None, None), (t1, col, sun_e, sun_col, strength)):
        if c is not None:
            bg.inputs[0].default_value = (*hexrgb(c), 1)
            bg.inputs[1].default_value = st
            sd.energy, sd.color = e, sc_
        bg.inputs[0].keyframe_insert("default_value", frame=F(t))
        bg.inputs[1].keyframe_insert("default_value", frame=F(t))
        sd.keyframe_insert("energy", frame=F(t))
        sd.keyframe_insert("color", frame=F(t))


def talk(o, who, spk):
    """Mouth scale from mouth.json, only where this speaker talks (plus closed keys around)."""
    m = part(o[who], "mouth")
    env = MOUTH[spk]
    PREF.keyframe_new_interpolation_type = "LINEAR"
    prev = 0.0
    for f, v in enumerate(env):
        if v > 0.02 or prev > 0.02:
            m.scale = (1.3, 0.5, 0.25 + 1.6 * v)
            m.keyframe_insert("scale", frame=f)
        prev = v


def animate(o):
    PREF.keyframe_new_interpolation_type = "BEZIER"
    adi, rudi, cam = o["adi"], o["rudi"], o["cam"]
    zero = (0, 0, 0)

    # initial states: hidden props
    hidden = [o["tub"], o["line"], *o["mini"], o["stadium"], *o["medals"], o["fA"], o["fR"], o["shoeA"], o["shoeR"],
              o["pitchA"], o["pitchR"], *o["folk"], o["tombA"], o["tombR"], *o["puffs"], o["peace"], o["ballx"], *o["mixed"],
              o["bunker"]]
    for ob in hidden:
        key(ob, "scale", 0, zero, "CONSTANT")
    for aw, sign in o["awn"]:
        key(aw, "scale", 0, zero, "CONSTANT")
        key(sign, "scale", 0, zero, "CONSTANT")
    sky(o, 0, 0.01, "#FFD9A0", 3.2, (1.0, 0.95, 0.86), 1.2)

    # l0 — hook: the brothers face off on the bridge; a sneaker pops for each; they turn their backs
    key(cam, "location", 0, (0.0, -3.0, 1.5))
    key(o["tgt"], "location", 0, (0.0, 0.0, 0.62))
    key(cam.data, "lens", 0, 42)
    shot(o, 0.2, L("l0", 4.6), (0.4, -2.6, 1.25), (0.0, 0.0, 0.6))
    pop(o["shoeA"], W("l0", "adidas"), s=0.75)
    move(o["shoeA"], W("l0", "adidas"), W("l0", "adidas", d=0.4), (-0.85, -0.55, 0.3))
    pop(o["shoeR"], W("l0", "puma"), s=0.75)
    move(o["shoeR"], W("l0", "puma"), W("l0", "puma", d=0.4), (0.85, 0.55, 0.3))
    for ob, rz in ((adi, -math.pi / 2), (rudi, math.pi / 2)):
        key(ob, "location", W("l0", "hermanos", d=-0.1), tuple(ob.location))
        key(ob, "location", W("l0", "hermanos", d=0.08), (ob.location[0], ob.location[1], 0.42))
        key(ob, "location", W("l0", "hermanos", d=0.28), tuple(ob.location), "BACK")
    turn(adi, W("l0", "odiaban"), W("l0", "odiaban", d=0.35), math.pi / 2)
    turn(rudi, W("l0", "odiaban", d=0.1), W("l0", "odiaban", d=0.45), -math.pi / 2)
    for ob in (adi, rudi):
        a = part(ob, "armR"), part(ob, "armL")
        for arm in a:
            key(arm, "rotation_euler", W("l0", "odiaban"), (0, 0, 0))
            key(arm, "rotation_euler", W("l0", "odiaban", d=0.3), (0, math.radians(35 if arm is a[0] else -35), 0), "BACK")
    shake(o, W("l0", "odiaban"), 0.4, 0.05)
    unpop(o["shoeA"], L("l1", 0.2), s=0.75)
    unpop(o["shoeR"], L("l1", 0.25), s=0.75)

    # l1 — crane out over the toy town ("Alemania, años veinte"), brothers hop to the laundry tub at home
    shot(o, L("l1", 0.0), W("l1", "veinte", d=0.5), (-1.0, -12.5, 9.5), (0.0, 1.0, 0.0), lens=38)
    shot(o, W("l1", "adi", d=-0.2), W("l1", "dassler", d=0.3), (-3.0, -1.6, 2.1), (-3.4, 2.0, 0.55), lens=42)
    pop(o["tub"], W("l1", "adi", d=-0.1))
    pop(o["line"], W("l1", "lavanderia", d=-0.1))
    hop(adi, W("l1", "adi"), W("l1", "adi", d=0.55), (-3.95, 1.75, 0.08))
    turn(adi, W("l1", "adi"), W("l1", "adi", d=0.55), math.radians(-30))
    hop(rudi, W("l1", "rudi"), W("l1", "rudi", d=0.55), (-2.85, 1.75, 0.08))
    turn(rudi, W("l1", "rudi"), W("l1", "rudi", d=0.55), math.radians(30))
    for ob in (adi, rudi):
        for arm in (part(ob, "armR"), part(ob, "armL")):
            key(arm, "rotation_euler", W("l1", "hacen", d=-0.1), (0, 0, 0))
            key(arm, "rotation_euler", W("l1", "hacen", d=0.2), (math.radians(-70), 0, 0), "BACK")
    for i, s in enumerate(o["mini"]):  # shoes come out of the tub one after another
        t = W("l1", "zapatos", d=-0.05 + i * 0.15)
        pop(s, t, s=0.42)
        a = tuple(s.location)
        key(s, "location", t, (-3.4, 2.15, 0.45))
        key(s, "location", t + 0.35, a, "BACK")

    # l2 — the newest pair flies from the tub to the stadium: Jesse Owens runs, four golds
    shot(o, L("l2", 0.0), W("l2", "treinta", d=0.3), (3.4, -0.6, 3.2), (3.2, 4.4, 0.4), lens=40)
    pop(o["stadium"], L("l2", 0.05))
    rp = o["runner_path"]
    t_run0, t_run1 = W("l2", "jesse", d=-0.2), W("l2", "tenis", d=0.6)
    key(rp, "rotation_euler", t_run0, 0.0, "LINEAR", index=2)
    key(rp, "rotation_euler", t_run1, 2 * math.pi * 1.25, "LINEAR", index=2)
    rp.scale = (1.0, 0.62, 1.0)
    rn = o["runner"]
    rn.rotation_euler[2] = 0.0
    for k in range(int((t_run1 - t_run0) / 0.16)):  # running bob
        key(rn, "location", t_run0 + k * 0.16, (1.95, 0, 0.04 + (0.07 if k % 2 else 0.0)), "LINEAR")
    for arm, sgn in ((part(rn, "armR"), 1), (part(rn, "armL"), -1)):
        for k in range(int((t_run1 - t_run0) / 0.16)):
            key(arm, "rotation_euler", t_run0 + k * 0.16, (math.radians(45 * sgn * (1 if k % 2 else -1)), 0, 0), "LINEAR")
    for i, m in enumerate(o["medals"]):
        pop(m, W("l2", "cuatro", d=i * 0.17))
        key(m, "rotation_euler", W("l2", "cuatro", d=i * 0.17), (0, 0, 0))
        key(m, "rotation_euler", W("l2", "tenis", d=0.8), (0, 0, 2 * math.pi), "LINEAR")
    shot(o, W("l2", "con", d=-0.1), W("l2", "tenis", d=0.2), (3.2, 2.2, 1.6), (3.2, 4.4, 0.35), lens=50)

    # l3 — war: sky darkens, planes cross, bombs puff, both brothers end up in the same shelter
    sky(o, W("l3", "guerra", d=-0.2), W("l3", "guerra", d=0.5), "#6F6A73", 1.2, (1.0, 0.7, 0.5), 0.55)
    shot(o, L("l3", 0.0), W("l3", "guerra", d=0.4), (2.0, -6.5, 6.0), (2.5, 3.0, 1.5), lens=36)
    for i, p in enumerate(o["planes"]):
        t0 = W("l3", "guerra", d=0.1 + i * 0.25)
        key(p, "location", t0, (-12, 2.0 + i * 1.2, 4.2 + i * 0.4), "LINEAR")
        key(p, "location", t0 + 4.5, (14, 2.6 + i * 1.2, 4.6 + i * 0.4), "LINEAR")
    for i, pf in enumerate(o["puffs"]):
        t = W("l3", "bombardeo", d=i * 0.22)
        pop(pf, t, 0.3, s=1.0 + 0.3 * (i % 2))
        unpop(pf, t + 0.9, 0.5, s=1.0 + 0.3 * (i % 2))
        e = o["sun"]
        key(e, "energy", t, 1.2, "LINEAR")
        key(e, "energy", t + 0.06, 6.0, "LINEAR")
        key(e, "energy", t + 0.25, 1.2, "BEZIER")
    shake(o, W("l3", "bombardeo"), 0.45, 0.12)
    for i, m in enumerate(o["medals"]):
        unpop(m, L("l3", 0.1 + i * 0.05), 0.25)
    pop(o["bunker"], W("l3", "terminan", d=-0.3))
    for ob, x in ((adi, -0.5), (rudi, 0.5)):
        key(ob, "rotation_euler", W("l3", "terminan"), (0, 0, ob.rotation_euler[2]))
        hop(ob, W("l3", "terminan", d=0.05 if ob is adi else 0.2), W("l3", "mismo", d=0.1 if ob is adi else 0.25),
            (3.4 + x, 1.95, 0.12), h=1.2)
        key(ob, "rotation_euler", W("l3", "mismo", d=0.25), (0, 0, 0), "BACK")
        for arm in (part(ob, "armR"), part(ob, "armL")):
            key(arm, "rotation_euler", W("l3", "terminan"), tuple(arm.rotation_euler))
            key(arm, "rotation_euler", W("l3", "mismo", d=0.2), (0, 0, 0))
    shot(o, W("l3", "refugio", d=-0.4), W("l3", "refugio", d=0.4), (3.4, -1.2, 1.05), (3.4, 1.9, 0.62), lens=40)

    # l4 — Adi points at the sky: "¡Ahí vienen otra vez esos desgraciados!"
    shot(o, L("l4", -0.15), L("l4", 0.3), (2.75, -0.6, 0.95), (2.9, 1.95, 0.75), lens=55)
    arm = part(adi, "armR")
    key(arm, "rotation_euler", W("l4", "ahi", d=-0.05), (0, 0, 0))
    key(arm, "rotation_euler", W("l4", "ahi", d=0.25), (math.radians(-160), 0, math.radians(-20)), "BACK")
    turn(adi, W("l4", "ahi"), W("l4", "ahi", d=0.3), math.radians(-25))
    key(part(adi, "head"), "rotation_euler", W("l4", "ahi"), (0, 0, 0))
    key(part(adi, "head"), "rotation_euler", W("l4", "ahi", d=0.3), (math.radians(-25), 0, 0), "BACK")
    talk(o, "adi", "adi")

    # l5 — Rudi snaps around, red-faced: "¿¡Desgraciados!? ¿¡Me lo dices a mí!?"
    shot(o, L("l5", -0.15), L("l5", 0.25), (4.1, -0.6, 0.95), (3.9, 1.95, 0.75), lens=55)
    turn(rudi, L("l5", -0.1), L("l5", 0.2), math.radians(60))
    hd = part(rudi, "head")
    face = hd.children[0].data.materials[0]
    angry = face.copy()
    angry.name = "rudi_angry"
    hd.children[0].data.materials[0] = angry
    bsdf = angry.node_tree.nodes["Principled BSDF"].inputs["Base Color"]
    for t, c in ((L("l5", -0.05), SKIN), (L("l5", 0.35), "#E8584A"), (L("l6", 1.2), "#E8584A"), (L("l6", 2.0), SKIN)):
        bsdf.default_value = (*hexrgb(c), 1)
        bsdf.keyframe_insert("default_value", frame=F(t))
    key(rudi, "location", L("l5", 0.0), (3.9, 1.95, 0.12))
    key(rudi, "location", L("l5", 0.15), (3.9, 1.95, 0.35))
    key(rudi, "location", L("l5", 0.35), (3.9, 1.95, 0.12), "BACK")
    for a, sgn in ((part(rudi, "armR"), 1), (part(rudi, "armL"), -1)):
        key(a, "rotation_euler", W("l5", "me", d=-0.1), (0, 0, 0))
        key(a, "rotation_euler", W("l5", "me", d=0.15), (math.radians(-80), 0, math.radians(30 * sgn)), "BACK")
    shake(o, L("l5", 0.0), 0.35, 0.04)
    talk(o, "rudi", "rudi")

    # l6 — the planes pass; Adi points up ("de los aviones"), Rudi crosses arms and turns away
    shot(o, L("l6", 0.0), W("l6", "aviones", d=0.2), (3.4, -1.6, 1.4), (3.4, 3.5, 3.4), lens=34)
    for i, p in enumerate(o["planes"]):
        t0 = W("l6", "hablaba", d=-0.6 + i * 0.25)
        key(p, "location", t0, (-4, 3.0 + i * 0.6, 3.8 + i * 0.3), "LINEAR")
        key(p, "location", t0 + 2.6, (11, 3.4 + i * 0.6, 4.0 + i * 0.3), "LINEAR")
    shot(o, W("l6", "rudi", d=-0.3), W("l6", "rudi", d=0.3), (3.6, -0.9, 1.05), (3.6, 1.95, 0.7), lens=48)
    turn(rudi, W("l6", "nunca"), W("l6", "nunca", d=0.35), math.radians(200))
    hd = part(rudi, "head")
    for k in range(4):  # head shake "no"
        key(hd, "rotation_euler", W("l6", "creyo", d=-0.2 + k * 0.12), (0, 0, math.radians(18 * (1 if k % 2 else -1))), "LINEAR")
    key(hd, "rotation_euler", W("l6", "creyo", d=0.35), (0, 0, 0))
    key(arm, "rotation_euler", W("l6", "nunca"), tuple(arm.rotation_euler))
    key(arm, "rotation_euler", W("l6", "nunca", d=0.4), (0, 0, 0))

    # l7 — 1948: the board splits along the river; each brother gets a half and a factory
    sky(o, L("l7", -0.3), L("l7", 0.5), "#FFD9A0", 3.2, (1.0, 0.95, 0.86), 1.2)
    unpop(o["bunker"], L("l7", 0.0), 0.3)
    shot(o, L("l7", 0.0), W("l7", "separan", d=-0.1), (0.0, -14.5, 13.0), (0.0, 0.0, 0.0), lens=34)
    hop(adi, L("l7", 0.1), W("l7", "separan", d=-0.2), (-1.0, 1.8, 0.08), h=1.6)
    hop(rudi, L("l7", 0.25), W("l7", "separan", d=-0.05), (-1.0, -1.8, 0.08), h=1.6)
    turn(adi, L("l7", 0.1), W("l7", "separan", d=-0.2), 0.0)
    turn(rudi, L("l7", 0.25), W("l7", "separan"), math.pi)
    t_sep = W("l7", "separan")
    for half, sgn in ((o["north"], 1), (o["south"], -1)):
        key(half, "location", t_sep, (0, 0, 0))
        key(half, "location", t_sep + 0.9, (0, 1.2 * sgn, 0), "BACK")
    key(o["river"], "scale", t_sep, (1, 1, 1))
    key(o["river"], "scale", t_sep + 0.9, (1, 2.75, 1), "BACK")
    key(o["bridge"], "scale", t_sep, (1, 1, 1))
    key(o["bridge"], "scale", t_sep + 0.4, (0, 0, 0))
    for ob, dy in ((adi, 1.2), (rudi, -1.2)):
        key(ob, "location", t_sep, tuple(ob.location))
        key(ob, "location", t_sep + 0.9, (ob.location[0], ob.location[1] + dy, ob.location[2]), "BACK")
    shake(o, t_sep, 0.45, 0.1)
    pop(o["fA"], W("l7", "adidas", d=-0.15), 0.45)
    pop(o["fR"], W("l7", "puma", d=-0.15), 0.45)
    for smk, w in ((o["smkA"], "adidas"), (o["smkR"], "puma")):
        for i, s in enumerate(smk):
            pop(s, W("l7", w, d=0.35 + i * 0.12), 0.3)
    shot(o, W("l7", "adidas", d=-0.4), W("l7", "adidas", d=0.2), (-1.0, -0.6, 2.4), (-1.0, 3.7, 0.8), lens=34)
    shot(o, W("l7", "puma", d=-0.35), W("l7", "puma", d=0.2), (-1.0, 0.4, 1.7), (-1.0, -3.7, 0.95), lens=34)
    shot(o, W("l7", "cada", d=-0.2), W("l7", "rio", d=0.2), (-1.0, -10.0, 8.5), (-1.0, 0.4, 0.3), lens=28)

    # l8 — the whole town split: bars, bakeries, football pitches; people look at your shoes (bent necks)
    shot(o, L("l8", 0.0), W("l8", "dos", d=0.3), (-9.5, -7.5, 8.0), (-4.0, 0.0, 0.0), lens=34)
    for i, (aw, sign) in enumerate(o["awn"]):
        w = "bares" if i % 2 == 0 else "panaderias"
        pop(aw, W("l8", w, d=(i // 2) * 0.15))
        pop(sign, W("l8", w, d=0.1 + (i // 2) * 0.15))
    pop(o["pitchA"], W("l8", "futbol", d=-0.35))
    pop(o["pitchR"], W("l8", "futbol", d=-0.2))
    shot(o, W("l8", "hasta", d=-0.1), W("l8", "futbol", d=0.2), (5.6, -9.5, 7.5), (5.6, 0.3, 0.0), lens=28)
    for i, f in enumerate(o["folk"]):
        pop(f, W("l8", "antes", d=-0.4 + (i % 6) * 0.07), s=0.62)
    shot(o, W("l8", "antes", d=-0.3), W("l8", "hablarte", d=0.1), (-5.6, -1.6, 2.0), (-5.6, 2.3, 0.25), lens=40)
    for i, f in enumerate(o["folk"]):
        hd = part(f, "head")
        t = W("l8", "miraban", d=(i % 6) * 0.08)
        key(hd, "rotation_euler", t, (0, 0, 0))
        key(hd, "rotation_euler", t + 0.3, (math.radians(38), 0, 0), "BACK")

    # l9 — night: graves at opposite ends of the board
    sky(o, L("l9", -0.2), L("l9", 0.6), "#27305C", 1.6, (0.62, 0.72, 1.0), 0.7)
    pop(o["tombA"], L("l9", 0.2))
    pop(o["tombR"], W("l9", "extremos", d=-0.1))
    for ob in (adi, rudi):
        unpop(ob, L("l9", 0.1), 0.3)
    for i, f in enumerate(o["folk"]):  # townspeople go home at night: they hid the graves
        unpop(f, L("l9", -0.2 + (i % 6) * 0.04), 0.25, s=0.62)
    shot(o, L("l9", 0.0), W("l9", "muertos", d=0.5), (-6.9, -1.4, 1.5), (-7.7, 2.4, 0.45), lens=40)
    shot(o, W("l9", "extremos", d=-0.3), W("l9", "opuestos", d=0.0), (6.9, 1.4, 1.5), (7.7, -2.4, 0.45), lens=40)
    shot(o, W("l9", "cementerio", d=0.1), L("l10", 0.4), (0.0, -15.0, 6.5), (0.0, 0.0, 0.3), lens=26)

    # l10 — sunrise, the halves join again; one match with mixed teams over the river (2009)
    sky(o, L("l10", -0.1), L("l10", 0.6), "#FFD9A0", 3.2, (1.0, 0.95, 0.86), 1.2)
    t_join = W("l10", "paces", d=-0.1)
    for half in (o["north"], o["south"]):
        key(half, "location", t_join, tuple(half.location))
        key(half, "location", t_join + 0.8, (0, 0, 0), "BACK")
    key(o["river"], "scale", t_join, (1, 2.75, 1))
    key(o["river"], "scale", t_join + 0.8, (1, 1, 1), "BACK")
    pop(o["peace"], W("l10", "partido", d=-0.15))
    for i, p in enumerate(o["mixed"]):
        pop(p, W("l10", "partido", d=0.05 + i * 0.06), s=0.55)
    pop(o["ballx"], W("l10", "futbol", d=-0.35))
    bl = o["ballx"]
    t0 = W("l10", "futbol", d=-0.3)
    for k, (x, z) in enumerate([(0, 1.4), (0.5, 0.42), (1.0, 0.9), (1.4, 0.42), (1.7, 0.7), (1.95, 0.42)]):
        key(bl, "location", t0 + k * 0.2, (x, 0, z), "BEZIER")
    shot(o, L("l10", 0.0), W("l10", "partido", d=0.3), (6.5, -1.6, 3.2), (0.0, 0.0, 0.3), lens=34)
    shot(o, W("l10", "futbol", d=-0.2), END, (4.4, -1.0, 1.6), (1.0, 0.0, 0.45), lens=40)


def render(sc, a=None, b=None, force=None):
    out = ROOT / "blender" / "frames"
    out.mkdir(parents=True, exist_ok=True)
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    a, b = int(a or 0), int(b or LAST)
    for f in range(a, b + 1):
        p = out / f"f{f:05d}.png"
        if p.exists() and not force:
            continue
        sc.frame_set(f)
        sc.render.filepath = str(p)
        bpy.ops.render.render(write_still=True)


def stills(sc, times):
    out = ROOT / "blender" / "stills"
    out.mkdir(parents=True, exist_ok=True)
    sc.render.resolution_percentage = 50
    sc.render.image_settings.file_format = "JPEG"
    for t in times:
        sc.frame_set(F(float(t)))
        sc.render.filepath = str(out / f"t{float(t):05.1f}.jpg")
        bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["save"]
    sc, o = build()
    animate(o)
    sc.frame_set(0)
    if argv[0] == "save":
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "blender" / "escena.blend"))
    elif argv[0] == "still":
        stills(sc, argv[1].split(","))
    elif argv[0] == "render":
        render(sc, *argv[1:4])
    print(f"END {END} s, frames 0..{LAST}")


main()
