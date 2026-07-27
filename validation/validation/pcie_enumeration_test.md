# PCIe Enumeration Test

> 目標：驗證功能性 enumeration 與 negotiated link，不宣稱 PCI-SIG compliance。

## Linux

```bash
TEST_START="$(date --iso-8601=seconds)"
journalctl -k -b 0 -o short-iso > <evidence-dir>/kernel-before.txt
lspci -nn
lspci -vv -s <BDF>
sudo nvme list
sudo nvme id-ctrl /dev/nvmeX
journalctl -k -b 0 --since "$TEST_START" -o short-iso > <evidence-dir>/kernel-after.txt
```

`<BDF>`、`/dev/nvmeX` 與 `<evidence-dir>` 必須由 reviewer 逐項確認。流程禁止使用
`dmesg --clear` 或其他清除 host kernel log 的操作。若 host 沒有 persistent
systemd journal，改在測試前後分別保存 `dmesg --time-format iso` 全量 snapshot，
不得清空 ring buffer。

保存：

- Host motherboard、BIOS version、slot、OS/kernel。
- SSD manufacturer、model、firmware、capacity。
- BDF、Vendor／Device ID。
- `LnkCap` 與 `LnkSta` speed／width。
- ASPM 狀態、AER counter、retrain／reset 訊息。

## Windows

- Device Manager：Hardware IDs、driver、event status。
- HWiNFO：PCIe link speed／width。
- CrystalDiskInfo：model、firmware、SMART。
- Event Viewer：WHEA／storage／PCIe warning。

## 判定

- Enumeration：端點出現且在觀察期間沒有重複消失／重現。
- Link width：只有 host slot 與 SSD 都支援 x4 時才以 x4 為 pass 條件。
- Link speed：只有 host、SSD、BIOS 皆允許 Gen3 時才以 Gen3 為 pass 條件。
- x1、x2、Gen1、Gen2 或 link down 均進入 fault tree；不得直接判定為 SI 根因。

## Evidence

- 原始 command output／screenshots。
- Cold boot 與 warm boot 分開命名。
- 任何 BIOS setting 變更寫入 debug log。
- 使用 [test profiles](test_profiles.csv) 的 case ID、trial count 與 evidence prefix。

## 工具來源

- [journalctl manual](https://www.man7.org/linux/man-pages/man1/journalctl.1.html)：
  `-k` 篩選 kernel message、`--since`／`--until` 限定時間範圍。
- [dmesg manual](https://man7.org/linux/man-pages/man1/dmesg.1.html)：
  `--time-format` 可保留有時間標記的 snapshot；本計畫不使用 clear action。
