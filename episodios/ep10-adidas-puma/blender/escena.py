"""EP10 v2: Adidas vs Puma as a handmade toy world (Blender, EEVEE) — six separate sets instead of one board.

  blender -b -P blender/escena.py -- still 0.5,8,15        # 50 % JPEGs in blender/stills/ (to review)
  blender -b -P blender/escena.py -- render [from to]      # 1080×1920 PNG in blender/frames/ (skips existing)
  blender -b -P blender/escena.py -- save                  # blender/escena.blend to open by hand

Sets (far apart, the camera cuts between them): HOOK stage, LAUNDRY interior, STADIUM 1936, TOWN board (night war, day split,
divided streets, sunrise), BUNKER interior, CEMETERY at night. Each has its own light and mood; the sky is a gradient keyed
per shot. Every cue is anchored to a word with W(line, word) from transcript.json, so a new voice re-syncs by itself.
No brand logos: only colours (the names are HTML labels).
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
END = round(LINES["l10"]["end"] + 0.45, 2)  # the HTML end card covers everything after this
LAST = int(END * FPS) + 6
random.seed(10)

BLUE, RED, GOLD, CREAM = "#2F6FD6", "#D6402F", "#F2B33D", "#F4F1EA"
SKIN, INK = "#F2C29B", "#1B1B2F"
P_HOOK, P_LAUN, P_STAD, P_BUNK, P_CEME = (60, 0, 0), (-60, 0, 0), (0, 60, 0), (0, -60, 0), (60, 60, 0)


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


def add(p, v):
    return tuple(a + b for a, b in zip(p, v))


# ---------------------------------------------------------------- keyframes
PREF = bpy.context.preferences.edit


def key(owner, path, t, value, interp="BEZIER", index=-1, frame=None):
    """Keyframe at time t (s). interp: BEZIER (ease), BACK (overshoot), LINEAR, CONSTANT."""
    PREF.keyframe_new_interpolation_type = interp
    setattr(owner, path, value) if index < 0 else getattr(owner, path).__setitem__(index, value)
    owner.keyframe_insert(path, frame=F(t) if frame is None else frame, index=index)


def pop(ob, t, dur=0.35, s=1.0):
    key(ob, "scale", t - 0.01, (0, 0, 0), "BACK")
    key(ob, "scale", t + dur, (s, s, s), "BEZIER")


def unpop(ob, t, dur=0.25, s=1.0):
    key(ob, "scale", t, (s, s, s), "BEZIER")
    key(ob, "scale", t + dur, (0, 0, 0), "BEZIER")



def move(ob, t0, t1, loc, interp="BEZIER", end="BEZIER"):
    key(ob, "location", t0, tuple(ob.location), interp)
    key(ob, "location", t1, loc, end)


def hop(ob, t0, t1, loc, h=0.8):
    a = tuple(ob.location)
    mid = ((a[0] + loc[0]) / 2, (a[1] + loc[1]) / 2, max(a[2], loc[2]) + h)
    key(ob, "location", t0, a)
    key(ob, "location", (t0 + t1) / 2, mid)
    key(ob, "location", t1, loc, "BACK")


def turn(ob, t0, t1, rz):
    key(ob, "rotation_euler", t0, ob.rotation_euler[2], index=2)
    key(ob, "rotation_euler", t1, rz, "BACK", index=2)


def hidden(*obs):
    for ob in obs:
        key(ob, "scale", 0, (0, 0, 0), "CONSTANT")


# ---------------------------------------------------------------- scene and materials
def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "BLENDER_EEVEE"
    sc.render.resolution_x, sc.render.resolution_y = 1080, 1920
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 0, LAST
    ee = sc.eevee
    for attr, v in (("taa_render_samples", 32), ("use_shadows", True), ("use_raytracing", True), ("use_fast_gi", True),
                    ("volumetric_tile_size", "4"), ("volumetric_samples", 48), ("volumetric_end", 140.0),
                    ("use_volumetric_shadows", True), ("motion_blur_steps", 1)):
        if hasattr(ee, attr):
            try:
                setattr(ee, attr, v)
            except (TypeError, ValueError):
                pass
    sc.render.use_motion_blur = True
    sc.render.motion_blur_shutter = 0.5
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = "AgX - Punchy"
    except TypeError:
        pass
    return sc


MATS = {}


def nodes_of(m):
    try:
        m.use_nodes = True
    except AttributeError:
        pass
    return m.node_tree.nodes, m.node_tree.links


def hexrgb(h):
    h = h.lstrip("#")
    srgb = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in srgb)


def mat(name, rgb, rough=0.45, coat=0.25, emit=0.0, kind=None, bump=1.0, rgb2=None, sheen=0.0, scale=1.0):
    """Handmade look: every surface gets a fine noise bump (paint / fingerprints). kind: wood, checker, stripes, felt,
    water, objcolor (colour from Object.color, for shared meshes)."""
    if name in MATS:
        return MATS[name]
    m = bpy.data.materials.new(name)
    N, Lk = nodes_of(m)
    b = N["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Coat Weight"].default_value = coat
    if sheen:
        b.inputs["Sheen Weight"].default_value = sheen
    if emit:
        b.inputs["Emission Color"].default_value = (*rgb, 1)
        b.inputs["Emission Strength"].default_value = emit
    rgb2 = hexrgb(rgb2) if isinstance(rgb2, str) else rgb2
    tc = N.new("ShaderNodeTexCoord")
    dark = tuple(c * 0.62 for c in rgb)
    if kind == "wood":
        wv = N.new("ShaderNodeTexWave")
        wv.inputs["Scale"].default_value, wv.inputs["Distortion"].default_value = 3.0 * scale, 9.0
        wv.inputs["Detail"].default_value = 3.0
        Lk.new(tc.outputs["Object"], wv.inputs["Vector"])
        rp = N.new("ShaderNodeValToRGB")
        rp.color_ramp.elements[0].color, rp.color_ramp.elements[1].color = (*dark, 1), (*rgb, 1)
        Lk.new(wv.outputs["Fac"], rp.inputs["Fac"])
        Lk.new(rp.outputs["Color"], b.inputs["Base Color"])
    elif kind == "checker":
        ck = N.new("ShaderNodeTexChecker")
        ck.inputs["Color1"].default_value, ck.inputs["Color2"].default_value = (*rgb, 1), (*(rgb2 or dark), 1)
        ck.inputs["Scale"].default_value = 1.0 * scale
        Lk.new(tc.outputs["Object"], ck.inputs["Vector"])
        Lk.new(ck.outputs["Color"], b.inputs["Base Color"])
    elif kind == "stripes":
        wv = N.new("ShaderNodeTexWave")
        wv.inputs["Scale"].default_value, wv.inputs["Distortion"].default_value = 2.0 * scale, 0.0
        Lk.new(tc.outputs["Object"], wv.inputs["Vector"])
        rp = N.new("ShaderNodeValToRGB")
        rp.color_ramp.interpolation = "CONSTANT"
        rp.color_ramp.elements[1].position = 0.5
        rp.color_ramp.elements[0].color, rp.color_ramp.elements[1].color = (*rgb, 1), (*(rgb2 or dark), 1)
        Lk.new(wv.outputs["Fac"], rp.inputs["Fac"])
        Lk.new(rp.outputs["Color"], b.inputs["Base Color"])
    elif kind == "objcolor":
        oi = N.new("ShaderNodeObjectInfo")
        Lk.new(oi.outputs["Color"], b.inputs["Base Color"])
    if kind == "felt":
        b.inputs["Sheen Weight"].default_value = 0.6
    if bump:
        nz = N.new("ShaderNodeTexNoise")
        nz.inputs["Scale"].default_value = 26.0 if kind != "water" else 3.5
        nz.inputs["Detail"].default_value = 6.0
        if kind == "water":
            mp = N.new("ShaderNodeMapping")
            Lk.new(tc.outputs["Object"], mp.inputs["Vector"])
            Lk.new(mp.outputs["Vector"], nz.inputs["Vector"])
            loc = mp.inputs["Location"]
            for f, v in ((0, (0, 0, 0)), (LAST, (2.5, 0.6, 1.5))):
                loc.default_value = v
                PREF.keyframe_new_interpolation_type = "LINEAR"
                loc.keyframe_insert("default_value", frame=f)
        else:
            Lk.new(tc.outputs["Object"], nz.inputs["Vector"])
        bp = N.new("ShaderNodeBump")
        bp.inputs["Strength"].default_value = 0.18 * bump if kind != "felt" else 0.45 * bump
        bp.inputs["Distance"].default_value = 0.02
        Lk.new(nz.outputs["Fac"], bp.inputs["Height"])
        Lk.new(bp.outputs["Normal"], b.inputs["Normal"])
    MATS[name] = m
    return m


def C(h, **kw):
    return mat(h + str(sorted(kw.items())), hexrgb(h), **kw)


def fog(name, loc, size, density, col="#FFFFFF", parent=None):
    """Volume box (light shafts, fog). Returns the density socket so it can be keyed."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    ob = bpy.context.object
    ob.name, ob.scale = name, size
    ob.parent = parent
    m = bpy.data.materials.new(name)
    N, Lk = nodes_of(m)
    N.remove(N["Principled BSDF"])
    v = N.new("ShaderNodeVolumePrincipled")
    v.inputs["Color"].default_value = (*hexrgb(col), 1)
    v.inputs["Density"].default_value = density
    Lk.new(v.outputs[0], N["Material Output"].inputs["Volume"])
    ob.data.materials.append(m)
    return v.inputs["Density"]


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


def ball(name, loc, r, m, parent=None, scale=(1, 1, 1), seg=32):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=seg, ring_count=seg // 2, radius=r, location=loc)
    ob = bpy.context.object
    ob.name, ob.scale = name, scale
    return finish(ob, m, parent)


def empty(name, loc=(0, 0, 0), parent=None):
    ob = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(ob)
    ob.location = loc
    ob.parent = parent
    return ob


def root(name, loc, parent, scale=1.0, rz=0.0):
    r = empty(name, loc, parent)
    r.rotation_euler[2] = rz
    r.scale = (scale,) * 3
    return r


def template(ob):
    """Turn a freshly built object into a shared mesh (for crowds, confetti, graves)."""
    me = ob.data
    bpy.data.objects.remove(ob)
    return me


def inst(name, me, loc, parent=None, color=None, rot=(0, 0, 0), scale=(1, 1, 1)):
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location, ob.rotation_euler, ob.scale = loc, rot, scale
    ob.parent = parent
    if color:
        ob.color = (*hexrgb(color), 1)
    return ob


def light(kind, name, loc, energy, col="#FFFFFF", parent=None, size=0.1, rot=(0, 0, 0), spot=40, dist=30):
    d = bpy.data.lights.new(name, kind)
    d.energy, d.color = energy, hexrgb(col)
    if kind != "SUN":
        d.shadow_soft_size = size
    if kind == "SPOT":
        d.spot_size, d.spot_blend = math.radians(spot), 0.35
        d.specular_factor = 0.25  # no mirror-disc highlights of the lamp on glossy floors
    if hasattr(d, "use_custom_distance"):
        d.use_custom_distance, d.cutoff_distance = True, dist
    ob = bpy.data.objects.new(name, d)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent, ob.location, ob.rotation_euler = parent, loc, rot
    return ob


def aim(ob, target):
    """Point a light (−Z) at a world point."""
    from mathutils import Vector
    d = Vector(target) - ob.matrix_world.translation if ob.parent is None else Vector(target) - Vector(ob.location)
    ob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()


# ---------------------------------------------------------------- props
def peg(name, body, loc, parent=None, skin=SKIN, hair="#5A3A22", rz=0.0, s=1.0, cap=None, arms=True, feet=None, bun=False):
    """Wooden peg doll (~0.95 tall). Parts stored as names: head, mouth, armR, armL, eyes, brows."""
    r = root(name, loc, parent, s, rz)
    cyl(name + "_body", (0, 0, 0.28), 0.2, 0.56, C(body, kind="wood", rough=0.4), r, bevel=0.06)
    cyl(name + "_belt", (0, 0, 0.2), 0.205, 0.05, C("#3A2A1E", rough=0.6), r, bevel=0.01)
    head = empty(name + "_neck", (0, 0, 0.56), r)
    ball(name + "_head", (0, 0, 0.2), 0.2, C(skin, rough=0.5, coat=0.1), head)
    ball(name + "_hair", (0, 0.02, 0.27), 0.195, C(hair, rough=0.7, coat=0.0, kind="felt"), head, scale=(1.03, 1.03, 0.62))
    if bun:
        ball(name + "_bun", (0, 0.12, 0.4), 0.09, C(hair, rough=0.7, kind="felt"), head)
    if cap:
        cyl(name + "_cap", (0, 0, 0.37), 0.2, 0.08, C(cap, kind="felt"), head, bevel=0.02)
        cube(name + "_visor", (0, -0.2, 0.34), (0.26, 0.14, 0.03), C(cap, kind="felt"), head, bevel=0.01)
    eyes, brows = [], []
    for sx in (-1, 1):
        eyes.append(ball(f"{name}_eye{sx}", (0.075 * sx, -0.175, 0.23), 0.032, C(INK, coat=0.6), head).name)
        ball(f"{name}_cheek{sx}", (0.12 * sx, -0.15, 0.15), 0.035, C("#F08A7A", rough=0.6, coat=0.0), head, scale=(1, 0.4, 0.7))
        brows.append(cube(f"{name}_brow{sx}", (0.075 * sx, -0.18, 0.3), (0.09, 0.02, 0.022), C(hair), head, bevel=0.008).name)
    mouth = ball(name + "_mouth", (0, -0.185, 0.12), 0.045, C("#7A2230", coat=0.2), head, scale=(1.3, 0.5, 0.25))
    arm_r = arm_l = None
    if arms:
        arm_r = empty(name + "_armR", (0.21, 0, 0.48), r)
        cyl(name + "_armRm", (0, 0, -0.17), 0.055, 0.34, C(body, kind="wood"), arm_r, bevel=0.02)
        ball(name + "_handR", (0, 0, -0.35), 0.06, C(skin, rough=0.5, coat=0.1), arm_r)
        arm_l = empty(name + "_armL", (-0.21, 0, 0.48), r)
        cyl(name + "_armLm", (0, 0, -0.17), 0.055, 0.34, C(body, kind="wood"), arm_l, bevel=0.02)
        ball(name + "_handL", (0, 0, -0.35), 0.06, C(skin, rough=0.5, coat=0.1), arm_l)
    if feet:
        for sx in (-1, 1):
            shoe(f"{name}_ft{sx}", (0.1 * sx, -0.13, 0.0), r, CREAM, feet, s=0.28)
    r["head"], r["mouth"] = head.name, mouth.name
    r["armR"], r["armL"] = (arm_r.name if arm_r else ""), (arm_l.name if arm_l else "")
    r["eyes"], r["brows"] = ",".join(eyes), ",".join(brows)
    return r


def part(rt, k):
    return bpy.data.objects[rt[k]]


def parts(rt, k):
    return [bpy.data.objects[n] for n in rt[k].split(",")]


def blink(rt, t0, t1, every=2.9, phase=0.0):
    for e in parts(rt, "eyes"):
        t = t0 + phase
        while t < t1:
            key(e, "scale", t, (1, 1, 1), "LINEAR")
            key(e, "scale", t + 0.05, (1, 1, 0.12), "LINEAR")
            key(e, "scale", t + 0.12, (1, 1, 1), "LINEAR")
            t += every


def brows(rt, t, mood, dur=0.15):
    """mood: 0 neutral, 1 angry, -1 worried."""
    for b, sx in zip(parts(rt, "brows"), (-1, 1)):
        key(b, "rotation_euler", t, tuple(b.rotation_euler))
        key(b, "rotation_euler", t + dur, (0, -0.45 * sx * mood, 0), "BACK")


def house(name, loc, parent, wall, roof, s=1.0, rz=0.0):
    r = root(name, loc, parent, s, rz)
    cube(name + "_w", (0, 0, 0.4), (0.9, 0.8, 0.8), C(wall, rough=0.7, coat=0.05), r)
    for sx in (-1, 1):  # timber frame
        cube(f"{name}_beam{sx}", (0.44 * sx, -0.405, 0.4), (0.06, 0.02, 0.8), C("#6B4226", kind="wood"), r, bevel=0.005)
    cube(name + "_beamh", (0, -0.405, 0.42), (0.9, 0.02, 0.05), C("#6B4226", kind="wood"), r, bevel=0.005)
    bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=0.78, depth=0.55, location=(0, 0, 1.07), rotation=(0, 0, math.pi / 4))
    rf = bpy.context.object
    rf.name, rf.scale = name + "_r", (1.0, 0.95, 1)
    finish(rf, C(roof, rough=0.6, kind="felt"), r, smooth=False)
    cyl(name + "_chim", (0.25, 0.15, 1.15), 0.06, 0.4, C("#8B4B3B", rough=0.7), r, verts=10)
    cube(name + "_door", (0, -0.405, 0.18), (0.2, 0.03, 0.34), C("#6B4226", kind="wood"), r, bevel=0.01)
    for sx in (-1, 1):
        cube(f"{name}_win{sx}", (0.24 * sx, -0.405, 0.6), (0.16, 0.03, 0.16), C("#FFE7A3", emit=1.2), r, bevel=0.01)
    return r


def tree(name, loc, parent, s=1.0, col="#3E8E4A"):
    r = root(name, loc, parent, s)
    cyl(name + "_t", (0, 0, 0.18), 0.06, 0.36, C("#7A4E2D", kind="wood"), r, bevel=0.0, verts=12)
    for i, (z, rr) in enumerate(((0.5, 0.34), (0.75, 0.27), (0.97, 0.18))):
        cone(f"{name}_c{i}", (0, 0, z), rr, 0.4, C(col, rough=0.8, kind="felt"), r, verts=20)
    return r


def bush(name, loc, parent, s=1.0):
    r = root(name, loc, parent, s)
    for i, (x, y, rr) in enumerate(((0, 0, 0.22), (0.18, 0.05, 0.16), (-0.16, 0.04, 0.15))):
        ball(f"{name}_{i}", (x, y, rr * 0.7), rr, C("#4E9A4A", rough=0.85, kind="felt"), r, seg=16)
    return r


def cloud(name, loc, parent=None, s=1.0):
    r = root(name, loc, parent, s)
    for i, (x, z, rr) in enumerate(((0, 0, 0.7), (0.75, -0.1, 0.55), (-0.7, -0.12, 0.5), (0.3, 0.35, 0.5), (-0.3, 0.3, 0.45))):
        ball(f"{name}_{i}", (x, 0, z), rr, C("#FFFFFF", rough=1.0, coat=0.0, kind="felt"), r, seg=20)
    return r


def lamp_post(name, loc, parent):
    r = root(name, loc, parent)
    cyl(name + "_p", (0, 0, 0.45), 0.025, 0.9, C("#2E2E36", rough=0.4), r, bevel=0.0, verts=10)
    ball(name + "_b", (0, 0, 0.95), 0.07, C("#FFE2A0", emit=6.0), r, seg=16)
    return r


def shoe(name, loc, parent, color, stripe, s=1.0, rz=0.0):
    """Generic toy sneaker (no brand marks): sole + upper + toe + one side band in the brother's colour."""
    r = root(name, loc, parent, s, rz)
    cube(name + "_sole", (0, 0, 0.04), (0.28, 0.62, 0.08), C("#3B2A1E", rough=0.6), r, bevel=0.035)
    cube(name + "_up", (0, 0.08, 0.17), (0.26, 0.42, 0.2), C(color, kind="felt"), r, bevel=0.07)
    ball(name + "_toe", (0, -0.17, 0.11), 0.13, C(color, kind="felt"), r, scale=(1.0, 1.25, 0.75), seg=16)
    cube(name + "_band", (0, 0.06, 0.17), (0.268, 0.1, 0.16), C(stripe, rough=0.4), r, bevel=0.03)
    for i in range(3):
        cube(f"{name}_lace{i}", (0, -0.06 + i * 0.07, 0.27), (0.16, 0.02, 0.02), C("#FFFFFF"), r, bevel=0.005)
    return r


def plane_toy(name, loc, parent=None, col="#5B6849"):
    r = root(name, loc, parent)
    cyl(name + "_f", (0, 0, 0), 0.12, 1.1, C(col, rough=0.5), r, rot=(0, math.pi / 2, 0))
    cube(name + "_w", (0.05, 0, 0), (0.28, 1.5, 0.04), C(col, rough=0.5), r, bevel=0.02)
    cube(name + "_tail", (-0.48, 0, 0.12), (0.14, 0.4, 0.03), C(col, rough=0.5), r, bevel=0.01)
    prop = cyl(name + "_prop", (0.58, 0, 0), 0.22, 0.02, C("#2B2B2B"), r, rot=(0, math.pi / 2, 0), verts=3)
    key(prop, "rotation_euler", 0, 0.0, "LINEAR", index=0)
    key(prop, "rotation_euler", END, 400.0, "LINEAR", index=0)
    return r


def goal(name, loc, parent, rz=0.0):
    r = root(name, loc, parent, 1.0, rz)
    white = C("#FFFFFF")
    for sx in (-1, 1):
        cyl(f"{name}_p{sx}", (0.35 * sx, 0, 0.18), 0.025, 0.36, white, r, bevel=0.0, verts=10)
    cyl(name + "_bar", (0, 0, 0.36), 0.025, 0.72, white, r, bevel=0.0, verts=10, rot=(0, math.pi / 2, 0))
    return r


def pitch(name, loc, parent, size=(1.8, 1.2)):
    r = root(name, loc, parent, 1.0)
    cube(name + "_g", (0, 0, 0.02), (size[0], size[1], 0.04), C("#4FAE57", rough=0.8, kind="stripes", rgb2="#45A04D", scale=4),
         r, bevel=0.01)
    w = C("#FFFFFF", rough=0.6)
    cube(name + "_mid", (0, 0, 0.045), (0.03, size[1] - 0.1, 0.01), w, r, bevel=0.0)
    cyl(name + "_c", (0, 0, 0.045), 0.18, 0.01, w, r, bevel=0.0)
    cyl(name + "_c2", (0, 0, 0.048), 0.15, 0.012, C("#4FAE57", rough=0.8), r, bevel=0.0)
    goal(name + "_g1", (-size[0] / 2 + 0.08, 0, 0.04), r, rz=math.pi / 2)
    goal(name + "_g2", (size[0] / 2 - 0.08, 0, 0.04), r, rz=math.pi / 2)
    return r


def factory(name, loc, parent, color):
    r = root(name, loc, parent, 1.0)
    cube(name + "_b", (0, 0, 0.5), (1.5, 0.9, 1.0), C(color, rough=0.5, kind="felt"), r)
    for i in range(3):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(-0.5 + i * 0.5, 0, 1.12))
        t = bpy.context.object
        t.name, t.scale = f"{name}_saw{i}", (0.5, 0.88, 0.32)
        bpy.ops.object.transform_apply(scale=True)
        t.data.vertices[0].co.z = t.data.vertices[2].co.z = 0.0  # saw-tooth roof
        finish(t, C(CREAM, rough=0.5), r, smooth=False)
    cyl(name + "_ch", (0.6, 0.25, 1.5), 0.11, 1.0, C("#8B4B3B", rough=0.6), r, verts=16)
    for i in range(4):
        cube(f"{name}_win{i}", (-0.55 + i * 0.37, -0.455, 0.55), (0.22, 0.02, 0.3), C("#FFE7A3", emit=1.5), r, bevel=0.01)
    smoke = [ball(f"{name}_smk{i}", (0.6, 0.25, 2.1 + i * 0.3), 0.14 + i * 0.05, C("#E9E6E0", rough=1.0, coat=0.0, kind="felt"), r)
             for i in range(3)]
    return r, smoke


def puffs(name, center, t, n=6, col="#B9B4AA", spread=0.6, size=0.25, parent=None, rng=None):
    """Dust/smoke ring: balls pop out from a point and fade (shrink)."""
    rng = rng or random.Random(hash(name) & 0xFFFF)
    out = []
    for i in range(n):
        a = 2 * math.pi * i / n + rng.uniform(-0.3, 0.3)
        b = ball(f"{name}{i}", center, size * rng.uniform(0.7, 1.3), C(col, rough=1.0, coat=0.0, kind="felt"), parent, seg=12)
        key(b, "scale", 0, (0, 0, 0), "CONSTANT")
        key(b, "scale", t - 0.01, (0, 0, 0), "BACK")
        key(b, "scale", t + 0.2, (1, 1, 1))
        key(b, "scale", t + 0.9, (0, 0, 0))
        key(b, "location", t, center)
        key(b, "location", t + 0.9, add(center, (spread * math.cos(a), spread * math.sin(a), 0.25)), "LINEAR")
        out.append(b)
    return out


CONF = {}


def confetti(name, center, t, n, cols, parent=None, spread=2.0, h=2.5, rng=None):
    if "me" not in CONF:
        tpl = cube("conf_tpl", (0, 0, 0), (0.07, 0.05, 0.008), mat("confetti", (1, 1, 1), rough=0.4, kind="objcolor", bump=0),
                   bevel=0.0)
        CONF["me"] = template(tpl)
    rng = rng or random.Random(7)
    for i in range(n):
        c = inst(f"{name}{i}", CONF["me"], center, parent, rng.choice(cols))
        key(c, "scale", 0, (0, 0, 0), "CONSTANT")
        key(c, "scale", t, (1, 1, 1), "CONSTANT")
        top = add(center, (rng.uniform(-spread, spread) * 0.5, rng.uniform(-spread, spread) * 0.5, h * rng.uniform(0.7, 1.1)))
        end = add(center, (rng.uniform(-spread, spread), rng.uniform(-spread, spread), rng.uniform(-0.2, 0.3)))
        key(c, "location", t, center, "LINEAR")
        key(c, "location", t + 0.35, top, "BEZIER")
        key(c, "location", t + 2.6, end, "LINEAR")
        key(c, "rotation_euler", t, (0, 0, 0), "LINEAR")
        key(c, "rotation_euler", t + 2.6, (rng.uniform(-12, 12), rng.uniform(-12, 12), rng.uniform(-6, 6)), "LINEAR")


# ---------------------------------------------------------------- sets
def build_town(o):
    """The toy town on a round board split by a river (north = Adi/blue, south = Rudi/red), on a big wooden table."""
    stage = empty("STAGE")
    north, south = empty("NORTH", parent=stage), empty("SOUTH", parent=stage)
    cube("table", (0, 0, -0.75), (90, 90, 0.5), C("#8A5A34", kind="wood", rough=0.45, scale=0.15), None, bevel=0.0)
    for half, sgn in ((north, 1), (south, -1)):
        bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=8.5, depth=0.5, location=(0, 0, -0.25))
        b = bpy.context.object
        b.name = f"board{sgn}"
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.bisect(plane_co=(0, 0.55 * sgn, 0), plane_no=(0, -sgn, 0), clear_outer=True, use_fill=True)
        bpy.ops.object.mode_set(mode="OBJECT")
        finish(b, C("#B07A47", rough=0.5, coat=0.3, kind="wood"), half, bevel=0.06, smooth=False)
        bpy.ops.mesh.primitive_cylinder_add(vertices=128, radius=8.2, depth=0.08, location=(0, 0, 0.04))
        g = bpy.context.object
        g.name = f"grass{sgn}"
        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.bisect(plane_co=(0, 0.75 * sgn, 0), plane_no=(0, -sgn, 0), clear_outer=True, use_fill=True)
        bpy.ops.object.mode_set(mode="OBJECT")
        finish(g, C("#7BC86C" if sgn > 0 else "#86C766", rough=0.9, coat=0.0, kind="felt"), half, smooth=False)
        cube(f"street{sgn}", (0, 1.65 * sgn, 0.085), (15.6, 0.55, 0.02), C("#CDBB9A", rough=0.9, kind="checker", rgb2="#B9A685",
                                                                              scale=6), half, bevel=0.0)
    o["river"] = cube("river", (0, 0, -0.08), (17.2, 1.4, 0.2), C("#3FA7D6", rough=0.08, coat=0.8, kind="water"), stage, bevel=0.0)
    br = root("bridge", (0, 0, 0), stage)
    halves = []
    for sgn in (1, -1):
        h = root(f"bridge{sgn}", (0, 0.0, 0.12), br)
        cube(f"bridge_deck{sgn}", (0, 0.47 * sgn, 0), (1.3, 0.95, 0.12), C("#C98F55", kind="wood"), h, bevel=0.03)
        for sx in (-1, 1):
            cube(f"bridge_rail{sgn}{sx}", (0.6 * sx, 0.47 * sgn, 0.2), (0.08, 0.95, 0.08), C("#8E5A30", kind="wood"), h, bevel=0.02)
        halves.append(h)
    o["bridge"], o["bridge_halves"] = br, halves

    reserved = [(-3.4, 3.2), (-1.0, 3.0), (-5.3, 2.3), (-6.8, 2.1), (5.6, 2.2), (4.6, 2.2), (6.6, 2.2), (2.6, 5.4), (-1.0, 2.0),
                (-6.0, 1.3), (-4.6, 1.3)]
    rng = random.Random(4)
    for half, sgn, walls, roof in ((north, 1, ("#F7E7C6", "#EAD9F2", "#D9ECF7", "#FFF1D6"), "#2F6FD6"),
                                   (south, -1, ("#F7E7C6", "#F7D9D2", "#F2EBD0", "#FFE9D6"), "#D6402F")):
        k = 0
        for y in (3.9, 5.1, 6.3, 7.3):
            for x in [-7.5 + 1.25 * i for i in range(13)]:
                x2, y2 = x + rng.uniform(-0.2, 0.2), y + rng.uniform(-0.15, 0.15)
                if x2 * x2 + y2 * y2 > 7.5 ** 2 or any((x2 - a) ** 2 + (y2 - b) ** 2 < 1.6 ** 2 for a, b in reserved):
                    continue
                c = rng.random()
                if c < 0.62:
                    house(f"h{sgn}_{k}", (x2, y2 * sgn, 0.08), half, rng.choice(walls), roof, s=0.62 + rng.random() * 0.25,
                          rz=(0 if sgn > 0 else math.pi) + rng.uniform(-0.15, 0.15))
                elif c < 0.85:
                    tree(f"t{sgn}_{k}", (x2, y2 * sgn, 0.08), half, s=0.65 + rng.random() * 0.5,
                         col=rng.choice(("#3E8E4A", "#4E9A4A", "#2F7A40")))
                else:
                    bush(f"b{sgn}_{k}", (x2, y2 * sgn, 0.08), half, s=0.8 + rng.random() * 0.4)
                k += 1
        for i, x in enumerate((-2.6, 2.0, 7.0)):
            lamp_post(f"lamp{sgn}_{i}", (x, 1.25 * sgn, 0.08), half)
    # church tower (north) and town hall (south): landmarks for wide shots
    ch = root("church", (2.6, 5.4, 0.08), north)
    cube("church_b", (0, 0, 0.6), (1.0, 1.4, 1.2), C("#FFF6E6", rough=0.7), ch)
    cube("church_t", (0, -0.4, 1.4), (0.6, 0.6, 1.6), C("#FFF6E6", rough=0.7), ch)
    cone("church_s", (0, -0.4, 2.65), 0.48, 0.9, C(BLUE, kind="felt"), ch, verts=4)
    cyl("church_clock", (0, -0.71, 1.75), 0.18, 0.03, C("#FFFFFF", emit=0.6), ch, rot=(math.pi / 2, 0, 0))
    hl = root("hall", (2.6, -5.4, 0.08), south, rz=math.pi)
    cube("hall_b", (0, 0, 0.55), (1.6, 1.0, 1.1), C("#F7D9D2", rough=0.7), hl)
    cone("hall_r", (0, 0, 1.4), 1.1, 0.6, C(RED, kind="felt"), hl, verts=4, rot=(0, 0, math.pi / 4))
    for i in range(3):
        cyl(f"hall_col{i}", (-0.45 + i * 0.45, -0.55, 0.45), 0.07, 0.9, C("#FFFFFF"), hl, verts=12)
    for i, (x, y, z, s) in enumerate(((-4, 3, 7.5, 1.3), (3, 6, 8.2, 1.6), (6, -3, 7.0, 1.2), (-5, -5, 8.6, 1.5), (0.5, -1, 9.4, 1.1),
                                      (-1.5, 9, 6.8, 1.4))):
        cloud(f"cloud{i}", (x, y, z), None, s)

    o.update(stage=stage, north=north, south=south)
    o["home"] = house("home", (-3.4, 3.2, 0.08), north, "#FFF1D6", "#8A5A3C", s=1.15)
    o["fA"], o["smkA"] = factory("fA", (-1.0, 3.0, 0.08), north, BLUE)
    o["fR"], o["smkR"] = factory("fR", (-1.0, -3.0, 0.08), south, RED)
    o["fR"].rotation_euler[2] = math.pi
    o["tAdi"] = peg("tAdi", BLUE, (-1.0, 2.0, 0.08), north, hair="#3B2A1A", cap="#3A4A5C", s=0.8)
    o["tRudi"] = peg("tRudi", RED, (-1.0, -2.0, 0.08), south, hair="#1E1410", s=0.8, rz=math.pi)

    o["shops"] = []
    for half, sgn, col in ((north, 1, BLUE), (south, -1, RED)):
        for i, (x, y) in enumerate(((-5.3, 2.4), (-6.8, 2.4))):
            hb = house(f"shop{sgn}_{i}", (x, y * sgn, 0.08), half, "#FFF6E6", col, s=1.0, rz=0 if sgn > 0 else math.pi)
            aw = root(f"awn{sgn}_{i}", (0, -0.5, 0.42), hb)
            for k in range(4):
                cube(f"awn{sgn}_{i}_{k}", (-0.34 + k * 0.23, 0, 0), (0.23, 0.3, 0.05),
                     C(col if k % 2 == 0 else "#FFFFFF", rough=0.6, kind="felt"), aw, bevel=0.01, rot=(0.45, 0, 0))
            sign = root(f"sign{sgn}_{i}", (0, -0.5, 0.95), hb)
            if i == 0:
                cyl(f"mug{sgn}", (0, 0, 0), 0.12, 0.24, C(GOLD, rough=0.2, coat=0.6), sign, bevel=0.02)
                cyl(f"foam{sgn}", (0, 0, 0.14), 0.13, 0.07, C("#FFFFFF", rough=0.7, kind="felt"), sign, bevel=0.03)
            else:
                bpy.ops.mesh.primitive_torus_add(major_radius=0.13, minor_radius=0.045, location=(0, 0, 0), rotation=(math.pi / 2, 0, 0))
                pz = bpy.context.object
                pz.name = f"pretzel{sgn}"
                finish(pz, C("#B5651D", rough=0.4), sign)
            o["shops"].append((aw, sign))
        # bunting along the street, popped on "dos"
        bt = root(f"bunting{sgn}", (0, 0, 0), half)
        cyl(f"bunt_rope{sgn}", (-3.0, 2.0 * sgn, 1.0), 0.008, 9.0, C("#EEEEEE"), bt, bevel=0.0, verts=6, rot=(0, math.pi / 2, 0))
        for k in range(22):
            x = -7.4 + k * 0.42
            cone(f"bunt{sgn}_{k}", (x, 2.0 * sgn, 0.92), 0.11, 0.16, C(col if k % 2 == 0 else "#FFFFFF", kind="felt"), bt, verts=3,
                 rot=(math.pi, 0, 0))
        o[f"bunting{sgn}"] = bt
    o["pitchA"] = pitch("pitchA", (5.6, 2.3, 0.08), north)
    o["pitchR"] = pitch("pitchR", (5.6, -2.3, 0.08), south)
    o["kick"] = [ball(f"kickball{s}", (5.6, 2.3 * s, 0.2), 0.08, C("#FFFFFF"), h) for s, h in ((1, north), (-1, south))]
    o["players"] = [peg(f"pl{s}{i}", c, (5.6 + 0.5 * (1 if i else -1), 2.3 * s, 0.12), h, s=0.45, arms=False,
                        rz=(math.pi / 2 if i else -math.pi / 2)) for s, h, c in ((1, north, BLUE), (-1, south, RED)) for i in (0, 1)]
    o["folk"] = []
    rng = random.Random(7)
    for half, sgn, body in ((north, 1, BLUE), (south, -1, RED)):
        for i, x in enumerate((-7.0, -6.45, -5.9, -5.35, -4.8, -4.25)):
            f = peg(f"folk{sgn}_{i}", body, (x, (1.05 + rng.uniform(-0.08, 0.08)) * sgn, 0.08), half,
                    rz=(0 if sgn > 0 else math.pi) + rng.uniform(-0.35, 0.35), s=0.62,
                    hair=rng.choice(("#5A3A22", "#2B1D12", "#C9A15B", "#8A8A8A")), arms=False, feet=body)
            o["folk"].append(f)

    # war props: planes, fire glows, searchlights, smoke
    o["planes"] = [plane_toy(f"plane{i}", (-16, 4.0 + i * 1.0, 4.4 + i * 0.35)) for i in range(3)]
    o["fires"] = [light("POINT", f"fire{i}", (x, y, 0.6), 0, "#FF7A2E", size=0.4, dist=12)
                  for i, (x, y) in enumerate(((-4.5, 5.2), (1.2, 6.2), (5.4, 4.6), (-2.2, 4.4), (4.0, -4.6)))]
    o["search"] = [light("SPOT", f"search{i}", (x, y, 0.4), 0, "#DDE6FF", size=0.05, spot=7, dist=40)
                   for i, (x, y) in enumerate(((-7.5, 7.5), (7.5, 7.0), (0.0, -8.0)))]
    o["town_fog"] = fog("town_fog", (0, 0, 3.0), (26, 26, 7), 0.0, "#FFFFFF")
    o["peace"] = pitch("peace", (0, 0, 0.3), stage, size=(3.4, 2.3))
    o["ballx"] = ball("soccer", (0, 0, 1.4), 0.12, C("#FFFFFF", rough=0.4), stage)
    o["mixed"] = [peg(f"mix{i}", (BLUE, RED)[i % 2], ((-1.2 + i * 0.48), (0.5 if i % 2 else -0.5), 0.34), stage,
                      rz=(math.pi / 2 if i % 2 else -math.pi / 2), s=0.55, arms=False, feet=(BLUE, RED)[i % 2]) for i in range(6)]


def build_hook(o):
    P = empty("HOOK", P_HOOK)
    cube("hook_floor", (0, 0, -0.05), (30, 30, 0.1), C("#15151F", rough=0.45, coat=0.3), P, bevel=0.0)
    cyl("hook_ped", (0, 0, 0.12), 2.0, 0.24, C("#9C6B3E", kind="wood", coat=0.5), P, bevel=0.05, verts=96)
    o["crack"] = cube("hook_crack", (0, 0, 0.245), (0.07, 4.0, 0.02), C("#1A0F08", rough=0.9), P, bevel=0.0)
    o["hAdi"] = peg("hAdi", BLUE, (-0.42, 0, 0.24), P, hair="#3B2A1A", cap="#3A4A5C", rz=math.pi / 2)
    o["hRudi"] = peg("hRudi", RED, (0.42, 0, 0.24), P, hair="#1E1410", rz=-math.pi / 2)
    o["hShoeA"] = shoe("hShoeA", (-1.35, 1.5, 9.0), P, CREAM, BLUE, s=3.6, rz=0.35)
    o["hShoeR"] = shoe("hShoeR", (1.35, 1.5, 9.0), P, CREAM, RED, s=3.6, rz=-0.35)
    for nm, x, col in (("hkA", -3.5, "#4F8DFF"), ("hkR", 3.5, "#FF4A3A")):
        s = light("SPOT", nm, (x, -2.0, 4.5), 2600, col, P, size=0.1, spot=38, dist=20)
        aim(s, (x * 0.12, 0.3, 0.5))
    rim = light("SPOT", "hk_rim", (0, 4.0, 3.5), 900, "#FFF2DA", P, size=0.1, spot=60, dist=20)
    fl = light("AREA", "hk_fill", (0, -5.0, 2.0), 150, "#B8C4FF", P, size=4.0, dist=20)
    aim(fl, (0, 0, 0.6))
    aim(rim, (0, 0, 0.6))
    fog("hook_fog", (0, 0, 3), (12, 12, 6), 0.02, "#FFFFFF", P)


def build_laundry(o):
    P = empty("LAUNDRY", P_LAUN)
    o["laun"] = P
    cube("ln_floor", (0, 1.0, -0.05), (10.4, 7.0, 0.1), C("#E9DCC2", kind="checker", rgb2="#C4553E", scale=1.2, rough=0.5), P, bevel=0.0)
    wall = C("#F3E3C3", kind="stripes", rgb2="#E8CFA3", scale=3.0, rough=0.8)
    cube("ln_back", (0, 4.5, 2.5), (10.4, 0.2, 5.0), wall, P, bevel=0.0)
    cube("ln_right", (5.1, 1.0, 2.5), (0.2, 7.0, 5.0), wall, P, bevel=0.0)
    for nm, loc, size in (("lw_a", (-5.1, -1.25, 2.5), (0.2, 2.5, 5.0)), ("lw_b", (-5.1, 3.4, 2.5), (0.2, 2.2, 5.0)),
                          ("lw_c", (-5.1, 1.15, 0.7), (0.2, 2.3, 1.4)), ("lw_d", (-5.1, 1.15, 4.0), (0.2, 2.3, 2.0))):
        cube(nm, loc, size, wall, P, bevel=0.0)  # left wall with a window hole (y 0..2.3, z 1.4..3.0)
    cube("ln_sill", (-5.0, 1.15, 1.42), (0.4, 2.4, 0.08), C("#FFFFFF"), P, bevel=0.01)
    cube("ln_mull", (-5.1, 1.15, 2.2), (0.12, 0.06, 1.6), C("#FFFFFF"), P, bevel=0.0)
    cube("ln_ceil", (0, 1.0, 5.05), (10.4, 7.0, 0.1), C("#E8D6B4", rough=0.9), P, bevel=0.0)
    for i in range(5):
        cube(f"ln_beam{i}", (-4 + i * 2, 1.0, 4.9), (0.2, 7.0, 0.2), C("#7A5232", kind="wood"), P, bevel=0.01)
    for i, (x, col) in enumerate(((-0.8, "#81B29A"), (3.6, "#E07A5F"))):
        cube(f"frame{i}", (x, 4.38, 3.2), (1.0, 0.05, 0.8), C("#6B4226", kind="wood"), P, bevel=0.02)
        cube(f"pic{i}", (x, 4.35, 3.2), (0.8, 0.03, 0.6), C(col, kind="felt"), P, bevel=0.0)
    cube("ln_skirt", (0, 4.38, 0.15), (10.4, 0.06, 0.3), C("#7A5232", kind="wood"), P, bevel=0.0)
    sun = light("SPOT", "ln_sun", (-9.0, 1.4, 4.2), 9000, "#FFD9A0", P, size=0.2, spot=28, dist=25)
    aim(sun, (-1.0, 1.6, 0.0))
    fill = light("AREA", "ln_fill", (1.0, -4.0, 3.5), 600, "#FFE6C7", P, size=4.0, dist=20)
    aim(fill, (0.5, 2.0, 1.0))
    lampc = root("ln_lamp", (1.6, 2.0, 5.0), P)
    cyl("ln_cord", (0, 0, -0.9), 0.01, 1.8, C("#222222"), lampc, bevel=0.0, verts=6)
    cone("ln_shade", (0, 0, -1.85), 0.35, 0.25, C("#2F5A3A", rough=0.4), lampc, verts=24)
    ball("ln_bulb", (0, 0, -1.98), 0.08, C("#FFE7A3", emit=10.0), lampc, seg=16)
    light("POINT", "ln_bulbL", (0, 0, -2.05), 160, "#FFC77A", lampc, size=0.1, dist=12)
    fog("ln_fog", (0, 1.0, 2.6), (10, 7, 5.2), 0.045, "#FFF4E0", P)
    # mom's laundry corner: big tub with bubbles, mom
    tub = root("tub", (-2.6, 2.2, 0), P)
    cyl("tub_b", (0, 0, 0.42), 0.95, 0.84, C("#A9B4BE", rough=0.25, coat=0.7), tub, bevel=0.05, verts=48)
    cyl("tub_w", (0, 0, 0.78), 0.88, 0.04, C("#CFEAF7", rough=0.05, coat=0.9), tub, bevel=0.0, verts=48)
    cube("tub_board", (0.55, 0.0, 0.95), (0.6, 0.06, 0.8), C("#C98F55", kind="wood"), tub, bevel=0.02, rot=(0, 0.35, 0))
    o["bubbles"] = []
    rng = random.Random(3)
    for i in range(14):
        b = ball(f"bub{i}", (rng.uniform(-0.7, 0.7), rng.uniform(-0.6, 0.6), 0.85), rng.uniform(0.05, 0.13),
                 C("#E8F6FF", rough=0.0, coat=1.0), tub, seg=16)
        o["bubbles"].append(b)
    o["mom"] = peg("mom", "#7A4E8A", (-3.75, 1.45, 0), P, hair="#8A8A8A", bun=True, rz=-0.5, s=1.05)
    # workbench with tools; brothers work behind it
    cube("bench_top", (1.6, 1.7, 0.5), (2.9, 0.8, 0.08), C("#B07A47", kind="wood", coat=0.2), P, bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cube(f"bench_leg{sx}{sy}", (1.6 + 1.3 * sx, 1.7 + 0.3 * sy, 0.23), (0.1, 0.1, 0.46), C("#7A5232", kind="wood"), P, bevel=0.01)
    cube("bench_front", (1.6, 1.32, 0.33), (2.9, 0.05, 0.26), C("#8E5A30", kind="wood"), P, bevel=0.01)
    for i, x in enumerate((0.55, 2.7)):
        ball(f"last{i}", (x, 1.55, 0.62), 0.12, C("#C9A27A", kind="wood"), P, scale=(1.0, 2.0, 0.8))
    for i, (x, col) in enumerate(((1.6, "#E6C79C"), (2.1, "#B5651D"), (0.15, "#2F6FD6"))):
        cube(f"leather{i}", (x, 1.5, 0.55), (0.35, 0.28, 0.015), C(col, kind="felt"), P, bevel=0.0, rot=(0, 0, 0.3 * i))
    for i, (x, col) in enumerate(((2.95, BLUE), (3.1, RED), (0.3, "#FFFFFF"))):
        cyl(f"spool{i}", (x, 1.95, 0.63), 0.06, 0.18, C(col, kind="felt"), P, verts=16)
    o["lAdi"] = peg("lAdi", BLUE, (1.0, 2.3, 0.0), P, hair="#3B2A1A", cap="#3A4A5C", s=1.25)
    o["lRudi"] = peg("lRudi", RED, (2.25, 2.3, 0.0), P, hair="#1E1410", s=1.25)
    hm = root("hammer", (0, 0, -0.38), part(o["lAdi"], "armR"))
    hm.rotation_euler = (math.pi / 2, 0, 0)
    cyl("hm_h", (0, 0, 0.12), 0.02, 0.3, C("#8E5A30", kind="wood"), hm, verts=8)
    cube("hm_head", (0, 0, 0.28), (0.16, 0.06, 0.06), C("#555B66", rough=0.3, coat=0.6), hm, bevel=0.01)
    # shelf
    cube("shelf", (3.4, 4.25, 2.2), (2.6, 0.4, 0.08), C("#8E5A30", kind="wood"), P, bevel=0.01)
    for i, col in enumerate(("#E07A5F", "#81B29A", "#F2CC8F", "#3D405B")):
        cyl(f"jar{i}", (2.4 + i * 0.6, 4.25, 2.45), 0.15, 0.42, C(col, rough=0.15, coat=0.8), P, verts=20)
    # clothesline with shoes popping like laundry
    for sx in (-1, 1):
        cyl(f"ln_pole{sx}", (4.7 * sx, 3.6, 1.5), 0.04, 3.0, C("#6B4226", kind="wood"), P, bevel=0.0, verts=10)
    cyl("ln_rope", (0, 3.6, 2.85), 0.01, 9.4, C("#EEEEEE"), P, bevel=0.0, verts=6, rot=(0, math.pi / 2, 0))
    for i, (x, col) in enumerate(((-4.0, "#FFFFFF"), (-3.4, "#F2B33D"), (-2.8, "#9FD3FF"))):
        cube(f"cloth{i}", (x, 3.6, 2.45), (0.5, 0.02, 0.75), C(col, rough=0.9, kind="felt"), P, bevel=0.01)
    o["hang"] = []
    for i in range(6):
        x = -1.6 + i * 1.05
        h = root(f"hang{i}", (x, 3.6, 2.82), P)
        cube(f"pin{i}", (0, 0, 0.0), (0.04, 0.05, 0.16), C("#C98F55", kind="wood"), h, bevel=0.005)
        shoe(f"hs{i}", (0, 0.0, -0.36), h, CREAM, (BLUE, RED)[i % 2], s=1.1).rotation_euler = (0, 0.25, math.pi / 2)
        o["hang"].append(h)
    o["flyshoe"] = shoe("flyshoe", (1.55, 3.6, 2.55), P, CREAM, BLUE, s=0.8)


def build_stadium(o):
    P = empty("STADIUM", P_STAD)
    bpy.ops.mesh.primitive_cylinder_add(vertices=96, radius=7.4, depth=0.1, location=(0, 0, -0.05))
    g = bpy.context.object
    g.name, g.scale = "st_field", (1.5, 0.95, 1)
    finish(g, C("#5DBB63", rough=0.9, kind="stripes", rgb2="#52AD58", scale=1.5), P, smooth=False)
    bpy.ops.mesh.primitive_torus_add(major_radius=5.5, minor_radius=0.65, location=(0, 0, 0.0), major_segments=96)
    tr = bpy.context.object
    tr.name, tr.scale = "st_track", (1.5, 0.9, 0.06)
    finish(tr, C("#C8553D", rough=0.9, coat=0.0, kind="felt"), P)
    for k in range(4):  # lane lines
        bpy.ops.mesh.primitive_torus_add(major_radius=5.0 + k * 0.33, minor_radius=0.012, location=(0, 0, 0.04), major_segments=96)
        ln = bpy.context.object
        ln.name, ln.scale = f"st_lane{k}", (1.5, 0.9, 1)
        finish(ln, C("#FFFFFF"), P)
    concrete = C("#D9D2C3", rough=0.8)
    tiers = []
    for k in range(5):
        bpy.ops.mesh.primitive_torus_add(major_radius=7.6 + k * 0.75, minor_radius=0.42, location=(0, 0, 0.25 + k * 0.45),
                                         major_segments=96, minor_segments=4)
        t = bpy.context.object
        t.name, t.scale = f"st_tier{k}", (1.5, 1.0, 1.0)
        finish(t, concrete, P, smooth=False)
        tiers.append(7.6 + k * 0.75)
    # crowd: shared meshes, colour per object
    cm = mat("crowd", (1, 1, 1), rough=0.6, kind="objcolor")
    body = template(cyl("crowd_b", (0, 0, 0.22), 0.16, 0.44, cm, None, bevel=0.0, verts=12))
    head = template(ball("crowd_h", (0, 0, 0.58), 0.15, C(SKIN, rough=0.6), None, seg=12))
    rng = random.Random(11)
    o["crowd"] = []
    for k, R in enumerate(tiers):
        n = 46 + k * 6
        for i in range(n):
            a = 2 * math.pi * (i + rng.random() * 0.4) / n
            if rng.random() < 0.12:
                continue
            x, y, z = 1.5 * R * math.cos(a), 1.0 * R * math.sin(a), 0.45 + k * 0.45
            c = empty(f"cr{k}_{i}", (x, y, z), P)
            c.rotation_euler[2] = a + math.pi / 2
            inst(f"crb{k}_{i}", body, (0, 0, 0), c, rng.choice(("#E9E1D0", "#C9B79C", "#6B7A8F", "#8C4A3C", "#3E5C76", "#F2E8D5")))
            inst(f"crh{k}_{i}", head, (0, 0, 0), c)
            o["crowd"].append(c)
    for i in range(18):  # pennant flags along the rim
        a = 2 * math.pi * i / 18
        x, y = 1.5 * 11.0 * math.cos(a), 1.0 * 11.0 * math.sin(a)
        cyl(f"fp{i}", (x, y, 2.9), 0.03, 2.2, C("#EEEEEE"), P, bevel=0.0, verts=8)
        f = cone(f"ff{i}", (x + 0.3, y, 3.75), 0.25, 0.6, C(("#2F6FD6", "#F2B33D", "#2E9E5B", "#D6402F", "#FFFFFF")[i % 5], kind="felt"),
                 P, verts=3, rot=(0, math.pi / 2, 0))
        key(f, "rotation_euler", 0, (0.0, math.pi / 2, 0), "LINEAR")
        for k in range(1, int(END / 0.5)):
            key(f, "rotation_euler", k * 0.5, (0.18 * (1 if k % 2 else -1), math.pi / 2, 0), "BEZIER")
    # podium
    for nm, x, h, col in (("pod1", 2.6, 0.9, GOLD), ("pod2", 1.75, 0.6, "#C9CED6"), ("pod3", 3.45, 0.42, "#C98F55")):
        cube(nm, (x, -2.6, h / 2), (0.85, 0.85, h), C("#FFFFFF", rough=0.5), P, bevel=0.03)
        cube(nm + "_band", (x, -3.03, h - 0.12), (0.86, 0.02, 0.12), C(col, rough=0.3, coat=0.7), P, bevel=0.0)
    o["owens"] = peg("owens", "#FFFFFF", (-7.2, -4.95, 0.04), P, skin="#6B4430", hair="#1E1410", s=0.9, feet="#2B2B2B",
                     rz=math.pi / 2)
    o["medals"] = []
    for i in range(4):
        m = root(f"medal{i}", (-0.3 + i * 0.2, 0, 0), P)
        cyl(f"medal{i}_d", (0, 0, 0), 0.1, 0.03, C(GOLD, rough=0.15, coat=0.9, emit=0.3), m, rot=(math.pi / 2, 0, 0))
        cyl(f"medal{i}_rib", (0, 0.0, 0.15), 0.015, 0.3, C(BLUE if i % 2 else RED, kind="felt"), m, bevel=0.0, verts=6)
        o["medals"].append(m)
    o["stshoe"] = shoe("stshoe", (-6.2, -4.6, 9.0), P, CREAM, "#2B2B2B", s=0.9)
    for i, (x, y, z, s) in enumerate(((-6, 10, 9, 2.0), (5, 12, 10, 2.4), (12, 4, 8, 1.8), (-12, 2, 9, 2.0))):
        cloud(f"stcloud{i}", (x, y, z), P, s)


def build_bunker(o):
    P = empty("BUNKER", P_BUNK)
    concrete = C("#8C9096", rough=0.85, coat=0.0, bump=2.5)
    cube("bk_floor", (0, 0.5, -0.05), (6.4, 4.4, 0.1), C("#5E5A55", rough=0.95, bump=2.0), P, bevel=0.0)
    cube("bk_ceil", (0, 0.5, 3.05), (6.4, 4.4, 0.1), concrete, P, bevel=0.0)
    # back wall with a slot window (x −1..1, z 2.1..2.6)
    for nm, loc, size in (("bk_bl", (-2.1, 2.7, 1.5), (2.2, 0.3, 3.0)), ("bk_br", (2.1, 2.7, 1.5), (2.2, 0.3, 3.0)),
                          ("bk_bb", (0, 2.7, 1.05), (2.0, 0.3, 2.1)), ("bk_bt", (0, 2.7, 2.8), (2.0, 0.3, 0.4))):
        cube(nm, loc, size, concrete, P, bevel=0.0)
    for nm, loc, size in (("bk_ra", (3.2, 0.5, 1.5), (0.3, 4.4, 3.0)), ("bk_la", (-3.2, 1.75, 1.5), (0.3, 1.9, 3.0)),
                          ("bk_lb", (-3.2, -1.25, 1.5), (0.3, 1.5, 3.0)), ("bk_lt", (-3.2, 0.25, 2.5), (0.3, 1.1, 1.0))):
        cube(nm, loc, size, concrete, P, bevel=0.0)  # left wall with a door (y −0.3..0.8, z<2)
    red = light("AREA", "bk_door", (-4.2, 0.25, 1.0), 400, "#FF5A2A", P, size=1.2, dist=8)
    aim(red, (-2.5, 0.25, 0.8))
    o["bk_door"] = red.data
    cube("bk_seat", (0, 1.95, 0.42), (3.4, 0.55, 0.1), C("#7A5232", kind="wood"), P, bevel=0.02)
    for sx in (-1, 0, 1):
        cube(f"bk_sl{sx}", (1.5 * sx, 1.95, 0.2), (0.1, 0.5, 0.4), C("#5A3A22", kind="wood"), P, bevel=0.01)
    rng = random.Random(5)
    for i in range(14):  # sandbags
        x = (-2.7 if i < 7 else 2.6) + rng.uniform(-0.25, 0.25)
        y = -0.9 + (i % 7) % 3 * 0.55
        z = 0.15 + (i % 7) // 3 * 0.26
        ball(f"sand{i}", (x, y, z), 0.32, C("#BFA67A", rough=0.95, kind="felt"), P, scale=(1.0, 0.7, 0.42), seg=16)
    for i in range(3):
        cube(f"crate{i}", (2.3 - i * 0.15, 1.9 - i * 0.05, 0.25 + i * 0.5), (0.6, 0.6, 0.5), C("#A47148", kind="wood"), P, bevel=0.02,
             rot=(0, 0, 0.2 * i))
    for i, col in enumerate(("#7D8C6E", "#B04A3A", "#C9B26B")):
        cyl(f"can{i}", (-2.3 + i * 0.25, 2.25, 0.62 + 0.0), 0.08, 0.2, C(col, rough=0.3, coat=0.6), P, verts=16)
    sw = root("bk_swing", (0, 1.0, 3.0), P)
    cyl("bk_cord", (0, 0, -0.45), 0.01, 0.9, C("#222222"), sw, bevel=0.0, verts=6)
    ball("bk_bulb", (0, 0, -0.95), 0.08, C("#FFE7A3", emit=12.0), sw, seg=16)
    o["bulbL"] = light("POINT", "bk_bulbL", (0, 0, -1.02), 220, "#FFC27A", sw, size=0.06, dist=10).data
    o["swing"] = sw
    o["bk_fog"] = fog("bk_fog", (0, 0.5, 1.5), (6.2, 4.2, 3.0), 0.04, "#E8DCC8", P)
    kf = light("AREA", "bk_fill", (0.0, -2.5, 1.6), 60, "#6F86C8", P, size=3.0, dist=8)
    aim(kf, (0, 1.9, 0.9))
    o["bAdi"] = peg("bAdi", BLUE, (-3.6, 0.25, 0.0), P, hair="#3B2A1A", cap="#3A4A5C")
    o["bRudi"] = peg("bRudi", RED, (-3.6, 0.25, 0.0), P, hair="#1E1410")
    o["dust"] = []
    for i in range(26):
        d = ball(f"dust{i}", (rng.uniform(-2.5, 2.5), rng.uniform(-0.5, 2.3), 2.95), rng.uniform(0.015, 0.04),
                 C("#CFC6B4", rough=1.0), P, seg=8)
        o["dust"].append(d)
    # outside the slot: the planes pass, lit by a searchlight
    o["bk_planes"] = [plane_toy(f"bkplane{i}", (-7, 5.0 + i * 0.8, 2.35 + i * 0.12), P, col="#3C4436") for i in range(3)]
    s = light("SPOT", "bk_out", (0, 3.4, 0.4), 0, "#DDE6FF", P, size=0.05, spot=30, dist=12)
    aim(s, (0, 5.4, 3.2))
    o["bk_out"] = s.data
    cube("bk_sky", (0, 9.0, 2.5), (20, 0.2, 10), C("#7A2A22", emit=1.5, rough=1.0), P, bevel=0.0)


def build_cemetery(o):
    P = empty("CEMETERY", P_CEME)
    cube("cm_ground", (0, 0, -0.05), (24, 30, 0.1), C("#3E5A3A", rough=0.95, kind="felt"), P, bevel=0.0)
    cube("cm_path", (0, 0, 0.01), (1.3, 24, 0.03), C("#9A927E", rough=0.95, kind="checker", rgb2="#8A836F", scale=5), P, bevel=0.0)
    stone = C("#9AA0A6", rough=0.85, bump=2.0)
    gtpl = template(cube("grave_tpl", (0, 0, 0.3), (0.42, 0.13, 0.6), stone, None, bevel=0.05))
    xtpl = template(cube("cross_tpl", (0, 0, 0.35), (0.08, 0.08, 0.7), stone, None, bevel=0.01))
    xbar = template(cube("crossb_tpl", (0, 0, 0.5), (0.36, 0.08, 0.08), stone, None, bevel=0.01))
    rng = random.Random(9)
    for i in range(46):
        y = rng.uniform(-9.0, 9.0)
        x = rng.choice((-1, 1)) * rng.uniform(1.4, 6.5)
        rz = rng.uniform(-0.25, 0.25)
        tilt = (rng.uniform(-0.12, 0.12), rng.uniform(-0.08, 0.08), rz)
        if rng.random() < 0.65:
            inst(f"grave{i}", gtpl, (x, y, 0), P, rot=tilt, scale=(1, 1, rng.uniform(0.8, 1.3)))
        else:
            inst(f"crossv{i}", xtpl, (x, y, 0), P, rot=tilt)
            inst(f"crossh{i}", xbar, (x, y, 0), P, rot=tilt)
    for i in range(60):  # iron fence at the far back and sides
        y = -11 + i * 0.4
        for sx in (-1, 1):
            cyl(f"fence{sx}_{i}", (7.2 * sx, y, 0.45), 0.02, 0.9, C("#222228", rough=0.4), P, bevel=0.0, verts=6)
    for i, (x, y) in enumerate(((-4.5, 6), (5.0, -3.5), (-5.8, -7.5))):  # dead trees
        t = root(f"dtree{i}", (x, y, 0), P)
        cyl(f"dt{i}", (0, 0, 0.9), 0.08, 1.8, C("#3A2A1E", kind="wood"), t, verts=10)
        for k in range(3):
            cyl(f"db{i}{k}", (0.25 * (1 if k % 2 else -1), 0, 1.2 + k * 0.25), 0.03, 0.7, C("#3A2A1E", kind="wood"), t, verts=8,
                rot=(0, 0.9 * (1 if k % 2 else -1), 0))
    o["tombA"] = root("tombA", (0.0, 10.5, 0), P)
    o["tombR"] = root("tombR", (0.0, -10.5, 0), P, rz=math.pi)
    for t, col, nm in ((o["tombA"], BLUE, "A"), (o["tombR"], RED, "R")):
        cube(f"tb{nm}_s", (0, 0, 0.42), (0.6, 0.18, 0.84), C("#B6BCC2", rough=0.7, bump=2.0), t, bevel=0.06)
        ball(f"tb{nm}_top", (0, 0, 0.84), 0.3, C("#B6BCC2", rough=0.7, bump=2.0), t, scale=(1, 0.3, 0.6))
        cube(f"tb{nm}_band", (0, -0.1, 0.45), (0.44, 0.02, 0.1), C(col, rough=0.4), t, bevel=0.01)
        cube(f"tb{nm}_dirt", (0, -0.55, 0.04), (0.6, 0.8, 0.08), C("#4A3424", rough=0.95, kind="felt"), t, bevel=0.03)
        for sx in (-1, 1):
            cyl(f"tb{nm}_cand{sx}", (0.42 * sx, -0.25, 0.1), 0.04, 0.2, C("#FFF6E0"), t, verts=10)
            ball(f"tb{nm}_flame{sx}", (0.42 * sx, -0.25, 0.24), 0.03, C("#FFC46B", emit=20.0), t, seg=8)
        light("POINT", f"tb{nm}_glow", (0, -0.6, 0.7), 120, col, t, size=0.2, dist=8)
    o["moon"] = ball("moon", (8, 40, 16), 2.2, C("#F4F1EA", emit=3.0), P)
    o["cm_fog"] = fog("cm_fog", (0, 0, 0.5), (22, 28, 1.0), 0.05, "#C7D2F0", P)
    light("SPOT", "cm_moonspot", (6, 22, 9), 6000, "#AFC4FF", P, size=1.0, spot=50, dist=60).rotation_euler = (math.radians(-60), 0, 0)


# ---------------------------------------------------------------- world, light, camera
def build_world(sc, o):
    world = bpy.data.worlds.new("W")
    sc.world = world
    N, Lk = nodes_of(world)
    bg = N["Background"]
    tc, sep, rp = N.new("ShaderNodeTexCoord"), N.new("ShaderNodeSeparateXYZ"), N.new("ShaderNodeValToRGB")
    Lk.new(tc.outputs["Generated"], sep.inputs[0])
    mr = N.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = -0.05, 0.55
    Lk.new(sep.outputs["Z"], mr.inputs["Value"])
    Lk.new(mr.outputs["Result"], rp.inputs["Fac"])
    Lk.new(rp.outputs["Color"], bg.inputs["Color"])
    o["sky"], o["bg"] = rp.color_ramp.elements, bg
    sd = bpy.data.lights.new("sun", "SUN")
    sd.angle = math.radians(6)
    sun = bpy.data.objects.new("sun", sd)
    sc.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(50), math.radians(10), math.radians(-35))
    o["sun"] = sd
    rig, tgt = empty("RIG"), empty("TGT")
    cam_d = bpy.data.cameras.new("cam")
    cam_d.dof.use_dof, cam_d.dof.focus_object = True, tgt
    cam = bpy.data.objects.new("cam", cam_d)
    sc.collection.objects.link(cam)
    cam.parent = rig
    tt = cam.constraints.new("TRACK_TO")
    tt.target, tt.track_axis, tt.up_axis = tgt, "TRACK_NEGATIVE_Z", "UP_Y"
    sc.camera = cam
    o["rig"], o["tgt"], o["cam"] = rig, tgt, cam


#           horizon     zenith      bg   sun  sun colour  town fog
MOODS = {
    "hook":    ("#262A4A", "#0A0A14", 0.6, 0.0, "#FFFFFF", 0.0),
    "day":     ("#FFE2B8", "#7FB8EE", 1.0, 3.6, "#FFF1DA", 0.0),
    "laundry": ("#FFE2B8", "#7FB8EE", 0.35, 0.0, "#FFF1DA", 0.0),
    "stadium": ("#FFF0CF", "#5FA8F0", 1.1, 4.4, "#FFF6E6", 0.0),
    "war":     ("#C8442A", "#141A3A", 0.9, 0.8, "#8DA2FF", 0.012),
    "bunker":  ("#1A1210", "#0A0808", 0.1, 0.0, "#FFFFFF", 0.0),
    "night":   ("#4A62A8", "#0A1030", 1.2, 1.6, "#9FB4FF", 0.0),
    "sunrise": ("#FFB46E", "#6FA8DC", 1.0, 3.2, "#FFC88A", 0.0),
}
CUTS = set()


def set_mood(o, t, name, fade=0.0):
    hz, zn, st, se, scol, fd = MOODS[name]
    items = [(o["sky"][0], "color", (*hexrgb(hz), 1)), (o["sky"][1], "color", (*hexrgb(zn), 1)),
             (o["bg"].inputs[1], "default_value", st), (o["sun"], "energy", se), (o["sun"], "color", hexrgb(scol)),
             (o["town_fog"], "default_value", fd)]
    for owner, path, v in items:
        if fade:
            PREF.keyframe_new_interpolation_type = "BEZIER"
            owner.keyframe_insert(path, frame=F(t))
            setattr(owner, path, v)
            PREF.keyframe_new_interpolation_type = "CONSTANT"
            owner.keyframe_insert(path, frame=F(t + fade))
        else:
            PREF.keyframe_new_interpolation_type = "CONSTANT"
            if F(t) > 0:
                owner.keyframe_insert(path, frame=F(t) - 1)
            setattr(owner, path, v)
            owner.keyframe_insert(path, frame=F(t))


SHOTS = []


def shot(t, cam, tgt, lens, cam1=None, tgt1=None, lens1=None, fstop=2.0, cut=True, ease="BEZIER"):
    """A camera shot from t until the next shot: moves cam/tgt/lens from the first to the second value.
    cut=True jumps at t (hard cut); cut=False continues smoothly from where the last shot ended."""
    SHOTS.append(dict(t=t, cam=cam, tgt=tgt, lens=lens, cam1=cam1 or cam, tgt1=tgt1 or tgt, lens1=lens1 or lens, f=fstop,
                      cut=cut, ease=ease))


def apply_shots(o):
    cam, tgt = o["cam"], o["tgt"]
    SHOTS.sort(key=lambda s: s["t"])
    for i, s in enumerate(SHOTS):
        t1 = (SHOTS[i + 1]["t"] - 1 / FPS) if i + 1 < len(SHOTS) else END
        f0 = F(s["t"])
        if s["cut"] and i:
            CUTS.add(f0)
        if s["cut"] or i == 0:
            for ob, path, v in ((cam, "location", s["cam"]), (tgt, "location", s["tgt"]), (cam.data, "lens", s["lens"]),
                                (cam.data.dof, "aperture_fstop", s["f"])):
                key(ob, path, 0, v, s["ease"], frame=f0)
        else:  # continue: re-key the previous end at t with an ease
            for ob, path in ((cam, "location"), (tgt, "location"), (cam.data, "lens"), (cam.data.dof, "aperture_fstop")):
                v = getattr(ob, path)
                key(ob, path, 0, tuple(v) if hasattr(v, "__len__") else v, s["ease"], frame=f0)
            key(cam.data.dof, "aperture_fstop", 0, s["f"], s["ease"], frame=f0)
        fe = max(F(t1), f0 + 1)
        if s["ease"] == "LINEAR":
            for f in range(f0 + 2, fe, 2):
                u = (f - f0) / (fe - f0)
                for ob, a, b in ((cam, s["cam"], s["cam1"]), (tgt, s["tgt"], s["tgt1"])):
                    key(ob, "location", 0, tuple(x + (y - x) * u for x, y in zip(a, b)), "LINEAR", frame=f)
        for ob, path, v in ((cam, "location", s["cam1"]), (tgt, "location", s["tgt1"]), (cam.data, "lens", s["lens1"]),
                            (cam.data.dof, "aperture_fstop", s["f"])):
            key(ob, path, 0, v, "CONSTANT", frame=fe)


def shake(o, t, dur=0.4, amp=0.08):
    """Short burst (≤0.5 s) on a mood change — never constant."""
    rig = o["rig"]
    key(rig, "location", t, (0, 0, 0), "LINEAR")
    n = 6
    for i in range(1, n):
        a = amp * (1 - i / n)
        key(rig, "location", t + dur * i / n, (random.uniform(-a, a), random.uniform(-a, a), random.uniform(-a, a)), "LINEAR")
    key(rig, "location", t + dur, (0, 0, 0), "BEZIER")


def talk(rt, spk):
    m = part(rt, "mouth")
    env = MOUTH[spk]
    PREF.keyframe_new_interpolation_type = "LINEAR"
    prev = 0.0
    for f, v in enumerate(env):
        if v > 0.02 or prev > 0.02:
            m.scale = (1.3, 0.5, 0.25 + 1.6 * v)
            m.keyframe_insert("scale", frame=f)
        prev = v


def swing(ob, t, amp, dur=3.0, period=0.9):
    """Damped pendulum on X."""
    n = int(dur / (period / 2))
    for i in range(n + 1):
        a = amp * (1 - i / n) * (1 if i % 2 else -1) if i else 0.0
        key(ob, "rotation_euler", t + i * period / 2, (math.radians(a), 0, 0), "BEZIER")


def lightkey(d, path, t, v, interp="LINEAR"):
    PREF.keyframe_new_interpolation_type = interp
    setattr(d, path, v)
    d.keyframe_insert(path, frame=F(t))


# ---------------------------------------------------------------- animation (all anchored to words)
def animate(o):
    PREF.keyframe_new_interpolation_type = "BEZIER"
    set_mood(o, 0, "hook")

    # ---- l0 HOOK: dark stage, two spotlights; giant sneakers crash down; they turn their backs, the pedestal cracks
    adi, rudi = o["hAdi"], o["hRudi"]
    shot(0, (60.0, -3.4, 0.75), (60.0, 0.0, 0.72), 38, (60.0, -2.9, 0.7), (60.0, 0.0, 0.72), 40, fstop=1.4)
    shot(W("l0", "adidas", d=-0.15), (61.4, -5.6, 1.6), (60.0, 0.8, 1.0), 32, (60.6, -5.2, 1.3), (60.0, 0.8, 0.95), 34, fstop=2.2)
    shot(W("l0", "hermanos", d=-0.1), (60.0, -2.2, 0.55), (60.0, 0.0, 0.78), 45, (60.0, -2.0, 0.6), (60.0, 0.0, 0.8), 48, fstop=1.2)
    shot(W("l0", "odiaban", d=-0.05), (60.0, -6.0, 3.6), (60.0, 0.0, 0.4), 30, (60.0, -6.6, 4.2), (60.0, 0.0, 0.3), 30, fstop=3.0)
    for sh, w in ((o["hShoeA"], "adidas"), (o["hShoeR"], "puma")):
        t = W("l0", w)
        key(sh, "location", 0, tuple(sh.location), "CONSTANT")
        key(sh, "location", t - 0.05, tuple(sh.location), "LINEAR")
        key(sh, "location", t + 0.25, (sh.location[0], 1.5, 0.0), "LINEAR")
        key(sh, "location", t + 0.38, (sh.location[0], 1.5, 0.35), "BEZIER")
        key(sh, "location", t + 0.52, (sh.location[0], 1.5, 0.0), "BEZIER")
        puffs(f"hdust{w}", (sh.location[0], 1.3, 0.1), t + 0.25, n=8, spread=1.2, size=0.3, col="#8A847A", parent=bpy.data.objects["HOOK"])
    for ob in (adi, rudi):
        for arm, sx in ((part(ob, "armR"), 1), (part(ob, "armL"), -1)):
            key(arm, "rotation_euler", W("l0", "adidas", d=0.15), (0, 0, 0))
            key(arm, "rotation_euler", W("l0", "adidas", d=0.4), (0, math.radians(25 * sx), 0), "BACK")  # flinch
        key(ob, "location", W("l0", "hermanos", d=-0.1), tuple(ob.location))
        key(ob, "location", W("l0", "hermanos", d=0.08), (ob.location[0], 0, 0.5))
        key(ob, "location", W("l0", "hermanos", d=0.3), (ob.location[0], 0, 0.24), "BACK")
        brows(ob, W("l0", "hermanos"), 1)
    turn(adi, W("l0", "odiaban"), W("l0", "odiaban", d=0.35), -math.pi / 2)
    turn(rudi, W("l0", "odiaban", d=0.1), W("l0", "odiaban", d=0.45), math.pi / 2)
    for ob in (adi, rudi):
        key(ob, "location", W("l0", "odiaban", d=0.0), tuple(ob.location))
        key(ob, "location", W("l0", "odiaban", d=0.45), (ob.location[0] * 1.9, 0, 0.24), "BACK")
    key(o["crack"], "scale", 0, (1, 0, 1), "CONSTANT")
    key(o["crack"], "scale", W("l0", "odiaban", d=0.0), (1, 0, 1), "LINEAR")
    key(o["crack"], "scale", W("l0", "odiaban", d=0.3), (1, 1, 1), "BACK")
    shake(o, W("l0", "odiaban"), 0.4, 0.06)
    blink(adi, 0.4, 4.8, 2.3)
    blink(rudi, 0.9, 4.8, 2.6)

    # ---- l1 TOWN establishing (crane down through cotton clouds) → LAUNDRY interior
    set_mood(o, L("l1"), "day")
    shot(L("l1"), (-1.0, -6.0, 13.0), (-3.0, 2.5, 0.5), 30, (-3.4, -1.9, 2.6), (-3.4, 3.0, 0.8), 34, fstop=4.0)
    set_mood(o, W("l1", "adi", d=-0.1), "laundry")
    la, lr, P = o["lAdi"], o["lRudi"], P_LAUN
    shot(W("l1", "adi", d=-0.1), add(P, (0.4, -0.9, 1.3)), add(P, (1.0, 2.3, 0.95)), 45, add(P, (0.65, -0.6, 1.25)),
         add(P, (1.05, 2.3, 0.95)), 50, fstop=1.6)
    shot(W("l1", "rudi", d=-0.1), add(P, (0.9, -0.7, 1.4)), add(P, (1.1, 2.3, 1.0)), 52, add(P, (2.1, -0.7, 1.25)),
         add(P, (2.2, 2.3, 0.95)), 50, fstop=1.6, cut=False)
    shot(W("l1", "zapatos", d=-0.15), add(P, (1.6, -1.2, 2.2)), add(P, (1.0, 3.6, 2.5)), 30, add(P, (1.3, -1.6, 2.3)),
         add(P, (0.9, 3.6, 2.4)), 30, fstop=2.4)
    shot(W("l1", "lavanderia", d=-0.1), add(P, (0.6, -2.8, 2.6)), add(P, (-1.0, 2.0, 1.1)), 24, add(P, (0.2, -6.2, 3.4)),
         add(P, (-0.6, 2.0, 1.2)), 24, fstop=3.5, cut=False)
    arm = part(la, "armR")
    t, k = W("l1", "adi", d=0.05), 0
    while t < L("l2") - 0.1:  # hammering loop
        key(arm, "rotation_euler", t, (math.radians(-110), 0, 0), "BEZIER")
        key(arm, "rotation_euler", t + 0.16, (math.radians(-55), 0, 0), "LINEAR")
        t += 0.32
    for a2 in (part(lr, "armR"), part(lr, "armL")):  # Rudi stitching
        t = W("l1", "rudi", d=0.0)
        sgn = 1 if a2.name.endswith("R") else -1
        while t < L("l2") - 0.1:
            key(a2, "rotation_euler", t, (math.radians(-70), 0, math.radians(15 * sgn)), "BEZIER")
            key(a2, "rotation_euler", t + 0.25, (math.radians(-50), 0, math.radians(-10 * sgn)), "BEZIER")
            t += 0.5
    key(lr, "rotation_euler", W("l1", "rudi"), (0, 0, 0))
    key(lr, "rotation_euler", W("l1", "rudi", d=0.3), (0, 0, math.radians(-20)), "BACK")
    blink(la, 7.0, 11.8, 2.2)
    blink(lr, 7.5, 11.8, 2.7)
    blink(o["mom"], 6.0, 11.8, 2.5)
    for i, h in enumerate(o["hang"]):
        pop(h, W("l1", "zapatos", d=-0.05 + i * 0.12), 0.3)
        key(h, "rotation_euler", W("l1", "zapatos", d=0.2 + i * 0.12), (0, 0, 0))
        key(h, "rotation_euler", W("l1", "zapatos", d=0.45 + i * 0.12), (math.radians(14), 0, 0), "BEZIER")
        key(h, "rotation_euler", W("l1", "zapatos", d=0.8 + i * 0.12), (math.radians(-6), 0, 0), "BEZIER")
        key(h, "rotation_euler", W("l1", "zapatos", d=1.1 + i * 0.12), (0, 0, 0), "BEZIER")
    marm = part(o["mom"], "armR")
    t = 5.0
    while t < L("l2"):  # mom scrubbing
        key(marm, "rotation_euler", t, (math.radians(-60), 0, 0))
        key(marm, "rotation_euler", t + 0.3, (math.radians(-35), 0, 0))
        t += 0.6
    for i, b in enumerate(o["bubbles"]):  # bubbles rise and pop, staggered
        x, y, _ = b.location
        t = 5.0 + i * 0.37
        while t < L("l2"):
            key(b, "location", t, (x, y, 0.85), "LINEAR")
            key(b, "scale", t, (0.2, 0.2, 0.2), "LINEAR")
            key(b, "scale", t + 0.3, (1, 1, 1), "LINEAR")
            key(b, "location", t + 2.2, (x + 0.2, y, 2.6), "LINEAR")
            key(b, "scale", t + 2.19, (1, 1, 1), "LINEAR")
            key(b, "scale", t + 2.25, (0, 0, 0), "CONSTANT")
            t += 2.6
    fs = o["flyshoe"]  # one shoe flies at the lens → match cut into the stadium sky
    hidden(fs)
    key(fs, "scale", L("l2", -0.5), (0.8, 0.8, 0.8), "CONSTANT")
    key(fs, "location", L("l2", -0.5), (1.55, 3.6, 2.55), "BEZIER")
    key(fs, "location", L("l2", -0.03), (0.3, -5.6, 3.3), "LINEAR")
    key(fs, "rotation_euler", L("l2", -0.5), (0, 0, 0), "LINEAR")
    key(fs, "rotation_euler", L("l2", -0.03), (2.5, 0.6, 3.0), "LINEAR")

    # ---- l2 STADIUM 1936: the shoe falls from the sky; Owens runs (low tracking shot); podium, 4 golds; close on the shoes
    set_mood(o, L("l2"), "stadium")
    S = P_STAD
    ow = o["owens"]
    sh = o["stshoe"]
    shot(L("l2"), add(S, (-4.5, -13.0, 11.5)), add(S, (-6.2, -4.6, 7.0)), 32, add(S, (-4.0, -11.5, 2.4)), add(S, (-6.6, -4.9, 0.6)),
         30, fstop=3.5)
    key(sh, "location", 0, tuple(sh.location), "LINEAR", frame=F(L("l2")))
    key(sh, "location", W("l2", "seis", d=0.2), (-6.6, -4.6, 0.04), "BACK")
    key(sh, "rotation_euler", L("l2"), (2.5, 0.6, 3.0), "LINEAR")
    key(sh, "rotation_euler", W("l2", "seis", d=0.2), (0, 0, 0.6), "BEZIER")
    unpop(sh, W("l2", "jesse", d=-0.25), 0.2, s=0.9)
    puffs("stdust", (-6.6, -4.6, 0.1), W("l2", "seis", d=0.2), n=6, spread=0.7, size=0.18, col="#E0C9A6",
          parent=bpy.data.objects["STADIUM"])
    t0, t1 = W("l2", "jesse", d=-0.1), W("l2", "cuatro", d=-0.35)
    shot(t0, add(S, (-6.9, -6.5, 0.45)), add(S, (-7.0, -4.95, 0.55)), 30, add(S, (2.7, -6.5, 0.5)), add(S, (2.6, -4.95, 0.55)), 30,
         fstop=1.8, ease="LINEAR")
    key(ow, "location", t0, (-7.2, -4.95, 0.04), "LINEAR")
    key(ow, "location", t1, (2.5, -4.95, 0.04), "LINEAR")
    n = int((t1 - t0) / 0.14)
    for k in range(n + 1):  # run cycle: bob + lean + arm swing
        key(ow, "location", 0, (-7.2 + (2.5 + 7.2) * k / n, -4.95, 0.04 + (0.09 if k % 2 else 0.0)), "LINEAR", frame=F(t0 + k * 0.14))
    key(ow, "rotation_euler", t0, (math.radians(12), 0, math.pi / 2))
    for arm, sgn in ((part(ow, "armR"), 1), (part(ow, "armL"), -1)):
        for k in range(n + 1):
            key(arm, "rotation_euler", t0 + k * 0.14, (math.radians(50 * sgn * (1 if k % 2 else -1)), 0, 0), "LINEAR")
        key(arm, "rotation_euler", W("l2", "cuatro", d=0.2), (math.radians(-170), 0, math.radians(15 * sgn)), "BACK")  # victory
    key(ow, "rotation_euler", t1, (math.radians(12), 0, math.pi / 2))
    hop(ow, t1, W("l2", "cuatro", d=-0.02), (2.6, -2.6, 0.9), h=0.9)
    key(ow, "rotation_euler", W("l2", "cuatro", d=-0.02), (0, 0, 0), "BACK")
    blink(ow, 12.5, 18.0, 2.4)
    shot(W("l2", "cuatro", d=-0.3), add(S, (2.6, -6.4, 1.9)), add(S, (2.6, -2.6, 1.55)), 40, add(S, (2.6, -5.4, 1.75)),
         add(S, (2.6, -2.6, 1.55)), 46, fstop=2.0)
    for i, m in enumerate(o["medals"]):
        t = W("l2", "cuatro", d=i * 0.17)
        end = (2.6 - 0.2 + i * 0.13, -2.8, 0.9 + 0.36 * 0.9)
        key(m, "location", 0, (end[0], end[1], end[2] + 4.0), "CONSTANT")
        key(m, "location", t - 0.25, (end[0], end[1], end[2] + 4.0), "LINEAR")
        key(m, "location", t, end, "BACK")
        key(m, "rotation_euler", t, (0, 0, 0))
        key(m, "rotation_euler", L("l3"), (0, 0, 4 * math.pi), "LINEAR")
    confetti("goldconf", add((2.6, -2.6, 1.5), (0, 0, 0)), W("l2", "oros"), 50, (GOLD, "#FFE08A", "#FFFFFF"),
             bpy.data.objects["STADIUM"], spread=2.4, h=1.6)
    shot(W("l2", "tenis", d=-0.3), add(S, (3.45, -3.55, 1.02)), add(S, (2.6, -2.72, 0.93)), 55, add(S, (3.3, -3.4, 0.99)),
         add(S, (2.6, -2.72, 0.93)), 62, fstop=1.6)
    for nm in ("owens_ft-1_band", "owens_ft1_band"):  # the shoes light up on "tenis"
        ob = bpy.data.objects[nm]
        ob.data.materials[0] = mat("glowband", hexrgb(GOLD), emit=0.0)
    gb = MATS["glowband"].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
    for t, v in ((W("l2", "tenis", d=-0.1), 0.0), (W("l2", "tenis", d=0.15), 6.0), (L("l3"), 2.0)):
        gb.default_value = v
        gb.keyframe_insert("default_value", frame=F(t))
    gbc = MATS["glowband"].node_tree.nodes["Principled BSDF"].inputs["Emission Color"]
    gbc.default_value = (*hexrgb(GOLD), 1)
    rng = random.Random(2)
    for c in o["crowd"]:  # the crowd jumps
        z = c.location[2]
        t = L("l2", rng.uniform(0, 0.4))
        while t < L("l3"):
            key(c, "location", t, (c.location[0], c.location[1], z), "BEZIER")
            key(c, "location", t + 0.18, (c.location[0], c.location[1], z + rng.uniform(0.12, 0.3)), "BEZIER")
            t += rng.uniform(0.38, 0.6)

    # ---- l3 WAR: the town at night, red sky, searchlights, planes overhead, bomb flashes → the BUNKER
    set_mood(o, L("l3"), "war")
    shot(L("l3"), (0.6, 1.25, 0.35), (-0.5, 6.0, 3.6), 22, (0.3, 1.2, 0.3), (0.2, 6.0, 3.9), 22, fstop=5.0)
    shot(W("l3", "bombardeo", d=-0.05), (7.5, -9.0, 6.5), (0.0, 3.5, 0.6), 30, (6.6, -8.0, 5.6), (0.0, 3.5, 0.6), 32, fstop=6.0)
    for i, p in enumerate(o["planes"]):
        t0 = L("l3", 0.1 + i * 0.25)
        key(p, "location", t0, (-16, 4.0 + i * 1.0, 4.4 + i * 0.35), "LINEAR")
        key(p, "location", t0 + 3.6, (16, 4.4 + i * 1.0, 4.6 + i * 0.35), "LINEAR")
    for i, s in enumerate(o["search"]):
        lightkey(s.data, "energy", L("l3", -0.05), 0, "CONSTANT")
        lightkey(s.data, "energy", L("l3"), 2500, "CONSTANT")
        lightkey(s.data, "energy", W("l3", "terminan", d=0.0), 0, "CONSTANT")
        for k in range(5):
            a = (0.35 if (k + i) % 2 else -0.35)
            key(s, "rotation_euler", L("l3", k * 0.7), (math.pi + a, 0.25 * (1 if i % 2 else -1), 0.3 * i))
    for i, fl in enumerate(o["fires"]):
        t = W("l3", "bombardeo", d=i * 0.2)
        lightkey(fl.data, "energy", t - 0.01, 0, "CONSTANT")
        lightkey(fl.data, "energy", t + 0.06, 12000, "LINEAR")
        lightkey(fl.data, "energy", t + 0.4, 1500, "BEZIER")
        k = 0
        while t + 0.5 + k * 0.12 < W("l3", "terminan"):
            lightkey(fl.data, "energy", t + 0.5 + k * 0.12, 900 + 600 * ((k * 7 + i) % 3), "LINEAR")
            k += 1
        lightkey(fl.data, "energy", W("l3", "terminan", d=0.01), 0, "CONSTANT")
        puffs(f"bomb{i}", (fl.location[0], fl.location[1], 0.4), t, n=7, col="#8A7A70", spread=1.3, size=0.55)
        fb = ball(f"fireball{i}", (fl.location[0], fl.location[1], 0.4), 0.7, C("#FF8A2E", emit=14.0, kind="felt"), seg=16)
        hidden(fb)
        key(fb, "scale", t - 0.01, (0, 0, 0), "BACK")
        key(fb, "scale", t + 0.15, (1.8, 1.8, 1.8))
        key(fb, "scale", t + 1.0, (0, 0, 0))
    shake(o, W("l3", "bombardeo"), 0.45, 0.12)

    set_mood(o, W("l3", "terminan", d=-0.1), "bunker")
    B = P_BUNK
    ba, bb = o["bAdi"], o["bRudi"]
    shot(W("l3", "terminan", d=-0.1), add(B, (0.4, -3.4, 1.7)), add(B, (-0.4, 1.0, 0.9)), 24, add(B, (0.2, -2.6, 1.5)),
         add(B, (-0.2, 1.2, 0.95)), 26, fstop=2.8)
    shot(W("l3", "refugio", d=-0.05), add(B, (0.0, -1.8, 1.25)), add(B, (0.0, 1.9, 0.95)), 38, add(B, (0.0, -1.4, 1.2)),
         add(B, (0.0, 1.9, 0.95)), 40, fstop=1.8, cut=False)
    shot(W("l3", "adi", d=-0.2), add(B, (-0.3, -0.5, 1.0)), add(B, (-0.6, 1.9, 1.0)), 55, add(B, (-0.4, -0.2, 0.95)),
         add(B, (-0.6, 1.9, 1.02)), 58, fstop=1.4, cut=False)
    for ob, w, x in ((ba, "terminan", -0.6), (bb, "mismo", 0.6)):
        t = W("l3", w)
        key(ob, "location", 0, (-3.6, 0.25, 0.0), "CONSTANT")
        key(ob, "location", t - 0.05, (-3.6, 0.25, 0.0), "LINEAR")
        key(ob, "location", t + 0.25, (-1.6, 0.6, 0.9))
        key(ob, "location", t + 0.55, (x, 1.9, 0.47), "BACK")
        key(ob, "rotation_euler", t, (0, 0, -math.pi / 2))
        key(ob, "rotation_euler", t + 0.55, (0, 0, 0), "BACK")
    swing(o["swing"], W("l3", "terminan"), 18, 3.5)
    blink(ba, 22.5, 33.8, 2.5)
    blink(bb, 22.8, 33.8, 2.9)
    for b in (ba, bb):
        brows(b, W("l3", "refugio"), -1)  # worried

    # ---- l4 Adi points at the ceiling: "¡Ahí vienen otra vez esos desgraciados!"
    shot(L("l4", -0.1), add(B, (-0.85, 0.2, 0.62)), add(B, (-0.6, 1.9, 1.15)), 50, add(B, (-0.8, 0.45, 0.6)),
         add(B, (-0.6, 1.9, 1.15)), 55, fstop=1.2)
    arm = part(ba, "armR")
    key(arm, "rotation_euler", W("l4", "ahi", d=-0.05), (0, 0, 0))
    key(arm, "rotation_euler", W("l4", "ahi", d=0.25), (math.radians(-165), 0, math.radians(-15)), "BACK")
    hd = part(ba, "head")
    key(hd, "rotation_euler", W("l4", "ahi"), (0, 0, 0))
    key(hd, "rotation_euler", W("l4", "ahi", d=0.3), (math.radians(-22), 0, 0), "BACK")
    brows(ba, W("l4", "desgraciados", d=-0.2), 1)
    talk(ba, "adi")
    t = W("l4", "desgraciados")
    for d in (o["bulbL"],):
        for dt, v in ((-0.01, 220), (0.03, 20), (0.08, 300), (0.13, 40), (0.2, 220)):
            lightkey(d, "energy", t + dt, v)
    lightkey(o["bk_door"], "energy", t - 0.01, 400)
    lightkey(o["bk_door"], "energy", t + 0.05, 3500)
    lightkey(o["bk_door"], "energy", t + 0.5, 400)
    swing(o["swing"], t, 14, 2.5)
    for i, d in enumerate(o["dust"]):  # dust rains from the ceiling
        x, y, _ = d.location
        key(d, "location", 0, (x, y, 2.95), "CONSTANT")
        key(d, "location", t + i * 0.02, (x, y, 2.95), "LINEAR")
        key(d, "location", t + 1.6 + i * 0.03, (x + 0.1, y, 0.02), "LINEAR")
    shake(o, t, 0.35, 0.03)

    # ---- l5 Rudi snaps round, red-faced: "¿¡Desgraciados!? ¿¡Me lo dices a mí!?" (crash zoom)
    shot(L("l5", -0.05), add(B, (-0.2, 0.55, 0.95)), add(B, (0.6, 1.9, 1.05)), 40, add(B, (-0.2, 0.55, 0.95)),
         add(B, (0.6, 1.9, 1.05)), 70, fstop=1.2, ease="BACK")
    turn(bb, L("l5", -0.1), L("l5", 0.2), math.radians(-55))
    brows(bb, L("l5", -0.05), 1, 0.1)
    hd = part(bb, "head")
    face = hd.children[0].data.materials[0]
    angry = face.copy()
    angry.name = "rudi_angry"
    hd.children[0].data.materials[0] = angry
    bsdf = angry.node_tree.nodes["Principled BSDF"].inputs["Base Color"]
    for t, c in ((L("l5", -0.05), SKIN), (L("l5", 0.35), "#E8584A"), (L("l6", 1.0), "#E8584A"), (L("l6", 2.0), SKIN)):
        bsdf.default_value = (*hexrgb(c), 1)
        bsdf.keyframe_insert("default_value", frame=F(t))
    key(bb, "location", L("l5", 0.0), (0.6, 1.9, 0.47))
    key(bb, "location", L("l5", 0.15), (0.6, 1.9, 0.75))
    key(bb, "location", L("l5", 0.35), (0.6, 1.9, 0.47), "BACK")
    for a, sgn in ((part(bb, "armR"), 1), (part(bb, "armL"), -1)):
        key(a, "rotation_euler", W("l5", "me", d=-0.1), (0, 0, 0))
        key(a, "rotation_euler", W("l5", "me", d=0.15), (math.radians(-80), 0, math.radians(30 * sgn)), "BACK")
    shake(o, L("l5", 0.0), 0.35, 0.04)
    talk(bb, "rudi")

    # ---- l6 "Adi juraba que hablaba de los aviones": tilt up to the slot, planes pass; Rudi crosses his arms, turns away
    shot(L("l6"), add(B, (0.0, -1.3, 1.1)), add(B, (0.0, 1.9, 0.95)), 36, add(B, (0.0, -1.1, 1.1)), add(B, (0.0, 1.9, 0.95)), 38,
         fstop=2.0)
    shot(W("l6", "aviones", d=-0.35), add(B, (0.0, -0.2, 0.8)), add(B, (0.0, 2.7, 2.35)), 30, add(B, (0.0, 0.3, 0.9)),
         add(B, (0.0, 2.7, 2.4)), 34, fstop=2.5, cut=False)
    lightkey(o["bk_out"], "energy", W("l6", "aviones", d=-0.4), 0, "CONSTANT")
    lightkey(o["bk_out"], "energy", W("l6", "aviones", d=-0.3), 1500, "CONSTANT")
    lightkey(o["bk_out"], "energy", W("l6", "rudi", d=0.0), 0, "CONSTANT")
    for i, p in enumerate(o["bk_planes"]):
        t0 = W("l6", "aviones", d=-0.35 + i * 0.22)
        key(p, "location", t0, (-7, 5.0 + i * 0.8, 2.35 + i * 0.12), "LINEAR")
        key(p, "location", t0 + 1.6, (7, 5.0 + i * 0.8, 2.45 + i * 0.12), "LINEAR")
    key(arm, "rotation_euler", W("l6", "aviones", d=-0.2), (math.radians(-60), 0, 0))
    key(arm, "rotation_euler", W("l6", "aviones", d=0.1), (math.radians(-165), 0, math.radians(-15)), "BACK")
    shot(W("l6", "rudi", d=-0.15), add(B, (1.8, 0.9, 1.0)), add(B, (0.6, 1.9, 1.0)), 42, add(B, (1.7, 1.0, 0.98)),
         add(B, (0.6, 1.9, 1.0)), 48, fstop=1.3)
    turn(bb, W("l6", "nunca"), W("l6", "nunca", d=0.35), math.radians(110))
    for a, sgn in ((part(bb, "armR"), 1), (part(bb, "armL"), -1)):  # crosses his arms
        key(a, "rotation_euler", W("l6", "nunca"), tuple(a.rotation_euler))
        key(a, "rotation_euler", W("l6", "nunca", d=0.3), (math.radians(-80), 0, math.radians(-55 * sgn)), "BACK")
    hd = part(bb, "head")
    for k in range(5):
        key(hd, "rotation_euler", W("l6", "creyo", d=-0.25 + k * 0.11), (0, 0, math.radians(20 * (1 if k % 2 else -1))), "LINEAR")
    key(hd, "rotation_euler", W("l6", "creyo", d=0.35), (0, 0, 0))
    key(arm, "rotation_euler", W("l6", "nunca"), tuple(arm.rotation_euler))
    key(arm, "rotation_euler", W("l6", "nunca", d=0.4), (0, 0, 0))
    brows(ba, W("l6", "nunca"), -1)

    # ---- l7 1948, TOWN by day: top-down, the board splits; factories rise; low shot along the river
    set_mood(o, L("l7"), "day")
    ta, tr = o["tAdi"], o["tRudi"]
    hidden(ta, tr)
    pop(ta, L("l7", 0.2), s=0.8)
    pop(tr, L("l7", 0.35), s=0.8)
    shot(L("l7"), (0.0, -0.6, 25.0), (0.0, 0.0, 0.0), 35, (0.0, -0.8, 21.0), (0.0, 0.0, 0.0), 35, fstop=8.0)
    t_sep = W("l7", "separan")
    for half, sgn in ((o["north"], 1), (o["south"], -1)):
        key(half, "location", t_sep, (0, 0, 0))
        key(half, "location", t_sep + 0.9, (0, 1.4 * sgn, 0), "BACK")
    key(o["river"], "scale", t_sep, (1, 1, 1))
    key(o["river"], "scale", t_sep + 0.9, (1, 3.0, 1), "BACK")
    for h, sgn in zip(o["bridge_halves"], (1, -1)):
        key(h, "location", t_sep, (0, 0, 0.12))
        key(h, "location", t_sep + 0.9, (0, 1.4 * sgn, 0.12), "BACK")
        key(h, "rotation_euler", t_sep + 0.3, (0, 0, 0))
        key(h, "rotation_euler", t_sep + 0.8, (math.radians(-35 * sgn), 0, 0), "BACK")
    shake(o, t_sep, 0.45, 0.15)
    hidden(o["fA"], o["fR"], *o["smkA"], *o["smkR"])
    for f, w in ((o["fA"], "adidas"), (o["fR"], "puma")):
        key(f, "scale", W("l7", w, d=-0.25), (1, 1, 0), "BACK")
        key(f, "scale", W("l7", w, d=0.3), (1, 1, 1), "BEZIER")
    for smk, w in ((o["smkA"], "adidas"), (o["smkR"], "puma")):
        for i, s in enumerate(smk):
            t = W("l7", w, d=0.35 + i * 0.15)
            while t < L("l9"):
                key(s, "scale", t, (0.3, 0.3, 0.3), "LINEAR")
                key(s, "scale", t + 0.5, (1.1, 1.1, 1.1), "LINEAR")
                key(s, "scale", t + 1.2, (0, 0, 0), "LINEAR")
                t += 1.25
    shot(W("l7", "adi", d=-0.15), (-1.6, 0.5, 0.75), (-1.0, 4.2, 1.2), 26, (-1.3, 0.7, 0.7), (-1.0, 4.4, 1.0), 28, fstop=2.5)
    shot(W("l7", "rudi", d=-0.1), (-0.4, -0.5, 0.75), (-1.0, -4.4, 1.0), 26, (-0.7, -0.7, 0.7), (-1.0, -4.4, 1.0), 28, fstop=2.5)
    for ob, w in ((ta, "adidas"), (tr, "puma")):
        arm = part(ob, "armR")
        key(arm, "rotation_euler", W("l7", w, d=0.1), (0, 0, 0))
        key(arm, "rotation_euler", W("l7", w, d=0.4), (math.radians(-170), 0, 0), "BACK")
        key(ob, "location", W("l7", w, d=0.1), tuple(ob.location))
        key(ob, "location", W("l7", w, d=0.3), (ob.location[0], ob.location[1], 0.4))
        key(ob, "location", W("l7", w, d=0.5), (ob.location[0], ob.location[1], 0.08), "BACK")
        brows(ob, W("l7", w), 1)
    shot(W("l7", "cada", d=-0.1), (-8.6, 0.0, 0.7), (2.0, 0.0, 0.5), 28, (-6.8, 0.0, 0.65), (2.0, 0.0, 0.5), 28, fstop=4.0)

    # ---- l8 the town split in two: bunting, bars, bakeries, pitches; people look at your shoes
    shot(L("l8"), (-10.5, -9.5, 8.5), (-2.5, 0.0, 0.0), 30, (-9.0, -8.0, 7.0), (-2.5, 0.0, 0.0), 30, fstop=6.0)
    hidden(o["bunting1"], o["bunting-1"], *o["kick"])
    pop(o["bunting1"], W("l8", "dos", d=-0.1), 0.4)
    pop(o["bunting-1"], W("l8", "dos", d=0.05), 0.4)
    for i, (aw, sign) in enumerate(o["shops"]):
        hidden(aw, sign)
        w = "bares" if i % 2 == 0 else "panaderias"
        pop(aw, W("l8", w, d=(i // 2) * 0.12))
        pop(sign, W("l8", w, d=0.1 + (i // 2) * 0.12))
    shot(W("l8", "bares", d=-0.2), (-4.3, 0.2, 0.8), (-5.3, 3.8, 1.1), 32, (-5.0, 0.2, 0.8), (-6.0, 3.8, 1.1), 32, fstop=2.2)
    shot(W("l8", "panaderias", d=-0.1), (-6.2, -0.2, 0.8), (-6.8, -3.8, 1.1), 32, (-6.8, -0.2, 0.8), (-7.0, -3.8, 1.1), 32,
         fstop=2.2)
    shot(W("l8", "hasta", d=-0.1), (5.6, -10.0, 6.5), (5.6, 0.0, 0.0), 30, (5.6, -8.5, 5.0), (5.6, 0.0, 0.0), 32, fstop=6.0)
    for i, (b, sgn) in enumerate(zip(o["kick"], (1, -1))):
        t = W("l8", "equipos", d=i * 0.1)
        pop(b, t - 0.1, 0.2)
        for k in range(8):
            x = 5.6 + (0.5 if k % 2 else -0.5)
            key(b, "location", t + k * 0.35, (x, 2.3 * sgn, 0.12), "BEZIER")
            key(b, "location", t + k * 0.35 + 0.17, (5.6, 2.3 * sgn, 0.45), "BEZIER")
    for p in o["players"]:
        t = W("l8", "equipos")
        while t < L("l9"):
            key(p, "location", t, (p.location[0], p.location[1], 0.12))
            key(p, "location", t + 0.17, (p.location[0], p.location[1], 0.3))
            t += 0.35
    shot(W("l8", "antes", d=-0.15), (-5.6, -0.2, 0.95), (-5.6, 2.6, 0.55), 40, (-5.5, 0.1, 0.85), (-5.6, 2.6, 0.5), 42, fstop=1.8)
    for i, f in enumerate(o["folk"]):
        hd = part(f, "head")
        t = W("l8", "miraban", d=(i % 6) * 0.07)
        key(hd, "rotation_euler", t, (0, 0, 0))
        key(hd, "rotation_euler", t + 0.3, (math.radians(40), 0, 0), "BACK")
        blink(f, 41.8 + (i % 6) * 0.3, 50.3, 2.4)
    shot(W("l8", "zapatos", d=-0.12), (-5.0, 1.3, 0.35), (-5.9, 2.4, 0.1), 38, (-5.4, 1.35, 0.32), (-6.3, 2.4, 0.1), 40, fstop=1.6)

    # ---- l9 CEMETERY at night: fog, moon; Adi's grave at the far end, whip to Rudi's at the near end; crane up
    set_mood(o, L("l9"), "night")
    hidden(o["moon"])
    key(o["moon"], "scale", L("l9"), (1, 1, 1), "CONSTANT")
    key(o["moon"], "scale", L("l10"), (0, 0, 0), "CONSTANT")
    M = P_CEME
    shot(L("l9"), add(M, (0.0, -1.0, 0.65)), add(M, (0.0, 10.5, 0.5)), 70, add(M, (0.0, 0.5, 0.65)), add(M, (0.0, 10.5, 0.5)), 75,
         fstop=1.6)
    shot(W("l9", "estan", d=-0.1), add(M, (0.2, 1.0, 0.7)), add(M, (0.0, -10.5, 0.5)), 70, add(M, (0.2, -1.0, 0.7)),
         add(M, (0.0, -10.5, 0.5)), 75, fstop=1.6)
    shot(W("l9", "cementerio", d=-0.15), add(M, (0.0, -3.0, 6.0)), add(M, (0.0, 0.0, 0.0)), 30, add(M, (0.0, -0.6, 27.0)),
         add(M, (0.0, 0.0, 0.0)), 28, fstop=8.0, cut=False)
    for tb, t in ((o["tombA"], W("l9", "muertos", d=0.1)), (o["tombR"], W("l9", "extremos", d=-0.1))):
        z = tb.location[2]
        key(tb, "location", 0, (tb.location[0], tb.location[1], -1.2), "CONSTANT")
        key(tb, "location", t - 0.01, (tb.location[0], tb.location[1], -1.2), "LINEAR")
        key(tb, "location", t + 0.6, (tb.location[0], tb.location[1], z), "BACK")
        puffs(f"tdust{tb.name}", (tb.location[0], tb.location[1] - 0.3, 0.1), t, n=6, col="#5A4A3A", spread=0.8, size=0.2,
              parent=bpy.data.objects["CEMETERY"])

    # ---- l10 TOWN at sunrise: the halves come together; a match with mixed teams over the river; confetti
    set_mood(o, L("l10"), "night")
    set_mood(o, L("l10", 0.05), "sunrise", fade=1.4)
    shot(L("l10"), (10.0, -12.5, 8.0), (0.0, 0.0, 0.5), 30, (8.5, -10.5, 6.5), (0.0, 0.0, 0.5), 30, fstop=6.0)
    t_join = W("l10", "paces", d=-0.1)
    for half in (o["north"], o["south"]):
        key(half, "location", t_join, tuple(half.location))
        key(half, "location", t_join + 0.8, (0, 0, 0), "BACK")
    key(o["river"], "scale", t_join, (1, 3.0, 1))
    key(o["river"], "scale", t_join + 0.8, (1, 1, 1), "BACK")
    for h in o["bridge_halves"]:
        key(h, "rotation_euler", t_join, tuple(h.rotation_euler))
        key(h, "rotation_euler", t_join + 0.6, (0, 0, 0), "BACK")
        key(h, "location", t_join, tuple(h.location))
        key(h, "location", t_join + 0.8, (0, 0, 0.12), "BACK")
    hidden(o["peace"], o["ballx"], *o["mixed"])
    pop(o["peace"], W("l10", "partido", d=-0.2))
    for i, p in enumerate(o["mixed"]):
        pop(p, W("l10", "partido", d=0.0 + i * 0.06), s=0.55)
    pop(o["ballx"], W("l10", "futbol", d=-0.4))
    bl = o["ballx"]
    t0 = W("l10", "futbol", d=-0.35)
    for k, (x, z) in enumerate([(0, 1.4), (0.5, 0.42), (1.0, 0.9), (1.4, 0.42), (1.7, 0.7), (1.95, 0.42)]):
        key(bl, "location", t0 + k * 0.2, (x, 0, z), "BEZIER")
    confetti("peaceconf", (0.0, 0.0, 0.5), W("l10", "futbol", d=0.0), 90, (BLUE, RED, GOLD, "#FFFFFF"), bpy.data.objects["STAGE"],
             spread=3.5, h=3.0)
    shot(W("l10", "partido", d=-0.3), (3.6, -4.6, 2.4), (0.0, 0.0, 0.45), 34, (1.0, -5.4, 1.9), (0.3, 0.0, 0.5), 36, fstop=2.8)

    apply_shots(o)


# ---------------------------------------------------------------- render
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
        sc.render.use_motion_blur = f not in CUTS  # no smear across hard cuts
        sc.render.filepath = str(p)
        bpy.ops.render.render(write_still=True)


def stills(sc, times):
    out = ROOT / "blender" / "stills"
    out.mkdir(parents=True, exist_ok=True)
    sc.render.resolution_percentage = 50
    sc.render.image_settings.file_format = "JPEG"
    for t in times:
        f = F(float(t))
        sc.frame_set(f)
        sc.render.use_motion_blur = f not in CUTS
        sc.render.filepath = str(out / f"t{float(t):05.1f}.jpg")
        bpy.ops.render.render(write_still=True)


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else ["save"]
    sc = reset()
    o = {}
    build_world(sc, o)
    build_town(o)
    build_hook(o)
    build_laundry(o)
    build_stadium(o)
    build_bunker(o)
    build_cemetery(o)
    animate(o)
    sc.frame_set(0)
    if argv[0] == "save":
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / "blender" / "escena.blend"))
    elif argv[0] == "still":
        stills(sc, argv[1].split(","))
    elif argv[0] == "render":
        render(sc, *argv[1:4])
    print(f"END {END} s, frames 0..{LAST}, cuts {sorted(CUTS)}")


main()
