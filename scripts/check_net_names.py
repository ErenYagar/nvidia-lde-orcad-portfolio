#!/usr/bin/env python3
"""Validate net-name syntax and PCIe lane/polarity completeness."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Sequence


NET_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")
PAIR_RE = re.compile(r"^(PCIE_(?:TX|RX)[0-3]|PCIE_REFCLK)_([PN])$")
REQUIRED_SIDEBANDS = {
    "PCIE_PERST_N",
    "PCIE_CLKREQ_N",
    "PCIE_PEWAKE_N",
    "PCIE_PRSNT_N",
}
REQUIRED_POWER = {"P12V_SLOT", "P3V3_NVME", "P3V3_AUX", "PGOOD_3V3"}
REQUIRED_TELEMETRY = {"I2C_SCL", "I2C_SDA"}


def check_names(path: Path) -> list[str]:
    issues: list[str] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if "Net_Name" not in (reader.fieldnames or []):
                return [f"{path}:1:Net_Name:ERROR:required column missing"]
            nets: set[str] = set()
            for row_number, row in enumerate(reader, start=2):
                net = (row.get("Net_Name") or "").strip()
                if not net:
                    issues.append(
                        f"{path}:{row_number}:Net_Name:ERROR:blank net name"
                    )
                    continue
                nets.add(net)
                if not NET_RE.fullmatch(net):
                    issues.append(
                        f"{path}:{row_number}:Net_Name:"
                        f"ERROR:invalid net name {net!r}"
                    )
    except (OSError, UnicodeError, csv.Error) as exc:
        raise RuntimeError(str(exc)) from exc

    pair_members: dict[str, set[str]] = {}
    for net in nets:
        match = PAIR_RE.fullmatch(net)
        if match:
            pair_members.setdefault(match.group(1), set()).add(match.group(2))
    expected_pairs = {
        *(f"PCIE_TX{lane}" for lane in range(4)),
        *(f"PCIE_RX{lane}" for lane in range(4)),
        "PCIE_REFCLK",
    }
    for pair in sorted(expected_pairs):
        members = pair_members.get(pair, set())
        if members != {"P", "N"}:
            issues.append(
                f"{path}:0:{pair}:ERROR:"
                f"expected P/N members, found {sorted(members)}"
            )
    for net in sorted(REQUIRED_SIDEBANDS | REQUIRED_POWER | REQUIRED_TELEMETRY):
        if net not in nets:
            issues.append(f"{path}:0:{net}:ERROR:required net missing")
    return issues


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("connection_matrix", type=Path)
    args = parser.parse_args(argv)
    if not args.connection_matrix.is_file():
        print(
            f"ERROR: file not found: {args.connection_matrix}",
            file=sys.stderr,
        )
        return 2
    try:
        issues = check_names(args.connection_matrix)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for issue in issues:
        print(issue)
    print(f"Checked net names; {len(issues)} issue(s).")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
