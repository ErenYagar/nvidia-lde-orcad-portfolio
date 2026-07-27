# Stage 3 fabrication 與 bring-up gate

- Interview status：`Interview_Digital_Complete`
- Fabrication_Ready: `false`
- PCIe compliance：`Not_Claimed`
- Bench qualification：`Not_Yet_Measured`
- ODB++：`Not_Supported_By_Installed_Tool`
- IPC-356：`Failed_Empty_Output_Excluded`

## 已完成的 OrCAD 數位 closure

- [x] RevK native board 可 save、close、reopen，且 SHA-256 已綁定 manifest。
- [x] Native DRC 0，無 hidden/waived DRC 宣稱。
- [x] Unconnected 0、active rats 0、PCIe unconnected nets 0。
- [x] L2/L5 GND與 L4 power shapes 已建立；shape islands 0、unassigned shapes 0。
- [x] 9 組 PCIe/REFCLK native differential pairs，每組兩個 members。
- [x] Gerber、NC Drill、IPC-2581、BOM、P&P、assembly artwork、CAM previews與STEP已由同一 RevK board hash產生。
- [x] Assembly STEP 已隔離重新指派至 native DRA並讀回 mapping。
- [x] RevK native 3DX證據與八張黑背景portfolio圖已寫入hash-bound manifests。
- [x] PSpice 3.109 V recovery failure與27案 runtime limit已保存且明示。
- [x] IPC-356空檔已排除；ODB++安裝限制已明示。

## Fabrication release 尚未完成

- [ ] 取得並封存 JLCPCB 當期 1.6 mm 六層 controlled-impedance stack-up與quote。
- [ ] 以 PCIe CEM／M.2受控規格完成 critical pin、mechanical與impedance sign-off。
- [ ] 依板廠calculator凍結九組 pair的width/gap/via/anti-pad/reference-layer規則。
- [ ] 完成最終 Constraint Manager report、SI/return-path人工審查與全層CAM review。
- [ ] 凍結 eFuse current limit/inrush、有效輸出電容與 supported-SSD power envelope。
- [ ] 以exact SSD/standoff/bracket/cable/chassis/heatsink CAD重跑3D-01～3D-08。
- [ ] 根據上述ECO重新產生所有製造輸出並由第二人覆核。
- [ ] 使用者明確核准板廠、數量、價格與上傳archive hash。

## 實體 bring-up

1. 記錄板號、批次、目視與bare-board short檢查。
2. 無SSD，以current-limited bench supply驗證12 V、protected 12 V、3.3 V與PGOOD。
3. 驗證I²C telemetry與header不可回灌。
4. 電源Gate通過後才安裝核准的sacrificial SN750。
5. 記錄startup current、3.3 V droop、PGOOD與溫度。
6. Host關機後安裝卡，確認bracket與connector seating。
7. 記錄enumeration、BDF、negotiated speed/width、AER與NVMe Identify。
8. 依序執行read-only、短I/O、stress與thermal測試。
9. 所有異常寫入`debug_log_template.md`，變更使用`eco_template.md`。

實體量測前，所有bring-up結果只可標示`Planned`或`Not_Yet_Measured`。
