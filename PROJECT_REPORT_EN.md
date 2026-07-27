# PCIe Gen3 x4 → M.2 NVMe Adapter — Technical Case Study (English)

繁體中文版：[`PROJECT_REPORT_ZH.md`](PROJECT_REPORT_ZH.md)｜Current master report with evidence links: [`PROJECT_REPORT.md`](PROJECT_REPORT.md)

**Status: `Interview_Digital_Complete_Not_For_Fabrication`**

## 1. Executive summary

This project is a low-profile, half-length, six-layer PCIe Gen3 x4 add-in card that physically connects a host PCIe edge connector to an M.2 M-Key 2280 NVMe SSD. It is a passive physical interposer, not a protocol converter: the host Root Complex and the NVMe controller remain the protocol endpoints.

The public package connects Capture interface data, native Allegro placement and constraints, 3DX/STEP handoff, PSpice profiles, CAM outputs, BOM/P&P and Python validators. It does not claim PCIe compliance, universal SSD support, chassis compatibility, bench qualification or fabrication readiness.

## 2. Actual function and boundary

- **Signal:** J1 PCIe edge → four lanes of TX/RX, REFCLK and sidebands → J2 M.2 M-Key 2280.
- **Power:** `P12V_SLOT` → TPS25947 family eFuse → TPS543620 6 A buck → 5 mΩ Kelvin shunt → `P3V3_NVME`.
- **Telemetry:** INA238 current monitor, TMP1075 temperature sensor and target-only I²C header.
- **Excluded:** PCIe switch, retimer, bridge, firmware, packet conversion and host enumeration logic.

Source documents: [`docs/interface_definition.md`](docs/interface_definition.md) and [`docs/system_block_diagram.md`](docs/system_block_diagram.md).

## 3. Requirements and verification contract

| Requirement | Design response | Current status |
|---|---|---|
| PCIe Gen3 x4 physical path | Eight data pairs, REFCLK and sidebands | Logical intent present; physical pin freeze blocked |
| M.2 M-Key 2280 | J2 placement, SSD envelope and retention baseline | Preliminary |
| Six layers / 1.6 mm nominal | L1/L6 signal, L2/L5 GND, L3 control, L4 power | Native baseline present; fabricator geometry pending |
| 3.3 V / 5 A normal target | eFuse, 6 A buck and Kelvin shunt | Engineering target; not bench-qualified |
| 7 A / 100 µs pulse study | Official buck-model transient profile | Simulation-limited |
| Reviewable release package | Reports, hashes, 3DX, STEP, CAM and validators | Digital package complete |

## 4. Architecture and design decisions

I compared slot 3.3 V distribution with slot 12 V plus local conversion. Architecture B was selected because it exposes protection, conversion, current sensing, hot-loop placement and PSpice reasoning in one interview project; it is not presented as universally superior.

| Decision | Selection | Reason and remaining risk |
|---|---|---|
| Input power | 12 V + eFuse + buck | Reviewable protection/conversion; slot budget and inrush are not closed by a controlled source |
| Regulator | TPS543620, 6 A class | 5 A normal and short pulse study; recovery still fails |
| Current sense | 5 mΩ four-terminal Kelvin shunt + INA238 | Low drop and observable rail; calibration/bench data open |
| High-speed conditioning | No added AC caps, termination, CMC or ESD | Waits for transmitter ownership and CEM/M.2 source confirmation |
| Layer strategy | L1/L6 referenced to L2/L5, L4 power | Width/gap/via depend on JLCPCB stack-up |
| Manufacturing exchange | Gerber + NC Drill + IPC-2581-C | ODB++ unsupported; empty IPC-356 excluded |

## 5. Capture and electrical interface

`schematic/connection_matrix.csv` is the logical source; `symbol_pinmap.csv`, `footprint_assignment.csv` and the native ERC report provide pin-to-footprint traceability. Because the controlled PCIe CEM/M.2 documents are not included in the public package, J1/J2 critical physical pins remain `Pending_Human_Verification`. The B12/CLKREQ# and M.2 pin-32 revision conflict is recorded instead of guessed.

## 6. Power and PSpice

The power estimate uses `P = V × I`, a 5 mΩ shunt, effective capacitance and explicit efficiency assumptions.

| Profile | Observation | Disposition |
|---|---|---|
| Solver smoke | Command-line solver concluded | Simulated |
| 5 A steady | 3.149 V minimum in the recorded window | Passes that model window only |
| 7 A / 100 µs | 3.204 V minimum in the recorded window | Passes that model window only |
| Recovery | 3.109 V, below the 3.135 V screen | **Simulated failure** |
| eFuse isolated run | No valid output startup reached | Functional validation failed |
| COUT/ESR/CFF sweep | 27 cases stopped by runtime limit | Not concluded |

The 132 µF candidate is not a released BOM value. No supported-SSD claim is inferred from the partial or failed runs.

## 7. PCB and high-speed intent

The RevK native board contains placement, power shapes, return-path intent and nine differential-pair objects (eight data plus REFCLK). The current gate report records DRC 0, unconnected 0, active rats 0 and zero shape islands.

This is digital PCB closure, not SI/PI sign-off. Pair width, gap, via, anti-pad, reference layer, skew and back-drill must wait for the JLCPCB stack-up and governing specification.

## 8. Mechanical review, 3DX and STEP

Native 3DX screenshots, portfolio views and AP242/mm STEP re-import are bound to the current RevK board hash. SSD, J2, standoff, bracket and host-chassis inputs are not all exact controlled models. Collision cases therefore remain `Preliminary_Clear` or `Blocked_Missing_Exact_Model`; a polished image cannot upgrade a missing model to Pass.

## 9. Manufacturing outputs

Gerber, NC Drill, IPC-2581-C, BOM, preliminary P&P, assembly-drawing evidence and STEP are exported. IPC-356 was empty and excluded; ODB++ is unsupported by the installed tool. This is an engineering-review package, not a direct fabrication release.

## 10. Automation and negative tests

The Python layer uses `csv`, `argparse`, `pathlib` and `unittest` to check CSV schemas, BOM fields, duplicate pins, net naming and Stage 2/3 evidence contracts. Negative fixtures cover missing columns/MPN, duplicate pins, invalid nets, pad mismatch, unplaced components, stale hashes, missing evidence and false routing claims. Python does not parse proprietary `.brd`/`.dsn` files and does not replace native Cadence review.

## 11. Results and limitations

| Area | Result |
|---|---|
| System architecture | Reviewable design intent closed |
| Native PCB digital closure | RevK DRC/connectivity/shape counters closed |
| Power topology | Preliminary baseline |
| PSpice | 5 A/7 A windows recorded; recovery failure |
| Constraint Manager | Pair objects present; impedance geometry not frozen |
| 3DX/STEP | Handoff loop verified; exact fit preliminary |
| Manufacturing | Digital outputs generated; not fab-ready |
| Hardware | No physical measurement claimed |

## 12. Rev L plan

Obtain controlled CEM/M.2 specifications, freeze J1/J2 physical pins, import the current JLCPCB stack-up, close recovery and eFuse behavior, replace exact mechanical models, then perform DFM, fabrication, safe power-up, enumeration, Gen3 x4 link, NVMe identify, stress and thermal testing.

## 13. Demonstrated skills

Requirements decomposition, architecture trade-offs, Capture/Allegro traceability, buck/shunt/power reasoning, differential-pair constraints, 3DX/STEP handoff, CAM automation, negative testing, failure disclosure and release-gate communication.

## 14. Interview walkthrough

- **30 seconds:** “I designed a passive PCIe Gen3 x4 to M.2 2280 physical adapter and built the Capture, power, Allegro, 3DX/STEP, CAM and validation workflow.”
- **2 minutes:** Explain Architecture B, DRC/connectivity, 3DX/STEP and the power chain.
- **5 minutes:** Show the 3.109 V recovery failure, nine pair objects, the pin-source gate and fabrication blockers.
- **10 minutes:** Use the [bilingual interview guide](docs/INTERVIEW_GUIDE.md) and [claim matrix](docs/CLAIM_EVIDENCE_MATRIX.md) for an evidence-based design review.
