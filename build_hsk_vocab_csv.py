from __future__ import annotations

import csv
from typing import Dict, List

from hsk_csv_utils import (
    LEVELS,
    OUTPUT_DIR,
    WORDS_DIR,
    numbered_pinyin_to_tone_marks,
    read_entries,
    write_csv,
)


ANKI_DIR = WORDS_DIR.parent / "Anki xiehanzi"


def unique_preserve_order(values: List[str]) -> List[str]:
    return list(dict.fromkeys(values))


def is_name_pinyin(pinyin: str) -> bool:
    return bool(pinyin) and pinyin[0].isalpha() and pinyin[0].isupper()


def load_anki_pinyin(levels: List[int]) -> Dict[str, List[str]]:
    mapping: Dict[str, List[str]] = {}
    for level in levels:
        path = ANKI_DIR / f"HSK_Level_{level}.txt"
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as handle:
            reader = csv.reader(handle, delimiter="\t")
            for row in reader:
                if len(row) < 3:
                    continue
                simp, trad, pinyin = row[0].strip(), row[1].strip(), row[2].strip()
                if pinyin:
                    mapping.setdefault(simp, []).append(pinyin)
                    if trad:
                        mapping.setdefault(trad, []).append(pinyin)
    return mapping


def normalize_vocab_key(word: str) -> str:
    # Drop trailing digits like "本1" -> "本"
    i = len(word)
    while i > 0 and word[i - 1].isdigit():
        i -= 1
    return word[:i] if i != len(word) else word


def col_pinyin_from_map(word: str, pinyin_map: Dict[str, List[str]]) -> str:
    key = normalize_vocab_key(word)
    raw = pinyin_map.get(key) or pinyin_map.get(word) or []
    if not raw:
        return ""
    lowered = [p.lower() for p in raw]
    converted = [numbered_pinyin_to_tone_marks(p) for p in lowered]
    unique = unique_preserve_order([p for p in converted if p])
    return ";".join(unique)


def build_vocabulary_csv() -> None:
    pinyin_map = load_anki_pinyin(LEVELS)

    rows: List[Dict[str, object]] = []
    for level in LEVELS:
        source = WORDS_DIR / f"HSK_Level_{level}_words.txt"
        entries = read_entries(source)
        for vocab in entries:
            rows.append(
                {
                    "vocab": vocab,
                    "tian_level": level,
                    "hsk_level": level,
                    "pinyin": col_pinyin_from_map(vocab, pinyin_map),
                    "meaning": "",
                    "meaning_mnemonic": "",
                    "reading_mnemonic": "",
                    "components": "",
                    "example_sentences": "",
                }
            )
    write_csv(
        rows,
        [
            "vocab",
            "tian_level",
            "hsk_level",
            "pinyin",
            "meaning",
            "meaning_mnemonic",
            "reading_mnemonic",
            "components",
            "example_sentences",
        ],
        OUTPUT_DIR / "vocabulary_levels_1_3.csv",
    )


def main() -> None:
    build_vocabulary_csv()


if __name__ == "__main__":
    main()
