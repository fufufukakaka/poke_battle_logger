"""
Proof of Concept: Synthetic OCR training data generation for Pokemon Champions.

Uses actual Champions game screenshots as background templates, then renders
new text with free fonts (BIZ UDGothic / Noto Sans CJK JP) to create
EasyOCR fine-tuning data.

Usage:
    poetry run python tests/synthetic_data_poc.py
"""

import io
import random
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

SCRIPT_DIR = Path(__file__).parent
FONTS_DIR = SCRIPT_DIR / "fonts"
TEST_CASES_DIR = SCRIPT_DIR / "ocr_test_cases"
OUTPUT_DIR = SCRIPT_DIR / "synthetic_data_poc_output"

# Fonts
FONT_BOLD = str(FONTS_DIR / "BIZUDGothic-Bold.ttf")
FONT_REGULAR = str(FONTS_DIR / "NotoSansCJKjp-Regular.otf")
FONT_NOTO_BOLD = str(FONTS_DIR / "NotoSansCJKjp-Bold.otf")


# ---------------------------------------------------------------------------
# Background extraction from real Champions images
# ---------------------------------------------------------------------------


def extract_background_from_name_window(img_path: Path) -> Image.Image:
    """Extract background by inpainting text region from a name window image."""
    img_bgr = cv2.imread(str(img_path))
    if img_bgr is None:
        raise FileNotFoundError(f"Cannot read {img_path}")
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    # Detect bright text pixels (white text on darker background)
    _, mask = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY)
    # Dilate mask slightly to cover anti-aliased edges
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    # Inpaint
    result = cv2.inpaint(img_bgr, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))


def extract_background_from_battle_message(img_path: Path) -> Image.Image:
    """Extract background from battle message image."""
    img_bgr = cv2.imread(str(img_path))
    if img_bgr is None:
        raise FileNotFoundError(f"Cannot read {img_path}")
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 160, 255, cv2.THRESH_BINARY)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    result = cv2.inpaint(img_bgr, mask, inpaintRadius=7, flags=cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))


def extract_background_from_move_name(img_path: Path) -> Image.Image:
    """Extract background from move name image."""
    img_bgr = cv2.imread(str(img_path))
    if img_bgr is None:
        raise FileNotFoundError(f"Cannot read {img_path}")
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    kernel = np.ones((3, 3), np.uint8)
    mask = cv2.dilate(mask, kernel, iterations=1)
    result = cv2.inpaint(img_bgr, mask, inpaintRadius=5, flags=cv2.INPAINT_TELEA)
    return Image.fromarray(cv2.cvtColor(result, cv2.COLOR_BGR2RGB))


# ---------------------------------------------------------------------------
# Synthetic image generators
# ---------------------------------------------------------------------------


def generate_name_window(
    text: str,
    bg_image: Image.Image,
    font_path: str = FONT_BOLD,
    target_width: int = 180,
    target_height: int = 55,
) -> Image.Image:
    """Generate a synthetic Pokemon name window image."""
    # Resize background to target size
    bg = bg_image.resize((target_width, target_height), Image.LANCZOS).convert("RGBA")

    # Draw text
    draw = ImageDraw.Draw(bg)

    # Auto-size font to fit the image
    font_size = int(target_height * 0.55)
    font = ImageFont.truetype(font_path, font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    # Center text
    x_pos = (target_width - text_w) // 2
    y_pos = (target_height - text_h) // 2 - 2  # slight upward offset

    # Subtle shadow
    draw.text((x_pos + 1, y_pos + 1), text, fill=(0, 0, 0, 100), font=font)
    # Main text (white)
    draw.text((x_pos, y_pos), text, fill=(255, 255, 255, 255), font=font)

    return bg.convert("RGB")


def generate_battle_message(
    text: str,
    bg_image: Image.Image,
    font_path: str = FONT_REGULAR,
    target_width: int = 888,
    target_height: int = 158,
) -> Image.Image:
    """Generate a synthetic battle message image."""
    bg = bg_image.resize((target_width, target_height), Image.LANCZOS).convert("RGBA")
    draw = ImageDraw.Draw(bg)

    font_size = int(target_height * 0.28)
    font = ImageFont.truetype(font_path, font_size)

    # Left-aligned with padding
    x_pos = int(target_width * 0.03)
    y_pos = int(target_height * 0.25)

    # Shadow
    draw.text((x_pos + 1, y_pos + 1), text, fill=(0, 0, 0, 80), font=font)
    # Main text
    draw.text((x_pos, y_pos), text, fill=(255, 255, 255, 255), font=font)

    return bg.convert("RGB")


def generate_move_name(
    text: str,
    bg_image: Image.Image,
    font_path: str = FONT_REGULAR,
    target_width: int = 170,
    target_height: int = 44,
) -> Image.Image:
    """Generate a synthetic move name image."""
    bg = bg_image.resize((target_width, target_height), Image.LANCZOS).convert("RGBA")
    draw = ImageDraw.Draw(bg)

    font_size = int(target_height * 0.5)
    font = ImageFont.truetype(font_path, font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    x_pos = (target_width - text_w) // 2
    y_pos = (target_height - text_h) // 2 - 1

    draw.text((x_pos, y_pos), text, fill=(255, 255, 255, 255), font=font)

    return bg.convert("RGB")


# ---------------------------------------------------------------------------
# Augmentation
# ---------------------------------------------------------------------------


def augment_image(img: Image.Image) -> Image.Image:
    """Add realistic variation to a synthetic image."""
    # Brightness variation
    enhancer = ImageEnhance.Brightness(img)
    img = enhancer.enhance(random.uniform(0.88, 1.12))

    # Slight blur (simulating video compression)
    if random.random() < 0.3:
        img = img.filter(ImageFilter.GaussianBlur(radius=random.uniform(0.3, 0.7)))

    # JPEG compression artifacts
    if random.random() < 0.4:
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=random.randint(75, 95))
        buffer.seek(0)
        img = Image.open(buffer).copy()

    return img


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    # --- 1. Collect background templates from Champions images ---
    print("=== Extracting backgrounds from Champions images ===\n")

    name_window_bgs = []
    for p in sorted((TEST_CASES_DIR / "name_windows" / "champions").glob("*.png")):
        try:
            bg = extract_background_from_name_window(p)
            name_window_bgs.append(bg)
            print(f"  [name_window bg] {p.name}: {bg.size}")
        except Exception as e:
            print(f"  [SKIP] {p.name}: {e}")

    battle_msg_bgs = []
    for p in sorted((TEST_CASES_DIR / "battle_messages" / "champions").glob("*.png")):
        try:
            bg = extract_background_from_battle_message(p)
            battle_msg_bgs.append(bg)
            print(f"  [battle_msg bg] {p.name}: {bg.size}")
        except Exception as e:
            print(f"  [SKIP] {p.name}: {e}")

    move_name_bgs = []
    for p in sorted((TEST_CASES_DIR / "move_names" / "champions").glob("*.png")):
        try:
            bg = extract_background_from_move_name(p)
            move_name_bgs.append(bg)
            print(f"  [move_name bg] {p.name}: {bg.size}")
        except Exception as e:
            print(f"  [SKIP] {p.name}: {e}")

    # --- 2. Generate synthetic images ---
    print("\n=== Generating synthetic images ===\n")

    # Sample Pokemon names (mix of Japanese and English)
    pokemon_names_ja = [
        "ガブリアス", "ミロカロス", "サーナイト", "サザンドラ",
        "ヤドラン", "ハバタクカミ", "テツノツツミ", "カイリュー",
        "ウーラオス", "オーガポン", "パオジアン", "ランドロス",
    ]
    pokemon_names_en = [
        "Garchomp", "Milotic", "Gardevoir", "Hydreigon",
        "Slowbro", "Oranguru", "Ursaluna", "Dragonite",
        "Urshifu", "Ogerpon", "Chien-Pao", "Landorus",
    ]

    # Sample move names
    move_names_ja = [
        "シャドーボール", "ムーンフォース", "こごえるかぜ", "ワイドフォース",
        "りゅうせいぐん", "あくのはどう", "じしん", "かえんほうしゃ",
        "れいとうビーム", "10まんボルト", "サイコキネシス", "エナジーボール",
    ]

    # Sample battle messages
    battle_msgs = [
        "Garchomp used Rock Slide!",
        "Go! Garchomp and Milotic!",
        "It's super effective!",
        "The opposing Hydreigon fainted!",
        "Gardevoir used Moonblast!",
        "ガブリアスのいわなだれ！",
        "相手のサザンドラは倒れた！",
        "サーナイトのムーンフォース！",
    ]

    labels = []
    img_idx = 0

    # Generate name windows
    all_names = pokemon_names_ja + pokemon_names_en
    for name in all_names:
        for variation in range(3):  # 3 variations per name
            bg = random.choice(name_window_bgs) if name_window_bgs else None
            if bg is None:
                continue
            font = FONT_BOLD if any(ord(c) > 0x3000 for c in name) else FONT_NOTO_BOLD
            img = generate_name_window(name, bg, font_path=font)
            img = augment_image(img)
            fname = f"name_{img_idx:05d}.png"
            img.save(OUTPUT_DIR / fname)
            labels.append(f"{fname}\t{name}")
            img_idx += 1

    n_name = img_idx
    print(f"  Name windows: {n_name} images")

    # Generate move names
    for move in move_names_ja:
        for variation in range(3):
            bg = random.choice(move_name_bgs) if move_name_bgs else None
            if bg is None:
                continue
            img = generate_move_name(move, bg)
            img = augment_image(img)
            fname = f"move_{img_idx:05d}.png"
            img.save(OUTPUT_DIR / fname)
            labels.append(f"{fname}\t{move}")
            img_idx += 1

    n_move = img_idx - n_name
    print(f"  Move names: {n_move} images")

    # Generate battle messages
    for msg in battle_msgs:
        for variation in range(3):
            bg = random.choice(battle_msg_bgs) if battle_msg_bgs else None
            if bg is None:
                continue
            font = FONT_REGULAR if any(ord(c) > 0x3000 for c in msg) else FONT_REGULAR
            img = generate_battle_message(msg, bg, font_path=font)
            img = augment_image(img)
            fname = f"msg_{img_idx:05d}.png"
            img.save(OUTPUT_DIR / fname)
            labels.append(f"{fname}\t{msg}")
            img_idx += 1

    n_msg = img_idx - n_name - n_move
    print(f"  Battle messages: {n_msg} images")

    # --- 3. Save labels ---
    labels_path = OUTPUT_DIR / "labels.txt"
    labels_path.write_text("\n".join(labels) + "\n", encoding="utf-8")

    print(f"\n=== Summary ===")
    print(f"Total: {img_idx} images")
    print(f"Labels: {labels_path}")
    print(f"Output dir: {OUTPUT_DIR}")

    # --- 4. Visual comparison ---
    print("\n=== Comparison: Real vs Synthetic ===")
    print("(Open the output directory to compare side-by-side)")

    # Copy a few real images for comparison
    comparison_dir = OUTPUT_DIR / "comparison"
    comparison_dir.mkdir(exist_ok=True)

    import shutil
    real_examples = [
        TEST_CASES_DIR / "name_windows" / "champions" / "サーナイト.png",
        TEST_CASES_DIR / "name_windows" / "champions" / "Oranguru.png",
        TEST_CASES_DIR / "move_names" / "champions" / "シャドーボール.png",
        TEST_CASES_DIR / "battle_messages" / "champions" / "Garchomp used Rock Slide!.png",
    ]
    for src in real_examples:
        if src.exists():
            shutil.copy2(src, comparison_dir / f"REAL_{src.name}")

    print(f"Real images copied to: {comparison_dir}")
    print("Done!")


if __name__ == "__main__":
    main()
