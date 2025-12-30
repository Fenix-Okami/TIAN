from __future__ import annotations

import csv
import re
from html import unescape
from typing import Dict, List, Optional
from pathlib import Path

from hsk_csv_utils import (
    LEVELS,
    OUTPUT_DIR,
    WORDS_DIR,
    read_entries,
    write_csv,
)

ANKI_DIR = WORDS_DIR.parent / "Anki xiehanzi"
HANZI_LEVELS_PATH = OUTPUT_DIR / "hanzi_levels_1_3.csv"


def unique_preserve_order(values: List[str]) -> List[str]:
    return list(dict.fromkeys(values))


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text)


def parse_pinyin_syllables(html_text: str, fallback: str) -> List[str]:
    match = re.search(r'<span class="pinYinWrapper">(.*?)</span>\s*<ul', html_text, re.S)
    source = match.group(1) if match else fallback
    cleaned = strip_tags(unescape(source))
    return [part.lower() for part in cleaned.split() if part]


def parse_meaning(html_text: str) -> str:
    lis = re.findall(r"<li>(.*?)</li>", html_text, re.S)
    cleaned = [" ".join(strip_tags(unescape(li)).split()) for li in lis if li]
    cleaned = [c for c in cleaned if c]
    return "; ".join(cleaned)


def load_hanzi_levels(path: Path = HANZI_LEVELS_PATH) -> Dict[str, int]:
    levels: Dict[str, int] = {}
    if not path.exists():
        return levels
    with path.open(encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            ch = (row.get("hanzi") or "").strip()
            try:
                level = int(row.get("tian_level", ""))
            except ValueError:
                continue
            if ch:
                levels[ch] = level
    return levels


def parse_simple_meaning(html_text: str) -> str:
    lis = re.findall(r"<li>(.*?)</li>", html_text, re.S)
    for li in lis:
        cleaned = " ".join(strip_tags(unescape(li)).split())
        if cleaned:
            return cleaned
    return ""


def load_anki_data(levels: List[int]) -> Dict[str, Dict[str, object]]:
    data: Dict[str, Dict[str, object]] = {}
    for level in levels:
        path = ANKI_DIR / f"HSK_Level_{level}.txt"
        if not path.exists():
            continue
        with path.open(encoding="utf-8") as handle:
            reader = csv.reader(handle, delimiter="\t")
            for row in reader:
                if len(row) < 4:
                    continue
                simp = row[0].strip()
                trad = row[1].strip() if len(row) > 1 else ""
                base_pinyin = row[2].strip() if len(row) > 2 else ""
                html_text = "\t".join(row[7:]) if len(row) > 7 else row[-1] if row else ""
                pinyin_syllables = parse_pinyin_syllables(html_text, base_pinyin)
                meaning = parse_meaning(html_text)
                simple_meaning = parse_simple_meaning(html_text)
                entry = {
                    "pinyin": pinyin_syllables,
                    "meaning": meaning,
                    "simple_meaning": simple_meaning,
                }
                if simp:
                    data[simp] = entry
                if trad:
                    data.setdefault(trad, entry)
    return data


def normalize_vocab_key(word: str) -> str:
    # Drop trailing digits like "本1" -> "本"
    i = len(word)
    while i > 0 and word[i - 1].isdigit():
        i -= 1
    return word[:i] if i != len(word) else word


def col_pinyin_from_data(word: str, anki_data: Dict[str, Dict[str, object]]) -> str:
    key = normalize_vocab_key(word)
    entry: Optional[Dict[str, object]] = anki_data.get(key) or anki_data.get(word)
    if not entry:
        return ""
    syllables = entry.get("pinyin", [])
    if not isinstance(syllables, list):
        return ""
    unique = unique_preserve_order([s for s in syllables if s])
    return "".join(unique)


def col_pinyin_spaced(word: str, anki_data: Dict[str, Dict[str, object]]) -> str:
    key = normalize_vocab_key(word)
    entry: Optional[Dict[str, object]] = anki_data.get(key) or anki_data.get(word)
    if not entry:
        return ""
    syllables = entry.get("pinyin", [])
    if not isinstance(syllables, list):
        return ""
    unique = unique_preserve_order([s for s in syllables if s])
    return " ".join(unique)


def col_meaning_from_data(word: str, anki_data: Dict[str, Dict[str, object]]) -> str:
    key = normalize_vocab_key(word)
    entry: Optional[Dict[str, object]] = anki_data.get(key) or anki_data.get(word)
    if not entry:
        return ""
    meaning = entry.get("meaning", "")
    return meaning if isinstance(meaning, str) else ""


def col_simple_meaning_from_data(word: str, anki_data: Dict[str, Dict[str, object]]) -> str:
    key = normalize_vocab_key(word)
    entry: Optional[Dict[str, object]] = anki_data.get(key) or anki_data.get(word)
    if not entry:
        return ""
    meaning = entry.get("simple_meaning", "")
    return meaning if isinstance(meaning, str) else ""


def build_vocabulary_csv() -> None:
    anki_data = load_anki_data(LEVELS)
    hanzi_levels = load_hanzi_levels()

    rows: List[Dict[str, object]] = []
    for level in LEVELS:
        source = WORDS_DIR / f"HSK_Level_{level}_words.txt"
        entries = read_entries(source)
        for vocab in entries:
            char_levels = [hanzi_levels.get(ch) for ch in vocab if hanzi_levels.get(ch) is not None]
            tian_level = max(char_levels) if char_levels else level
            rows.append(
                {
                    "vocab": vocab,
                    "tian_level": tian_level,
                    "hsk_level": level,
                    "pinyin": col_pinyin_from_data(vocab, anki_data),
                    "pinyin_spaced": col_pinyin_spaced(vocab, anki_data),
                    "meaning": col_meaning_from_data(vocab, anki_data),
                    "simple_meaning": col_simple_meaning_from_data(vocab, anki_data),
                    "meaning_mnemonic": "",
                    "reading_mnemonic": "",
                    "components": "",
                    "example_sentences": "",
                }
            )

    rows.sort(key=lambda r: (r["tian_level"], r["hsk_level"], r["vocab"]))
    write_csv(
        rows,
        [
            "vocab",
            "tian_level",
            "hsk_level",
            "pinyin",
            "pinyin_spaced",
            "meaning",
            "simple_meaning",
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
