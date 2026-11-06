"""EP04 — Cleopatra, más cerca de la Luna que de las pirámides. Una línea del tiempo vertical en papiro.

  cd manim && ~/.manim-py/Scripts/manim.exe script.py EP04

La voz es el reloj: cada aparición está atada a una palabra de ../transcript.json (at(t) espera hasta t).
Sin temblores ni "line boil" (regla del canal). El fondo de abajo (y < -4.2) queda libre para los subtítulos.
"""
import json
import unicodedata
from pathlib import Path

from manim import *

# ---- the voice is the clock: every cue is a word of ../transcript.json, so a new voice re-syncs by itself ----
ROOT = Path(__file__).resolve().parent.parent
WORDS = json.loads((ROOT / "transcript.json").read_text(encoding="utf-8"))
LINES = {l["id"]: l for l in json.loads((ROOT / "assets" / "lines.json").read_text(encoding="utf-8"))}


def _norm(t):
    t = unicodedata.normalize("NFD", t.lower())
    return "".join(c for c in t if c.isalnum() and not unicodedata.combining(c))


def L(line, d=-0.04):
    return LINES[line]["start"] + d


def W(line, word, k=1, d=-0.04):
    ln = LINES[line]
    hits = [w for w in WORDS if ln["start"] - 0.05 <= w["start"] <= ln["end"] and _norm(w["text"]) == _norm(word)]
    return hits[k - 1]["start"] + d

config.pixel_width, config.pixel_height = 1080, 1920
config.frame_width, config.frame_height = 9, 16
config.frame_rate = 30
config.background_color = "#EFE0BC"

INK, GOLD, LAPIS, TERRA, MOON, SKIN = "#2B2118", "#D9A441", "#1F4E8C", "#B5482E", "#D8D8DE", "#B97A4F"
SERIF, BLACK = "Georgia", "Impact"
END = LINES["l9"]["end"] + 0.45  # the end card (HyperFrames) starts here

# timeline geometry: 2560 a.C. (top) → 1969 d.C. (bottom); no year zero
TX, Y_PYR, Y_MOON = -1.0, 5.4, -3.5
IX = 1.15  # icons column
SPAN = 2560 + 1969 - 1


def y_of(year):  # year < 0 = a.C.
    elapsed = (year + 2560) if year < 0 else (2560 + year - 1)
    return Y_PYR - (Y_PYR - Y_MOON) * elapsed / SPAN


Y_CLEO = y_of(-30)
Y_MAMMOTH = y_of(-1650)


def T(s, size, color=INK, font=BLACK, **kw):
    return Text(s, font=font, font_size=size, color=color, **kw)


def pyramid():
    base = Polygon([-1, 0, 0], [1, 0, 0], [0, 1.15, 0], fill_color=GOLD, fill_opacity=1, stroke_color=INK, stroke_width=6)
    shade = Polygon([0, 0, 0], [1, 0, 0], [0, 1.15, 0], fill_color="#B98530", fill_opacity=1, stroke_width=0)
    rows = VGroup(*[Line([-1 + k * 0.29, k * 0.333, 0], [1 - k * 0.29, k * 0.333, 0], color=INK, stroke_width=3) for k in (1, 2)])
    return VGroup(base, shade, rows, base.copy().set_fill(opacity=0)).move_to(ORIGIN)


def cleo():
    hair = RoundedRectangle(corner_radius=0.25, width=1.55, height=1.75, fill_color="#14110F", fill_opacity=1, stroke_color=INK, stroke_width=5).shift(DOWN * 0.1)
    face = Ellipse(width=0.92, height=1.15, fill_color=SKIN, fill_opacity=1, stroke_color=INK, stroke_width=5).shift(DOWN * 0.05)
    bangs = Rectangle(width=0.98, height=0.32, fill_color="#14110F", fill_opacity=1, stroke_width=0).shift(UP * 0.42)
    band = Rectangle(width=1.0, height=0.1, fill_color=GOLD, fill_opacity=1, stroke_color=INK, stroke_width=3).shift(UP * 0.26)
    cobra = Triangle(fill_color=GOLD, fill_opacity=1, stroke_color=INK, stroke_width=3).scale(0.12).shift(UP * 0.4)
    eyes = VGroup(*[VGroup(Ellipse(width=0.2, height=0.1, fill_color=WHITE, fill_opacity=1, stroke_color=INK, stroke_width=3),
                           Dot(radius=0.04, color=INK), Line([0.1, 0, 0], [0.2, 0.06, 0], color=INK, stroke_width=4)).shift(RIGHT * dx + UP * 0.02)
                    for dx in (-0.2, 0.2)])
    eyes[0][2].flip(UP).shift(LEFT * 0.3)
    lips = Ellipse(width=0.22, height=0.08, fill_color="#9E2A2B", fill_opacity=1, stroke_width=0).shift(DOWN * 0.33)
    collar = AnnularSector(inner_radius=0.5, outer_radius=0.72, angle=PI, start_angle=PI, fill_color=GOLD, fill_opacity=1,
                           stroke_color=INK, stroke_width=4).shift(DOWN * 0.68)
    return VGroup(hair, collar, face, bangs, band, cobra, eyes, lips).move_to(ORIGIN)


def moon():
    disc = Circle(radius=0.72, fill_color=MOON, fill_opacity=1, stroke_color=INK, stroke_width=6)
    craters = VGroup(*[Circle(radius=r, fill_color="#B8B8C2", fill_opacity=1, stroke_color=INK, stroke_width=2).shift(v)
                       for r, v in ((0.16, [-0.25, 0.2, 0]), (0.1, [0.25, -0.25, 0]), (0.08, [0.3, 0.3, 0]))])
    pole = Line([0.05, 0.6, 0], [0.05, 1.25, 0], color=INK, stroke_width=4)
    flag = Rectangle(width=0.36, height=0.22, fill_color=WHITE, fill_opacity=1, stroke_color=INK, stroke_width=3).next_to(pole, RIGHT, buff=0).align_to(pole, UP)
    return VGroup(disc, craters, pole, flag).move_to(ORIGIN)


def mammoth():
    body = Ellipse(width=2.0, height=1.25, fill_color="#7A5230", fill_opacity=1, stroke_color=INK, stroke_width=5)
    legs = VGroup(*[Rectangle(width=0.26, height=0.55, fill_color="#6A4527", fill_opacity=1, stroke_color=INK, stroke_width=4).shift([x, -0.62, 0])
                    for x in (-0.65, -0.3, 0.3, 0.62)])
    head = Circle(radius=0.48, fill_color="#7A5230", fill_opacity=1, stroke_color=INK, stroke_width=5).shift([-0.95, 0.3, 0])
    hump = Circle(radius=0.3, fill_color="#7A5230", fill_opacity=1, stroke_width=0).shift([-0.7, 0.62, 0])
    trunk = CubicBezier([-1.3, 0.15, 0], [-1.6, -0.3, 0], [-1.5, -0.8, 0], [-1.2, -0.85, 0], color=INK, stroke_width=14)
    trunk_in = trunk.copy().set_stroke(color="#7A5230", width=8)
    tusk = CubicBezier([-1.1, -0.05, 0], [-1.3, -0.55, 0], [-0.9, -0.75, 0], [-0.6, -0.55, 0], color=INK, stroke_width=12)
    tusk_in = tusk.copy().set_stroke(color="#FFF8E7", width=7)
    eye = Dot([-1.05, 0.4, 0], radius=0.05, color=INK)
    return VGroup(legs, body, hump, head, trunk, trunk_in, tusk, tusk_in, eye).move_to(ORIGIN)


def node(y, color=GOLD):
    return Dot([TX, y, 0], radius=0.16, color=color, stroke_color=INK, stroke_width=4)


class EP04(Scene):
    def at(self, t):
        dt = t - self.renderer.time
        if dt > 1e-3:
            self.wait(dt)
        elif dt < -0.05:
            print(f"LATE {-dt:.2f}s for cue at {t:.2f}", flush=True)

    def construct(self):
        # ---------- hook: the question and the three icons, on screen from frame 0 ----------
        q1 = T("¿MÁS CERCA", 92).move_to([0, 5.6, 0])
        q2 = T("DE LA LUNA", 92, LAPIS).next_to(q1, DOWN, buff=0.3)
        q3 = T("QUE DE LAS", 92).next_to(q2, DOWN, buff=0.3)
        q4 = T("PIRÁMIDES?", 92, TERRA).next_to(q3, DOWN, buff=0.3)
        title = VGroup(q1, q2, q3, q4)
        p0, c0, m0 = pyramid().scale(1.15), cleo().scale(1.15), moon().scale(1.15)
        row = VGroup(p0, c0, m0).arrange(RIGHT, buff=0.9).move_to([0, -1.2, 0])
        name = T("CLEOPATRA", 40, INK).next_to(c0, DOWN, buff=0.3)
        self.add(title, row, name)
        self.play(c0.animate.scale(1.12), run_time=0.4)
        self.play(c0.animate.scale(1 / 1.12), run_time=0.3)
        self.at(W("l0", "y"))
        self.play(p0.animate.shift(LEFT * 0.25), m0.animate.shift(RIGHT * 0.25), run_time=0.5)

        # ---------- l1: the timeline, the pyramid at the top ----------
        self.at(L("l1"))
        line = Line([TX, Y_PYR, 0], [TX, Y_MOON, 0], color=INK, stroke_width=10)
        self.play(FadeOut(title, shift=UP), FadeOut(c0), FadeOut(m0), FadeOut(name),
                  p0.animate.move_to([IX, Y_PYR, 0]), run_time=0.6)
        n_pyr = node(Y_PYR)
        self.play(Create(line), FadeIn(n_pyr), run_time=0.9)
        lab_pyr = T("Gran Pirámide", 32, INK, font=SERIF).move_to([IX, Y_PYR - 0.95, 0])
        self.play(FadeIn(lab_pyr, shift=LEFT * 0.2), run_time=0.4)
        self.at(W("l1", "dos"))
        d_pyr = T("2560 a.C.", 42, TERRA, font=SERIF, weight=BOLD).next_to(n_pyr, LEFT, buff=0.3)
        self.play(Write(d_pyr), run_time=0.6)

        # ---------- l2: Cleopatra ----------
        self.at(L("l2"))
        c1 = cleo().scale(1.1).move_to([IX, Y_CLEO, 0])
        n_cleo = node(Y_CLEO)
        lab_cleo = T("Cleopatra", 32, INK, font=SERIF).next_to(c1, DOWN, buff=0.12)
        self.play(FadeIn(c1, scale=0.6), FadeIn(n_cleo), FadeIn(lab_cleo, shift=LEFT * 0.2), run_time=0.5)
        self.at(W("l2", "treinta"))
        d_cleo = T("30 a.C.", 42, TERRA, font=SERIF, weight=BOLD).next_to(n_cleo, LEFT, buff=0.3)
        self.play(Write(d_cleo), run_time=0.5)

        # ---------- l3: pyramid → Cleopatra ≈ 2 500 years ----------
        self.at(W("l3", "entre"))
        seg1 = Line([TX, Y_PYR, 0], [TX, Y_CLEO, 0], color=GOLD, stroke_width=18)
        self.play(Create(seg1), run_time=1.2)
        self.add(n_pyr, n_cleo)
        self.at(W("l3", "dos"))
        g1 = T("≈ 2 500\naños", 46, GOLD, font=SERIF, weight=BOLD, line_spacing=0.8).move_to([2.95, (Y_PYR + Y_CLEO) / 2 - 0.2, 0])
        g1.set_stroke(INK, 3, background=True)
        self.play(FadeIn(g1, scale=1.4), run_time=0.4)

        # ---------- l4: Cleopatra → Moon < 2 000 ----------
        self.at(W("l4", "luna"))
        m1 = moon().scale(1.1).move_to([IX, Y_MOON, 0])
        n_moon = node(Y_MOON, LAPIS)
        lab_moon = T("La Luna", 32, INK, font=SERIF).next_to(m1, RIGHT, buff=0.3)
        self.play(FadeIn(m1, shift=UP * 0.6), FadeIn(n_moon), FadeIn(lab_moon, shift=LEFT * 0.2), run_time=0.45)
        self.at(W("l4", "mil"))
        d_moon = T("1969", 42, LAPIS, font=SERIF, weight=BOLD).next_to(n_moon, LEFT, buff=0.3)
        self.play(Write(d_moon), run_time=0.5)
        seg2 = Line([TX, Y_CLEO, 0], [TX, Y_MOON, 0], color=LAPIS, stroke_width=18)
        self.play(Create(seg2), run_time=0.9)
        self.add(n_cleo, n_moon)
        self.at(W("l4", "menos"))
        g2 = T("< 2 000\naños", 46, LAPIS, font=SERIF, weight=BOLD, line_spacing=0.8).move_to([2.95, (Y_CLEO + Y_MOON) / 2 - 0.75, 0])
        self.play(FadeIn(g2, scale=1.4), run_time=0.4)

        # ---------- l5: closer to us ----------
        self.at(W("l5", "cerca"))
        arrow = Arrow([-3.7, Y_CLEO - 0.6, 0], [-3.7, Y_MOON + 0.5, 0], color=LAPIS, stroke_width=12, buff=0, max_tip_length_to_length_ratio=0.12)
        closer = T("MÁS\nCERCA", 40, LAPIS, line_spacing=0.8).next_to(arrow, RIGHT, buff=0.15).shift(DOWN * 0.2)
        self.play(GrowArrow(arrow), FadeIn(closer), run_time=0.5)
        self.at(W("l5", "piramides"))
        self.play(seg1.animate.set_opacity(0.3), g1.animate.set_opacity(0.4), run_time=0.4)

        # ---------- l6: as ancient for her as she is for you ----------
        self.at(L("l6"))
        board = VGroup(line, seg1, seg2, n_pyr, n_cleo, n_moon, p0, c1, m1, lab_pyr, lab_cleo, lab_moon,
                       d_pyr, d_cleo, d_moon, g1, g2, arrow, closer)
        self.play(FadeOut(board), run_time=0.5)
        k = 7.4 / 2530
        b1 = Rectangle(width=2530 * k, height=0.6, fill_color=GOLD, fill_opacity=1, stroke_color=INK, stroke_width=5)
        b2 = Rectangle(width=2055 * k, height=0.6, fill_color=LAPIS, fill_opacity=1, stroke_color=INK, stroke_width=5)
        b1.move_to([0, 2.2, 0]).align_to([-3.7, 0, 0], LEFT)
        b2.move_to([0, -0.4, 0]).align_to([-3.7, 0, 0], LEFT)
        t1 = T("Pirámide → Cleopatra", 40).next_to(b1, UP, buff=0.25).align_to(b1, LEFT)
        t2 = T("Cleopatra → TÚ (2026)", 40).next_to(b2, UP, buff=0.25).align_to(b2, LEFT)
        v1 = T("2 530 años", 40, INK, font=SERIF, weight=BOLD).next_to(b1, DOWN, buff=0.2).align_to(b1, RIGHT)
        v2 = T("2 055 años", 40, INK, font=SERIF, weight=BOLD).next_to(b2, DOWN, buff=0.2).align_to(b2, RIGHT)
        self.at(W("l6", "piramide"))
        self.play(FadeIn(t1), GrowFromEdge(b1, LEFT), run_time=0.6)
        self.play(FadeIn(v1), run_time=0.3)
        self.at(W("l6", "ella", 2))
        self.play(FadeIn(t2), GrowFromEdge(b2, LEFT), run_time=0.6)
        self.play(FadeIn(v2), run_time=0.3)

        # ---------- l7: and there were mammoths ----------
        self.at(L("l7"))
        self.play(FadeOut(VGroup(b1, b2, t1, t2, v1, v2)), run_time=0.4)
        top = VGroup(line, n_pyr, p0, lab_pyr, d_pyr)
        self.play(FadeIn(top), run_time=0.4)
        self.at(W("l7", "mamuts"))
        mm = mammoth().scale(1.1).move_to([2.2, Y_MAMMOTH - 0.8, 0])
        alive = T("¡MAMUTS VIVOS!", 56, TERRA).move_to([1.75, Y_MAMMOTH - 2.25, 0])
        self.play(FadeIn(mm, shift=LEFT * 1.2), run_time=0.45)
        self.play(FadeIn(alive, scale=1.4), run_time=0.35)

        # ---------- l8: the last ones, on an Arctic island ----------
        self.at(W("l8", "isla"))
        isla = T("Isla de Wrangel, Ártico", 34, INK, font=SERIF).next_to(alive, DOWN, buff=0.3)
        self.play(FadeIn(isla, shift=UP * 0.2), run_time=0.4)
        self.at(W("l8", "siglos"))
        n_mm = node(Y_MAMMOTH, TERRA)
        d_mm = T("≈ 2000–1650\na.C.", 32, TERRA, font=SERIF, weight=BOLD, line_spacing=0.8).next_to(n_mm, LEFT, buff=0.3)
        seg3 = Line([TX, Y_PYR, 0], [TX, Y_MAMMOTH, 0], color=TERRA, stroke_width=18)
        self.play(Create(seg3), FadeIn(n_mm), Write(d_mm), run_time=0.6)
        self.add(n_pyr)

        # ---------- l9: ancient for whom? ----------
        self.at(W("l9", "eso"))
        everything = Group(*self.mobjects)
        self.play(FadeOut(everything), run_time=0.5)
        p2, c2, m2 = pyramid().scale(1.15), cleo().scale(1.15), moon().scale(1.15)
        row2 = VGroup(p2, c2, m2).arrange(RIGHT, buff=0.9).move_to([0, -1.6, 0])
        self.play(LaggedStart(*[FadeIn(x, shift=UP * 0.4) for x in row2], lag_ratio=0.25), run_time=0.8)
        self.at(W("l9", "antigua", 2))
        a1 = T("¿ANTIGUA", 120, TERRA).move_to([0, 3.4, 0])
        a2 = T("PARA QUIÉN?", 104, INK).next_to(a1, DOWN, buff=0.35)
        self.play(FadeIn(a1, scale=1.3), run_time=0.35)
        self.play(FadeIn(a2, scale=1.3), run_time=0.35)
        self.at(END)
