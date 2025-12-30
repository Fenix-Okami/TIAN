from __future__ import annotations

# Thin orchestrator to run all CSV generators in dependency order.

from build_radicals_csv import build_radicals_csv
from build_hsk_hanzi_csv import build_hanzi_csv
from build_hsk_vocab_csv import build_vocabulary_csv


def main() -> None:
    # Radicals feed hanzi levels, which feed vocabulary levels.
    build_radicals_csv()
    build_hanzi_csv()
    build_vocabulary_csv()


if __name__ == "__main__":
    main()
