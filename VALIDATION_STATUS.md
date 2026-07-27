# Public package validation status

Validation run on 2026-07-27 for the curated RevK interview package.

| Check | Result | Notes |
|---|---|---|
| `python scripts/validate_csv.py --root .` | PASS | 33 CSV files checked; 0 format issues. |
| `python scripts/check_bom_fields.py manufacturing/bom.csv` | PASS | Required manufacturer/MPN/package/quantity/reference/lifecycle fields present. |
| `python scripts/check_net_names.py schematic/connection_matrix.csv` | PASS | Naming and lane/sideband checks passed. |
| `python scripts/check_duplicate_pins.py ...` | PASS with review warnings | 0 errors; 31 shared-net duplicate-appearance warnings require engineering review. |
| `python -m unittest discover -s scripts -p 'test_*.py' -v` | PARTIAL | 42 tests passed; 3 Stage 2 repository-specific tests are not green because the public package intentionally excludes raw CSDF and historical Stage 2 evidence. |
| `python scripts/check_stage3_delivery.py --root .` | NOT USED AS A GATE | The legacy checker is hard-coded for the older RevI directory names. This public package is the RevK interview release; the native reports and current evidence are kept under the RevK paths. |

## Interpretation

This repository is an interview portfolio release, not a fabrication release. The published evidence preserves the actual limitations: the PSpice recovery case is disclosed, controlled fabricator stack-up confirmation is pending, some mechanical models are preliminary, and ODB++ is not supported by the installed toolchain. No PCIe compliance or universal SSD-support claim is made.

The Stage 2 test failures are not hidden as a green result. They reflect the deliberately curated public package boundary; the full private working directory remains the source of the excluded raw simulation and historical evidence files.
