# 元件候選集與 Rev A 推薦組

## 選型原則

本文件只把原廠資料已能支持的能力標成 `Confirmed_Official`。應用中的電流、熱、footprint、
供應鏈與模型相容性仍需在對應 Gate 完成。價格是 2026-07-23 的 qty-1 budgetary snapshot，
不是採購報價，也不會使尚未完成的 selection gate 自動關閉。

## Rev A 推薦組

| 功能 | 推薦料號／名義值 | 已知官方能力 | 專案狀態與理由 |
|---|---|---|---|
| eFuse | TI `TPS259472LRPWR` | 2.7–23 V family、active current limit、PG/PGTH、pin-selectable OVC；`L` variant在 thermal shutdown後 latch-off | exact MPN／Pin／fault behavior 為 `Confirmed_Official`；它不等同 ITIMER 到期即關斷的 `TPS259474L` circuit-breaker，OVCSEL、RILM、CdVdt、ITIMER、PGTH與SOA均保持 `Pending_Human_Verification` |
| Buck | TI `TPS543620RPYR` | 4–18 V、6 A、0.5–7 V、PGOOD、可選 0.5–4 ms soft-start、官方 PSpice transient model | `Engineering_Assumption`；1 MHz、high current-limit、1 ms soft-start baseline |
| 電感 | Coilcraft `XGL5050-152MEC` | 1.5 µH、DCR 4.7 mΩ typ/5.7 mΩ max、Isat 9.8 A（20% drop）、Irms 17.1 A（40°C rise） | 官方電氣值為 `Confirmed_Official`；footprint、hot inductance、core-loss、thermal 與供應仍待確認 |
| Buck local Cin | 2 × TDK `C3225X7R1E106K250AC` + HF bypass | 10 µF / 25 V / X7R / 1210、TDK `Production`；TI 要求 VIN–PGND local ceramic 與高頻 bypass | exact MPN 已進 BOM 但仍為 `Engineering_Assumption`；12 V DC-bias 未 Freeze |
| Buck Cout | 4 × TDK `C3225X7R1C226M250AC`；有效值設計下限 44 µF | 22 µF / 16 V / X7R / ±20% / 1210、TDK `Production` | exact MPN 已進 BOM 但仍為 `Engineering_Assumption`；88 µF nominal 不能等同 88 µF effective |
| Shunt | Vishay `WSK25125L000FEA` | WSK2512 四端、`5L000 = 0.005 Ω`、`F = 1%`、`EA` lead-free tape/reel | ordering identity `Confirmed_Official`；land pattern、pulse 與系統熱審查仍 pending |
| Power monitor | TI `INA238AIDGSR` | 16-bit I²C power monitor、2.7–5.5 V supply、ADCRANGE=1 為 ±40.96 mV | `Engineering_Assumption`；5 mΩ 時 nominal full-scale ±8.192 A，7 A=35 mV |
| Temperature | TI `TMP1075DR` | 1.7–5.5 V、I²C、D package | `Engineering_Assumption`；量 PCB local temperature，不宣稱 SSD controller junction temperature |

## 被動料候選但未核准

- Cin candidate：TDK `C3225X7R1E106K250AC`，10 µF / 25 V / X7R / 1210。
- Cout candidate：TDK `C3225X7R1C226M250AC`，22 µF / 16 V / X7R / ±20% / 1210。
- 上述 MPN 均為 `Pending_Human_Verification`：需在原廠 SimSurf/characteristic data 以 12 V 或
  3.3 V DC bias、溫度、AC ripple 取得 effective capacitance，再同步 manufacturing BOM。
- 若兩顆 Cin 在 12 V 的合計有效值不滿足設計需求，增加相同 MLCC 顆數或使用已驗證的
  25 V polymer bulk；不可只用 nominal µF 作結論。

原 Murata `GRM32ER71A226KE20L` 在 2026-07-23 的授權通路資料為 NRND，
`GRM188R71A105KA61D` 為 Obsolete；兩者已退出 Rev A 推薦組。原
`GRM21BR71E106KA73L` 未能以原廠／授權通路資料完成 lifecycle 證明，也不再作主選。

## A／B 組比較與相容性

下表的 `Drop-in` 只表示機械／Pin 層級候選，不代表可以跳過 simulation、thermal、
SI/PI、firmware 或 mechanical review。價格為 qty-1、USD、2026-07-23 snapshot。

| 功能 | Set A／單價 | Set B／單價 | Lifecycle／模型 | Drop-in 或必要 ECO | 結論 |
|---|---|---|---|---|---|
| PCIe edge | `CUSTOM-PCIE-GEN3-X4-EDGE`／PCB quote | N/A | Board feature／無模型 | 必須跟 CEM 與板廠共同凍結 | 無採購型 second source |
| M.2 connector | `MDT420M01501`／$4.09 | `MDT320M01001`／$2.42 | 兩者 Active；無 PSpice | Drawing、height、1:1 print、STEP fit 後才可判定 | B 是機構備選，不先稱 drop-in |
| eFuse | `TPS259472LRPWR`／$1.72 | `TPS259474LRPWR`／$1.72 | 兩者 Active；TPS25947 family transient model | RPW footprint 相同候選；overcurrent 行為不同，需設定與 fault-policy ECO | A 保留 latch-off baseline |
| Buck | `TPS543620RPYR`／$3.16 | `TPS543820RPYR`／約 $4.37 | 兩者 Active；A 有官方 PSpice，B model availability 待下載 smoke test | TI 宣稱 pin-to-pin family compatibility；仍需 BOM、MODE、thermal、transient 全重跑 | B 是 7 A pulse 失敗時首選 ECO |
| Current monitor | `INA238AIDGSR`／$3.26 | `INA226AIDGSR`／$2.66 | 兩者 Active；以 analytical/register model 為主 | DGS-10 相同不代表 Pin／register drop-in；需 symbol、firmware、range ECO | A 的 ±40.96 mV range 更符合本案 |
| Temperature | `TMP1075DR`／$0.54 | `TMP1075DGKR`／約 $0.46 | 兩者 Active；power transient 不需模型 | SOIC-8 與 VSSOP-8 不同 footprint | B 需要 PCB ECO |
| Sense reverse blocker | `ADP198ACPZ-R7`／$1.41 | `NO_EXACT_BACKUP_SELECTED` | A 為 Production；LTspice listed、PSpice 不宣稱 | 任何替代品都要證明 unpowered reverse-block／leakage | 未選定 B 是 release blocker |
| 5 mΩ Kelvin shunt | `WSK25125L000FEA`／$2.37 | `NO_EXACT_DROP_IN_SELECTED` | A Active；primitive R + parasitic | 必須同為四端、pulse/TC/land pattern 通過 | 未選定 B 是 supply-chain blocker |
| Inductor | `XGL5050-152MEC`／$4.11 | `XGL5050-182MEC`／quote | 兩者 Active；primitive L/DCR，飽和與 core loss 不完整 | 同系列 footprint 候選；L、DCR、Isat 變更需重算 | B 不是數值 drop-in |
| AUX ferrite | `BLM21PG221SN1D`／$0.11 | `RC0805JR-070RL`／約 $0.10 | 兩者 Active；primitive | B 會移除濾波功能，必須先通過 PI/EMI review | B 是 DNI／debug ECO，不是 second source |
| Buck Cin | `C3225X7R1E106K250AC`／$0.62 | `CL32B106KAULNNE`／$0.45 | 兩者 Active/Production；可用 vendor characteristic data | 1210 nominal match；仍比較 height、DC-bias、ESR/ESL、ripple | A 推薦 |
| Buck Cout | `C3225X7R1C226M250AC`／$0.61 | `GRM32ER71C226KEA8L`／$0.86 | 兩者 Active/Production；vendor curve + primitive | 1210；tolerance、thickness、DC-bias 與 land pattern 要重審 | A 推薦 |
| 小信號 MLCC／R | BOM 中 exact MPN／$0.10–0.15 | BOM `Alternative_Part` | selected exact parts為 Active/Production；primitive | 相同 case 不等於核准 AVL；value/tolerance/voltage/TCR 要逐列關閉 | 未列 exact B 的 resistor row 保持 blocker |
| Indicator | `2N7002-7-F` + `LTST-C190KGKT`／$0.35 | `2N7002ET1G` + `SML-E12M8WT86`／quote | 主選 Active；MOSFET vendor model／LED 無需模型 | G/S/D 與 LED polarity/brightness 都要 cross-probe | B 需 symbol/assembly ECO |
| Header／TP | `TSW-104-08-L-S-RA` + `S1751-46R`／$0.82 + $0.30 ea. | Header B 未選；TP `Keystone 5006` | 主選 Active；無 PSpice | Drill、tail、mating clearance、probe access 不同 | Header B 未選是 release blocker |
| Retention／bracket | `TBD_M2_2280_STANDOFF` + custom bracket／quote | 未選 | mechanical-only | 先凍結 connector stack height、CEM datum、chassis fit | 未完成，不可交付組裝 |

## 成本基準

- `manufacturing/bom.csv` 的 `Estimated_Cost_USD` 定義為 qty-1 unit cost；同一 line
  有多顆時以 `Quantity × unit cost` 計算。
- `manufacturing/cost_estimate.csv` 保存來源、存取日與 extended cost。
- 已有 exact MPN 且 Rev A 為 Populate 的 electronics priced subtotal 是 **US$30.79**。
- subtotal 不含 J1 PCB/controlled impedance、C2/C3、R1–R6、MH1、BR1、assembly、
  shipping、tax、tariff、reel fee 與 Coilcraft marketplace shipping。
- `TBD_AFTER_CEM` 與 `Quote_Required` 是刻意保留的 Gate，不是零成本。

## 主要候選比較

| 功能 | 候選 | 相對優點 | 風險／使用條件 | 結論 |
|---|---|---|---|---|
| eFuse | TPS259472L | Active current limit、PG、pin-selected clamp；限流／clamp造成 thermal shutdown後 latch-off | OVCSEL、RILM、dVdt、ITIMER、SOA與 fault recovery 需在 CEM review 後計算 | Rev A baseline；fault policy必須經 [setting worksheet](../calculations/efuse_setting_worksheet.md) 關閉 |
| eFuse | TPS259474L | ITIMER後 circuit-breaker shutdown、PG、adjustable OVLO；`L` variant保持 latch-off | 對 transient、overvoltage與desired behavior不同 | 備選；若要求 immediate circuit-breaker latch，再走 ECO |
| eFuse | TPS259470L | Adjustable OVLO、FLT | 無 PG/PGTH，與目前 sequencing 需求不完全相符 | 不推薦 Rev A |
| Buck | TPS543620 | 6 A、小型、官方 transient model、與計畫一致 | 7 A 只可當短 pulse；thermal margin 要驗證 | Rev A 推薦 |
| Buck | TPS543820 | 8 A、datasheet 宣稱與 TPS543620 pin-to-pin compatible | BOM、MODE、thermal 與模型需重新走 Gate | 若 7 A pulse 失敗的首選 ECO |
| Telemetry | INA238 | 85 V common-mode、16-bit、可選 ±40.96 mV range | 7 A 只剩 5.96 mV nominal headroom 到 full-scale | Rev A 推薦；tolerance 必測 |
| Temperature | TMP1075 | 簡單、I²C、標準封裝 | 只代表 sensor/PCB 溫度 | Rev A 推薦 |

## 關鍵設定

- `RFSEL = 11.8 kΩ, 1%`：TPS543620 nominal 1 MHz。
- `RMODE = 11.3 kΩ, 1%`：High current-limit、4 pF ramp、1 ms soft-start；與 TI
  TPS543620 Rev. C 3.3 V / 1 MHz reference（Figure 8-30）一致。
- `L1 = 1.5 µH`：TI Table 8-2 的 3.3 V / 1 MHz / 6 A recommended 值，允許範圍 1–3.3 µH。
- `RFB_BOTTOM = 4.99 kΩ, 1%`、`RFB_TOP = 28.0 kΩ, 1%`：以 0.5 V nominal reference
  得 3.305 V nominal；最終值需配合 Kelvin sense 位置與 tolerance profile。
- `CFF = 33 pF candidate/DNI-capable`：採 TI 3.3 V / 1 MHz reference baseline；
  只能在 loop/transient review 後 Freeze。
- eFuse `CdVdt`、`RILM`、`ITIMER`、`PGTH` 與 `OVCSEL`：全部維持 `TBD_AFTER_CEM_*`。
  先由正式 slot power／inrush、Buck startup、eFuse SOA 與 fault policy 算出 target，再用
  TI equation／calculator 和 tolerance profile 選值；不得把 datasheet example 當成 Rev A 設定。

## Selection Gate

1. Datasheet revision、orderable suffix、lifecycle 與 footprint 四項一致。
2. L1 的 Isat 必須高於 PSpice 量得的 worst-case peak，且以 hot DCR/Irms 檢查溫升。
3. Cin/Cout 必須以 exact MPN 的 DC-bias 曲線通過有效電容下限。
4. INA238 設 `ADCRANGE=1` 時，含 shunt +1%、load overshoot 的 `|VSHUNT| < 40.96 mV`。
5. 任何 7 A profile 觸發 current limit、hiccup、PGOOD fault 或 rail 超限，即限制 supported SSD
   或改評 TPS543820；不得把短 pulse 結果外推成連續 7 A。

## 官方來源

- <https://www.ti.com/lit/ds/symlink/tps543620.pdf>
- <https://www.ti.com/product/TPS543620>
- <https://www.ti.com/lit/ds/symlink/tps25947.pdf>
- <https://www.ti.com/product/TPS25947>
- <https://www.ti.com/lit/ds/symlink/ina238.pdf>
- <https://www.ti.com/lit/ds/symlink/tmp1075.pdf>
- <https://www.vishay.com/docs/30108/wsk2512.pdf>
- <https://www.coilcraft.com/en-us/products/power/shielded-inductors/molded-inductor/xgl/xgl5050/xgl5050-152/>
