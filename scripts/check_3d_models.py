#!/usr/bin/env python3
"""Validate 3D model provenance, mapping, and collision evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


STATUS_VALUES = {
    "Confirmed_Official",
    "Engineering_Assumption",
    "Pending_Human_Verification",
    "Pending_Fabricator_Confirmation",
    "Planned",
    "Simulated",
    "Estimated",
    "Not_Yet_Measured",
}
REQUIRED_COLUMNS = (
    "Reference_or_Assembly",
    "Manufacturer",
    "Manufacturer_Part_Number",
    "Footprint_or_Board_Object",
    "Canonical_Model_Name",
    "Model_Format",
    "Official_Model_Source",
    "Official_Drawing_Source",
    "Local_Model_Path",
    "File_SHA256",
    "Units",
    "CAD_Datum",
    "Footprint_Datum",
    "Rotation_X_deg",
    "Rotation_Y_deg",
    "Rotation_Z_deg",
    "Offset_X_mm",
    "Offset_Y_mm",
    "Offset_Z_mm",
    "Nominal_Height_mm",
    "Height_Source",
    "Collision_Evidence_Path",
    "Model_Status",
    "Mapping_Status",
    "Collision_Check_Status",
    "Notes",
)
STATUS_FIELDS = ("Model_Status", "Mapping_Status", "Collision_Check_Status")
TRANSFORM_FIELDS = (
    "Rotation_X_deg",
    "Rotation_Y_deg",
    "Rotation_Z_deg",
    "Offset_X_mm",
    "Offset_Y_mm",
    "Offset_Z_mm",
)
MODEL_FORMATS = {"STEP", "STP", "IGES", "SAB", "IDF", "IDX", "BOARD_NATIVE", "TBD"}
MODEL_SUFFIXES = {".step", ".stp", ".iges", ".igs", ".sab", ".idf", ".idx", ".brd"}
SHA256_RE = re.compile(r"^[0-9A-Fa-f]{64}$")


@dataclass(frozen=True)
class Issue:
    path: Path
    row: int
    field: str
    severity: str
    message: str

    def format(self) -> str:
        return (
            f"{self.path}:{self.row}:{self.field}:"
            f"{self.severity}:{self.message}"
        )


def _value(row: dict[str, str], field: str) -> str:
    return (row.get(field) or "").strip()


def _is_tbd(value: str) -> bool:
    upper = value.upper()
    return not value or upper == "TBD" or upper.startswith("TBD_") or upper.startswith("TBD-")


def _safe_project_path(root: Path, value: str) -> Path | None:
    candidate = Path(value)
    if candidate.is_absolute() or ".." in candidate.parts:
        return None
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError:
        return None
    return resolved


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _require_numeric(
    issues: list[Issue],
    path: Path,
    row_number: int,
    row: dict[str, str],
    field: str,
) -> None:
    raw = _value(row, field)
    if _is_tbd(raw):
        issues.append(
            Issue(path, row_number, field, "ERROR", "confirmed mapping requires a numeric value")
        )
        return
    try:
        float(raw)
    except ValueError:
        issues.append(Issue(path, row_number, field, "ERROR", f"not numeric: {raw!r}"))


def validate_mapping(path: Path, root: Path) -> list[Issue]:
    """Return row-level issues for a 3D mapping CSV."""
    issues: list[Issue] = []
    seen: dict[str, int] = {}

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = reader.fieldnames
        if headers is None:
            return [Issue(path, 1, "<header>", "ERROR", "missing header")]
        for field in REQUIRED_COLUMNS:
            if field not in headers:
                issues.append(Issue(path, 1, field, "ERROR", "required column missing"))
        if issues:
            return issues

        row_count = 0
        for row_number, row in enumerate(reader, start=2):
            row_count += 1
            for field in REQUIRED_COLUMNS:
                if not _value(row, field):
                    issues.append(
                        Issue(path, row_number, field, "ERROR", "required value is blank")
                    )

            reference = _value(row, "Reference_or_Assembly")
            if reference in seen:
                issues.append(
                    Issue(
                        path,
                        row_number,
                        "Reference_or_Assembly",
                        "ERROR",
                        f"duplicate reference; first seen on row {seen[reference]}",
                    )
                )
            elif reference:
                seen[reference] = row_number

            for field in STATUS_FIELDS:
                status = _value(row, field)
                if status not in STATUS_VALUES:
                    issues.append(
                        Issue(path, row_number, field, "ERROR", f"unsupported status {status!r}")
                    )

            model_format = _value(row, "Model_Format").upper()
            if model_format not in MODEL_FORMATS:
                issues.append(
                    Issue(
                        path,
                        row_number,
                        "Model_Format",
                        "ERROR",
                        f"unsupported model format {model_format!r}",
                    )
                )
            units = _value(row, "Units").lower()
            if units not in {"mm", "inch", "tbd"}:
                issues.append(
                    Issue(path, row_number, "Units", "ERROR", f"unsupported units {units!r}")
                )

            height = _value(row, "Nominal_Height_mm")
            if not _is_tbd(height):
                try:
                    if float(height) <= 0:
                        raise ValueError
                except ValueError:
                    issues.append(
                        Issue(
                            path,
                            row_number,
                            "Nominal_Height_mm",
                            "ERROR",
                            "height must be a positive number or a TBD token",
                        )
                    )

            model_status = _value(row, "Model_Status")
            mapping_status = _value(row, "Mapping_Status")
            collision_status = _value(row, "Collision_Check_Status")
            local_model = _value(row, "Local_Model_Path")
            local_model_path: Path | None = None

            if not _is_tbd(local_model):
                local_model_path = _safe_project_path(root, local_model)
                if local_model_path is None:
                    issues.append(
                        Issue(
                            path,
                            row_number,
                            "Local_Model_Path",
                            "ERROR",
                            "path must be relative and remain inside project root",
                        )
                    )
                elif local_model_path.suffix.lower() not in MODEL_SUFFIXES:
                    issues.append(
                        Issue(
                            path,
                            row_number,
                            "Local_Model_Path",
                            "ERROR",
                            f"unsupported model file suffix {local_model_path.suffix!r}",
                        )
                    )

            if model_status == "Confirmed_Official":
                if _is_tbd(_value(row, "Official_Model_Source")):
                    issues.append(
                        Issue(
                            path,
                            row_number,
                            "Official_Model_Source",
                            "ERROR",
                            "confirmed model requires an official source",
                        )
                    )
                if _is_tbd(local_model) or local_model_path is None:
                    issues.append(
                        Issue(
                            path,
                            row_number,
                            "Local_Model_Path",
                            "ERROR",
                            "confirmed model requires a valid local file",
                        )
                    )
                elif not local_model_path.is_file():
                    issues.append(
                        Issue(
                            path,
                            row_number,
                            "Local_Model_Path",
                            "ERROR",
                            f"model file not found: {local_model_path}",
                        )
                    )
                declared_hash = _value(row, "File_SHA256")
                if not SHA256_RE.fullmatch(declared_hash):
                    issues.append(
                        Issue(
                            path,
                            row_number,
                            "File_SHA256",
                            "ERROR",
                            "confirmed model requires a 64-hex SHA-256",
                        )
                    )
                elif local_model_path is not None and local_model_path.is_file():
                    actual_hash = _sha256(local_model_path)
                    if actual_hash != declared_hash.upper():
                        issues.append(
                            Issue(
                                path,
                                row_number,
                                "File_SHA256",
                                "ERROR",
                                f"hash mismatch; actual {actual_hash}",
                            )
                        )

            if mapping_status == "Confirmed_Official":
                if model_status != "Confirmed_Official":
                    issues.append(
                        Issue(
                            path,
                            row_number,
                            "Mapping_Status",
                            "ERROR",
                            "confirmed mapping requires Confirmed_Official model",
                        )
                    )
                if _is_tbd(_value(row, "CAD_Datum")):
                    issues.append(
                        Issue(path, row_number, "CAD_Datum", "ERROR", "confirmed mapping requires CAD datum")
                    )
                if _is_tbd(_value(row, "Footprint_Datum")):
                    issues.append(
                        Issue(
                            path,
                            row_number,
                            "Footprint_Datum",
                            "ERROR",
                            "confirmed mapping requires footprint datum",
                        )
                    )
                for field in TRANSFORM_FIELDS:
                    _require_numeric(issues, path, row_number, row, field)

            if collision_status == "Confirmed_Official":
                if mapping_status != "Confirmed_Official":
                    issues.append(
                        Issue(
                            path,
                            row_number,
                            "Collision_Check_Status",
                            "ERROR",
                            "confirmed collision check requires confirmed mapping",
                        )
                    )
                evidence = _value(row, "Collision_Evidence_Path")
                evidence_path = None if _is_tbd(evidence) else _safe_project_path(root, evidence)
                if evidence_path is None or not evidence_path.is_file():
                    issues.append(
                        Issue(
                            path,
                            row_number,
                            "Collision_Evidence_Path",
                            "ERROR",
                            "confirmed collision check requires an existing evidence file",
                        )
                    )

        if row_count == 0:
            issues.append(Issue(path, 1, "<data>", "ERROR", "CSV has no data rows"))

    return issues


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mapping_csv", type=Path)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    path = args.mapping_csv.resolve()
    if not root.is_dir():
        print(f"ERROR: project root not found: {root}", file=sys.stderr)
        return 2
    if not path.is_file():
        print(f"ERROR: mapping CSV not found: {path}", file=sys.stderr)
        return 2
    try:
        issues = validate_mapping(path, root)
    except (OSError, UnicodeError, csv.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for issue in issues:
        print(issue.format())
    print(f"Checked {path}; {len(issues)} issue(s).")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
