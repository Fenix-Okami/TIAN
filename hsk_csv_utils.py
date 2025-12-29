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


TONE_MARKS = {
    "a": ["ā", "á", "ǎ", "à"],
    "e": ["ē", "é", "ě", "è"],
    "i": ["ī", "í", "ǐ", "ì"],
    "o": ["ō", "ó", "ǒ", "ò"],
    "u": ["ū", "ú", "ǔ", "ù"],
    "ü": ["ǖ", "ǘ", "ǚ", "ǜ"],
}


def numbered_pinyin_to_tone_marks(pinyin: str) -> str:
    """Convert numbered pinyin (e.g. 'xue3') to tone marks (e.g. 'xuě').

    Supports whitespace-separated syllables and 'u:' for 'ü'.
    """

    def convert_syllable(syllable: str) -> str:
        if not syllable:
            return syllable

        syllable = syllable.replace("u:", "ü").replace("U:", "Ü")

        tone = 5
        if syllable[-1].isdigit():
            tone = int(syllable[-1])
            syllable = syllable[:-1]

        if tone in (0, 5):
            return syllable

        lower = syllable.lower()
        vowels = "aeiouü"
        vowel_positions = [i for i, ch in enumerate(lower) if ch in vowels]
        if not vowel_positions:
            return syllable

        # Tone placement rules:
        # - If 'a' or 'e' present, mark the first of those.
        # - Else if 'ou' present, mark the 'o'.
        # - Else for 'iu' mark 'u', for 'ui' mark 'i'.
        # - Else mark the last vowel.
        mark_index = None
        for v in ("a", "e"):
            idx = lower.find(v)
            if idx != -1:
                mark_index = idx
                break
        if mark_index is None and "ou" in lower:
            mark_index = lower.find("o")
        if mark_index is None and "iu" in lower:
            mark_index = lower.find("u")
        if mark_index is None and "ui" in lower:
            mark_index = lower.find("i")
        if mark_index is None:
            mark_index = vowel_positions[-1]

        ch = lower[mark_index]
        marked = TONE_MARKS.get(ch, [ch, ch, ch, ch])[tone - 1]
        # Preserve original case of the vowel being replaced
        if syllable[mark_index].isupper():
            marked = marked.upper()

        return syllable[:mark_index] + marked + syllable[mark_index + 1 :]

    return " ".join(convert_syllable(s) for s in pinyin.split())


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
