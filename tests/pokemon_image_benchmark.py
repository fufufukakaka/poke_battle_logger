"""
Pokemon Image Recognition Benchmark: DINOv2 + FAISS vs SwinV2 Classifier.

Splits template images into reference (index) and query (test) sets,
then compares recognition accuracy between:
  1. DINOv2-Small (frozen embeddings) + FAISS cosine similarity
  2. SwinV2-base classifier (fufufukakaka/pokemon_image_classifier)

Usage:
    poetry run python tests/pokemon_image_benchmark.py
"""

import glob
import random
import time
from collections import defaultdict
from pathlib import Path

import cv2
import faiss
import numpy as np
import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModel, pipeline

random.seed(42)

TEMPLATE_DIRS = [
    "template_images/labeled_pokemon_templates",
    "template_images/user_labeled_pokemon_templates",
]


# ---------------------------------------------------------------------------
# Data collection
# ---------------------------------------------------------------------------


def collect_all_images() -> dict[str, list[str]]:
    """Collect all template images grouped by Pokemon name."""
    images_by_name: dict[str, list[str]] = defaultdict(list)
    for template_dir in TEMPLATE_DIRS:
        for path in glob.glob(f"{template_dir}/*/*.png"):
            name = path.split("/")[-2]
            images_by_name[name].append(path)
    return dict(images_by_name)


def split_train_test(
    images_by_name: dict[str, list[str]],
) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Split images: hold out 1 image per Pokemon (if >=2 images) for testing."""
    train: dict[str, list[str]] = {}
    test: dict[str, list[str]] = {}

    for name, paths in images_by_name.items():
        if len(paths) < 2:
            # Only 1 image: use for reference only, skip testing
            train[name] = paths
            continue
        shuffled = paths.copy()
        random.shuffle(shuffled)
        test[name] = [shuffled[0]]
        train[name] = shuffled[1:]

    return train, test


# ---------------------------------------------------------------------------
# DINOv2 engine
# ---------------------------------------------------------------------------


class DINOv2Engine:
    """DINOv2-Small embeddings + FAISS cosine similarity search."""

    def __init__(self) -> None:
        model_name = "facebook/dinov2-small"
        print(f"  Loading DINOv2-Small ({model_name})...")
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval()
        self.index: faiss.IndexFlatIP | None = None
        self.labels: list[str] = []

    def _embed(self, img_bgr: np.ndarray) -> np.ndarray:
        """Compute normalized embedding for a single image."""
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        inputs = self.processor(images=pil_img, return_tensors="pt")
        with torch.no_grad():
            outputs = self.model(**inputs)
        # Use CLS token embedding
        embedding = outputs.last_hidden_state[:, 0, :].squeeze().numpy()
        # L2 normalize for cosine similarity
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        return embedding.astype(np.float32)

    def build_index(self, train_data: dict[str, list[str]]) -> None:
        """Build FAISS index from training images."""
        embeddings = []
        self.labels = []
        for name, paths in train_data.items():
            for path in paths:
                img = cv2.imread(path)
                if img is None:
                    continue
                emb = self._embed(img)
                embeddings.append(emb)
                self.labels.append(name)

        emb_array = np.array(embeddings)
        dim = emb_array.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # Inner product (cosine for normalized)
        self.index.add(emb_array)
        print(f"  FAISS index built: {len(self.labels)} vectors, dim={dim}")

    def predict(self, img_bgr: np.ndarray, top_k: int = 5) -> list[tuple[str, float]]:
        """Predict Pokemon name from image using FAISS search."""
        assert self.index is not None
        emb = self._embed(img_bgr).reshape(1, -1)
        scores, indices = self.index.search(emb, top_k)
        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0:
                continue
            results.append((self.labels[idx], float(scores[0][i])))
        return results


# ---------------------------------------------------------------------------
# SwinV2 engine
# ---------------------------------------------------------------------------


class SwinV2Engine:
    """SwinV2-base classifier from HuggingFace."""

    def __init__(self) -> None:
        model_name = "fufufukakaka/pokemon_image_classifier"
        print(f"  Loading SwinV2 classifier ({model_name})...")
        self.pipe = pipeline(
            task="image-classification",
            model=model_name,
            model_kwargs={"ignore_mismatched_sizes": True},
            framework="pt",
            device="cpu",
        )
        # Get the label set
        self.known_labels = set(self.pipe.model.config.id2label.values())
        print(f"  SwinV2 knows {len(self.known_labels)} Pokemon classes")

    def predict(
        self, img_bgr: np.ndarray, top_k: int = 5
    ) -> list[tuple[str, float]]:
        """Predict Pokemon name from image."""
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        pil_img = Image.fromarray(img_rgb)
        results = self.pipe(pil_img, top_k=top_k)
        return [(r["label"], r["score"]) for r in results]

    def is_known(self, name: str) -> bool:
        """Check if a Pokemon name is in the SwinV2 training set."""
        return name in self.known_labels


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------


def evaluate_engine(
    engine_name: str,
    predict_fn,
    test_data: dict[str, list[str]],
    known_filter_fn=None,
) -> dict:
    """Evaluate an engine on test data."""
    results = {
        "total": 0,
        "top1_correct": 0,
        "top3_correct": 0,
        "top5_correct": 0,
        "total_time": 0.0,
        "errors": [],
    }

    for gt_name, paths in test_data.items():
        for path in paths:
            img = cv2.imread(path)
            if img is None:
                continue

            results["total"] += 1
            t0 = time.perf_counter()
            try:
                predictions = predict_fn(img, top_k=5)
            except Exception as e:
                results["errors"].append((path, str(e)))
                continue
            elapsed = time.perf_counter() - t0
            results["total_time"] += elapsed

            pred_names = [p[0] for p in predictions]
            top1_score = predictions[0][1] if predictions else 0.0

            if pred_names and pred_names[0] == gt_name:
                results["top1_correct"] += 1
            if gt_name in pred_names[:3]:
                results["top3_correct"] += 1
            if gt_name in pred_names[:5]:
                results["top5_correct"] += 1

    return results


def print_results(engine_name: str, results: dict, subset_label: str = "") -> None:
    """Print evaluation results."""
    total = results["total"]
    if total == 0:
        print(f"  {engine_name}: no test samples")
        return

    label = f"{engine_name} {subset_label}".strip()
    top1 = results["top1_correct"] / total * 100
    top3 = results["top3_correct"] / total * 100
    top5 = results["top5_correct"] / total * 100
    avg_time = results["total_time"] / total * 1000  # ms

    print(
        f"  {label:<45s} | "
        f"Top-1: {top1:5.1f}% | "
        f"Top-3: {top3:5.1f}% | "
        f"Top-5: {top5:5.1f}% | "
        f"n={total:3d} | "
        f"Avg: {avg_time:.0f}ms"
    )
    if results["errors"]:
        print(f"    Errors: {len(results['errors'])}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 80)
    print("  Pokemon Image Recognition Benchmark: DINOv2 vs SwinV2")
    print("=" * 80)

    # Collect and split data
    print("\n--- Data ---")
    all_images = collect_all_images()
    train_data, test_data = split_train_test(all_images)
    n_train = sum(len(v) for v in train_data.values())
    n_test = sum(len(v) for v in test_data.values())
    print(f"  Pokemon species: {len(all_images)}")
    print(f"  Reference images: {n_train}")
    print(f"  Test images: {n_test} ({len(test_data)} species)")

    # Initialize engines
    print("\n--- Loading models ---")
    dino_engine = DINOv2Engine()
    swin_engine = SwinV2Engine()

    # Build DINOv2 FAISS index
    print("\n--- Building DINOv2 FAISS index ---")
    t0 = time.perf_counter()
    dino_engine.build_index(train_data)
    index_time = time.perf_counter() - t0
    print(f"  Index build time: {index_time:.1f}s")

    # Evaluate both on ALL test data
    print("\n--- Evaluation: All test Pokemon ---")
    print(f"{'':45s} | {'Top-1':>11s} | {'Top-3':>11s} | {'Top-5':>11s} | {'n':>5s} | {'Speed':>8s}")
    print("-" * 110)

    dino_results_all = evaluate_engine(
        "DINOv2", dino_engine.predict, test_data
    )
    print_results("DINOv2-Small + FAISS", dino_results_all, "(all)")

    swin_results_all = evaluate_engine(
        "SwinV2", swin_engine.predict, test_data
    )
    print_results("SwinV2-base classifier", swin_results_all, "(all)")

    # Evaluate on the subset that SwinV2 actually knows
    swin_known_test = {
        name: paths
        for name, paths in test_data.items()
        if swin_engine.is_known(name)
    }
    swin_unknown_test = {
        name: paths
        for name, paths in test_data.items()
        if not swin_engine.is_known(name)
    }
    n_known = sum(len(v) for v in swin_known_test.values())
    n_unknown = sum(len(v) for v in swin_unknown_test.values())
    print(f"\n  SwinV2 knows {n_known}/{n_test} test images ({len(swin_known_test)} species)")
    print(f"  SwinV2 does NOT know {n_unknown} test images ({len(swin_unknown_test)} species)")

    # Fair comparison: only Pokemon both can recognize
    print(f"\n--- Evaluation: SwinV2-known Pokemon only ({len(swin_known_test)} species) ---")
    print(f"{'':45s} | {'Top-1':>11s} | {'Top-3':>11s} | {'Top-5':>11s} | {'n':>5s} | {'Speed':>8s}")
    print("-" * 110)

    dino_known = evaluate_engine(
        "DINOv2", dino_engine.predict, swin_known_test
    )
    print_results("DINOv2-Small + FAISS", dino_known, "(swin-known)")

    swin_known = evaluate_engine(
        "SwinV2", swin_engine.predict, swin_known_test
    )
    print_results("SwinV2-base classifier", swin_known, "(swin-known)")

    # DINOv2 on Pokemon that SwinV2 doesn't know
    if swin_unknown_test:
        print(f"\n--- DINOv2 on SwinV2-unknown Pokemon ({len(swin_unknown_test)} species) ---")
        dino_unknown = evaluate_engine(
            "DINOv2", dino_engine.predict, swin_unknown_test
        )
        print_results("DINOv2-Small + FAISS", dino_unknown, "(swin-unknown)")

    # Some specific error examples
    print("\n--- DINOv2 misclassification examples (top-1 wrong) ---")
    for gt_name, paths in list(test_data.items()):
        for path in paths:
            img = cv2.imread(path)
            if img is None:
                continue
            preds = dino_engine.predict(img, top_k=3)
            if preds and preds[0][0] != gt_name:
                pred_str = ", ".join(f"{p[0]}({p[1]:.3f})" for p in preds[:3])
                print(f"  GT: {gt_name:<15s} → Predicted: {pred_str}")

    print("\n" + "=" * 80)
    print("  Benchmark complete.")
    print("=" * 80)


if __name__ == "__main__":
    main()
