# OrCAD Engineering Report Gap Audit

## 0. 審查範圍與基準

| 欄位 | 內容 |
|---|---|
| Repository | [ErenYagar/nvidia-lde-orcad-portfolio](https://github.com/ErenYagar/nvidia-lde-orcad-portfolio) |
| Branch | `main` |
| Audited commit | `24d9f51a3bbe024b5cb5d757c8823362d4c2612a` |
| 審查日期 | 2026-07-28（Asia/Taipei） |
| 目前交付定位 | `Interview_Digital_Complete_Not_For_Fabrication` |
| 主要板版次 | RevK interview digital closure；部分 Capture／PSpice 證據仍以 Stage 2 或 RevK 前置資料為來源 |
| 審查方式 | 讀取指定 Markdown、CSV、native report、Allegro/Capture/PSpice 證據與 validator；於同一 commit 的 shallow clone 執行可重現檢查 |

本文件是第一階段 Gap Audit，不是完整技術報告重寫。它以 GitHub `main` 的 commit `24d9f51...` 為唯一基準；`C:\project\orcad_project\nvidia-lde-orcad-portfolio` 的本機工作副本不是該 commit 的 Git checkout，不能拿來替代 repository 證據。

本次沒有加入 PCI-SIG 或 M.2 受版權保護的完整標準；報告只記錄官方入口、access exception 與待人工覆核狀態。

### Status 定義

- `VERIFIED`：有可定位的 native report 或可重現檔案證據，且結論只在該證據範圍內成立。
- `PRELIMINARY`：已有數位輸出或工程候選，但尚未完成 governing specification、板廠資料或最終簽核。
- `SIMULATION-LIMITED`：實際有 solver/model 執行，但結果受模型、時間窗、收斂或量測限制，不能升級成設計通過。
- `BLOCKED`：缺少受控規格、板廠資料、授權、exact model 或實體條件，無法完成該 Gate。
- `OPEN`：已有問題、警告或需人工判斷，尚未形成可關閉的證據。

## 1. Executive conclusion

這個 repository 已足以作為 **PCB／LDE／硬體工程師面試用的數位設計案例**，但還不是可直接送板、可宣稱 PCIe compliance、或已完成實體驗證的產品資料包。

目前最有價值且可追溯的成果包括：

- 有 project-authored Capture／Allegro／PSpice 工作包、native ERC report、native board 與 3DX/STEP 證據。
- RevK 證據記錄 current rule set 下 `DRC=0`、`unconnected=0`、`active rats=0`、`shape islands=0`。
- 已建立 9 組 differential-pair objects（8 data pairs + REFCLK），但實際 impedance、width、gap、skew 與 governing pin mapping 尚未 freeze。
- 有實際 PSpice power run；5 A 與 7 A／100 µs screen 通過指定 3.135 V screen，但 recovery 最低為 3.109 V，屬 failure。
- 27-case recovery sweep 全部被 15 s runtime cap 終止，沒有任何 completed case；不得從中推論 SSD 支援。
- Gerber、NC Drill、IPC-2581、BOM/P&P 與 assembly STEP 已生成，但文件自身標示為 engineering-review／preliminary，不是 fabrication release。

阻擋「完整工程放行」的核心缺口是：

1. PCIe CEM／M.2 physical pin mapping 與 governing specification 尚未正式 freeze。
2. JLCPCB 當期 controlled-impedance stack-up、線寬、間距、via geometry 與 skew 尚未取得並導入。
3. PSpice recovery failure、eFuse functional validation failure 與 27-case runtime-limited sweep 尚未收斂。
4. 未找到可直接引用的 native Constraint Manager final report；CSV／Markdown 不能取代它。
5. 尚無 SI/PI sign-off、thermal validation、physical measurements、enumeration、Gen3 x4 link、NVMe Identify 或 bench bring-up 證據。
6. Public package 的 repository-specific tests 仍有 3 項失敗，主要涉及被排除的歷史 artifact、access exception opt-in 與 stale/missing manifest references。

因此最準確的面試定位是：

> **RevK routed digital release candidate with native ERC/DRC/connectivity and 3DX/STEP evidence; fabricator constraint freeze and physical validation remain open.**

不能寫成「protocol converter」；這是 passive PCIe-to-M.2 interposer／adapter。不能宣稱 PCIe compliance、fabrication-ready、universal SSD support、SI/PI pass 或 bench-qualified。

## 2. 指定文件與目錄盤點

### 2.1 指定文件

以下指定文件在 audited commit 中均找到：

- `README.md`
- `PROJECT_REPORT.md`
- `PROJECT_REPORT_ZH.md`
- `PROJECT_REPORT_EN.md`
- `PROJECT_PLAN.md`
- `VALIDATION_STATUS.md`
- `docs/requirements.md`
- `docs/interface_definition.md`
- `docs/system_block_diagram.md`
- `docs/architecture_tradeoff.md`
- `docs/CLAIM_EVIDENCE_MATRIX_ZH.md`
- `docs/DOCUMENTATION_AUDIT_ZH.md`
- `docs/INTERVIEW_GUIDE_ZH.md`

### 2.2 工程目錄

`schematic/`、`pcb/`、`pspice/`、`evidence/`、`manufacturing/`、`validation/`、`scripts/` 均存在，且包含相應的 native artifact、CSV、報告或 validator。

### 2.3 文件一致性初判

- 目前主報告仍以約 14 個主題段落描述專案，尚未依要求形成 26 章的完整 engineering report。
- `PROJECT_REPORT*`、`README`、`VALIDATION_STATUS` 的限制聲明大致一致，均禁止 PCIe compliance、fabrication-ready 與 physical validation 宣稱。
- Board revision、source path 與 commit hash 沒有在每一個量化 claim 中一致呈現；需要下一階段建立統一 Source Register 與 claim table。
- Public clone 的 validator 結果與 `VALIDATION_STATUS.md` 的歷史摘要存在差異：本次重新執行 46 個 CSV，而文件記載的歷史 run 為 33 個 CSV。兩者都必須保留日期、commit 與命令，不能互相覆寫。

## 3. Gap matrix

| ID | 審查項目 | Status | 已找到的證據 | Gap／不能證明的內容 | 下一步所需證據 |
|---|---|---|---|---|---|
| G-01 | Tool/version | `VERIFIED` | README、native ERC、Allegro/PSpice evidence 記錄 OrCAD X 25.1 S040／Capture／Allegro／PSpice | 工具版本未在每個輸出 artifact manifest 中一致綁定 | 每個 native report、export manifest 加工具版本與執行日期 |
| G-02 | Board revision | `PRELIMINARY` | RevK board、`final_release_status.md`、board hash | Stage 2、RevI、RevJ、RevK 證據並存，部分 report 仍指向舊歷史檔 | 建立 revision-to-artifact matrix，禁止 stale path |
| G-03 | Schematic sheet hierarchy | `VERIFIED` | 7-page Capture DBO/ERC report，61 part instances | 未形成完整 report chapter，且 governed J1/J2 physical pin source 仍 access exception | 保存 native reopen、sheet hierarchy、page hash 與 source mapping |
| G-04 | System block diagram | `PRELIMINARY` | `docs/system_block_diagram.md`、README | Block diagram 是架構說明，不能取代 native schematic review | 將 block diagram nodes 綁定 schematic refs、nets 與 board revision |
| G-05 | Power tree | `PRELIMINARY` | README、power tree、TPS25947 → TPS543620 → shunt → NVMe 路徑 | slot power、inrush、eFuse setting 與 SSD support envelope 未完全 freeze | native power report、slot budget、eFuse validation 與 revised PSpice evidence |
| G-06 | Component selection | `PRELIMINARY` | BOM、architecture tradeoff、TI model assets、SN750 candidate | candidate 不等於 qualified support；部分 alternatives/lifecycle/thermal margin 尚未閉合 | dated datasheet/source register、AVL、derating and lifecycle review |
| G-07 | Derating | `OPEN` | 有 power budget、current/voltage targets 與部分 component rationale | 未找到完整且 native/report-backed 的 resistor、capacitor、inductor、thermal、voltage/current derating table | 建立含 condition、rating、stress、margin、temperature 的 derating report |
| G-08 | Pin/footprint traceability | `BLOCKED` | `physical_pin_report.csv`、symbol pin map、footprints、native reports | controlled PCIe CEM/M.2 pin table 尚未正式可用；不能用 CSV 或公開 secondary source 取代 governing spec | 合法受控 spec review、page/section citation、pin-to-pad cross-probe |
| G-09 | ERC | `VERIFIED` | `schematic/orcad/stage2/reports/erc_report.txt`：0 errors、0 warnings | Result 只涵蓋 configured Capture rules；report 仍明示 compliance/fab-ready prohibited | 保留 native DRC/ERC、project hash、revision matching；不要擴大結論 |
| G-10 | PSpice profiles | `SIMULATION-LIMITED` | `pspice/stage2/profile_results.csv`、vendor model logs、recovery sweep | recovery 3.109 V failure；eFuse functional validation failed；27 sweep cases runtime-limited | 完成或正式封存 timeout evidence、修正 power design、bench correlation |
| G-11 | Stack-up | `BLOCKED` | `pcb/stackup.md`、JLCPCB candidate reference | 當期 fab stack-up、dielectric/copper thickness、impedance calculator output 未凍結 | JLCPCB dated quote/calculator/stack-up PDF，含 board revision |
| G-12 | Constraint Manager | `BLOCKED` | `evidence/stage3/constraint_manager_status.md`、`pcb/constraints.csv` | 找不到名為 `constraint_report.txt` 的 native final report；CSV/Markdown 不是 native sign-off | native Constraint Manager export、rule freeze、tool log、stack-up binding |
| G-13 | Differential pairs | `PRELIMINARY` | `pcb/differential_pairs.csv`：9 pair objects | 9 objects 不等於通過 impedance/skew；9 rows 的 pin mapping/status 仍 pending | native pair/constraint report、governing pin source、fabricator geometry |
| G-14 | Length/skew | `BLOCKED` | 有 pair intent／constraint rows | 未找到可接受的 final length/skew report，也沒有可信 geometry freeze | native length/skew report、stack-up、pair tuning review |
| G-15 | Return paths | `PRELIMINARY` | board layer intent、GND planes、3DX/placement evidence | 未找到 SI/PI sign-off 或 native return-path analysis；DRC=0 不證明 return path | layer-by-layer return-path review、SI/PI evidence、plane cut/transition analysis |
| G-16 | Power routing | `PRELIMINARY` | RevK power planes、shape-island=0、DRC/unconnected counters | 沒有完整 current-density、thermal copper、via capacity 與 power integrity sign-off | native shape report、current/thermal calculation、PI review |
| G-17 | Kelvin sensing | `PRELIMINARY` | 5 mΩ shunt、INA238、Kelvin intent、telemetry docs | 未找到實板 shunt drop/measurement error/placement review；不能稱 telemetry validated | Kelvin net cross-probe、layout review、bench measurement plan/results |
| G-18 | DRC | `VERIFIED` | RevK `3d_status.md` and release reports: DRC 0 | 只在 current rule set 成立；不等於 SI/PI、DFM 或 fab sign-off | native DRC report hash、final stack-up rules、DFM ruleset |
| G-19 | DFM/DFA/DFT | `OPEN` | manufacturing README、assembly/BOM/P&P、bring-up plan | 未找到完整 fab/assembly/DFT checklist 的 native sign-off；0-width CAM warnings retained | fabricator DFM feedback、assembly review、test-point/access coverage |
| G-20 | 3DX/STEP | `PRELIMINARY` | AP242/mm STEP、isolated DRA readback、3DX images、3D status | exact SSD/standoff/bracket/chassis/service-path models 不全；collision cases 仍 preliminary/blocked | exact model files、transform hash、3D-01~08 re-run、native screenshots |
| G-21 | BOM/P&P | `PRELIMINARY` | `manufacturing/bom.csv`、P&P、BOM hash bound | BOM/P&P 是 preliminary；不等於 procurement AVL、assembly approval 或 fab release | final AVL, MPN/lifecycle, package/rotation, assembly sign-off |
| G-22 | CAM outputs | `PRELIMINARY` | 14 Gerber、2 NC Drill、IPC-2581-C、CAM README | IPC-356 empty excluded；ODB++ unsupported；Gerber has retained 0-width warnings | final CAM review, fabricator import feedback, corrected/exported netlist |
| G-23 | Bring-up plan | `PRELIMINARY` | validation/stage3 bring-up gate and test sequence | 只有 planned procedure，沒有 physical board, instrument log 或 enumeration result | safety power-up log, scope captures, lspci/NVMe Identify, thermal log |
| G-24 | Physical measurements | `OPEN` | 未找到 actual voltage/ripple/inrush/temperature/Gen3 link measurement | PSpice 與 digital report 不能代替量測 | dated bench data with instrument/model/probe/bandwidth/conditions |
| G-25 | References | `PRELIMINARY` | README links、source docs、official vendor model records | 尚無統一 Source Register；controlled spec access exception 未形成逐 claim register | `SOURCE_REGISTER.md/.csv`、access date、revision/page、review status |
| G-26 | Personal contribution | `OPEN` | interview guide、project narrative、文件中有 self-directed project 描述 | 尚未將 individual contribution、tool ownership、review boundary 逐項與 artifact 綁定 | contribution matrix：本人完成、工具執行、假設、待人工簽核 |
| G-27 | Known limitations | `VERIFIED` | README、PROJECT_REPORT、VALIDATION_STATUS、final release status | 限制已多數明示，但跨檔案的 wording/board revision/commit 尚未完全一致 | claim-evidence cross-check，對每個 limitation 綁 source path |
| G-28 | ECO plan | `PRELIMINARY` | Rev L plan、power recovery、stack-up、exact model、DFM/bring-up open items | 尚無 actual Rev L ECO record、diff、re-run evidence 或 ECO approval | Rev L change list、before/after native reports、reviewer/date/status |

## 4. 量化 Claim / Evidence register（本次 Gap Audit 範圍）

每筆量化結論均保留數值、單位、條件、狀態、source path、board revision 與 audited commit。`VERIFIED` 僅代表該數值在來源檔的狹義範圍內成立，不代表產品通過。

| Claim | 數值與單位 | 條件 | Status | Source path | Board rev | Git commit |
|---|---:|---|---|---|---|---|
| Board geometry/layer baseline | 120 × 64 mm；1.600 mm nominal；6 layers | RevK digital board baseline；preliminary mechanical envelope | `PRELIMINARY` | `PROJECT_REPORT.md`; `evidence/stage3/final_release_status.md` | RevK | `24d9f51a3bbe024b5cb5d757c8823362d4c2612a` |
| Native board connectivity checks | DRC 0；unconnected 0；active rats 0；shape islands 0 | Current native rule set and RevK audit | `VERIFIED` | `evidence/stage3/3d_status.md`; `evidence/stage3/constraint_manager_status.md` | RevK | same |
| Logical design size | 61 components；54 nets；197 unrouted connections reported as 0 after routing | Native board/3DX status; does not prove electrical protocol correctness | `VERIFIED` | `evidence/stage3/3d_status.md`; `schematic/orcad/stage2/reports/erc_report.txt` | RevK / Stage 2 source | same |
| Differential-pair objects | 9 pairs | 8 data + REFCLK; pair constraints still pending | `PRELIMINARY` | `pcb/differential_pairs.csv`; `evidence/stage3/constraint_manager_status.md` | RevK | same |
| Native ERC | 0 errors；0 warnings；7 pages；61 part instances | Native Capture ERC + DBO/ISCF audit; 53 expected vs 54 actual nets; one documented extra net | `VERIFIED` | `schematic/orcad/stage2/reports/erc_report.txt` | Stage 2 electrical source | same |
| 5 A steady-state power result | 3.149 V minimum | PW-01 macro-model run; compared with 3.135 V screen | `SIMULATION-LIMITED` | `pspice/stage2/profile_results.csv` | RevK power model | same |
| 7 A / 100 µs pulse result | 3.204 V minimum | PW-01 macro-model run; compared with 3.135 V screen | `SIMULATION-LIMITED` | `pspice/stage2/profile_results.csv` | RevK power model | same |
| Recovery result | 3.109 V minimum | PW-01 recovery window; PGOOD remained high; 3.135 V screen | `SIMULATION-LIMITED` / failure | `pspice/stage2/profile_results.csv`; `PROJECT_REPORT.md` | RevK power model | same |
| Peak inductor current | 8.656 A | PW-01 macro-model run; model/layout/thermal limitations apply | `SIMULATION-LIMITED` | `pspice/stage2/profile_results.csv` | RevK power model | same |
| Recovery sweep | 27 cases; 15 s timeout each; 0 completed | `COUT_EFF={100,132,176} µF`, `ESR={2,3,5} mΩ`, `CFF={0,4.7,8.2}` pF | `SIMULATION-LIMITED` / not concluded | `pspice/stage3/recovery_sweep/recovery_sweep_results.csv` | RevK power model | same |
| Repository CSV validation | 46 CSV；0 format issues | `python scripts/validate_csv.py --root .` on audited clone | `VERIFIED` | validator console result; `scripts/validate_csv.py` | Repository audit | same |
| Duplicate-pin review | 0 errors；31 warnings | Same-net duplicate appearance; requires human cross-probe | `OPEN` | `VALIDATION_STATUS.md`; validator result | Repository audit | same |
| Manufacturing outputs | 14 Gerber；2 NC Drill | Engineering review output; not final fab release | `PRELIMINARY` | `manufacturing/stage3_final_revk/export_status.csv` | RevK | same |
| Fabrication status | `Fabrication_Ready=false` | Current stack-up, controlled specs, impedance freeze and physical evidence absent | `BLOCKED` | `evidence/stage3/final_release_status.md` | RevK | same |

## 5. Validator 與 native evidence 結果

### 5.1 本次在 audited clone 執行

| Command | 結果 | 解讀 |
|---|---|---|
| `python scripts/validate_csv.py --root .` | PASS；46 CSV；0 issues | 資料格式通過，不是 electrical sign-off |
| `python scripts/check_bom_fields.py manufacturing/bom.csv` | PASS；0 issues | BOM 欄位完整，不代表 AVL、採購或組裝 approval |
| `python scripts/check_duplicate_pins.py ...` | PASS；0 errors；31 warnings | same-net fanout warnings 仍需人工 review |
| `python scripts/check_net_names.py ...` | PASS；0 issues | 命名／配對檢查通過，不代表 pin mapping governing spec 已確認 |
| `python scripts/check_documentation_links.py --root .` | PASS；225 local links；0 issues | 連結完整，不代表內容正確 |
| `python scripts/check_portfolio_i18n.py` | PASS；75 i18n nodes；0 issues | 中英文節點檢查通過 |
| `python -m unittest discover -s scripts -p "test_*.py" -v` | FAIL；45 tests，3 failures | Public package 的 repo-specific tests 仍有 evidence/manifest/access-exception gaps |

三個失敗測試的性質：

1. `test_blocked_collision_cases_are_complete_and_honest`：public package 缺少部分歷史 collision evidence。
2. `test_documented_access_exception_requires_explicit_opt_in`：access exception 的 opt-in 規則與現有資料不一致。
3. `test_repository_progress_delivery_passes`：部分 Stage 2 manifest 指向被排除的歷史 artifact，並存在 stale hash／CSDF evidence reference。

### 5.2 Native report 優先原則

目前找到最有價值的 native source 是：

- `schematic/orcad/stage2/reports/erc_report.txt`：native Capture ERC、DBO/ISCF connectivity audit、0 errors、0 warnings，且清楚標示 scope limitation。
- `evidence/stage3/3d_status.md`：記錄 board hash、DRC/connectivity/shape counters、STEP hash 與 native DRA readback，但其本身是 evidence summary，不是 native Allegro report。
- `evidence/stage3/constraint_manager_status.md`：記錄 9 pair objects 與 pending rule freeze，但不能取代 native final Constraint Manager export。

本次未找到名為 `constraint_report.txt` 的 native final Constraint Manager report。`pcb/constraints.csv`、`pcb/differential_pairs.csv`、Markdown status 與 Python validator 只能作為 traceability／intent 輔助，不能單獨宣稱 Constraint Manager sign-off。

## 6. 高優先級缺口

### P0：不得在面試或報告中越級宣稱

- **Physical pin freeze**：CEM/M.2 controlled source、revision、page/section、pin-to-pad cross-probe 未閉合。
- **Impedance/stack-up freeze**：沒有當期 JLCPCB stack-up／calculator evidence，因此 width、gap、skew、via geometry 仍 pending。
- **Power closure**：3.109 V recovery failure；eFuse isolated functional validation failure；27-case sweep 未結論。
- **Native constraints**：找不到 final native Constraint Manager report。
- **Physical validation**：沒有實體 voltage/ripple/inrush/thermal、enumeration、Gen3 x4、NVMe Identify 或 bench log。

### P1：面試資料可用，但需補強可審查性

- RevK 與 Stage 2/RevI/RevJ 證據需由一張 revision matrix 統一。
- 所有量化 claim 要統一加 source path、board revision、commit、condition、status。
- Public release 內的 historical artifact／manifest reference 需修正，讓 45 tests 全部通過；這是 repository packaging gap，不應掩蓋為 design pass。
- DFM/DFA/DFT、derating、Kelvin measurement、P&P orientation、CAM warning 與 ECO proof 需補成正式 review record。
- 3D exact model 缺口要按 case 分開寫，不能將 Preliminary_Clear 寫成 collision Pass。

## 7. 建議後續順序（本回合不執行）

1. 建立 `docs/SOURCE_REGISTER.md` 與 `docs/SOURCE_REGISTER.csv`，先統一所有 claim 的來源、版本、頁碼、access status 與 review status。
2. 只分析實際存在的 `profile_results.csv`、recovery sweep、DRC/constraint、BOM、pair 與 validation CSV，輸出 5 A、7 A、recovery 分開的 data analysis；明確保留 3.109 V failure 與 27-case runtime-limited。
3. 修正 public-package stale manifest／missing evidence／access-exception test，再重新執行 45 tests。
4. 依 28 項 Gap matrix 補強 `ORCAD_ENGINEERING_REPORT_ZH.md`，但每一章只引用已存在的 evidence，找不到就寫「未找到」。
5. 最後才建立 12 頁、每頁標題直接呈現結論的面試 deck outline。

## 8. 本回合完成範圍

- 已完成 GitHub repository `main` commit `24d9f51...` 的 Gap Audit。
- 已建立本文件：`C:\project\orcad_project\結論\docs\review\ORCAD_REPORT_GAP_AUDIT_ZH.md`。
- 沒有在 GitHub repository 內改寫 README、PROJECT_REPORT、PROJECT_PLAN、VALIDATION_STATUS 或其他工程文件。
- 尚未建立 Source Register、engineering summary、完整 26 章技術報告或 12 頁簡報；這些屬於使用者指定的後續階段。
