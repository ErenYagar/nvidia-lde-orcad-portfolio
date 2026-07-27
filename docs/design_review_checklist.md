# Design Review Checklist

本清單是 release gate，不是工作完成宣告。未勾選項目均為 `Planned`；只有附 evidence path、reviewer 與日期的項目才可勾選。

## SRR — System Requirements Review

- [ ] 系統邊界固定為 PCIe Gen3 x4、單一 M.2 2280 M-Key NVMe。
- [ ] Low-profile、half-length mechanical requirement 已由適用 CEM 文件確認。
- [ ] In-scope／out-of-scope 與不宣稱 PCIe compliance 的限制已簽核。
- [ ] 每個 requirement 具有來源、verification method 與 status。
- [ ] 5 A normal 與 7 A / 100 µs transient 已明示為 design stimulus。
- [ ] 所有實機結果仍為 `Not_Yet_Measured`，除非有原始量測 evidence。

## PDR — Architecture and Component Review

- [ ] Architecture A／B 比較的假設、權重與退出條件已 review。
- [ ] PCIe slot power／inrush boundary 已由 [PCI-SIG CEM 3.0](https://pcisig.com/PCIExpress/Specs/CEM/CardElectromechanical_3.0) 確認。
- [ ] TPS543620 operating point、switching frequency、inductor、Cin、Cout、feedback、soft-start 與 thermal 已計算。
- [ ] TPS25947 exact orderable MPN、latch-off／auto-retry、PG／FLT、current limit、timer 與 slew 已確認。
- [ ] INA238 shunt range、calibration、error budget 與 Kelvin connection 已確認。
- [ ] TMP1075 address、placement 與量測語意已確認。
- [ ] MDT420M01501 與 MDT320M01001 exact drawings／3D files 可追溯。
- [ ] `pcb/3d_model_mapping.csv` 的 critical model hash、datum、transform與 collision evidence通過 `check_3d_models.py`。
- [ ] 每個實裝料具有 lifecycle、datasheet status、footprint status 與 alternative。
- [ ] Top risks 有 owner、mitigation 與 closure evidence。

## Gate 1 — Pin Mapping Freeze

- [ ] PCIe edge 與 M.2 connector 的 orientation／view definition 已鎖定。
- [ ] Lane 0–3 的 TX/RX direction 已以 host 與 device 視角交叉確認。
- [ ] 每組 differential pair 的 P/N polarity 已確認。
- [ ] REFCLK P/N 已確認。
- [ ] PERST#、CLKREQ#、PEWAKE# 的 direction、voltage domain 與 pull-up ownership 已確認。
- [ ] PRSNT pins／lane-width indication 已確認。
- [ ] M-Key pin definition 與 no-connect／reserved pins 已確認。
- [ ] AC coupling transmitter ownership 已確認，且 BOM 沒有重複 capacitor。
- [ ] 每個 critical row 具 governing spec 與第二份公開原廠設計 evidence。
- [ ] `check_duplicate_pins.py` 與 `check_net_names.py` 通過。
- [ ] `Pending_Human_Verification` critical pins 為 0。

## Schematic CDR

- [ ] 七頁 hierarchy 與 page-to-page ports 一致。
- [ ] Symbols 以 exact datasheet pinout 建立並完成 independent check。
- [ ] Power net、signal net、sideband、test point 命名符合規則。
- [ ] eFuse／buck compensation or internally compensated design、enable、PG、fault path 完整。
- [ ] I²C address、pull-ups、header pinout 與 back-power prevention 完整。
- [ ] Test points 可量測 input、protected 12 V、3.3 V、PGOOD、I²C 與 GND。
- [ ] Annotation、BOM、connection matrix 與 footprint assignment 一致。
- [ ] ERC 無未解釋 error／warning。
- [ ] Native project 可關閉後重新開啟，且 netlist 可重建。

## Gate 2 — Power Design Freeze

- [ ] Target SSD official power information 或明確 restricted envelope 已建立。
- [ ] Slot input、eFuse、buck、shunt 與 connector 的 steady-state power budget 已閉合。
- [ ] 5 A case 包含 efficiency、loss、junction／board temperature 與 derating。
- [ ] 7 A / 100 µs case 包含 inductor current、current limit、Cout droop 與 recovery。
- [ ] MLCC DC-bias、tolerance、temperature 與 aging 影響已納入。
- [ ] Inductor saturation、RMS current 與 thermal rating 已確認。
- [ ] Shunt power、pulse、TCR 與 INA238 full-scale 均有 margin。
- [ ] eFuse startup SOA 與 fault recovery sequence 已確認。
- [ ] Gate failure 時的 Architecture A／restricted SSD fallback 已決策。

## PSpice Review

- [ ] Vendor model URL、revision、download date 與 hash 已保存。
- [ ] Vendor example circuit 可在本機重現，或已記錄 limitation。
- [ ] Startup、input ramp、soft-start、inrush profiles 已建立。
- [ ] 10→100% load step 與 100→10% release 已建立。
- [ ] 7 A / 100 µs pulse 已建立且條件清楚。
- [ ] Line transient、ripple、inductor current、switch-node 與 PGOOD 已建立。
- [ ] Tolerance／derating profiles 已建立。
- [ ] 每個 profile 有 time step、stop time、probe、criteria 與 expected behavior。
- [ ] Loop stability／Monte Carlo 若模型或 license 不支援，已標為 `Not_Supported_By_Model`。
- [ ] 所有圖表標為 `Simulated`，且不描述成 measured。

## Gate 3 — PCB Constraint Freeze

- [ ] 投板當下 JLCPCB 1.6 mm 六層 stack-up 與 quote evidence 已保存。
- [ ] Differential impedance geometry 由 [JLCPCB calculator](https://jlcpcb.com/help/article/user-guide-to-the-jlcpcb-impedance-calculator) 與 governing spec 決定。
- [ ] L1/L2 與 L6/L5 reference 關係已確認。
- [ ] Pair spacing、intra-pair skew、length、via count 與 layer-transition rule 已輸入 Constraint Manager。
- [ ] Plane-crossing prohibition 與 return-via rule 已輸入。
- [ ] Power current／width rules 已由 copper temperature-rise estimate 支持。
- [ ] Constraint export 可追溯至 source table，無 silent default。

## Placement and Routing Review

- [ ] Board outline、edge-finger datum、bracket、M.2 connector、2280 standoff 與 keepout 已確認。
- [ ] 1:1 connector／standoff print check 已完成。
- [ ] SSD top／bottom component envelope 與 chassis clearance 已確認。
- [ ] PCIe breakout 短、直、對稱，pair 無不必要 layer change。
- [ ] 每個 high-speed transition 有鄰近 GND return vias。
- [ ] Pair 無跨 plane split、void 或 reference discontinuity。
- [ ] Buck Cin–switch–inductor–Cout hot loop 最小化。
- [ ] Switch-node copper 受控並遠離 PCIe lane／telemetry sense。
- [ ] Shunt high-current path 與 Kelvin sense 分離。
- [ ] Thermal vias、copper spreading 與 solder-mask intent 已 review。
- [ ] Test points 在裝上 SSD／bracket 後仍可接近。
- [ ] DRC、unconnected report、return-path review 與 power-layout review 無未解釋項。

## Manufacturing Release Review

- [ ] Gerber／ODB++ output 只由實際可用 license 產生。
- [ ] NC Drill、IPC netlist、BOM、P&P、assembly drawing 與 fabrication notes 版本一致。
- [ ] CAM preview 檢查 board outline、drill、mask、paste、legend、edge fingers 與 slots。
- [ ] Controlled-impedance notes 與 stack-up revision 一致。
- [ ] DNI、polarity、pin-1、connector／standoff assembly notes 清楚。
- [ ] AVL 與 lifecycle 在 release date 重新確認。
- [ ] Release archive 具有 revision、date、manifest 與 checksum。

## Bring-up Readiness Review

- [ ] Visual inspection、short check 與 current-limited startup 順序已寫入 traveler。
- [ ] 無 SSD 上電的 voltage、current、PGOOD、ripple criteria 已定義。
- [ ] SSD 安裝後的 inrush／steady-state criteria 已定義。
- [ ] Linux `lspci -vv`、`nvme-cli`、`fio`、`smartctl`、`dmesg` evidence 保存方式已定義。
- [ ] Windows Device Manager、HWiNFO、CrystalDiskInfo／Mark 只作輔助證據。
- [ ] Cold boot、warm boot、不同 SSD 與 thermal stress test matrix 已定義。
- [ ] Fault tree、debug log 與 ECO template 可用。
- [ ] 未執行項目保持 `Planned`／`Not_Yet_Measured`。

## Portfolio Claim Audit

- [ ] README、slides、resume 與口頭稿沒有「PCIe compliant」或等價誤導。
- [ ] 每個數字可連回 official source、calculation、simulation 或 measurement。
- [ ] `Estimated`、`Simulated` 與 `Not_Yet_Measured` 在圖表標題／caption 可見。
- [ ] 未完成 Gate 與設計限制被主動揭露。
- [ ] 面試回答能說明 trade-off、failure mode、verification method 與 ECO path，而非只背規格值。
