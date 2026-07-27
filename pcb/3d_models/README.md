# 3D Model Store

本目錄只保存可追溯、授權允許且與 exact MPN／assembly相符的 mechanical models。
MDT420M01501 原廠 STEP 已於 2026-07-24 保存並完成來源與結構驗證；
footprint transform 與 collision review 尚未核准。

## Naming

```text
<manufacturer>_<mpn>_<document-revision>_<download-date>.<step|stp|iges|sab>
```

不得用 `connector.step`、`final.step` 等無法追溯名稱。原始 vendor file若必須保留
官方檔名，mapping CSV仍要記錄 exact MPN與 SHA-256。

## Required record

- manufacturer、exact MPN／assembly revision；
- official product／model URL；
- drawing number／revision；
- download date、login／license限制；
- file size、SHA-256、units；
- original or repaired copy；
- reviewer與 disposition。

## Current inventory and blockers

- `amphenol_mdt420m01501_vendor-c3d-rev-unstated_2026-07-24.stp`：
  exact official product-page model，AP214／mm，SHA-256
  `F5427DE4C21FD8C98D0425E09D63247DC632733ACE2211E52F6E282C68F593CD`。
  Vendor model revision未宣告；Allegro rotation／offset與collision仍待確認。
- PCIe bracket／standoff／exact SSD：尚未選定 exact model。
- Board assembly：Stage 1 native `.brd` 已存在；Stage 2 electrical board尚未建立。

禁止以相近 connector、generic 2280 block或其他專案的 3D model把 blocker標成已完成。
