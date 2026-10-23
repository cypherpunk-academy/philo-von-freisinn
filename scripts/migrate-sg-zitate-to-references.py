#!/usr/bin/env python3
"""§3a.1: Drop freitext zitate from soziale-gesundheit.yaml; FM members.references."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ZITATE_8 = re.compile(r"^        zitate:(?: \[\])?\s*$")
ZITATE_4 = re.compile(r"^    zitate:(?: \[\])?\s*$")
CHUNK_8 = re.compile(r"^        chunk_id:")
ASPECT = re.compile(r"^      - schlagwort:")
FIELD_KEY = re.compile(r"^    [a-z_]+:")


def skip_zitate_content(lines: list[str], i: int, stop_patterns: list[re.Pattern[str]]) -> int:
    while i < len(lines):
        nxt = lines[i]
        for pat in stop_patterns:
            if pat.match(nxt):
                return i
        if nxt.startswith("  - id:") or nxt.startswith("  #"):
            return i
        i += 1
    return i


def strip_zitate_blocks(lines: list[str]) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if "zitate:" in line and not ZITATE_8.match(line) and not ZITATE_4.match(line):
            out.append(re.sub(r"\s+zitate: \[\]\s*$", "\n", line.rstrip("\n")) + line[len(line.rstrip("\n")) :])
            i += 1
            continue
        if ZITATE_8.match(line):
            i = skip_zitate_content(
                lines,
                i + 1,
                [CHUNK_8, ASPECT, re.compile(r"^    chunk_id:")],
            )
            continue
        if ZITATE_4.match(line):
            i = skip_zitate_content(lines, i + 1, [FIELD_KEY])
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
    text = text.replace("    quotes: zitate", "    references: references")
    lines = text.splitlines(keepends=True)
    new_lines = strip_zitate_blocks(lines)
    path.write_text("".join(new_lines), encoding="utf-8")
    remaining = sum(1 for ln in new_lines if "zitate" in ln)
    print(f"Updated {path}; remaining 'zitate' lines: {remaining}")
    return 0 if remaining == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
