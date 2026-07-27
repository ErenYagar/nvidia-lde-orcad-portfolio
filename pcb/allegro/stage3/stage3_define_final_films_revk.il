; Manufacturing-review film definitions for the Rev K interview closure.

setq(stage3RevKFinalBoard
  "C:/project/orcad_project/nvidia-lde-orcad-portfolio/pcb/allegro/stage3/pcie_gen3_x4_nvme_adapter_reva_stage3_route_revk_interview_digital_complete.brd")

procedure(stage3DefineFinalFilmsRevK()
  let((design saved)
    axlFilmCreate("L1_TOP" ?layers list("ETCH/TOP" "BOARD GEOMETRY/DESIGN_OUTLINE"))
    axlFilmCreate("L2_GND1" ?layers list("ETCH/GND1" "BOARD GEOMETRY/DESIGN_OUTLINE"))
    axlFilmCreate("L3_SIG1" ?layers list("ETCH/SIG1" "BOARD GEOMETRY/DESIGN_OUTLINE"))
    axlFilmCreate("L4_PWR" ?layers list("ETCH/PWR" "BOARD GEOMETRY/DESIGN_OUTLINE"))
    axlFilmCreate("L5_GND2" ?layers list("ETCH/GND2" "BOARD GEOMETRY/DESIGN_OUTLINE"))
    axlFilmCreate("L6_BOTTOM" ?layers list("ETCH/BOTTOM" "BOARD GEOMETRY/DESIGN_OUTLINE"))
    axlFilmCreate("SM_TOP" ?layers list(
      "BOARD GEOMETRY/SOLDERMASK_TOP" "PACKAGE GEOMETRY/SOLDERMASK_TOP"
      "PIN/SOLDERMASK_TOP" "VIA CLASS/SOLDERMASK_TOP"
      "BOARD GEOMETRY/DESIGN_OUTLINE"))
    axlFilmCreate("SM_BOTTOM" ?mirrored t ?layers list(
      "BOARD GEOMETRY/SOLDERMASK_BOTTOM" "PACKAGE GEOMETRY/SOLDERMASK_BOTTOM"
      "PIN/SOLDERMASK_BOTTOM" "VIA CLASS/SOLDERMASK_BOTTOM"
      "BOARD GEOMETRY/DESIGN_OUTLINE"))
    axlFilmCreate("SILK_TOP" ?layers list(
      "BOARD GEOMETRY/SILKSCREEN_TOP" "PACKAGE GEOMETRY/SILKSCREEN_TOP"
      "REF DES/SILKSCREEN_TOP" "BOARD GEOMETRY/DESIGN_OUTLINE"))
    axlFilmCreate("SILK_BOTTOM" ?mirrored t ?layers list(
      "BOARD GEOMETRY/SILKSCREEN_BOTTOM" "PACKAGE GEOMETRY/SILKSCREEN_BOTTOM"
      "REF DES/SILKSCREEN_BOTTOM" "BOARD GEOMETRY/DESIGN_OUTLINE"))
    axlFilmCreate("PASTE_TOP" ?layers list(
      "PACKAGE GEOMETRY/PASTEMASK_TOP" "PIN/PASTEMASK_TOP"
      "BOARD GEOMETRY/DESIGN_OUTLINE"))
    axlFilmCreate("PASTE_BOTTOM" ?mirrored t ?layers list(
      "PACKAGE GEOMETRY/PASTEMASK_BOTTOM" "PIN/PASTEMASK_BOTTOM"
      "BOARD GEOMETRY/DESIGN_OUTLINE"))
    axlFilmCreate("ASSEMBLY_TOP" ?layers list(
      "PACKAGE GEOMETRY/ASSEMBLY_TOP" "REF DES/ASSEMBLY_TOP"
      "BOARD GEOMETRY/DESIGN_OUTLINE"))
    axlFilmCreate("ASSEMBLY_BOTTOM" ?mirrored t ?layers list(
      "PACKAGE GEOMETRY/ASSEMBLY_BOTTOM" "REF DES/ASSEMBLY_BOTTOM"
      "BOARD GEOMETRY/DESIGN_OUTLINE"))
    design = axlDBGetDesign()
    saved = axlSaveDesign(?design stage3RevKFinalBoard ?noMru t ?noConfirm t)
    unless(saved error("STAGE3_REVK_FINAL_FILMS_SAVE_FAILED"))
    axlMsgPut("STAGE3_REVK_FINAL_FILMS_DEFINED_AND_SAVED")
    t
  )
)

stage3DefineFinalFilmsRevK()
