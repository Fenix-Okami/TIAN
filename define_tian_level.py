from __future__ import annotations

"""
Utility to determine Tian level for HSK 2025 vocab/hanzi inputs.

Given a word/character, prints its Tian level (1-3) based on the existing
HSK lists under references/HSK-3.0/New HSK (2025).
"""

from pathlib import Path
from typing import List, Dict

from hsk_csv_utils import LEVELS, WORDS_DIR, HANZI_DIR, read_entries


def build_index() -> Dict[str, int]:
    index: Dict[str, int] = {}
    # Vocab
    for level in LEVELS:
        vocab_path = WORDS_DIR / f"HSK_Level_{level}_words.txt"
        if vocab_path.exists():
            for w in read_entries(vocab_path):
                index.setdefault(w, level)
    # Hanzi
    for level in LEVELS:
        hanzi_path = HANZI_DIR / f"HSK_Level_{level}_hanzi.txt"
        if hanzi_path.exists():
            for h in read_entries(hanzi_path):
                index.setdefault(h, level)
    return index


def define_tian_level(terms: List[str]) -> None:
    index = build_index()
    for term in terms:
        level = index.get(term)
        print(f"{term}: {level if level is not None else 'not found'}")


def main() -> None:
    import sys

    if len(sys.argv) < 2:
        print("Usage: python define_tian_level.py <term1> [<term2> ...]")
        sys.exit(1)
    define_tian_level(sys.argv[1:])


if __name__ == "__main__":
    main()
