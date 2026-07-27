# Requirements and Traceability

## 系統邊界

本專案設計單一 PCIe Gen3 x4 Add-in Card 至單一 M.2 2280 M-Key NVMe SSD。外部系統包含 host PCIe slot、NVMe SSD、I²C reader 與量測儀器；板上不包含 PCIe switch、retimer、redriver、MCU 或第二顆 SSD。

## Requirement matrix

| ID | Requirement | 類型 | 來源／理由 | 驗證方法 | 目前狀態 |
|---|---|---|---|---|---|
| SYS-001 | 板卡應提供 PCIe Gen3 x4 host-to-NVMe data path | Functional | 專案目標；[PCI-SIG CEM 3.0](https://pcisig.com/PCIExpress/Specs/CEM/CardElectromechanical_3.0) | net review、constraint report、planned enumeration | `Planned` |
| SYS-002 | 應支援單一 M.2 2280 M-Key NVMe SSD | Functional／Mechanical | 專案目標；M.2 governing spec 待取得 | drawing review、3D clearance、planned fit check | `Pending_Human_Verification` |
| SYS-003 | 板形應為 low-profile、half-length | Mechanical | 專案目標；PCIe CEM mechanical definition | outline dimension audit、bracket／chassis check | `Pending_Human_Verification` |
| IF-001 | Lane 0–3、P/N、TX/RX、REFCLK 與 sideband mapping 必須逐 pin 可追溯 | Interface | governing PCIe／M.2 requirements | 雙來源 pin review、CSV checker、schematic inspection | `Pending_Human_Verification` |
| IF-002 | 板上不得任意增加 PCIe lane AC coupling、termination、CMC 或 ESD | Signal integrity | 避免未經規格支持的 channel discontinuity | schematic BOM audit、design review | `Planned` |
| IF-003 | PERST#、CLKREQ#、PEWAKE#、PRSNT 應依 applicable specification 實作 | Interface | PCIe CEM／M.2 | pin map review、ERC、planned functional test | `Pending_Human_Verification` |
| PWR-001 | 主電源路徑應為 12 V slot → eFuse → buck → 3.3 V NVMe | Power | architecture decision | schematic review、netlist、planned power-up | `Planned` |
| PWR-002 | eFuse 應提供受控 slew／inrush、current protection 與 fault／PG visibility | Protection | Rev A safety／debug requirement；已選 [TI TPS259472LRPWR](https://www.ti.com/product/TPS25947/part-details/TPS259472LRPWR) | [power budget](power_budget.md)、ILIM／dV/dt／ITIMER／SOA 計算、PSpice、planned bench fault test | `Engineering_Assumption` |
| PWR-003 | 3.3 V buck 應以 5 A steady-state 為設計點 | Power | engineering target，不是 SSD universal rating | calculation、thermal estimate、PSpice、planned load test | `Engineering_Assumption` |
| PWR-004 | 電源應以 7 A / 100 µs load pulse 作 transient validation stimulus | Power transient | margin test；不是 continuous rating | PSpice load-step profile、planned electronic-load test | `Engineering_Assumption` |
| PWR-005 | 若 slot power、thermal 或 transient Gate 不通過，應限制支援 SSD 清單 | Safety／Product | 防止 overclaim | [supported SSD matrix](../validation/supported_ssd_matrix.csv)、release checklist 與 per-device evidence | `Planned` |
| MON-001 | 應量測 3.3 V NVMe rail 的 current、bus voltage 與 calculated power | Telemetry | debug／validation goal；[TI INA238](https://www.ti.com/product/INA238/part-details/INA238AIDGSR) | register readback、DMM correlation；尚未量測 | `Not_Yet_Measured` |
| MON-002 | 應提供 PCB 鄰近溫度 sensing，並明示不等同 SSD junction temperature | Telemetry | thermal debug；[TI TMP1075](https://www.ti.com/product/TMP1075/part-details/TMP1075DR) | I²C readback、reference thermometer correlation | `Not_Yet_Measured` |
| MON-003 | 應提供獨立 1×4 I²C header：GND、SCL、SDA、3.3 V sense，禁止外部回灌 | Interface／Safety | 專案邊界；[ADI ADP198](https://www.analog.com/en/products/adp198.html) reverse-current-blocking function | U5／RISO1 schematic review、label review、unpowered injection and output-short checks | `Planned` |
| PCB-001 | PCB 應使用六層結構，L1/L2 與 L6/L5 提供連續高速 reference | Layout | architecture baseline | stack-up／plane review | `Engineering_Assumption` |
| PCB-002 | 最終 impedance geometry 必須由投板當下板廠 stack-up 凍結 | Manufacturing | [JLCPCB calculator guide](https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator) | 保存 calculator、stack-up、quote evidence | `Pending_Fabricator_Confirmation` |
| PCB-003 | PCIe pairs 應以短、直、同層、對稱 transition 與鄰近 return vias 為原則 | Signal integrity | return-path control | Constraint Manager report、layout review | `Planned` |
| PCB-004 | Buck hot loop、switch-node keepout、Kelvin shunt 與 thermal vias 應完成專項 review | Power integrity | datasheet／layout best practice | layout review checklist、DRC | `Planned` |
| CAD-001 | OrCAD schematic 必須可重開、annotation 可重現、ERC 無未解釋項 | Tool／Quality | portfolio quality gate | native round-trip、ERC log | `Planned` |
| SIM-001 | 每個 PSpice profile 應記錄 model、condition、time step、stop time、probe 與 criteria | Simulation | reproducibility | profile review、run log | `Planned` |
| SIM-002 | 不支援的 loop stability／Monte Carlo 應標為 `Not_Supported_By_Model`，不得偽造 | Integrity | evidence policy | model／license audit | `Planned` |
| REL-001 | Release package 應包含 Gerber、NC Drill、IPC netlist、BOM、P&P、assembly drawing 與 checklist | Manufacturing | handoff readiness | CAM／package manifest audit | `Planned` |
| VAL-001 | Bring-up 應依 visual → shorts → current-limited power → rails → SSD → enumeration → stress 順序 | Validation／Safety | controlled bring-up | test traveler 與 debug log | `Planned` |
| VAL-002 | 實測前，enumeration、link width／speed、power、ripple、thermal 均維持 `Not_Yet_Measured` | Integrity | truth-in-evidence rule | repository status audit | `Not_Yet_Measured` |
| DOC-001 | 每個 critical data row 應有 source、status 與 review note | Traceability | project quality gate | CSV validation、peer review | `Planned` |
| DOC-002 | 所有對外材料不得宣稱 PCIe compliance | Portfolio integrity | project scope | README／slides／resume text audit | `Planned` |

## 驗收情境

1. **Pin conflict negative case**：同一 connector pin 指向不同 net 時，checker 必須 exit `1`，且 Gate 1 不得通過。
2. **Missing source negative case**：critical power／pin／impedance row 標為 `Confirmed_Official` 但沒有 `Source_Document` 時必須失敗。
3. **Power margin failure**：7 A pulse 造成 unacceptable droop、current limit 或 thermal margin 不足時，修正 power stage 或限制 SSD，不可修改 pass criteria 掩蓋問題。
4. **Fabricator change**：stack-up revision 改變時，重新計算 geometry 並重跑 Constraint Gate，不沿用舊 trace width。
5. **No hardware case**：即使 CAD 與 simulation 完整，只能報告 `Planned` bring-up／`Not_Yet_Measured` results。

## 需求變更控制

新增 SSD form factor、Gen4／Gen5、額外 connector、retimer 或 MCU 均視為 scope change，必須建立新 requirement、architecture review 與 revision；Rev A 不預留 speculative circuitry。
