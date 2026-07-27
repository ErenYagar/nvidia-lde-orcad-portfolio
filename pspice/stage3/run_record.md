# Stage 3 PSpice recovery-closure attempt

- Tool: OrCAD PSpice 25.1 S040, `psp_cmd.exe`
- Model: TI TPS543620 official SLUM787A transient macro-model
- Candidate: 132 uF effective COUT, 3 mOhm ESR, 8.2 pF feed-forward capacitor
- Requested stop time: 1.400 ms
- Reached simulation time before termination: approximately 0.255 ms
- Disposition: `Not_Concluded_Runtime_Limit`
- Pass/fail result: none

The process consumed about 1,449 CPU seconds and was stopped after the observed
runtime projected beyond one hour. The partial waveform is retained only as a
diagnostic artifact and must not be used to close recovery undershoot.

Hashes:

- Partial CSDF SHA-256:
  `EE2C9FC9680C009F1F090CFE0429994B4C2F251E8CFD46A702D7C3F5353F45E8`
- OUT SHA-256:
  `E45E48119EC8C30D093F56FDD382C4FA8477F16146699DE385C29B2107F5AE2B`

The previous completed official-model result remains the governing evidence:
88 uF effective COUT failed the 3.135 V recovery screen with a 3.109 V minimum.
