"""Build the animated hero banner used by the profile README.

A deliberate departure from the old dark-navy/node-network look: a
glassmorphic aurora banner with soft, translucent color ribbons
drifting behind a frosted glass identity panel.
"""

from math import pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "github-profile-banner-animated.gif"
W, H = 960, 288
FRAMES = 30
FONT = Path("C:/Windows/Fonts/segoeuib.ttf")

BASE_BG = (7, 9, 16, 255)
RIBBONS = (
    {"color": (99, 102, 241), "y": 70, "amp": 26, "wavelength": 420, "speed": 0.6, "thickness": 90, "alpha": 95},
    {"color": (139, 92, 246), "y": 150, "amp": 34, "wavelength": 520, "speed": -0.4, "thickness": 110, "alpha": 85},
    {"color": (34, 211, 238), "y": 200, "amp": 22, "wavelength": 360, "speed": 0.8, "thickness": 80, "alpha": 90},
    {"color": (236, 72, 153), "y": 40, "amp": 18, "wavelength": 300, "speed": -0.55, "thickness": 60, "alpha": 60},
)

TITLE = (248, 250, 252)
SUBTITLE = (125, 211, 252)
MUTED = (148, 163, 184)


def text_font(size: int):
    return ImageFont.truetype(str(FONT), size)


def wave_polygon(y_base: float, amplitude: float, wavelength: float, phase: float, thickness: float, step: int = 10) -> list:
    top, bottom = [], []
    x = 0
    while x <= W:
        y = y_base + amplitude * sin(2 * pi * (x / wavelength + phase))
        top.append((x, y - thickness / 2))
        bottom.append((x, y + thickness / 2))
        x += step
    return top + bottom[::-1]


def frame(index: int) -> Image.Image:
    phase = index / FRAMES
    base = Image.new("RGBA", (W, H), BASE_BG)

    aurora = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for ribbon in RIBBONS:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        poly = wave_polygon(ribbon["y"], ribbon["amp"], ribbon["wavelength"], phase * ribbon["speed"], ribbon["thickness"])
        draw.polygon(poly, fill=(*ribbon["color"], ribbon["alpha"]))
        aurora = Image.alpha_composite(aurora, layer)
    aurora = aurora.filter(ImageFilter.GaussianBlur(18))
    base = Image.alpha_composite(base, aurora)

    vignette = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    vdraw = ImageDraw.Draw(vignette)
    vdraw.rectangle((0, 0, W, H), fill=(7, 9, 16, 70))
    base = Image.alpha_composite(base, vignette)

    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(panel)
    pdraw.rounded_rectangle((40, 36, 456, 252), radius=24, fill=(15, 18, 30, 130), outline=(255, 255, 255, 35), width=1)
    base = Image.alpha_composite(base, panel)

    draw = ImageDraw.Draw(base)
    draw.text((66, 62), "BÙI HOÀNG VIỆT", font=text_font(33), fill=TITLE)
    draw.text((66, 113), "AI / LLM / RAG Engineer", font=text_font(19), fill=SUBTITLE)
    draw.text((66, 144), "Turning AI ideas into real-world systems", font=text_font(17), fill=(203, 213, 225))

    draw.rounded_rectangle((66, 196, 326, 228), radius=16, outline=(148, 197, 255, 110), width=1)
    scanner = 73 + int(((phase * 1.35) % 1) * 246)
    draw.line((scanner, 201, scanner, 223), fill=(103, 232, 249), width=2)
    draw.text((82, 203), "RAG  •  LLMs  •  VISION", font=text_font(12), fill=(203, 213, 225))

    draw.text((820, 258), "thevietofficial-coder", font=text_font(12), fill=(148, 163, 184))

    return base.convert("RGB")


images = [frame(i) for i in range(FRAMES)]
images[0].save(
    OUTPUT,
    save_all=True,
    append_images=images[1:],
    duration=100,
    loop=0,
    optimize=True,
    disposal=2,
)
print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
