"""Build the lightweight animated hero used by the profile README."""

from math import cos, pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "github-profile-banner-animated.gif"
W, H = 960, 288
FRAMES = 24
FONT = Path("C:/Windows/Fonts/segoeuib.ttf")
FONT_BOLD = Path("C:/Windows/Fonts/segoeuib.ttf")


def text_font(size: int):
    return ImageFont.truetype(str(FONT), size)


def frame(index: int) -> Image.Image:
    image = Image.new("RGB", (W, H), "#07111f")
    draw = ImageDraw.Draw(image)
    phase = index / FRAMES

    # Calm cyan/purple atmospheric glow.
    for radius in range(260, 8, -8):
        alpha = int(16 * (1 - radius / 260))
        color = (10 + alpha, 32 + alpha * 2, 54 + alpha * 3)
        draw.ellipse((680 - radius, 94 - radius, 680 + radius, 94 + radius), fill=color)

    # Fine technical grid.
    for x in range(0, W, 48):
        draw.line((x, 0, x, H), fill="#0b2035", width=1)
    for y in range(0, H, 48):
        draw.line((0, y, W, y), fill="#0b2035", width=1)

    # Animated data routes from identity to AI nodes.
    origin = (438, 145)
    nodes = [(590, 74), (710, 132), (610, 222), (830, 75), (850, 218)]
    for n, target in enumerate(nodes):
        color = "#22d3ee" if n < 3 else "#a78bfa"
        draw.line((origin, target), fill="#16425d", width=2)
        draw.ellipse((target[0] - 7, target[1] - 7, target[0] + 7, target[1] + 7), outline=color, width=2)
        progress = (phase + n / len(nodes)) % 1
        px = origin[0] + (target[0] - origin[0]) * progress
        py = origin[1] + (target[1] - origin[1]) * progress
        draw.ellipse((px - 4, py - 4, px + 4, py + 4), fill=color)

    # Central AI nucleus with a gentle pulse.
    pulse = 4 * sin(2 * pi * phase)
    draw.ellipse((origin[0] - 23 - pulse, origin[1] - 23 - pulse, origin[0] + 23 + pulse, origin[1] + 23 + pulse), outline="#22d3ee", width=2)
    draw.ellipse((origin[0] - 11, origin[1] - 11, origin[0] + 11, origin[1] + 11), fill="#0e7490")
    draw.text((origin[0] - 7, origin[1] - 10), "AI", font=text_font(13), fill="white")

    # Profile copy and a small moving scanner on the lower line.
    draw.text((58, 59), "BÙI HOÀNG VIỆT", font=text_font(34), fill="#f8fafc")
    draw.text((58, 111), "AI / LLM / RAG Engineer", font=text_font(20), fill="#67e8f9")
    draw.text((58, 143), "Turning AI ideas into real-world systems", font=text_font(18), fill="#cbd5e1")
    draw.rounded_rectangle((58, 202, 318, 234), radius=16, outline="#1e506c", width=1)
    scanner = 65 + int(((phase * 1.35) % 1) * 246)
    draw.line((scanner, 207, scanner, 229), fill="#22d3ee", width=2)
    draw.text((74, 209), "RAG  •  LLMs  •  VISION", font=text_font(12), fill="#94a3b8")

    draw.text((728, 252), "thevietofficial-coder", font=text_font(12), fill="#64748b")
    return image


images = [frame(i) for i in range(FRAMES)]
images[0].save(
    OUTPUT,
    save_all=True,
    append_images=images[1:],
    duration=125,
    loop=0,
    optimize=True,
    disposal=2,
)
print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
