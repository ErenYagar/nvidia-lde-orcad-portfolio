#!/usr/bin/env python3
"""Unit tests for check_3d_delivery.py helpers."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("check_3d_delivery.py")
SPEC = importlib.util.spec_from_file_location("check_3d_delivery", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load {MODULE_PATH}")
check_3d_delivery = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = check_3d_delivery
SPEC.loader.exec_module(check_3d_delivery)


class Check3dDeliveryTests(unittest.TestCase):
    def test_semicolon_and_comma_reference_expansion(self) -> None:
        self.assertEqual(
            {"C1", "C2", "C3"},
            check_3d_delivery.expand_bom_references("C1; C2,C3"),
        )

    def test_expected_case_contract(self) -> None:
        self.assertEqual(
            {"3D-01", "3D-02", "3D-03", "3D-04", "3D-05", "3D-06", "3D-07", "3D-08"},
            check_3d_delivery.EXPECTED_CASES,
        )

    def test_duplicate_case_detection(self) -> None:
        rows = [{"Case_ID": "3D-01"}, {"Case_ID": "3D-01"}, {"Case_ID": "3D-02"}]
        self.assertEqual(["3D-01"], check_3d_delivery.duplicate_case_ids(rows))

    def test_collision_number_tokens(self) -> None:
        self.assertIsNone(check_3d_delivery.parse_collision_number("N/A"))
        self.assertIsNone(check_3d_delivery.parse_collision_number("TBD"))
        self.assertEqual(6.75, check_3d_delivery.parse_collision_number("6.750"))

    def test_collision_numbers_reject_nonfinite_and_negative_values(self) -> None:
        for raw in ("inf", "-inf", "nan", "1e309", "-0.001"):
            with self.subTest(raw=raw):
                with self.assertRaises(ValueError):
                    check_3d_delivery.parse_collision_number(raw)

    def test_preliminary_screening_margin(self) -> None:
        self.assertTrue(check_3d_delivery.has_screening_margin(0.5, 6.75, 0.2))
        self.assertFalse(check_3d_delivery.has_screening_margin(0.5, 0.6, 0.2))
        self.assertFalse(
            check_3d_delivery.has_screening_margin(0.5, float("inf"), 0.2)
        )
        self.assertFalse(
            check_3d_delivery.has_screening_margin(0.5, float("nan"), 0.2)
        )

    def test_malformed_native_audit_becomes_standard_issue(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "native_symbols.txt"
            path.write_text(
                "S!MECHANICAL!BOX!!0!1!0!1!not-a-number!0!0!\n",
                encoding="utf-8",
            )
            symbols, issues = check_3d_delivery.checked_native_symbol_counter(path)
        self.assertIsNone(symbols)
        self.assertEqual(1, len(issues))
        self.assertEqual("<content>", issues[0].field)
        self.assertEqual("ERROR", issues[0].severity)
        self.assertIn("must be finite and non-negative", issues[0].message)

    def test_collision_evidence_must_be_registered_in_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            evidence = root / "evidence.jpg"
            evidence.write_bytes(b"evidence")
            issues = check_3d_delivery.validate_collision_evidence(
                root,
                root / "collision_report.csv",
                2,
                "evidence.jpg",
                {},
            )
        self.assertEqual(1, len(issues))
        self.assertEqual("Evidence_File", issues[0].field)
        self.assertIn("not registered", issues[0].message)

    def test_manifest_hash_and_size_drift_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / "evidence.bin"
            artifact.write_bytes(b"current evidence")
            board_hash = "A" * 64
            row = {
                "Path": "evidence.bin",
                "Size_Bytes": "1",
                "SHA256": "0" * 64,
                "Source_Board_SHA256": board_hash,
            }
            issues = check_3d_delivery.validate_artifact_manifest_row(
                root,
                root / "artifact_manifest.csv",
                2,
                row,
                board_hash,
            )
        self.assertEqual(
            {"Size_Bytes", "SHA256"},
            {issue.field for issue in issues},
        )


if __name__ == "__main__":
    unittest.main()
