#!/usr/bin/env python3
"""Detect duplicate symbol pins and pins assigned to conflicting nets."""

from __future__ import annotations

import argparse
import csv
import sys
from collections import defaultdict
from pathlib import Path
from typing import Sequence


PLACEHOLDER_PINS = {
    "",
    "TBD",
    "PENDING",
    "PENDING_HUMAN_VERIFICATION",
    "N/A",
    "NA",
    "?",
}


def _is_concrete_pin(pin: str) -> bool:
    return pin.strip().upper() not in PLACEHOLDER_PINS


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return (reader.fieldnames or [], list(reader))


def check_connection_matrix(path: Path) -> list[str]:
    headers, rows = _read_csv(path)
    required = {
        "Source_Component",
        "Source_Pin",
        "Destination_Component",
        "Destination_Pin",
        "Net_Name",
    }
    missing = sorted(required.difference(headers))
    if missing:
        return [
            f"{path}:1:{field}:ERROR:required column missing"
            for field in missing
        ]

    pin_nets: dict[tuple[str, str], set[str]] = defaultdict(set)
    appearances: dict[tuple[str, str, str], list[int]] = defaultdict(list)
    for row_number, row in enumerate(rows, start=2):
        net = row["Net_Name"].strip()
        for prefix in ("Source", "Destination"):
            component = row[f"{prefix}_Component"].strip()
            pin = row[f"{prefix}_Pin"].strip()
            if component and _is_concrete_pin(pin) and net:
                pin_nets[(component, pin)].add(net)
                appearances[(component, pin, net)].append(row_number)

    issues: list[str] = []
    for (component, pin), nets in sorted(pin_nets.items()):
        if len(nets) > 1:
            issues.append(
                f"{path}:0:{component}.{pin}:ERROR:"
                f"pin connects to conflicting nets {sorted(nets)}"
            )
    for (component, pin, net), row_numbers in sorted(appearances.items()):
        if len(row_numbers) > 1:
            issues.append(
                f"{path}:{row_numbers[0]}:{component}.{pin}:WARNING:"
                f"duplicate appearance on {net}; human review rows {row_numbers}"
            )
    return issues


def check_symbol_pinmap(path: Path) -> list[str]:
    headers, rows = _read_csv(path)
    component_field = (
        "Component" if "Component" in headers else "Reference_Designator"
    )
    pin_field = "Pin_Number"
    missing = [
        field
        for field in (component_field, pin_field)
        if field not in headers
    ]
    if missing:
        return [
            f"{path}:1:{field}:ERROR:required column missing"
            for field in missing
        ]

    seen: dict[tuple[str, str], int] = {}
    issues: list[str] = []
    for row_number, row in enumerate(rows, start=2):
        key = (row[component_field].strip(), row[pin_field].strip())
        if not key[0] or not _is_concrete_pin(key[1]):
            continue
        if key in seen:
            issues.append(
                f"{path}:{row_number}:{key[0]}.{key[1]}:ERROR:"
                f"duplicate symbol pin; first seen at row {seen[key]}"
            )
        else:
            seen[key] = row_number
    return issues


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("connection_matrix", type=Path)
    parser.add_argument("symbol_pinmap", nargs="?", type=Path)
    args = parser.parse_args(argv)
    paths = [args.connection_matrix]
    if args.symbol_pinmap is not None:
        paths.append(args.symbol_pinmap)
    if any(not path.is_file() for path in paths):
        for path in paths:
            if not path.is_file():
                print(f"ERROR: file not found: {path}", file=sys.stderr)
        return 2
    try:
        issues = check_connection_matrix(args.connection_matrix)
        if args.symbol_pinmap is not None:
            issues.extend(check_symbol_pinmap(args.symbol_pinmap))
    except (OSError, UnicodeError, csv.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for issue in issues:
        print(issue)
    errors = sum(":ERROR:" in issue for issue in issues)
    print(f"Checked pin data; {errors} error(s), {len(issues) - errors} warning(s).")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
