#!/usr/bin/env python3
"""Remove selected field-level keys from soziale-gesundheit.yaml."""

from __future__ import annotations

import re
import sys
from pathlib import Path

DROP_KEYS = frozenset({"fremde_mittel", "aktualitaet", "spannung"})
FIELD_KEY = re.compile(r"^    ([a-z_0-9]+):")


def strip_keys(lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        m = FIELD_KEY.match(line)
        if m and m.group(1) in DROP_KEYS:
            i += 1
            while i < len(lines):
                nxt = lines[i]
                if FIELD_KEY.match(nxt):
                    break
                if nxt.startswith("  - id:") or re.match(r"^  chunk_id:", nxt):
                    break
                if re.match(r"^chunk_id:", nxt):
                    break
                i += 1
            continue
        out.append(line)
        i += 1
    return out


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    path = root / "sources/typologies/soziale-gesundheit.yaml"
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    new_lines = strip_keys(lines)
    path.write_text("".join(new_lines), encoding="utf-8")
    remaining = sum(
        1 for ln in new_lines if any(k in ln for k in DROP_KEYS)
    )
    print(f"Updated {path}; lines with dropped key names: {remaining}")
    return 0 if remaining == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
