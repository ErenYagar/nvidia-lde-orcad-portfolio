#!/usr/bin/env python3
"""Validate the RevK interview digital closure without parsing the .brd binary."""

from __future__ import annotations

import argparse
import csv
import hashlib
import re
from pathlib import Path


BOARD_REL = Path(
    "pcb/allegro/stage3/"
    "pcie_gen3_x4_nvme_adapter_reva_stage3_route_revk_interview_digital_complete.brd"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def pipe_value(text: str, key: str) -> str:
    match = re.search(rf"^{re.escape(key)}\|([^\r\n]+)$", text, re.MULTILINE)
    if not match:
        raise ValueError(f"missing audit key: {key}")
    return match.group(1).strip()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        return list(csv.DictReader(stream))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args()
    root = args.root.resolve()
    failures: list[str] = []

    def require(condition: bool, message: str) -> None:
        if not condition:
            failures.append(message)

    board = root / BOARD_REL
    require(board.is_file() and board.stat().st_size > 0, "RevK native board missing or empty")
    board_hash = sha256(board) if board.is_file() else ""

    closure_path = root / "pcb/allegro/stage3/stage3_revk_closure_audit.txt"
    closure = closure_path.read_text(encoding="utf-8") if closure_path.is_file() else ""
    expected_zero = (
        "DRC_COUNT",
        "TOTAL_UNCONNECTED_CONNECTIONS",
        "ACTIVE_RAT_OBJECT_COUNT",
        "PCIE_UNCONNECTED_CONNECTIONS",
        "SHAPE_ISLAND_COUNT_FROM_NET_BRANCHES",
        "UNASSIGNED_SHAPE_COUNT",
    )
    for key in expected_zero:
        try:
            require(pipe_value(closure, key) == "0", f"{key} is not zero")
        except ValueError as exc:
            failures.append(str(exc))
    for key, minimum in (("GND1_SHAPES", 1), ("GND2_SHAPES", 1), ("PWR_SHAPES", 5)):
        try:
            require(int(pipe_value(closure, key)) >= minimum, f"{key} below {minimum}")
        except (ValueError, TypeError) as exc:
            failures.append(f"{key}: {exc}")
    require("POWER_AND_PLANE_ROUTING_STATUS|IMPLEMENTED_PRELIMINARY" in closure, "power/plane status not implemented")
    require("FAB_READY_CLAIM|PROHIBITED" in closure, "fab-ready prohibition missing")

    pairs_path = root / "pcb/allegro/stage3/stage3_revk_native_diffpair_reopen_audit.txt"
    pairs = pairs_path.read_text(encoding="utf-8") if pairs_path.is_file() else ""
    require(len(re.findall(r"^DIFF_PAIR\|[^|]+\|MEMBERS\|2\|", pairs, re.MULTILINE)) == 9, "native differential pair count/membership is not 9 x 2")
    require("GEOMETRY_STATUS|Pending_Fabricator_Confirmation" in pairs, "fabricator geometry blocker missing")

    manufacturing = root / "manufacturing/stage3_final_revk"
    gerbers = sorted(manufacturing.glob("*.art"))
    drills = sorted(manufacturing.glob("*.drl"))
    require(len(gerbers) == 14 and all(path.stat().st_size > 0 for path in gerbers), "expected 14 non-empty Gerber files")
    require(len(drills) == 2 and all(path.stat().st_size > 0 for path in drills), "expected two non-empty drill files")
    ipc2581 = manufacturing / "pcie_gen3_x4_nvme_adapter_reva_revk_final_ipc2581.xml"
    step = manufacturing / "pcie_gen3_x4_nvme_adapter_reva_revk_final_preliminary.step"
    require(ipc2581.is_file() and ipc2581.stat().st_size > 1_000_000, "IPC-2581 missing or unexpectedly small")
    require(step.is_file() and step.stat().st_size > 1_000_000, "assembly STEP missing or unexpectedly small")
    require(not list(manufacturing.glob("*.ipc")), "failed IPC-356 must be excluded from primary output")
    failed_ipc = manufacturing / "diagnostics/ipc356_failed/pcie_gen3_x4_nvme_adapter_reva_revk_final.ipc"
    require(failed_ipc.is_file() and failed_ipc.stat().st_size == 0, "IPC-356 failure evidence missing")
    require(len(list((manufacturing / "cam_preview").glob("*.png"))) >= 3, "CAM preview evidence incomplete")

    roundtrip = root / "evidence/stage3/3d/roundtrip_revk"
    roundtrip_dra = roundtrip / "pcie_gen3_x4_nvme_adapter_reva_revk_final_step_reimport.dra"
    roundtrip_log = roundtrip / "stage3_final_step_reimport_native_log.txt"
    require(roundtrip_dra.is_file() and roundtrip_dra.stat().st_size > 0, "STEP roundtrip DRA missing")
    require(roundtrip_log.is_file() and "NATIVE_DRA_STEP_ASSIGNMENT_OK" in roundtrip_log.read_text(encoding="utf-8"), "STEP roundtrip readback did not pass")

    sweep_path = root / "pspice/stage3/recovery_sweep/recovery_sweep_results.csv"
    sweep = read_csv(sweep_path) if sweep_path.is_file() else []
    require(len(sweep) == 27, "PSpice recovery sweep does not contain 27 cases")
    require(
        all(
            row.get("Status") == "Simulated"
            and row.get("Disposition") == "Not_Concluded_Runtime_Limit"
            for row in sweep
        ),
        "PSpice runtime-limited cases were not disclosed consistently",
    )
    pspice_record = root / "evidence/stage2/pspice/pw01_vendor_combined_run/run_record.md"
    pspice_text = pspice_record.read_text(encoding="utf-8") if pspice_record.is_file() else ""
    require("3.109 V" in pspice_text and "Fail_Recovery_Undershoot_5pct" in pspice_text, "governing PSpice recovery failure not disclosed")

    native_images = sorted((root / "evidence/stage3/3dx_native_revk").glob("*.png"))
    portfolio_images = sorted((root / "evidence/stage3/portfolio_revk").glob("*.png"))
    require(len(native_images) >= 8 and all(path.stat().st_size > 0 for path in native_images), "fewer than eight native RevK 3DX captures")
    require(len(portfolio_images) >= 8 and all(path.stat().st_size > 0 for path in portfolio_images), "fewer than eight RevK portfolio views")

    manifest_path = manufacturing / "artifact_manifest.csv"
    manifest = read_csv(manifest_path) if manifest_path.is_file() else []
    require(bool(manifest), "artifact manifest missing")
    for row in manifest:
        path = root / row.get("Path", "")
        require(row.get("Source_Board_SHA256") == board_hash, f"stale board hash in manifest: {row.get('Path')}")
        require(path.is_file() and path.stat().st_size > 0, f"manifest artifact missing or empty: {row.get('Path')}")
        if path.is_file() and path.stat().st_size > 0:
            require(row.get("SHA256") == sha256(path), f"artifact hash mismatch: {row.get('Path')}")

    constraint_text = (root / "evidence/stage3/constraint_manager_status.md").read_text(encoding="utf-8")
    require("Pending_Fabricator_Confirmation" in constraint_text and "9" in constraint_text, "Constraint Manager blocker/status incomplete")
    warning_review = root / "evidence/stage3/csv_warning_review.md"
    require(
        warning_review.is_file()
        and "31 warnings and 0 errors" in warning_review.read_text(encoding="utf-8"),
        "CSV warning review is missing",
    )
    gate_text = (root / "validation/stage3_fabrication_and_bringup_gate.md").read_text(encoding="utf-8")
    require("Interview_Digital_Complete" in gate_text, "interview completion status missing")
    require("Fabrication_Ready: `false`" in gate_text, "fabrication-ready false declaration missing")
    require("Not_Supported_By_Installed_Tool" in gate_text, "ODB++ limitation missing")

    if failures:
        for message in failures:
            print(f"ERROR: {message}")
        return 1
    print(f"PASS: Interview_Digital_Complete board_sha256={board_hash}")
    print("PASS: Fabrication_Ready=false (external gates remain open)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
