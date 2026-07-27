# Documentation Audit (English)

繁體中文版：[`DOCUMENTATION_AUDIT_ZH.md`](DOCUMENTATION_AUDIT_ZH.md)｜Current master audit: [`DOCUMENTATION_AUDIT.md`](DOCUMENTATION_AUDIT.md)

Scope: public repository `ErenYagar/nvidia-lde-orcad-portfolio`. Method: file inventory, path checks, evidence/status review, claim scan and Python validators.

## 1. Repository position

This is an interview-oriented PCB system-design case study for a six-layer PCIe Gen3 x4 add-in card to M.2 M-Key 2280 NVMe physical interposer. It does not implement PCIe protocol conversion, a retimer, a switch or firmware. The engineering story connects system intent, pin/net interfaces, power assumptions, 3DX/STEP, CAM and automated checks.

The public baseline is Rev K / RevK evidence with status `Interview_Digital_Complete_Not_For_Fabrication`.

## 2. Strong evidence already present

| Area | Evidence | Audit conclusion |
|---|---|---|
| System intent | [`docs/interface_definition.md`](interface_definition.md), [`docs/system_block_diagram.md`](system_block_diagram.md) | Host, edge, M.2, SSD, power and telemetry boundaries are explicit |
| Architecture | [`docs/architecture_tradeoff.md`](architecture_tradeoff.md) | Options, selection rationale and exit conditions are recorded |
| Capture | [`schematic/connection_matrix.csv`](../schematic/connection_matrix.csv), ERC report | Machine-readable source and native reports are retained |
| PSpice | [`pspice/stage2/profile_results.csv`](../pspice/stage2/profile_results.csv) | The 3.109 V recovery failure is visible |
| PCB | [`evidence/stage3/stage3_delivery_gate.md`](../evidence/stage3/stage3_delivery_gate.md) | Native DRC/connectivity/shape closure and nine pair objects are evidenced |
| 3D/MCAD | [`evidence/stage3/3d_status.md`](../evidence/stage3/3d_status.md) | Native 3DX and AP242/mm STEP round-trip are hash-bound |
| Manufacturing | [`manufacturing/stage3_final_revk/README.md`](../manufacturing/stage3_final_revk/README.md) | Gerber, NC Drill, IPC-2581, BOM/P&P exist but are not a fab release |
| Automation | [`scripts/`](../scripts/) | Schema, negative fixtures and command-line checks are repeatable |

## 3. Genuine open engineering evidence

1. Controlled PCIe CEM/M.2 specifications are not included; J1/J2 physical pins remain `Pending_Human_Verification`.
2. The current JLCPCB stack-up and impedance width/gap/via geometry are not frozen.
3. Exact host chassis, bracket, standoff, cable, J2 and SSD models are incomplete; collisions remain preliminary or blocked.
4. The official buck model reaches 3.109 V in recovery against a 3.135 V screen; the 27-case sweep is runtime-limited.
5. The TPS25947x isolated run did not reach valid output startup.
6. No physical board, oscilloscope, Bode/impedance, thermal-camera, NVMe-enumeration or Gen3 x4 bench results are included.
7. IPC-356 was empty and ODB++ is limited by the installed tool; IPC-2581-C is the available intelligent exchange.

## 4. Deliberately absent design elements

- Lane AC capacitors, termination, CMC and ESD were not added before transmitter ownership is confirmed by controlled sources.
- No protocol converter, retimer, switch or firmware is present because this is a passive adapter.
- No universal-SSD, chassis-compatibility or bench-qualification claim is made.
- A 3DX render is handoff/placement evidence, not proof of exact fit or physical test.

## 5. Overclaim risks

`PCIe compliance`, `fabrication-ready`, `universal SSD`, `chassis compatibility`, `bench qualification`, `exact fit`, `SI sign-off` and `thermal validation` must always be qualified as unclaimed or incomplete. The claim matrix links each boundary to evidence.

## 6. Documentation acceptance standard

- A reader can find what the board does, does not do and where the evidence lives within two clicks.
- Every quantitative claim has a status or evidence path.
- Failures, runtime limits, missing models and fabrication blockers remain visible.
- Original Cadence binaries, PCB, PSpice, CAM and images are not rewritten.
