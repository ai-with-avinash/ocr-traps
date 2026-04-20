"""Evaluation metrics for OCR output comparison.

Implements standard OCR evaluation metrics with proper text normalization,
Counter-based token matching, and error decomposition (S/I/D).

Changes from original:
- F1 uses Counter (bag-of-words with multiplicity), not set
- Added precision and recall as separate fields
- Added substitution/insertion/deletion rate decomposition
- Added normalize_ocr_text() for Unicode NFKC + markdown stripping
- Removed BLEU (inappropriate for OCR evaluation)
- Added word_accuracy (1 - WER, floored at 0)
"""

import re
import unicodedata
from collections import Counter
from dataclasses import dataclass
from typing import Optional


# ---------------------------------------------------------------------------
# Text normalization
# ---------------------------------------------------------------------------

_MD_PATTERNS = [
    (re.compile(r"^\#{1,6}\s+", re.MULTILINE), ""),         # markdown headings
    (re.compile(r"^[\-\*\_]{3,}$", re.MULTILINE), ""),       # horizontal rules (before bold/italic)
    (re.compile(r"\*{1,3}(.+?)\*{1,3}"), r"\1"),            # bold/italic
    (re.compile(r"`(.+?)`"), r"\1"),                         # inline code
    (re.compile(r"!\[.*?\]\(.*?\)"), ""),                    # images
    (re.compile(r"\[(.+?)\]\(.*?\)"), r"\1"),                # links
    (re.compile(r"^\|.*\|$", re.MULTILINE), ""),             # table rows
    (re.compile(r"^[\-\|:\s]+$", re.MULTILINE), ""),         # table separators
    (re.compile(r"^\s*[\-\*\+]\s+", re.MULTILINE), ""),      # list bullets
    (re.compile(r"^\s*\d+\.\s+", re.MULTILINE), ""),         # numbered lists
    (re.compile(r"<[^>]+>"), ""),                             # HTML tags
    (re.compile(r"&amp;"), "&"),                              # HTML entities
    (re.compile(r"&lt;"), "<"),
    (re.compile(r"&gt;"), ">"),
]


def normalize_ocr_text(text: str) -> str:
    """Normalize OCR text for fair metric comparison.

    Steps:
    1. Unicode NFKC normalization (critical for Devanagari and accented chars)
    2. Strip markdown/HTML formatting artifacts
    3. Collapse whitespace
    4. Strip leading/trailing whitespace
    """
    if not text:
        return ""

    # Unicode NFKC normalization
    text = unicodedata.normalize("NFKC", text)

    # Strip markdown/HTML formatting
    for pattern, replacement in _MD_PATTERNS:
        text = pattern.sub(replacement, text)

    # Collapse whitespace (newlines, tabs, multiple spaces → single space)
    text = " ".join(text.split())

    return text.strip()


# ---------------------------------------------------------------------------
# Metrics dataclass
# ---------------------------------------------------------------------------

@dataclass
class MetricsResult:
    """Computed metrics for one document + model pair."""
    doc_path: str
    model_name: str
    cer: Optional[float] = None               # Character Error Rate (lower is better)
    wer: Optional[float] = None               # Word Error Rate (lower is better)
    word_accuracy: Optional[float] = None     # 1 - WER, floored at 0 (higher is better)
    edit_dist: Optional[float] = None         # Normalized edit distance 0–1 (lower is better)
    f1: Optional[float] = None                # Token-level F1 with multiplicity (higher is better)
    precision: Optional[float] = None         # Token-level precision (higher is better)
    recall: Optional[float] = None            # Token-level recall (higher is better)
    char_count_pred: int = 0
    char_count_gt: int = 0
    word_count_pred: int = 0
    word_count_gt: int = 0
    # Error decomposition
    char_substitutions: int = 0
    char_insertions: int = 0
    char_deletions: int = 0
    substitution_rate: Optional[float] = None  # S / len(gt)
    insertion_rate: Optional[float] = None     # I / len(gt)
    deletion_rate: Optional[float] = None      # D / len(gt)

    def to_dict(self) -> dict:
        return {k: round(v, 4) if isinstance(v, float) and v is not None else v
                for k, v in self.__dict__.items()}


# ---------------------------------------------------------------------------
# Individual metrics
# ---------------------------------------------------------------------------

def compute_cer(prediction: str, ground_truth: str) -> float:
    """Character Error Rate using Levenshtein distance."""
    from rapidfuzz.distance import Levenshtein
    if not ground_truth:
        return 0.0 if not prediction else 1.0
    dist = Levenshtein.distance(prediction, ground_truth)
    return dist / max(len(ground_truth), 1)


def compute_wer(prediction: str, ground_truth: str) -> float:
    """Word Error Rate using Levenshtein distance on word sequences."""
    from rapidfuzz.distance import Levenshtein
    pred_words = prediction.split()
    gt_words = ground_truth.split()
    if not gt_words:
        return 0.0 if not pred_words else 1.0
    dist = Levenshtein.distance(pred_words, gt_words)
    return dist / max(len(gt_words), 1)


def compute_edit_distance(prediction: str, ground_truth: str) -> float:
    """Normalized edit distance (0 = identical, 1 = completely different)."""
    from rapidfuzz.distance import Levenshtein
    if not ground_truth and not prediction:
        return 0.0
    dist = Levenshtein.distance(prediction, ground_truth)
    return dist / max(len(prediction), len(ground_truth), 1)


def compute_error_decomposition(prediction: str, ground_truth: str) -> tuple[int, int, int]:
    """Decompose character-level edit operations into substitutions, insertions, deletions.

    Uses rapidfuzz editops. In rapidfuzz's convention:
    - "replace": character at src_pos was substituted
    - "delete": character at src_pos in prediction has no match in GT (insertion error)
    - "insert": character at dest_pos in GT has no match in prediction (deletion error)

    Returns:
        (substitutions, insertions, deletions) counts from the OCR perspective:
        - substitutions: characters recognized incorrectly
        - insertions: characters in prediction that shouldn't be there (hallucinated)
        - deletions: characters in GT missing from prediction
    """
    from rapidfuzz.distance import Levenshtein
    if not ground_truth and not prediction:
        return 0, 0, 0

    editops = Levenshtein.editops(prediction, ground_truth)
    subs, ins, dels = 0, 0, 0
    for op in editops:
        if op.tag == "replace":
            subs += 1
        elif op.tag == "delete":
            # pred has extra char not in GT → insertion error
            ins += 1
        elif op.tag == "insert":
            # GT has char missing from pred → deletion error
            dels += 1
    return subs, ins, dels


def compute_f1(prediction: str, ground_truth: str) -> tuple[float, float, float]:
    """Token-level F1 score using Counter (bag-of-words with multiplicity).

    Unlike set-based F1, this correctly handles duplicate tokens and reflects
    the actual word frequency distribution.

    Returns:
        (f1, precision, recall)
    """
    pred_tokens = Counter(prediction.lower().split())
    gt_tokens = Counter(ground_truth.lower().split())

    if not gt_tokens:
        return (1.0, 1.0, 1.0) if not pred_tokens else (0.0, 0.0, 0.0)
    if not pred_tokens:
        return (0.0, 0.0, 0.0)

    # True positives: sum of min counts for each shared token
    shared_keys = set(pred_tokens.keys()) & set(gt_tokens.keys())
    tp = sum(min(pred_tokens[k], gt_tokens[k]) for k in shared_keys)

    pred_total = sum(pred_tokens.values())
    gt_total = sum(gt_tokens.values())

    precision = tp / pred_total if pred_total > 0 else 0.0
    recall = tp / gt_total if gt_total > 0 else 0.0

    if precision + recall == 0:
        return (0.0, 0.0, 0.0)

    f1 = 2 * precision * recall / (precision + recall)
    return (f1, precision, recall)


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def compute_all_metrics(prediction: str, ground_truth: str,
                        doc_path: str = "", model_name: str = "") -> MetricsResult:
    """Compute all metrics for a prediction/ground truth pair.

    Text is normalized (Unicode NFKC, markdown stripping, whitespace collapse)
    before metric computation.
    """
    pred = normalize_ocr_text(prediction)
    gt = normalize_ocr_text(ground_truth)

    cer = compute_cer(pred, gt)
    wer = compute_wer(pred, gt)
    f1, precision, recall = compute_f1(pred, gt)
    subs, ins, dels = compute_error_decomposition(pred, gt)
    gt_len = max(len(gt), 1)

    return MetricsResult(
        doc_path=doc_path,
        model_name=model_name,
        cer=cer,
        wer=wer,
        word_accuracy=max(1.0 - wer, 0.0),
        edit_dist=compute_edit_distance(pred, gt),
        f1=f1,
        precision=precision,
        recall=recall,
        char_count_pred=len(pred),
        char_count_gt=len(gt),
        word_count_pred=len(pred.split()),
        word_count_gt=len(gt.split()),
        char_substitutions=subs,
        char_insertions=ins,
        char_deletions=dels,
        substitution_rate=subs / gt_len,
        insertion_rate=ins / gt_len,
        deletion_rate=dels / gt_len,
    )
