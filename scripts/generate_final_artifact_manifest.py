#!/usr/bin/env python3
"""Generate hash-bound RevK interview-digital-complete manifests."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path


BOARD = Path(
    "pcb/allegro/stage3/"
    "pcie_gen3_x4_nvme_adapter_reva_stage3_route_revk_interview_digital_complete.brd"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def add_files(paths: list[Path], base: Path, pattern: str, recursive: bool = False) -> None:
    finder = base.rglob if recursive else base.glob
    paths.extend(path for path in finder(pattern) if path.is_file())


def classify(path: Path, root: Path) -> tuple[str, str, str, str]:
    rel = path.relative_to(root).as_posix()
    if rel.endswith(".brd"):
        return ("Native_Board", "OrCAD X PCB Professional Plus 25.1 S040", "Native database", "Interview_Digital_Complete")
    if "/3dx_native_revk/" in f"/{rel}":
        return ("Native_3DX_Evidence", "OrCAD X 3DX Canvas 25.1 S040", "Tool UI capture", "Confirmed_Current_Board")
    if "/portfolio_revk/" in f"/{rel}":
        return (
            "Portfolio_View",
            "Portfolio renderer",
            "Black background; presentation carry-forward; external placement/models unchanged from RevI to RevK",
            "Engineering_Assumption_Presentation_Only",
        )
    if rel.endswith(".step"):
        return ("Assembly_STEP", "OrCAD X 3DX Canvas 25.1 S040", "mm; STEP AP242; TOP/UPPER datum; internal conductors/vias excluded", "Preliminary_Mechanical")
    if rel.endswith(".xml") and "ipc2581" in rel.lower():
        return ("IPC2581", "OrCAD X PCB Editor 25.1 S040", "IPC-2581-C; mm; masks/paste/silkscreen included", "Engineering_Review_Not_For_Fabrication")
    if rel.endswith(".art"):
        return ("Gerber", "OrCAD X PCB Editor 25.1 S040", "Artwork batch export", "Engineering_Review_Not_For_Fabrication")
    if rel.endswith(".drl"):
        return ("NC_Drill", "OrCAD X PCB Editor 25.1 S040", "Excellon batch export; auto tool table retained", "Engineering_Review_Not_For_Fabrication")
    if "/cam_preview/" in f"/{rel}":
        return ("CAM_Preview", "OrCAD X PCB Editor 25.1 S040", "Native film view", "Engineering_Review")
    if "roundtrip_revk" in rel:
        return ("STEP_Roundtrip", "OrCAD X PCB Editor 25.1 S040", "Isolated DRA assignment/readback", "Native_DRA_STEP_Assignment_OK")
    if "recovery_sweep" in rel:
        return ("PSpice_Sweep", "PSpice 25.1", "15 s per-case runtime limit", "Not_Concluded_Runtime_Limit")
    if rel.endswith(".csv") and "bom" in rel.lower():
        return ("BOM", "Python 3.13", "Board-hash-bound review BOM", "Interview_Only")
    if rel.endswith(".csv") and ("pick_and_place" in rel.lower() or "placement" in rel.lower()):
        return ("Placement", "OrCAD X/Python 3.13", "Native placement export", "Preliminary_Not_For_Fabrication")
    return ("Report_or_Log", "OrCAD X/Python 3.13", "Audit or export evidence", "Recorded")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    board = root / BOARD
    board_hash = sha256(board)

    files: list[Path] = [
        board,
        root / "pcb/allegro/stage3/stage3_revk_closure_audit.txt",
        root / "pcb/allegro/stage3/stage3_revk_native_diffpair_reopen_audit.txt",
        root / "pcb/allegro/stage3/stage3_revk_shape_island_closure_report.txt",
        root / "evidence/stage2/pspice/pw01_vendor_combined_run/run_record.md",
        root / "pspice/stage3/recovery_sweep/recovery_sweep_results.csv",
        root / "evidence/stage3/constraint_manager_status.md",
        root / "evidence/stage3/csv_warning_review.md",
        root / "validation/stage3_fabrication_and_bringup_gate.md",
    ]
    manufacturing = root / "manufacturing/stage3_final_revk"
    for pattern in ("*.art", "*.drl", "*.xml", "*.step", "*.csv", "*.log", "*.txt", "*.md"):
        add_files(files, manufacturing, pattern)
    add_files(files, manufacturing / "cam_preview", "*.png")
    add_files(files, root / "evidence/stage3/3dx_native_revk", "*.png")
    add_files(files, root / "evidence/stage3/portfolio_revk", "*.png")
    add_files(files, root / "evidence/stage3/3d/roundtrip_revk", "*")

    unique = sorted(
        {
            path.resolve()
            for path in files
            if path.is_file()
            and path.stat().st_size > 0
            and "signoise.run" not in path.as_posix()
            and "diagnostics/ipc356_failed" not in path.as_posix()
            and path.name not in {
                "artifact_manifest.csv",
                "final_evidence_manifest.csv",
                "portfolio_final_manifest.csv",
            }
        },
        key=lambda path: path.relative_to(root).as_posix(),
    )

    output = manufacturing / "artifact_manifest.csv"
    fields = [
        "Category",
        "Path",
        "Size_Bytes",
        "SHA256",
        "Source_Board_SHA256",
        "Tool_Version",
        "Export_Options",
        "Artifact_State",
    ]
    with output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        for path in unique:
            category, tool, options, status = classify(path, root)
            writer.writerow(
                {
                    "Category": category,
                    "Path": path.relative_to(root).as_posix(),
                    "Size_Bytes": path.stat().st_size,
                    "SHA256": sha256(path),
                    "Source_Board_SHA256": board_hash,
                    "Tool_Version": tool,
                    "Export_Options": options,
                    "Artifact_State": status,
                }
            )

    evidence_manifest = root / "evidence/stage3/final_evidence_manifest.csv"
    evidence_rows = [
        row
        for row in csv.DictReader(output.open(newline="", encoding="utf-8"))
        if row["Category"]
        in {"Native_3DX_Evidence", "Portfolio_View", "CAM_Preview", "STEP_Roundtrip"}
    ]
    with evidence_manifest.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(evidence_rows)

    portfolio_manifest = root / "evidence/stage3/portfolio_final_manifest.csv"
    portfolio_rows = [row for row in evidence_rows if row["Category"] == "Portfolio_View"]
    with portfolio_manifest.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(portfolio_rows)

    print(f"BOARD_SHA256={board_hash}")
    print(f"ARTIFACTS={len(unique)}")
    print(f"NATIVE_3DX={sum(row['Category'] == 'Native_3DX_Evidence' for row in evidence_rows)}")
    print(f"PORTFOLIO={len(portfolio_rows)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
