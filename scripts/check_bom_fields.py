#!/usr/bin/env python3
"""Check required manufacturing BOM fields and simple field formats."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Sequence


REQUIRED_FIELDS = (
    "Manufacturer",
    "Manufacturer_Part_Number",
    "Package",
    "Quantity",
    "Reference_Designator",
    "Lifecycle",
    "Datasheet_Review_Status",
    "Alternative_Part",
)
REFDES_RE = re.compile(r"^[A-Z]+[0-9]+(?:\s*;\s*[A-Z]+[0-9]+)*$")


def check_bom(path: Path) -> list[str]:
    issues: list[str] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames or []
            for field in REQUIRED_FIELDS:
                if field not in headers:
                    issues.append(
                        f"{path}:1:{field}:ERROR:required column missing"
                    )
            if issues:
                return issues

            for row_number, row in enumerate(reader, start=2):
                for field in REQUIRED_FIELDS:
                    if not (row.get(field) or "").strip():
                        issues.append(
                            f"{path}:{row_number}:{field}:"
                            "ERROR:required value is blank"
                        )
                quantity_text = (row.get("Quantity") or "").strip()
                try:
                    quantity = int(quantity_text)
                    if quantity < 1:
                        raise ValueError
                except ValueError:
                    issues.append(
                        f"{path}:{row_number}:Quantity:"
                        "ERROR:quantity must be a positive integer"
                    )
                refdes = (row.get("Reference_Designator") or "").strip()
                if refdes and not REFDES_RE.fullmatch(refdes):
                    issues.append(
                        f"{path}:{row_number}:Reference_Designator:"
                        "ERROR:expected semicolon-separated designators"
                    )
    except (OSError, UnicodeError, csv.Error) as exc:
        raise RuntimeError(str(exc)) from exc
    return issues


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bom", type=Path)
    args = parser.parse_args(argv)
    if not args.bom.is_file():
        print(f"ERROR: file not found: {args.bom}", file=sys.stderr)
        return 2
    try:
        issues = check_bom(args.bom)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for issue in issues:
        print(issue)
    print(f"Checked BOM; {len(issues)} issue(s).")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
