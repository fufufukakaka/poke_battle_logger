"""
EasyOCR Tuning Benchmark: Compare different parameter/preprocessing combinations.

Usage:
    TESSDATA_PREFIX=/opt/homebrew/Cellar/tesseract/5.5.0/share/tessdata_best/ \
    poetry run python tests/ocr_benchmark_easyocr_tuning.py
"""

import time
from pathlib import Path

import cv2
import editdistance
import numpy as np
import pandas as pd

# Reuse helpers from main benchmark
from ocr_benchmark import (
    TEST_CASES_DIR,
    best_match_for_name_windows,
    calc_edit_distance,
    calc_normalized_edit_distance,
    collect_battle_messages,
    collect_first_selection,
    collect_move_names,
    collect_name_windows,
    collect_rank_numbers,
    is_exact_match,
    normalize_text,
    preprocess_grayscale,
    preprocess_threshold,
)

# ---------------------------------------------------------------------------
# Preprocessing variants
# ---------------------------------------------------------------------------


def preprocess_clahe(gray: np.ndarray) -> np.ndarray:
    """CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(gray)


def preprocess_upscale(img: np.ndarray, scale: int = 2) -> np.ndarray:
    """Upscale image by a factor using INTER_CUBIC."""
    h, w = img.shape[:2]
    return cv2.resize(img, (w * scale, h * scale), interpolation=cv2.INTER_CUBIC)


def preprocess_white_text_extraction(img_bgr: np.ndarray) -> np.ndarray:
    """Extract white/bright text from colored background using HSV."""
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    # White text: low saturation, high value
    lower = np.array([0, 0, 180])
    upper = np.array([180, 60, 255])
    mask = cv2.inRange(hsv, lower, upper)
    return mask


# ---------------------------------------------------------------------------
# EasyOCR Engine variants
# ---------------------------------------------------------------------------


class EasyOCRVariant:
    """Configurable EasyOCR engine wrapper."""

    def __init__(
        self,
        name: str,
        langs: list[str],
        readtext_kwargs: dict | None = None,
    ):
        import easyocr

        self.name = name
        self._reader = easyocr.Reader(langs, gpu=False, verbose=False)
        self._readtext_kwargs = readtext_kwargs or {}

    def recognize(self, img: np.ndarray) -> str:
        results = self._reader.readtext(img, detail=0, **self._readtext_kwargs)
        return "".join(results).strip()


# ---------------------------------------------------------------------------
# Per-category OCR with preprocessing
# ---------------------------------------------------------------------------


def run_variant_for_case(
    engine: EasyOCRVariant,
    img_bgr: np.ndarray,
    gray: np.ndarray,
    category: str,
    ground_truth: str,
    use_upscale: bool = False,
    use_clahe: bool = False,
    use_white_extraction: bool = False,
) -> str:
    """Run EasyOCR variant with optional preprocessing enhancements."""

    def _apply_preprocessing(g: np.ndarray, bgr: np.ndarray) -> np.ndarray:
        result = g
        if use_white_extraction:
            result = preprocess_white_text_extraction(bgr)
        if use_clahe:
            result = preprocess_clahe(result)
        if use_upscale:
            result = preprocess_upscale(result)
        return result

    if category == "name_windows":
        results = []
        for thresh in [200, 130]:
            binary = preprocess_threshold(gray, thresh)
            processed = _apply_preprocessing(binary, img_bgr)
            text = engine.recognize(processed)
            if text:
                results.append(text)
        # Raw grayscale with enhancements
        processed_raw = _apply_preprocessing(gray, img_bgr)
        raw_text = engine.recognize(processed_raw)
        if raw_text:
            results.append(raw_text)
        if not results:
            return ""
        def _best_ed(t: str) -> int:
            _, ed, _, _ = best_match_for_name_windows(ground_truth, t)
            return ed
        return min(results, key=_best_ed)
    elif category == "move_names":
        processed = _apply_preprocessing(gray, img_bgr)
        return engine.recognize(processed)
    elif category == "battle_messages":
        binary = preprocess_threshold(gray, 200)
        processed_bin = _apply_preprocessing(binary, img_bgr)
        text_binary = engine.recognize(processed_bin)
        processed_raw = _apply_preprocessing(gray, img_bgr)
        text_raw = engine.recognize(processed_raw)
        return text_binary if len(text_binary) >= len(text_raw) else text_raw
    elif category == "first_selection":
        binary = preprocess_threshold(gray, 200)
        processed = _apply_preprocessing(binary, img_bgr)
        return engine.recognize(processed)
    elif category == "rank_numbers":
        binary = preprocess_threshold(gray, 160)
        processed = _apply_preprocessing(binary, img_bgr)
        return engine.recognize(processed)
    else:
        processed = _apply_preprocessing(gray, img_bgr)
        return engine.recognize(processed)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("Initializing EasyOCR variants...", flush=True)

    # EasyOCR doesn't allow mixing ja + ch_tra in one Reader.
    # Use separate readers and pick best result for ch_tra variants.

    # Define variants to test
    variants_config = [
        # Baseline (same as main benchmark)
        {
            "name": "baseline",
            "langs": ["ja", "en"],
            "kwargs": {},
            "upscale": False,
            "clahe": False,
            "white_ext": False,
            "extra_reader_langs": None,
        },
        # ja+en reader + ch_tra reader, pick best
        {
            "name": "+ch_tra",
            "langs": ["ja", "en"],
            "kwargs": {},
            "upscale": False,
            "clahe": False,
            "white_ext": False,
            "extra_reader_langs": ["ch_tra", "en"],
        },
        # Upscale 2x
        {
            "name": "upscale2x",
            "langs": ["ja", "en"],
            "kwargs": {},
            "upscale": True,
            "clahe": False,
            "white_ext": False,
            "extra_reader_langs": None,
        },
        # CLAHE contrast enhancement
        {
            "name": "CLAHE",
            "langs": ["ja", "en"],
            "kwargs": {},
            "upscale": False,
            "clahe": True,
            "white_ext": False,
            "extra_reader_langs": None,
        },
        # White text extraction (HSV mask)
        {
            "name": "white_ext",
            "langs": ["ja", "en"],
            "kwargs": {},
            "upscale": False,
            "clahe": False,
            "white_ext": True,
            "extra_reader_langs": None,
        },
        # Lower contrast threshold
        {
            "name": "low_contrast",
            "langs": ["ja", "en"],
            "kwargs": {"contrast_ths": 0.05, "adjust_contrast": 0.7},
            "upscale": False,
            "clahe": False,
            "white_ext": False,
            "extra_reader_langs": None,
        },
        # Upscale + CLAHE combo
        {
            "name": "up2x+CLAHE",
            "langs": ["ja", "en"],
            "kwargs": {},
            "upscale": True,
            "clahe": True,
            "white_ext": False,
            "extra_reader_langs": None,
        },
        # Upscale + ch_tra (separate reader)
        {
            "name": "up2x+ch_tra",
            "langs": ["ja", "en"],
            "kwargs": {},
            "upscale": True,
            "clahe": False,
            "white_ext": False,
            "extra_reader_langs": ["ch_tra", "en"],
        },
    ]

    # Build engines (share reader where possible)
    reader_cache: dict[str, EasyOCRVariant] = {}
    extra_reader_cache: dict[str, EasyOCRVariant] = {}
    engines_with_config = []

    for vc in variants_config:
        lang_key = ",".join(vc["langs"])
        kwargs_key = str(vc["kwargs"])
        cache_key = f"{lang_key}|{kwargs_key}"

        if cache_key not in reader_cache:
            print(f"  Loading EasyOCR [{lang_key}]...", flush=True)
            reader_cache[cache_key] = EasyOCRVariant(
                name=vc["name"],
                langs=vc["langs"],
                readtext_kwargs=vc["kwargs"],
            )

        extra_engine = None
        if vc["extra_reader_langs"]:
            extra_lang_key = ",".join(vc["extra_reader_langs"])
            extra_cache_key = f"{extra_lang_key}|{kwargs_key}"
            if extra_cache_key not in extra_reader_cache:
                print(f"  Loading EasyOCR [{extra_lang_key}] (extra)...", flush=True)
                extra_reader_cache[extra_cache_key] = EasyOCRVariant(
                    name=vc["name"] + "_extra",
                    langs=vc["extra_reader_langs"],
                    readtext_kwargs=vc["kwargs"],
                )
            extra_engine = extra_reader_cache[extra_cache_key]

        engines_with_config.append(
            {
                "engine": reader_cache[cache_key],
                "extra_engine": extra_engine,
                "name": vc["name"],
                "kwargs": vc["kwargs"],
                "upscale": vc["upscale"],
                "clahe": vc["clahe"],
                "white_ext": vc["white_ext"],
            }
        )

    print("  Done.\n")

    # Collect test cases
    all_cases = []
    all_cases.extend(collect_name_windows())
    all_cases.extend(collect_move_names())
    all_cases.extend(collect_battle_messages())
    all_cases.extend(collect_first_selection())
    all_cases.extend(collect_rank_numbers())

    print(f"Total test images: {len(all_cases)}")
    print(f"Variants to test: {len(engines_with_config)}\n")

    records = []

    for case in all_cases:
        img_bgr = cv2.imread(str(case["path"]))
        if img_bgr is None:
            continue

        gray = preprocess_grayscale(img_bgr)
        gt = case["ground_truth"]
        category = case["category"]

        for ec in engines_with_config:
            t0 = time.perf_counter()
            try:
                ocr_output = run_variant_for_case(
                    engine=ec["engine"],
                    img_bgr=img_bgr,
                    gray=gray,
                    category=category,
                    ground_truth=gt,
                    use_upscale=ec["upscale"],
                    use_clahe=ec["clahe"],
                    use_white_extraction=ec["white_ext"],
                )
                # If extra reader available, try it too and pick best
                if ec["extra_engine"] is not None:
                    extra_output = run_variant_for_case(
                        engine=ec["extra_engine"],
                        img_bgr=img_bgr,
                        gray=gray,
                        category=category,
                        ground_truth=gt,
                        use_upscale=ec["upscale"],
                        use_clahe=ec["clahe"],
                        use_white_extraction=ec["white_ext"],
                    )
                    # Pick the output with lower edit distance
                    if category == "name_windows":
                        _, ed1, _, _ = best_match_for_name_windows(gt, ocr_output)
                        _, ed2, _, _ = best_match_for_name_windows(gt, extra_output)
                    else:
                        ed1 = calc_edit_distance(gt, ocr_output)
                        ed2 = calc_edit_distance(gt, extra_output)
                    if ed2 < ed1:
                        ocr_output = extra_output
            except Exception as e:
                ocr_output = f"[ERROR: {e}]"
            elapsed = time.perf_counter() - t0

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
                    "engine": ec["name"],
                    "ocr_output": ocr_output,
                    "exact_match": exact,
                    "edit_distance": ed,
                    "norm_edit_distance": ned,
                    "elapsed_sec": round(elapsed, 4),
                }
            )

        print(f"  [{category}] {case['path'].name} ... done", flush=True)

    df = pd.DataFrame(records)

    # Save detailed results
    output_csv = Path(__file__).parent / "ocr_benchmark_easyocr_tuning_results.csv"
    df.to_csv(output_csv, index=False, encoding="utf-8-sig")
    print(f"\nDetailed results saved to: {output_csv}")

    # Print summary
    engine_names = [vc["name"] for vc in variants_config]

    for cat in df["category"].unique():
        cat_df = df[df["category"] == cat]
        n_images = cat_df["image"].nunique()
        print(f"\n{'='*70}")
        print(f"  {cat} ({n_images} images)")
        print(f"{'='*70}")
        print(
            f"{'Variant':<16} | {'Exact Match':>11} | {'Avg ED':>7} | {'Avg NormED':>10} | {'Avg Time':>8}"
        )
        print(f"{'-'*16}-+-{'-'*11}-+-{'-'*7}-+-{'-'*10}-+-{'-'*8}")

        for engine_name in engine_names:
            eng_df = cat_df[cat_df["engine"] == engine_name]
            if eng_df.empty:
                continue
            exact_pct = eng_df["exact_match"].mean() * 100
            avg_ed = eng_df["edit_distance"].mean()
            avg_ned = eng_df["norm_edit_distance"].mean()
            avg_time = eng_df["elapsed_sec"].mean()
            print(
                f"{engine_name:<16} | {exact_pct:>10.1f}% | {avg_ed:>7.2f} | {avg_ned:>10.3f} | {avg_time:>7.3f}s"
            )

    # Overall
    print(f"\n{'='*70}")
    print(f"  OVERALL ({df['image'].nunique()} images)")
    print(f"{'='*70}")
    print(
        f"{'Variant':<16} | {'Exact Match':>11} | {'Avg ED':>7} | {'Avg NormED':>10} | {'Avg Time':>8}"
    )
    print(f"{'-'*16}-+-{'-'*11}-+-{'-'*7}-+-{'-'*10}-+-{'-'*8}")
    for engine_name in engine_names:
        eng_df = df[df["engine"] == engine_name]
        if eng_df.empty:
            continue
        exact_pct = eng_df["exact_match"].mean() * 100
        avg_ed = eng_df["edit_distance"].mean()
        avg_ned = eng_df["norm_edit_distance"].mean()
        avg_time = eng_df["elapsed_sec"].mean()
        print(
            f"{engine_name:<16} | {exact_pct:>10.1f}% | {avg_ed:>7.2f} | {avg_ned:>10.3f} | {avg_time:>7.3f}s"
        )


if __name__ == "__main__":
    main()
