from __future__ import annotations

import importlib
from typing import Dict, List

from hsk_csv_utils import (
    HANZI_DIR,
    LEVELS,
    OUTPUT_DIR,
    numbered_pinyin_to_tone_marks,
    read_entries,
    write_csv,
)

def load_hanzipy():
    """Load hanzipy classes without requiring static imports."""
    try:
        decomposer_mod = importlib.import_module("hanzipy.decomposer")
        dictionary_mod = importlib.import_module("hanzipy.dictionary")
        return decomposer_mod.HanziDecomposer, dictionary_mod.HanziDictionary
    except Exception as exc:  # pragma: no cover
        raise SystemExit(
            "hanzipy is required but not available. "
            "Install dependencies in the project venv: "
            "./venv/Scripts/python.exe -m pip install -r requirements.txt\n"
            f"Original error: {exc}"
        )


def col_hanzi(hanzi: str) -> str:
    return hanzi


def is_name_pinyin(pinyin: str) -> bool:
    return bool(pinyin) and pinyin[0].isalpha() and pinyin[0].isupper()


def unique_preserve_order(values: List[str]) -> List[str]:
    return list(dict.fromkeys(values))


def lookup_pinyins(hanzi: str, dictionary) -> List[str]:
    entries = dictionary.definition_lookup(hanzi) or []
    filtered: List[str] = []

    for entry in entries:
        if not isinstance(entry, dict):
            continue
        definition = str(entry.get("definition") or "")
        if "(archaic)" in definition.lower():
            continue
        pinyin = str(entry.get("pinyin") or "").strip()
        if pinyin:
            filtered.append(pinyin)

    if filtered:
        return filtered

    # Fallback: if CC-CEDICT has no entry, use get_pinyin.
    return dictionary.get_pinyin(hanzi) or []


def col_pinyin(raw_pinyins: List[str]) -> str:
    if not raw_pinyins:
        return ""

    non_name = [p for p in raw_pinyins if not is_name_pinyin(p)]
    converted = [numbered_pinyin_to_tone_marks(p) for p in non_name]
    unique = unique_preserve_order([p for p in converted if p])
    return ";".join(unique)


def col_in_names(raw_pinyins: List[str]) -> str:
    return "true" if any(is_name_pinyin(p) for p in raw_pinyins) else "false"


def get_components(hanzi: str, decomposer) -> List[str]:
    decomposition = decomposer.decompose(hanzi, 2)
    if not isinstance(decomposition, dict):
        return []

    components = decomposition.get("components")
    if components is None:
        components = decomposition.get("radical")
    if not isinstance(components, list):
        return []

    cleaned = [c for c in components if c and c != "No glyph available"]
    return list(dict.fromkeys(cleaned))


def load_radical_levels() -> Dict[str, int]:
    path = OUTPUT_DIR / "radicals_levels_1_3.csv"
    levels: Dict[str, int] = {}
    if not path.exists():
        return levels
    import csv

    with path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            radical = row.get("radical", "").strip()
            try:
                level = int(row.get("tian_level", ""))
            except ValueError:
                continue
            if radical:
                levels[radical] = level
    return levels


def tian_level_from_components(components: List[str], radical_levels: Dict[str, int], fallback: int) -> int:
    if not components:
        return fallback
    levels = [radical_levels.get(c) for c in components if radical_levels.get(c) is not None]
    return max(levels) if levels else fallback


def build_hanzi_csv() -> None:
    HanziDecomposer, HanziDictionary = load_hanzipy()
    dictionary = HanziDictionary()
    decomposer = HanziDecomposer()
    radical_levels = load_radical_levels()

    rows: List[Dict[str, object]] = []
    for level in LEVELS:
        source = HANZI_DIR / f"HSK_Level_{level}_hanzi.txt"
        entries = read_entries(source)
        for hanzi in entries:
            raw_pinyins = lookup_pinyins(hanzi, dictionary)
            pinyin_str = col_pinyin(raw_pinyins)
            primary_reading = pinyin_str.split(";")[0] if pinyin_str else ""
            components_list = get_components(hanzi, decomposer)
            tian_level = tian_level_from_components(components_list, radical_levels, level)
            rows.append(
                {
                    "hanzi": col_hanzi(hanzi),
                    "tian_level": tian_level,
                    "hsk_level": level,
                    "pinyin": pinyin_str,
                    "primary_reading": primary_reading,
                    "simple_meaning": "",
                    "meaning": "",
                    "meaning_mnemonic": "",
                    "reading_mnemonic": "",
                    "components": " ".join(components_list),
                    "in_names": col_in_names(raw_pinyins),
                }
            )

    # Confirming existing sort operation
    rows.sort(key=lambda r: (r["tian_level"], r["hsk_level"], r["hanzi"]))
    write_csv(
        rows,
        [
            "hanzi",
            "tian_level",
            "hsk_level",
            "pinyin",
            "primary_reading",
            "simple_meaning",
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
