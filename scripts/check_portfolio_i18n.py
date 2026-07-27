"""Check that each portfolio data-i18n node has English and Traditional Chinese text."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--file", type=Path, default=Path("portfolio/index.html"))
    args = parser.parse_args()
    text = args.file.read_text(encoding="utf-8")
    node_keys = set(re.findall(r'data-i18n="([A-Za-z][A-Za-z0-9]*)"', text))
    en_block = text.split("en: {", 1)[1].split("\n      },\n      zh:", 1)[0]
    zh_block = text.split("zh: {", 1)[1].split("\n      }\n    };", 1)[0]
    en_keys = set(re.findall(r"([A-Za-z][A-Za-z0-9]*):", en_block))
    zh_keys = set(re.findall(r"([A-Za-z][A-Za-z0-9]*):", zh_block))
    missing_en = sorted(node_keys - en_keys)
    missing_zh = sorted(node_keys - zh_keys)
    for key in missing_en:
        print(f"ERROR: missing English translation: {key}")
    for key in missing_zh:
        print(f"ERROR: missing Chinese translation: {key}")
    print(f"Checked {len(node_keys)} i18n node(s); {len(missing_en) + len(missing_zh)} issue(s).")
    return 1 if missing_en or missing_zh else 0


if __name__ == "__main__":
    raise SystemExit(main())
