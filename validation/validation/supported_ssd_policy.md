# Rev A Supported SSD Policy

## Current support statement

**目前沒有任何 SSD 被列為 Rev A supported device。**

5 A steady-state 與 7 A／100 µs 只是本板的設計與驗證 stimulus，不是任一 SSD 的
官方 power envelope，也不是通用 M.2 支援宣告。在 Power、Pin、Mechanical 與
hardware validation Gate 全部關閉前，對外說法只能是：

> Designed for evaluation with a single M.2 2280 M-Key NVMe SSD; the qualified
> device list is pending specification, simulation, and bench validation.

## Qualification states

| State | 必要證據 | 對外可宣稱內容 |
|---|---|---|
| `Candidate` | Exact manufacturer、model、capacity、firmware與官方 datasheet／power資料已保存 | 只可說列入評估 |
| `Power_Screened` | Normal、startup、peak、duration、power-state資料已與已確認的 slot／board envelope比較 | 只可說通過文件篩選 |
| `Simulated` | 使用該 SSD envelope 的 startup、inrush、steady、load pulse與 tolerance profiles均有可重現 pass結果 | 只可說通過指定模型與條件的模擬 |
| `Mechanically_Reviewed` | 2280 envelope、connector／standoff Z-chain、top／bottom keepout與散熱空間完成審查 | 只可說指定機構配置已審查 |
| `Bench_Qualified` | 指定 host、board revision、SSD firmware／capacity通過安全上電、enumeration、link、stress、power與thermal測試 | 只可說該明確配置通過功能驗證 |
| `Supported_RevA` | 上述證據齊全，所有 exception／ECO 關閉並由 reviewer簽核 | 才可進 Rev A supported list；仍不代表 PCIe compliance |

`Candidate`、`Power_Screened`、`Mechanically_Reviewed`、`Bench_Qualified` 與
`Supported_RevA` 是 qualification workflow labels，不取代 repository 的 evidence
status tokens。每筆證據仍須標示 `Confirmed_Official`、`Simulated`、
`Not_Yet_Measured` 等適用狀態。

## Mandatory screening criteria

任何 SSD 必須同時滿足：

1. Exact device 是 M.2 2280、M-Key、PCIe NVMe；容量、firmware與 hardware revision
   均可追溯。
2. Governing M.2 revision、Pin mapping、3.3 V tolerance、sideband與mechanical
   requirements已完成 Gate review。
3. Vendor official data 足以定義 normal、startup與peak power；沒有官方 envelope時，
   不以通路頁、平均功耗或其他容量版本替代。
4. Normal SSD current不得超過已驗證 continuous envelope；目前 5 A只是 design point。
5. Peak current與duration不得超過實際通過的 transient envelope；目前
   7 A／100 µs只是 planned stress case。
6. eFuse current limit、dV/dt、ITIMER、SOA與 slot inrush／power budget已協調。
7. 3.3 V rail、shunt range、inductor peak、PGOOD與元件額定在所有 tolerance corner
   均通過。
8. Connector、standoff、component keepout、heatsink／airflow與 low-profile chassis
   配置無干涉。
9. 在明確 host/platform 上完成 enumeration、negotiated link width／speed、
   NVMe identify、short test、stress、power與thermal validation。
10. 測試失敗、firmware差異或容量版本差異都建立 exception；不得外推到未測型號。

## Automatic exclusion conditions

符合任一條件即不得列為 `Supported_RevA`：

- 非 2280 M-Key NVMe，或需要本板未實作的 sideband／power feature；
- 缺少可追溯的 exact-device power envelope；
- normal、startup或peak demand超過已確認的 slot／board envelope；
- canonical PSpice profile出現 rail超限、current limit、hiccup、PGOOD fault或
  unacceptable inrush；
- `|VSHUNT|`、inductor peak、thermal margin或元件額定不通過；
- connector／SSD／standoff／bracket／heatsink存在未處置干涉；
- 無法在指定 host穩定 enumerate為預期 link width／speed；
- stress test出現 reset、AER、link downshift、I/O error、thermal throttling超出
  release criterion或不可解釋的 power fault；
- 任何必要證據仍是 `Pending_Human_Verification`、
  `Pending_Fabricator_Confirmation` 或 `Not_Yet_Measured`。

## Supported-device table

此表在 qualification evidence成立前刻意保持空白。

| Manufacturer | Exact model | Capacity | Firmware | Official power source | Simulation run IDs | Host／link result | Power／thermal result | Qualification state | Reviewer／date |
|---|---|---|---|---|---|---|---|---|---|

空表表示「尚無 qualified SSD」，不是缺少文件。

## Per-device evidence record

新增候選時，至少記錄：

- Manufacturer、exact model、capacity、hardware revision、firmware；
- datasheet URL、revision、download date、local path與SHA-256；
- normal／idle／startup／peak current or power，以及duration與測試條件；
- board revision、host、BIOS／OS／driver、airflow與ambient；
- PSpice run IDs及所有 pass/fail measurements；
- connector／standoff／heatsink mechanical review evidence；
- enumeration、BDF、VID／DID、negotiated speed／width與NVMe identify；
- workload、duration、error counters、rail min/max、input current與temperature；
- deviation、ECO、reviewer、date與最終qualification state。

## Release Gate

Rev A release checklist 必須同時確認：

- supported-device table不是空表，或 release notes明確宣告「無 qualified SSD，
  evaluation only」；
- 每個 `Supported_RevA` row都有完整 evidence record；
- marketing、README、slides與resume沒有把候選、模擬或單一樣品結果外推；
- functional qualification沒有被描述為 PCIe compliance。

