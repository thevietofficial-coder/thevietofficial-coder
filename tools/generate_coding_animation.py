"""Generate an original animated "matrix terminal" coding illustration.

A completely different visual language from the syntax-highlighted
editor version: black background, falling green matrix rain, and a
translucent terminal panel typing out a live model-training log.
"""

from pathlib import Path
import random

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "coding-animation.gif"
W, H = 480, 280
MONO = "C:/Windows/Fonts/consola.ttf"

BLACK = (0, 2, 1)
RAIN_CHARS = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ<>/*+-="
RAIN_FONT_SIZE = 15
COLS = W // RAIN_FONT_SIZE
TRAIL = 9

random.seed(3)
COL_SPEED = [random.uniform(0.5, 1.6) for _ in range(COLS)]
COL_OFFSET = [random.uniform(0, H) for _ in range(COLS)]

LOG_LINES = (
    ("$ python train.py", (120, 255, 160)),
    ("Loading dataset... done", (90, 200, 130)),
    ("Epoch 1/5  [##--------] loss: 1.842", (60, 255, 140)),
    ("Epoch 2/5  [####------] loss: 1.203", (60, 255, 140)),
    ("Epoch 3/5  [######----] loss: 0.874", (60, 255, 140)),
    ("Epoch 4/5  [########--] loss: 0.512", (60, 255, 140)),
    ("Epoch 5/5  [##########] loss: 0.291", (60, 255, 140)),
    ("Training complete", (170, 255, 210)),
)

PANEL_BOX = (14, 14, W - 14, H - 14)


def rain_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(MONO, size)


def code_font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(MONO, size)


def draw_rain(draw: ImageDraw.ImageDraw, frame_index: int, dim: bool) -> None:
    font = rain_font(RAIN_FONT_SIZE)
    for col in range(COLS):
        x = col * RAIN_FONT_SIZE
        head_y = (COL_OFFSET[col] + frame_index * COL_SPEED[col] * 6) % (H + TRAIL * RAIN_FONT_SIZE)
        head_y -= TRAIL * RAIN_FONT_SIZE
        for t in range(TRAIL):
            y = head_y + t * RAIN_FONT_SIZE
            if -RAIN_FONT_SIZE < y < H:
                rng = random.Random((col * 977) + (frame_index // 3) + t)
                ch = rng.choice(RAIN_CHARS)
                brightness = 1 - t / TRAIL
                g = int(70 + 150 * brightness)
                color = (0, g if not dim else g // 3, int(g * 0.45) if not dim else g // 5)
                draw.text((x, y), ch, font=font, fill=color)


def total_chars() -> int:
    return sum(len(text) for text, _ in LOG_LINES)


def draw_panel_and_text(image: Image.Image, revealed: int, cursor: bool) -> None:
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.rounded_rectangle(PANEL_BOX, radius=12, fill=(2, 12, 8, 195), outline=(40, 220, 140, 255), width=2)
    image.paste(Image.alpha_composite(image.convert("RGBA"), overlay).convert("RGB"), (0, 0))

    draw = ImageDraw.Draw(image)
    draw.ellipse((28, 26, 36, 34), fill=(255, 90, 90))
    draw.text((46, 22), "training.log", font=code_font(12), fill=(150, 210, 180))
    draw.line((28, 44, W - 28, 44), fill=(30, 120, 90))

    font = code_font(15)
    line_h = 25
    x0, y0 = 30, 56
    remaining = revealed
    cursor_x, cursor_y = x0, y0

    for row, (text, color) in enumerate(LOG_LINES):
        y = y0 + row * line_h
        take = text[: max(remaining, 0)]
        if take:
            draw.text((x0, y), take, font=font, fill=color)
        cursor_x, cursor_y = x0 + draw.textlength(take, font=font), y
        remaining -= len(text)
        if remaining < 0 and not take:
            break

    if cursor:
        draw.rectangle((cursor_x + 2, cursor_y + 1, cursor_x + 9, cursor_y + 17), fill=(120, 255, 170))


def frame(frame_index: int, revealed: int, cursor: bool, dim: bool = False) -> Image.Image:
    image = Image.new("RGB", (W, H), BLACK)
    draw = ImageDraw.Draw(image)
    draw_rain(draw, frame_index, dim)
    draw_panel_and_text(image, revealed, cursor)
    return image


frames = []
total = total_chars()
f_index = 0
for size in range(0, total + 1, 2):
    frames.append(frame(f_index, size, True))
    f_index += 1
for blink in range(12):
    frames.append(frame(f_index, total, blink % 2 == 0))
    f_index += 1

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
