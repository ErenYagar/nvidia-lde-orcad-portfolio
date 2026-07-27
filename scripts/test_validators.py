#!/usr/bin/env python3
"""Basic regression tests for the CSV validator command-line tools."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import csv
import hashlib
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
VALID = SCRIPT_DIR / "testdata" / "valid"
INVALID = SCRIPT_DIR / "testdata" / "invalid"


def run_script(script: str, *arguments: Path | str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8",
            str(SCRIPT_DIR / script),
            *(str(arg) for arg in arguments),
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


class ValidatorTests(unittest.TestCase):
    def test_valid_bom_passes(self) -> None:
        result = run_script("check_bom_fields.py", VALID / "bom.csv")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_blank_mpn_fails(self) -> None:
        result = run_script(
            "check_bom_fields.py", INVALID / "bom_missing_mpn.csv"
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Manufacturer_Part_Number", result.stdout)

    def test_missing_column_fails_schema_validation(self) -> None:
        result = run_script(
            "check_bom_fields.py",
            INVALID / "bom_missing_column.csv",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Datasheet_Review_Status", result.stdout)

    def test_confirmed_critical_row_without_source_fails(self) -> None:
        fixture_root = INVALID / "missing_source"
        fixture = fixture_root / "schematic" / "connection_matrix.csv"
        result = run_script(
            "validate_csv.py",
            "--root",
            fixture_root,
            fixture,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Source_Document", result.stdout)

    def test_unsupported_status_fails(self) -> None:
        fixture_root = INVALID / "invalid_status"
        fixture = fixture_root / "schematic" / "connection_matrix.csv"
        result = run_script(
            "validate_csv.py",
            "--root",
            fixture_root,
            fixture,
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("unsupported status", result.stdout)

    def test_missing_file_returns_usage_error(self) -> None:
        result = run_script("validate_csv.py", INVALID / "does_not_exist.csv")
        self.assertEqual(result.returncode, 2)

    def test_discovery_excludes_frozen_release_snapshots(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            (root / "source.csv").write_text(
                "Name,Value\nsource,valid\n", encoding="utf-8"
            )
            release = root / "releases" / "frozen"
            release.mkdir(parents=True)
            (release / "empty_history.csv").write_text(
                "Name,Value\n", encoding="utf-8"
            )
            result = run_script("validate_csv.py", "--root", root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Checked 1 CSV file(s); 0 issue(s).", result.stdout)

    def test_duplicate_pin_fails(self) -> None:
        result = run_script(
            "check_duplicate_pins.py",
            INVALID / "connection_duplicate_pin.csv",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("conflicting nets", result.stdout)

    def test_invalid_net_fails(self) -> None:
        result = run_script(
            "check_net_names.py",
            INVALID / "connection_invalid_net.csv",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("invalid net name", result.stdout)

    def test_valid_connection_names_pass(self) -> None:
        result = run_script(
            "check_net_names.py", VALID / "connection_matrix.csv"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_summary_counts_profile_table_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            pspice = root / "pspice"
            pspice.mkdir()
            (pspice / "simulation_plan.md").write_text(
                "\n".join(
                    [
                        "| ID | Profile | Status |",
                        "|---|---|---|",
                        "| ST-01 | Startup | `Simulated` |",
                        "| LT-01 | Load step | `Planned` |",
                        "| AC-01 | Loop audit | `Not_Supported_By_Model` |",
                    ]
                ),
                encoding="utf-8",
            )
            manufacturing = root / "manufacturing"
            manufacturing.mkdir()
            (manufacturing / "cost_estimate.csv").write_text(
                "\n".join(
                    [
                        "Reference_Designator,Extended_Cost_USD,Status",
                        "U1,1.72,Estimated",
                        "J1,N/A,Pending_Fabricator_Confirmation",
                        "PRICED_SUBTOTAL,1.72,Estimated",
                    ]
                ),
                encoding="utf-8",
            )
            result = run_script("generate_project_summary.py", "--root", root)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("已處置／待執行 simulation profiles：2／1", result.stdout)
        self.assertIn(
            "Not_Supported_By_Model` 計入已處置",
            result.stdout,
        )
        self.assertIn("electronics subtotal：US$1.72", result.stdout)
        self.assertIn("尚未定價 cost rows：1", result.stdout)

    def test_source_manifest_hashes_vendor_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            models = root / "models"
            models.mkdir()
            model = models / "SLUM787A.ZIP"
            model.write_bytes(b"vendor-model")
            output = root / "manifest.csv"
            result = run_script(
                "generate_source_manifest.py",
                "--root",
                root,
                "--source-dir",
                models,
                "--output",
                output,
                "--access-date",
                "2026-07-23",
            )
            with output.open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(len(rows), 1)
        self.assertEqual(
            rows[0]["SHA256"],
            hashlib.sha256(b"vendor-model").hexdigest().upper(),
        )
        self.assertEqual(rows[0]["Status"], "Confirmed_Official")


if __name__ == "__main__":
    unittest.main()
