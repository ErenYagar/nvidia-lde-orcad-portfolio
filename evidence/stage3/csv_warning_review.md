# CSV validator warning review

`check_duplicate_pins.py` reports 31 warnings and 0 errors for `schematic/connection_matrix.csv`.

Review disposition：`Reviewed_Expected_Same_Net_Expansion`

Each warning is the same physical component pin appearing more than once on the **same net** because the connection matrix expands a multi-drop electrical net into reviewable endpoint rows. Examples include the five PCIe 12 V fingers on `P12V_SLOT`, multi-pin GND connectivity, I²C multi-drop endpoints, the shunt current path and repeated power/test-point endpoints.

The validator independently checks the failure condition—one physical pin assigned to different net names—and reports zero such errors. Therefore these warnings are not waived shorts, duplicate pads or Allegro DRCs; they are source-data normalization warnings retained for reviewer visibility.

Native board evidence remains independently closed at DRC 0, unconnected 0 and active rats 0.
