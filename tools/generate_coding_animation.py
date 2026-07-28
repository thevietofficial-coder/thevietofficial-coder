"""Generate an animated "glass terminal" coding illustration.

Uses the same aurora-glass material as the banner/toolkit cards: a
soft blurred indigo/violet/cyan wash behind a frosted terminal panel
typing out a live model-training log.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "coding-animation.gif"
W, H = 480, 280
MONO = "C:/Windows/Fonts/consola.ttf"

BASE_BG = (7, 9, 16, 255)
WASH = ((99, 102, 241), (34, 211, 238), (139, 92, 246))
PANEL_BOX = (18, 18, W - 18, H - 18)

LABEL = (34, 211, 238)
PROMPT = (167, 139, 250)
PLAIN = (226, 232, 240)
MUTED = (148, 163, 184)
DONE = (110, 231, 183)

LOG_LINES = (
    ("$ python train.py", PROMPT),
    ("Loading dataset... done", MUTED),
    ("Epoch 1/5  [##--------] loss: 1.842", LABEL),
    ("Epoch 2/5  [####------] loss: 1.203", LABEL),
    ("Epoch 3/5  [######----] loss: 0.874", LABEL),
    ("Epoch 4/5  [########--] loss: 0.512", LABEL),
    ("Epoch 5/5  [##########] loss: 0.291", LABEL),
    ("Training complete", DONE),
)


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(MONO, size)


def build_background() -> Image.Image:
    base = Image.new("RGBA", (W, H), BASE_BG)
    wash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wdraw = ImageDraw.Draw(wash)
    wdraw.ellipse((-80, -60, 220, 200), fill=(*WASH[0], 70))
    wdraw.ellipse((W - 220, H - 160, W + 80, H + 80), fill=(*WASH[1], 65))
    wdraw.ellipse((W // 2 - 120, -40, W // 2 + 160, 160), fill=(*WASH[2], 45))
    wash = wash.filter(ImageFilter.GaussianBlur(38))
    return Image.alpha_composite(base, wash)


def total_chars() -> int:
    return sum(len(text) for text, _ in LOG_LINES)


def draw_panel_and_text(background: Image.Image, revealed: int, cursor: bool) -> Image.Image:
    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(panel)
    pdraw.rounded_rectangle(PANEL_BOX, radius=16, fill=(15, 18, 30, 150), outline=(255, 255, 255, 40), width=1)
    image = Image.alpha_composite(background, panel).convert("RGB")

    draw = ImageDraw.Draw(image)
    for i, color in enumerate(((99, 102, 241), (34, 211, 238), (139, 92, 246))):
        cx = 40 + i * 16
        draw.ellipse((cx - 4, 30 - 4, cx + 4, 30 + 4), fill=color)
    draw.text((90, 24), "train.py — session", font=font(12), fill=(180, 190, 205))
    draw.line((32, 46, W - 32, 46), fill=(60, 70, 95))

    text_font = font(15)
    line_h = 25
    x0, y0 = 34, 58
    remaining = revealed
    cursor_x, cursor_y = x0, y0

    for row, (text, color) in enumerate(LOG_LINES):
        y = y0 + row * line_h
        take = text[: max(remaining, 0)]
        if take:
            draw.text((x0, y), take, font=text_font, fill=color)
        cursor_x, cursor_y = x0 + draw.textlength(take, font=text_font), y
        remaining -= len(text)
        if remaining < 0 and not take:
            break

    if cursor:
        draw.rectangle((cursor_x + 2, cursor_y + 1, cursor_x + 9, cursor_y + 17), fill=(103, 232, 249))

    return image


frames = []
background = build_background()
total = total_chars()
for size in range(0, total + 1, 2):
    frames.append(draw_panel_and_text(background, size, True))
for blink in range(12):
    frames.append(draw_panel_and_text(background, total, blink % 2 == 0))

frames[0].save(
    OUTPUT,
    save_all=True,
    append_images=frames[1:],
    duration=65,
    loop=0,
    optimize=True,
    disposal=2,
)
print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
