# Risk Register

評分方式：Probability（P）與 Severity（S）各為 1–5，初始優先度為 `P × S`。分數是專案管理用 `Engineering_Assumption`，不代表實測失效率。

| ID | 風險 | P | S | 觸發條件／早期訊號 | 預防與緩解 | 驗證／關閉證據 | Owner | 狀態 |
|---|---|---:|---:|---|---|---|---|---|
| RSK-001 | PCIe TX/RX、lane 或 polarity mapping 錯誤 | 3 | 5 | 來源間命名視角不一致；pin row 無雙來源 | 建立 board-centric net naming；逐 pin 雙人覆核；Gate 1 前禁止正式接線 | signed pin-map review、netlist audit | Schematic | `Pending_Human_Verification` |
| RSK-002 | AC coupling ownership 判斷錯誤，造成重複或缺少 capacitor | 3 | 5 | host／SSD transmitter ownership 未明；相近 reference design 作法不同 | 只依 governing spec 與 endpoint implementation evidence 決策；Rev A 不任意加料 | source excerpt reference、schematic review | SI | `Pending_Human_Verification` |
| RSK-003 | PCIe slot 12 V power／inrush 不足 | 3 | 5 | power budget 接近 CEM limit；eFuse startup 觸發保護 | 先完成 CEM power review、target SSD envelope 與 inrush model；必要時限制 SSD | Gate 2 record、supported SSD list | Power | `Pending_Human_Verification` |
| RSK-004 | 6 A buck 無法承受 5 A steady-state thermal condition | 3 | 5 | estimated junction／board temperature margin 不足 | 使用 [TPS543620 datasheet](https://www.ti.com/lit/ds/symlink/tps543620.pdf) 計算 loss／thermal；改善 copper 或降額 | calculation review、planned thermal test | Power／PCB | `Planned` |
| RSK-005 | 7 A / 100 µs pulse 造成 droop、current limit 或 instability | 4 | 4 | PSpice rail droop 超出 SSD requirement；inductor saturation | 以可追溯 model 做 load-step；調整 Cout／inductor／limit 或限制 SSD | PSpice run package；planned bench correlation | Power | `Planned` |
| RSK-006 | TPS259472L 系統設定或模型 variant 不一致，fault response 不符需求 | 3 | 5 | 472L 在 ITIMER後是 active current limit，`L` latch發生於 thermal shutdown後；若被誤當 474L circuit-breaker，fault energy與recovery會錯估 | 依 [eFuse setting worksheet](../calculations/efuse_setting_worksheet.md) 鎖定 fault policy；BOM／symbol／model／設定四方比對；必要時以 474L ECO重做 overvoltage／fault驗證 | configuration review、SOA與fault-profile correlation | Power／Library | `Planned` |
| RSK-007 | eFuse SOA 在 startup／short condition 超限 | 3 | 5 | large Cout、slow slew 或 short event 使 die heating 過高 | 計算 inrush、timer、SOA；PSpice 與 planned current-limited bench test | SOA worksheet、fault test log | Power | `Planned` |
| RSK-008 | 5 mΩ shunt 壓降、功耗或 telemetry range 不合 | 3 | 3 | INA238 full-scale／calibration 不匹配；shunt 溫升過高 | 建立 error budget、power／TCR／Kelvin review；確認 exact WSK2512 suffix | calculation、layout inspection、planned DMM correlation | Telemetry | `Planned` |
| RSK-009 | I²C header 外部回灌 3.3 V rail | 3 | 4 | external controller 帶電且板卡未上電 | 使用 U5 ADP198 reverse-current blocker 加 RISO1；header 標示 sense-only；檢查 pull-up ownership | schematic review、reverse leakage calculation、unpowered injection／short test | Telemetry／Validation | `Planned` |
| RSK-010 | M.2 connector footprint 或 standoff 高度錯誤 | 3 | 5 | exact drawing 不可得；使用相近 suffix footprint | 不從 family drawing 猜測 land pattern；保存 exact drawing；1:1 print、3D 與實體零件核對 | signed footprint validation | Mechanical／Library | `Pending_Human_Verification` |
| RSK-011 | JLCPCB stack-up 改版導致 impedance geometry 失效 | 3 | 5 | quote 時 laminate／copper／prepreg 與設計假設不同 | release 當天重新取得 stack-up 與 calculator evidence；geometry change 重新跑 constraints | fabricator evidence、constraint diff | PCB／Manufacturing | `Pending_Fabricator_Confirmation` |
| RSK-012 | 高速 pair 跨 plane split 或缺 return path | 3 | 5 | placement 迫使 layer transition／L4 split reference | 優先 L1/L2；必要 transition 成對且加鄰近 GND vias；逐 pair return-path review | layout screenshots、constraint report | PCB／SI | `Planned` |
| RSK-013 | Buck switch node／hot loop 耦合至 PCIe lane | 3 | 4 | power stage 靠近 connector breakout；lane 經過 SW keepout | floorplan 先隔離 power 與 high-speed；最小化 hot loop；建立 SW keepout | placement review、layout review | PCB／Power | `Planned` |
| RSK-014 | PSpice vendor model 不收斂或不支援目標分析 | 4 | 3 | startup failed、hidden limits、loop model 不可用 | 保存 model version／hash；先跑 vendor example；記錄 solver／limitation；不偽造結果 | run log 或 `Not_Supported_By_Model` record | Simulation | `Planned` |
| RSK-015 | OrCAD 25.1 license／feature 不足 | 2 | 4 | Capture、Advanced Analysis、ODB++ export 無法啟動 | 先做 license smoke test；將 optional output 明示；不以手工檔案替代 native data | tool/version/license log | CAD | `Pending_Human_Verification` |
| RSK-016 | 供應或 lifecycle 變化使 selected part 不可採購 | 3 | 3 | manufacturer status／stock 改變；alternative 未驗證 | release 前重新查原廠 lifecycle 與 AVL；備選料需獨立 footprint／electrical review | dated AVL／BOM review | Component／Manufacturing | `Planned` |
| RSK-017 | Enumeration 成功被誤寫成 compliance 通過 | 2 | 5 | slide／resume 使用「compliant」字樣但無 lab report | 全 repository claim audit；固定用 functional bring-up／link verification 語句 | document grep、review sign-off | Project owner | `Planned` |
| RSK-018 | 將 simulation／estimate 誤當 measurement | 2 | 5 | 圖表缺 evidence type、instrument、date 或 conditions | 每張圖標 `Simulated`／`Estimated`／`Not_Yet_Measured`；量測才記 instrument／setup | evidence audit | Project owner | `Planned` |

## Top-five review focus

目前最高關注為 RSK-001、RSK-003、RSK-004、RSK-007、RSK-010／011／012。它們共同特徵是一次錯誤可能造成無法 enumerate、電源保護誤動作、熱失效、機構不相容或整板重製，因此必須在對應 design gate 前關閉，不接受「layout 後再看」。

## 升級與 ECO 規則

- `P × S ≥ 15`：必須在 PDR／CDR 明確 review，未關閉不得 release。
- 新 evidence 推翻既有假設時，先更新 requirement、assumption 與 source log，再修改 CAD。
- 實體測試失敗時建立 debug log，先保存 symptom、conditions 與 observation，再提出 corrective action。
- 任何改動若影響 pin、power、stack-up、footprint 或 manufacturing output，必須新建 ECO 並重新跑相依檢查。
