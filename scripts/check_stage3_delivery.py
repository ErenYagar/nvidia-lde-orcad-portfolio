"""Audit the Stage 3 routing/manufacturing candidate without parsing .brd binary data."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def read_audit(path: Path) -> dict[str, int]:
    text = path.read_text(encoding="utf-8")
    result: dict[str, int] = {}
    for key in (
        "DRC_COUNT",
        "TOTAL_UNCONNECTED_CONNECTIONS",
        "NETS_WITH_UNCONNECTED_CONNECTIONS",
    ):
        match = re.search(rf"^{key}\|(\d+)$", text, re.MULTILINE)
        if not match:
            raise ValueError(f"{path}: missing {key}")
        result[key] = int(match.group(1))
    collection = re.search(
        r"^(?:RAT_OBJECT_COLLECTION_COUNT|RAT_OBJECT_COUNT)\|(\d+)$",
        text,
        re.MULTILINE,
    )
    active = re.search(r"^ACTIVE_RAT_OBJECT_COUNT\|(\d+)$", text, re.MULTILINE)
    if not collection or not active:
        raise ValueError(f"{path}: missing collection or active rat count")
    result["RAT_OBJECT_COLLECTION_COUNT"] = int(collection.group(1))
    result["ACTIVE_RAT_OBJECT_COUNT"] = int(active.group(1))
    result["UNCONNECTED_PCIE_NETS"] = len(
        re.findall(r"^NET\|PCIE_[^|]+\|UNCONNECTED\|[1-9]\d*\|", text, re.MULTILINE)
    )
    return result


def count_csv_value(path: Path, columns: tuple[str, ...], value: str) -> int:
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = csv.DictReader(stream)
        return sum(
            1
            for row in rows
            if any(row.get(column, "").strip() == value for column in columns)
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()

    board = root / (
        "pcb/allegro/stage3/"
        "pcie_gen3_x4_nvme_adapter_reva_stage3_route_revi_3d_mapped.brd"
    )
    audit_path = root / "pcb/allegro/stage3/stage3_routed_candidate_audit.txt"
    manufacturing = root / "manufacturing/stage3_review"
    pspice_out = root / "pspice/stage3/pw01_recovery_closure_132u_8p2.out"
    mapping = root / "pcb/3d_model_mapping.csv"
    diffpairs = root / "pcb/differential_pairs.csv"
    mapping_inventory = root / "pcb/allegro/stage3/stage3_3d_mapping_inventory.txt"
    assembly_step = root / "manufacturing/mcad/pcie_gen3_x4_nvme_adapter_reva_stage3_digital_release_candidate.step"
    roundtrip_dra = root / "evidence/stage3/3d/roundtrip/pcie_gen3_x4_nvme_adapter_reva_stage3_step_reimport.dra"
    roundtrip_log = root / "evidence/stage3/3d/roundtrip/stage3_step_reimport_native_log.txt"
    render_manifest = root / "evidence/stage3/3d/stage3_portfolio_render_manifest.json"

    audit = read_audit(audit_path)
    gerbers = sorted(manufacturing.glob("*.art"))
    drills = sorted(manufacturing.glob("*.drl"))
    ipc2581 = manufacturing / (
        "pcie_gen3_x4_nvme_adapter_reva_stage3_review_ipc2581.xml"
    )
    ipc356 = manufacturing / "pcie_gen3_x4_nvme_adapter_reva_stage3_review.ipc"
    pspice_concluded = (
        pspice_out.is_file()
        and "JOB CONCLUDED" in pspice_out.read_text(encoding="utf-8", errors="replace")
    )

    pending_models = count_csv_value(
        mapping,
        ("Model_Status", "Mapping_Status", "Collision_Check_Status"),
        "Pending_Human_Verification",
    )
    pending_pair_constraints = count_csv_value(
        diffpairs,
        ("Constraint_Status",),
        "Pending_Fabricator_Confirmation",
    )

    mapping_text = mapping_inventory.read_text(encoding="utf-8")
    mapped_symbols = len(re.findall(r"\|STEP_MAPPED\|t\|", mapping_text))
    unmapped_symbols = len(re.findall(r"\|STEP_MAPPED\|nil\|", mapping_text))
    board_edge_is_only_unmapped = (
        unmapped_symbols == 1
        and "NAME|PCIE_CEM_X4_EDGE_REVA" in mapping_text
        and "NAME|PCIE_CEM_X4_EDGE_REVA" in mapping_text.split("|STEP_MAPPED|nil|")[0].splitlines()[-1]
    )
    native_roundtrip_ok = (
        roundtrip_dra.is_file()
        and roundtrip_dra.stat().st_size > 0
        and roundtrip_log.is_file()
        and "NATIVE_DRA_STEP_ASSIGNMENT_OK"
        in roundtrip_log.read_text(encoding="utf-8")
    )
    render_data = json.loads(render_manifest.read_text(encoding="utf-8"))
    portfolio_views = render_data.get("views", [])
    portfolio_hash_bound = (
        assembly_step.is_file()
        and render_data.get("source_step_sha256") == sha256(assembly_step)
        and len(portfolio_views) >= 7
        and all(
            (root / view["file"]).is_file()
            and sha256(root / view["file"]) == view["sha256"]
            for view in portfolio_views
        )
    )

    gates = {
        "native_board_exists": board.is_file() and board.stat().st_size > 0,
        "native_drc_zero": audit["DRC_COUNT"] == 0,
        "all_connections_routed": audit["TOTAL_UNCONNECTED_CONNECTIONS"] == 0,
        "active_rats_zero": audit["ACTIVE_RAT_OBJECT_COUNT"] == 0,
        "all_pcie_nets_routed": audit["UNCONNECTED_PCIE_NETS"] == 0,
        "all_component_3d_bodies_mapped": mapped_symbols == 63
        and board_edge_is_only_unmapped,
        "assembly_step_generated": assembly_step.is_file()
        and assembly_step.stat().st_size > 0,
        "assembly_step_native_roundtrip": native_roundtrip_ok,
        "portfolio_views_hash_bound": portfolio_hash_bound,
        "constraint_manager_frozen": pending_pair_constraints == 0,
        "gerber_review_set_generated": len(gerbers) >= 12
        and all(path.stat().st_size > 0 for path in gerbers),
        "nc_drill_review_set_generated": len(drills) >= 2
        and all(path.stat().st_size > 0 for path in drills),
        "ipc2581_review_export_generated": ipc2581.is_file()
        and ipc2581.stat().st_size > 0,
        "ipc356_export_generated": ipc356.is_file() and ipc356.stat().st_size > 0,
        "pspice_recovery_closure_concluded": pspice_concluded,
        "exact_3d_mapping_closed": pending_models == 0,
        "physical_bringup_completed": False,
    }
    release_ready = all(gates.values())
    digital_gate_names = (
        "native_board_exists",
        "native_drc_zero",
        "all_connections_routed",
        "active_rats_zero",
        "all_pcie_nets_routed",
        "all_component_3d_bodies_mapped",
        "assembly_step_generated",
        "assembly_step_native_roundtrip",
        "portfolio_views_hash_bound",
    )
    digital_stage3_complete = all(gates[name] for name in digital_gate_names)

    artifacts: list[dict[str, object]] = []
    portfolio_files = [root / view["file"] for view in portfolio_views]
    for path in [
        board,
        assembly_step,
        roundtrip_dra,
        render_manifest,
        *portfolio_files,
        ipc2581,
        ipc356,
        *gerbers,
        *drills,
    ]:
        if path.is_file():
            artifacts.append(
                {
                    "path": path.relative_to(root).as_posix(),
                    "size": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )

    report = {
        "stage": "Stage 3",
        "candidate_status": "Digital_Stage3_Complete_Review_Only_Not_For_Fabrication"
        if digital_stage3_complete
        else "Digital_Stage3_Incomplete",
        "digital_stage3_complete": digital_stage3_complete,
        "release_ready": release_ready,
        "audit": audit,
        "pending_3d_rows": pending_models,
        "pending_fabricator_pair_constraints": pending_pair_constraints,
        "mapped_3d_symbols": mapped_symbols,
        "unmapped_board_defined_symbols": unmapped_symbols,
        "portfolio_view_count": len(portfolio_views),
        "gates": gates,
        "artifacts": artifacts,
        "claims": {
            "fab_ready": False,
            "pcie_compliance": False,
            "bench_qualified": False,
        },
    }

    if args.write_report:
        evidence = root / "evidence/stage3"
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / "stage3_delivery_gate.json").write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        lines = [
            "# Stage 3 delivery gate",
            "",
            f"- Digital Stage 3: `{'COMPLETE' if digital_stage3_complete else 'INCOMPLETE'}`",
            f"- Fabrication / physical release: `{'PASS' if release_ready else 'BLOCKED'}`",
            f"- Candidate status: `{report['candidate_status']}`",
            f"- Native DRC: {audit['DRC_COUNT']}",
            f"- Unconnected connections: {audit['TOTAL_UNCONNECTED_CONNECTIONS']}",
            f"- Active rats: {audit['ACTIVE_RAT_OBJECT_COUNT']}",
            f"- Unconnected PCIe nets: {audit['UNCONNECTED_PCIE_NETS']}",
            f"- Pending differential-pair fabricator constraints: {pending_pair_constraints}",
            f"- Pending 3D mapping/collision rows: {pending_models}",
            f"- Mapped component/mechanical 3D symbols: {mapped_symbols}; board-defined edge symbols without STEP: {unmapped_symbols}",
            f"- Hash-bound portfolio views: {len(portfolio_views)}",
            "",
            "## Gate results",
            "",
        ]
        lines.extend(
            f"- [{'x' if passed else ' '}] `{name}`"
            for name, passed in gates.items()
        )
        lines += [
            "",
            "Gerber, drill and IPC-2581 files are engineering-review outputs only.",
            "They must not be uploaded for fabrication while any release gate is open.",
            "",
        ]
        (evidence / "stage3_delivery_gate.md").write_text(
            "\n".join(lines), encoding="utf-8"
        )

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if digital_stage3_complete else 1


if __name__ == "__main__":
    raise SystemExit(main())
