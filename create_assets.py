from pathlib import Path
from PIL import Image, ImageDraw

def generate_placeholder_logos():
    image_dir = Path("Image")
    image_dir.mkdir(exist_ok=True)

    # Create light logo
    img_light = Image.new("RGBA", (300, 100), (255, 255, 255, 0))
    d1 = ImageDraw.Draw(img_light)
    d1.rectangle([(10, 10), (290, 90)], outline=(40, 40, 40), width=3)
    d1.text((50, 40), "⚖️ LegalEase", fill=(20, 20, 20))
    img_light.save(image_dir / "Logo.png")

    # Create inverse logo for dark mode
    img_dark = Image.new("RGBA", (300, 100), (30, 30, 40, 255))
    d2 = ImageDraw.Draw(img_dark)
    d2.rectangle([(10, 10), (290, 90)], outline=(200, 200, 200), width=3)
    d2.text((50, 40), "⚖️ LegalEase", fill=(255, 255, 255))
    img_dark.save(image_dir / "inverseLogo.png")
    print("Default branding assets generated in Image/ directory.")

if __name__ == "__main__":
    generate_placeholder_logos()