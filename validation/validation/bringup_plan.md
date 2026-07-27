# Bring-up Plan

> 狀態：`Planned / Not_Yet_Measured`。任何實際值必須連同儀器、探棒、SSD、host、日期與原始證據記錄。

## 安全條件

- 不在主機通電時插拔 PCIe card 或 M.2 SSD。
- 第一次上電不得直接由未知主機板供電；先使用經 review 的 current-limited bench injection 方法。
- Bench supply 注入點不得反向回灌 PCIe edge；若無法證明隔離，停止測試。
- 示波器接地不可造成 12V、3.3V 或 host chassis 短路。
- 所有 pass/fail limit 必須在測試前由 requirements、datasheet 或 PSpice 結果凍結。

## Phase 0 — 文件與目視

1. 核對 board revision、BOM、assembly drawing、ECO。
2. 目視 QFN、M.2 connector、shunt、電感、極性與 gold finger。
3. 量測未裝 SSD 時 `P12V_SLOT`、`P12V_PROTECTED`、`P3V3_NVME` 對 GND 阻抗；記錄時間相關變化與雙向讀值。
4. 確認沒有明顯短路、錯件或 mechanical interference。

## Phase 1 — 無 SSD 受控上電

5. 設定 bench supply 電壓與 current limit；兩者必須來自已核准測試卡，不能現場猜測。
6. 上電並觀察 supply current、`P12V_PROTECTED`、`P3V3_NVME`、`PGOOD_EFUSE`、`PGOOD_3V3`。
7. 確認 3.3V startup、steady-state、no-load current 與 ripple。
8. 測試 shutdown、re-start 與 protection latch reset；任何異常立即斷電。
9. 以外部 I²C master 讀 INA238／TMP1075；確認 Header 不會 back-power。

## Phase 2 — 安裝 SSD

10. 斷電、放電後安裝已核准且資料可清除的 NVMe SSD。
11. 重複 power-to-ground sanity check。
12. 捕捉 SSD 啟動電流、3.3V droop、PGOOD、eFuse/buck response。
13. 確認沒有 nuisance trip、hiccup、過熱或異常聲音。

## Phase 3 — 主機功能

14. 主機完全關機後安裝 card，確認 bracket 與 slot seating。
15. 開機後依 `pcie_enumeration_test.md` 保存 kernel-log before／after，再收集
    `lspci`、`lspci -vv`、`nvme list`、`nvme id-ctrl`；不得清除 host kernel log。
16. 記錄 negotiated speed、width、BDF、AER／link reset 訊息。
17. 先做非破壞讀取，再對專用 test namespace 做短時間 verified read/write。

## Phase 4 — 壓力、熱與相容性

18. 依 `storage_stress_test.md` 與 `test_profiles.csv` 執行 staged workload；先
    `--parse-only`，read case保留 `--readonly`，同步記錄電壓、電流、溫度、SMART 與 kernel log。
19. 依 `BOOT-COLD-10`／`BOOT-WARM-10` 各執行十次，兩種 evidence分開保存。
20. 使用第二顆已核准 SSD 重複 power、enumeration、speed、width 與短測。
21. 每項失敗建立 debug log；只有在證據支持時才提出 ECO。

## Stop Conditions

- 可見煙霧、異味、異常聲音、快速升溫。
- Bench supply 進入未預期 current limit。
- 3.3V 超出已核准 operating window。
- PGOOD、buck switching 或 input protection 出現未解釋 oscillation。
- 主機反覆 reset、PCIe fatal AER、SSD 消失或資料錯誤。

## 完成定義

- 測試矩陣每一列有 Pass、Fail、Blocked 或 Not_Run 結果及證據。
- 實測與 Simulated／Estimated 值分欄比較。
- 所有 failure 有 reproducibility、diagnostic evidence、disposition 與 regression plan。
