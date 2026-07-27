# 工程變更單（Engineering Change Order）— `<ECO-ID>`

> 本模板不得預填成功結果。未執行項目使用 `Planned`，未量測項目使用
> `Not_Yet_Measured`；只有附上證據後才能填 `Simulated` 或實測結論。

## 識別資料（Identification）

- 變更標題（Title）：
- ECO狀態（ECO Status）：Draft／Under_Review／Approved／Released／Rejected
- 來源問題／Debug Log（Originating Issue）：
- 受影響版本（Affected Revision）：
- 建議新版本（Proposed Revision）：
- 提出人／Owner：
- 審查人（Reviewers）：
- 建立日期／目標釋出日（Created／Target Release）：

## 問題與證據（Problem Statement & Evidence）

- 可重現症狀（Observed Symptom）：
- 重現條件與次數（Reproduction Conditions／Trial Count）：
- 已確認證據及路徑（Confirmed Evidence／Path）：
- 尚未排除的替代原因（Remaining Alternatives）：
- 安全／資料完整性／製造影響（Safety／Data Integrity／Manufacturing Impact）：
- 若不變更的風險（Risk of No Change）：

## 變更內容（Change Definition）

| Artifact／交付物 | Current／現況 | Proposed／建議變更 | Rationale／理由 | Owner | Status |
|---|---|---|---|---|---|
| Schematic／原理圖 | | | | | Planned |
| BOM／AVL | | | | | Planned |
| PCB／Constraints | | | | | Planned |
| Firmware／Test | | | | | Planned |
| Fabrication package | | | | | Planned |
| Assembly package | | | | | Planned |
| Validation／Interview docs | | | | | Planned |

## 影響分析（Impact Analysis）

| Domain／領域 | 影響與trade-off | 必須重跑的分析／測試 | Reviewer | Decision |
|---|---|---|---|---|
| Electrical／SI／PI | | | | Planned |
| Power／Telemetry | | | | Planned |
| Thermal | | | | Planned |
| Mechanical | | | | Planned |
| EMC／ESD | | | | Planned |
| Firmware／Software | | | | Planned |
| Manufacturing／Test | | | | Planned |
| Supply Chain | | | | Planned |

- 成本／時程（Cost／Schedule）：
- 相容性與supported-SSD影響（Compatibility）：
- 既有庫存／在製品／返工作法（Inventory／WIP／Rework Disposition）：
- 回復方案（Rollback Plan）：

## 製造交接（Fabrication & Assembly Handoff）

- Release manifest／版本／日期：
- Gerber或ODB++、NC Drill、IPC netlist：
- Fab drawing、正式stack-up、impedance／coupon要求：
- BOM、AVL、P&P、assembly drawing：
- Polarity／pin-1／DNI／特殊製程／rework notes：
- DFM／DFA問題與處置：
- Package checksum／檔案雜湊：
- 板廠／代工廠通知人與確認日期：

## 驗證矩陣（Verification Matrix）

| Test ID | Before-change reproduction | After-change test | Pass／Fail Criteria | Evidence Path | Result／Status |
|---|---|---|---|---|---|
| | | | | | Planned |

- ERC／DRC／netlist／BOM一致性：
- PSpice／corner analysis：
- Bring-up regression：
- PCIe enumeration／link width／speed：
- Power／thermal／telemetry：
- Mechanical fit／assembly：
- Compatibility regression：
- 失敗時的stop condition：

## 核准與釋出（Approval & Release）

| Role／角色 | Name | Decision | Date | Evidence／Notes |
|---|---|---|---|---|
| Board Design | | Planned | | |
| SI／PI | | Planned | | |
| Thermal | | Planned | | |
| Mechanical | | Planned | | |
| EMC | | Planned | | |
| Manufacturing／Assembly | | Planned | | |
| Validation | | Planned | | |
| Release Owner | | Planned | | |

- 最終release revision：
- 舊版封存位置（Archive Location）：
- CHANGELOG／source log更新：
- ECO關閉條件（Closure Criteria）：
