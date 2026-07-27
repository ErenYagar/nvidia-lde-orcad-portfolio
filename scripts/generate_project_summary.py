#!/usr/bin/env python3
"""Generate a conservative Markdown project-status summary."""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Sequence


CHECKBOX_RE = re.compile(r"^\s*[-*]\s+\[([ xX])\]", re.MULTILINE)
PROFILE_ROW_RE = re.compile(r"^\|\s*([A-Z]{2}-\d{2}[A-Z]?)\s*\|")
SIMULATION_DISPOSED_STATUSES = {"Simulated", "Not_Supported_By_Model"}
CHECKLIST_FILES = (
    "docs/design_review_checklist.md",
    "schematic/erc_checklist.md",
    "pcb/drc_checklist.md",
    "manufacturing/gerber_release_checklist.md",
    "manufacturing/pick_and_place_checklist.md",
    "manufacturing/revision_release_checklist.md",
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _status(row: dict[str, str], field: str) -> str:
    return (row.get(field) or "").strip()


def _count_pending_rows(
    path: Path,
    status_fields: tuple[str, ...],
) -> int:
    if not path.is_file():
        return 0
    count = 0
    for row in read_rows(path):
        if any(
            _status(row, field) != "Confirmed_Official"
            for field in status_fields
        ):
            count += 1
    return count


def _count_simulation_profiles(root: Path) -> tuple[int, int]:
    """Count canonical profile rows rather than guessing from file count."""
    path = root / "pspice" / "simulation_plan.md"
    if not path.is_file():
        return 0, 0
    complete = 0
    total = 0
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        if not PROFILE_ROW_RE.match(line):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        total += 1
        status = cells[-1] if cells else ""
        if status in SIMULATION_DISPOSED_STATUSES:
            complete += 1
    return complete, total


def _cost_snapshot(root: Path) -> tuple[str, int]:
    """Return the declared priced subtotal and unresolved detail-row count."""
    path = root / "manufacturing" / "cost_estimate.csv"
    if not path.is_file():
        return "N/A", 0
    rows = read_rows(path)
    subtotal = next(
        (
            _status(row, "Extended_Cost_USD")
            for row in rows
            if _status(row, "Reference_Designator") == "PRICED_SUBTOTAL"
        ),
        "N/A",
    )
    unresolved = sum(
        _status(row, "Status") != "Estimated"
        for row in rows
        if _status(row, "Reference_Designator") != "PRICED_SUBTOTAL"
    )
    return subtotal or "N/A", unresolved


def build_summary(root: Path) -> str:
    bom_path = root / "manufacturing" / "bom.csv"
    bom_rows = read_rows(bom_path) if bom_path.is_file() else []
    component_line_items = len(bom_rows)
    component_quantity = sum(
        int(row["Quantity"])
        for row in bom_rows
        if (row.get("Quantity") or "").isdigit()
    )
    pending_pins = _count_pending_rows(
        root / "schematic" / "symbol_pinmap.csv",
        ("Human_Review_Status",),
    )
    pending_footprints = _count_pending_rows(
        root / "schematic" / "footprint_assignment.csv",
        ("Assignment_Status", "Human_Review_Status"),
    )
    pending_constraints = _count_pending_rows(
        root / "pcb" / "constraints.csv",
        ("Impedance_Status", "Assumption_Status", "Review_Status"),
    )
    simulation_complete, simulation_total = _count_simulation_profiles(root)
    priced_subtotal, unresolved_cost_rows = _cost_snapshot(root)
    test_matrix = root / "validation" / "test_matrix.csv"
    validation_rows = read_rows(test_matrix) if test_matrix.is_file() else []
    validation_complete = sum(
        _status(row, "Validation_Status") == "Confirmed_Official"
        for row in validation_rows
    )

    checked = 0
    total = 0
    for relative in CHECKLIST_FILES:
        path = root / relative
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8-sig")
        marks = CHECKBOX_RE.findall(text)
        total += len(marks)
        checked += sum(mark.lower() == "x" for mark in marks)
    completion = round(100 * checked / total, 1) if total else 0.0

    return "\n".join(
        [
            "# 專案狀態摘要",
            "",
            "> 此摘要由明確的 CSV 狀態、simulation profile 與 release checklist 產生；不是電氣、機構或實測證明。",
            "",
            f"- BOM line items／listed quantity：{component_line_items}／{component_quantity}",
            f"- 未確認 symbol Pin rows：{pending_pins}",
            f"- 未完成 footprint assignment rows：{pending_footprints}",
            f"- 未凍結 constraint rows：{pending_constraints}",
            (
                "- 已處置／待執行 simulation profiles："
                f"{simulation_complete}／{simulation_total - simulation_complete}"
            ),
            (
                "- 已完成／未完成 validation cases："
                f"{validation_complete}／{len(validation_rows) - validation_complete}"
            ),
            f"- 已定價 electronics subtotal：US${priced_subtotal}",
            f"- 尚未定價 cost rows：{unresolved_cost_rows}",
            f"- 明確 checklist completion：{checked}/{total} ({completion}%)",
            "",
            "`Not_Supported_By_Model` 計入已處置，但不代表已模擬或通過。",
            "完成率只計算上述固定 checklist 的勾選項；不以檔案數量推測。",
            "成本 subtotal 不含 PCB、待 CEM 決定的 safety-setting parts、機構、組裝、運費與稅費。",
            "",
        ]
    )


def main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if not root.is_dir():
        print(f"ERROR: root directory not found: {root}", file=sys.stderr)
        return 2
    try:
        summary = build_summary(root)
        if args.output is None:
            print(summary)
        else:
            args.output.write_text(summary, encoding="utf-8", newline="\n")
            print(f"Wrote {args.output}")
    except (OSError, UnicodeError, csv.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
