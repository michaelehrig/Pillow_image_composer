from PIL import Image
from pathlib import Path

TARGET_IMG_SIZE = 1600
CANVAS_SIZE = (2000, 3000)


def load_and_scale_square_png(path, target_size=TARGET_IMG_SIZE):
    img = Image.open(path)

    if img.format != "PNG":
        raise ValueError(f"{path} is not a PNG file")

    w, h = img.size
    if w != h:
        raise ValueError(f"{path} is not square: {w}x{h}")

    return img.resize((target_size, target_size), Image.LANCZOS)


def compose_images(img1_path, img2_path, output_path):
    img1 = load_and_scale_square_png(img1_path)
    img2 = load_and_scale_square_png(img2_path)

    canvas = Image.new("RGB", CANVAS_SIZE, (255, 255, 255))

    top_left_pos = (0, 0)
    bottom_right_pos = (
        CANVAS_SIZE[0] - TARGET_IMG_SIZE,
        CANVAS_SIZE[1] - TARGET_IMG_SIZE,
    )

    canvas.paste(img1, top_left_pos, img1 if img1.mode == "RGBA" else None)
    canvas.paste(img2, bottom_right_pos, img2 if img2.mode == "RGBA" else None)

    canvas.save(
        output_path,
        format="JPEG",
        quality=95,
        subsampling=0,
        optimize=True,
    )


def process_directory():
    src_dir = Path("src")
    out_dir = Path("out")

    # Ensure output directory exists
    out_dir.mkdir(parents=True, exist_ok=True)

    fronts = {}

    # Collect all Front_2_<NAME>.png files
    for file in src_dir.glob("Front 2, *.png"):
        name = file.stem.replace("Front 2, ", "")
        fronts[name] = file

    # Look for matching Back_2_<NAME>.png files
    for name, front_path in fronts.items():
        back_path = src_dir / f"Back 2, {name}.png"

        if not back_path.exists():
            print(f"⚠️  Missing back image for '{name}', skipping.")
            continue

        output_path = out_dir / f"Promotional_{name}.jpg"

        print(f"✔️  Creating composite for '{name}'")
        compose_images(
            img1_path=front_path,
            img2_path=back_path,
            output_path=output_path,
        )


if __name__ == "__main__":
    process_directory()

