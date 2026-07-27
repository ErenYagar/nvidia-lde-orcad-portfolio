# Power Architecture Trade-off

## 問題定義

NVMe SSD 需要 3.3 V 電源。Rev A 有兩個合理來源：

- **Architecture A**：直接使用 PCIe slot 3.3 V，經 eFuse／load switch、sense 與 filtering 後送至 SSD。
- **Architecture B**：使用 PCIe slot 12 V，經 eFuse 後由 synchronous buck 轉為 3.3 V。

本比較評估的不只是 BOM 數量，也包含 slot power boundary、inrush、thermal、PSpice 可驗證性、layout difficulty 與 NVIDIA LDE 面試價值。

## 比較矩陣

評分採 1（不利）至 5（有利）；分數是 `Engineering_Assumption`，在正式 power budget 前只用於決策排序。

| 評估面向 | 權重 | A：slot 3.3 V | B：12 V + buck | 判讀 |
|---|---:|---:|---:|---|
| 電路簡潔度 | 15% | 5 | 2 | A 元件少、轉換損耗少 |
| 可用電流／power flexibility | 20% | 2 | 4 | B 可能較容易配置較高 3.3 V load，但仍受 CEM slot budget 限制 |
| Inrush／fault control | 10% | 4 | 4 | 兩者皆可用 eFuse；B 還需管理 buck startup |
| Efficiency／thermal | 15% | 5 | 3 | A 少一級轉換；B 必須實證 efficiency 與溫升 |
| Noise／SI coexistence | 10% | 5 | 3 | B 增加 switch node 與 hot loop |
| PSpice／power-debug 展示價值 | 15% | 2 | 5 | B 可展示 startup、transient、control 與 layout judgment |
| Layout／bring-up 風險 | 10% | 5 | 3 | B 的 placement、return path 與 thermal 難度較高 |
| BOM／availability | 5% | 5 | 3 | B 料件較多且 exact variants 必須管控 |
| **加權分數** | **100%** | **3.85** | **3.45** | 分數不是唯一決策依據 |

## 決策

Rev A **暫定採 Architecture B**：

```text
P12V_SLOT
  -> TPS25947-family eFuse
  -> P12V_PROTECTED
  -> TPS543620 synchronous buck
  -> P3V3_PRE_SENSE
  -> 5 mΩ Kelvin shunt
  -> P3V3_NVME
```

原因不是 B 的加權分數較高，而是本作品集的主要目標包含 power budget、soft-start、inrush、load transient、Power Good、PSpice 與 power-layout review。這些能力與 LDE／board design 面試的關聯度高，且可以用明確 Gate 控制風險。

決策狀態為 `Engineering_Assumption`，尚未 Power Design Freeze。

## B 架構的強制退出條件

若任一條成立，Rev A 必須回到 Architecture A 或限制支援 SSD：

1. 正式 CEM 資料顯示 slot 12 V power／inrush 無法涵蓋定義負載與 margin。
2. TPS543620 在實際 Vin、temperature、frequency、inductor 與 PCB thermal 條件下不能支援 5 A steady-state。
3. 7 A / 100 µs stimulus 觸發 unacceptable droop、current limit 或 instability，且合理 Cout／layout 無法修正。
4. eFuse SOA、latch behavior 或 current-limit tolerance 與 buck startup 不相容。
5. switching converter 與 PCIe lane 的 placement／return-path isolation 在 low-profile half-length outline 內無法成立。
6. exact parts、footprints、models 或供應狀態無法在 release 前確認。

## 主要元件決策邊界

- [TPS543620](https://www.ti.com/product/TPS543620) 的官方產品頁列出 4–18 V input、6 A synchronous buck、Power Good、soft-start 與 PSpice transient model。這只證明元件功能，不代表本系統已通過 5 A／7 A case。
- [TPS25947](https://www.ti.com/product/TPS25947) family 提供可調 soft-start／current protection 及不同 fault behavior；已由 TI Rev. C truth table 選定 `TPS259472LRPWR`（active current limit、PG／PGTH、latch-off）。此確認只涵蓋料號功能與 Pin，不代表 slot power、ILIM、dV/dt、SOA 或 fault coordination 已通過。
- 5 mΩ shunt、INA238 gain range、rail drop、power dissipation 與 error budget必須整體計算，不以單一額定值選料。

## Decision record

| 項目 | 結論 | 狀態 | 下一個證據 |
|---|---|---|---|
| Power source | 優先 12 V slot | `Engineering_Assumption` | CEM slot power review |
| Protection | TPS259472LRPWR | `Engineering_Assumption` | ILIM／dV/dt／ITIMER／SOA 與 slot-power coordination |
| Buck | TPS543620 | `Engineering_Assumption` | component calculation + PSpice |
| Load envelope | 5 A normal；7 A / 100 µs stimulus | `Engineering_Assumption` | target SSD data + transient result |
| Fallback | Architecture A 或 restricted SSD list | `Planned` | Gate 2 decision |
