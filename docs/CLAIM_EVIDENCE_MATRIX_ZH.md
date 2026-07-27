# Claim / Evidence Matrix（繁體中文）

English version：[`CLAIM_EVIDENCE_MATRIX.md`](CLAIM_EVIDENCE_MATRIX.md)

狀態定義：`VERIFIED` = 有目前 repository artifact 直接支持；`PRELIMINARY` = 設計意圖或初步審查；`SIMULATION-LIMITED` = 有模型／runtime 邊界的模擬結果；`BLOCKED` = 必要輸入或 gate 缺少；`OPEN` = 尚未量測或尚未結論。

| Claim | 狀態 | 為何重要 | Evidence | 證明什麼 | 不證明什麼 |
|---|---|---|---|---|---|
| 板子是 passive PCIe-to-M.2 physical interposer，不是 protocol converter | VERIFIED | 避免錯誤描述系統功能 | [`docs/interface_definition.md`](interface_definition.md) | Host 與 SSD 仍是協定端點 | 成功 enumeration 或 compliance |
| Architecture B 為 12 V → eFuse → buck → shunt → 3.3 V | PRELIMINARY | 說明電源 trade-off | [`docs/architecture_tradeoff.md`](architecture_tradeoff.md) | topology 與選擇理由 | 完整元件設定或 bench performance |
| 六層、120 × 64 mm、1.6 mm nominal baseline 存在 | PRELIMINARY | 定義設計 envelope | [`evidence/stage3/final_release_status.md`](../evidence/stage3/final_release_status.md) | 目前 native baseline | CEM outline、chassis fit、fab release |
| RevK native board DRC=0、unconnected=0、active rats=0、shape islands=0 | VERIFIED | 證明 digital PCB closure | [`evidence/stage3/stage3_delivery_gate.md`](../evidence/stage3/stage3_delivery_gate.md) | 目前 board counters | SI/PI、製造性或電氣性能 |
| 有八組 data pairs 加一組 REFCLK pair | VERIFIED | 讓高速意圖可審查 | [`pcb/differential_pairs.csv`](../pcb/differential_pairs.csv) | 九組 logical/native pair objects | Frozen impedance 或 eye quality |
| PCIe lane、sideband、power logical names 完整 | PRELIMINARY | 提供穩定 source interface | [`schematic/connection_matrix.csv`](../schematic/connection_matrix.csv) | P/N naming 與 net intent | J1/J2 正確 physical pin numbers |
| J1/J2 critical physical pins 已 freeze | BLOCKED | 錯誤 mapping 會破壞功能 | [`docs/pcie_m2_pin_mapping.md`](pcie_m2_pin_mapping.md) | B12/Pin32 conflict 被記錄 | 所有 pin 已 Confirmed |
| 沒有加入 lane AC caps、termination、CMC、ESD | PRELIMINARY | 保留 transmitter ownership | [`docs/interface_definition.md`](interface_definition.md) | 目前設計選擇 | 所有規格版本下的 compliance |
| 3.3 V / 5 A 是 normal design target | PRELIMINARY | 定義 power sizing | [`docs/power_budget.md`](power_budget.md) | engineering target | qualified continuous SSD support |
| 7 A / 100 µs 是 transient pulse study | SIMULATION-LIMITED | 測試 transient headroom | [`pspice/stage2/profile_results.csv`](../pspice/stage2/profile_results.csv) | profile 與 threshold window | supported SSD power rating |
| Startup、5 A、7 A、PGOOD profile 已執行 | SIMULATION-LIMITED | 顯示可重複的 power analysis | [`pspice/stage2/profile_results.csv`](../pspice/stage2/profile_results.csv) | raw disposition 與觀察 | layout parasitics、thermal、silicon guarantee |
| 88 µF official-model recovery 到 3.109 V | SIMULATION-LIMITED | failure 沒有被隱藏 | [`pspice/stage2/profile_results.csv`](../pspice/stage2/profile_results.csv) | recovery screen failure | final capacitor recommendation |
| 27-case COUT/ESR/CFF sweep 已結案 | OPEN | 防止誤稱 tuning pass | [`pspice/stage3/recovery_sweep/recovery_sweep_results.csv`](../pspice/stage3/recovery_sweep/recovery_sweep_results.csv) | cases、hash、runtime disposition | sweep pass/fail closure |
| TPS25947x eFuse behavior 已 validation | BLOCKED | inrush/fault 是安全 gate | [`pspice/stage2/profile_results.csv`](../pspice/stage2/profile_results.csv) | `Fail_Functional_Validation` | current-limit、latch-off、SOA proof |
| INA238/TMP1075 telemetry paths 已設計 | PRELIMINARY | 建立 observability | [`docs/interface_definition.md`](interface_definition.md) | shunt/temp/I²C paths | address、calibration、measured telemetry |
| Native 3DX screenshots 綁定目前 board | VERIFIED | 讓視覺 evidence 可追溯 | [`evidence/stage3/3dx_native_revk/`](../evidence/stage3/3dx_native_revk/) | RevK status 與 native views | exact host/chassis mating fit |
| AP242/mm STEP 可 export 且可 isolated re-import | VERIFIED | 證明 MCAD handoff loop | [`evidence/stage3/3d_status.md`](../evidence/stage3/3d_status.md) | units/orientation/readback | exact transforms 或 production acceptance |
| 所有 3D collision cases 都 Pass | BLOCKED | 需要 exact model/rule | [`evidence/stage3/3d_status.md`](../evidence/stage3/3d_status.md) | preliminary/blocked dispositions | 缺模型時的 Pass |
| Gerber、NC Drill、IPC-2581-C 已生成 | VERIFIED | 證明 digital manufacturing output | [`manufacturing/stage3_final_revk/export_status.csv`](../manufacturing/stage3_final_revk/export_status.csv) | files 與 export records | DFM approval 或 board-house quote |
| ODB++ 完整且 IPC-356 可用 | OPEN | 防止格式 overclaim | [`manufacturing/stage3_final_revk/export_status.csv`](../manufacturing/stage3_final_revk/export_status.csv) | 不支援／空檔已揭露 | 這兩種格式已交付 |
| Supported SSD list 已 qualification | PRELIMINARY | 限制產品聲明 | [`validation/supported_ssd_matrix.csv`](../validation/supported_ssd_matrix.csv) | reference-policy structure | universal compatibility 或 bench qualification |
| CSV validators 與 negative fixtures 可重複 | VERIFIED | 展示 rule-driven automation | [`scripts/`](../scripts/) | schema/negative-test behavior | native binary correctness 或 board performance |
| Fabrication-ready release 已存在 | BLOCKED | 區分 interview closure 與板廠 release | [`evidence/stage3/final_release_status.md`](../evidence/stage3/final_release_status.md) | 明確 false status 與 blockers | 可直接下單 |
| Physical enumeration、Gen3 x4、NVMe identify、thermal 已完成 | OPEN | 這是最終硬體驗證 | [`PROJECT_PLAN.md`](../PROJECT_PLAN.md) | gap 被承認 | 任何 measured hardware outcome |
