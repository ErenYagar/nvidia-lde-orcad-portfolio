#!/usr/bin/env python3
"""Validate a STEP export without pretending to perform an MCAD sign-off."""

from __future__ import annotations

import argparse
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


REQUIRED_PRODUCTS = (
    "PlaceBound_BRACKET_PRELIM",
    "PlaceBound_M2_CONN_PRELIM",
    "PlaceBound_M2_2280_PRELIM",
    "PlaceBound_M2_STANDOFF_PRELIM",
    "PlaceBound_QFN_2X2",
    "PlaceBound_QFN_2P5X3",
    "PlaceBound_XGL5050",
    "PlaceBound_WSK2512",
    "PlaceBound_HDR1X4_RA",
)


@dataclass(frozen=True)
class Issue:
    path: Path
    field: str
    severity: str
    message: str

    def format(self) -> str:
        return f"{self.path}:1:{self.field}:{self.severity}:{self.message}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def inspect_step(path: Path, expected_sha256: str | None = None) -> tuple[list[Issue], dict[str, str | int]]:
    issues: list[Issue] = []
    data = path.read_text(encoding="latin-1")
    counts = {
        "bytes": path.stat().st_size,
        "sha256": sha256(path),
        "products": data.count("PRODUCT("),
        "assembly_occurrences": data.count("NEXT_ASSEMBLY_USAGE_OCCURRENCE"),
        "solid_breps": data.count("MANIFOLD_SOLID_BREP"),
        "closed_shells": data.count("CLOSED_SHELL"),
        "advanced_faces": data.count("ADVANCED_FACE"),
    }

    if not data.startswith("ISO-10303-21;"):
        issues.append(Issue(path, "header", "ERROR", "missing ISO-10303-21 header"))
    if not data.rstrip().endswith("END-ISO-10303-21;"):
        issues.append(Issue(path, "footer", "ERROR", "missing ISO-10303-21 footer"))
    if "AUTOMOTIVE_DESIGN" not in data and "AP214" not in data.upper():
        issues.append(Issue(path, "schema", "ERROR", "AP214/AUTOMOTIVE_DESIGN schema not found"))
    if "MILLIMETRE" not in data and "SI_UNIT(.MILLI.,.METRE.)" not in data:
        issues.append(Issue(path, "units", "ERROR", "millimetre length unit not found"))
    if counts["solid_breps"] < 1 or counts["closed_shells"] < 1:
        issues.append(Issue(path, "geometry", "ERROR", "no closed solid B-rep found"))
    if counts["solid_breps"] != counts["closed_shells"]:
        issues.append(
            Issue(
                path,
                "geometry",
                "ERROR",
                "MANIFOLD_SOLID_BREP and CLOSED_SHELL counts differ",
            )
        )
    if counts["assembly_occurrences"] < 1:
        issues.append(Issue(path, "assembly", "ERROR", "no assembly occurrences found"))

    for product in REQUIRED_PRODUCTS:
        if product not in data:
            issues.append(
                Issue(path, "product", "ERROR", f"required preliminary body missing: {product}")
            )

    if expected_sha256 and counts["sha256"] != expected_sha256.upper():
        issues.append(
            Issue(
                path,
                "sha256",
                "ERROR",
                f"hash mismatch; actual {counts['sha256']}",
            )
        )

    return issues, counts


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("step_file", type=Path)
    parser.add_argument("--expected-sha256")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    path = args.step_file.resolve()
    if not path.is_file():
        print(f"ERROR: STEP file not found: {path}", file=sys.stderr)
        return 2
    try:
        issues, counts = inspect_step(path, args.expected_sha256)
    except (OSError, UnicodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    for issue in issues:
        print(issue.format())
    print(f"STEP file: {path}")
    for key, value in counts.items():
        print(f"{key}: {value}")
    print(f"Checked {path}; {len(issues)} issue(s).")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
