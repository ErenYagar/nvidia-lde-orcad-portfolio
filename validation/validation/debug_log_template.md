# 除錯紀錄（Debug Log）— `<ISSUE-ID>`

> 先保存raw evidence，再寫interpretation。未執行測試填 `Planned`，尚無實測填
> `Not_Yet_Measured`；若證據不足，root cause必須填 `Not confirmed`。

## 基本資料（Metadata）

- 日期／負責人（Date／Owner）：
- Issue狀態（Issue Status）：Open／Investigating／Monitoring／ECO_Required／Closed
- Board revision／serial：
- ECO state／reference：
- Host／BIOS／slot：
- SSD／firmware：
- OS／kernel／driver：
- Instruments／asset ID／calibration due：
- 原始資料目錄（Raw Evidence Path）：

## 症狀定義（Symptom Definition）

- 精確觀察（Exact Observation）：
- 首次出現（First Occurrence）：
- 預先宣告試驗次數／重現率（Trial Count／Reproduction Rate）：
- 預期行為與pass/fail（Expected Behavior／Criteria）：
- 安全／資料損毀／硬體損壞風險（Safety／Data Integrity Impact）：
- Stop condition／立即停測條件：

## 基準與變更（Baseline／Changes）

- Last known good／最後正常版本：
- Hardware changes：
- Schematic／BOM／layout revision：
- Software／BIOS changes：
- SSD／host substitution：
- Environmental changes（temperature／airflow／power source）：
- 與基準不同但尚未控制的變數（Uncontrolled Variables）：

## 測量完整性（Measurement Integrity）

- Probe node／reference／bandwidth：
- Current direction／polarity convention：
- Sample rate／record length：
- Instrument loading／fixture／cable：
- Calibration／zero／deskew：
- Simulation model revision／SHA-256（若適用）：
- 測量限制（Known Measurement Limitations）：

## 假設清單（Hypotheses）

| ID | Hypothesis／假設 | Evidence For／支持 | Evidence Against／反證 | Next Discriminating Test／區分測試 | Owner | Status |
|---|---|---|---|---|---|---|
| H1 | | | | | | Planned |

## 測試紀錄（Test Log）

| Time／Run ID | Test／目的 | Controlled Setup／設定 | Raw Evidence／原始證據 | Observation／觀察 | Interpretation／解讀 | Result Status |
|---|---|---|---|---|---|---|
| | | | | | | Planned |

## Load Transient 專用欄位（如適用）

- Load low／high：
- Rise／fall time：
- Pulse width／repetition：
- Effective Cin／Cout：
- Source impedance／VIN：
- VOUT min／max／settling：
- Inductor／input／shunt current peak：
- PGOOD／current-limit／hiccup：
- Criterion source／status：

## 跨領域分流（Cross-functional Triage）

| Domain | 問題／所需輸入 | Evidence Package | Owner／Reviewer | Next Action | Status |
|---|---|---|---|---|---|
| SI／PI | | | | | Planned |
| Power／Thermal | | | | | Planned |
| Mechanical | | | | | Planned |
| EMC／ESD | | | | | Planned |
| Fabrication／Assembly | | | | | Planned |
| Firmware／Host | | | | | Planned |

## 結論與後續（Conclusion & Next Actions）

- Confirmed root cause／已確認根因：
- Confidence／信心與remaining alternatives：
- Corrective action／修正措施：
- 為何此測試能區分假設（Discriminating Evidence）：
- Regression tests／回歸測試：
- Affected artifacts：
- ECO trigger／reference：
- Owner／due date：
- 關閉條件（Closure Criteria）：

> `Closed` 必須連到可重現的before evidence、修正後evidence與回歸結果；只有「問題沒有再出現」
> 不足以證明root cause。
