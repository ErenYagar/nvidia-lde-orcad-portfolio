# 電源預算與 Power Design Gate

## 文件狀態

- 設計階段：Rev A pre-freeze
- 架構：`P12V_SLOT` → TPS259472L eFuse → TPS543620 → `P3V3_PRE_SENSE` → 5 mΩ Kelvin shunt → `P3V3_NVME`
- 正常負載：3.3 V / 5 A
- 壓力測試：3.3 V / 7 A、100 µs；這是 `Engineering_Assumption`，不是 TPS543620 的連續額定宣稱
- 計算狀態：`Estimated`
- 模擬與量測狀態：`Planned` / `Not_Yet_Measured`

## 一頁結論

| 項目 | 正常 5 A | 7 A / 100 µs | 判讀 |
|---|---:|---:|---|
| SSD 輸出功率 | 16.500 W | 23.100 W | `P = V × I` |
| 5 mΩ shunt 壓降 | 25.05 mV | 35.05 mV | shunt 電流含 SSD 5/7 A 與下游 local 10 mA |
| shunt 損耗 | 0.126 W | 0.246 W | 100 µs 值不是連續熱額定 |
| `P3V3_PRE_SENSE` | 3.325 V / 5.010 A | 3.335 V / 7.010 A | feedback 在 shunt 後的 `P3V3_NVME` 時的估算 |
| Buck 輸出端需求 | 16.659 W | 23.379 W | `P = VPRE × ISHUNT`，未重複加總 shunt loss |
| Buck 輸入功率，η=90% 假設 | 18.509 W | 25.976 W | 效率尚待 PSpice／bench；此處是保守預算假設 |
| 12 V 端 Buck 電流 | 1.542 A | 2.165 A | 未含 eFuse 損耗 |
| eFuse 損耗，28.2 mΩ typ | 0.068 W | 0.134 W | 以 slot-side 1.548 A / 2.176 A 估算 |
| Slot 12 V 估算電流 | 1.548 A | 2.176 A | 未加入 connector/copper loss |

計算細節與機器可讀數字保留於原始工作包；public package 以本文件與
`pspice/stage2/profile_results.csv` 作為可審查摘要。PCIe CEM 插槽允許功率、inrush 與 12 V tolerance 尚未以
可授權的正式規格完成覆核，所以本文件**不宣告 Power Design Freeze**。

## 預算邊界

1. 5 A 是 SSD branch 的設計點；INA238、TMP1075、PGOOD pull-up 與 LED 的合計先保留
   10 mA allowance。現行接法為 shunt 後 `P3V3_NVME` 經 FB1 至 `P3V3_AUX`，所以 shunt、
   Buck output 與 upstream 計算使用 5.010 A / 7.010 A。
2. Buck 預算效率固定用 90%，目的為估計上游功率，不把它當作 TPS543620 保證值。
3. eFuse 計算使用 28.2 mΩ typical 與 45 mΩ worst-case 兩個 datasheet 值；worst-case 正常負載
   以 1.548 A 估算約 0.108 W。
4. Connector、edge finger、plane、via 與電感 core loss 尚未納入 slot 電流；layout 完成後必須
   由實際銅幾何補算。
5. 7 A 載入會使 TPS543620 超過 6 A continuous rating；只有 100 µs transient profile 通過且
   無 hiccup、PGOOD fault、過度 droop 或元件額定超限時，才可列為支援情境。

## 電壓回授與 shunt 壓降

Rev A 首選由 `P3V3_NVME` 端做 Kelvin feedback，使控制器補償 shunt 的 25.05 mV 正常壓降。
這條 sense trace 不承載負載電流，必須遠離 SW node，並在 OrCAD/ERC 與 layout review 中確認
沒有錯接。若模型或穩定度審查不允許 remote sense，則改在 `P3V3_PRE_SENSE` sense，並把
25.05 mV / 35.05 mV 壓降直接列入 SSD 端電壓 pass/fail。

## Power Design Gate

下列項目全部完成才可 Freeze：

- 以正式 PCIe CEM 文件確認 slot power、12 V operating range 與 inrush envelope。
- 取得目標 SSD 的 vendor power envelope；若超過本預算，建立明確 supported-SSD list。
- 依 [Supported SSD matrix](../validation/supported_ssd_matrix.csv) 保存 reference
  model／capacity／firmware與 qualification evidence；目前 supported-device table為空。
- 在 OrCAD PSpice 實跑 startup、5 A normal、5→7 A/100 µs、line transient 與 tolerance profiles。
- 驗證 high current-limit 模式下 7 A pulse 的 peak inductor current，不得碰到 8.6 A minimum
  high-side limit；模型量得的 margin 必須記錄。
- 以確切 MLCC 料號的 DC-bias 曲線確認 `COUT_EFFECTIVE ≥ 44 µF`；44 µF 只是初版下限。
- 以 PCB 實際銅面重算 TPS543620、TPS259472L、L1 與 shunt 溫升。
- 實板確認 `P3V3_NVME` 在正式 SSD tolerance 內；正式 tolerance 未確認前，內部設計目標用
  3.135 V 至 3.465 V（±5%）並標 `Engineering_Assumption`。
- 依官方 TPS25947 資料與本文件後續建立 eFuse setting worksheet；public package 未包含 worksheet
  關閉 UVLO、OVCSEL、CdVdt、RILM、CITIMER、PGTH、SOA 與 fault-policy corners；
  特別確認 472L 的 active-current-limit／thermal latch 行為是否符合系統需求。

## 可追溯來源

- TI, **TPS543620 datasheet Rev. C**, SLUSDR5C：4–18 V、6 A、Table 7-4/7-5、Table 8-2、
  Equation 6–19。<https://www.ti.com/lit/ds/symlink/tps543620.pdf>
- TI, **TPS25947 datasheet Rev. C**, SLVSFC9C：TPS259472L 功能、RON、ILIM、dVdt 與 thermal。
  <https://www.ti.com/lit/ds/symlink/tps25947.pdf>
- TI, **INA238 datasheet Rev. B**, SLYS025B：ADCRANGE 與 shunt full-scale。
  <https://www.ti.com/lit/ds/symlink/ina238.pdf>
- Vishay, **WSK2512 Power Metal Strip Resistors, 4-Terminal**：ordering code 與額定。
  <https://www.vishay.com/docs/30108/wsk2512.pdf>
