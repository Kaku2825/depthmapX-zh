"""Fill a .ts catalogue produced by lupdate with the Chinese dictionary.

The dictionary is keyed by the *source* string, so it does not depend on the
context lupdate assigns; that keeps the translation file maintainable even when
upstream refactors classes around.

Usage:  python tools/fill_ts.py i18n/depthmapX_zh_CN.ts translations/depthmapX_zh_CN.json
"""

from __future__ import annotations

import json
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def unescape(text: str) -> str:
    """Undo the \\n / \\t / \\\" escapes lupdate uses inside <source>."""
    out = []
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "\\" and i + 1 < len(text):
            nxt = text[i + 1]
            if nxt == "n":
                out.append("\n")
                i += 2
                continue
            if nxt == "t":
                out.append("\t")
                i += 2
                continue
            if nxt == "r":
                out.append("\r")
                i += 2
                continue
            if nxt in {'"', "'", "\\"}:
                out.append(nxt)
                i += 2
                continue
        out.append(ch)
        i += 1
    return "".join(out)


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    ts_path = Path(sys.argv[1])
    dict_path = Path(sys.argv[2])
    zh = json.loads(dict_path.read_text(encoding="utf-8"))

    tree = ET.parse(ts_path)
    root = tree.getroot()

    filled = 0
    empty = 0
    unfilled: list[str] = []

    for ctx in root.findall("context"):
        for message in ctx.findall("message"):
            src_el = message.find("source")
            tr_el = message.find("translation")
            if src_el is None or tr_el is None:
                continue
            raw = src_el.text or ""
            # lupdate may write newlines escaped; accept both spellings.
            candidates = [raw, unescape(raw)]
            value = None
            for c in candidates:
                if c in zh and zh[c]:
                    value = zh[c]
                    break
            if message.get("numerus") == "yes":
                # No plural forms are expected in this project; leave untouched.
                continue
            if value is None:
                empty += 1
                if len(raw) > 1:
                    unfilled.append(raw.replace("\n", "\\n"))
                continue
            tr_el.text = value
            for attr in list(tr_el.attrib):
                del tr_el.attrib[attr]
            filled += 1

    tree.write(ts_path, encoding="utf-8", xml_declaration=True)

    print(f"填充 {filled} 条，未填 {empty} 条")
    if unfilled:
        shown = sorted(set(unfilled))[:40]
        print("未翻译（原始文本）示例:")
        for s in shown:
            print(f"    {s}")

    if filled < 400:
        print("::error::填充数量异常偏低，检查 lupdate 输出或字典键是否匹配")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
