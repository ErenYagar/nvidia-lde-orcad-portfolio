#!/usr/bin/env python3
"""Unit tests for check_3d_models.py."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("check_3d_models.py")
SPEC = importlib.util.spec_from_file_location("check_3d_models", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load {MODULE_PATH}")
check_3d_models = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = check_3d_models
SPEC.loader.exec_module(check_3d_models)


HEADER = ",".join(check_3d_models.REQUIRED_COLUMNS)


def row(**overrides: str) -> str:
    values = {
        "Reference_or_Assembly": "J2",
        "Manufacturer": "Amphenol",
        "Manufacturer_Part_Number": "MDT420M01501",
        "Footprint_or_Board_Object": "AMPHENOL_MDT420M01501",
        "Canonical_Model_Name": "J2_PRELIMINARY_ENVELOPE",
        "Model_Format": "STEP",
        "Official_Model_Source": "https://example.com/official",
        "Official_Drawing_Source": "https://example.com/drawing",
        "Local_Model_Path": "TBD_LOGIN_REQUIRED",
        "File_SHA256": "TBD",
        "Units": "mm",
        "CAD_Datum": "M2_SEATING_PLANE",
        "Footprint_Datum": "TBD_J2_LIBRARY_ORIGIN",
        "Rotation_X_deg": "TBD",
        "Rotation_Y_deg": "TBD",
        "Rotation_Z_deg": "TBD",
        "Offset_X_mm": "TBD",
        "Offset_Y_mm": "TBD",
        "Offset_Z_mm": "TBD",
        "Nominal_Height_mm": "4.2",
        "Height_Source": "https://example.com/drawing",
        "Collision_Evidence_Path": "TBD_AFTER_3D_REVIEW",
        "Model_Status": "Pending_Human_Verification",
        "Mapping_Status": "Pending_Human_Verification",
        "Collision_Check_Status": "Planned",
        "Notes": "Pending exact model",
    }
    values.update(overrides)
    return ",".join(values[field] for field in check_3d_models.REQUIRED_COLUMNS)


class Check3dModelsTests(unittest.TestCase):
    def validate(self, content: str) -> list[check_3d_models.Issue]:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = root / "mapping.csv"
            path.write_text(content, encoding="utf-8", newline="\n")
            return check_3d_models.validate_mapping(path, root)

    def test_pending_row_is_valid(self) -> None:
        issues = self.validate(f"{HEADER}\n{row()}\n")
        self.assertEqual([], issues)

    def test_confirmed_model_requires_file_and_hash(self) -> None:
        issues = self.validate(
            f"{HEADER}\n{row(Model_Status='Confirmed_Official')}\n"
        )
        fields = {issue.field for issue in issues}
        self.assertIn("Local_Model_Path", fields)
        self.assertIn("File_SHA256", fields)

    def test_confirmed_mapping_requires_confirmed_model_and_transform(self) -> None:
        issues = self.validate(
            f"{HEADER}\n{row(Mapping_Status='Confirmed_Official')}\n"
        )
        fields = {issue.field for issue in issues}
        self.assertIn("Mapping_Status", fields)
        self.assertIn("Rotation_X_deg", fields)
        self.assertIn("Offset_Z_mm", fields)

    def test_confirmed_collision_requires_mapping_and_evidence(self) -> None:
        issues = self.validate(
            f"{HEADER}\n{row(Collision_Check_Status='Confirmed_Official')}\n"
        )
        fields = {issue.field for issue in issues}
        self.assertIn("Collision_Check_Status", fields)
        self.assertIn("Collision_Evidence_Path", fields)


if __name__ == "__main__":
    unittest.main()
