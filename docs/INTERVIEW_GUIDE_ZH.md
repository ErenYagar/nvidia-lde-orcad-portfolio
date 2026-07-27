# 面試指南（繁體中文）

English version：[`INTERVIEW_GUIDE.md`](INTERVIEW_GUIDE.md)

## 30 秒說法

我設計一張六層 PCIe Gen3 x4 add-in card，將 host PCIe slot 實體連到 M.2 M-Key 2280 NVMe SSD。它是 passive interposer，不是 protocol converter。專題涵蓋 Capture 介面、12 V 保護與 buck power、PSpice、Allegro placement/constraints、3DX/STEP、CAM 與 Python negative tests。現況是 `Interview_Digital_Complete_Not_For_Fabrication`，我能清楚說明哪些已關閉、哪些仍需要受控規格或硬體量測。

## 2 分鐘說法

1. 先展示 [雙語作品集](../portfolio/index.html)，說明 host、board、SSD 的功能邊界。
2. 開啟 [system block diagram](system_block_diagram.md)，解釋 J1→J2 訊號直通與 eFuse/buck/shunt 電源鏈。
3. 開啟 [stage3 gate](../evidence/stage3/stage3_delivery_gate.md)，說明 DRC/connectivity/shape closure 與尚未 freeze 的 impedance/pin gates。
4. 展示 [native 3DX view](../evidence/stage3/3dx_native_revk/revk_top_isometric_detailed_with_ui.png) 與 [STEP status](../evidence/stage3/3d_status.md)。

## 5～10 分鐘說法

加入 Architecture B trade-off、Capture connection matrix、PSpice profile table、nine differential pairs、CAM status，主動說明 3.109 V recovery failure、eFuse validation gap、CEM/M.2 source gate 與 JLCPCB stack-up blocker。最後以 [Rev L plan](../PROJECT_REPORT.md#12-rev-l--next-revision-plan) 結尾。

## 技術問答

### 1. 這張板實際解決什麼問題？

它提供 host PCIe Gen3 x4 到 M.2 M-Key 2280 NVMe 的 physical connection、local power protection/conversion 與 optional telemetry。它不轉換 PCIe protocol。參考 [`docs/interface_definition.md`](interface_definition.md)。

### 2. 為什麼沒有 PCIe switch 或 retimer？

因為需求是 passive adapter。加入 switch/retimer 會改變 power、firmware、SI 與 compliance scope。

### 3. 為什麼選 12 V + buck？

我在 [`docs/architecture_tradeoff.md`](architecture_tradeoff.md) 比較 slot 3.3 V 與 local conversion；Architecture B 能展示 protection、conversion、sensing 與 hot-loop review。

### 4. 正常負載是多少？

3.3 V / 5 A 是 engineering normal target；7 A / 100 µs 是 transient study，不是通用 SSD rating。

### 5. 為什麼 6 A buck 要分析 7 A？

7 A 只是一個短暫電容／控制迴路事件，不是 7 A continuous claim；但模型觀察到 8.656 A peak inductor current，且 recovery 失敗，所以尚未關閉。

### 6. PSpice 失敗在哪裡？

官方 buck model 的 recovery minimum 是 3.109 V，低於 3.135 V lower screen；PGOOD 仍保持 high。結果保留為 `Fail_Recovery_Undershoot_5pct`。

### 7. 為什麼 capacitor sweep 沒有結案？

27 個 COUT/ESR/CFF cases 因 runtime limit 中止；132 µF candidate 只跑到約 0.255 ms，不能推導 pass。

### 8. eFuse 做什麼？

控制 slot 12 V 到 buck 的 current limit、soft-start 與 fault response；isolated model run 沒有有效 output startup，因此 inrush/latch-off 尚未驗證。

### 9. 為什麼使用 5 mΩ Kelvin shunt？

它能在低壓降下提供 INA238 differential sense；5 A 時 nominal drop 約 25 mV，但 calibration 與 layout parasitic 需 bench correlation。

### 10. INA238/TMP1075 的用途？

INA238 量測 SSD branch current/voltage，TMP1075 量測板上溫度；J3 是 target-only I²C header，不能外部回灌供電。

### 11. 為什麼沒有 AC coupling 或 CMC？

在 transmitter ownership 與 governing CEM/M.2 source 確認前，不改變高速 topology，避免自行加入沒有來源的元件。

### 12. DRC=0 證明什麼？

它證明目前 native database 通過報告中的 design-rule/connectivity checks；不證明 SI/PI、impedance、thermal、fit、compliance 或 yield。

### 13. 有幾組 differential pairs？

九組：八組 PCIe data pairs 加一組 REFCLK pair。Width/gap/via/skew 仍等 fabricator stack-up。

### 14. 為什麼 J1/J2 physical pins 還 pending？

受控 CEM/M.2 source 尚未納入 public package；B12/CLKREQ# 與 M.2 pin 32 的版本差異已記錄，沒有猜 pin number。

### 15. 為什麼 stack-up 未 freeze？

Controlled impedance 必須使用當期 JLCPCB dielectric/copper stack-up 與 calculator；填造一組 width/gap 會是假精確。

### 16. 3DX/STEP 證明什麼？

證明 native board → 3DX → AP242/mm STEP → isolated re-import 的 handoff loop；不證明 exact chassis fit。

### 17. 為什麼碰撞案例有 blocked？

Collision Pass 需要 exact model、confirmed transform 與 sourced clearance rule；保守 envelope 只能是 preliminary。

### 18. 有哪些製造檔？

Gerber、NC Drill、IPC-2581-C、BOM、preliminary P&P、assembly evidence 與 STEP；IPC-356 空檔排除，ODB++ 不支援，因此不是 direct-fab release。

### 19. 自動化做了什麼？

Python 檢查 CSV schema、BOM、duplicate pins、net naming、evidence contract 與 negative fixtures；不取代 Cadence native review。

### 20. 如何避免 failure 被覆蓋？

每個重要 run 保存 input/output、status、limitation 與 hash；3.109 V failure 與 runtime-limited sweep 都保留在 report/matrix。

### 21. 下板前要做什麼？

Freeze CEM/M.2 pins、導入 JLCPCB stack-up、關閉 power recovery/eFuse、補 exact models，再做 DFM、CAM 與 board-house review。

### 22. Bench bring-up 順序？

限流上電且不插 SSD → 檢查 rails/inrush/PGOOD → 插入 reference SSD → enumeration/link width/speed/NVMe identify → stress/thermal。這些結果目前未宣稱。

### 23. 為什麼與 LDE 工作相關？

因為它展示從 interface ownership、power、library、constraints、MCAD、CAM、automation 到 failure disclosure 的完整 loop。

### 24. 最大風險是什麼？

Missing controlled source data，尤其是 connector physical pin freeze 與 fabricator stack-up；它們可能讓漂亮的 board encode 錯誤 mapping 或 impedance。

### 25. Rev L 要改什麼？

Rev L 是 controlled ECO：pin freeze、stack-up-derived constraints、power recovery/eFuse closure、exact mechanical remapping、DFM/fabrication 與 bring-up，不是單純重新 render。

## 快速證據連結

- [中文技術報告](../PROJECT_REPORT_ZH.md)
- [English technical report](../PROJECT_REPORT_EN.md)
- [中文 claim matrix](CLAIM_EVIDENCE_MATRIX_ZH.md)
- [English claim matrix](CLAIM_EVIDENCE_MATRIX.md)
