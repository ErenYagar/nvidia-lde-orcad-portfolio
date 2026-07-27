# Fault Tree

> Probability 與 Severity 是 Rev A 工程排序，不是 field-return 統計。根因只有在診斷證據支持後才能確認。

| Symptom | Possible Cause | Probability | Severity | Diagnostic Test | Required Instrument | Expected Observation | Corrective Action | ECO Impact |
|---|---|---|---|---|---|---|---|---|
| 完全無法辨識 SSD | 無 3.3V、PERST#／REFCLK／lane pin map 錯、SSD/host 問題 | Medium assumption | Critical | 依序查 power→sideband→clock→lane continuity→換 SSD/slot | DMM、scope、lspci、TDR/continuity | 將 failure 隔離到電源、介面或外部平台 | 修正 power或 pin map；外部問題則更新 AVL | 可能重佈關鍵網路，High |
| SSD 偶爾消失 | droop、thermal、connector、AER、marginal SI | Medium assumption | High | 同步 log power、temperature、AER、mechanical perturbation | Scope、logger、thermal sensor | 消失時間與至少一項事件相關 | 依證據調電容、散熱、connector或 routing | Medium～High |
| Link Width 只有 x1 | lane 1～3 open/short、pin map、host bifurcation、SSD能力 | Medium assumption | High | 比對 LnkCap/LnkSta、continuity、lane swap、第二 host | lspci、DMM、TDR | 找到缺失 lane 或 platform限制 | 修正 lane connectivity或文件化 host限制 | High if PCB |
| Link Speed 只能 Gen1/Gen2 | host/SSD setting、loss/return path、clock、via discontinuity | Medium assumption | Medium | 強制/自動 link比較、AER、第二 host/SSD、layout review | lspci、scope、SI review | 降速可由平台或通道相關條件重現 | 修正 constraint／routing或支援清單 | Medium～High |
| 開機後卡住 | short、slot power trip、BIOS compatibility、PRSNT錯 | Low assumption | Critical | 無卡/無SSD/有卡分段啟動並監視12V | Bench supply、DMM、POST log | 卡住只在特定配置出現 | 修正 power/PRSNT；更新相容性 | High |
| 3.3V 無輸出 | eFuse disabled/latched、Buck EN/UVLO、assembly fault | Medium assumption | Critical | 量 VIN/EN/PG/SW/VOUT 並查 latch reset | DMM、scope | 第一個失效節點被定位 | 修正設定、焊接或 power chain | Medium |
| 3.3V 啟動後掉壓 | current limit、soft-start、inductor saturation、SSD peak | High assumption | Critical | 捕捉 startup current、SW、PG、eFuse status | Current probe、scope | 掉壓與限流/峰值同步 | 調整經驗證的 limit、L/C或限制 SSD | Medium～High |
| Ripple 過高 | layout loop、電容 derating、control mode、probe artifact | Medium assumption | High | 短 ground 重測、不同帶寬、檢查 SW/L/C | Scope、LCR meter | 區分真實 ripple 與 probing artifact | 修正 layout/component或量測程序 | Medium |
| Buck 過熱 | 損耗、SW頻率、copper/thermal via不足、過載 | Medium assumption | High | 量 input/output power與case/board溫度 | DMM、current probe、thermocouple | 溫升與負載／損耗相關 | 改頻率、copper、散熱或器件 | Medium～High |
| SSD 壓測降速 | SSD thermal、SLC cache、power cap、link error | High assumption | Medium | 同步 SMART、temperature、power、AER、workload phase | smartctl、fio、thermal logger | throttle原因與 log對應 | 改散熱；若板級則修正 power/SI | Low～Medium |
| I²C Telemetry 無法讀取 | 地址、pull-up、供電、header、bus stuck | Medium assumption | Low | 查 VCC、SCL/SDA idle、scan approved address | DMM、logic analyzer | 無 ACK或線被拉低 | 修正 strap/pull-up/接線 | Low |
| 電流讀值不準 | shunt tolerance、Kelvin錯、calibration、offset | Medium assumption | Medium | 以 reference load/DMM多點比對 | DMM、electronic load | error隨 offset/gain/temperature呈特徵 | 校正或修正 shunt routing/value | Low～Medium |
| 部分 PCIe Lane 開路 | connector solder、via/pad、fab defect、symbol錯 | Low assumption | High | Bare-board net test、X-ray、TDR、cross-probe | DMM、X-ray、TDR | 明確 open位置 | 返修僅作診斷；PCB ECO修正 | High |
| 不同主機板相容性不同 | BIOS、slot routing/power、ASPM、mechanical seating | Medium assumption | Medium | 固定 SSD/card，比較 host config與log | 多主機、lspci、scope | failure聚集於特定 host條件 | 更新 AVL/BIOS設定或改善 margin | Medium |

