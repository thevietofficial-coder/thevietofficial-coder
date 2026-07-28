"""Generate the compact status ticker shown below the profile hero.

Matches the banner's glassmorphic aurora treatment: a frosted pill
over a soft drifting color wash, instead of the old flat dark bar.
"""

from math import pi, sin
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "now-status.gif"
W, H = 560, 52
FONT = "C:/Windows/Fonts/segoeuib.ttf"
MESSAGES = (
    "Now: Building AI apps with LLMs & RAG",
    "Now: Learning AI Agents & MLOps",
    "Now: Exploring Computer Vision projects",
)

BASE_BG = (7, 9, 16, 255)
WASH_COLORS = ((99, 102, 241), (34, 211, 238), (236, 72, 153))


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size)


def render(message: str, visible: int, cursor: bool, phase: float) -> Image.Image:
    base = Image.new("RGBA", (W, H), BASE_BG)

    wash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wdraw = ImageDraw.Draw(wash)
    for i, color in enumerate(WASH_COLORS):
        cx = W * ((phase * (0.4 + i * 0.15) + i / len(WASH_COLORS)) % 1)
        cy = H / 2 + 10 * sin(2 * pi * (phase + i))
        r = 60
        wdraw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(*color, 70))
    wash = wash.filter(ImageFilter.GaussianBlur(14))
    base = Image.alpha_composite(base, wash)

    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(panel)
    pdraw.rounded_rectangle((1, 1, W - 2, H - 2), radius=25, fill=(15, 18, 30, 130), outline=(255, 255, 255, 35), width=1)
    base = Image.alpha_composite(base, panel)

    draw = ImageDraw.Draw(base)
    pulse = 0.5 + 0.5 * sin(2 * pi * phase * 3)
    dot_r = 5 + pulse
    draw.ellipse((25 - dot_r, 26 - dot_r, 25 + dot_r, 26 + dot_r), fill=(103, 232, 249))
    draw.text((45, 15), message[:visible] + ("|" if cursor else ""), font=font(18), fill=(226, 232, 240))

    return base.convert("RGB")


frames = []
total_steps = sum(len(m) // 3 + 1 + 8 for m in MESSAGES)
step_counter = 0
for message in MESSAGES:
    for size in range(1, len(message) + 1, 3):
        frames.append(render(message, size, True, step_counter / total_steps))
        step_counter += 1
    for blink in range(8):
        frames.append(render(message, len(message), blink % 2 == 0, step_counter / total_steps))
        step_counter += 1

frames[0].save(
    OUTPUT,
    save_all=True,
    append_images=frames[1:],
    duration=110,
    loop=0,
    optimize=True,
    disposal=2,
)
print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
