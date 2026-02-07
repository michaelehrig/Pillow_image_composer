from PIL import Image
from pathlib import Path
import argparse

TARGET_IMG_SIZE = 1600
CANVAS_SIZE = (2000, 3000)
BUCKET_NUMBER = 5


def open_copy_delete_png(path):
    # opens the given path and raises ValueError if not of appropriate format
    with Image.open(path) as img:
        if img.format != "PNG":
            raise ValueError(f"{path} is not a PNG file (format={img.format})")
        
        # we convert it with the "RGBA" command to handle transparencies
        img = img.convert("RGBA")

        # load it into memory
        img.load()

        # create a copy of it
        img_copy = img.copy()

    # we unlink the path, so that we can delete the original file
    path.unlink()
    print(f"🗑️  Deleted source file: {path}")

    # we return the loaded copy
    return img_copy


def load_scale_square_png(path, target_size = TARGET_IMG_SIZE):
    # we open and copy the target image
    img = open_copy_delete_png(path)

    # get size of the image
    w, h = img.size
    
    # if the image is not square we raise a ValueError
    if w != h:
        raise ValueError(f"{path} is not square: {w}x{h}")

    # we return the resized png
    return img.resize((target_size, target_size), Image.LANCZOS)


def save_as_jpeg_on_white(img_rgba, output_path, quality = 95):
    # We make sure that our image is in "RGBA" mode
    if img_rgba.mode != "RGBA":
        img_rgba = img_rgba.convert("RGBA")

    # We create a white background
    white_bg = Image.new("RGB", img_rgba.size, (255, 255, 255))
    
    # we paste our image onto the white background using transparency
    white_bg.paste(img_rgba, (0, 0), img_rgba)  

    # Then we save the whole composition as a JPEG
    white_bg.save(output_path, format="JPEG", quality=quality, subsampling=0, optimize=True)


def compose_images(front_path, back_path, output_path):
    # We load our front side image
    front = load_scale_square_png(front_path)
    
    # We load our back side image
    back = load_scale_square_png(back_path)

    # We create a canvas to compose the two images on
    canvas = Image.new("RGB", CANVAS_SIZE, (255, 255, 255))

    # Paste front side image on the top left
    canvas.paste(front, (0, 0), front)

    # Paste back side image on the bottom right
    canvas.paste(
        back,
        (CANVAS_SIZE[0] - TARGET_IMG_SIZE, CANVAS_SIZE[1] - TARGET_IMG_SIZE),
        back,
    )

    # Save the result as a JPEG
    canvas.save(output_path, format="JPEG", quality=95, subsampling=0, optimize=True)


def first_match(directory, pattern):
    # Look for the first element in the directory that matches the pattern
    return next(directory.glob(pattern), None)


def find_third_action_png(subdir):
    # Look for a png that does not start with "front" or "back"
    for p in subdir.glob("*.png"):
        name = p.name.lower()
        if not (name.startswith("front") or name.startswith("back")):
            # If found return its path
            return p
    # Otherwise return None
    return None


def process_directory(output_base):
    # We declare our source and output directories
    src_root = Path("src")
    out_dir = Path("out")
    
    # Making sure that the output exists
    out_dir.mkdir(parents=True, exist_ok=True)

    # We go through our subdirectories, they are just numbered
    for i in range(1, BUCKET_NUMBER + 1):
        subdir = src_root / str(i)
        # If the directory does not exist, we let the user know
        if not subdir.exists():
            print(f"⚠️  Missing directory: {subdir}, skipping.")
            continue

        # We get the path for our front and back side images
        front_path = first_match(subdir, "Front*.png")
        back_path = first_match(subdir, "Back*.png")

        # If we do not find both, we let the user know and skip
        if front_path is None or back_path is None:
            print(f"⚠️  Missing front/back in {subdir}, skipping composite.")
        else:
            # If we find it compose the two images via our function compose_images
            promo_out = out_dir / f"{output_base}_PROMOTIONAL_{i}.jpg"
            print(f"✔️  src/{i}: composing Front+Back -> {promo_out.name}")
            compose_images(front_path, back_path, promo_out)

        # Then we look whether we can find the action shot
        action_path = find_third_action_png(subdir)
        if action_path is None:
            print(f"⚠️  No action PNG found in {subdir}, skipping action.")
            continue

        # If we found it, we get it, delete the original
        action_img = open_copy_delete_png(action_path)
        w, h = action_img.size
        
        # Scale our version by 50%
        new_size = (max(1, w // 2), max(1, h // 2))  # 50% scale
        action_img = action_img.resize(new_size, Image.LANCZOS)

        # We give it a name and save it as a jpeg
        action_out = out_dir / f"{output_base}_PROMOTIONAL_ACTION_{i}.jpg"
        print(f"✔️  src/{i}: saving action (50%) -> {action_out.name}")
        save_as_jpeg_on_white(action_img, action_out)


def main():
    parser = argparse.ArgumentParser(
        description="Create promotional composites + action shot from src subfolders; delete source PNGs after loading."
    )
    parser.add_argument(
        "OUTPUT",
        help="Base name for output files (e.g. PRODUCT_XYZ)",
    )
    args = parser.parse_args()
    process_directory(args.OUTPUT)


if __name__ == "__main__":
    main()
