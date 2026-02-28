"""
OCR Engine Benchmark: Tesseract vs EasyOCR vs RapidOCR

Usage:
    poetry run python tests/ocr_benchmark.py
"""

import os
import sys
import time
from pathlib import Path
from typing import Optional

import cv2
import editdistance
import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Test data root
# ---------------------------------------------------------------------------
TEST_CASES_DIR = Path(__file__).parent / "ocr_test_cases"
DATA_DIR = Path(__file__).parent.parent / "data"

# ---------------------------------------------------------------------------
# Multi-language Pokemon name lookup
# ---------------------------------------------------------------------------
LANG_COLUMNS = ["en", "ja", "fr", "de", "es", "it", "ko", "zh_HK", "zh"]


def load_pokemon_name_lookup() -> dict[str, list[str]]:
    """Build a lookup: Japanese name -> list of all language variants."""
    df = pd.read_csv(DATA_DIR / "pokemon_name_multi_language.csv")
    lookup: dict[str, list[str]] = {}
    for _, row in df.iterrows():
        ja_name = row["ja"]
        variants = [str(row[col]) for col in LANG_COLUMNS if pd.notna(row[col])]
        lookup[ja_name] = variants
    return lookup


# Global lookup (loaded once)
_POKEMON_NAME_LOOKUP: dict[str, list[str]] | None = None


def get_pokemon_name_lookup() -> dict[str, list[str]]:
    global _POKEMON_NAME_LOOKUP
    if _POKEMON_NAME_LOOKUP is None:
        _POKEMON_NAME_LOOKUP = load_pokemon_name_lookup()
    return _POKEMON_NAME_LOOKUP

# ---------------------------------------------------------------------------
# Engine wrappers
# ---------------------------------------------------------------------------


class TesseractEngine:
    name = "Tesseract"

    def __init__(self) -> None:
        import pytesseract  # noqa: F811

        self._pytesseract = pytesseract

    def recognize(
        self, img: np.ndarray, lang: str = "eng+jpn", psm: int = 6
    ) -> str:
        text: str = self._pytesseract.image_to_string(
            img, lang=lang, config=f"--psm {psm}"
        )
        return text.replace("\n", "").strip()


class EasyOCREngine:
    name = "EasyOCR"

    def __init__(self) -> None:
        import easyocr

        self._reader = easyocr.Reader(["ja", "en"], gpu=False, verbose=False)

    def recognize(
        self, img: np.ndarray, lang: str = "", psm: int = 6
    ) -> str:
        results = self._reader.readtext(img, detail=0)
        return "".join(results).strip()


class RapidOCREngine:
    name = "RapidOCR"

    def __init__(self) -> None:
        from rapidocr_onnxruntime import RapidOCR

        self._engine = RapidOCR()

    def recognize(
        self, img: np.ndarray, lang: str = "", psm: int = 6
    ) -> str:
        result, _ = self._engine(img)
        if result is None:
            return ""
        texts = [r[1] for r in result]
        return "".join(texts).strip()


# ---------------------------------------------------------------------------
# Preprocessing helpers (matching existing pipeline)
# ---------------------------------------------------------------------------


def preprocess_grayscale(img: np.ndarray) -> np.ndarray:
    if len(img.shape) == 3:
        return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    return img


def preprocess_threshold(gray: np.ndarray, threshold: int) -> np.ndarray:
    _, binary = cv2.threshold(gray, threshold, 255, cv2.THRESH_BINARY)
    return binary


# ---------------------------------------------------------------------------
# Evaluation helpers
# ---------------------------------------------------------------------------


def normalize_text(text: str) -> str:
    """Strip whitespace and common OCR artifacts for comparison."""
    return text.replace(" ", "").replace("\u3000", "").replace("|", "").strip()


def calc_edit_distance(ground_truth: str, ocr_output: str) -> int:
    return editdistance.eval(normalize_text(ground_truth), normalize_text(ocr_output))


def calc_normalized_edit_distance(ground_truth: str, ocr_output: str) -> float:
    gt = normalize_text(ground_truth)
    out = normalize_text(ocr_output)
    max_len = max(len(gt), len(out))
    if max_len == 0:
        return 0.0
    return editdistance.eval(gt, out) / max_len


def is_exact_match(ground_truth: str, ocr_output: str) -> bool:
    return normalize_text(ground_truth) == normalize_text(ocr_output)


def best_match_for_name_windows(
    ja_name: str, ocr_output: str
) -> tuple[str, int, float, bool]:
    """For name_windows: find the best matching language variant.

    Returns (best_gt, edit_distance, norm_edit_distance, exact_match).
    """
    lookup = get_pokemon_name_lookup()
    variants = lookup.get(ja_name, [ja_name])
    out = normalize_text(ocr_output)

    best_gt = ja_name
    best_ed = calc_edit_distance(ja_name, ocr_output)
    best_ned = calc_normalized_edit_distance(ja_name, ocr_output)
    best_exact = is_exact_match(ja_name, ocr_output)

    for variant in variants:
        v = normalize_text(variant)
        ed = editdistance.eval(v, out)
        max_len = max(len(v), len(out))
        ned = ed / max_len if max_len > 0 else 0.0
        exact = v == out
        if ed < best_ed or (ed == best_ed and exact):
            best_gt = variant
            best_ed = ed
            best_ned = ned
            best_exact = exact

    return best_gt, best_ed, round(best_ned, 3), best_exact


# ---------------------------------------------------------------------------
# Benchmark runners per category
# ---------------------------------------------------------------------------


def collect_name_windows() -> list[dict]:
    """name_windows/{pokemon_name}/*.png → ground_truth = dir name"""
    cases = []
    base = TEST_CASES_DIR / "name_windows"
    if not base.exists():
        return cases
    for pokemon_dir in sorted(base.iterdir()):
        if not pokemon_dir.is_dir():
            continue
        gt = pokemon_dir.name
        for img_path in sorted(pokemon_dir.glob("*.png")):
            cases.append({"path": img_path, "ground_truth": gt, "category": "name_windows"})
    return cases


def collect_move_names() -> list[dict]:
    """move_names/*.png and move_names/champions/*.png → ground_truth = filename stem"""
    cases = []
    base = TEST_CASES_DIR / "move_names"
    if not base.exists():
        return cases
    for img_path in sorted(base.glob("*.png")):
        cases.append({"path": img_path, "ground_truth": img_path.stem, "category": "move_names"})
    champ = base / "champions"
    if champ.exists():
        for img_path in sorted(champ.glob("*.png")):
            cases.append({"path": img_path, "ground_truth": img_path.stem, "category": "move_names"})
    return cases


def collect_battle_messages() -> list[dict]:
    cases = []
    base = TEST_CASES_DIR / "battle_messages"
    if not base.exists():
        return cases
    for img_path in sorted(base.glob("*.png")):
        cases.append({"path": img_path, "ground_truth": img_path.stem, "category": "battle_messages"})
    champ = base / "champions"
    if champ.exists():
        for img_path in sorted(champ.glob("*.png")):
            cases.append({"path": img_path, "ground_truth": img_path.stem, "category": "battle_messages"})
    return cases


def collect_first_selection() -> list[dict]:
    cases = []
    base = TEST_CASES_DIR / "first_selection"
    if not base.exists():
        return cases
    for img_path in sorted(base.glob("*.png")):
        cases.append({"path": img_path, "ground_truth": img_path.stem, "category": "first_selection"})
    return cases


def collect_rank_numbers() -> list[dict]:
    cases = []
    base = TEST_CASES_DIR / "rank_numbers"
    if not base.exists():
        return cases
    for img_path in sorted(base.glob("*.png")):
        cases.append({"path": img_path, "ground_truth": img_path.stem, "category": "rank_numbers"})
    return cases


# ---------------------------------------------------------------------------
# Per-category OCR strategy
# ---------------------------------------------------------------------------


def run_tesseract_for_case(
    engine: TesseractEngine, gray: np.ndarray, category: str, ground_truth: str
) -> str:
    if category == "name_windows":
        # Try jpn, eng, chi_sim, chi_tra with two thresholds
        results = []
        for lang in ["jpn", "eng", "chi_sim", "chi_tra"]:
            for thresh in [200, 130]:
                binary = preprocess_threshold(gray, thresh)
                text = engine.recognize(binary, lang=lang, psm=6)
                results.append(text)
        # Pick result with lowest edit distance against all language variants
        def _best_ed(t: str) -> int:
            _, ed, _, _ = best_match_for_name_windows(ground_truth, t)
            return ed
        best = min(results, key=_best_ed)
        return best
    elif category == "move_names":
        return engine.recognize(gray, lang="eng+jpn", psm=6)
    elif category == "battle_messages":
        binary = preprocess_threshold(gray, 200)
        return engine.recognize(binary, lang="eng+jpn", psm=6)
    elif category == "first_selection":
        binary = preprocess_threshold(gray, 200)
        # Detect language from ground truth
        is_japanese = any(ord(c) > 0x3000 for c in ground_truth)
        if is_japanese:
            return engine.recognize(binary, lang="jpn", psm=8)
        else:
            return engine.recognize(binary, lang="eng", psm=6)
    elif category == "rank_numbers":
        binary = preprocess_threshold(gray, 160)
        return engine.recognize(binary, lang="eng", psm=6)
    else:
        return engine.recognize(gray, lang="eng+jpn", psm=6)


def run_generic_for_case(
    engine, gray: np.ndarray, category: str, ground_truth: str = ""
) -> str:
    """EasyOCR / RapidOCR — apply same preprocessing but engine handles language internally."""
    if category == "name_windows":
        results = []
        for thresh in [200, 130]:
            binary = preprocess_threshold(gray, thresh)
            text = engine.recognize(binary)
            if text:
                results.append(text)
        # Also try raw grayscale (these engines may work better without thresholding)
        raw_text = engine.recognize(gray)
        if raw_text:
            results.append(raw_text)
        if not results:
            return ""
        # Pick result with lowest edit distance against all language variants
        def _best_ed(t: str) -> int:
            _, ed, _, _ = best_match_for_name_windows(ground_truth, t)
            return ed
        return min(results, key=_best_ed)
    elif category == "move_names":
        return engine.recognize(gray)
    elif category == "battle_messages":
        binary = preprocess_threshold(gray, 200)
        # Try both preprocessed and raw
        text_binary = engine.recognize(binary)
        text_raw = engine.recognize(gray)
        return text_binary if len(text_binary) >= len(text_raw) else text_raw
    elif category == "first_selection":
        binary = preprocess_threshold(gray, 200)
        return engine.recognize(binary)
    elif category == "rank_numbers":
        binary = preprocess_threshold(gray, 160)
        return engine.recognize(binary)
    else:
        return engine.recognize(gray)


# ---------------------------------------------------------------------------
# Main benchmark
# ---------------------------------------------------------------------------


def run_benchmark() -> pd.DataFrame:
    print("Initializing OCR engines...")
    print("  Loading Tesseract...", flush=True)
    tesseract = TesseractEngine()
    print("  Loading EasyOCR (first run downloads models)...", flush=True)
    easyocr_engine = EasyOCREngine()
    print("  Loading RapidOCR...", flush=True)
    rapidocr_engine = RapidOCREngine()
    print("  Done.\n")

    engines = [tesseract, easyocr_engine, rapidocr_engine]

    # Collect all test cases
    all_cases = []
    all_cases.extend(collect_name_windows())
    all_cases.extend(collect_move_names())
    all_cases.extend(collect_battle_messages())
    all_cases.extend(collect_first_selection())
    all_cases.extend(collect_rank_numbers())

    print(f"Total test images: {len(all_cases)}\n")

    records = []

    for case in all_cases:
        img = cv2.imread(str(case["path"]))
        if img is None:
            print(f"  [WARN] Could not read: {case['path']}")
            continue

        gray = preprocess_grayscale(img)
        gt = case["ground_truth"]
        category = case["category"]

        for engine in engines:
            t0 = time.perf_counter()
            try:
                if isinstance(engine, TesseractEngine):
                    ocr_output = run_tesseract_for_case(engine, gray, category, gt)
                else:
                    ocr_output = run_generic_for_case(engine, gray, category, gt)
            except Exception as e:
                ocr_output = f"[ERROR: {e}]"
            elapsed = time.perf_counter() - t0

            # For name_windows, evaluate against all language variants
            if category == "name_windows":
                matched_gt, ed, ned, exact = best_match_for_name_windows(gt, ocr_output)
            else:
                matched_gt = gt
                ed = calc_edit_distance(gt, ocr_output)
                ned = round(calc_normalized_edit_distance(gt, ocr_output), 3)
                exact = is_exact_match(gt, ocr_output)

            records.append(
                {
                    "category": category,
                    "image": case["path"].name,
                    "ground_truth": gt,
                    "matched_variant": matched_gt,
                    "engine": engine.name,
                    "ocr_output": ocr_output,
                    "exact_match": exact,
                    "edit_distance": ed,
                    "norm_edit_distance": ned,
                    "elapsed_sec": round(elapsed, 4),
                }
            )

        # Progress indicator
        print(f"  [{category}] {case['path'].name} ... done", flush=True)

    return pd.DataFrame(records)


def print_summary(df: pd.DataFrame) -> None:
    categories = df["category"].unique()

    for cat in categories:
        cat_df = df[df["category"] == cat]
        n_images = cat_df["image"].nunique()
        print(f"\n{'='*60}")
        print(f"  {cat} ({n_images} images)")
        print(f"{'='*60}")
        print(
            f"{'Engine':<12} | {'Exact Match':>11} | {'Avg EditDist':>12} | {'Avg NormED':>10} | {'Avg Time':>8}"
        )
        print(f"{'-'*12}-+-{'-'*11}-+-{'-'*12}-+-{'-'*10}-+-{'-'*8}")

        for engine_name in ["Tesseract", "EasyOCR", "RapidOCR"]:
            eng_df = cat_df[cat_df["engine"] == engine_name]
            if eng_df.empty:
                continue
            exact_pct = eng_df["exact_match"].mean() * 100
            avg_ed = eng_df["edit_distance"].mean()
            avg_ned = eng_df["norm_edit_distance"].mean()
            avg_time = eng_df["elapsed_sec"].mean()
            print(
                f"{engine_name:<12} | {exact_pct:>10.1f}% | {avg_ed:>12.2f} | {avg_ned:>10.3f} | {avg_time:>7.3f}s"
            )

    # Overall
    print(f"\n{'='*60}")
    print(f"  OVERALL ({df['image'].nunique()} images)")
    print(f"{'='*60}")
    print(
        f"{'Engine':<12} | {'Exact Match':>11} | {'Avg EditDist':>12} | {'Avg NormED':>10} | {'Avg Time':>8}"
    )
    print(f"{'-'*12}-+-{'-'*11}-+-{'-'*12}-+-{'-'*10}-+-{'-'*8}")
    for engine_name in ["Tesseract", "EasyOCR", "RapidOCR"]:
        eng_df = df[df["engine"] == engine_name]
        if eng_df.empty:
            continue
        exact_pct = eng_df["exact_match"].mean() * 100
        avg_ed = eng_df["edit_distance"].mean()
        avg_ned = eng_df["norm_edit_distance"].mean()
        avg_time = eng_df["elapsed_sec"].mean()
        print(
            f"{engine_name:<12} | {exact_pct:>10.1f}% | {avg_ed:>12.2f} | {avg_ned:>10.3f} | {avg_time:>7.3f}s"
        )


def print_mismatches(df: pd.DataFrame) -> None:
    """Print cases where at least one engine got it wrong for analysis."""
    print(f"\n{'='*60}")
    print("  DETAILED MISMATCHES (per category)")
    print(f"{'='*60}")

    for cat in df["category"].unique():
        cat_df = df[df["category"] == cat]
        images_with_errors = cat_df[~cat_df["exact_match"]]["image"].unique()
        if len(images_with_errors) == 0:
            print(f"\n  [{cat}] All engines matched perfectly!")
            continue

        print(f"\n  [{cat}] {len(images_with_errors)} images with errors:")
        for img_name in images_with_errors:
            img_df = cat_df[cat_df["image"] == img_name]
            gt = img_df["ground_truth"].iloc[0]
            # Show matched variant if different from ground truth
            variants_info = ""
            if "matched_variant" in img_df.columns:
                variants = img_df["matched_variant"].unique()
                non_gt = [v for v in variants if v != gt]
                if non_gt:
                    variants_info = f"  [best match variants: {', '.join(non_gt)}]"
            print(f"\n    {img_name}  (GT: {gt}){variants_info}")
            for _, row in img_df.iterrows():
                marker = "OK" if row["exact_match"] else "NG"
                variant_note = ""
                if "matched_variant" in row and row["matched_variant"] != gt:
                    variant_note = f" → vs {row['matched_variant']}"
                print(
                    f"      [{marker}] {row['engine']:<12}: {row['ocr_output']!r}  (ed={row['edit_distance']}{variant_note})"
                )


def main() -> None:
    df = run_benchmark()

    # Save detailed results
    output_csv = Path(__file__).parent / "ocr_benchmark_results.csv"
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"\nDetailed results saved to: {output_csv}")

    # Print summary tables
    print_summary(df)
    print_mismatches(df)


if __name__ == "__main__":
    main()
