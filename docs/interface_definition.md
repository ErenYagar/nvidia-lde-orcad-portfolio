# 介面定義

## 文件目的與狀態

本文件定義 Rev A PCIe Gen3 x4 Add-in Card（AIC）轉 M.2 M-Key 2280 NVMe 的邏輯介面邊界。它是 Capture 接線、Constraint Manager 分類及 bring-up 的共同輸入，不是 PCIe compliance 證明。

截至 2026-07-23，PCIe CEM 3.0 與 M.2 controlled specification 的實體 Pin mapping 尚未完成雙來源逐 Pin 覆核。因此：

- 邏輯訊號名稱、方向與設計所有權已定義。
- J1 PCIe edge 與 J2 M.2 的實體 Pin number 一律維持 `Pending_Human_Verification`。
- 不得從網路圖片、第三方 pinout 或記憶填入 Pin number。
- `schematic/connection_matrix.csv` 是連接真相來源；本文件僅描述介面契約。

## 系統邊界

| 邊界 | 本板角色 | 對端 | 本板責任 |
|---|---|---|---|
| J1 PCIe edge | Endpoint add-in card interposer | PCIe Root Complex / slot | 接收四組 host TX、送出四組 device TX、接收 REFCLK 與 reset、取得 12 V |
| J2 M.2 M-Key | M.2 host socket | 2280 NVMe SSD | 將 host lane 直通至 SSD、供應受保護的 3.3 V、提供標準 sideband |
| J3 I²C debug header | I²C target-only telemetry | 外部 USB-to-I²C 或 MCU master | 只提供 GND、SCL、SDA、high-impedance 3.3 V sense；不得供電或回灌 |
| 機構 | Low-profile half-length AIC | 機箱、bracket、SSD | 維持 edge datum、bracket、2280 standoff 與 keepout |

## 高速 PCIe 介面

### 邏輯訊號

| Net | 來源 → 目的 | 類型 | AC coupling 所有權 | 目前狀態 |
|---|---|---|---|---|
| `PCIE_TX[0..3]_[P/N]` | J1 host TX → J2 SSD RX | PCIe Gen3 differential | Host transmitter 端；本板不加電容 | `Pending_Human_Verification` |
| `PCIE_RX[0..3]_[P/N]` | J2 SSD TX → J1 host RX | PCIe Gen3 differential | SSD transmitter 端；本板不加電容 | `Pending_Human_Verification` |
| `PCIE_REFCLK_[P/N]` | J1 → J2 | Differential reference clock | 不適用；本板不加串聯元件 | `Pending_Human_Verification` |

`TX`／`RX` 命名固定以 PCIe slot／host 視角定義。任何 Capture 頁面、PCB net、測試文件均不得改用局部元件視角。每一 lane 必須保留 P/N 極性；不得為了便利而在未留下 ECO 記錄的情況下交換 polarity 或 lane。

本板是被動 lane 直通，沒有 switch、retimer、redriver、common-mode choke、高速 TVS、額外 termination 或額外 AC coupling capacitor。若 SI review 要求新增器件，必須先記錄 governing specification、channel budget 影響與新 PSpice／S-parameter 驗證計畫。

### 高速驗收 Gate

1. PCI-SIG CEM 3.0 controlled copy 確認 J1 lane、REFCLK、sideband、PRSNT 與電源 Pin。
2. M.2 controlled specification 確認 J2 M-Key lane、REFCLK、sideband、3.3 V、ground 與 key/no-connect Pin。
3. 以第二份原廠公開 reference design 逐 lane 交叉檢查 TX/RX 方向與 P/N。
4. 兩位 reviewer 或「建立者＋獨立 checker」簽核 `pcie_m2_pin_mapping.md`。
5. Gate 通過前禁止建立 native `.dsn` 或凍結 footprint。

## Sideband 介面

| Net | 方向（相對本板） | 電氣意圖 | Fail-safe 規則 |
|---|---|---|---|
| `PCIE_PERST_N` | J1 → J2 | Host reset 至 SSD | 不在本板反相；上電時序由正式規格覆核 |
| `PCIE_CLKREQ_N` | J2 → J1 | SSD clock request | 視為 open-drain 類別，禁止未經規格確認的強驅動或本地 pull-up |
| `PCIE_PEWAKE_N` | J2 → J1 | SSD wake request | 視為 open-drain 類別，禁止未經規格確認的強驅動或本地 pull-up |
| `PCIE_PRSNT_N` | J1 edge 內部連接 | Add-in card presence detect | 連接方式與實體 Pin 由 CEM controlled copy 決定 |

sideband 的 voltage domain、pull-up 所有權與 rail sequencing 在正式規格查核前均為 `Pending_Human_Verification`。不得把 PCIe SMBus 連到 telemetry I²C。

## 電源介面

固定電源樹：

```text
J1 P12V_SLOT
  -> U1 TPS25947-family eFuse
  -> P12V_PROTECTED
  -> U2 TPS543620 + L1/COUT
  -> P3V3_PRE_SENSE
  -> RSH1 5 mΩ four-terminal Kelvin shunt
  -> P3V3_NVME
  -> J2 M.2 power pins
```

| Rail | 正常目標 | 短時驗證目標 | 狀態／限制 |
|---|---:|---:|---|
| `P12V_SLOT` | 由 PCIe slot 供應 | 依 CEM inrush／slot power | Pin、功率與 inrush 尚未完成正式規格覆核 |
| `P12V_PROTECTED` | U1 後級 12 V | 受 current limit 與 soft-start 約束 | U1 已選 TPS259472LRPWR；ILIM、dV/dt 與系統 SOA 未凍結 |
| `P3V3_PRE_SENSE` | 約 3.325 V / 5.010 A（估算） | 約 3.335 V / 7.010 A、100 µs | 假設 feedback 在 shunt 後；不是已量測能力 |
| `P3V3_NVME` | 3.3 V；SSD 5 A + local 10 mA allowance | SSD 7 A + local 10 mA、100 µs | 只有 Power Gate 通過後才可宣稱支援指定 SSD |
| `P3V3_AUX` | telemetry 與 I²C pull-up | 低電流 | 由 `P3V3_NVME` 經 FB1 派生，不是 PCIe auxiliary power |

`P3V3_AUX` 名稱中的 AUX 只表示本板輔助量測 rail，不表示 PCIe 3.3 Vaux。Capture 頁面必須加入文字註記避免誤解。

## Telemetry 與 Debug 介面

### 量測鏈

- INA238AIDGSR 以 Kelvin 線直接跨接 RSH1 的 sense terminals；force copper 不得共用 sense via。
- TMP1075DR 放在 M.2 控制器端附近，但不侵犯 connector、SSD 或 screw keepout。
- U3、U4 使用 `P3V3_AUX`，I²C pull-up 也只接 `P3V3_AUX`。
- 因 `P3V3_AUX` 從 shunt 後派生，RSH1 與 INA238 量到的是 SSD branch 加本板 local
  telemetry／indicator current；目前以 10 mA allowance 計算，須在 freeze 前換成 worst-case sum。
- 位址 strap、ALERT 使用方式與 decoupling 依各正式 datasheet 完成後凍結。

### J3 固定邏輯 pinout

J3 是本設計自行定義的 1×4 header，並非 PCIe 或 M.2 標準 Pin：

| J3 Pin | Net | 方向 | 使用規則 |
|---:|---|---|---|
| 1 | `GND` | reference | 外部工具 ground |
| 2 | `I2C_SCL` | bidirectional/open-drain | 外部工具為 master；不得超過 rail |
| 3 | `I2C_SDA` | bidirectional/open-drain | 外部工具為 master；不得超過 rail |
| 4 | `P3V3_SENSE_OUT` | output sense only | 經 U5 reverse-current blocker 與 RISO1 short-current limiter；禁止向本板供電 |

J3 Pin 4 不得標示為 `3V3 POWER`。絲印使用 `3V3_SENSE` 與 `NO BACKFEED`。U5 暫選 production-status ADP198ACPZ-R7，EN 隨內部 `P3V3_AUX` 啟用，利用原廠 reverse-current blocking 防止外部輸出回供；RISO1 再限制誤短路電流。外部工具仍必須 high impedance。U5 reverse-drive leakage、RISO1 阻值、sense 誤差與未上電 injection 測試完成前，此安全需求維持 `Planned`。

## 未連接與保留訊號策略

- J1、J2 所有 ground/power Pin 必須在 Pin Gate 後逐 Pin 展開，不得只保留 aggregate placeholder。
- M.2 Key M 的 reserved、vendor-specific、DAS/DSS、CONFIG 與 no-connect 定義須依 controlled specification 建立明確 `NC`／strap／net；不得留成未說明的懸空 Pin。
- 所有 intentional no-connect 在 Capture 加 `No Connect` marker，並在 ERC checklist 記錄理由與來源。
- M.2 其他形態或 SATA 功能不在 Rev A 範圍，不因 connector 有 Pin 而自行接線。

## 介面變更控制

任何下列變更都視為 Gate 重新開啟：lane 交換、P/N 交換、AC coupling 所有權改變、sideband pull-up 新增、J1/J2 Pin number 修改、M.2 connector part number 修改、power rail 越過 shunt 的負載移動。變更必須同步更新：

1. `pcie_m2_pin_mapping.md`
2. `schematic/connection_matrix.csv`
3. `schematic/symbol_pinmap.csv`
4. `pcb/differential_pairs.csv`
5. `pcb/constraints.csv`
6. ERC／DRC review 記錄與 CHANGELOG

## 主要來源

- PCI-SIG, [PCI Express Card Electromechanical Specification Revision 3.0](https://pcisig.com/PCIExpress/Specs/CEM/CardElectromechanical_3.0)
- NVM Express, [NVMe specifications](https://nvmexpress.org/specifications/)
- NVM Express, [Power Governance webinar](https://nvmexpress.org/wp-content/uploads/NVMe_Power_Governance_Webinar_FINAL.pdf)
- NVIDIA, [Jetson Download Center](https://developer.nvidia.com/embedded/downloads)
- TI, [TPS543620](https://www.ti.com/product/TPS543620), [TPS25947](https://www.ti.com/product/TPS25947), [INA238](https://www.ti.com/product/INA238), [TMP1075](https://www.ti.com/product/TMP1075)
