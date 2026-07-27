# Interview guide — PCIe Gen3 x4 to M.2 NVMe adapter

語言 / Language：[`繁體中文版`](INTERVIEW_GUIDE_ZH.md)｜English canonical version is this file

Use the short version first, then open the linked evidence only when the interviewer asks for depth. The safe framing is: **digital interview closure, not fabrication release or PCIe compliance**.

## Walkthrough scripts

### 30 seconds

> I designed a six-layer, low-profile PCIe Gen3 x4 add-in card that physically connects a host PCIe slot to an M.2 M-Key 2280 NVMe SSD. It is a passive interposer—not a protocol converter. My engineering focus was the complete traceable workflow: Capture interface definition, protected 12 V to 3.3 V power, PSpice boundary testing, Allegro placement/constraints, native 3DX/STEP, CAM outputs and Python negative tests. The current RevK result is `Interview_Digital_Complete_Not_For_Fabrication`; I can show exactly what is closed and what still needs a controlled spec or hardware measurement.

### 2 minutes

1. Show the [portfolio hero](../portfolio/index.html) and state the function boundary.
2. Show the [system block diagram](system_block_diagram.md) and explain J1 → J2 signal continuity plus the eFuse/buck/shunt power path.
3. Show the [stage3 gate](../evidence/stage3/stage3_delivery_gate.md): DRC/connectivity/shape closure is real, but impedance geometry and exact models are not frozen.
4. Show one [3DX view](../evidence/stage3/3dx_native_revk/revk_top_isometric_detailed_with_ui.png) and the [STEP status](../evidence/stage3/3d_status.md).

### 5 minutes

Add the Architecture B trade-off, Capture connection matrix, PSpice profile table, nine-pair constraint record, and manufacturing status. Explicitly mention the 3.109 V recovery failure and the eFuse validation gap.

### 10 minutes

Use the questions below as a guided design review. Finish with the [Rev L plan](../PROJECT_REPORT.md#12-rev-l--next-revision-plan), not with an unsupported “ready to ship” statement.

## Questions and concise answers

### 1. What problem does the board solve?

It provides a physical PCIe Gen3 x4 host-to-M.2 M-Key 2280 NVMe connection with local power protection/conversion and optional telemetry. It does not translate PCIe protocol. See [`docs/interface_definition.md`](interface_definition.md).

### 2. Why is there no PCIe switch or retimer?

The requested use case is a passive adapter. Adding a switch/retimer would change the architecture, power, firmware, SI and compliance scope. The current host and SSD remain the protocol endpoints.

### 3. Why did you choose 12 V input plus a buck instead of slot 3.3 V?

I compared both in [`docs/architecture_tradeoff.md`](architecture_tradeoff.md). Architecture B exposes protection, conversion, current sensing and layout decisions that are valuable in an LDE interview, while the worksheet also records its complexity and risks.

### 4. What is the normal load target?

3.3 V / 5 A is the engineering normal target. 7 A / 100 µs is a transient study pulse, not a blanket SSD power rating. The calculations are in [`docs/power_budget.md`](power_budget.md).

### 5. Why is a 6 A regulator used if the pulse is 7 A?

The 7 A event is time-limited and relies on output capacitance/control response; it is not a 7 A continuous claim. The model still reaches an 8.656 A peak inductor-current observation and recovery fails, so this is not closed. See [`pspice/stage2/profile_results.csv`](../pspice/stage2/profile_results.csv).

### 6. What failed in PSpice?

The completed official-model combined profile reached 3.109 V in recovery against a 3.135 V lower screen, while PGOOD stayed high. That result is retained as `Fail_Recovery_Undershoot_5pct`; it is not hidden or rewritten as pass.

### 7. Why did the capacitor sweep not close the issue?

The 27 COUT/ESR/CFF cases were terminated by runtime limits, and the 132 µF candidate only reached about 0.255 ms of a requested 1.4 ms run. The hashes and disposition remain in [`pspice/stage3/run_record.md`](../pspice/stage3/run_record.md).

### 8. What does the eFuse contribute?

It is intended to control current, soft-start and fault behavior between slot 12 V and the buck. The isolated encrypted-model run did not reach valid output startup, so inrush/current-limit/latch-off behavior is still a validation task, not a claim.

### 9. Why use a 5 mΩ Kelvin shunt?

It gives a low-loss differential sense element for INA238 while keeping force and sense paths separate. At 5 A the nominal drop is about 25 mV; exact loss, layout parasitics and calibration require bench correlation.

### 10. What is INA238/TMP1075 used for?

INA238 monitors the SSD branch current/voltage across the shunt; TMP1075 monitors local board temperature. J3 is a target-only I²C/debug header and must not back-feed the board. See the [interface definition](interface_definition.md).

### 11. How did you handle PCIe AC coupling and conditioning?

I did not add lane AC capacitors, termination, CMC or ESD before transmitter ownership and the governing CEM/M.2 pin specification were confirmed. This avoids silently changing a high-speed topology, but the final decision remains a controlled-source gate.

### 12. What does DRC=0 prove?

It proves the current native database passed the reported design-rule/connectivity checks. It does not prove SI/PI, impedance, thermal, mechanical fit, PCIe compliance or manufacturing yield. The counters are in [`evidence/stage3/stage3_delivery_gate.md`](../evidence/stage3/stage3_delivery_gate.md).

### 13. How many differential pairs are defined?

Nine native pair objects: eight PCIe data pairs (TX/RX for lanes 0–3) plus one REFCLK pair. Width/gap/via and skew are intentionally pending the fabricator stack-up. See [`pcb/differential_pairs.csv`](../pcb/differential_pairs.csv).

### 14. Why are physical J1/J2 pins still pending?

The controlled CEM/M.2 source documents were not available for legal verification. The repository records a B12/CLKREQ# and M.2 pin-32 conflict instead of guessing. See [`docs/pcie_m2_pin_mapping.md`](pcie_m2_pin_mapping.md).

### 15. Why is the stack-up not frozen?

Controlled impedance depends on the actual JLCPCB dielectric/copper stack-up and calculator output. Until that evidence is attached, a made-up line width/gap would be less credible than an explicit blocker. See [`evidence/stage3/constraint_manager_status.md`](../evidence/stage3/constraint_manager_status.md).

### 16. What did the 3DX/STEP work demonstrate?

It demonstrated a native-board-to-3DX-to-AP242/mm STEP handoff and isolated re-import with a hash-bound record. It did not demonstrate exact chassis fit because several mating models/transforms are preliminary or missing.

### 17. Why do some collision cases say blocked?

Collision Pass requires an exact model, confirmed transform and sourced clearance rule. A conservative envelope can support `Preliminary_Clear`, but a polished image cannot turn a missing controlled model into an engineering Pass. See [`evidence/stage3/3d_status.md`](../evidence/stage3/3d_status.md).

### 18. What manufacturing files are present?

Gerber artwork, NC Drill, IPC-2581-C, BOM, preliminary P&P, assembly drawing evidence and STEP are present. IPC-356 was empty and excluded; ODB++ is unsupported by the installed tool. The package is not direct-fab upload material. See [`manufacturing/stage3_final_revk/README.md`](../manufacturing/stage3_final_revk/README.md).

### 19. What did you automate?

I used standard-library Python to validate CSV schemas, BOM fields, duplicate pins, net naming and Stage 2/3 evidence contracts. Negative fixtures intentionally fail for missing columns/MPN, duplicate pins, invalid nets, stale hashes and false routing claims. See [`scripts/`](../scripts/) and [`PROJECT_REPORT.md`](../PROJECT_REPORT.md#10-automation-and-negative-tests--自動化).

### 20. How do you keep a failed result from being lost?

Every important run records input/output paths, status, limits and hashes. The PSpice recovery failure and runtime-limited sweep are linked from the report and claim matrix rather than overwritten by a later presentation image.

### 21. What would you do before ordering boards?

Freeze CEM/M.2 physical pins, import the current fabricator stack-up, close pair geometry and power recovery, validate eFuse behavior, replace preliminary mechanical models, then rerun DRC/CAM/DFM and review the board-house quote.

### 22. What would you do on the bench?

Use a current-limited supply and no SSD first; verify rails, inrush and PGOOD; then insert the reference SSD, check enumeration/link width/speed/NVMe identify, and finally perform short stress and thermal checks. None of those results are currently claimed.

### 23. Why is this an LDE-relevant project?

It shows the complete loop an LDE must manage: interface ownership, power trade-offs, library/footprint discipline, high-speed constraints, MCAD handoff, manufacturing outputs, automation, failure analysis and honest release gates—not only schematic capture.

### 24. What is the single biggest risk?

The highest-impact cluster is missing controlled source data: connector pin freeze and fabricator stack-up. Without them, a visually convincing board could still encode the wrong physical mapping or impedance geometry.

### 25. What is the next revision called and what changes?

Rev L is a controlled ECO: source-controlled pin freeze, stack-up-derived constraints, power recovery closure, eFuse validation, exact mechanical remapping, then CAM/DFM and physical bring-up. It is not a cosmetic rerender of RevK.

## Evidence quick links

- [Project report](../PROJECT_REPORT.md)
- [Claim/evidence matrix](CLAIM_EVIDENCE_MATRIX.md)
- [Documentation audit](DOCUMENTATION_AUDIT.md)
- [Stage 3 gate](../evidence/stage3/stage3_delivery_gate.md)
- [Final release status](../evidence/stage3/final_release_status.md)
