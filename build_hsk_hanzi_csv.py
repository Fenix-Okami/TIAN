from __future__ import annotations

from typing import Dict, List

from hsk_csv_utils import HANZI_DIR, LEVELS, OUTPUT_DIR, read_entries, write_csv


def build_hanzi_csv() -> None:
    rows: List[Dict[str, object]] = []
    for level in LEVELS:
        source = HANZI_DIR / f"HSK_Level_{level}_hanzi.txt"
        entries = read_entries(source)
        for hanzi in entries:
            rows.append(
                {
                    "hanzi": hanzi,
                    "tian_level": level,
                    "hsk_level": level,
                    "pinyin": "",
                    "meaning": "",
                    "meaning_mnemonic": "",
                    "reading_mnemonic": "",
                    "components": "",
                    "in_names": "",
                }
            )
    write_csv(
        rows,
        [
            "hanzi",
            "tian_level",
            "hsk_level",
            "pinyin",
            "meaning",
            "meaning_mnemonic",
            "reading_mnemonic",
            "components",
            "in_names",
        ],
        OUTPUT_DIR / "hanzi_levels_1_3.csv",
    )


def main() -> None:
    build_hanzi_csv()


if __name__ == "__main__":
    main()
