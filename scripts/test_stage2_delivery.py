#!/usr/bin/env python3
"""Regression tests for the Stage 2 delivery validator."""

from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
FIXTURES = SCRIPT_DIR / "testdata" / "stage2"
MODULE_PATH = SCRIPT_DIR / "check_stage2_delivery.py"
SPEC = importlib.util.spec_from_file_location("check_stage2_delivery", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load {MODULE_PATH}")
stage2 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = stage2
SPEC.loader.exec_module(stage2)


class Stage2DeliveryTests(unittest.TestCase):
    def test_repository_progress_delivery_passes(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                "-X",
                "utf8",
                str(MODULE_PATH),
                "--root",
                str(PROJECT_ROOT),
                "--mode",
                "progress",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_repository_strict_delivery_remains_blocked(self) -> None:
        issues = stage2.validate_progress(PROJECT_ROOT, strict=True)
        messages = [issue.message for issue in issues]
        self.assertIn("CONTROLLED_SPEC_GATE is not closed", messages)

    def test_documented_access_exception_requires_explicit_opt_in(self) -> None:
        _, closed_without_exception = stage2.validate_gates(PROJECT_ROOT)
        issues, closed_with_exception = stage2.validate_gates(
            PROJECT_ROOT,
            allow_access_exception=True,
        )
        self.assertFalse(closed_without_exception)
        self.assertTrue(closed_with_exception)
        self.assertEqual([], issues)

    def test_blocked_collision_cases_are_complete_and_honest(self) -> None:
        self.assertEqual([], stage2.validate_collision_results(PROJECT_ROOT))

    def test_valid_status_and_consistency_fixtures_pass(self) -> None:
        self.assertEqual(
            [],
            stage2.validate_delivery_status(FIXTURES / "valid" / "delivery_status.csv"),
        )
        self.assertEqual(
            [],
            stage2.validate_component_consistency(
                FIXTURES / "valid" / "component_consistency.csv"
            ),
        )

    def test_false_routing_claim_fails(self) -> None:
        issues = stage2.validate_delivery_status(
            FIXTURES / "invalid" / "routing_claim" / "delivery_status.csv"
        )
        self.assertTrue(any(issue.field == "State" for issue in issues))

    def test_pad_mismatch_fails(self) -> None:
        issues = stage2.validate_component_consistency(
            FIXTURES / "invalid" / "pad_mismatch" / "component_consistency.csv"
        )
        self.assertTrue(any("counts differ" in issue.message for issue in issues))

    def test_unplaced_component_fails(self) -> None:
        issues = stage2.validate_component_consistency(
            FIXTURES / "invalid" / "unplaced" / "component_consistency.csv"
        )
        self.assertTrue(any(issue.field == "Placed" for issue in issues))

    def test_missing_physical_pin_fails(self) -> None:
        issues = stage2.validate_component_consistency(
            FIXTURES / "invalid" / "missing_pin" / "component_consistency.csv"
        )
        self.assertTrue(any("missing physical pin" in issue.message for issue in issues))

    def test_missing_evidence_and_stale_hash_fail(self) -> None:
        missing_root = FIXTURES / "invalid" / "missing_evidence"
        missing_issues = stage2.validate_artifact_manifest(
            missing_root, required_artifacts=set()
        )
        self.assertTrue(any(issue.message == "evidence missing" for issue in missing_issues))

        stale_root = FIXTURES / "invalid" / "stale_hash"
        stale_issues = stage2.validate_artifact_manifest(
            stale_root, required_artifacts=set()
        )
        self.assertTrue(any(issue.message == "stale hash" for issue in stale_issues))


if __name__ == "__main__":
    unittest.main()
