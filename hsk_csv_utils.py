from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable, List, Dict

# Shared utilities/constants for generating HSK 2025 CSV outputs.

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "references" / "HSK-3.0" / "New HSK (2025)"
HANZI_DIR = DATA_DIR / "HSK Hanzi"
WORDS_DIR = DATA_DIR / "HSK Words"
OUTPUT_DIR = BASE_DIR / "output"

LEVELS: List[int] = [1, 2, 3]


def read_entries(path: Path) -> List[str]:
    """Return non-empty, stripped lines from a UTF-8 text file."""
    with path.open(encoding="utf-8") as handle:
        return [line.strip() for line in handle if line.strip()]


def write_csv(rows: Iterable[Dict[str, object]], headers: List[str], path: Path) -> None:
    """Write rows to CSV with the given headers."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
