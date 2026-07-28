"""Render animated glassmorphic toolkit cards for the GitHub profile README.

Matches the banner/ticker's aurora-glass treatment: a soft drifting
color wash behind a frosted panel, with skill tags popping in one by
one instead of the old flat dark card with a solid accent bar.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "toolkit-cards"
FONT = "C:/Windows/Fonts/segoeuib.ttf"
W, H = 1080, 190
BASE_BG = (7, 9, 16, 255)

CARDS = (
    (
        "toolkit-ai-ml.gif",
        "AI & Machine Learning",
        "MODELS, RETRIEVAL, AND GENERATIVE AI APPLICATIONS",
        (
            "Python", "PyTorch", "TensorFlow", "Keras", "scikit-learn", "NumPy", "Pandas",
            "Matplotlib", "OpenCV", "YOLOv8", "Hugging Face", "Gymnasium", "Jupyter",
        ),
        ((99, 102, 241), (34, 211, 238)),
    ),
    (
        "toolkit-languages-web.gif",
        "Languages & Web",
        "CORE LANGUAGES AND WEB DELIVERY",
        ("C++", "Java", "JavaScript", "Next.js", "WordPress", "Streamlit"),
        ((139, 92, 246), (236, 72, 153)),
    ),
    (
        "toolkit-tools-hardware.gif",
        "Tools, Design & Hardware",
        "BUILD, VERSION, DESIGN, AND DEPLOY TO THE EDGE",
        ("Git", "GitHub", "Photoshop", "Canva", "Raspberry Pi", "Arduino", "ROS2", "pytest"),
        ((245, 158, 11), (244, 63, 94)),
    ),
)


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size)


def blend(a: tuple[int, int, int], b: tuple[int, int, int], t: float) -> tuple[int, int, int]:
    return tuple(int(a[c] + (b[c] - a[c]) * t) for c in range(3))


def tag_width(draw: ImageDraw.ImageDraw, value: str, tag_font: ImageFont.FreeTypeFont) -> int:
    return int(draw.textbbox((0, 0), value, font=tag_font)[2]) + 34


def build_background(colors: tuple[tuple[int, int, int], tuple[int, int, int]]) -> Image.Image:
    color_a, color_b = colors
    base = Image.new("RGBA", (W, H), BASE_BG)

    wash = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    wdraw = ImageDraw.Draw(wash)
    wdraw.ellipse((-60, -80, 260, 200), fill=(*color_a, 100))
    wdraw.ellipse((W - 300, H - 140, W + 60, H + 120), fill=(*color_b, 90))
    wash = wash.filter(ImageFilter.GaussianBlur(36))
    base = Image.alpha_composite(base, wash)

    panel = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    pdraw = ImageDraw.Draw(panel)
    pdraw.rounded_rectangle((1, 1, W - 2, H - 2), radius=22, fill=(15, 18, 30, 120), outline=(255, 255, 255, 35), width=1)
    base = Image.alpha_composite(base, panel)

    return base


def draw_gradient_bar(image: Image.Image, colors: tuple[tuple[int, int, int], tuple[int, int, int]]) -> None:
    color_a, color_b = colors
    for y in range(29, 77):
        t = (y - 29) / (77 - 29)
        color = blend(color_a, color_b, t)
        for x in range(28, 34):
            image.putpixel((x, y), (*color, 255))


def draw_card(background: Image.Image, title: str, subtitle: str, tags: tuple[str, ...], colors, loading: bool) -> Image.Image:
    image = background.copy()
    draw_gradient_bar(image, colors)
    draw = ImageDraw.Draw(image)
    draw.text((58, 25), title, font=font(29), fill=(248, 250, 252))
    draw.text((60, 66), subtitle, font=font(13), fill=(180, 190, 205))

    accent = blend(colors[0], colors[1], 0.5)
    tag_font = font(16)
    x, y = 32, 111
    for tag in tags:
        width = tag_width(draw, tag, tag_font)
        if x + width > W - 32:
            x, y = 32, y + 42
        draw.rounded_rectangle((x, y, x + width, y + 30), radius=15, fill=(20, 24, 38, 235), outline=(*accent, 200), width=1)
        draw.text((x + 17, y + 6), tag, font=tag_font, fill=(226, 232, 240))
        x += width + 10

    if loading:
        for i in range(3):
            cx = x + 10 + i * 12
            draw.ellipse((cx, y + 11, cx + 6, y + 17), fill=accent)

    return image.convert("RGB")


def render(filename: str, title: str, subtitle: str, tags: tuple[str, ...], colors) -> None:
    background = build_background(colors)
    frames = []
    for k in range(len(tags) + 1):
        loading = k < len(tags)
        frames.append(draw_card(background, title, subtitle, tags[:k], colors, loading))
    # Hold the fully revealed card before the loop restarts.
    for _ in range(14):
        frames.append(draw_card(background, title, subtitle, tags, colors, False))

    frames[0].save(
        OUT / filename,
        save_all=True,
        append_images=frames[1:],
        duration=[260] * len(tags) + [90] + [140] * 14,
        loop=0,
        optimize=True,
        disposal=2,
    )


OUT.mkdir(parents=True, exist_ok=True)
for card in CARDS:
    render(*card)
    print(f"Wrote {card[0]}")
