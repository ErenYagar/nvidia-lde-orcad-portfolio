; Rev K closes the three verified L4 shape islands without modifying Rev J.
; Via geometry remains preliminary until the fabricator stack-up is frozen.

setq(stage3RevKBoard
  "C:/project/orcad_project/nvidia-lde-orcad-portfolio/pcb/allegro/stage3/pcie_gen3_x4_nvme_adapter_reva_stage3_route_revk_interview_digital_complete.brd")
setq(stage3RevKReport
  "C:/project/orcad_project/nvidia-lde-orcad-portfolio/pcb/allegro/stage3/stage3_revk_shape_island_closure_report.txt")

procedure(stage3FindNetByName(netName)
  let((found net)
    found = nil
    foreach(net axlDBGetDesign()->nets
      when(net->name == netName found = net)
    )
    found
  )
)

procedure(stage3CreatePowerTieVia(netName xy)
  let((result)
    result = axlDBCreateVia("S3_VIA_D0P20_P0P45" xy netName nil 0.0 nil)
    unless(result
      error(sprintf(nil "STAGE3_REVK_VIA_CREATE_FAILED|%s|%L" netName xy))
    )
    car(result)
  )
)

procedure(stage3CloseShapeIslandsRevK()
  let((design nvme pre nvmeA nvmeB preTie port saved)
    design = axlDBGetDesign()
    nvme = stage3FindNetByName("P3V3_NVME")
    pre = stage3FindNetByName("P3V3_PRE_SENSE")
    unless(nvme && pre error("STAGE3_REVK_POWER_NETS_MISSING"))
    unless(nvme->nBranches == 3 && pre->nBranches == 2
      error(sprintf(nil "STAGE3_REVK_UNEXPECTED_BRANCH_BASELINE|NVME=%d|PRE=%d"
        nvme->nBranches pre->nBranches))
    )

    ; Exact tie points are on existing Top-layer routed centerlines and inside
    ; the corresponding L4/Pwr boundaries.  They are connectivity closure
    ; points, not a final current-density via array.
    nvmeA = stage3CreatePowerTieVia("P3V3_NVME" 31.4278:42.7)
    nvmeB = stage3CreatePowerTieVia("P3V3_NVME" 99.0:61.0)
    preTie = stage3CreatePowerTieVia("P3V3_PRE_SENSE" 83.7:49.55)

    axlShell("shape update all")
    axlShell("drc update")
    design = axlDBGetDesign()
    nvme = stage3FindNetByName("P3V3_NVME")
    pre = stage3FindNetByName("P3V3_PRE_SENSE")

    port = outfile(stage3RevKReport "w")
    fprintf(port "AUDIT|STAGE3_REVK_SHAPE_ISLAND_CLOSURE|25.1_S040\n")
    fprintf(port "SOURCE_REVJ_POWER_PLANES_SHA256|8B6D0C33D19083539C2BB4A085946B1B7E497F232747259FB62230CDA859069F\n")
    fprintf(port "VIA_PADSTACK|S3_VIA_D0P20_P0P45|DRILL_MM|0.20|PAD_MM|0.45\n")
    fprintf(port "VIA|P3V3_NVME|(31.4278 42.7)|(ETCH/TOP ETCH/BOTTOM)\n")
    fprintf(port "VIA|P3V3_NVME|(99.0 61.0)|(ETCH/TOP ETCH/BOTTOM)\n")
    fprintf(port "VIA|P3V3_PRE_SENSE|(83.7 49.55)|(ETCH/TOP ETCH/BOTTOM)\n")
    fprintf(port "P3V3_NVME_N_BRANCHES|%d\n" nvme->nBranches)
    fprintf(port "P3V3_PRE_SENSE_N_BRANCHES|%d\n" pre->nBranches)
    fprintf(port "P3V3_NVME_UNCONNECTED|%d\n" nvme->unconnected)
    fprintf(port "P3V3_PRE_SENSE_UNCONNECTED|%d\n" pre->unconnected)
    fprintf(port "DRC_STATE|%L\n" design->drcState)
    fprintf(port "DRC_COUNT|%d\n" length(design->drcs))
    foreach(drc design->drcs
      fprintf(port "DRC|%L|TYPE|%L|SOURCE|%L|XY|%L|ACTUAL|%L|EXPECTED|%L\n"
        drc->name drc->type drc->source drc->xy drc->actual drc->expected)
    )
    fprintf(port "FINAL_VIA_GEOMETRY|Pending_Fabricator_Confirmation\n")
    fprintf(port "FAB_READY_CLAIM|PROHIBITED\n")
    close(port)

    unless(nvme->nBranches == 1 && pre->nBranches == 1
      error(sprintf(nil "STAGE3_REVK_ISLAND_CLOSURE_FAILED|NVME=%d|PRE=%d"
        nvme->nBranches pre->nBranches))
    )
    unless(length(design->drcs) == 0
      error(sprintf(nil "STAGE3_REVK_DRC_FAILED|COUNT=%d" length(design->drcs)))
    )

    saved = axlSaveDesign(?design stage3RevKBoard ?noMru t ?noConfirm t)
    unless(saved error("STAGE3_REVK_SAVE_FAILED"))
    axlMsgPut("STAGE3_REVK_ZERO_SHAPE_ISLANDS_SAVED")
    t
  )
)

stage3CloseShapeIslandsRevK()
