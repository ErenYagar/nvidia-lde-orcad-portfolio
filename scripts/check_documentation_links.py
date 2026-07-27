"""Check local Markdown links and HTML href/src paths without network access."""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from urllib.parse import unquote

LINK_RE = re.compile(r"(?<!\!)\[[^\]]+\]\(([^)]+)\)|(?:href|src)=\"([^\"]+)\"")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    root = args.root.resolve()
    checked = 0
    issues: list[str] = []
    files = list(root.rglob("*.md")) + [root / "portfolio/index.html"]
    for source in files:
        if not source.is_file():
            continue
        text = source.read_text(encoding="utf-8", errors="ignore")
        for match in LINK_RE.finditer(text):
            target = (match.group(1) or match.group(2)).split("#", 1)[0]
            if not target or target.startswith(("http:", "https:", "mailto:", "data:", "#")):
                continue
            checked += 1
            resolved = (source.parent / unquote(target)).resolve()
            if not resolved.exists():
                issues.append(f"{source.relative_to(root)} -> {target}")
    for issue in issues:
        print(f"ERROR:{issue}")
    print(f"Checked {checked} local link(s); {len(issues)} issue(s).")
    return 1 if issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
