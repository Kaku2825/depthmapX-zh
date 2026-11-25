"""Merge the translation parts, then validate against the extracted strings.

Checks performed:
  * every key in the merged dictionary actually exists in the sources
    (a misspelled key would silently never be applied)
  * placeholder count/names (%1..%9) identical between source and translation
  * accelerator markers (&X) are preserved
  * trailing/leading spaces and newline counts are preserved
  * JSON is valid and has no duplicate keys across parts

Usage:  python tools/build_zh.py [--out translations/depthmapX_zh_CN.json]
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_strings import collect  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
TRANS_DIR = ROOT / "translations"
PARTS = sorted(TRANS_DIR.glob("_part*.json"))
PLACEHOLDER_RE = re.compile(r"%[1-9]")


def load_parts() -> dict[str, str]:
    merged: dict[str, str] = {}
    dupes: list[str] = []
    for part in PARTS:
        data = json.loads(part.read_text(encoding="utf-8"))
        for k, v in data.items():
            if k in merged and merged[k] != v:
                dupes.append(k)
            merged[k] = v
    if dupes:
        print(f"[注意] {len(dupes)} 条在多个分片中被重复定义（已取后者）")
        for k in dupes[:10]:
            print(f"    {k!r}")
    return merged


def main() -> int:
    sources, _ = collect()
    zh = load_parts()
    out_path = TRANS_DIR / "depthmapX_zh_CN.json"
    if "--out" in sys.argv:
        out_path = Path(sys.argv[sys.argv.index("--out") + 1])
    out_path.write_text(
        json.dumps(dict(sorted(zh.items())), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    errors: list[str] = []
    warnings: list[str] = []

    # 1. keys that do not exist in the sources
    for key in zh:
        if key not in sources:
            warnings.append(f"键在源码中不存在（检查拼写）: {key!r}")

    # 2. placeholder / structure checks
    for src, dst in zh.items():
        sp, dp = PLACEHOLDER_RE.findall(src), PLACEHOLDER_RE.findall(dst)
        if sp != dp:
            errors.append(f"占位符不一致: {src!r} -> {dst!r}  ({sp} vs {dp})")
        if src.count("&") and src.count("&") > dst.count("&"):
            errors.append(f"加速键丢失: {src!r} -> {dst!r}")
        if src.endswith("\n") != dst.endswith("\n"):
            warnings.append(f"结尾换行不一致: {src!r} -> {dst!r}")
        if src.startswith(" ") != dst.startswith(" "):
            warnings.append(f"开头空格不一致: {src!r} -> {dst!r}")
        if src.endswith(" ") != dst.endswith(" "):
            warnings.append(f"结尾空格不一致: {src!r} -> {dst!r}")

    # 3. coverage of UI-ish strings
    def looks_like_ui(text: str) -> bool:
        if text.startswith((":/", "<html", "<!DOCTYPE", "<RCC")):
            return False
        if len(text.strip()) < 2:
            return False
        if not re.search(r"[A-Za-z]{2}", text):
            return False
        return True

    untranslated = [s for s in sources if s not in zh and looks_like_ui(s)]

    print(f"分片数: {len(PARTS)}    词典条目: {len(zh)}    源码文案: {len(sources)}")
    print(f"已翻译: {sum(1 for s in sources if s in zh)} / {len(sources)}")
    print(f"疑似漏翻: {len(untranslated)}")
    if untranslated:
        for s in sorted(untranslated, key=lambda t: (-sources[t], t))[:60]:
            print(f"    ({sources[s]:3d}) {s!r}")
    if warnings:
        print(f"警告 {len(warnings)} 条:")
        for w in warnings[:20]:
            print("    " + w)
    if errors:
        print(f"错误 {len(errors)} 条:")
        for e in errors:
            print("    " + e)
    print(f"输出: {out_path}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
