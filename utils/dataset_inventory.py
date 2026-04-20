"""Shared dataset inventory helpers for visible OCR inputs."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Iterable


VISIBLE_DOCUMENT_EXTENSIONS = (".jpg", ".jpeg", ".png", ".tif", ".tiff", ".pdf", ".bmp")


def is_visible_document(path: str | Path, extensions: Iterable[str] | None = None) -> bool:
    """Return True when a path is a visible OCR input document."""
    doc_path = Path(path)
    allowed = {ext.lower() for ext in (extensions or VISIBLE_DOCUMENT_EXTENSIONS)}

    return (
        doc_path.is_file()
        and doc_path.suffix.lower() in allowed
        and "ground_truth" not in doc_path.parts
        and not doc_path.name.startswith(".")
        and not any(part.startswith(".") for part in doc_path.parts)
        and "_tmp_" not in str(doc_path)
    )


def find_documents(dataset_dir: str | Path, extensions: Iterable[str] | None = None) -> list[Path]:
    """Recursively find visible OCR input documents under a dataset directory."""
    dataset_path = Path(dataset_dir)
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset directory not found: {dataset_dir}")

    docs: list[Path] = []
    for path in dataset_path.rglob("*"):
        if is_visible_document(path, extensions=extensions):
            docs.append(path)

    return sorted(docs, key=lambda path: str(path))


def get_document_category(doc_path: str | Path) -> str:
    """Extract category from a document path (e.g. ``01_printed_english/invoices``)."""
    parts = Path(doc_path).parts
    for i, part in enumerate(parts):
        if part.startswith(("01_", "02_", "03_", "04_", "05_", "06_", "07_")):
            return "/".join(parts[i:i + 2]) if i + 1 < len(parts) else parts[i]
    return "unknown"


def category_counts(doc_paths: Iterable[str | Path]) -> dict[str, int]:
    """Count visible documents by category."""
    counts = Counter(get_document_category(path) for path in doc_paths)
    return dict(sorted(counts.items()))


def build_manifest(base_dir: str | Path, folders: Iterable[str]) -> tuple[int, dict[str, list[str]]]:
    """Build a visible-input manifest for the requested dataset folders."""
    base_path = Path(base_dir)
    manifest: dict[str, list[str]] = {}
    total = 0

    for folder in folders:
        folder_path = base_path / folder
        files: list[Path] = []
        if folder_path.exists():
            files = [path for path in folder_path.iterdir() if is_visible_document(path)]

        visible_names = sorted(path.name for path in files)
        manifest[folder] = visible_names
        total += len(visible_names)

    return total, manifest
