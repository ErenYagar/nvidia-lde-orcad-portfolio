# NVIDIA LDE OrCAD RevK interview package

Status：`Interview_Digital_Complete`

Fabrication_Ready：`false`

This archive is the curated interview handoff for the RevK native Allegro board. It includes the current board database, reusable SKILL sources, package/STEP mapping library, Capture reports, PSpice raw recovery evidence, current-board 3DX captures, portfolio views and engineering manufacturing exports.

Primary board SHA-256：

`C772E9C3CD7A04A2CE3FBD1F5AE659E0935B786B235B17354DB83371BB4FF3EA`

Important limitations：

- Do not upload this archive to a PCB fabricator.
- Differential-pair impedance geometry is still `Pending_Fabricator_Confirmation`.
- PCIe CEM／M.2 controlled-spec sign-off is incomplete.
- PSpice governing recovery is a disclosed 3.109 V failure; the 27 candidate cases were runtime-limited.
- Exact mechanical context and physical bring-up are not complete.
- IPC-356 zero-byte output is excluded; its console log is retained under diagnostics.
- ODB++ is `Not_Supported_By_Installed_Tool`; IPC-2581-C is included.

Start with the root `README.md`, then review:

1. `evidence/stage3/stage3_delivery_gate.md`
2. `evidence/stage3/constraint_manager_status.md`
3. `manufacturing/stage3_final_revk/README.md`
4. `manufacturing/stage3_final_revk/artifact_manifest.csv`
5. `validation/stage3_fabrication_and_bringup_gate.md`
