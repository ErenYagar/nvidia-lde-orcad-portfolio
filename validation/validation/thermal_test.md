# Basic Thermal Test

> 這是工程溫升調查，不是安全、可靠度或產品認證。

## 測點

- Ambient／host inlet。
- TPS543620 package top 與附近 PCB。
- Inductor。
- TPS259472L。
- 5mΩ shunt。
- M.2 connector power-pin 區。
- SSD controller、NAND／PMIC 可接近位置。

## 方法

1. 記錄 board orientation、case、fan、airflow、SSD heatsink、ambient。
2. Idle 穩定後記錄 baseline。
3. 執行已核准 staged workload，同步記錄 power、SMART、TMP1075。
4. 使用細線 thermocouple 為主要定量方法；IR camera 僅在 emissivity 已處理時作交叉檢查。
5. 記錄溫度隨時間曲線，不只記最高單點。
6. 冷卻後檢查是否有 permanent offset、discoloration 或 connector damage。

## 判定

- 每顆元件的 limit 來自其 datasheet junction／case guidance與實際量測方法。
- SSD limit 來自該 SSD 原廠資料；不存在通用假設值。
- Engineering margin 在測試前定義。
- 任何 thermal throttling 都同時比對 SMART、performance、power 和 link log。

## 狀態

所有結果目前為 `Not_Yet_Measured`。

