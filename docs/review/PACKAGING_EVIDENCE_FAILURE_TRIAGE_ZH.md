# Packaging / Evidence Validator Failure Triage

## 0. Baseline 與執行條件

| 欄位 | 值 |
|---|---|
| Repository | `ErenYagar/nvidia-lde-orcad-portfolio` |
| Branch | `main` |
| Commit | `24d9f51a3bbe024b5cb5d757c8823362d4c2612a` |
| Working directory | `C:\project\orcad_project\.repo_audit_tmp_20260728` |
| Python | `Python 3.13.13` |
| Rerun date | 2026-07-28（Asia/Taipei） |
| Native source modification | 無 |

完整 command、timestamp、exit code、stdout、stderr 與 affected files 保存於：

- `evidence/validation/latest_validator_run.txt`
- `evidence/validation/latest_validator_summary.csv`

## 1. Documented validation commands 結果

| Run ID | Command | Exit code | Contract result | Pass / Fail / Warning |
|---|---|---:|---|---|
| VAL-01 | `python scripts/validate_csv.py --root .` | 0 | PASS | 46 CSV / 0 / 0 |
| VAL-02 | `python scripts/check_bom_fields.py manufacturing/bom.csv` | 0 | PASS | 1 / 0 / 0 |
| VAL-03 | `python scripts/check_duplicate_pins.py schematic/connection_matrix.csv schematic/symbol_pinmap.csv` | 0 | PASS_WITH_REVIEW_WARNINGS | 1 / 0 / 31 |
| VAL-04 | `python scripts/check_net_names.py schematic/connection_matrix.csv` | 0 | PASS | 1 / 0 / 0 |
| VAL-05 | `python scripts/check_documentation_links.py --root .` | 0 | PASS | 225 links / 0 / 0 |
| VAL-06 | `python scripts/check_portfolio_i18n.py` | 0 | PASS | 75 nodes / 0 / 0 |
| VAL-07 | `python -m unittest discover -s scripts -p "test_*.py" -v` | 1 | PARTIAL_FAIL | 42 / 3 / 0 |
| VAL-08 | `python scripts/check_stage3_delivery.py --root .` | 1 | FAILED_NOT_USED_AS_GATE | 0 / 1 / 0 |

另外為 triage 執行：

| Run ID | Command | Exit code | Result |
|---|---|---:|---|
| VAL-09 | `python -X utf8 scripts/check_stage2_delivery.py --root . --mode progress` | 1 | 63 issues：9 baseline artifact missing、27 evidence missing、8 size drift、8 stale hash、5 source missing、6 CSDF evidence missing |

### Negative fixture 判讀

`test_false_routing_claim_fails`、`test_pad_mismatch_fails`、`test_unplaced_component_fails`、`test_missing_physical_pin_fails`、`test_missing_evidence_and_stale_hash_fail` 均為預期 validator 拒絕 invalid fixture 的負向測試，而且本次全部 `ok`。因此 console 中看到 fixture 被 validator 拒絕，不是 repository regression。

本次真正失敗的只有下列三個 repository-specific test。

## 2. Failure 1 — Stage 2 collision evidence 缺失

### 2.1 Test identity

| 欄位 | 內容 |
|---|---|
| Test ID / name | `test_stage2_delivery.Stage2DeliveryTests.test_blocked_collision_cases_are_complete_and_honest` |
| 執行指令 | `python -m unittest discover -s scripts -p "test_*.py" -v` |
| Expected result | `validate_collision_results(PROJECT_ROOT)` 回傳空 issue list |
| Actual result | 回傳 8 個 `Evidence_File:ERROR:evidence file missing` |
| Error message | `AssertionError: Lists differ: [] != [...]`；第一筆為 `stage2_collision_results.csv:2:Evidence_File:ERROR:evidence file missing` |
| Failure category | `Evidence`、`Packaging`、`Missing artifact` |

### 2.2 Affected files

主索引：

- `evidence/stage2/3d/stage2_collision_results.csv`

CSV 仍引用、但 public commit 中不存在的 evidence：

- `evidence/stage2/3d/stage2_3dx_ssd_underside_clearance.jpg`
- `evidence/stage2/3d/stage2_3dx_top.jpg`
- `evidence/stage2/3d/stage2_3dx_bracket_clearance.jpg`
- `evidence/stage2/3d/stage2_3dx_top_iso.jpg`
- `evidence/stage2/3d/stage2_3dx_left.jpg`
- `evidence/stage2/3d/stage2_3dx_right.jpg`
- `evidence/stage2/3d/roundtrip/stage2_step_reimport_3dx.jpg`

### 2.3 Claim / impact assessment

| Claim / gate | 影響 |
|---|---|
| Interview_Digital_Complete | **有影響，限 evidence traceability**。不能說 Stage 2 collision validator 全通過；RevK current evidence 必須獨立引用。 |
| Not_For_Fabrication | 不改變；缺 exact model / evidence 反而支持維持 not-for-fabrication。 |
| DRC closure | 無直接影響；沒有證據顯示 native DRC result 被修改。 |
| PSpice result | 無影響。 |
| Manufacturing package | 對機構／assembly review 有影響；不直接改變 Gerber/NC Drill 檔案內容。 |

Affected claim：`3D-01～3D-08` 每案具有可追溯 evidence，尤其 `Preliminary_Clear` 的 3D-01/3D-08。Blocked case 的誠實狀態仍存在，但所指證據缺失。

### 2.4 Root cause

公開封包保留 `stage2_collision_results.csv`，卻排除了它引用的 Stage 2 JPG evidence。這是 **public-package selection 與 evidence index 不一致**，不是 negative fixture，也不是 native design failure。

### 2.5 Recommended fix / waiver / exit criteria

- Recommended fix：恢復所引用的 Stage 2 evidence 並重新產生 hash manifest；若 Stage 2 已由 RevK 取代，應建立經審查的 supersession mapping，讓每個 case 指向 RevK current evidence，再退役舊 CSV。不可刪除 evidence existence 檢查來讓測試通過。
- Waiver：目前 test contract 下不建議直接 waiver。只有在 RevK evidence 已完整 hash-bound、Stage 2 claim 明確標為 superseded、且 review record 批准後，才可對「歷史 Stage 2 圖不公開」做 packaging waiver。
- Exit criteria：8/8 case 的 `Evidence_File` 存在、hash/board revision 一致，`validate_collision_results()` 回傳 0 issues。
- 修正後 rerun result：本回合未修改 repository，重跑仍為 **FAIL**。

## 3. Failure 2 — Controlled-spec access exception 文件不存在

### 3.1 Test identity

| 欄位 | 內容 |
|---|---|
| Test ID / name | `test_stage2_delivery.Stage2DeliveryTests.test_documented_access_exception_requires_explicit_opt_in` |
| 執行指令 | `python -m unittest discover -s scripts -p "test_*.py" -v` |
| Expected result | 不允許 exception 時 Gate 保持 open；`allow_access_exception=True` 時，明確 exception 文件與 G1-01/G1-02 row 使 validator 回傳 closed-with-exception 且 0 issue |
| Actual result | `closed_with_exception=False` |
| Error message | `AssertionError: False is not true` |
| Failure category | `Evidence`、`Documentation link`、`Missing artifact` |

### 3.2 Affected files

- `stage2/input_gate.csv`：G1-01/G1-02 的 `Current_State` 寫有 `exception recorded`。
- `stage2/CONTROLLED_SPEC_ACCESS_EXCEPTION.md`：CSV 與 validator 期待此檔，但 public commit 中不存在。

### 3.3 Claim / impact assessment

| Claim / gate | 影響 |
|---|---|
| Interview_Digital_Complete | 有限影響：面試版可維持「controlled source blocked」，但不能說 access-exception evidence 完整。 |
| Not_For_Fabrication | 不改變，且仍必須維持。 |
| DRC closure | 無直接影響。 |
| PSpice result | 無影響。 |
| Manufacturing package | **有 Gate 影響**：physical pin / power / mechanical release-critical source 未關閉，不能放行製造。 |

Affected claim：PCIe CEM／M.2 governing specification 因取得限制，已由明確、可審查的 exception 程序處置。現有封包只能證明 Gate 保持 pending，不能證明 exception record 已隨包提供。

### 3.4 Root cause

`input_gate.csv` 保留「exception recorded」文字，但被引用的 exception Markdown 未納入 public package。原因可確定為 **missing evidence artifact**；找不到證據證明 native design 或 pin mapping 因此改變。

### 3.5 Recommended fix / waiver / exit criteria

- Recommended fix：加入不含 restricted standard 內容的 access-exception record，只記錄文件 title/revision、取得限制、禁止事項、reviewer/date 與未關閉 Gate。不得把 PCI-SIG/M.2 受控內容複製進 public repository。
- Waiver：對 fabrication/release claim 不合理。對 interview-only package，只有在 `input_gate.csv` 改成明示 `BLOCKED_NO_EXCEPTION_ARTIFACT`、移除「recorded」的錯誤 claim 後，才可接受暫時 waiver；本回合不可改測試標準。
- Exit criteria：`CONTROLLED_SPEC_ACCESS_EXCEPTION.md` 存在，內容不含 restricted standard，G1-01/G1-02 status 和 reviewer/date 一致，allow-access-exception contract 通過。
- 修正後 rerun result：本回合未修改 repository，重跑仍為 **FAIL**。

## 4. Failure 3 — Stage 2 public-package manifest 不自洽

### 4.1 Test identity

| 欄位 | 內容 |
|---|---|
| Test ID / name | `test_stage2_delivery.Stage2DeliveryTests.test_repository_progress_delivery_passes` |
| 執行指令 | unit test 內呼叫 `python -X utf8 scripts/check_stage2_delivery.py --root <repo> --mode progress` |
| Expected result | progress validator exit code 0 |
| Actual result | exit code 1，63 issues |
| Error message | `AssertionError: 1 != 0`；issues 包含 artifact/evidence/source missing、size drift、stale hash、CSDF evidence missing |
| Failure category | `Packaging`、`Evidence`、`Stale hash`、`Missing artifact` |

### 4.2 Issue composition

| Issue | Count | 說明 |
|---|---:|---|
| Baseline artifact missing | 9 | `stage2/baseline_manifest.csv` 的 10 筆中只有 Amphenol STEP 留在 public package；Stage 1 board/STEP/manifest 與 official-source files被排除 |
| Evidence missing | 27 | Stage 2 batch logs、board/reports、3DX/STEP evidence 等未納入 public package |
| Source missing | 5 | manifest 的 `Source_Path` 指向被排除檔案 |
| CSDF evidence missing | 6 | raw/derived Stage 2 PSpice evidence 被 public curation 排除 |
| Size drift | 8 | 其中 6 筆為 Windows checkout CRLF/LF 差異；2 筆為真正 manifest/current commit 不一致 |
| Stale hash | 8 | 同上：6 筆 Git blob hash 與 manifest 相同，只是 worktree newline conversion；2 筆 Git blob 本身已和 manifest 不同 |

### 4.3 Stale hash 判定

已比對 manifest expected hash、Windows worktree hash 與 `git show HEAD:<path>` blob hash：

- **Checkout newline effect，不是 commit artifact stale**：
  - `capture_electrical_reopen_audit.csv`
  - `erc_report.txt`
  - `run_record.md`
  - `profile_results.csv`
  - `stage2_collision_results.csv`
  - `stage2/delivery_status.csv`

  上述 6 筆的 Git blob SHA-256 與 manifest 一致；Windows worktree 因 CRLF checkout 產生 size/hash 差異。這是 validator 的 cross-platform hashing contract gap。

- **真正 stale manifest**：
  - `schematic/orcad/stage2/native_25_1/pcie_gen3_x4_nvme_adapter_reva_stage2_electrical.opj`
  - `schematic/orcad/stage2/reports/annotation_report.txt`

  這兩筆的 Git commit blob SHA-256 也不等於 manifest expected hash，確認不是單純換行。最可信分類為「artifact 更新後 manifest 未同步」。目前沒有證據指出它們對應不同 board revision；不能猜測為 RevI/RevK mismatch。

### 4.4 Claim / impact assessment

| Claim / gate | 影響 |
|---|---|
| Interview_Digital_Complete | 有影響：不能宣稱 public package validators 全通過；current RevK claim 必須與 historical Stage 2 manifest 分離。 |
| Not_For_Fabrication | 不改變，必須維持。 |
| DRC closure | 無直接 native-design 反證；本 failure 沒有重新解析或否定 RevK native DRC。 |
| PSpice result | 量化摘要仍存在，但 raw CSDF evidence 缺失會降低 public-package reproducibility；3.109 V failure 不得被改寫。 |
| Manufacturing package | public packaging integrity 有影響；不能將 Stage 2 manifest 當 final release manifest。 |

### 4.5 Root cause

根因不是單一問題，而是三層混合：

1. Public package 刻意排除大型／歷史／official-source artifacts，但仍保留 private-workspace manifest。
2. Validator 對 text artifact 以 Windows worktree bytes 驗證，與 Git LF blob hash contract 不一致。
3. OPJ 與 annotation report 是真正未同步 manifest 的 stale entries。

沒有證據顯示 63 issues 本身造成 native board routing、DRC 或 connectivity 改變；但 evidence integrity 與 claim traceability 確實受影響，不能標記為無關緊要。

### 4.6 Recommended fix / waiver / exit criteria

- Recommended fix：建立專用 public-package manifest，只列實際公開 artifact；對 excluded files 記錄 `Excluded_With_Reason` 而不是保留不存在的 required path。將 Git blob hash 與 distributed ZIP/worktree hash分欄記錄；重新產生 OPJ/annotation entries。不可刪除 hash/missing-evidence 檢查。
- Waiver：對 deliberately excluded raw CSDF 可有 conditional packaging waiver，但必須保留 metrics、model/version、run record 與 exclusion rationale。對真正 stale OPJ/annotation hash不可 waiver，應重建 manifest。對 release-critical governing source不可 waiver 成 fabrication pass。
- Exit criteria：progress checker exit 0；manifest 只引用存在或明確 excluded 的 artifact；Git blob/distribution hash contract固定；OPJ/annotation hash同步；CSDF exclusion policy可稽核。
- 修正後 rerun result：本回合未修改 repository，VAL-09 仍為 **63 issues / FAIL**；unit test仍為 **FAIL**。

## 5. Legacy Stage 3 checker（不列入三個 unit-test failures）

`python scripts/check_stage3_delivery.py --root .` exit 1，因為它直接讀取不存在的：

`pcb/allegro/stage3/stage3_3d_mapping_inventory.txt`

`VALIDATION_STATUS.md` 已明確說明此 checker hard-coded for older RevI paths，RevK public package 不以它為 Gate。因此分類為 `Packaging / Legacy path / Missing artifact`。這不是預期 negative fixture，也不應被寫成 PASS；在建立 RevK-aware validator 前維持 `NOT_USED_AS_GATE`。

## 6. 整體結論

### A. 三項是否都只是 packaging 問題？

**否。** 三項都包含 packaging 問題，但 Failure 1、2、3 同時是 evidence integrity / claim traceability 問題；Failure 3 還包含 2 筆真正 stale manifest hash。不能簡化成「只是少放檔案」。

### B. 是否有 native design / evidence integrity 問題？

- 本次沒有發現能證明 native Capture/Allegro design database 損壞或 RevK DRC closure失效的證據。
- **有 evidence integrity 問題**：Stage 2 collision evidence 缺失、access-exception record 缺失、private/public manifest 不一致、2 筆真正 stale hash。

### C. 是否仍可維持 `Interview_Digital_Complete_Not_For_Fabrication`？

**可以有條件維持。** 條件是對外明示：

- RevK current native evidence 與 historical Stage 2 packaging 分開；
- validator status 是 `42/45 PASS, 3 repository-specific FAIL`，不是全綠；
- controlled pin/stack-up/fabrication/bench gates仍 blocked；
- 3.109 V recovery failure與27-case runtime-limited結果不變。

### D. 若不接受上述條件，最誠實的暫時狀態

`Interview_Digital_Candidate_Evidence_Reconciliation_Open_Not_For_Fabrication`

## 7. 本回合 disposition

- 沒有修改任何測試判準。
- 沒有修改 GitHub repository 或 native Cadence/PSpice source。
- 沒有宣稱 validators 全部通過。
- 三個 failure 在本回合只完成分類、root-cause analysis 與 exit criteria；repository rerun result仍為 42/45。
