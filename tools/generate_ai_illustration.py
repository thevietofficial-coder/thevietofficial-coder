"""Generate an original animated neural-network illustration for the profile top.

Visual language matches the hero banner: dark navy base, fine technical
grid, atmospheric glow, and traveling signal pulses along a node graph.
"""

from math import sin, pi
from pathlib import Path
import random

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "ai-illustration-animated.gif"
W, H = 480, 280
FRAMES = 30
BG = "#07111f"
GRID = "#0b2035"

random.seed(7)

# Nodes laid out in a loose oval "brain" silhouette, row by row.
ROWS = (3, 5, 6, 5, 3)
CENTER = (240, 148)
RX, RY = 165, 95
NODES = []
for r, count in enumerate(ROWS):
    row_y = CENTER[1] + (r - (len(ROWS) - 1) / 2) * (2 * RY / (len(ROWS) - 1))
    span = RX * (1 - abs(r - (len(ROWS) - 1) / 2) / (len(ROWS) / 2) * 0.35)
    for c in range(count):
        t = c / (count - 1) if count > 1 else 0.5
        row_x = CENTER[0] + (t - 0.5) * 2 * span
        jitter_x = random.uniform(-6, 6)
        jitter_y = random.uniform(-5, 5)
        NODES.append((row_x + jitter_x, row_y + jitter_y))

# Connect each node to its nearest few neighbours to form a mesh.
EDGES = []
for i, a in enumerate(NODES):
    dists = sorted(
        ((j, (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) for j, b in enumerate(NODES) if j != i),
        key=lambda item: item[1],
    )
    for j, _ in dists[:3]:
        edge = tuple(sorted((i, j)))
        if edge not in EDGES:
            EDGES.append(edge)


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def blend(base: tuple[int, int, int], accent: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(base[c] + (accent[c] - base[c]) * t) for c in range(3))


BASE_RGB = hex_to_rgb(BG)
CYAN_RGB = hex_to_rgb("#22d3ee")
PURPLE_RGB = hex_to_rgb("#a78bfa")


def frame(index: int) -> Image.Image:
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)
    phase = index / FRAMES

    for x in range(0, W, 30):
        draw.line((x, 0, x, H), fill=GRID, width=1)
    for y in range(0, H, 30):
        draw.line((0, y, W, y), fill=GRID, width=1)

    for radius in range(190, 10, -10):
        t = 0.05 * (1 - radius / 190)
        draw.ellipse(
            (CENTER[0] - radius, CENTER[1] - radius, CENTER[0] + radius, CENTER[1] + radius),
            fill=blend(BASE_RGB, CYAN_RGB, t),
        )

    draw.ellipse(
        (CENTER[0] - RX - 14, CENTER[1] - RY - 14, CENTER[0] + RX + 14, CENTER[1] + RY + 14),
        outline="#16425d",
        width=1,
    )

    for n, (i, j) in enumerate(EDGES):
        a, b = NODES[i], NODES[j]
        draw.line((a, b), fill="#16425d", width=1)
        progress = (phase + n / len(EDGES)) % 1
        px = a[0] + (b[0] - a[0]) * progress
        py = a[1] + (b[1] - a[1]) * progress
        color = "#22d3ee" if n % 2 == 0 else "#a78bfa"
        draw.ellipse((px - 3, py - 3, px + 3, py + 3), fill=color)

    for i, (nx, ny) in enumerate(NODES):
        pulse = 0.5 + 0.5 * sin(2 * pi * phase + i * 0.7)
        accent_rgb = CYAN_RGB if i % 3 else PURPLE_RGB
        core = blend(BASE_RGB, accent_rgb, 0.4 + 0.3 * pulse)
        r = 5 + 2 * pulse
        draw.ellipse((nx - r, ny - r, nx + r, ny + r), fill=core, outline=(
            "#67e8f9" if i % 3 else "#c4b5fd"
        ), width=1)

    return image


images = [frame(i) for i in range(FRAMES)]
images[0].save(
    OUTPUT,
    save_all=True,
    append_images=images[1:],
    duration=90,
    loop=0,
    optimize=True,
    disposal=2,
)
print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
