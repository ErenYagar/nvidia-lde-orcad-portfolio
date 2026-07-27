# Storage Stress Test

> 狀態：`Planned`。僅能使用可清除的測試 SSD／namespace；禁止對使用者資料執行破壞性 workload。

## 前置條件

- Power、enumeration、link speed／width、NVMe identify 與短時間讀寫已通過。
- 測試容量、時間、I/O pattern、queue depth、block size、驗證模式在執行前凍結。
- 同步 log：P3V3_NVME、INA238 current、TMP1075、SSD SMART、ambient、`dmesg`。

## Profile freeze

所有 case 的 runtime、block size、queue depth、verify、trial count、stop conditions 與
evidence prefix 定義於 [test_profiles.csv](test_profiles.csv)。這些數字是預先凍結的
`Engineering_Assumption` 測試設定，不是 NVMe／PCIe 規格要求，也不是已執行結果。

每次執行前必須產生 reviewer-approved `.fio` job file，且至少記錄：

- exact host、BDF、controller、namespace、SSD model／capacity／firmware；
- `lsblk`／mount 狀態、serial-to-device mapping、資料可清除批准；
- job file SHA-256、fio version、reviewer、日期與 evidence directory；
- power／thermal limits與 emergency stop operator。

## Staged Workload

1. Sequential read。
2. Sequential verified write to test namespace。
3. Random read。
4. Mixed read/write。
5. Sustained workload until預定時間或 stop condition。

先只解析 job file，不進行 I/O：

```bash
fio --parse-only <reviewed-read-job.fio>
```

read-only case 執行時額外保留 fio safety guard：

```bash
fio --readonly --output=<evidence-file.json> --output-format=json <reviewed-read-job.fio>
```

`--parse-only` 只驗證 option parsing，不證明 target 安全；`--readonly` 只允許
read-only profile。Repository **刻意不提供可直接複製執行的 write／trim command**。
`FIO-WRITE-VERIFY-SHORT` 與 `FIO-MIXED-STRESS` 只有在 exact disposable namespace、
unmounted state、backup／data-loss approval、job hash與 second-person review全部完成後，
才由 lab procedure 產生一次性執行命令。不得在 system disk、使用者資料或未核准
namespace 上移除 `--readonly`。

## Stop Conditions

- I/O verification error、namespace 消失、controller reset。
- PCIe AER／WHEA fatal error。
- P3V3_NVME 超出核准範圍或 protection 動作。
- 元件溫度接近核准 derated limit。
- SMART critical warning 或 host stability 受影響。

## Evidence／判定

- 不以 throughput 數字作為主要設計成功宣稱。
- Pass 需要零 verification error、零未解釋 reset、電源與溫度在核准範圍。
- 降速必須同時檢查 SSD thermal、power、host、workload cache 與 PCIe link，不能直接歸因 PCB。

## 工具來源

- [fio official documentation](https://fio.readthedocs.io/en/master/fio_doc.html)：
  `--parse-only` 不啟動 I/O；`--readonly` 阻止 write／trim workload。這兩項是額外
  safety guard，不能替代 exact-target 人工核准。
