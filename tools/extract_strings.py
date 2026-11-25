"""Extract translatable UI strings from the depthmapX GUI sources.

This mirrors what lupdate does (tr("...") plus Qt Designer .ui <string> entries)
so that we can build and check the Chinese dictionary offline, without a Qt SDK.
The authoritative context/message mapping is still produced by lupdate in CI;
this script only needs the *set* of source strings.

Usage:  python tools/extract_strings.py [--json out.json]
"""

from __future__ import annotations

import html
import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUI_DIR = ROOT / "depthmapX"

# tr("literal") / tr("a" "b") / QObject::tr("literal")
TR_RE = re.compile(r'\btr\s*\(\s*((?:"(?:[^"\\]|\\.)*"\s*)+)')
# QCoreApplication::translate("context", "source")
TRANSLATE_RE = re.compile(
    r'\btranslate\s*\(\s*"(?:[^"\\]|\\.)*"\s*,\s*((?:"(?:[^"\\]|\\.)*"\s*)+)'
)
STRING_LIT_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')
UI_STRING_RE = re.compile(r"<string>([^<]*)</string>")
# tr("...") with a trailing comma means tr(source, disambiguation) - fine, source only.
# tr() without any literal is dynamic and cannot be translated statically.
BARE_TR_RE = re.compile(r"\btr\s*\(\s*[^\"\s)]")


def unescape(lit: str) -> str:
    """Turn the raw inside of a C string literal into the actual text."""
    out = []
    i = 0
    while i < len(lit):
        ch = lit[i]
        if ch == "\\" and i + 1 < len(lit):
            nxt = lit[i + 1]
            mapping = {"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\", "'": "'"}
            if nxt in mapping:
                out.append(mapping[nxt])
                i += 2
                continue
            out.append(nxt)
            i += 2
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def join_literals(blob: str) -> str:
    """Concatenate adjacent string literals: "a" "b" -> "ab"."""
    return "".join(unescape(m.group(1)) for m in STRING_LIT_RE.finditer(blob))


def collect() -> tuple[Counter, list[str]]:
    counts: Counter = Counter()
    problems: list[str] = []

    for path in sorted(GUI_DIR.rglob("*")):
        if path.suffix not in {".cpp", ".h", ".hpp", ".ui"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.relative_to(ROOT).as_posix()

        if path.suffix == ".ui":
            # lupdate parses .ui as XML, so entities (&quot; &amp; ...) arrive
            # at the translator already decoded - decode them here as well.
            for m in UI_STRING_RE.finditer(text):
                counts[html.unescape(m.group(1))] += 1
            continue

        for regex in (TR_RE, TRANSLATE_RE):
            for m in regex.finditer(text):
                src = join_literals(m.group(1))
                if src:
                    counts[src] += 1

        line = text.count("\n")
        n_bare = len(BARE_TR_RE.findall(text))
        if n_bare:
            problems.append(f"{rel}: {n_bare} 处 tr() 不带字符串字面量（动态拼接，需人工看）")

    return counts, problems


def main() -> int:
    counts, problems = collect()
    items = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))

    print(f"唯一文案: {len(items)} 条    总出现: {sum(counts.values())} 处")
    print("--- 未带字面量的 tr() ---")
    for p in problems:
        print("  " + p)

    if "--json" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--json") + 1])
        out.write_text(
            json.dumps({k: "" for k, _ in items}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"已写出骨架: {out}")

    print("--- 出现次数最多的 15 条 ---")
    for src, n in items[:15]:
        print(f"  {n:4d}  {src!r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
