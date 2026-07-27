#!/usr/bin/env python3
"""Unit tests for check_step_export.py."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("check_step_export.py")
SPEC = importlib.util.spec_from_file_location("check_step_export", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load {MODULE_PATH}")
check_step_export = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = check_step_export
SPEC.loader.exec_module(check_step_export)


def valid_step() -> str:
    products = "\n".join(
        f"#{index}=PRODUCT('{name}','{name}','',());"
        for index, name in enumerate(check_step_export.REQUIRED_PRODUCTS, start=10)
    )
    return (
        "ISO-10303-21;\n"
        "HEADER;\n"
        "FILE_SCHEMA(('AUTOMOTIVE_DESIGN'));\n"
        "ENDSEC;\n"
        "DATA;\n"
        "#1=(CONVERSION_BASED_UNIT('MILLIMETRE',#2)LENGTH_UNIT()NAMED_UNIT(#3));\n"
        "#4=MANIFOLD_SOLID_BREP('',#5);\n"
        "#5=CLOSED_SHELL('',());\n"
        "#6=NEXT_ASSEMBLY_USAGE_OCCURRENCE('','','',#7,#8,$);\n"
        f"{products}\n"
        "ENDSEC;\n"
        "END-ISO-10303-21;\n"
    )


class CheckStepExportTests(unittest.TestCase):
    def inspect(self, content: str):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "test.step"
            path.write_text(content, encoding="latin-1", newline="\n")
            return check_step_export.inspect_step(path)

    def test_valid_structural_export(self) -> None:
        issues, counts = self.inspect(valid_step())
        self.assertEqual([], issues)
        self.assertEqual(1, counts["solid_breps"])

    def test_missing_units_fails(self) -> None:
        issues, _ = self.inspect(valid_step().replace("MILLIMETRE", "UNKNOWN_UNIT"))
        self.assertIn("units", {issue.field for issue in issues})

    def test_missing_preliminary_body_fails(self) -> None:
        issues, _ = self.inspect(
            valid_step().replace("PlaceBound_M2_2280_PRELIM", "MISSING_BODY")
        )
        self.assertIn("product", {issue.field for issue in issues})


if __name__ == "__main__":
    unittest.main()
