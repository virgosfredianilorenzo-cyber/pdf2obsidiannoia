from __future__ import annotations
import re

_CALLOUT_MAP: list[tuple[str, str]] = [
    (r"note|remarque|info", "NOTE"),
    (r"important|à retenir|a retenir", "IMPORTANT"),
    (r"attention|avertissement|warning|danger", "WARNING"),
    (r"exemple|example", "EXAMPLE"),
    (r"conseil|tip", "TIP"),
]

_COMBINED = "|".join(p for p, _ in _CALLOUT_MAP)
_PATTERN = re.compile(rf"^({_COMBINED})\s*:\s*(.*)$", re.IGNORECASE)


def _type_for(keyword: str) -> str:
    kw = keyword.lower()
    for pattern, callout_type in _CALLOUT_MAP:
        if re.fullmatch(pattern, kw, re.IGNORECASE):
            return callout_type
    return "NOTE"


def detect_callouts(text: str) -> str:
    """Converts 'Keyword: text' paragraphs into Obsidian callout blocks."""
    lines = text.split("\n")
    result: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if re.match(r"^#+\s", line):
            result.append(line)
            i += 1
            continue
        m = _PATTERN.match(line)
        if m:
            keyword, rest = m.group(1), m.group(2).strip()
            callout_type = _type_for(keyword)
            result.append(f"> [!{callout_type}] {keyword.capitalize()}")
            if rest:
                result.append(f"> {rest}")
            i += 1
            while i < len(lines) and lines[i].strip() and not re.match(r"^#+\s", lines[i]):
                result.append(f"> {lines[i]}")
                i += 1
        else:
            result.append(line)
            i += 1
    return "\n".join(result)
