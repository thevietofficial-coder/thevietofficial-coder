"""Render clean, readable horizontal toolkit cards for the GitHub profile README."""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "toolkit-cards"
FONT = "C:/Windows/Fonts/segoeuib.ttf"
W, H = 1080, 190

CARDS = (
    (
        "toolkit-ai-ml.png",
        "AI & Machine Learning",
        "MODELS, RETRIEVAL, AND GENERATIVE AI APPLICATIONS",
        ("Python", "PyTorch", "TensorFlow", "Keras", "scikit-learn", "NumPy", "Pandas", "Matplotlib", "OpenCV", "CUDA"),
        "#22d3ee",
    ),
    (
        "toolkit-languages-web.png",
        "Languages & Web",
        "CORE LANGUAGES AND WEB DELIVERY",
        ("C++", "Java", "JavaScript", "Next.js", "WordPress"),
        "#a78bfa",
    ),
    (
        "toolkit-tools-hardware.png",
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


def render(filename: str, title: str, subtitle: str, tags: tuple[str, ...], accent: str) -> None:
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

    image.save(OUT / filename, optimize=True)


OUT.mkdir(parents=True, exist_ok=True)
for card in CARDS:
    render(*card)
    print(f"Wrote {card[0]}")
