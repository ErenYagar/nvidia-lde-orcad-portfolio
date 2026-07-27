# Power Measurement Plan

## 量測節點

| Node | 目的 | 儀器 | Probe 方法 | 狀態 |
|---|---|---|---|---|
| P12V_SLOT | 插槽輸入與 inrush | Differential probe／DMM | Edge 後第一個 test point | Planned |
| P12V_PROTECTED | eFuse 壓降與 fault response | Differential probe | eFuse OUT Kelvin point | Planned |
| P3V3_PRE_SENSE | Buck regulation | Low-noise probe | Buck output capacitor端 | Planned |
| P3V3_NVME | SSD 實際供電 | Low-noise probe | Shunt load-side capacitor端 | Planned |
| VSHUNT_P/N | SSD current | INA238＋differential probe | Kelvin sense pads | Planned |
| PGOOD_EFUSE | Protection timing | Logic probe | 10× high-impedance | Planned |
| PGOOD_3V3 | Buck timing | Logic probe | 10× high-impedance | Planned |
| SW_3V3 | Switch-node行為 | Rated probe | 極短 ground spring；僅由合格操作者量測 | Planned |

## Measurement Discipline

- 每次 capture 記錄 scope、probe、bandwidth、sample rate、time base、coupling、ground method。
- Ripple 同時保留 full-bandwidth 與明確 bandwidth-limited capture，不混用。
- Current probe 在測試前 degauss／zero；INA238 讀值以 shunt tolerance 與 reference DMM 交叉驗證。
- 溫升測試前記錄 ambient、airflow、SSD heatsink、case orientation。
- 不把 bench wire injection 的結果直接等同 PCIe slot 實際供電。

## Planned Conditions

- No-load、10% load、100% design load。
- Startup、shutdown、line ramp、load step、load release。
- 5A normal target。
- 7A／100µs engineering pulse，用於瞬態承受驗證，不等同 SSD 實測波形。
- Protection short／overcurrent 只在 current-limited fixture 與已核准程序中進行。

## Pass／Fail

具體電壓、ripple、droop、inrush、timing 與 temperature limit 必須在以下資料完成後寫入：

1. PCIe CEM slot power review。
2. Target SSD official power data。
3. TPS543620／TPS259472L 計算與 PSpice。
4. JLCPCB copper／thermal stack-up。

在此之前所有數值欄均為 `Pending_Human_Verification`，不得用示意值判定 Pass。

