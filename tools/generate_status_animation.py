"""Generate the compact status animation shown below the profile hero."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "now-status.gif"
W, H = 560, 52
FONT = "C:/Windows/Fonts/segoeuib.ttf"
MESSAGES = (
    "Now: Building AI apps with LLMs & RAG",
    "Now: Learning AI Agents & MLOps",
    "Now: Exploring Computer Vision projects",
)


def render(message: str, visible: int, cursor: bool) -> Image.Image:
    image = Image.new("RGB", (W, H), "#07111f")
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype(FONT, 18)
    draw.rounded_rectangle((1, 1, W - 2, H - 2), radius=25, outline="#16425d", width=1)
    draw.ellipse((20, 20, 30, 30), fill="#22d3ee")
    draw.text((45, 15), message[:visible] + ("|" if cursor else ""), font=font, fill="#cbd5e1")
    return image


frames = []
for message in MESSAGES:
    for size in range(1, len(message) + 1, 3):
        frames.append(render(message, size, True))
    for blink in range(8):
        frames.append(render(message, len(message), blink % 2 == 0))

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
