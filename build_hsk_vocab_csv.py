from __future__ import annotations

from typing import Dict, List

from hsk_csv_utils import LEVELS, OUTPUT_DIR, WORDS_DIR, read_entries, write_csv


def build_vocabulary_csv() -> None:
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
                    "pinyin": "",
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
