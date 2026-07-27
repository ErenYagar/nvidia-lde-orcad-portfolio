#!/usr/bin/env python3
"""Validate portfolio CSV schemas and row-level data quality."""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence


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

def _is_controlled_status_field(field: str) -> bool:
    """Return whether a column carries project evidence status."""
    return field == "Status" or field.endswith("_Status")


@dataclass(frozen=True)
class Schema:
    required_columns: tuple[str, ...]
    required_nonempty: tuple[str, ...]


SCHEMAS: dict[str, Schema] = {
    "manufacturing/bom.csv": Schema(
        (
            "Reference_Designator",
            "Quantity",
            "Manufacturer",
            "Manufacturer_Part_Number",
            "Description",
            "Package",
            "Lifecycle",
            "Datasheet_Review_Status",
            "Alternative_Part",
        ),
        (
            "Reference_Designator",
            "Quantity",
            "Manufacturer",
            "Manufacturer_Part_Number",
            "Description",
            "Package",
            "Lifecycle",
            "Datasheet_Review_Status",
            "Alternative_Part",
        ),
    ),
    "schematic/connection_matrix.csv": Schema(
        (
            "Source_Component",
            "Source_Pin",
            "Source_Pin_Name",
            "Net_Name",
            "Destination_Component",
            "Destination_Pin",
            "Destination_Pin_Name",
            "Signal_Type",
            "Voltage_Domain",
            "Differential_Pair_Name",
            "Direction",
            "Source_Document",
            "Human_Review_Status",
            "Notes",
        ),
        (
            "Source_Component",
            "Source_Pin",
            "Source_Pin_Name",
            "Net_Name",
            "Destination_Component",
            "Destination_Pin",
            "Destination_Pin_Name",
            "Signal_Type",
            "Voltage_Domain",
            "Direction",
            "Source_Document",
            "Human_Review_Status",
        ),
    ),
    "schematic/symbol_pinmap.csv": Schema(
        (
            "Component",
            "Pin_Number",
            "Pin_Name",
            "Pin_Type",
            "Voltage_Domain",
            "Source_Document",
            "Human_Review_Status",
            "Notes",
        ),
        (
            "Component",
            "Pin_Number",
            "Pin_Name",
            "Pin_Type",
            "Source_Document",
            "Human_Review_Status",
        ),
    ),
    "pcb/constraints.csv": Schema(
        (
            "Net_Class",
            "Net_Name_or_Group",
            "Signal_Type",
            "Target_Impedance",
            "Impedance_Status",
            "Intra_Pair_Skew",
            "Inter_Pair_Matching",
            "Maximum_Via_Count",
            "Reference_Layer",
            "Plane_Crossing_Rule",
            "Minimum_Spacing",
            "Length_Target",
            "Propagation_Delay_Target",
            "Current_Target",
            "Width_Rule",
            "Source",
            "Assumption_Status",
            "Review_Status",
            "Notes",
        ),
        (
            "Net_Class",
            "Net_Name_or_Group",
            "Signal_Type",
            "Target_Impedance",
            "Impedance_Status",
            "Reference_Layer",
            "Plane_Crossing_Rule",
            "Source",
            "Assumption_Status",
            "Review_Status",
        ),
    ),
    "pcb/3d_model_mapping.csv": Schema(
        (
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
        ),
        (
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
        ),
    ),
}

EMPTY_ALLOWED_PATHS = {
    "evidence/stage2/batch/tps543620_vendor_occurrences.csv",
    "schematic/orcad/stage2/reports/capture_electrical_occurrences.csv",
}

DISCOVERY_EXCLUDED_DIRECTORIES = {"releases"}


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


def _relative_key(path: Path, root: Path) -> str:
    try:
        return path.resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path.name


def validate_file(path: Path, root: Path) -> list[Issue]:
    """Return validation issues for one CSV file."""
    issues: list[Issue] = []
    key = _relative_key(path, root)
    schema = SCHEMAS.get(key)

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames
            if headers is None:
                return [Issue(path, 1, "<header>", "ERROR", "missing header")]
            if any(not header.strip() for header in headers):
                issues.append(
                    Issue(path, 1, "<header>", "ERROR", "blank column name")
                )
            duplicates = sorted(
                {header for header in headers if headers.count(header) > 1}
            )
            for duplicate in duplicates:
                issues.append(
                    Issue(
                        path,
                        1,
                        duplicate,
                        "ERROR",
                        "duplicate column name",
                    )
                )

            if schema is not None:
                for column in schema.required_columns:
                    if column not in headers:
                        issues.append(
                            Issue(
                                path,
                                1,
                                column,
                                "ERROR",
                                "required column missing",
                            )
                        )

            row_count = 0
            for row_number, row in enumerate(reader, start=2):
                row_count += 1
                if None in row:
                    issues.append(
                        Issue(
                            path,
                            row_number,
                            "<row>",
                            "ERROR",
                            "row has more values than header",
                        )
                    )
                if all(not (value or "").strip() for value in row.values()):
                    issues.append(
                        Issue(
                            path,
                            row_number,
                            "<row>",
                            "ERROR",
                            "completely blank row",
                        )
                    )
                    continue

                if schema is not None:
                    for field in schema.required_nonempty:
                        if field in headers and not (row.get(field) or "").strip():
                            issues.append(
                                Issue(
                                    path,
                                    row_number,
                                    field,
                                    "ERROR",
                                    "required value is blank",
                                )
                            )

                for field in (name for name in headers if _is_controlled_status_field(name)):
                    value = (row.get(field) or "").strip()
                    if not value:
                        issues.append(
                            Issue(
                                path,
                                row_number,
                                field,
                                "ERROR",
                                "status value is blank",
                            )
                        )
                    elif value not in STATUS_VALUES:
                        issues.append(
                            Issue(
                                path,
                                row_number,
                                field,
                                "ERROR",
                                f"unsupported status {value!r}",
                            )
                        )

            if row_count == 0 and key not in EMPTY_ALLOWED_PATHS:
                issues.append(
                    Issue(path, 1, "<data>", "ERROR", "CSV has no data rows")
                )
    except (OSError, UnicodeError, csv.Error) as exc:
        issues.append(Issue(path, 0, "<file>", "ERROR", str(exc)))

    return issues


def discover_csv_files(root: Path) -> list[Path]:
    """Find source CSV files, excluding fixtures and frozen release snapshots."""
    files: list[Path] = []
    for path in root.rglob("*.csv"):
        try:
            relative_parts = path.relative_to(root).parts
        except ValueError:
            relative_parts = path.parts
        parts = {part.lower() for part in relative_parts}
        if "invalid" in parts:
            continue
        if parts & DISCOVERY_EXCLUDED_DIRECTORIES:
            continue
        files.append(path)
    return sorted(files)


def run(paths: Iterable[Path], root: Path) -> int:
    issues: list[Issue] = []
    files = list(paths)
    if not files:
        print("ERROR: no CSV files found", file=sys.stderr)
        return 2
    for path in files:
        if not path.is_file():
            print(f"ERROR: file not found: {path}", file=sys.stderr)
            return 2
        issues.extend(validate_file(path, root))

    for issue in issues:
        print(issue.format())
    print(f"Checked {len(files)} CSV file(s); {len(issues)} issue(s).")
    return 1 if issues else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="*", type=Path, help="specific CSV files")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="project root used for discovery and schema matching",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    files = [path.resolve() for path in args.files]
    if not files:
        if not root.is_dir():
            print(f"ERROR: root directory not found: {root}", file=sys.stderr)
            return 2
        files = discover_csv_files(root)
    return run(files, root)


if __name__ == "__main__":
    raise SystemExit(main())
