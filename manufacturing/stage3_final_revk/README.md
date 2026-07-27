# RevK final interview digital package

Status：`Interview_Digital_Complete_Not_For_Fabrication`

Source board：

`pcb/allegro/stage3/pcie_gen3_x4_nvme_adapter_reva_stage3_route_revk_interview_digital_complete.brd`

SHA-256：`C772E9C3CD7A04A2CE3FBD1F5AE659E0935B786B235B17354DB83371BB4FF3EA`

Included：14 Gerber review files、2 NC Drill files、IPC-2581-C、BOM、preliminary P&P、native placement、CAM previews與mm/AP242 assembly STEP。

Known limitations：

- `Fabrication_Ready=false`；JLCPCB stack-up與impedance geometry未凍結。
- IPC-356輸出仍為空，已移到`diagnostics/ipc356_failed/`並排除。
- ODB++為`Not_Supported_By_Installed_Tool`。
- Gerber 0-width outline/text warnings保留於`photoplot.log`與`artwork_console.log`。
- STEP中的部分mechanical models仍為preliminary envelopes；不能作final collision Pass。
- 不得直接將此目錄上傳板廠下單。
