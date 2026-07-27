; OrCAD X PCB Professional Plus 25.1
; Isolated re-import of the RevK interview-digital-complete assembly STEP.
; Creates a new mechanical-symbol drawing and does not modify the routed board.

setq(revkRoundtripStep
  "C:/project/orcad_project/nvidia-lde-orcad-portfolio/manufacturing/stage3_final_revk/pcie_gen3_x4_nvme_adapter_reva_revk_final_preliminary.step")
setq(revkRoundtripDra
  "C:/project/orcad_project/nvidia-lde-orcad-portfolio/evidence/stage3/3d/roundtrip_revk/pcie_gen3_x4_nvme_adapter_reva_revk_final_step_reimport.dra")
setq(revkRoundtripLog
  "C:/project/orcad_project/nvidia-lde-orcad-portfolio/evidence/stage3/3d/roundtrip_revk/stage3_final_step_reimport_native_log.txt")

procedure(revkRunStepRoundtrip()
  let((assigned mapping placeBound saved logPort)
    axlDBChangeDesignUnits("millimeters" 4)
    unless(
      axlDBChangeDesignExtents(
        list(list(-10.0 -10.0) list(130.0 75.0))
      )
      error("REVK_STEP_REIMPORT_EXTENTS_FAILED")
    )

    placeBound = axlDBCreateRectangle(
      list(list(0.0 0.0) list(120.0 64.0))
      t
      "PACKAGE GEOMETRY/PLACE_BOUND_TOP"
    )
    unless(placeBound
      error("REVK_STEP_REIMPORT_PLACE_BOUND_FAILED")
    )

    assigned = axlStepSet('primary nil revkRoundtripStep nil)
    unless(assigned
      error("REVK_STEP_REIMPORT_ASSIGN_FAILED")
    )

    mapping = axlStepGet(nil 'primary nil)
    unless(mapping
      error("REVK_STEP_REIMPORT_READBACK_FAILED")
    )

    saved = axlSaveDesign(
      ?design revkRoundtripDra
      ?noMru t
      ?noConfirm t
    )
    unless(saved
      error("REVK_STEP_REIMPORT_DRA_SAVE_FAILED")
    )

    logPort = outfile(revkRoundtripLog)
    fprintf(logPort "REVK INTERVIEW DIGITAL COMPLETE\n")
    fprintf(logPort "PRELIMINARY MECHANICAL PLACEMENT - NOT FAB READY\n")
    fprintf(logPort "Result: NATIVE_DRA_STEP_ASSIGNMENT_OK\n")
    fprintf(logPort "Source_STEP: %s\n" revkRoundtripStep)
    fprintf(logPort "Output_DRA: %s\n" saved)
    fprintf(logPort "Wrapper_Units: millimeters\n")
    fprintf(logPort "Wrapper_Place_Bound_mm: 120.000 x 64.000\n")
    fprintf(logPort "Mapping_Readback: %L\n" mapping)
    close(logPort)

    axlMsgPut(sprintf(nil "REVK_STEP_REIMPORT_OK %s" saved))
    t
  )
)

axlCmdRegister("revk_step_roundtrip" 'revkRunStepRoundtrip)
