# Documentation audit — NVIDIA LDE OrCAD portfolio

語言 / Language：[`繁體中文版`](DOCUMENTATION_AUDIT_ZH.md)｜[`English full version`](DOCUMENTATION_AUDIT_EN.md)

Audit date: 2026-07-27  
Scope: public repository at `ErenYagar/nvidia-lde-orcad-portfolio`  
Method: repository file inventory, path checks, evidence/status review, claim scan, and validator execution.

## 1. What the repository is

This is a self-directed, interview-oriented PCB system-design case study for a six-layer PCIe Gen3 x4 add-in card that provides a physical PCIe-to-M.2 M-Key 2280 NVMe connection. The board does not translate PCIe protocol, enumerate a device by itself, or contain a PCIe switch/retimer. The host Root Complex and the NVMe controller remain the protocol endpoints; the board contributes connector pin mapping, power delivery, telemetry, placement, constraints, mechanical review, and release automation.

The current public baseline is Rev K / RevK evidence with status `Interview_Digital_Complete_Not_For_Fabrication`. The repository deliberately keeps native design artifacts and evidence close to the explanation, while excluding private credentials, personal contact data, and oversized/private simulation binaries.

## 2. Evidence that is already strong

| Area | Current evidence | Audit reading |
|---|---|---|
| System intent | [`docs/interface_definition.md`](interface_definition.md), [`docs/system_block_diagram.md`](system_block_diagram.md) | Clear host/edge/M.2/SSD/power/telemetry boundaries; passive interposer is explicit. |
| Architecture choice | [`docs/architecture_tradeoff.md`](architecture_tradeoff.md) | Options, weighted trade-off, selected 12 V + eFuse + buck chain, and exit conditions are recorded. |
| Component reasoning | [`docs/component_selection.md`](component_selection.md) | Official links, candidates, alternatives, and assumptions are separated. |
| Capture/electrical interface | [`schematic/connection_matrix.csv`](../schematic/connection_matrix.csv), [`schematic/symbol_pinmap.csv`](../schematic/symbol_pinmap.csv), [`schematic/orcad/stage2/reports/erc_report.txt`](../schematic/orcad/stage2/reports/erc_report.txt) | Reviewable machine-readable source tables and native-tool reports exist. |
| Power simulation | [`pspice/stage2/profile_results.csv`](../pspice/stage2/profile_results.csv), [`pspice/stage3/run_record.md`](../pspice/stage3/run_record.md) | Results are recorded with limitations; the 3.109 V recovery failure is not hidden. |
| PCB closure | [`evidence/stage3/stage3_delivery_gate.md`](../evidence/stage3/stage3_delivery_gate.md), [`evidence/stage3/constraint_manager_status.md`](../evidence/stage3/constraint_manager_status.md) | Current board has native DRC/connectivity/shape closure and nine differential pairs; impedance freeze is not claimed. |
| 3D/MCAD | [`evidence/stage3/3d_status.md`](../evidence/stage3/3d_status.md), [`evidence/stage3/3dx_native_revk/`](../evidence/stage3/3dx_native_revk/) | Native 3DX screens and AP242/mm STEP round-trip are hash-bound to RevK. |
| Manufacturing outputs | [`manufacturing/stage3_final_revk/README.md`](../manufacturing/stage3_final_revk/README.md), [`manufacturing/stage3_final_revk/export_status.csv`](../manufacturing/stage3_final_revk/export_status.csv) | Gerber, NC Drill, IPC-2581, BOM and preliminary P&P are present, but the package is explicitly not a fab release. |
| Automation | [`scripts/validate_csv.py`](../scripts/validate_csv.py), [`scripts/test_validators.py`](../scripts/test_validators.py) and the other `check_*.py` scripts | CSV schemas, negative fixtures, and repeatable command-line checks make the evidence auditable. |

## 3. Missing or weak evidence (result-only gaps)

These are not documentation failures; they are genuine engineering gates that the current result does not close.

1. The governing PCIe CEM/M.2 controlled specifications are not available in the public package, so critical J1/J2 physical pin numbers remain `Pending_Human_Verification`. The documented B12/CLKREQ# and M.2 pin-32 conflict is intentionally not guessed.
2. JLCPCB's current controlled-impedance six-layer stack-up and calculator output are not frozen. Pair width/gap, via geometry, anti-pad, reference-layer, skew and back-drill values therefore remain pending.
3. Exact mechanical context is incomplete: host chassis, bracket drawing, standoffs, cable and mating J2/SSD models are not all controlled exact models. Collision records are preliminary or blocked, not Pass.
4. The governing official-model PSpice sequence contains a 3.109 V recovery minimum against a 3.135 V lower screen. The 27-corner sweep and 132 uF candidate were runtime-limited; they are not a pass.
5. The isolated TPS25947x smoke run did not reach a valid output startup. Consequently there is no closed eFuse inrush/current-limit/latch-off claim.
6. No physical board, oscilloscope, Bode/impedance measurement, thermal camera, NVMe enumeration, or Gen3 x4 bench result is included. DRC and simulation are not substitutes for those measurements.
7. IPC-356 was empty and excluded; ODB++ is unavailable in the installed tool. IPC-2581-C is included as the intelligent manufacturing exchange instead.

## 4. Missing design reasons

Several items are intentionally absent rather than forgotten:

- No PCIe AC-coupling capacitors, termination, CMC, or ESD parts were added because transmitter ownership and the controlled pin specification were not closed.
- No protocol converter, retimer, switch, firmware, or host-side enumeration logic is in the architecture because the requested function is a passive physical adapter.
- No universal-SSD statement is made because the power, mechanical, firmware, and thermal envelope has not been qualified across devices.
- No fabricated-board result is represented by a 3DX render; portfolio images are presentation views backed by the native board and status reports.
- Raw/oversized private artifacts are not copied into the public repository; the manifest records the public evidence boundary.

## 5. Repetition and overclaim risks found before this audit

The earlier documents repeated the same status vocabulary and limitation paragraph in several places without a single claim-to-evidence index. That made it easy for a reader to see `DRC=0` or `STEP exported` without immediately seeing what those facts do not prove. The new report, matrix and interview guide use the same links and explicitly separate `VERIFIED`, `PRELIMINARY`, `SIMULATION-LIMITED`, `BLOCKED`, and `OPEN`.

The following phrases must always be qualified in portfolio copy: `PCIe compliance`, `fabrication-ready`, `universal SSD`, `chassis compatibility`, `bench qualification`, `exact fit`, `SI sign-off`, and `thermal validation`. In this repository they are used only to state that the claim is not made or is still open.

## 6. Evidence not previously surfaced enough

The repository contains useful evidence that was easy to miss from the old README: the native ERC report, the nine-pair constraint status, the power/shape audit, the AP242 re-import result, the 27-case recovery-sweep manifest, the eFuse failed-validation record, and the negative CSV fixtures. The revised entry points link these artifacts directly instead of listing directories without context.

## 7. Documentation acceptance criteria

- A reader can answer what the board does, what it deliberately does not do, and where each important claim is proven within two clicks.
- Every quantitative claim in the report has a source/status link or is labeled an engineering assumption.
- Simulation failures and runtime limits remain visible.
- Portfolio language is suitable for an interview but never implies PCIe compliance, fabrication release, universal SSD support, chassis fit, or bench qualification.
- Existing Cadence binaries, board files, simulation logs, CAM files and evidence images are preserved byte-for-byte.
