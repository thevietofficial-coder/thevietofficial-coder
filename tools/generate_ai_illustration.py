"""Generate an animated "energy core" AI illustration.

Uses the same aurora-glass material as the banner/toolkit cards
(soft blurred indigo/violet/cyan wash) so this piece reads as part of
one cohesive profile system rather than a clashing one-off palette.
"""

from math import cos, sin, pi
from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageFilter


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "ai-illustration-animated.gif"
W, H = 480, 280
FRAMES = 48
CENTER = (W // 2, H // 2 + 6)

BASE_BG = (7, 9, 16, 255)
WASH = ((99, 102, 241), (34, 211, 238), (139, 92, 246))
PARTICLE_COLORS = ((99, 102, 241), (34, 211, 238), (139, 92, 246), (236, 72, 153))

random.seed(11)
STARS = [(random.uniform(0, W), random.uniform(0, H), random.uniform(0.4, 1.0)) for _ in range(70)]

RINGS = (
    {"rx": 70, "ry": 26, "tilt": -0.25, "count": 4, "speed": 1.0, "trail": 5},
    {"rx": 118, "ry": 40, "tilt": 0.18, "count": 6, "speed": -0.7, "trail": 6},
    {"rx": 168, "ry": 54, "tilt": -0.1, "count": 7, "speed": 0.5, "trail": 7},
)


def blend(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return tuple(int(a[c] + (b[c] - a[c]) * t) for c in range(3))


def build_background() -> Image.Image:
    base = Image.new("RGBA", (W, H), BASE_BG)
    wash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wdraw = ImageDraw.Draw(wash)
    wdraw.ellipse((CENTER[0] - 220, CENTER[1] - 140, CENTER[0] + 220, CENTER[1] + 140), fill=(*WASH[0], 60))
    wdraw.ellipse((-60, -60, 220, 200), fill=(*WASH[1], 55))
    wdraw.ellipse((W - 220, H - 180, W + 60, H + 60), fill=(*WASH[2], 55))
    wash = wash.filter(ImageFilter.GaussianBlur(40))
    base = Image.alpha_composite(base, wash)
    draw = ImageDraw.Draw(base)
    for x, y, brightness in STARS:
        c = int(120 + 100 * brightness)
        draw.point((x, y), fill=(c, c, min(255, c + 25), 255))
    return base


def orbit_position(ring: dict, index: int, phase: float) -> tuple[float, float, float]:
    angle = 2 * pi * ((phase * ring["speed"]) + index / ring["count"])
    x = CENTER[0] + ring["rx"] * cos(angle)
    depth = sin(angle + ring["tilt"])
    y = CENTER[1] + ring["ry"] * depth
    return x, y, depth


def frame(background: Image.Image, index: int) -> Image.Image:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    phase = index / FRAMES

    for ring in RINGS:
        draw.ellipse(
            (CENTER[0] - ring["rx"], CENTER[1] - ring["ry"], CENTER[0] + ring["rx"], CENTER[1] + ring["ry"]),
            outline=(*blend(WASH[0], WASH[1], 0.5), 90),
            width=1,
        )

    pulse = 0.5 + 0.5 * sin(2 * pi * phase * 2)
    for r in range(46, 6, -3):
        t = 0.4 * (1 - r / 46) * (0.6 + 0.4 * pulse)
        color = blend(WASH[0], WASH[1], 0.5)
        draw.ellipse((CENTER[0] - r, CENTER[1] - r, CENTER[0] + r, CENTER[1] + r), fill=(*color, int(255 * t)))
    core_r = 13 + 3 * pulse
    draw.ellipse(
        (CENTER[0] - core_r, CENTER[1] - core_r, CENTER[0] + core_r, CENTER[1] + core_r),
        fill=(*blend(WASH[0], WASH[1], pulse), 255),
    )

    for ri, ring in enumerate(RINGS):
        for i in range(ring["count"]):
            base_color = PARTICLE_COLORS[(ri + i) % len(PARTICLE_COLORS)]
            for trail in range(ring["trail"], 0, -1):
                trail_phase = phase - trail * 0.006
                x, y, depth = orbit_position(ring, i, trail_phase)
                behind = depth < 0
                size = 3.4 if trail == ring["trail"] else 2.2
                fade = 1 - trail / (ring["trail"] + 1)
                alpha = int(255 * fade * (0.5 if behind else 1.0))
                draw.ellipse((x - size, y - size, x + size, y + size), fill=(*base_color, alpha))

    return Image.alpha_composite(background, overlay).convert("RGB")


background = build_background()
images = [frame(background, i) for i in range(FRAMES)]
images[0].save(
    OUTPUT,
    save_all=True,
    append_images=images[1:],
    duration=70,
    loop=0,
    optimize=True,
    disposal=2,
)
print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
