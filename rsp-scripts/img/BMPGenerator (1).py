from PIL import Image
from pathlib import Path

# OLED resolution (change ONLY if your display is different)
WIDTH = 128
HEIGHT = 32

BASE_DIR = Path(__file__).resolve().parent
INPUT_IMAGE = BASE_DIR / "inputs" / "neutral.jpg"
OUTPUT_IMAGE = BASE_DIR / "neutral_oled.png"


def convert_for_oled(input_path, output_path, width, height):
    # Load image
    img = Image.open(input_path)

    # Convert to grayscale first (important for good dithering)
    img = img.convert("L")

    # Resize to OLED resolution
    img = img.resize((width, height), Image.LANCZOS)

    # Convert to 1-bit with dithering
    img = img.convert("1")  # default Floyd–Steinberg dithering

    # Save result
    img.save(output_path)

    print(f"Saved OLED-compatible image: {output_path}")


if __name__ == "__main__":
    convert_for_oled(INPUT_IMAGE, OUTPUT_IMAGE, WIDTH, HEIGHT)
