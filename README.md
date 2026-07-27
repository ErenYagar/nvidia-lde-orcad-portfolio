# PCIe Gen3 x4 → M.2 NVMe adapter

**An interview-ready OrCAD X / Allegro PCB system-design case study.**<br>
This repository documents a six-layer, low-profile PCIe add-in card that physically connects a host PCIe slot to an M.2 M-Key 2280 NVMe SSD. It is a **passive interposer, not a protocol converter**.

**Current status:** `Interview_Digital_Complete_Not_For_Fabrication`<br>
**Not claimed:** PCIe compliance, universal SSD support, chassis compatibility, bench qualification, SI/PI sign-off, thermal validation or fabrication-ready release.

## Start here

1. [Open the bilingual visual portfolio](portfolio/index.html)
2. [Read the technical case study](PROJECT_REPORT.md)
3. [Use the interview walkthrough](docs/INTERVIEW_GUIDE.md)
4. [Trace every claim to evidence](docs/CLAIM_EVIDENCE_MATRIX.md)
5. [Read the documentation audit and open gaps](docs/DOCUMENTATION_AUDIT.md)

## What the board actually does

| Boundary | Implementation |
|---|---|
| Host/SSD data | J1 PCIe edge → eight data pairs + REFCLK/sideband → J2 M.2 M-Key 2280 |
| Power | PCIe slot 12 V → TPS25947-family eFuse → TPS543620 6 A buck → 5 mΩ Kelvin shunt → 3.3 V SSD |
| Telemetry | INA238 current monitor + TMP1075 temperature sensor + target-only I²C header |
| PCB baseline | Six layers, 120 × 64 mm preliminary envelope, 1.6 mm nominal |

The system interface and layer intent are defined in [`docs/interface_definition.md`](docs/interface_definition.md) and [`docs/system_block_diagram.md`](docs/system_block_diagram.md).

## Five design decisions

| Decision | Why it is in the case study | Current boundary |
|---|---|---|
| 12 V + eFuse + buck | Makes protection, conversion and hot-loop reviewable | Slot budget/eFuse behavior still open |
| 5 mΩ Kelvin shunt | Enables low-loss current telemetry | Calibration/bench correlation open |
| No added lane conditioning | Preserves transmitter ownership until specs are confirmed | CEM/M.2 controlled pin source blocked |
| L1/L6 referenced to L2/L5 | Makes return-path intent explicit | Width/gap/via geometry pending fabricator |
| Gerber + IPC-2581-C | Provides available manufacturing exchange | ODB++ unsupported; not fab-ready |

Full options and exit conditions: [`docs/architecture_tradeoff.md`](docs/architecture_tradeoff.md).

## Verification snapshot

| Item | Result |
|---|---|
| Native RevK DRC / unconnected / active rats / shape islands | 0 / 0 / 0 / 0 in current gate report |
| Differential-pair objects | 9 native pairs (8 data + REFCLK) |
| PSpice 5 A / 7 A window | Recorded model windows pass the 3.135 V screen; recovery reaches 3.109 V and fails |
| PSpice sweep | 27 cases retained, runtime-limited; no pass inferred |
| 3DX / STEP | Current-board native views and AP242/mm isolated re-import recorded |
| Manufacturing | Gerber, NC Drill, IPC-2581-C, BOM/P&P generated for engineering review |
| Hardware | No board measurement, enumeration, SI/PI or thermal result claimed |

Evidence sources: [`evidence/stage3/stage3_delivery_gate.md`](evidence/stage3/stage3_delivery_gate.md), [`pspice/stage2/profile_results.csv`](pspice/stage2/profile_results.csv), [`evidence/stage3/3d_status.md`](evidence/stage3/3d_status.md), [`manufacturing/stage3_final_revk/README.md`](manufacturing/stage3_final_revk/README.md).

## Repository map

- `schematic/` — connection matrix, symbol pins, footprint assignments and native Capture reports.
- `pcb/` — constraints, differential pairs, 3D model mapping and the native RevK board.
- `pspice/` — command-line profiles, recovery sweep records and model limits.
- `evidence/` — hash-bound gates, native 3DX screens, portfolio views and collision status.
- `manufacturing/` — Gerber, NC Drill, IPC-2581-C, BOM/P&P, STEP and export manifest.
- `scripts/` — standard-library validators and negative fixtures.

## Reproduce the data checks

```powershell
python scripts/validate_csv.py --root .
python scripts/check_bom_fields.py manufacturing/bom.csv
python scripts/check_duplicate_pins.py schematic/connection_matrix.csv schematic/symbol_pinmap.csv
python scripts/check_net_names.py schematic/connection_matrix.csv
python scripts/check_documentation_links.py --root .
python scripts/check_portfolio_i18n.py
python -m unittest discover -s scripts -p "test_*.py" -v
```

Expected interpretation is documented in [`VALIDATION_STATUS.md`](VALIDATION_STATUS.md); repo-specific public-package gaps are reported rather than suppressed.

## Next revision

Rev L must obtain controlled PCIe/M.2 pin sources and the current JLCPCB stack-up, close the PSpice recovery/eFuse gates, replace preliminary mechanical models, then perform DFM, fabrication and bench bring-up. Until then, this is an honest digital interview package—not a board-order instruction.
