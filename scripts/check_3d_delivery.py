#!/usr/bin/env python3
"""Validate the preliminary native Allegro/3DX evidence package."""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


EXPECTED_CASES = {f"3D-{index:02d}" for index in range(1, 9)}
REQUIRED_VIEWS = (
    "allegro_native_reopen.jpg",
    "3dx_top_preliminary.jpg",
    "3dx_bottom_preliminary.jpg",
    "3dx_side_front_preliminary.jpg",
    "3dx_isometric_top_preliminary.jpg",
    "3dx_ssd_underside_preliminary.jpg",
    "3dx_bracket_left_preliminary.jpg",
    "3dx_collision_review_preliminary.jpg",
    "3dx_step_reimport_preliminary.jpg",
    "3dx_step_reimport_properties_preliminary.jpg",
)
REQUIRED_ROUNDTRIP_EVIDENCE = (
    "pcie_gen3_x4_nvme_adapter_reva_step_reimport.dra",
    "step_reimport_native_log.txt",
    "step_reimport_batch.jrl",
)
ALLOWED_RESULTS = {
    "Preliminary_Clear",
    "Preliminary_Collision",
    "Blocked_Missing_Exact_Model",
    "Blocked_3DX_Reimport_Not_Available",
}
REQUIRED_COLLISION_FIELDS = (
    "Case_ID",
    "Object_A",
    "Object_B",
    "Rule_mm",
    "Measured_Clearance_mm",
    "Tolerance_mm",
    "Model_Revisions",
    "Result",
    "Evidence_File",
    "Status",
    "Notes",
)
CASE_CONTRACTS = {
    "3D-03": {
        "Result": "Preliminary_Clear",
        "Evidence_File": "evidence/3d/clearance_measurement_evidence.md",
    },
    "3D-06": {
        "Result": "Blocked_Missing_Exact_Model",
        "Evidence_File": "evidence/3d/3dx_top_preliminary.jpg",
    },
    "3D-08": {
        "Result": "Preliminary_Clear",
        "Evidence_File": "evidence/3d/step_roundtrip_evidence.md",
    },
}


@dataclass(frozen=True)
class Issue:
    path: Path
    row: int
    field: str
    severity: str
    message: str

    def format(self) -> str:
        return f"{self.path}:{self.row}:{self.field}:{self.severity}:{self.message}"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def parse_nonnegative_finite(raw: str, field: str) -> float:
    try:
        value = float(raw)
    except ValueError as exc:
        raise ValueError(
            f"{field} must be finite and non-negative, got {raw!r}"
        ) from exc
    if not math.isfinite(value) or value < 0:
        raise ValueError(f"{field} must be finite and non-negative, got {raw!r}")
    return value


def expand_bom_references(raw: str) -> set[str]:
    return {
        token.strip()
        for token in re.split(r"[;,]", raw)
        if token.strip()
    }


def parse_collision_number(raw: str) -> float | None:
    value = raw.strip().upper()
    if value in {"N/A", "TBD"}:
        return None
    return parse_nonnegative_finite(raw, "collision value")


def duplicate_case_ids(rows: Sequence[dict[str, str]]) -> list[str]:
    counts = Counter((row.get("Case_ID") or "").strip() for row in rows)
    return sorted(case_id for case_id, count in counts.items() if case_id and count > 1)


def has_screening_margin(rule: float, measured: float, tolerance: float) -> bool:
    values = (rule, measured, tolerance)
    return all(math.isfinite(value) and value >= 0 for value in values) and (
        measured >= rule + tolerance
    )


def native_symbol_counter(path: Path) -> Counter[tuple[str, float, float, float]]:
    symbols: Counter[tuple[str, float, float, float]] = Counter()
    for line_number, line in enumerate(
        path.read_text(encoding="utf-8-sig").splitlines(), start=1
    ):
        if not line.startswith("S!"):
            continue
        fields = line.split("!")
        if len(fields) < 11:
            raise ValueError(
                f"line {line_number}: malformed native symbol record: {line!r}"
            )
        numeric_fields = {
            "SYM_BOX_X1": fields[4],
            "SYM_BOX_X2": fields[5],
            "SYM_BOX_Y1": fields[6],
            "SYM_BOX_Y2": fields[7],
            "SYM_ROTATE": fields[8],
            "SYM_X": fields[9],
            "SYM_Y": fields[10],
        }
        try:
            parsed = {
                field: parse_nonnegative_finite(
                    raw, f"line {line_number} {field}"
                )
                for field, raw in numeric_fields.items()
            }
        except ValueError as exc:
            raise ValueError(str(exc)) from exc
        if parsed["SYM_BOX_X2"] < parsed["SYM_BOX_X1"]:
            raise ValueError(
                f"line {line_number}: SYM_BOX_X2 must be greater than or equal to SYM_BOX_X1"
            )
        if parsed["SYM_BOX_Y2"] < parsed["SYM_BOX_Y1"]:
            raise ValueError(
                f"line {line_number}: SYM_BOX_Y2 must be greater than or equal to SYM_BOX_Y1"
            )
        symbols[
            (
                fields[2].strip(),
                round(parsed["SYM_X"], 4),
                round(parsed["SYM_Y"], 4),
                round(parsed["SYM_ROTATE"], 3),
            )
        ] += 1
    return symbols


def checked_native_symbol_counter(
    path: Path,
) -> tuple[Counter[tuple[str, float, float, float]] | None, list[Issue]]:
    try:
        return native_symbol_counter(path), []
    except ValueError as exc:
        return None, [Issue(path, 0, "<content>", "ERROR", str(exc))]


def normalize_artifact_path(raw: str) -> str:
    return Path(raw.strip()).as_posix()


def build_artifact_manifest_index(
    rows: Sequence[dict[str, str]], manifest_path: Path
) -> tuple[dict[str, tuple[int, dict[str, str]]], list[Issue]]:
    index: dict[str, tuple[int, dict[str, str]]] = {}
    issues: list[Issue] = []
    for row_number, row in enumerate(rows, start=2):
        relative = (row.get("Path") or "").strip()
        if not relative:
            continue
        key = normalize_artifact_path(relative)
        if key in index:
            issues.append(
                Issue(
                    manifest_path,
                    row_number,
                    "Path",
                    "ERROR",
                    f"duplicate artifact path {key!r}",
                )
            )
            continue
        index[key] = (row_number, row)
    return index, issues


def validate_collision_evidence(
    root: Path,
    collision_path: Path,
    row_number: int,
    evidence_value: str,
    manifest_index: dict[str, tuple[int, dict[str, str]]],
) -> list[Issue]:
    issues: list[Issue] = []
    evidence_path = root / evidence_value
    if not evidence_value or not evidence_path.is_file():
        issues.append(
            Issue(
                collision_path,
                row_number,
                "Evidence_File",
                "ERROR",
                "evidence file missing",
            )
        )
        return issues
    key = normalize_artifact_path(evidence_value)
    if key not in manifest_index:
        issues.append(
            Issue(
                collision_path,
                row_number,
                "Evidence_File",
                "ERROR",
                "collision evidence is not registered in artifact_manifest.csv",
            )
        )
    return issues


def validate_artifact_manifest_row(
    root: Path,
    manifest_path: Path,
    row_number: int,
    row: dict[str, str],
    board_hash: str,
) -> list[Issue]:
    issues: list[Issue] = []
    relative = (row.get("Path") or "").strip()
    path = root / relative
    if not path.is_file():
        return [Issue(manifest_path, row_number, "Path", "ERROR", "artifact missing")]
    actual_size = str(path.stat().st_size)
    if actual_size != (row.get("Size_Bytes") or "").strip():
        issues.append(
            Issue(
                manifest_path,
                row_number,
                "Size_Bytes",
                "ERROR",
                f"size mismatch; actual {actual_size}",
            )
        )
    actual_hash = sha256(path)
    if actual_hash != (row.get("SHA256") or "").strip().upper():
        issues.append(
            Issue(
                manifest_path,
                row_number,
                "SHA256",
                "ERROR",
                f"hash mismatch; actual {actual_hash}",
            )
        )
    source_board_hash = (row.get("Source_Board_SHA256") or "").strip().upper()
    if source_board_hash != board_hash:
        issues.append(
            Issue(
                manifest_path,
                row_number,
                "Source_Board_SHA256",
                "ERROR",
                f"source board hash mismatch; actual {board_hash}",
            )
        )
    return issues


def validate(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    board = root / "pcb/allegro/pcie_gen3_x4_nvme_adapter_reva.brd"
    step = root / "manufacturing/mcad/pcie_gen3_x4_nvme_adapter_reva_preliminary.step"
    evidence = root / "evidence/3d"
    placement = root / "pcb/allegro/placement_manifest.csv"
    bom = root / "manufacturing/bom.csv"
    collision = evidence / "collision_report.csv"
    artifact_manifest = evidence / "artifact_manifest.csv"
    native_symbols = evidence / "native_board_audit_symbols.txt"

    for path in (board, step, placement, bom, collision, artifact_manifest, native_symbols):
        if not path.is_file():
            issues.append(Issue(path, 0, "<file>", "ERROR", "required file missing"))
    for name in REQUIRED_VIEWS:
        path = evidence / name
        if not path.is_file() or path.stat().st_size < 1024:
            issues.append(Issue(path, 0, "<file>", "ERROR", "required 3D evidence missing"))
    for name in REQUIRED_ROUNDTRIP_EVIDENCE:
        path = evidence / name
        if not path.is_file() or path.stat().st_size < 100:
            issues.append(
                Issue(path, 0, "<file>", "ERROR", "required native STEP round-trip evidence missing")
            )
    if issues:
        return issues

    roundtrip_log = (evidence / "step_reimport_native_log.txt").read_text(
        encoding="utf-8"
    )
    for token in (
        "NATIVE_DRA_STEP_ASSIGNMENT_OK",
        "Wrapper_Units: millimeters",
        "Wrapper_Place_Bound_mm: 120.000 x 64.000",
        'step_name "pcie_gen3_x4_nvme_adapter_reva_preliminary.step"',
    ):
        if token not in roundtrip_log:
            issues.append(
                Issue(
                    evidence / "step_reimport_native_log.txt",
                    1,
                    "<content>",
                    "ERROR",
                    f"missing native round-trip token {token!r}",
                )
            )

    with placement.open("r", encoding="utf-8-sig", newline="") as handle:
        placement_rows = list(csv.DictReader(handle))
    placed = {
        (row.get("Reference") or "").strip()
        for row in placement_rows
        if (row.get("Reference") or "").strip()
    }
    with bom.open("r", encoding="utf-8-sig", newline="") as handle:
        bom_refs: set[str] = set()
        for row in csv.DictReader(handle):
            if (row.get("Assembly_Disposition") or "").strip() == "PCB_Feature":
                continue
            bom_refs.update(expand_bom_references(row.get("Reference_Designator") or ""))
    missing = sorted(bom_refs - placed)
    if missing:
        issues.append(
            Issue(placement, 1, "Reference", "ERROR", f"BOM references not represented: {missing}")
        )
    if "SSD1" not in placed:
        issues.append(Issue(placement, 1, "Reference", "ERROR", "SSD1 assembly envelope missing"))

    placement_symbols: Counter[tuple[str, float, float, float]] = Counter()
    for row_number, row in enumerate(placement_rows, start=2):
        try:
            numeric_values = {
                field: parse_nonnegative_finite(
                    row.get(field) or "", f"placement {field}"
                )
                for field in (
                    "X_mm",
                    "Y_mm",
                    "Rotation_deg",
                    "Z_Min_mm",
                    "Z_Max_mm",
                )
            }
            if numeric_values["Z_Max_mm"] < numeric_values["Z_Min_mm"]:
                raise ValueError(
                    "placement Z_Max_mm must be greater than or equal to Z_Min_mm"
                )
            key = (
                (row.get("Body_Definition") or "").strip(),
                round(numeric_values["X_mm"], 4),
                round(numeric_values["Y_mm"], 4),
                round(numeric_values["Rotation_deg"], 3),
            )
        except ValueError as exc:
            issues.append(
                Issue(
                    placement,
                    row_number,
                    "X_mm/Y_mm/Rotation_deg/Z_Min_mm/Z_Max_mm",
                    "ERROR",
                    str(exc),
                )
            )
            continue
        placement_symbols[key] += 1
    board_symbols, native_symbol_issues = checked_native_symbol_counter(native_symbols)
    issues.extend(native_symbol_issues)
    if board_symbols is not None:
        for key, count in sorted((placement_symbols - board_symbols).items()):
            issues.append(
                Issue(
                    placement,
                    1,
                    "Body_Definition/X_mm/Y_mm/Rotation_deg",
                    "ERROR",
                    f"placement not found in native audit: {key} x{count}",
                )
            )
        for key, count in sorted((board_symbols - placement_symbols).items()):
            issues.append(
                Issue(
                    native_symbols,
                    1,
                    "<content>",
                    "ERROR",
                    f"native symbol not represented in placement manifest: {key} x{count}",
                )
            )

    with artifact_manifest.open("r", encoding="utf-8-sig", newline="") as handle:
        artifact_rows = list(csv.DictReader(handle))
    artifact_index, artifact_index_issues = build_artifact_manifest_index(
        artifact_rows, artifact_manifest
    )
    issues.extend(artifact_index_issues)
    board_hash = sha256(board)
    for row_number, row in enumerate(artifact_rows, start=2):
        issues.extend(
            validate_artifact_manifest_row(
                root, artifact_manifest, row_number, row, board_hash
            )
        )

    with collision.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    cases = {(row.get("Case_ID") or "").strip() for row in rows}
    if cases != EXPECTED_CASES:
        issues.append(
            Issue(
                collision,
                1,
                "Case_ID",
                "ERROR",
                f"expected {sorted(EXPECTED_CASES)}, got {sorted(cases)}",
            )
        )
    duplicates = duplicate_case_ids(rows)
    if duplicates:
        issues.append(
            Issue(collision, 1, "Case_ID", "ERROR", f"duplicate collision cases: {duplicates}")
        )
    if len(rows) != len(EXPECTED_CASES):
        issues.append(
            Issue(
                collision,
                1,
                "Case_ID",
                "ERROR",
                f"expected exactly {len(EXPECTED_CASES)} rows, got {len(rows)}",
            )
        )
    for row_number, row in enumerate(rows, start=2):
        for field in REQUIRED_COLLISION_FIELDS:
            if not (row.get(field) or "").strip():
                issues.append(Issue(collision, row_number, field, "ERROR", "field must not be blank"))
        case_id = (row.get("Case_ID") or "").strip()
        result = (row.get("Result") or "").strip()
        if result not in ALLOWED_RESULTS:
            issues.append(
                Issue(collision, row_number, "Result", "ERROR", f"unsupported result {result!r}")
            )
        evidence_value = (row.get("Evidence_File") or "").strip()
        issues.extend(
            validate_collision_evidence(
                root,
                collision,
                row_number,
                evidence_value,
                artifact_index,
            )
        )
        contract = CASE_CONTRACTS.get(case_id, {})
        for field, expected in contract.items():
            actual = (row.get(field) or "").strip()
            if actual != expected:
                issues.append(
                    Issue(
                        collision,
                        row_number,
                        field,
                        "ERROR",
                        f"{case_id} requires {expected!r}, got {actual!r}",
                    )
                )
        status = (row.get("Status") or "").strip()
        if result.startswith("Blocked_") and status != "Not_Yet_Measured":
            issues.append(
                Issue(
                    collision,
                    row_number,
                    "Status",
                    "ERROR",
                    "blocked collision case must be Not_Yet_Measured",
                )
            )
        if result.startswith("Blocked_") and (
            row.get("Measured_Clearance_mm") or ""
        ).strip().upper() not in {"N/A", "TBD"}:
            issues.append(
                Issue(
                    collision,
                    row_number,
                    "Measured_Clearance_mm",
                    "ERROR",
                    "blocked collision case must not claim a measured clearance",
                )
            )
        if result.startswith("Preliminary_") and status != "Engineering_Assumption":
            issues.append(
                Issue(
                    collision,
                    row_number,
                    "Status",
                    "ERROR",
                    "preliminary collision result must be Engineering_Assumption",
                )
            )
        collision_numbers: dict[str, float | None] = {}
        collision_numbers_valid = True
        for field in (
            "Rule_mm",
            "Measured_Clearance_mm",
            "Tolerance_mm",
        ):
            try:
                collision_numbers[field] = parse_collision_number(
                    row.get(field) or ""
                )
            except ValueError as exc:
                collision_numbers_valid = False
                issues.append(
                    Issue(
                        collision,
                        row_number,
                        field,
                        "ERROR",
                        str(exc),
                    )
                )
        if result == "Preliminary_Clear" and case_id != "3D-08":
            if collision_numbers_valid:
                rule = collision_numbers["Rule_mm"]
                measured = collision_numbers["Measured_Clearance_mm"]
                tolerance = collision_numbers["Tolerance_mm"]
                if rule is None or measured is None or tolerance is None:
                    issues.append(
                        Issue(
                            collision,
                            row_number,
                            "Rule_mm/Measured_Clearance_mm/Tolerance_mm",
                            "ERROR",
                            "preliminary clearance requires numeric rule, measurement and tolerance",
                        )
                    )
                elif not has_screening_margin(rule, measured, tolerance):
                    issues.append(
                        Issue(
                            collision,
                            row_number,
                            "Measured_Clearance_mm",
                            "ERROR",
                            "measured clearance is below rule plus tolerance",
                        )
                    )
        revisions = (row.get("Model_Revisions") or "").upper()
        if result == "Pass":
            issues.append(
                Issue(
                    collision,
                    row_number,
                    "Result",
                    "ERROR",
                    "Pass is prohibited in the preliminary delivery",
                )
            )
        if "PRELIM" in revisions and result not in ALLOWED_RESULTS:
            issues.append(
                Issue(
                    collision,
                    row_number,
                    "Result",
                    "ERROR",
                    "preliminary model cannot carry a release result",
                )
            )

    return issues


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    if not root.is_dir():
        print(f"ERROR: project root not found: {root}", file=sys.stderr)
        return 2
    try:
        issues = validate(root)
    except (OSError, UnicodeError, csv.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for issue in issues:
        print(issue.format())
    print(f"Checked preliminary 3D delivery; {len(issues)} issue(s).")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
