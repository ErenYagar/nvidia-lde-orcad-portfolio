# PCIe Gen3 x4 → M.2 NVMe 轉接板：技術專題報告（繁體中文）

英文完整版：[`PROJECT_REPORT_EN.md`](PROJECT_REPORT_EN.md)｜目前混合版主報告：[`PROJECT_REPORT.md`](PROJECT_REPORT.md)

**狀態：`Interview_Digital_Complete_Not_For_Fabrication`**

## 1. 專案摘要

本專題設計一張 low-profile、half-length、六層 PCIe Gen3 x4 add-in card，將主機 PCIe edge connector 實體連接到 M.2 M-Key 2280 NVMe SSD。它是 passive physical interposer，不是 protocol converter；Host Root Complex 與 NVMe controller 仍是協定端點。

目前完成的工作包含 Capture 介面資料、Allegro native board、placement、differential-pair objects、3DX/STEP handoff、PSpice profile、CAM 輸出、BOM/P&P 與 Python validators。Fabrication release、PCIe compliance、通用 SSD、chassis fit 與實體 bring-up 均未宣稱完成。

## 2. 實際功能與邊界

- **訊號：** J1 PCIe edge → 4 lanes 的 TX/RX、REFCLK、sideband → J2 M.2 M-Key 2280。
- **供電：** `P12V_SLOT` → TPS25947 family eFuse → TPS543620 6 A buck → 5 mΩ Kelvin shunt → `P3V3_NVME`。
- **遙測：** INA238 電流 monitor、TMP1075 溫度 sensor、target-only I²C header。
- **不包含：** PCIe switch、retimer、bridge、firmware、封包轉換或 host enumeration logic。

來源：[interface definition](docs/interface_definition.md)、[system block diagram](docs/system_block_diagram.md)。

## 3. 需求與驗證契約

| 需求 | 設計回應 | 目前狀態 |
|---|---|---|
| PCIe Gen3 x4 physical path | 八組 data pairs、REFCLK、sideband | Logical intent 有；physical pin freeze blocked |
| M.2 M-Key 2280 | J2 placement、SSD envelope、retention baseline | Preliminary |
| 六層、1.6 mm nominal | L1/L6 signal、L2/L5 GND、L3 control、L4 power | Native baseline 有；fabricator geometry pending |
| 3.3 V / 5 A normal | eFuse、6 A buck、Kelvin shunt | Engineering target，未 bench-qualified |
| 7 A / 100 µs pulse | Official buck model transient profile | Simulation-limited |
| 可審查交付 | reports、hash、3DX、STEP、CAM、validators | Digital package complete |

## 4. 架構選擇與設計決策

我比較了 slot 3.3 V distribution 與 slot 12 V + local conversion。最後選 Architecture B，因為它能在一個面試專題中呈現 eFuse、buck control、current sensing、hot-loop placement 與 PSpice；這不代表 B 在所有產品上都優於 A。

| 決策 | 選擇 | 理由與未完成風險 |
|---|---|---|
| 輸入電源 | 12 V + eFuse + buck | 可審查保護與轉換；slot budget/inrush 未由 controlled source 關閉 |
| Regulator | TPS543620 6 A | 5 A normal 與短暫 pulse；recovery 仍失敗 |
| 電流感測 | 5 mΩ 四端 Kelvin shunt + INA238 | 低壓降、可遙測；calibration/bench 未完成 |
| 高速調整 | 暫不加 AC caps、termination、CMC、ESD | 等 transmitter ownership 與 CEM/M.2 pin source 確認 |
| Layer strategy | L1/L6 參考 L2/L5，L4 為 power | Width/gap/via 等 JLCPCB stack-up 確認 |
| Manufacturing exchange | Gerber + NC Drill + IPC-2581-C | ODB++ 不支援；IPC-356 空檔排除 |

## 5. Capture 與電氣介面

`schematic/connection_matrix.csv` 是 logical source；`symbol_pinmap.csv`、`footprint_assignment.csv` 與 native ERC report 形成 pin-to-footprint traceability。由於受控 PCIe CEM/M.2 文件尚未納入公開 package，J1/J2 critical physical pins 保持 `Pending_Human_Verification`。B12/CLKREQ# 與 M.2 pin 32 的版本衝突被記錄，而不是猜測。

## 6. 電源與 PSpice

功率估算使用 `P = V × I`、5 mΩ shunt、effective capacitance 與明示的效率假設。主要結果：

| Profile | 結果 | 狀態 |
|---|---|---|
| Solver smoke | command-line solver concluded | Simulated |
| 5 A steady | 3.149 V minimum in recorded window | 僅該 model window pass |
| 7 A / 100 µs | 3.204 V minimum in recorded window | 僅該 model window pass |
| Recovery | 3.109 V，低於 3.135 V screen | **Simulated failure** |
| eFuse isolated run | 未達有效 output startup | Functional validation failed |
| COUT/ESR/CFF sweep | 27 cases 被 runtime limit 中止 | Not concluded |

因此目前不能由模擬推導 supported-SSD claim，也不能把 132 µF candidate 當成 released BOM。

## 7. PCB 與高速設計

RevK native board 已有 placement、power shapes、return-path intent 與九組 differential-pair objects（八組 data + 一組 REFCLK）。目前 gate report 記錄 DRC 0、unconnected 0、active rats 0、shape islands 0。

這是 digital PCB closure，不是 SI/PI sign-off。Pair width、gap、via、anti-pad、reference layer、skew 與 back-drill 必須等 JLCPCB stack-up 與 governing spec 到位後才能 freeze。

## 8. 機構、3DX 與 STEP

Native 3DX screenshots、portfolio views 與 AP242/mm STEP re-import 都已綁定目前 RevK board hash。SSD、J2、standoff、bracket 與 host chassis 並非全部 exact controlled models，因此碰撞案例只能是 `Preliminary_Clear` 或 `Blocked_Missing_Exact_Model`，不能由漂亮圖片升級為 Pass。

## 9. 製造輸出

Gerber、NC Drill、IPC-2581-C、BOM、preliminary P&P、assembly drawing evidence 與 STEP 均已輸出。IPC-356 為空檔並排除；安裝工具不支援 ODB++。所以這是 engineering review package，不是直接上傳板廠的 fabrication release。

## 10. 自動化與 negative tests

Python 使用 `csv`、`argparse`、`pathlib`、`unittest`，檢查 CSV schema、BOM 欄位、duplicate pins、net naming、Stage 2/3 evidence contract。Negative fixtures 覆蓋 missing column/MPN、duplicate pin、invalid net、pad mismatch、unplaced component、stale hash、missing evidence 與 false routing claim。Python 不解析 proprietary `.brd`/`.dsn`，也不取代 native Cadence review。

## 11. 結果與限制

| 區域 | 結果 |
|---|---|
| System architecture | Reviewable design intent closed |
| Native PCB digital closure | RevK DRC/connectivity/shape counters closed |
| Power topology | Preliminary baseline |
| PSpice | 5 A/7 A windows recorded；recovery failure |
| Constraint Manager | Pair objects 有；impedance geometry 未 freeze |
| 3DX/STEP | Handoff loop verified；exact fit preliminary |
| Manufacturing | Digital outputs generated；not fab-ready |
| Hardware | No physical measurement claimed |

## 12. Rev L 計畫

取得受控 CEM/M.2 規格、凍結 J1/J2 physical pins、匯入當期 JLCPCB stack-up、關閉 recovery 與 eFuse、替換 exact mechanical models，再執行 DFM、下板、上電、enumeration、Gen3 x4 link、NVMe identify、stress 與 thermal sequence。

## 13. 展示的能力

需求拆解、架構 trade-off、Capture/Allegro traceability、buck/shunt/power reasoning、differential-pair constraint、3DX/STEP handoff、CAM automation、negative testing、failure disclosure 與 release-gate communication。

## 14. 面試說法

- **30 秒：** 我設計的是 passive PCIe Gen3 x4 到 M.2 2280 physical adapter，並完成 Capture、power、Allegro、3DX/STEP、CAM 與驗證流程。
- **2 分鐘：** 說明 Architecture B、DRC/connectivity、3DX/STEP 與 power chain。
- **5 分鐘：** 主動展示 3.109 V recovery failure、nine pairs、pin-source gate 與 fabrication blockers。
- **10 分鐘：** 使用 [雙語面試指南](docs/INTERVIEW_GUIDE.md) 與 [claim matrix](docs/CLAIM_EVIDENCE_MATRIX.md) 做 evidence-based design review。
