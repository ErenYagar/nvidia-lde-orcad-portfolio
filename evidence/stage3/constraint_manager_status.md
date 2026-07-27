# Constraint Manager 最終狀態

Disposition：`Blocked_Pending_Fabricator_And_Governing_Specification`

RevK native board 已完成：

- 8 組 PCIe data pairs與 1 組 REFCLK pair，共 **9** 組 native differential pairs；每組均有兩個 members。
- DRC 0、unconnected 0、active rats 0、PCIe unconnected 0。
- L2/L5 GND shapes、L4 power shapes、Kelvin power split與 `Shape Islands=0`。
- power、Kelvin、sideband與 differential-pair 分類資料已保留在 constraint source CSV 與 native board。

仍未凍結：

- 九組 pair 的實際 width、gap、via drill/pad、anti-pad、reference-layer geometry。
- length/skew release limit與 backdrill 決策。
- JLCPCB 當期 1.6 mm 六層 dielectric/copper thickness。
- PCIe CEM／M.2 governing impedance與mechanical sign-off。

上述九組規則狀態維持 `Pending_Fabricator_Confirmation`，`RULE_FREEZE=NOT_FROZEN`。沒有用猜測值取代板廠 calculator 結果；因此本狀態支援 `Interview_Digital_Complete`，但禁止 `Fabrication_Ready` 宣稱。
