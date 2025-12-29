from __future__ import annotations

import importlib
from typing import Dict, List

from hsk_csv_utils import HANZI_DIR, LEVELS, OUTPUT_DIR, read_entries, write_csv


def load_decomposer():
    try:
        decomposer_mod = importlib.import_module("hanzipy.decomposer")
        return decomposer_mod.HanziDecomposer
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "hanzipy is required but not available. "
            "Install dependencies in the project venv: "
            "./venv/Scripts/python.exe -m pip install -r requirements.txt\n"
            f"Original error: {exc}"
        )


def extract_radicals(hanzi: str, decomposer) -> List[str]:
    decomposition = decomposer.decompose(hanzi, 2)
    if not isinstance(decomposition, dict):
        return []
    components = decomposition.get("components") or decomposition.get("radical")
    if not isinstance(components, list):
        return []
    cleaned = [c for c in components if c and c != "No glyph available"]
    return list(dict.fromkeys(cleaned))


def build_radicals_csv() -> None:
    HanziDecomposer = load_decomposer()
    decomposer = HanziDecomposer()

    counts: Dict[str, Dict[str, int]] = {}

    for level in LEVELS:
        source = HANZI_DIR / f"HSK_Level_{level}_hanzi.txt"
        entries = read_entries(source)
        for hanzi in entries:
            for radical in extract_radicals(hanzi, decomposer):
                record = counts.setdefault(radical, {"hsk1": 0, "hsk2": 0, "hsk3": 0})
                record[f"hsk{level}"] += 1

    rows: List[Dict[str, object]] = []
    for radical, record in counts.items():
        h1 = record["hsk1"]
        h2 = record["hsk2"]
        h3 = record["hsk3"]
        tian_level = 1 if h1 else 2 if h2 else 3
        productivity = h1 * 5 + h2 * 3 + h3
        radical_name = decomposer.get_radical_meaning(radical) or ""
        rows.append(
            {
                "radical": radical,
                "tian_level": tian_level,
                "radical_name": radical_name,
                "hsk1_occurance": h1,
                "hsk2_occurance": h2,
                "hsk3_occurance": h3,
                "productivity score": productivity,
            }
        )

    rows.sort(key=lambda r: (-r["productivity score"], r["radical"]))

    write_csv(
        rows,
        [
            "radical",
            "tian_level",
            "radical_name",
            "hsk1_occurance",
            "hsk2_occurance",
            "hsk3_occurance",
            "productivity score",
        ],
        OUTPUT_DIR / "radicals_levels_1_3.csv",
    )


def main() -> None:
    build_radicals_csv()


if __name__ == "__main__":
    main()
