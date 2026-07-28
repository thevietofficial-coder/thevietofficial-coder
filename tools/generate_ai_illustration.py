"""Generate an original animated "energy core" AI illustration.

A completely different visual language from the node-graph version:
warm magenta/gold/violet jewel tones, a radial nebula backdrop, and
particles orbiting a pulsing core on tilted elliptical rings.
"""

from math import cos, sin, pi
from pathlib import Path
import random

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "ai-illustration-animated.gif"
W, H = 480, 280
FRAMES = 48
CENTER = (W // 2, H // 2 + 6)

BG_OUTER = "#04010a"
BG_INNER = "#2b0b3f"
CORE_GOLD = "#fbbf24"
CORE_MAGENTA = "#ec4899"

PARTICLE_COLORS = ("#fbbf24", "#ec4899", "#8b5cf6", "#fb7185")

random.seed(11)
STARS = [
    (random.uniform(0, W), random.uniform(0, H), random.uniform(0.4, 1.0))
    for _ in range(70)
]

RINGS = (
    {"rx": 70, "ry": 26, "tilt": -0.25, "count": 4, "speed": 1.0, "trail": 5},
    {"rx": 118, "ry": 40, "tilt": 0.18, "count": 6, "speed": -0.7, "trail": 6},
    {"rx": 168, "ry": 54, "tilt": -0.1, "count": 7, "speed": 0.5, "trail": 7},
)


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def blend(base: tuple[int, int, int], accent: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    t = max(0.0, min(1.0, t))
    return tuple(int(base[c] + (accent[c] - base[c]) * t) for c in range(3))


OUTER_RGB = hex_to_rgb(BG_OUTER)
INNER_RGB = hex_to_rgb(BG_INNER)
GOLD_RGB = hex_to_rgb(CORE_GOLD)
MAGENTA_RGB = hex_to_rgb(CORE_MAGENTA)
PARTICLE_RGB = [hex_to_rgb(c) for c in PARTICLE_COLORS]


def draw_background(draw: ImageDraw.ImageDraw) -> None:
    max_r = 300
    for r in range(max_r, 0, -4):
        t = 1 - r / max_r
        color = blend(OUTER_RGB, INNER_RGB, t * t)
        draw.ellipse(
            (CENTER[0] - r, CENTER[1] - r * 0.75, CENTER[0] + r, CENTER[1] + r * 0.75),
            fill=color,
        )
    for x, y, brightness in STARS:
        c = int(120 + 100 * brightness)
        draw.point((x, y), fill=(c, c, min(255, c + 25)))


def orbit_position(ring: dict, index: int, phase: float) -> tuple[float, float, float]:
    angle = 2 * pi * ((phase * ring["speed"]) + index / ring["count"])
    x = CENTER[0] + ring["rx"] * cos(angle)
    depth = sin(angle + ring["tilt"])
    y = CENTER[1] + ring["ry"] * depth
    return x, y, depth


def frame(index: int) -> Image.Image:
    image = Image.new("RGB", (W, H), BG_OUTER)
    draw = ImageDraw.Draw(image)
    phase = index / FRAMES
    draw_background(draw)

    for ring in RINGS:
        draw.ellipse(
            (
                CENTER[0] - ring["rx"], CENTER[1] - ring["ry"],
                CENTER[0] + ring["rx"], CENTER[1] + ring["ry"],
            ),
            outline=blend(OUTER_RGB, MAGENTA_RGB, 0.22),
            width=1,
        )

    pulse = 0.5 + 0.5 * sin(2 * pi * phase * 2)
    for r in range(46, 6, -3):
        t = 0.35 * (1 - r / 46) * (0.6 + 0.4 * pulse)
        color = blend(OUTER_RGB, blend(MAGENTA_RGB, GOLD_RGB, 0.5), t)
        draw.ellipse((CENTER[0] - r, CENTER[1] - r, CENTER[0] + r, CENTER[1] + r), fill=color)
    core_r = 13 + 3 * pulse
    draw.ellipse(
        (CENTER[0] - core_r, CENTER[1] - core_r, CENTER[0] + core_r, CENTER[1] + core_r),
        fill=blend(MAGENTA_RGB, GOLD_RGB, pulse),
    )

    for ri, ring in enumerate(RINGS):
        for i in range(ring["count"]):
            base_color = PARTICLE_RGB[(ri + i) % len(PARTICLE_RGB)]
            for trail in range(ring["trail"], 0, -1):
                trail_phase = phase - trail * 0.006
                x, y, depth = orbit_position(ring, i, trail_phase)
                behind = depth < 0
                size = 3.4 if trail == ring["trail"] else 2.2
                fade = 1 - trail / (ring["trail"] + 1)
                color = blend(OUTER_RGB, base_color, fade * (0.5 if behind else 1.0))
                draw.ellipse((x - size, y - size, x + size, y + size), fill=color)

    return image


images = [frame(i) for i in range(FRAMES)]
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
