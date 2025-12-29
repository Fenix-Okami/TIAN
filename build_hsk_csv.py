from __future__ import annotations

# Thin orchestrator to run both dedicated generators.

from build_hsk_hanzi_csv import build_hanzi_csv
from build_hsk_vocab_csv import build_vocabulary_csv


def main() -> None:
    build_hanzi_csv()
    build_vocabulary_csv()


if __name__ == "__main__":
    main()
