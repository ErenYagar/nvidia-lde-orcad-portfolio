#!/usr/bin/env python3
"""Validate Stage 2 batch progress or the strict placed/unrouted delivery."""

from __future__ import annotations

import argparse
import csv
import hashlib
import math
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

EXPECTED_PAGES = {
    "01_SYSTEM_OVERVIEW",
    "02_PCIE_EDGE_INTERFACE",
    "03_M2_NVME_INTERFACE",
    "04_POWER_INPUT_PROTECTION",
    "05_3V3_POWER",
    "06_POWER_TELEMETRY",
    "07_DEBUG_AND_TESTPOINTS",
}

REQUIRED_PROGRESS_ARTIFACTS = {
    "Stage2_Capture_OPJ",
    "Stage2_Capture_DSN",
    "Capture_DBO_Probe_Log",
    "Capture_DRC_API_Probe_Log",
    "Capture_Page_Audit",
    "Capture_Page_Audit_Log",
    "Capture_Native_DRC_Output",
    "Capture_Post_ERC_Reopen_Log",
    "PSpice_CLI_Circuit",
    "PSpice_CLI_Output",
    "PSpice_CLI_Log",
    "Allegro_DBStat_Log",
}

REQUIRED_DELIVERY_STATES = {
    "Routing": "Not_Started",
    "Fabrication_Release": "Not_Released",
    "PCIe_Compliance": "Not_Claimed",
}

STRICT_REPORTS = (
    "schematic/orcad/stage2/reports/erc_report.txt",
    "schematic/orcad/stage2/reports/annotation_report.txt",
    "schematic/orcad/stage2/reports/capture_bom.csv",
    "schematic/orcad/stage2/reports/physical_pin_report.csv",
    "schematic/orcad/stage2/reports/netlist_manifest.csv",
    "pcb/allegro/stage2/reports/component_report.csv",
    "pcb/allegro/stage2/reports/unconnected_report.txt",
    "pcb/allegro/stage2/reports/constraint_report.txt",
)

MANIFEST_COLUMNS = {
    "Artifact",
    "Path",
    "Size_Bytes",
    "SHA256",
    "Source_Path",
    "Source_SHA256",
    "Status",
    "Stage_State",
    "Notes",
}

CONSISTENCY_COLUMNS = {
    "Reference",
    "BOM_Present",
    "Symbol_Pin_Count",
    "Footprint_Pad_Count",
    "Netlist_Present",
    "Allegro_Present",
    "Placed",
    "Inside_Board",
    "Status",
    "Evidence",
}

EXPECTED_3D_CASES = {f"3D-{index:02d}" for index in range(1, 9)}
EXPECTED_PSPICE_PROFILES = {
    "ST-00",
    "ST-02A",
    "PW-01",
    "LT-03S",
    "EF-01",
    "AC-01",
    "MC-01",
}
ALLOWED_3D_RESULTS = {
    "Pass",
    "Preliminary_Clear",
    "Preliminary_Collision",
    "Blocked_Missing_Exact_Model",
    "Blocked_3DX_Interactive_License",
}
COLLISION_COLUMNS = {
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
}
THREED_MANIFEST_COLUMNS = {
    "View_ID",
    "Path",
    "Size_Bytes",
    "SHA256",
    "Source_Board_SHA256",
    "View",
    "Wrapper_Visible",
    "Stage_State",
    "Status",
    "Notes",
}


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


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest().upper()


def read_text_auto(path: Path) -> str:
    data = path.read_bytes()
    if data.startswith((b"\xff\xfe", b"\xfe\xff")):
        return data.decode("utf-16", errors="replace")
    return data.decode("utf-8-sig", errors="replace")


def read_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            return [], []
        return reader.fieldnames, list(reader)


def validate_baseline(root: Path) -> list[Issue]:
    path = root / "stage2/baseline_manifest.csv"
    if not path.is_file():
        return [Issue(path, 0, "<file>", "ERROR", "baseline manifest missing")]
    _, rows = read_rows(path)
    issues: list[Issue] = []
    for row_number, row in enumerate(rows, start=2):
        relative = (row.get("Path") or "").strip()
        artifact = root / relative
        if not artifact.is_file():
            issues.append(Issue(path, row_number, "Path", "ERROR", "artifact missing"))
            continue
        if str(artifact.stat().st_size) != (row.get("Size_Bytes") or "").strip():
            issues.append(
                Issue(path, row_number, "Size_Bytes", "ERROR", "baseline size drift")
            )
        if sha256(artifact) != (row.get("SHA256") or "").strip().upper():
            issues.append(
                Issue(path, row_number, "SHA256", "ERROR", "baseline hash drift")
            )
        if artifact.suffix.lower() == ".pdf":
            with artifact.open("rb") as handle:
                if handle.read(5) != b"%PDF-":
                    issues.append(
                        Issue(
                            path,
                            row_number,
                            "Path",
                            "ERROR",
                            "claimed PDF does not have PDF magic",
                        )
                    )
    return issues


def validate_gates(
    root: Path,
    allow_access_exception: bool = False,
) -> tuple[list[Issue], bool]:
    path = root / "stage2/input_gate.csv"
    if not path.is_file():
        return [Issue(path, 0, "<file>", "ERROR", "input Gate file missing")], False
    _, rows = read_rows(path)
    issues: list[Issue] = []
    by_id: dict[str, dict[str, str]] = {}
    for row_number, row in enumerate(rows, start=2):
        gate_id = (row.get("Gate_ID") or "").strip()
        status = (row.get("Status") or "").strip()
        if not gate_id:
            issues.append(Issue(path, row_number, "Gate_ID", "ERROR", "blank Gate ID"))
        elif gate_id in by_id:
            issues.append(
                Issue(path, row_number, "Gate_ID", "ERROR", "duplicate Gate ID")
            )
        by_id[gate_id] = row
        if status not in STATUS_VALUES:
            issues.append(
                Issue(path, row_number, "Status", "ERROR", "unsupported status")
            )
    controlled_closed = all(
        (by_id.get(gate_id, {}).get("Status") or "").strip()
        == "Confirmed_Official"
        for gate_id in ("G1-01", "G1-02")
    )
    if not controlled_closed and allow_access_exception:
        exception = root / "stage2/CONTROLLED_SPEC_ACCESS_EXCEPTION.md"
        exception_rows = [by_id.get(gate_id, {}) for gate_id in ("G1-01", "G1-02")]
        exception_is_explicit = (
            exception.is_file()
            and all(
                (row.get("Status") or "").strip() == "Pending_Human_Verification"
                and "exception recorded"
                in (row.get("Current_State") or "").strip().lower()
                for row in exception_rows
            )
        )
        if exception_is_explicit:
            controlled_closed = True
        else:
            issues.append(
                Issue(
                    path,
                    1,
                    "Status",
                    "ERROR",
                    "controlled-spec access exception is incomplete",
                )
            )
    return issues, controlled_closed


def validate_artifact_manifest(
    root: Path,
    required_artifacts: set[str] | None = None,
) -> list[Issue]:
    path = root / "stage2/artifact_manifest.csv"
    if not path.is_file():
        return [Issue(path, 0, "<file>", "ERROR", "artifact manifest missing")]
    headers, rows = read_rows(path)
    issues: list[Issue] = []
    missing_columns = MANIFEST_COLUMNS - set(headers)
    for field in sorted(missing_columns):
        issues.append(Issue(path, 1, field, "ERROR", "required column missing"))
    if missing_columns:
        return issues

    artifact_ids: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        artifact_id = (row.get("Artifact") or "").strip()
        if artifact_id in artifact_ids:
            issues.append(
                Issue(path, row_number, "Artifact", "ERROR", "duplicate artifact ID")
            )
        artifact_ids.add(artifact_id)
        status = (row.get("Status") or "").strip()
        if status not in STATUS_VALUES:
            issues.append(
                Issue(path, row_number, "Status", "ERROR", "unsupported status")
            )
        relative = (row.get("Path") or "").strip()
        artifact = root / relative
        if not relative or not artifact.is_file():
            issues.append(Issue(path, row_number, "Path", "ERROR", "evidence missing"))
            continue
        if str(artifact.stat().st_size) != (row.get("Size_Bytes") or "").strip():
            issues.append(Issue(path, row_number, "Size_Bytes", "ERROR", "size drift"))
        if sha256(artifact) != (row.get("SHA256") or "").strip().upper():
            issues.append(Issue(path, row_number, "SHA256", "ERROR", "stale hash"))

        source_relative = (row.get("Source_Path") or "").strip()
        source_hash = (row.get("Source_SHA256") or "").strip().upper()
        if source_relative:
            source = root / source_relative
            if not source.is_file():
                issues.append(
                    Issue(path, row_number, "Source_Path", "ERROR", "source missing")
                )
            elif source_hash != sha256(source):
                issues.append(
                    Issue(
                        path,
                        row_number,
                        "Source_SHA256",
                        "ERROR",
                        "source hash drift",
                    )
                )

    required = REQUIRED_PROGRESS_ARTIFACTS if required_artifacts is None else required_artifacts
    for artifact_id in sorted(required - artifact_ids):
        issues.append(
            Issue(path, 1, "Artifact", "ERROR", f"required artifact missing: {artifact_id}")
        )
    return issues


def validate_delivery_status(path: Path) -> list[Issue]:
    if not path.is_file():
        return [Issue(path, 0, "<file>", "ERROR", "delivery status missing")]
    _, rows = read_rows(path)
    issues: list[Issue] = []
    by_item: dict[str, tuple[int, dict[str, str]]] = {}
    for row_number, row in enumerate(rows, start=2):
        item = (row.get("Item") or "").strip()
        by_item[item] = (row_number, row)
        status = (row.get("Status") or "").strip()
        if status not in STATUS_VALUES:
            issues.append(
                Issue(path, row_number, "Status", "ERROR", "unsupported status")
            )
    for item, expected_state in REQUIRED_DELIVERY_STATES.items():
        record = by_item.get(item)
        if record is None:
            issues.append(Issue(path, 1, "Item", "ERROR", f"missing item {item}"))
            continue
        row_number, row = record
        state = (row.get("State") or "").strip()
        if state != expected_state:
            issues.append(
                Issue(
                    path,
                    row_number,
                    "State",
                    "ERROR",
                    f"{item} must remain {expected_state!r} in Stage 2",
                )
            )
        evidence = (row.get("Evidence") or "").strip()
        if not evidence:
            issues.append(
                Issue(path, row_number, "Evidence", "ERROR", "evidence path missing")
            )
    return issues


def validate_capture_audit(root: Path, strict: bool) -> list[Issue]:
    path = (
        root / "schematic/orcad/stage2/reports/capture_electrical_reopen_audit.csv"
        if strict
        else root / "evidence/stage2/batch/capture_page_audit.csv"
    )
    if not path.is_file():
        return [Issue(path, 0, "<file>", "ERROR", "Capture page audit missing")]
    _, rows = read_rows(path)
    issues: list[Issue] = []
    pages = {(row.get("Page_Name") or "").strip() for row in rows}
    if pages != EXPECTED_PAGES or len(rows) != len(EXPECTED_PAGES):
        issues.append(
            Issue(path, 1, "Page_Name", "ERROR", "expected exact seven-page hierarchy")
        )
    total_parts = 0
    for row_number, row in enumerate(rows, start=2):
        try:
            count = int((row.get("Part_Instance_Count") or "").strip())
            if count < 0:
                raise ValueError
            total_parts += count
        except ValueError:
            issues.append(
                Issue(path, row_number, "Part_Instance_Count", "ERROR", "invalid count")
            )
    if strict and total_parts == 0:
        issues.append(
            Issue(
                path,
                1,
                "Part_Instance_Count",
                "ERROR",
                "strict delivery cannot be an empty Capture skeleton",
            )
        )
    return issues


def validate_native_erc(root: Path) -> list[Issue]:
    path = (
        root
        / "schematic/orcad/stage2/native_25_1/"
        "PCIE_GEN3_X4_NVME_ADAPTER_REVA_STAGE2_ELECTRICAL.DRC"
    )
    if not path.is_file():
        return [Issue(path, 0, "<file>", "ERROR", "native Capture ERC output missing")]

    text = read_text_auto(path)
    issues: list[Issue] = []
    required_markers = (
        "Checking Schematic: SCHEMATIC1",
        "Checking Electrical Rules",
        "Checking Physical Rules",
        "Checking Entire Design: PCIE_GEN3_X4_NVME_ADAPTER_REVA_STAGE2_ELECTRICAL",
    )
    for marker in required_markers:
        if marker not in text:
            issues.append(
                Issue(path, 0, "<content>", "ERROR", f"native ERC marker missing: {marker}")
            )
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip().upper()
        if stripped.startswith("ERROR") or stripped.startswith("WARNING"):
            issues.append(
                Issue(path, line_number, "<content>", "ERROR", "native ERC contains a reported issue")
            )
    return issues


def validate_lt03_summary(root: Path) -> list[Issue]:
    path = root / "evidence/stage2/batch/lt03_charge_deficit_summary.csv"
    if not path.is_file():
        return [Issue(path, 0, "<file>", "ERROR", "LT-03 screen summary missing")]
    _, rows = read_rows(path)
    issues: list[Issue] = []
    expected_cases = {44, 66, 88, 150, 330, 680}
    found_cases: set[int] = set()
    for row_number, row in enumerate(rows, start=2):
        try:
            capacitance = int((row.get("COUT_Effective_uF") or "").strip())
            vout_min = float((row.get("VOUT_Min_V") or "").strip())
            vpre_min = float((row.get("VPRE_Min_V") or "").strip())
            shunt_current = float(
                (row.get("Shunt_Current_Max_A") or "").strip()
            )
            if not all(math.isfinite(value) for value in (vout_min, vpre_min, shunt_current)):
                raise ValueError
        except ValueError:
            issues.append(
                Issue(path, row_number, "<numeric>", "ERROR", "invalid LT-03 numeric value")
            )
            continue
        found_cases.add(capacitance)
        expected_five = "Pass" if vout_min >= 3.135 else "Fail"
        expected_ten = "Pass" if vout_min >= 2.970 else "Fail"
        if (row.get("Five_Percent_Screen") or "").strip() != expected_five:
            issues.append(
                Issue(path, row_number, "Five_Percent_Screen", "ERROR", "threshold result mismatch")
            )
        if (row.get("Ten_Percent_Screen") or "").strip() != expected_ten:
            issues.append(
                Issue(path, row_number, "Ten_Percent_Screen", "ERROR", "threshold result mismatch")
            )
        if (row.get("Model_Scope") or "").strip() != (
            "Conservative_Charge_Deficit_Not_Vendor_MacroModel"
        ):
            issues.append(
                Issue(path, row_number, "Model_Scope", "ERROR", "model scope claim changed")
            )
        if (row.get("Status") or "").strip() != "Simulated":
            issues.append(Issue(path, row_number, "Status", "ERROR", "screen was not simulated"))
        evidence = root / (row.get("Evidence") or "").strip()
        if not evidence.is_file():
            issues.append(Issue(path, row_number, "Evidence", "ERROR", "CSDF evidence missing"))
    if found_cases != expected_cases or len(rows) != len(expected_cases):
        issues.append(
            Issue(path, 1, "COUT_Effective_uF", "ERROR", "expected exact six-case sweep")
        )
    return issues


def validate_pspice_profiles(root: Path, strict: bool) -> list[Issue]:
    path = root / "pspice/stage2/profile_results.csv"
    if not path.is_file():
        return [Issue(path, 0, "<file>", "ERROR", "PSpice profile results missing")]
    headers, rows = read_rows(path)
    required_columns = {
        "Profile_ID",
        "Profile",
        "Model",
        "Input",
        "Output",
        "Raw_Result",
        "Result",
        "Status",
        "Key_Observation",
        "Limitations",
    }
    issues: list[Issue] = []
    for field in sorted(required_columns - set(headers)):
        issues.append(Issue(path, 1, field, "ERROR", "required column missing"))
    if issues:
        return issues

    by_id: dict[str, tuple[int, dict[str, str]]] = {}
    for row_number, row in enumerate(rows, start=2):
        profile_id = (row.get("Profile_ID") or "").strip()
        if profile_id in by_id:
            issues.append(
                Issue(path, row_number, "Profile_ID", "ERROR", "duplicate profile ID")
            )
        by_id[profile_id] = (row_number, row)
        if (row.get("Status") or "").strip() not in STATUS_VALUES:
            issues.append(
                Issue(path, row_number, "Status", "ERROR", "unsupported status")
            )
        if not (row.get("Key_Observation") or "").strip():
            issues.append(
                Issue(path, row_number, "Key_Observation", "ERROR", "observation missing")
            )

    if set(by_id) != EXPECTED_PSPICE_PROFILES:
        issues.append(
            Issue(
                path,
                1,
                "Profile_ID",
                "ERROR",
                "expected exact Stage 2 PSpice profile set",
            )
        )

    for profile_id in ("AC-01", "MC-01"):
        record = by_id.get(profile_id)
        if record and (record[1].get("Result") or "").strip() != (
            "Not_Supported_By_Model"
        ):
            issues.append(
                Issue(
                    path,
                    record[0],
                    "Result",
                    "ERROR",
                    f"{profile_id} must disclose model non-support",
                )
            )

    efuse = by_id.get("EF-01")
    if efuse and not (efuse[1].get("Result") or "").strip().startswith("Fail"):
        issues.append(
            Issue(
                path,
                efuse[0],
                "Result",
                "ERROR",
                "retained eFuse functional failure was hidden",
            )
        )

    if not strict:
        return issues

    combined = by_id.get("PW-01")
    if combined:
        row_number, row = combined
        if (row.get("Status") or "").strip() != "Simulated":
            issues.append(
                Issue(
                    path,
                    row_number,
                    "Status",
                    "ERROR",
                    "strict delivery requires the combined profile to be simulated",
                )
            )
        if (row.get("Result") or "").strip() in {"", "Running", "Planned"}:
            issues.append(
                Issue(
                    path,
                    row_number,
                    "Result",
                    "ERROR",
                    "combined profile has no final disposition",
                )
            )

    output = root / "pspice/stage2/pw01_buck_combined_1400us.out"
    if not output.is_file() or "JOB CONCLUDED" not in read_text_auto(output):
        issues.append(
            Issue(
                output,
                0,
                "<content>",
                "ERROR",
                "combined official-model PSpice run did not conclude",
            )
        )
    for relative in (
        "evidence/stage2/pspice/pw01_vendor_combined_run/"
        "pw01_overall_metrics.csv",
        "evidence/stage2/pspice/pw01_vendor_combined_run/"
        "pw01_window_metrics.csv",
    ):
        evidence = root / relative
        if not evidence.is_file():
            issues.append(
                Issue(evidence, 0, "<file>", "ERROR", "combined profile metrics missing")
            )
    return issues


def validate_component_consistency(path: Path) -> list[Issue]:
    if not path.is_file():
        return [Issue(path, 0, "<file>", "ERROR", "consistency report missing")]
    headers, rows = read_rows(path)
    issues: list[Issue] = []
    for field in sorted(CONSISTENCY_COLUMNS - set(headers)):
        issues.append(Issue(path, 1, field, "ERROR", "required column missing"))
    if issues:
        return issues
    for row_number, row in enumerate(rows, start=2):
        reference = (row.get("Reference") or "").strip()
        if not reference:
            issues.append(Issue(path, row_number, "Reference", "ERROR", "blank reference"))
        for field in (
            "BOM_Present",
            "Netlist_Present",
            "Allegro_Present",
            "Placed",
            "Inside_Board",
        ):
            if (row.get(field) or "").strip().upper() != "YES":
                issues.append(
                    Issue(path, row_number, field, "ERROR", f"{field} must be YES")
                )
        try:
            symbol_pins = int((row.get("Symbol_Pin_Count") or "").strip())
            footprint_pads = int((row.get("Footprint_Pad_Count") or "").strip())
            if symbol_pins <= 0:
                issues.append(
                    Issue(
                        path,
                        row_number,
                        "Symbol_Pin_Count",
                        "ERROR",
                        "missing physical pin mapping",
                    )
                )
            if footprint_pads != symbol_pins:
                issues.append(
                    Issue(
                        path,
                        row_number,
                        "Footprint_Pad_Count",
                        "ERROR",
                        "symbol pin and footprint pad counts differ",
                    )
                )
        except ValueError:
            issues.append(
                Issue(
                    path,
                    row_number,
                    "Symbol_Pin_Count/Footprint_Pad_Count",
                    "ERROR",
                    "counts must be integers",
                )
            )
    return issues


def validate_collision_results(root: Path) -> list[Issue]:
    path = root / "evidence/stage2/3d/stage2_collision_results.csv"
    if not path.is_file():
        return [Issue(path, 0, "<file>", "ERROR", "collision results missing")]
    headers, rows = read_rows(path)
    issues: list[Issue] = []
    for field in sorted(COLLISION_COLUMNS - set(headers)):
        issues.append(Issue(path, 1, field, "ERROR", "required column missing"))
    if issues:
        return issues

    seen: set[str] = set()
    for row_number, row in enumerate(rows, start=2):
        case_id = (row.get("Case_ID") or "").strip()
        if case_id in seen:
            issues.append(Issue(path, row_number, "Case_ID", "ERROR", "duplicate case"))
        seen.add(case_id)
        result = (row.get("Result") or "").strip()
        if result not in ALLOWED_3D_RESULTS:
            issues.append(
                Issue(path, row_number, "Result", "ERROR", "unsupported collision result")
            )
        status = (row.get("Status") or "").strip()
        if status not in STATUS_VALUES:
            issues.append(Issue(path, row_number, "Status", "ERROR", "unsupported status"))
        evidence = root / (row.get("Evidence_File") or "").strip()
        if not evidence.is_file():
            issues.append(
                Issue(path, row_number, "Evidence_File", "ERROR", "evidence file missing")
            )
        if result == "Pass":
            try:
                rule = float((row.get("Rule_mm") or "").strip())
                measured = float((row.get("Measured_Clearance_mm") or "").strip())
                tolerance = float((row.get("Tolerance_mm") or "").strip())
                if (
                    not all(math.isfinite(value) and value >= 0 for value in (
                        rule,
                        measured,
                        tolerance,
                    ))
                    or measured < rule + tolerance
                ):
                    raise ValueError
            except ValueError:
                issues.append(
                    Issue(
                        path,
                        row_number,
                        "Measured_Clearance_mm",
                        "ERROR",
                        "Pass requires measured clearance at or above rule plus tolerance",
                    )
                )
            if status != "Confirmed_Official":
                issues.append(
                    Issue(
                        path,
                        row_number,
                        "Status",
                        "ERROR",
                        "Pass requires Confirmed_Official evidence",
                    )
                )
    if seen != EXPECTED_3D_CASES or len(rows) != len(EXPECTED_3D_CASES):
        issues.append(
            Issue(path, 1, "Case_ID", "ERROR", "expected exact cases 3D-01 through 3D-08")
        )
    return issues


def validate_stage2_3d_package(root: Path, board_hash: str) -> list[Issue]:
    issues = validate_collision_results(root)
    manifest = root / "evidence/stage2/3d/stage2_3dx_manifest.csv"
    if not manifest.is_file():
        issues.append(Issue(manifest, 0, "<file>", "ERROR", "3DX manifest missing"))
    else:
        headers, rows = read_rows(manifest)
        for field in sorted(THREED_MANIFEST_COLUMNS - set(headers)):
            issues.append(Issue(manifest, 1, field, "ERROR", "required column missing"))
        if THREED_MANIFEST_COLUMNS <= set(headers):
            image_rows = 0
            for row_number, row in enumerate(rows, start=2):
                relative = (row.get("Path") or "").strip()
                artifact = root / relative
                if not artifact.is_file():
                    issues.append(
                        Issue(manifest, row_number, "Path", "ERROR", "3DX view missing")
                    )
                    continue
                if artifact.suffix.lower() in {".png", ".jpg", ".jpeg"}:
                    image_rows += 1
                if str(artifact.stat().st_size) != (row.get("Size_Bytes") or "").strip():
                    issues.append(
                        Issue(manifest, row_number, "Size_Bytes", "ERROR", "size drift")
                    )
                if sha256(artifact) != (row.get("SHA256") or "").strip().upper():
                    issues.append(
                        Issue(manifest, row_number, "SHA256", "ERROR", "stale hash")
                    )
                if (
                    (row.get("Source_Board_SHA256") or "").strip().upper()
                    != board_hash
                ):
                    issues.append(
                        Issue(
                            manifest,
                            row_number,
                            "Source_Board_SHA256",
                            "ERROR",
                            "view belongs to a different board hash",
                        )
                    )
                if (row.get("Wrapper_Visible") or "").strip().upper() != "NO":
                    issues.append(
                        Issue(
                            manifest,
                            row_number,
                            "Wrapper_Visible",
                            "ERROR",
                            "portfolio view must hide wrapper geometry",
                        )
                    )
                if "PLACED / UNROUTED" not in (
                    row.get("Stage_State") or ""
                ).strip().upper():
                    issues.append(
                        Issue(
                            manifest,
                            row_number,
                            "Stage_State",
                            "ERROR",
                            "view must identify Stage 2 as Placed / Unrouted",
                        )
                    )
            if image_rows < 7:
                issues.append(
                    Issue(manifest, 1, "Path", "ERROR", "at least seven 3DX views required")
                )

    roundtrip = root / "evidence/stage2/3d/stage2_step_roundtrip.csv"
    step = (
        root
        / "manufacturing/mcad/"
        "pcie_gen3_x4_nvme_adapter_reva_stage2_preliminary.step"
    )
    if not roundtrip.is_file():
        issues.append(Issue(roundtrip, 0, "<file>", "ERROR", "STEP round-trip missing"))
    if not step.is_file():
        issues.append(Issue(step, 0, "<file>", "ERROR", "Stage 2 assembly STEP missing"))
    return issues


def validate_critical_pins(root: Path) -> list[Issue]:
    issues: list[Issue] = []
    matrix = root / "schematic/connection_matrix.csv"
    _, matrix_rows = read_rows(matrix)
    for row_number, row in enumerate(matrix_rows, start=2):
        for component_field, pin_field in (
            ("Source_Component", "Source_Pin"),
            ("Destination_Component", "Destination_Pin"),
        ):
            component = (row.get(component_field) or "").strip()
            pin = (row.get(pin_field) or "").strip().upper()
            if component in {"J1", "J2"} and pin.startswith("PENDING_"):
                issues.append(
                    Issue(matrix, row_number, pin_field, "ERROR", "critical pin is pending")
                )
    pinmap = root / "schematic/symbol_pinmap.csv"
    _, pin_rows = read_rows(pinmap)
    for row_number, row in enumerate(pin_rows, start=2):
        component = (row.get("Component") or "").strip()
        pin = (row.get("Pin_Number") or "").strip().upper()
        if component in {"J1", "J2"} and pin.startswith("PENDING_"):
            issues.append(
                Issue(pinmap, row_number, "Pin_Number", "ERROR", "critical pin is pending")
            )
    return issues


def validate_progress(
    root: Path,
    strict: bool,
    allow_access_exception: bool = False,
) -> list[Issue]:
    issues = validate_baseline(root)
    gate_issues, controlled_closed = validate_gates(
        root,
        allow_access_exception=allow_access_exception,
    )
    issues.extend(gate_issues)
    issues.extend(validate_artifact_manifest(root))
    issues.extend(validate_delivery_status(root / "stage2/delivery_status.csv"))
    issues.extend(validate_capture_audit(root, strict))
    issues.extend(validate_native_erc(root))
    issues.extend(validate_lt03_summary(root))
    issues.extend(validate_pspice_profiles(root, strict))

    if strict:
        opj = (
            root
            / "schematic/orcad/stage2/native_25_1/"
            "pcie_gen3_x4_nvme_adapter_reva_stage2_electrical.opj"
        )
        dsn = (
            root
            / "schematic/orcad/stage2/native_25_1/"
            "PCIE_GEN3_X4_NVME_ADAPTER_REVA_STAGE2_ELECTRICAL.dsn"
        )
    else:
        opj = root / "schematic/orcad/stage2/pcie_gen3_x4_nvme_adapter_reva_stage2.opj"
        dsn = root / "schematic/orcad/stage2/PCIE_GEN3_X4_NVME_ADAPTER_REVA_STAGE2.DSN"
    for path in (opj, dsn):
        if not path.is_file():
            issues.append(Issue(path, 0, "<file>", "ERROR", "native Capture artifact missing"))

    pspice_output = root / "evidence/stage2/batch/work/pspice_probe/pspice_probe.out"
    if not pspice_output.is_file() or "JOB CONCLUDED" not in read_text_auto(
        pspice_output
    ):
        issues.append(
            Issue(pspice_output, 0, "<content>", "ERROR", "PSpice probe did not conclude")
        )
    dbstat = root / "evidence/stage2/batch/allegro_dbstat.log"
    if not dbstat.is_file() or "25.1" not in read_text_auto(dbstat):
        issues.append(
            Issue(dbstat, 0, "<content>", "ERROR", "Allegro 25.1 dbstat evidence missing")
        )

    if not strict:
        return issues

    if not controlled_closed:
        issues.append(
            Issue(
                root / "stage2/input_gate.csv",
                1,
                "Status",
                "ERROR",
                "CONTROLLED_SPEC_GATE is not closed",
            )
        )
    issues.extend(validate_critical_pins(root))
    issues.extend(
        validate_component_consistency(root / "stage2/component_consistency.csv")
    )

    assignments = root / "schematic/footprint_assignment.csv"
    _, assignment_rows = read_rows(assignments)
    for row_number, row in enumerate(assignment_rows, start=2):
        if (row.get("Assignment_Status") or "").strip() == "Planned":
            issues.append(
                Issue(assignments, row_number, "Assignment_Status", "ERROR", "footprint not assigned")
            )

    board = root / "pcb/allegro/stage2/pcie_gen3_x4_nvme_adapter_reva_stage2.brd"
    if not board.is_file():
        issues.append(Issue(board, 0, "<file>", "ERROR", "Stage 2 board missing"))
    for relative in STRICT_REPORTS:
        report = root / relative
        if not report.is_file():
            issues.append(Issue(report, 0, "<file>", "ERROR", "strict report missing"))

    if board.is_file():
        issues.extend(validate_stage2_3d_package(root, sha256(board)))
    return issues


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--mode",
        choices=("progress", "strict"),
        default="strict",
        help="progress accepts explicit blockers; strict requires full Stage 2 delivery",
    )
    parser.add_argument(
        "--allow-access-exception",
        action="store_true",
        help=(
            "accept the documented PCI-SIG/M.2 access exception for the "
            "portfolio delivery; this never authorizes a compliance claim"
        ),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = args.root.resolve()
    if not root.is_dir():
        print(f"ERROR: project root not found: {root}", file=sys.stderr)
        return 2
    try:
        issues = validate_progress(
            root,
            strict=args.mode == "strict",
            allow_access_exception=args.allow_access_exception,
        )
    except (OSError, UnicodeError, csv.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    for issue in issues:
        print(issue.format())
    print(f"Checked Stage 2 {args.mode} delivery; {len(issues)} issue(s).")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
