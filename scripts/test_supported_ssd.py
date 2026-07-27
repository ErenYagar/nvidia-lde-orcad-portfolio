#!/usr/bin/env python3
"""Regression tests for the supported-SSD matrix validator."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
FIXTURES = SCRIPT_DIR / "testdata" / "supported_ssd"


def run_validator(path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-B",
            "-X",
            "utf8",
            str(SCRIPT_DIR / "check_supported_ssd.py"),
            str(path),
        ],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


class SupportedSsdValidatorTests(unittest.TestCase):
    def test_repository_placeholder_passes_without_support_claim(self) -> None:
        result = run_validator(
            PROJECT_ROOT / "validation" / "supported_ssd_matrix.csv"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_valid_fixture_passes(self) -> None:
        result = run_validator(FIXTURES / "valid" / "matrix.csv")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_supported_claim_without_evidence_fails(self) -> None:
        result = run_validator(
            FIXTURES / "invalid" / "supported_without_evidence.csv"
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Simulation_Evidence:ERROR", result.stdout)
        self.assertIn("Reviewer:ERROR", result.stdout)

    def test_power_values_without_official_source_fail(self) -> None:
        result = run_validator(
            FIXTURES / "invalid" / "power_without_source.csv"
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Power_Source_Document:ERROR", result.stdout)

    def test_invalid_project_status_fails(self) -> None:
        result = run_validator(
            FIXTURES / "invalid" / "invalid_status.csv"
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Official_Project_Status:ERROR", result.stdout)

    def test_over_envelope_candidate_must_be_excluded(self) -> None:
        result = run_validator(
            FIXTURES / "invalid" / "over_envelope_candidate.csv"
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("Disposition:ERROR", result.stdout)
        self.assertIn("must be Excluded", result.stdout)

    def test_missing_file_is_usage_or_file_error(self) -> None:
        result = run_validator(FIXTURES / "missing.csv")
        self.assertEqual(result.returncode, 2)
        self.assertIn(":0:<file>:ERROR:file not found", result.stderr)


if __name__ == "__main__":
    unittest.main()
