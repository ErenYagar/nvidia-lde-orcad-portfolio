# PW-01 official TPS543620 combined profile

- Tool: OrCAD PSpice 25.1 S040, `psp_cmd.exe`
- Model: TI TPS543620 transient macro-model SLUM787A
- Input: `pspice/stage2/pw01_buck_combined_1400us.cir`
- Stop time: 1.400 ms
- Solver result: `JOB CONCLUDED`
- Result: `Fail_Recovery_Undershoot_5pct`

## Evidence hashes

- OUT: `C0D6C76949B74518E8609B9E15B75F3BCA8EE3F8B211522E75085B260FCF2FE6`
- CSDF: `DD1F99E1487013285DC6D71F0F4B169B3DB1F7852E26799F85DD2C6F9E55141E`
- Overall metrics: `E160E8F06CC91D181BDCAB732A297C9D54AA96D0CDEF92522DBB88B1B8AFDB9D`
- Window metrics: `9DDA88AD5C82C945AA0F89F5C4309618D33D4F4DE6927CB079F4C6EA43DFB6C9`

## Window disposition

| Window | V(P3V3_NVME) minimum | 3.135 V screen | Key observation |
|---|---:|---|---|
| STARTUP_0P5A | 3.247 V | Pass | 0.5 A post-soft-start window |
| STEADY_5A | 3.149 V | Pass | 14 mV margin to the 5% lower bound |
| PEAK_7A | 3.204 V | Pass | 7 A for 100 µs; shunt drop is 35 mV |
| RECOVERY_5A | 3.109 V | Fail | minimum occurs in the 1330–1340 µs diagnostic window |
| RELEASE_0P5A | 3.306 V | Pass | final load release window |

PGOOD remains high throughout the recovery diagnostic windows. Peak simulated
inductor current is 8.656 A. The official macro-model result therefore supports
neither the broad 5 A/7 A power-envelope claim nor a supported-SSD claim.
Power-stage tuning and a complete rerun are required; layout parasitics,
capacitor variation and thermal correlation remain Stage 3 work.
