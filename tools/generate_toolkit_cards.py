"""Render animated horizontal toolkit cards for the GitHub profile README.

Each card's skill tags pop in one by one, hold fully revealed, then loop.
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "toolkit-cards"
FONT = "C:/Windows/Fonts/segoeuib.ttf"
W, H = 1080, 190

CARDS = (
    (
        "toolkit-ai-ml.gif",
        "AI & Machine Learning",
        "MODELS, RETRIEVAL, AND GENERATIVE AI APPLICATIONS",
        ("Python", "PyTorch", "TensorFlow", "Keras", "scikit-learn", "NumPy", "Pandas", "Matplotlib", "OpenCV"),
        "#22d3ee",
    ),
    (
        "toolkit-languages-web.gif",
        "Languages & Web",
        "CORE LANGUAGES AND WEB DELIVERY",
        ("C++", "Java", "JavaScript", "Next.js", "WordPress"),
        "#a78bfa",
    ),
    (
        "toolkit-tools-hardware.gif",
        "Tools, Design & Hardware",
        "BUILD, VERSION, DESIGN, AND DEPLOY TO THE EDGE",
        ("Git", "GitHub", "Photoshop", "Canva", "Raspberry Pi"),
        "#f59e0b",
    ),
)


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size)


def tag_width(draw: ImageDraw.ImageDraw, value: str, tag_font: ImageFont.FreeTypeFont) -> int:
    return int(draw.textbbox((0, 0), value, font=tag_font)[2]) + 34


def draw_card(title: str, subtitle: str, tags: tuple[str, ...], accent: str, loading: bool) -> Image.Image:
    image = Image.new("RGB", (W, H), "#07111f")
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((1, 1, W - 2, H - 2), radius=22, outline="#1e506c", width=2)
    draw.rounded_rectangle((28, 29, 37, 77), radius=4, fill=accent)
    draw.text((58, 25), title, font=font(29), fill="#f8fafc")
    draw.text((60, 66), subtitle, font=font(13), fill="#94a3b8")

    tag_font = font(16)
    x, y = 32, 111
    for tag in tags:
        width = tag_width(draw, tag, tag_font)
        if x + width > W - 32:
            x, y = 32, y + 42
        draw.rounded_rectangle((x, y, x + width, y + 30), radius=15, fill="#0d2235", outline="#1d4f69", width=1)
        draw.text((x + 17, y + 6), tag, font=tag_font, fill="#dbeafe")
        x += width + 10

    if loading:
        for i in range(3):
            cx = x + 10 + i * 12
            draw.ellipse((cx, y + 11, cx + 6, y + 17), fill=accent)

    return image


def render(filename: str, title: str, subtitle: str, tags: tuple[str, ...], accent: str) -> None:
    frames = []
    for k in range(len(tags) + 1):
        loading = k < len(tags)
        frames.append(draw_card(title, subtitle, tags[:k], accent, loading))
    # Hold the fully revealed card before the loop restarts.
    for _ in range(14):
        frames.append(draw_card(title, subtitle, tags, accent, False))

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
