# 專案報告｜PCIe Gen3 x4 to M.2 NVMe Adapter

**Project type:** Self-directed OrCAD X / Allegro interview portfolio project  
**Release:** Rev K — `Interview_Digital_Complete`  
**Portfolio:** [GitHub Pages bilingual portfolio](https://erenyagar.github.io/nvidia-lde-orcad-portfolio/)  
**Repository:** [ErenYagar/nvidia-lde-orcad-portfolio](https://github.com/ErenYagar/nvidia-lde-orcad-portfolio)

## 一句話說明

這是一張把桌機 PCIe Gen3 x4 插槽轉成 M.2 M-Key 2280 NVMe 介面的六層 low-profile add-in card。專案重點不是只畫出一張漂亮的 3D 圖，而是把規格、電源、原理圖、PCB placement、模擬、機構審查、製造輸出與自動驗證串成可追溯的工程流程。

## 為什麼做這個專案

我的研究背景是 FPGA、Verilog RTL、AES-GCM 與板級驗證；這個專案把數位硬體能力延伸到完整 PCB system design。它用一個面試官容易理解的產品問題，展示我能從 system requirement 開始，完成電氣架構、元件選型、Cadence flow、power integrity 思考、mechanical review 與 release discipline。

## 系統架構

```text
PCIe CEM slot
   ├─ PCIe Gen3 x4 TX/RX + REFCLK + sideband
   └─ 12 V slot power
        ↓
   TPS25947-family eFuse
        ↓
   P12V_PROTECTED
        ↓
   TPS543620 6 A synchronous buck
        ↓
   P3V3_PRE_SENSE → 5 mΩ Kelvin shunt → P3V3_NVME
        ↓
   M.2 M-Key 2280 NVMe connector
```

Telemetry uses INA238 current/voltage monitoring, TMP1075 temperature sensing and an isolated 1×4 I²C header. The power design targets 3.3 V / 5 A normal operation and retains a 7 A / 100 µs engineering pulse profile for transient analysis.

## 我實際完成的工程工作

1. **Requirements and architecture** — defined the PCIe-to-NVMe function, six-layer stack intent, power path, supported-SSD policy and risk gates.
2. **Capture** — created the hierarchy, symbols, pin map, connection matrix, footprint assignments, BOM and ERC evidence.
3. **Allegro PCB** — built the native board database, board outline, placement, layers, differential-pair groups, power zones, keepouts, test points and mechanical references.
4. **PSpice** — prepared startup, inrush, steady-state, load transient, line transient, PGOOD and recovery profiles; preserved the recovery limitation instead of fabricating a passing waveform.
5. **3DX / STEP** — mapped component bodies, generated top/bottom/side/isometric evidence, performed preliminary collision review and retained STEP round-trip evidence.
6. **Manufacturing package** — generated Gerber artwork, NC Drill, IPC-2581-C, preliminary BOM, P&P, assembly drawing and artifact hashes.
7. **Automation** — added Python CSV/BOM/pin/net/3D/delivery validators and negative fixtures so invalid data fails visibly.

## 可量化成果

| 項目 | 結果 |
|---|---|
| PCB baseline | 6 layers, 120 × 64 mm preliminary envelope |
| High-speed interface | PCIe Gen3 x4, 8 data differential pairs + REFCLK |
| Power architecture | 12 V eFuse → 6 A buck → 3.3 V NVMe |
| Native board checks | DRC = 0, unconnected = 0, active rats = 0 in the recorded Rev K closure evidence |
| 3D evidence | Native 3DX screenshots, mapped models, STEP export and re-import record |
| Automated validation | CSV, BOM, pin, net, supported-SSD and delivery checks |

## 狀態與工程邊界

這份作品集的正確定位是 **Interview Digital Complete**，不是 fabrication release。以下限制已刻意保留：

- 尚未宣稱 PCIe compliance、universal SSD support、chassis compatibility 或 bench qualification。
- JLCPCB 當期 controlled-impedance stack-up 與實際線寬／間距／via geometry 仍需投板前確認。
- PSpice recovery limitation 已保留在 profile 與 log 中，沒有把失敗波形改寫成 Pass。
- 部分機構模型是 preliminary envelope；exact host chassis、standoff、bracket 與 SSD fit 仍需實體資料和量測。
- ODB++ 不受目前安裝工具支援，因此以 IPC-2581-C 作為可用的 intelligent CAM exchange，不冒充 ODB++ 已完成。

## 面試時怎麼說（30 秒）

> 這是一個我自己完成的 OrCAD X／Allegro PCIe Gen3 x4 到 M.2 NVMe 轉接板作品。我從需求與電源架構開始，建立 Capture 原理圖、Allegro 六層板 placement、PSpice power profiles，再用 3DX Canvas 與 STEP 做機構審查，最後輸出 Gerber、NC Drill、IPC-2581 與可重現的 Python validators。我的重點不是宣稱它已經量產，而是把每個工程決策、限制與證據都留下來，讓設計可以被審查、重現與繼續收斂。

## 直接查看證據

- [Visual portfolio page](portfolio/index.html)
- [Native 3DX evidence](evidence/stage3/3dx_native_revk/)
- [Manufacturing and CAM package](manufacturing/stage3_final_revk/)
- [Power budget](docs/power_budget.md)
- [Validation status](VALIDATION_STATUS.md)
- [Bilingual portfolio page](https://erenyagar.github.io/nvidia-lde-orcad-portfolio/)
