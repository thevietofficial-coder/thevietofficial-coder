"""Generate an original animated "typing code" illustration for the profile top."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "coding-animation.gif"
W, H = 480, 280
MONO = "C:/Windows/Fonts/consola.ttf"
BG = "#07111f"
PANEL = "#0b1626"

KEYWORD = "#a78bfa"
STRING = "#38bdf8"
FUNC = "#67e8f9"
PLAIN = "#e2e8f0"
COMMENT = "#64748b"

LINES = (
    (("# rag_pipeline.py", COMMENT),),
    (("from ", KEYWORD), ("retriever", PLAIN), (" import ", KEYWORD), ("search", FUNC)),
    (("from ", KEYWORD), ("llm", PLAIN), (" import ", KEYWORD), ("generate", FUNC)),
    ((" ", PLAIN),),
    (("def ", KEYWORD), ("answer", FUNC), ("(query: str) -> str:", PLAIN)),
    (("    docs = ", PLAIN), ("search", FUNC), ("(query, k=5)", PLAIN)),
    (("    context = ", PLAIN), ('"\\n"', STRING), (".join(docs)", PLAIN)),
    (("    return ", KEYWORD), ("generate", FUNC), ("(query, context)", PLAIN)),
)


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(MONO, size)


def total_chars() -> int:
    return sum(len(seg) for line in LINES for seg, _ in line)


def frame(revealed: int, cursor: bool) -> Image.Image:
    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle((1, 1, W - 2, H - 2), radius=14, fill=PANEL, outline="#1e506c", width=2)
    draw.rounded_rectangle((1, 1, W - 2, 30), radius=14, fill="#111d30")
    draw.rectangle((1, 18, W - 2, 30), fill="#111d30")
    for i, color in enumerate(("#f87171", "#fbbf24", "#34d399")):
        cx = 20 + i * 18
        draw.ellipse((cx - 5, 10 - 5, cx + 5, 10 + 5), fill=color)
    draw.text((90, 5), "rag_pipeline.py", font=font(12), fill="#94a3b8")

    code_font = font(14)
    line_h = 26
    x0, y0 = 20, 44
    remaining = revealed
    cursor_x, cursor_y = x0, y0

    for row, line in enumerate(LINES):
        x = x0
        y = y0 + row * line_h
        for seg, color in line:
            if remaining <= 0:
                break
            take = seg[: max(remaining, 0)]
            if not take:
                break
            draw.text((x, y), take, font=code_font, fill=color)
            x += draw.textlength(take, font=code_font)
            remaining -= len(take)
        cursor_x, cursor_y = x, y
        if remaining <= 0:
            break

    if cursor:
        draw.rectangle((cursor_x + 2, cursor_y + 1, cursor_x + 10, cursor_y + 18), fill="#38bdf8")

    return image


frames = []
total = total_chars()
for size in range(0, total + 1, 2):
    frames.append(frame(size, True))
for blink in range(10):
    frames.append(frame(total, blink % 2 == 0))
# Brief hold on the empty shell before the loop restarts.
for _ in range(3):
    frames.append(frame(0, False))

frames[0].save(
    OUTPUT,
    save_all=True,
    append_images=frames[1:],
    duration=55,
    loop=0,
    optimize=True,
    disposal=2,
)
print(f"Wrote {OUTPUT} ({OUTPUT.stat().st_size:,} bytes)")
