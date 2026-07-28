# Source Register

## Register baseline

- Repository: `ErenYagar/nvidia-lde-orcad-portfolio`
- Branch: `main`
- Commit: `24d9f51a3bbe024b5cb5d757c8823362d4c2612a`
- Review date: `2026-07-28`
- Entries: **46**
- Full machine-readable register: `docs/SOURCE_REGISTER.csv`

本 Register 只登錄 audited commit 中實際存在的來源 metadata、local evidence，或明確標示為缺失／受控的 release-critical source。`VERIFIED` 只代表來源版本／檔案 provenance 可核對，不代表相關設計已通過。

CSV 的 `Review_Status` 遵循 repository 既有 canonical vocabulary；原始證據判定則保存在 `Notes` 的 `Evidence_Disposition=...`。兩者不可混用：前者供自動 validator，後者供工程審查與 release-gate 解讀。

受限制的 PCI-SIG、M.2、IPC 文件未加入輸出；只記錄 title、revision、section、access class 與 review status。第三方 pinout 不得取代 governing specification。

## Evidence disposition summary

| Evidence disposition | Count |
|---|---:|
| BLOCKED | 9 |
| OPEN | 7 |
| PRELIMINARY | 18 |
| VERIFIED | 12 |

## Canonical CSV review-status summary

| `Review_Status` | Count |
|---|---:|
| Confirmed_Official | 12 |
| Engineering_Assumption | 18 |
| Pending_Fabricator_Confirmation | 2 |
| Pending_Human_Verification | 14 |

## Category coverage

| Category | Entries |
|---|---:|
| Cadence OrCAD/Allegro/PSpice documentation | 4 |
| Capacitor/inductor/shunt datasheets | 7 |
| Connector drawings | 3 |
| INA238 datasheet | 2 |
| IPC standards | 3 |
| JLCPCB stack-up/calculator | 3 |
| M.2 specification | 1 |
| Mechanical models | 4 |
| NVMe-related public information | 4 |
| PCIe CEM | 2 |
| SI/PI/layout references | 3 |
| SSD reference devices | 2 |
| TMP1075 datasheet | 2 |
| TPS25947 datasheet/model | 3 |
| TPS543620 datasheet/model | 3 |

## Critical release interpretation

- `SR-001` PCIe CEM、`SR-003` M.2、`SR-033/034` fabricator stack-up、`SR-046` SI acceptance source 仍為 `BLOCKED`。
- Pin mapping、impedance、width/gap/skew、chassis collision 或 fabrication release 不得升級為 VERIFIED。
- `SR-010`、`SR-013` 的 vendor-model provenance 可驗證，但 project simulation disposition 仍包含 eFuse functional failure、3.109 V recovery failure 與 runtime-limited sweep。
- `SR-038/039` 是可驗證的 vendor mechanical files；`SR-040/041` 顯示其餘 model 多為工程包絡或缺失。

## Register

| ID | Category | Document / source | Revision | Supported claim | Access | Local path | Hash / provenance | Evidence disposition |
|---|---|---|---|---|---|---|---|---|
| SR-001 | PCIe CEM | PCI Express Card Electromechanical Specification | 3.0 | Governing J1 pin, slot-power, inrush and mechanical source | Controlled (public metadata only) | NOT_INCLUDED_IN_PUBLIC_PACKAGE | NOT_AVAILABLE | BLOCKED |
| SR-002 | PCIe CEM | PCI Express CEM specification overview | dynamic portal | Confirms CEM governance and official entry point only | Public | NOT_ARCHIVED | NOT_ARCHIVED | PRELIMINARY |
| SR-003 | M.2 specification | PCI Express M.2 Specification | 5.1 | Candidate governing J2 logical/physical definition | Controlled (public metadata only) | NOT_INCLUDED_IN_PUBLIC_PACKAGE | NOT_AVAILABLE | BLOCKED |
| SR-004 | NVMe-related public information | NVM Express Base Specification portal | ratified revision portal | NVMe protocol background and validation vocabulary | Public | NOT_ARCHIVED | NOT_ARCHIVED | PRELIMINARY |
| SR-005 | NVMe-related public information | NVMe Power Governance webinar | webinar deck | Background for 5 A normal and 7 A/100 us stimulus | Public | NOT_ARCHIVED | NOT_ARCHIVED | PRELIMINARY |
| SR-006 | NVMe-related public information | Jetson AGX Orin Developer Kit Carrier Board Specification | 1.2 | Second-source public cross-check for candidate mapping | Public | evidence/official_sources/NVIDIA_Jetson_AGX_Orin_Carrier_Board_Spec_SP-10900-001_v1.2.pdf | D817A69767B9E11EFAA9B54037B87039A16BFF3E5A7C41255CE3B75E47322CAC (recorded; file absent in public package) | PRELIMINARY |
| SR-007 | NVMe-related public information | The Linux PTP Hardware Clock Subsystem for 5G O-RAN White Box Hardware | 1.02 | Cross-check that B12 differs between CEM 3.0 and 4.0 | Public | evidence/official_sources/Renesas_R70WP0004EU0102_Rev1.02.pdf | 60C5879700910845A69823332FB1A8B2329458055B48C8D6274F0E51A1D69A99 (recorded; file absent in public package) | PRELIMINARY |
| SR-008 | TPS25947 datasheet/model | TPS25947 eFuse datasheet | Rev C | U1 pin map, active-current-limit behavior, SOA and setting equations | Public | NOT_ARCHIVED | NOT_ARCHIVED | VERIFIED |
| SR-009 | TPS25947 datasheet/model | TPS259472LRPWR orderable page | dynamic product record | Exact eFuse orderable identity and RPW package | Public | NOT_ARCHIVED | NOT_ARCHIVED | PRELIMINARY |
| SR-010 | TPS25947 datasheet/model | TPS25947x PSpice Transient Model | web Rev A; internal Final 1.00 | eFuse model provenance | Public download; vendor license applies | NOT_INCLUDED_IN_PUBLIC_PACKAGE | ZIP=9BFD3F61435AF48179C56BF8C4D9911471154511DB272241A9B4C2A9C9C28A2B; LIB=54586D04715478C3094DC1BE645A36D44F014A321B9E655A95034F34CE7C4D69 | VERIFIED |
| SR-011 | TPS543620 datasheet/model | TPS543620 6-A synchronous buck datasheet | Rev C | U2 pins, 6 A rating, L/C/feedback, limits and layout guidance | Public | NOT_ARCHIVED | NOT_ARCHIVED | VERIFIED |
| SR-012 | TPS543620 datasheet/model | TPS543620 product page | dynamic product record | Product lifecycle and model availability | Public | NOT_ARCHIVED | NOT_ARCHIVED | PRELIMINARY |
| SR-013 | TPS543620 datasheet/model | TPS543620 PSpice Transient Model | web Rev A; internal Final 1.1 | Buck transient model provenance | Public download; vendor license applies | NOT_INCLUDED_IN_PUBLIC_PACKAGE | ZIP=6D335BA1C367AEED5340D26EC9D954BE63B2A30960C966F0CA5B50B3E54F9C7D; LIB=EDA49ED925B97ABB34C956E87C5DF490AB0EFB605D2C0F7792D67E8CDEC2441F | VERIFIED |
| SR-014 | INA238 datasheet | INA238 digital power monitor datasheet | Rev B | U3 pin map, ADCRANGE=1 and shunt range | Public | NOT_ARCHIVED | NOT_ARCHIVED | VERIFIED |
| SR-015 | INA238 datasheet | INA238AIDGSR orderable page | dynamic product record | Exact MPN and DGS package | Public | NOT_ARCHIVED | NOT_ARCHIVED | PRELIMINARY |
| SR-016 | TMP1075 datasheet | TMP1075 temperature sensor datasheet | revision 未找到 | U4 pin map, address straps, accuracy and placement semantics | Public | NOT_ARCHIVED | NOT_ARCHIVED | OPEN |
| SR-017 | TMP1075 datasheet | TMP1075DR orderable page | dynamic product record | Exact MPN and SOIC-8 package | Public | NOT_ARCHIVED | NOT_ARCHIVED | PRELIMINARY |
| SR-018 | Capacitor/inductor/shunt datasheets | WSK2512 four-terminal resistor datasheet | revision 未找到 | 5 mOhm four-terminal identity, land pattern, power and TCR review | Public | NOT_ARCHIVED | NOT_ARCHIVED | OPEN |
| SR-019 | Capacitor/inductor/shunt datasheets | XGL5050-152 product data | revision 未找到 | 1.5 uH, DCR, Isat, Irms and package candidate | Public | NOT_ARCHIVED | NOT_ARCHIVED | OPEN |
| SR-020 | Capacitor/inductor/shunt datasheets | C3225X7R1E106K250AC product data | revision 未找到 | 10 uF/25 V input MLCC candidate | Public | NOT_ARCHIVED | NOT_ARCHIVED | OPEN |
| SR-021 | Capacitor/inductor/shunt datasheets | C3225X7R1C226M250AC product data | revision 未找到 | 22 uF/16 V output MLCC candidate | Public | NOT_ARCHIVED | NOT_ARCHIVED | OPEN |
| SR-022 | Capacitor/inductor/shunt datasheets | BLM21PG221SN1D product datasheet | product-search datasheet | Telemetry-rail ferrite candidate | Public | NOT_ARCHIVED | NOT_ARCHIVED | PRELIMINARY |
| SR-023 | Capacitor/inductor/shunt datasheets | ADP198 datasheet | Rev G | Reverse-current-blocking sense path and U5 pin map | Public | NOT_ARCHIVED | NOT_ARCHIVED | VERIFIED |
| SR-024 | Capacitor/inductor/shunt datasheets | 2N7002 datasheet | Rev 40-2 | Q1 G/S/D mapping and LED buffer limits | Public | NOT_ARCHIVED | NOT_ARCHIVED | VERIFIED |
| SR-025 | Cadence OrCAD/Allegro/PSpice documentation | PCB Design and Analysis product documentation portal | dynamic portal | Tool capability and native database boundary | Public | NOT_ARCHIVED | NOT_ARCHIVED | PRELIMINARY |
| SR-026 | Cadence OrCAD/Allegro/PSpice documentation | OrCAD X and PSpice FAQ | dynamic FAQ | License/model/database limitations | Public | NOT_ARCHIVED | NOT_ARCHIVED | PRELIMINARY |
| SR-027 | Cadence OrCAD/Allegro/PSpice documentation | Integrating a 3D CAD Model Library and OrCAD X / OrCAD X 3D FAQ | 2025 article + dynamic FAQ | 3DX/STEP workflow and mapping review method | Public | NOT_ARCHIVED | NOT_ARCHIVED | PRELIMINARY |
| SR-028 | Cadence OrCAD/Allegro/PSpice documentation | Stage 2 native Capture ERC report | Stage 2 | Native ERC result with documented limitations | Local project evidence | schematic/orcad/stage2/reports/erc_report.txt | F6EBE402CB39A1CB115414544D4AE5A55EF60938BB81B2114DE9309ABBBFE0D3 (Git blob hash) | VERIFIED |
| SR-029 | IPC standards | IPC-2581 intelligent data exchange standard | exact edition 未找到 | Basis for IPC-2581 export interpretation | Restricted/controlled; metadata not archived | NOT_INCLUDED_IN_PUBLIC_PACKAGE | NOT_AVAILABLE | BLOCKED |
| SR-030 | IPC standards | IPC-D-356 electrical test/netlist format | exact revision 未找到 | Basis for IPC-356 output interpretation | Restricted/controlled; metadata not archived | NOT_INCLUDED_IN_PUBLIC_PACKAGE | NOT_AVAILABLE | BLOCKED |
| SR-031 | IPC standards | IPC-2152 current-carrying capacity method | exact revision 未找到 | Power copper/current-density calculation method | Restricted/controlled; metadata not archived | NOT_INCLUDED_IN_PUBLIC_PACKAGE | NOT_AVAILABLE | BLOCKED |
| SR-032 | JLCPCB stack-up/calculator | User Guide to the JLCPCB Impedance Calculator | dynamic process guide | Process for deriving width/gap from actual stack-up | Public | NOT_ARCHIVED | NOT_ARCHIVED | PRELIMINARY |
| SR-033 | JLCPCB stack-up/calculator | Multi-layer PCB standard laminated structures | dynamic manufacturing data | Candidate six-layer stack-up availability | Public | NOT_ARCHIVED | NOT_ARCHIVED | BLOCKED |
| SR-034 | JLCPCB stack-up/calculator | Controlled Impedance PCB Parameters and Stackup | dynamic manufacturing page | Fabricator workflow and assumptions | Public | NOT_ARCHIVED | NOT_ARCHIVED | BLOCKED |
| SR-035 | Connector drawings | MDT420M01501 controlled drawing | Rev A | Exact J2 mechanical/land-pattern source | Public vendor drawing | evidence/official_sources/Amphenol_MDT420M01501_Controlled_Drawing_RevA.pdf | 53319C6F88C261445C294383F884524B50791ECEE759F8B63848D76522A823D4 (manifest-recorded; file absent in public package) | PRELIMINARY |
| SR-036 | Connector drawings | PCIe M.2 Gen5 connector family datasheet | revision 未找到 | Connector family/key/height/data-rate screening | Public | evidence/official_sources/Amphenol_PCIe_M2_Gen5_Datasheet.pdf | E303EAD10F8BFA1A02F4DC243E6F674EDE09F7BA2028AEE1D532265900167F59 (manifest-recorded; file absent in public package) | OPEN |
| SR-037 | Connector drawings | MDT320M01001 backup connector / family drawing | revision 未找到 | Mechanical backup candidate | Public | NOT_ARCHIVED | NOT_ARCHIVED | OPEN |
| SR-038 | Mechanical models | MDT420M01501 official STEP model | vendor revision unstated | Exact J2 model availability | Vendor model; public product page/login conditions | pcb/3d_models/amphenol_mdt420m01501_vendor-c3d-rev-unstated_2026-07-24.stp | F5427DE4C21FD8C98D0425E09D63247DC632733ACE2211E52F6E282C68F593CD | VERIFIED |
| SR-039 | Mechanical models | WSK2512 vendor STEP model | revision unstated | Shunt mechanical body for 3DX | Vendor model | pcb/3d_models/vishay_wsk2512_0p005_to_0p2_vendor_30323_2026-07-25.stp | 5DB533DD5423847B51D33E38AAE9731AD1C178A526C6B0A4E40B933719442BF3 | VERIFIED |
| SR-040 | Mechanical models | Stage 3 generated model manifest | RevK candidate | Traceability for package-level and engineering-envelope models | Local engineering evidence | pcb/3d_models/stage3/stage3_generated_model_manifest.json | 8A7E8431B6029620655EE5EC8AA3888AA791AF129478142F8A0A371A6DFDB638 | PRELIMINARY |
| SR-041 | Mechanical models | Exact SSD/standoff/bracket/cable/chassis CAD set | 未找到 | Release-grade collision and chassis compatibility | Controlled/restricted where applicable | NOT_AVAILABLE | NOT_AVAILABLE | BLOCKED |
| SR-042 | SSD reference devices | WD Black SN750 1 TB product brief | A06 | Reference SSD identity: Gen3 x4, M.2 2280, 2.38 mm, 2.8 A/10 us | Public | evidence/official_sources/WD_BLACK_SN750_Product_Brief_en_us.pdf | 8852578D4BB9B0107F27810EC067B8B5C6B78250453540B6F09315751BC4CC03 (manifest-recorded; file absent in public package) | PRELIMINARY |
| SR-043 | SSD reference devices | Supported SSD matrix | RevK candidate | No supported SSD claim because recovery minimum is 3.109 V | Local engineering evidence | validation/supported_ssd_matrix.csv | 5ADCF934C9F580D8D73BBA47866857B89F4AF19624204342A614DDFFC42D1C4D | VERIFIED |
| SR-044 | SI/PI/layout references | Project constraint strategy | RevK candidate | Documents constraint intent without fabricated impedance values | Local engineering evidence | pcb/constraints.csv | 7B551C14FB1E4C940CC190FF75D1B71F78B1430ECEDD38A5E35837AE1D32680F | PRELIMINARY |
| SR-045 | SI/PI/layout references | TPS543620 layout guidance | Rev C | Buck hot-loop and switch-node layout method | Public | NOT_ARCHIVED | NOT_ARCHIVED | VERIFIED |
| SR-046 | SI/PI/layout references | Governing PCIe channel / SI reference set | 未找到 | Release-grade high-speed constraint and SI acceptance criteria | Controlled/restricted | NOT_AVAILABLE | NOT_AVAILABLE | BLOCKED |

## Review rules

1. Product landing page 只能證明來源入口與 orderable identity，不能取代 revision-controlled datasheet。
2. Datasheet 沒有 document number/revision 時維持 `OPEN`；release-critical source 缺失時為 `BLOCKED`。
3. Vendor PSpice model 必須同時記 ZIP/library hash、下載日期與版本；model source verified 不等於 simulation pass。
4. Restricted standards 不公開；review record 只能保存合法 metadata、reviewer、section/page 與 disposition。
5. Internal CSV/Markdown 是 traceability 輔助，不取代 native OrCAD/Allegro report、governing specification 或 physical measurement。
