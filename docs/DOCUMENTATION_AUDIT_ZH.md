# 文件審查報告（繁體中文）

English version：[`DOCUMENTATION_AUDIT_EN.md`](DOCUMENTATION_AUDIT_EN.md)｜目前主審查檔：[`DOCUMENTATION_AUDIT.md`](DOCUMENTATION_AUDIT.md)

審查範圍：public repository `ErenYagar/nvidia-lde-orcad-portfolio`。方法包含檔案盤點、路徑檢查、evidence/status review、claim scan 與 Python validators。

## 1. Repository 定位

這是一個面試導向的 PCB system-design case study，主題是六層 PCIe Gen3 x4 add-in card 到 M.2 M-Key 2280 NVMe 的 physical interposer。它不做 PCIe protocol conversion、retimer、switch 或 firmware。重點是把 system intent、pin/net interface、power assumptions、3DX/STEP、CAM 與自動化檢查連成一條可追溯流程。

目前 public baseline 是 Rev K / RevK evidence，狀態為 `Interview_Digital_Complete_Not_For_Fabrication`。

## 2. 已有的強證據

| 領域 | 證據 | 審查結論 |
|---|---|---|
| System intent | [`docs/interface_definition.md`](interface_definition.md)、[`docs/system_block_diagram.md`](system_block_diagram.md) | Host、edge、M.2、SSD、power、telemetry 邊界清楚 |
| Architecture | [`docs/architecture_tradeoff.md`](architecture_tradeoff.md) | Options、選擇理由與 exit conditions 有記錄 |
| Capture | [`schematic/connection_matrix.csv`](../schematic/connection_matrix.csv)、ERC report | Machine-readable source 與 native report 有保存 |
| PSpice | [`pspice/stage2/profile_results.csv`](../pspice/stage2/profile_results.csv) | 3.109 V recovery failure 沒有被隱藏 |
| PCB | [`evidence/stage3/stage3_delivery_gate.md`](../evidence/stage3/stage3_delivery_gate.md) | Native DRC/connectivity/shape closure 與九組 pair objects 有證據 |
| 3D/MCAD | [`evidence/stage3/3d_status.md`](../evidence/stage3/3d_status.md) | Native 3DX 與 AP242/mm STEP round-trip 有 hash 綁定 |
| Manufacturing | [`manufacturing/stage3_final_revk/README.md`](../manufacturing/stage3_final_revk/README.md) | Gerber、NC Drill、IPC-2581、BOM/P&P 已輸出但非 fab release |
| Automation | [`scripts/`](../scripts/) | Schema、negative fixtures 與 command-line checks 可重複 |

## 3. 真正未關閉的工程證據

1. PCIe CEM/M.2 controlled specifications 未納入 public package，J1/J2 physical pins 仍為 `Pending_Human_Verification`。
2. JLCPCB 當期 stack-up、impedance width/gap/via 尚未 freeze。
3. Exact host chassis、bracket、standoff、cable、J2 與 SSD models 不完整，因此 collision 只能 preliminary 或 blocked。
4. 官方 buck model 的 recovery 最低 3.109 V，低於 3.135 V screen；27-case sweep runtime-limited。
5. TPS25947x eFuse isolated run 未達有效 output startup。
6. 沒有 physical board、oscilloscope、Bode/impedance、thermal camera、NVMe enumeration 或 Gen3 x4 bench results。
7. IPC-356 為空檔，ODB++ 受安裝工具限制；IPC-2581-C 作為可用替代交換格式。

## 4. 有意不加入的設計

- 沒有自行添加 lane AC capacitors、termination、CMC、ESD，因 transmitter ownership 尚未由 controlled specification 確認。
- 沒有 protocol converter、retimer、switch 或 firmware，因本案是 passive adapter。
- 沒有 universal-SSD、chassis compatibility 或 bench qualification 宣稱。
- 3DX render 只作 placement/hand-off evidence，不代替 exact fit 或 physical test。

## 5. 主要 overclaim 風險

`PCIe compliance`、`fabrication-ready`、`universal SSD`、`chassis compatibility`、`bench qualification`、`exact fit`、`SI sign-off` 與 `thermal validation` 必須在所有對外材料中加上「未宣稱／尚未完成」的限定。Claim matrix 已將這些限制與 evidence 綁定。

## 6. 審查後的文件標準

- 讀者兩次點擊內能知道板子做什麼、不做什麼、證據在哪裡。
- 每個量化 claim 都有 status 或 evidence path。
- Failure、runtime limit、missing model 與 fabrication blocker 保持可見。
- 原始 Cadence binary、PCB、PSpice、CAM 與圖片未被改寫。
