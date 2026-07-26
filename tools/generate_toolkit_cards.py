"""Render tech-styled horizontal toolkit cards for the GitHub profile README.

Visual language matches the animated banner: dark navy base, a fine
technical grid, radial glow accents, and a small network-node motif.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "toolkit-cards"
FONT = "C:/Windows/Fonts/segoeuib.ttf"
FONT_BOLD = "C:/Windows/Fonts/segoeuib.ttf"
W, H = 1080, 190
BG = "#07111f"
GRID = "#0b2035"
BORDER = "#1e506c"
ACCENT = "#3b82f6"
SILVER = "#94a3b8"

CARDS = (
    (
        "toolkit-ai-ml.png",
        "AI",
        "AI & Machine Learning",
        "MODELS, RETRIEVAL, AND GENERATIVE AI APPLICATIONS",
        ("Python", "PyTorch", "TensorFlow", "Keras", "scikit-learn", "NumPy", "Pandas", "Matplotlib", "OpenCV"),
    ),
    (
        "toolkit-languages-web.png",
        "</>",
        "Languages & Web",
        "CORE LANGUAGES AND WEB DELIVERY",
        ("C++", "Java", "JavaScript", "Next.js", "WordPress"),
    ),
    (
        "toolkit-tools-hardware.png",
        "OPS",
        "Tools, Design & Hardware",
        "BUILD, VERSION, DESIGN, AND DEPLOY TO THE EDGE",
        ("Git", "GitHub", "Photoshop", "Canva", "Raspberry Pi"),
    ),
)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT_BOLD if bold else FONT, size)


def hex_to_rgb(value: str) -> tuple[int, int, int]:
    value = value.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


def blend(base: tuple[int, int, int], accent: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(base[c] + (accent[c] - base[c]) * t) for c in range(3))


def tag_width(draw: ImageDraw.ImageDraw, value: str, tag_font: ImageFont.FreeTypeFont) -> int:
    return int(draw.textbbox((0, 0), value, font=tag_font)[2]) + 34


def draw_grid(draw: ImageDraw.ImageDraw) -> None:
    for x in range(0, W, 36):
        draw.line((x, 0, x, H), fill=GRID, width=1)
    for y in range(0, H, 36):
        draw.line((0, y, W, y), fill=GRID, width=1)


def draw_glow(draw: ImageDraw.ImageDraw, center: tuple[int, int], radius: int, accent_rgb: tuple[int, int, int], base_rgb: tuple[int, int, int]) -> None:
    cx, cy = center
    for r in range(radius, 4, -3):
        t = 0.22 * (1 - r / radius)
        color = blend(base_rgb, accent_rgb, t)
        draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=color)


def draw_network(draw: ImageDraw.ImageDraw) -> None:
    hub = (958, 46)
    satellites = [(1006, 24), (1032, 60), (994, 80)]
    for point in satellites:
        draw.line((hub, point), fill=BORDER, width=1)
        draw.ellipse((point[0] - 3, point[1] - 3, point[0] + 3, point[1] + 3), outline=SILVER, width=1)
    draw.ellipse((hub[0] - 4, hub[1] - 4, hub[0] + 4, hub[1] + 4), fill=ACCENT)


def render(filename: str, glyph: str, title: str, subtitle: str, tags: tuple[str, ...]) -> None:
    base_rgb = hex_to_rgb(BG)
    accent_rgb = hex_to_rgb(ACCENT)
    silver_rgb = hex_to_rgb(SILVER)

    image = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(image)
    draw_grid(draw)
    draw_glow(draw, (60, 53), 92, accent_rgb, base_rgb)
    draw_network(draw)
    draw.rounded_rectangle((1, 1, W - 2, H - 2), radius=22, outline=BORDER, width=2)

    # Node-style icon badge, echoing the banner's AI nucleus motif.
    icon_font = font(15 if len(glyph) <= 3 else 12, bold=True)
    draw.ellipse((36, 29, 84, 77), outline=ACCENT, width=2)
    draw.ellipse((44, 37, 76, 69), fill=blend(base_rgb, accent_rgb, 0.35))
    gw = draw.textbbox((0, 0), glyph, font=icon_font)[2]
    draw.text((60 - gw / 2, 46), glyph, font=icon_font, fill="#f8fafc")

    draw.text((100, 25), title, font=font(29), fill="#f8fafc")
    draw.text((102, 66), subtitle, font=font(13), fill=SILVER)
    draw.line((100, 90, 100 + draw.textbbox((0, 0), subtitle, font=font(13))[2], 90), fill=blend(base_rgb, accent_rgb, 0.6), width=2)

    tag_font = font(16)
    x, y = 32, 116
    tag_fill = blend(base_rgb, silver_rgb, 0.12)
    tag_border = blend(base_rgb, silver_rgb, 0.45)
    for tag in tags:
        width = tag_width(draw, tag, tag_font)
        if x + width > W - 32:
            x, y = 32, y + 42
        draw.rounded_rectangle((x, y, x + width, y + 30), radius=15, fill=tag_fill, outline=tag_border, width=1)
        draw.text((x + 17, y + 6), tag, font=tag_font, fill="#e2e8f0")
        x += width + 10

    image.save(OUT / filename, optimize=True)


OUT.mkdir(parents=True, exist_ok=True)
for card in CARDS:
    render(*card)
    print(f"Wrote {card[0]}")
