#!/usr/bin/env python3
"""Generate a SHA-256 manifest for downloaded vendor model evidence."""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
from datetime import date
from pathlib import Path
from typing import Sequence


SOURCE_MAP = {
    "SLUM787A": {
        "url": "https://www.ti.com/lit/zip/slum787a",
        "provenance": "Texas Instruments official TPS543620 PSpice archive",
    },
    "SLVMDJ6A": {
        "url": "https://www.ti.com/lit/zip/slvmdj6a",
        "provenance": "Texas Instruments official TPS25947x PSpice archive",
    },
}

FIELDNAMES = (
    "Source_ID",
    "Relative_Path",
    "File_Size_Bytes",
    "SHA256",
    "Official_Source_URL",
    "Access_Date",
    "Provenance",
    "Status",
    "Notes",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def source_id(relative_path: Path) -> str:
    return relative_path.parts[0].split(".", 1)[0].upper()


def build_rows(
    root: Path,
    source_dir: Path,
    output: Path,
    access_date: str,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file() or path.resolve() == output.resolve():
            continue
        relative_to_source = path.relative_to(source_dir)
        identifier = source_id(relative_to_source)
        source = SOURCE_MAP.get(identifier)
        rows.append(
            {
                "Source_ID": identifier,
                "Relative_Path": path.relative_to(root).as_posix(),
                "File_Size_Bytes": str(path.stat().st_size),
                "SHA256": sha256(path),
                "Official_Source_URL": source["url"] if source else "",
                "Access_Date": access_date,
                "Provenance": source["provenance"] if source else "Unmapped source",
                "Status": (
                    "Confirmed_Official"
                    if source
                    else "Pending_Human_Verification"
                ),
                "Notes": (
                    "Original vendor archive"
                    if path.suffix.lower() == ".zip"
                    else f"Extracted from {identifier} archive"
                ),
            }
        )
    return rows


def main(argv: Sequence[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=Path("pspice/vendor_models/ti"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("pspice/vendor_models/source_model_manifest.csv"),
    )
    parser.add_argument("--access-date", default=date.today().isoformat())
    args = parser.parse_args(argv)

    root = args.root.resolve()
    source_dir = (
        args.source_dir.resolve()
        if args.source_dir.is_absolute()
        else (root / args.source_dir).resolve()
    )
    output = (
        args.output.resolve()
        if args.output.is_absolute()
        else (root / args.output).resolve()
    )

    if not root.is_dir():
        print(f"ERROR: root directory not found: {root}", file=sys.stderr)
        return 2
    if not source_dir.is_dir() or not source_dir.is_relative_to(root):
        print(
            f"ERROR: source directory must exist inside root: {source_dir}",
            file=sys.stderr,
        )
        return 2
    if not output.is_relative_to(root):
        print(f"ERROR: output must be inside root: {output}", file=sys.stderr)
        return 2

    try:
        rows = build_rows(root, source_dir, output, args.access_date)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=FIELDNAMES,
                lineterminator="\n",
            )
            writer.writeheader()
            writer.writerows(rows)
    except (OSError, UnicodeError, csv.Error) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Wrote {output} with {len(rows)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
