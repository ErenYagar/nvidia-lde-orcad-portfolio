# PCIe CEM x4 ↔ M.2 M-Key Pin Mapping 工作表

## 使用規則

這份工作表刻意不列出尚未查核的實體 Pin number。`PENDING_*` 是唯一允許的 placeholder，不是實體 Pin 名稱。只有完成下列證據鏈後，才能把單一列改成 `Confirmed_Official`：

1. PCI-SIG CEM 3.0 controlled copy 的章節、表格與 revision。
2. M.2 controlled specification 的章節、表格與 revision。
3. 第二份原廠公開 reference design 的 page／net 交叉檢查。
4. Reviewer、日期、差異處置均有記錄。

公開產品頁只能證明文件存在，不能替代 controlled specification 中的 pin table。

## 公開 cross-check snapshot 與 revision Gate

NVIDIA SP-10900-001 v1.2 的 Table 2-8／2-13 提供下列公開原廠候選對照。這些資料只用來
檢查邏輯方向與找 revision 差異；未取得適用的 CEM／M.2 controlled pin table 前，不寫回
`connection_matrix.csv` 的 physical Pin。

| 功能 | CEM candidate pair／Pin | M.2 candidate pair／Pin | 狀態 |
|---|---|---|---|
| Host TX lane 0 → SSD RX lane 0 | B14／B15 | 43／41 | `Pending_Human_Verification` |
| Host TX lane 1 → SSD RX lane 1 | B19／B20 | 31／29 | `Pending_Human_Verification` |
| Host TX lane 2 → SSD RX lane 2 | B23／B24 | 19／17 | `Pending_Human_Verification` |
| Host TX lane 3 → SSD RX lane 3 | B27／B28 | 7／5 | `Pending_Human_Verification` |
| SSD TX lane 0 → Host RX lane 0 | A16／A17 | 49／47 | `Pending_Human_Verification` |
| SSD TX lane 1 → Host RX lane 1 | A21／A22 | 37／35 | `Pending_Human_Verification` |
| SSD TX lane 2 → Host RX lane 2 | A25／A26 | 25／23 | `Pending_Human_Verification` |
| SSD TX lane 3 → Host RX lane 3 | A29／A30 | 13／11 | `Pending_Human_Verification` |
| REFCLK pair | A13／A14 | 55／53 | `Pending_Human_Verification` |
| PERST# | A11 | 50 | `Pending_Human_Verification` |
| PEWAKE# | B11 | 54 | `Pending_Human_Verification` |
| CLKREQ# in NVIDIA 2024 design | B12 | 52 | `Pending_Human_Verification` |

目前 governing baseline 仍是 CEM 3.0。Renesas R70WP0004EU0102 Rev.1.02 Table 1 p.9
明確把 B12 列為 CEM 3.0 的 `RSVD`，並以另一個 footnote 說明 CEM 4.0 的 B12 才是
`CLKREQ#`。因此在下列任一條件完成前，禁止將 J1 B12 指派為
`PCIE_CLKREQ_N`：

1. 正式將 governing CEM revision 升級至 4.0 或以上，並保留受控 revision／ECN；
2. 重新完成 slot、sideband、mechanical 與 power 的整套 revision impact review；
3. reviewer 簽核 J1 B12 ↔ J2 pin 52 的 direction 與 pull ownership。

另有 M.2 pin 32 公開資料差異：PCI-SIG interoperability warning 的候選表把它列入
GND，而 NVIDIA v1.2 Table 2-13 將 30／32／34／36 列為 N/C。由於警告的 direct URL
在 2026-07-23 回傳 404，且 governing controlled M.2 revision／ECN 尚未保存，pin 32
維持未解析，不採用任何一方單獨關閉 Gate。

## 邏輯 Lane 對照

命名以 host／slot 視角為準，因此 `PCIE_TX0_P` 是 host transmit，必須到 SSD receive；`PCIE_RX0_P` 是 host receive，必須來自 SSD transmit。

| Lane | J1 邏輯功能 | Net | J2 邏輯功能 | J1 Pin | J2 Pin | 狀態 |
|---:|---|---|---|---|---|---|
| 0 | Host TX P | `PCIE_TX0_P` | SSD RX P | `PENDING_J1_PCIE_TX0_P` | `PENDING_J2_PCIE_RX0_P` | `Pending_Human_Verification` |
| 0 | Host TX N | `PCIE_TX0_N` | SSD RX N | `PENDING_J1_PCIE_TX0_N` | `PENDING_J2_PCIE_RX0_N` | `Pending_Human_Verification` |
| 0 | Host RX P | `PCIE_RX0_P` | SSD TX P | `PENDING_J1_PCIE_RX0_P` | `PENDING_J2_PCIE_TX0_P` | `Pending_Human_Verification` |
| 0 | Host RX N | `PCIE_RX0_N` | SSD TX N | `PENDING_J1_PCIE_RX0_N` | `PENDING_J2_PCIE_TX0_N` | `Pending_Human_Verification` |
| 1 | Host TX P | `PCIE_TX1_P` | SSD RX P | `PENDING_J1_PCIE_TX1_P` | `PENDING_J2_PCIE_RX1_P` | `Pending_Human_Verification` |
| 1 | Host TX N | `PCIE_TX1_N` | SSD RX N | `PENDING_J1_PCIE_TX1_N` | `PENDING_J2_PCIE_RX1_N` | `Pending_Human_Verification` |
| 1 | Host RX P | `PCIE_RX1_P` | SSD TX P | `PENDING_J1_PCIE_RX1_P` | `PENDING_J2_PCIE_TX1_P` | `Pending_Human_Verification` |
| 1 | Host RX N | `PCIE_RX1_N` | SSD TX N | `PENDING_J1_PCIE_RX1_N` | `PENDING_J2_PCIE_TX1_N` | `Pending_Human_Verification` |
| 2 | Host TX P | `PCIE_TX2_P` | SSD RX P | `PENDING_J1_PCIE_TX2_P` | `PENDING_J2_PCIE_RX2_P` | `Pending_Human_Verification` |
| 2 | Host TX N | `PCIE_TX2_N` | SSD RX N | `PENDING_J1_PCIE_TX2_N` | `PENDING_J2_PCIE_RX2_N` | `Pending_Human_Verification` |
| 2 | Host RX P | `PCIE_RX2_P` | SSD TX P | `PENDING_J1_PCIE_RX2_P` | `PENDING_J2_PCIE_TX2_P` | `Pending_Human_Verification` |
| 2 | Host RX N | `PCIE_RX2_N` | SSD TX N | `PENDING_J1_PCIE_RX2_N` | `PENDING_J2_PCIE_TX2_N` | `Pending_Human_Verification` |
| 3 | Host TX P | `PCIE_TX3_P` | SSD RX P | `PENDING_J1_PCIE_TX3_P` | `PENDING_J2_PCIE_RX3_P` | `Pending_Human_Verification` |
| 3 | Host TX N | `PCIE_TX3_N` | SSD RX N | `PENDING_J1_PCIE_TX3_N` | `PENDING_J2_PCIE_RX3_N` | `Pending_Human_Verification` |
| 3 | Host RX P | `PCIE_RX3_P` | SSD TX P | `PENDING_J1_PCIE_RX3_P` | `PENDING_J2_PCIE_TX3_P` | `Pending_Human_Verification` |
| 3 | Host RX N | `PCIE_RX3_N` | SSD TX N | `PENDING_J1_PCIE_RX3_N` | `PENDING_J2_PCIE_TX3_N` | `Pending_Human_Verification` |

## Clock、Sideband、Presence

| J1 邏輯功能 | Net | J2／本板功能 | J1 Pin | J2 Pin | Pull／終端所有權 | 狀態 |
|---|---|---|---|---|---|---|
| REFCLK P | `PCIE_REFCLK_P` | SSD REFCLK P | `PENDING_J1_REFCLK_P` | `PENDING_J2_REFCLK_P` | 依 governing spec；本板不預加 | `Pending_Human_Verification` |
| REFCLK N | `PCIE_REFCLK_N` | SSD REFCLK N | `PENDING_J1_REFCLK_N` | `PENDING_J2_REFCLK_N` | 依 governing spec；本板不預加 | `Pending_Human_Verification` |
| PERST# | `PCIE_PERST_N` | SSD reset | `PENDING_J1_PERST_N` | `PENDING_J2_PERST_N` | Host/platform | `Pending_Human_Verification` |
| CLKREQ# | `PCIE_CLKREQ_N` | SSD clock request | `PENDING_J1_CLKREQ_N` | `PENDING_J2_CLKREQ_N` | Platform；本板不預加 pull-up | `Pending_Human_Verification` |
| PEWAKE# | `PCIE_PEWAKE_N` | SSD wake request | `PENDING_J1_PEWAKE_N` | `PENDING_J2_PEWAKE_N` | Platform；本板不預加 pull-up | `Pending_Human_Verification` |
| PRSNT# endpoint | `PCIE_PRSNT_N` | J1 edge presence loop | `PENDING_J1_PRSNT_A` | 不適用 | 依 CEM | `Pending_Human_Verification` |
| PRSNT# return | `PCIE_PRSNT_N` | J1 edge presence loop | `PENDING_J1_PRSNT_B` | 不適用 | 依 CEM | `Pending_Human_Verification` |

## 電源、Ground 與 M.2 Configuration

| 類別 | J1 | J2 | Net／處置 | 狀態 |
|---|---|---|---|---|
| 12 V input | `PENDING_J1_P12V_PIN_SET` | 不適用 | `P12V_SLOT` → eFuse | `Pending_Human_Verification` |
| 3.3 V SSD | 不適用 | `PENDING_J2_P3V3_PIN_SET` | `P3V3_NVME`；Pin Gate 後逐 Pin 展開 | `Pending_Human_Verification` |
| Ground | `PENDING_J1_GND_PIN_SET` | `PENDING_J2_GND_PIN_SET` | `GND`；Pin Gate 後逐 Pin 展開 | `Pending_Human_Verification` |
| M.2 CONFIG／strap | 不適用 | `PENDING_J2_CONFIG_PIN_SET` | 依 M-Key NVMe host 定義逐 Pin 決定 strap 或 NC | `Pending_Human_Verification` |
| Reserved／vendor-specific | 不適用 | `PENDING_J2_RESERVED_PIN_SET` | 依 controlled spec 明確標 NC；禁止自行使用 | `Pending_Human_Verification` |
| PCIe 3.3 V／3.3 Vaux | `PENDING_J1_UNUSED_POWER_PIN_SET` | 不直接相連 | Rev A 電源架構未使用；依 CEM 明確處理 | `Pending_Human_Verification` |

`PENDING_*_PIN_SET` 必須在正式 Capture 建圖前展開為一列一個 physical Pin；它不能直接成為 OrCAD symbol Pin number。

## AC Coupling 與 Polarity 決策

- J1 host TX → J2 SSD RX：預期 AC coupling 由 host transmitter channel 負責；本板不放置額外 capacitor。仍須以 CEM/Base/M.2 controlled document 確認。
- J2 SSD TX → J1 host RX：預期 AC coupling 由 SSD transmitter 端負責；本板不放置額外 capacitor。仍須以 M.2/PCIe controlled document 確認。
- REFCLK 不套用 data lane 的 AC coupling 假設。
- 若第二來源顯示任何 lane 或 polarity 差異，狀態維持 pending，建立 issue，不採多數決。

## Pin Freeze 簽核表

| 檢查項 | 證據欄位 | Owner | Reviewer | 狀態 |
|---|---|---|---|---|
| J1 x4 lane Pin 與 polarity | CEM revision／table／page | Board designer | Independent reviewer | `Pending_Human_Verification` |
| J2 x4 lane Pin 與 polarity | M.2 revision／table／page | Board designer | Independent reviewer | `Pending_Human_Verification` |
| TX/RX 方向 | 兩份 controlled spec + reference design | Board designer | Independent reviewer | `Pending_Human_Verification` |
| REFCLK | Pin、polarity、電氣型態 | Board designer | Independent reviewer | `Pending_Human_Verification` |
| PERST#/CLKREQ#/PEWAKE# | Pin、direction、pull ownership | Board designer | Independent reviewer | `Pending_Human_Verification` |
| PRSNT | CEM presence loop | Board designer | Independent reviewer | `Pending_Human_Verification` |
| J1 power/GND | 全部 Pin、slot power、inrush | Power designer | Independent reviewer | `Pending_Human_Verification` |
| J2 3.3 V/GND/CONFIG/NC | 全部 Pin 與處置 | Board designer | Independent reviewer | `Pending_Human_Verification` |
| Connector drawing | MDT420M01501 drawing revision | Mechanical owner | PCB reviewer | `Pending_Human_Verification` |

## 可追溯來源

- PCI-SIG, [CEM Revision 3.0 landing page](https://pcisig.com/PCIExpress/Specs/CEM/CardElectromechanical_3.0)
- PCI-SIG, [M.2 Specification Revision 5.1 landing page](https://pcisig.com/PCIExpress/Spec/M.2/_5.1)（受控 pin table 尚未保存）
- NVIDIA, [Jetson AGX Orin Developer Kit Carrier Board Specification v1.2](https://developer.nvidia.com/assets/embedded/secure/jetson/agx_orin/jetson_agx_orin_devkit_carrier_board_specification_sp)（僅供公開 reference design 交叉檢查）
- Renesas, [R70WP0004EU0102 Rev.1.02](https://www.renesas.com/en/document/whp/linux-phc-infrastructure-5g)（CEM 3.0／4.0 B12 revision cross-check）
- Amphenol, [MDT420M01501 product page](https://www.amphenol-cs.com/product/mdt420m01501.html)
