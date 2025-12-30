from __future__ import annotations

import importlib
import math
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


def load_hanzi_components(decomposer) -> Dict[str, List[str]]:
    mapping: Dict[str, List[str]] = {}
    for level in LEVELS:
        source = HANZI_DIR / f"HSK_Level_{level}_hanzi.txt"
        if not source.exists():
            continue
        for hanzi in read_entries(source):
            comps = extract_radicals(hanzi, decomposer)
            if comps:
                mapping[hanzi] = comps
    return mapping


def build_radicals_csv() -> None:
    HanziDecomposer = load_decomposer()
    decomposer = HanziDecomposer()

    hanzi_components = load_hanzi_components(decomposer)

    counts: Dict[str, Dict[str, int]] = {}

    for level in LEVELS:
        source = HANZI_DIR / f"HSK_Level_{level}_hanzi.txt"
        entries = read_entries(source)
        for hanzi in entries:
            for radical in extract_radicals(hanzi, decomposer):
                record = counts.setdefault(radical, {"hsk1": 0, "hsk2": 0, "hsk3": 0})
                record[f"hsk{level}"] += 1

    radicals_sorted = sorted(
        counts.items(),
        key=lambda kv: (
            -(kv[1]["hsk1"] * 5 + kv[1]["hsk2"] * 3 + kv[1]["hsk3"]),
            kv[0],
        ),
    )

    introduced: set[str] = set()
    unlocked_hanzi: set[str] = set()
    raw_level_map: Dict[str, int] = {}
    target_per_level = 15

    for radical, record in radicals_sorted:
        introduced.add(radical)
        for hanzi, comps in hanzi_components.items():
            if hanzi in unlocked_hanzi:
                continue
            if set(comps).issubset(introduced):
                unlocked_hanzi.add(hanzi)
        raw_level = (len(unlocked_hanzi) + target_per_level - 1) // target_per_level
        raw_level_map[radical] = max(1, raw_level)

    max_raw_level = max(raw_level_map.values()) if raw_level_map else 1

    rows: List[Dict[str, object]] = []
    for radical, record in radicals_sorted:
        h1 = record["hsk1"]
        h2 = record["hsk2"]
        h3 = record["hsk3"]
        productivity = h1 * 5 + h2 * 3 + h3
        radical_name = decomposer.get_radical_meaning(radical) or ""
        raw_level = raw_level_map.get(radical, 1)

        if max_raw_level <= 1:
            tian_level = 1
        else:
            scaled_level = 1 + math.floor((raw_level - 1) * 59 / (max_raw_level - 1))
            tian_level = min(60, max(1, scaled_level))
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

    rows.sort(key=lambda r: (r["tian_level"], -r["productivity score"], r["radical"]))

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
