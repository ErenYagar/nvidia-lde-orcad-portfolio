# Source Gap Action List

## 0. Baseline

- Repository：`ErenYagar/nvidia-lde-orcad-portfolio`
- Branch：`main`
- Commit：`24d9f51a3bbe024b5cb5d757c8823362d4c2612a`
- Source Register：`docs/SOURCE_REGISTER.csv`，46 entries
- Review date：2026-07-28

本清單只排序來源／證據缺口，不代表已授權取得 restricted standard，也不授權把 PCI-SIG、M.2 或 IPC 完整文件加入公開 repository。

## 1. Summary

| Priority | Count | 定義 |
|---|---:|---|
| P0 | 7 | 可能造成錯誤接線、損壞、無法投板、安全風險或將錯誤 revision 送入 release |
| P1 | 8 | 影響 SI/PI、thermal、mechanical、DFM 或 validation 結論 |
| P2 | 6 | 文件品質、引用完整度、公開封包一致性與面試呈現 |
| Total | 21 | — |

## 2. P0 — Wiring / safety / fabrication blockers

| ID | Gap | Related source | Risk | Required action | Exit criteria |
|---|---|---|---|---|---|
| P0-01 | PCIe CEM 3.0 controlled copy/review 未取得 | SR-001 | J1 pin、PRSNT、slot power、inrush、mechanical 可能錯誤 | 由合法授權 reviewer 讀取 applicable revision；只保存 title/revision/section/page/disposition，不公開全文 | J1 physical pin/power/mechanical review record有 reviewer/date，所有差異已處置 |
| P0-02 | M.2 controlled specification 未取得 | SR-003 | J2 lane/sideband/3.3 V/GND/CONFIG/NC 可能錯接 | 合法 review controlled M.2 revision；與公開 NVIDIA/Renesas 只作 cross-check | J2 pin table逐 pin review完成，reserved/NC處置與 revision/page可追溯 |
| P0-03 | Pin-to-symbol-to-pad-to-net traceability 尚未以 governing source closure | SR-001, SR-003, SR-006, SR-007, SR-035 | 即使 ERC/DRC=0，錯誤 pin mapping仍可通過 CAD 規則 | 在 Capture/Allegro native cross-probe逐 pin覆核 J1/J2，產生 pin report與 reviewer sign-off | 無 `PENDING_*` release-critical pins；symbol/pad/net/source四向一致 |
| P0-04 | JLCPCB 當期 stack-up、impedance geometry、via structure未凍結 | SR-032, SR-033, SR-034, SR-046 | 無法可靠投板；阻抗與 return path 可能不符合設計目標 | 保存 dated quote/order stack-up與calculator report；再導入 Constraint Manager | dielectric/copper/width/gap/drill/pad/reference layer綁定 board revision；native report frozen |
| P0-05 | TPS25947 eFuse settings、slot inrush、SOA/fault policy未關閉 | SR-001, SR-008, SR-009, SR-010 | 上電過流、slot violation、thermal shutdown或錯誤 latch behavior | 完成 ILIM/dVdt/ITIMER/PGTH/OVCSEL/SOA worksheet與 model/bench plan | settings有 tolerance/thermal evidence；fault behavior符合安全需求 |
| P0-06 | Buck recovery 3.109 V failure與8.656 A peak-current margin未解決 | SR-011, SR-013, SR-020, SR-021 | SSD rail超出3.135 V內部screen；可能 reset/data loss或過流 | 修正 COUT/compensation/power stage，完成官方model run與量測計畫；不得更改 criteria掩蓋 failure | recovery在條件內通過，PGOOD/current/thermal margin有證據；否則限制SSD claim |
| P0-07 | Public/private manifest、board revision與artifact hash contract不一致 | SR-028, SR-040, SR-043, SR-044 | 可能把錯誤 revision、舊報告或錯誤 CAM package送入 review/fabrication | 建立 public-release manifest；分離 Git blob hash與distributed-file hash；修正2筆真正 stale hash | 所有 required artifacts存在或明確excluded；hash/board revision一致；progress validator exit 0 |

## 3. P1 — SI/PI / thermal / mechanical / DFM / validation

| ID | Gap | Related source | Impact | Required action | Exit criteria |
|---|---|---|---|---|---|
| P1-01 | Cin/Cout exact MPN 的 DC-bias、temperature、ripple/effective capacitance資料未保存 | SR-020, SR-021 | PI與recovery結果可能使用不實際的電容值 | 保存原廠 characteristic report與 revision；以12 V/3.3 V、溫度與 tolerance重算 | effective capacitance與ESR/ESL corner進入PSpice/BOM並通過review |
| P1-02 | XGL5050 hot inductance、core loss、thermal與peak-current margin未完成 | SR-019 | 可能飽和、過熱或改變 transient response | 取得 exact revision/curves；用8.656 A evidence與hot DCR/Irms重算 | worst-case Isat/core/temperature margin documented |
| P1-03 | WSK2512 datasheet revision、pulse/TCR/land-pattern與熱誤差未閉合 | SR-018, SR-039 | Kelvin量測誤差、焊盤熱問題與pulse stress不明 | 保存 revision-controlled datasheet/drawing；做 shunt tolerance/thermal analysis | force/sense pad、pulse、TCR、自熱誤差與footprint sign-off完成 |
| P1-04 | PCIe/REFCLK length、skew、loss、return-path/native constraint report未形成 release sign-off | SR-001, SR-003, SR-044, SR-046 | DRC=0不能證明SI通過 | 在stack-up freeze後產生 native pair/length/skew/transition report與return-path review | 9 pair rules frozen；所有 deviations有處置；仍不宣稱compliance |
| P1-05 | Power-plane current density、via capacity、thermal與PI sign-off不足 | SR-008, SR-011, SR-031, SR-045 | 可能造成droop、溫升或局部可靠度問題 | 依實際銅厚/shape/via做 current/thermal review，保存 PI/thermal assumptions | power routing、hot loop、SW keepout、thermal vias與rail drop有可審查結果 |
| P1-06 | Exact SSD/standoff/bracket/cable/chassis CAD不完整 | SR-038, SR-040, SR-041, SR-042 | collision/fit/chassis compatibility無法簽核 | 取得exact合法模型與drawing，確認transform/datum/revision | 3D-01～3D-08以exact models重跑；blocked cases關閉或保持明確blocker |
| P1-07 | DFM/DFA/DFT及test-point/probe-access缺少fabricator/assembler review | SR-029, SR-030, SR-031, SR-035 | CAM可生成但可能不可製造/組裝/測試 | 執行fab DFM、assembly orientation/stencil、test-access review | vendor feedback關閉；IPC-356/替代netlist與CAM preview可用 |
| P1-08 | 27-case recovery sweep runtime-limited，eFuse functional model亦未通過 | SR-010, SR-013 | 模擬空間沒有結論，不能外推SSD支援 | 以可接受runtime/solver設定重新跑或正式標示model limitation並建立bench替代 | 每個case有concluded pass/fail或approved model-limit disposition；supported SSD仍需bench |

## 4. P2 — Documentation / public package / interview clarity

| ID | Gap | Related source | Impact | Required action | Exit criteria |
|---|---|---|---|---|---|
| P2-01 | Stage 2 collision CSV引用7個不存在的JPG evidence | SR-040, SR-041 | 3D claim traceability中斷；unit test failure | 恢復evidence或建立經審查的RevK supersession mapping | 8/8 case evidence存在且hash/board revision一致 |
| P2-02 | `CONTROLLED_SPEC_ACCESS_EXCEPTION.md` 缺失，但input gate宣稱已recorded | SR-001, SR-003 | Access-exception claim不完整 | 加入不含restricted內容的exception record，或改成明確blocked且不宣稱recorded | allow-access-exception contract與文件內容一致 |
| P2-03 | Legacy `check_stage3_delivery.py` hard-coded RevI path | SR-040 | RevK public package無可用Stage 3 automated gate | 建立RevK-aware checker或由versioned manifest提供path；保留legacy result | 新checker針對RevK return 0，且不放寬evidence checks |
| P2-04 | TMP1075、WSK、XGL5050、TDK與多個dynamic pages缺exact revision/file hash | SR-016, SR-018, SR-019, SR-020, SR-021, SR-022 | Datasheet引用無法長期重現 | 保存授權允許的revision-controlled datasheet或metadata/hash | 所有critical BOM source都有document number/revision/access date/hash |
| P2-05 | Stage 2/RevI/RevJ/RevK revision-to-artifact mapping不集中 | SR-028, SR-040, SR-043, SR-044 | 面試與review容易引用舊數字/舊圖 | 建立revision matrix與superseded policy | 每個量化claim列source path、board revision、commit與status |
| P2-06 | Personal contribution、reviewer責任與claim/source對照仍分散 | All register entries | 面試官難以判斷本人完成內容與工具/人工邊界 | 建立contribution matrix與claim-evidence table；不得把工具輸出說成人工sign-off | 每個主要成果有owner/reviewer/evidence/non-goal，中文英文一致 |

## 5. Status recommendation

目前可維持：

`Interview_Digital_Complete_Not_For_Fabrication`

但必須同時附註：`Validator_Suite_Partial_42_of_45; Evidence_Reconciliation_Open`。

在 P0-01～P0-07 關閉前，`Fabrication_Ready` 必須保持 `false`；在實板與量測完成前，不得宣稱 PCIe compliance、Gen3 x4 link、enumeration、NVMe Identify、SI/PI/thermal或bench validation通過。
