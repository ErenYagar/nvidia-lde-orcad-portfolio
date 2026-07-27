#!/usr/bin/env python3
"""Validate the Rev A supported-SSD evidence matrix."""

from __future__ import annotations

import argparse
import csv
import sys
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Sequence


REQUIRED_COLUMNS = (
    "Candidate_ID",
    "Manufacturer",
    "Exact_Model",
    "Capacity_GB",
    "Hardware_Revision",
    "Firmware",
    "Form_Factor",
    "Steady_Current_A",
    "Peak_Current_A",
    "Peak_Duration_us",
    "Power_Source_Type",
    "Power_Source_Document",
    "Power_Source_Revision",
    "Power_Source_Date",
    "Simulation_Evidence",
    "Mechanical_Evidence",
    "Bench_Evidence",
    "Link_Evidence",
    "Thermal_Evidence",
    "Disposition",
    "Exclusion_Reason",
    "Reviewer",
    "Review_Date",
    "Official_Project_Status",
    "Notes",
)

PROJECT_STATUSES = {
    "Confirmed_Official",
    "Engineering_Assumption",
    "Pending_Human_Verification",
    "Pending_Fabricator_Confirmation",
    "Planned",
    "Simulated",
    "Estimated",
    "Not_Yet_Measured",
}

DISPOSITIONS = {
    "Candidate",
    "Power_Screened",
    "Simulated",
    "Mechanically_Reviewed",
    "Bench_Qualified",
    "Supported_RevA",
    "Excluded",
}

EXPECTED_FORM_FACTOR = "M.2_2280_M_Key_NVMe"
OFFICIAL_POWER_SOURCE = "Official_Manufacturer"
STEADY_ENVELOPE_A = Decimal("5")
PEAK_ENVELOPE_A = Decimal("7")
PEAK_ENVELOPE_US = Decimal("100")

IDENTITY_FIELDS = (
    "Manufacturer",
    "Exact_Model",
    "Capacity_GB",
    "Hardware_Revision",
    "Firmware",
    "Form_Factor",
)
POWER_FIELDS = (
    "Steady_Current_A",
    "Peak_Current_A",
    "Peak_Duration_us",
)
POWER_SOURCE_FIELDS = (
    "Power_Source_Type",
    "Power_Source_Document",
    "Power_Source_Revision",
    "Power_Source_Date",
)
ALL_EVIDENCE_FIELDS = (
    "Simulation_Evidence",
    "Mechanical_Evidence",
    "Bench_Evidence",
    "Link_Evidence",
    "Thermal_Evidence",
)
PLACEHOLDERS = {
    "",
    "TBD",
    "N/A",
    "NA",
    "NONE",
    "NO_EVIDENCE",
    "NOT_RUN",
    "PLANNED",
    "NOT_YET_MEASURED",
    "PENDING_HUMAN_VERIFICATION",
    "UNSELECTED",
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


def _text(row: dict[str | None, str | list[str] | None], field: str) -> str:
    value = row.get(field)
    return value.strip() if isinstance(value, str) else ""


def _substantive(value: str) -> bool:
    return value.strip().upper() not in PLACEHOLDERS


def _positive_decimal(
    path: Path,
    row_number: int,
    row: dict[str | None, str | list[str] | None],
    field: str,
    issues: list[Issue],
) -> Decimal | None:
    value = _text(row, field)
    if not value:
        return None
    try:
        parsed = Decimal(value)
    except InvalidOperation:
        issues.append(Issue(path, row_number, field, "ERROR", "must be numeric"))
        return None
    if not parsed.is_finite() or parsed <= 0:
        issues.append(
            Issue(path, row_number, field, "ERROR", "must be greater than zero")
        )
        return None
    return parsed


def _check_date(
    path: Path,
    row_number: int,
    row: dict[str | None, str | list[str] | None],
    field: str,
    issues: list[Issue],
) -> None:
    value = _text(row, field)
    if not value:
        return
    try:
        date.fromisoformat(value)
    except ValueError:
        issues.append(
            Issue(path, row_number, field, "ERROR", "expected ISO date YYYY-MM-DD")
        )


def _require_substantive(
    path: Path,
    row_number: int,
    row: dict[str | None, str | list[str] | None],
    fields: tuple[str, ...],
    reason: str,
    issues: list[Issue],
) -> None:
    for field in fields:
        if not _substantive(_text(row, field)):
            issues.append(Issue(path, row_number, field, "ERROR", reason))


def _check_row(
    path: Path,
    row_number: int,
    row: dict[str | None, str | list[str] | None],
) -> list[Issue]:
    issues: list[Issue] = []
    disposition = _text(row, "Disposition")
    status = _text(row, "Official_Project_Status")

    if not _substantive(_text(row, "Candidate_ID")):
        issues.append(
            Issue(path, row_number, "Candidate_ID", "ERROR", "required value is blank")
        )
    if disposition not in DISPOSITIONS:
        issues.append(
            Issue(
                path,
                row_number,
                "Disposition",
                "ERROR",
                f"unsupported disposition {disposition!r}",
            )
        )
    if status not in PROJECT_STATUSES:
        issues.append(
            Issue(
                path,
                row_number,
                "Official_Project_Status",
                "ERROR",
                f"unsupported status {status!r}",
            )
        )

    steady = _positive_decimal(
        path, row_number, row, "Steady_Current_A", issues
    )
    peak = _positive_decimal(path, row_number, row, "Peak_Current_A", issues)
    duration = _positive_decimal(
        path, row_number, row, "Peak_Duration_us", issues
    )
    _positive_decimal(path, row_number, row, "Capacity_GB", issues)
    _check_date(path, row_number, row, "Power_Source_Date", issues)
    _check_date(path, row_number, row, "Review_Date", issues)

    has_power_value = any(_text(row, field) for field in POWER_FIELDS)
    if has_power_value:
        _require_substantive(
            path,
            row_number,
            row,
            POWER_SOURCE_FIELDS,
            "power value requires a traceable official source",
            issues,
        )
        if _text(row, "Power_Source_Type") != OFFICIAL_POWER_SOURCE:
            issues.append(
                Issue(
                    path,
                    row_number,
                    "Power_Source_Type",
                    "ERROR",
                    f"must be {OFFICIAL_POWER_SOURCE!r} when power values are present",
                )
            )

    if peak is not None and steady is not None and peak < steady:
        issues.append(
            Issue(
                path,
                row_number,
                "Peak_Current_A",
                "ERROR",
                "peak current cannot be less than steady current",
            )
        )

    over_envelope = (
        (steady is not None and steady > STEADY_ENVELOPE_A)
        or (peak is not None and peak > PEAK_ENVELOPE_A)
        or (
            peak is not None
            and peak > STEADY_ENVELOPE_A
            and duration is not None
            and duration > PEAK_ENVELOPE_US
        )
    )
    if over_envelope and disposition != "Excluded":
        issues.append(
            Issue(
                path,
                row_number,
                "Disposition",
                "ERROR",
                "candidate exceeds the 5 A steady or 7 A/100 us project envelope and must be Excluded",
            )
        )

    if disposition == "Excluded":
        _require_substantive(
            path,
            row_number,
            row,
            ("Exclusion_Reason",),
            "Excluded row requires a reason",
            issues,
        )

    screened_or_later = {
        "Power_Screened",
        "Simulated",
        "Mechanically_Reviewed",
        "Bench_Qualified",
        "Supported_RevA",
    }
    if disposition in screened_or_later:
        _require_substantive(
            path,
            row_number,
            row,
            IDENTITY_FIELDS + POWER_FIELDS + POWER_SOURCE_FIELDS,
            "disposition requires exact identity and official power-envelope evidence",
            issues,
        )
        if _text(row, "Form_Factor") != EXPECTED_FORM_FACTOR:
            issues.append(
                Issue(
                    path,
                    row_number,
                    "Form_Factor",
                    "ERROR",
                    f"must be {EXPECTED_FORM_FACTOR!r} or the row must be Excluded",
                )
            )

    evidence_by_disposition = {
        "Simulated": ("Simulation_Evidence",),
        "Mechanically_Reviewed": ("Mechanical_Evidence",),
        "Bench_Qualified": ALL_EVIDENCE_FIELDS,
        "Supported_RevA": ALL_EVIDENCE_FIELDS,
    }
    evidence_fields = evidence_by_disposition.get(disposition, ())
    _require_substantive(
        path,
        row_number,
        row,
        evidence_fields,
        f"{disposition} claim requires evidence",
        issues,
    )

    if disposition == "Supported_RevA":
        _require_substantive(
            path,
            row_number,
            row,
            ("Reviewer", "Review_Date"),
            "Supported_RevA claim requires reviewer sign-off",
            issues,
        )
        if status != "Confirmed_Official":
            issues.append(
                Issue(
                    path,
                    row_number,
                    "Official_Project_Status",
                    "ERROR",
                    "Supported_RevA claim must use Confirmed_Official",
                )
            )

    form_factor = _text(row, "Form_Factor")
    if (
        form_factor
        and form_factor != EXPECTED_FORM_FACTOR
        and disposition != "Excluded"
    ):
        issues.append(
            Issue(
                path,
                row_number,
                "Disposition",
                "ERROR",
                "non-2280 M-Key NVMe device must be Excluded",
            )
        )
    return issues


def check_matrix(path: Path) -> list[Issue]:
    issues: list[Issue] = []
    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            headers = reader.fieldnames
            if headers is None:
                return [Issue(path, 1, "<header>", "ERROR", "missing header")]
            duplicates = sorted(
                {field for field in headers if headers.count(field) > 1}
            )
            for field in duplicates:
                issues.append(
                    Issue(path, 1, field, "ERROR", "duplicate column name")
                )
            for field in REQUIRED_COLUMNS:
                if field not in headers:
                    issues.append(
                        Issue(path, 1, field, "ERROR", "required column missing")
                    )
            if issues:
                return issues

            for row_number, row in enumerate(reader, start=2):
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
                    continue
                if all(not _text(row, field) for field in REQUIRED_COLUMNS):
                    issues.append(
                        Issue(path, row_number, "<row>", "ERROR", "blank row")
                    )
                    continue
                issues.extend(_check_row(path, row_number, row))
    except (OSError, UnicodeError, csv.Error) as exc:
        raise RuntimeError(str(exc)) from exc
    return issues


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path)
    args = parser.parse_args(argv)
    if not args.matrix.is_file():
        print(
            f"{args.matrix}:0:<file>:ERROR:file not found",
            file=sys.stderr,
        )
        return 2
    try:
        issues = check_matrix(args.matrix)
    except RuntimeError as exc:
        print(
            f"{args.matrix}:0:<file>:ERROR:{exc}",
            file=sys.stderr,
        )
        return 2
    for issue in issues:
        print(issue.format())
    print(f"Checked supported-SSD matrix; {len(issues)} issue(s).")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
