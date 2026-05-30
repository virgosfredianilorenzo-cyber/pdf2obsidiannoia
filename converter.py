from __future__ import annotations
from datetime import datetime
from extractor import PDFDocument, PDFSection
from callouts import detect_callouts
from wikilinks import add_wikilinks


def build_frontmatter(doc: PDFDocument, source_filename: str) -> str:
    title = doc.title.replace('"', '\\"')
    lines = [
        "---",
        f'title: "{title}"',
    ]
    if doc.author:
        lines.append(f"author: {doc.author}")
    lines += [
        f"date_extraction: {datetime.now().strftime('%Y-%m-%dT%H:%M:%S')}",
        f"source: {source_filename}",
        f"pages: {doc.pages}",
        "tags: []",
        "mode: obsidian-noia",
        "---",
    ]
    return "\n".join(lines)


def build_toc(sections: list[PDFSection]) -> str:
    headings = [s for s in sections if s.level in (1, 2, 3) and not s.is_table]
    if not headings:
        return ""
    lines = ["## Table des matières"]
    for s in headings:
        indent = "  " * (s.level - 1)
        lines.append(f"{indent}- [[#{s.text.strip()}]]")
    return "\n".join(lines)


def build_body(sections: list[PDFSection]) -> str:
    prefix_map = {1: "# ", 2: "## ", 3: "### ", 0: ""}
    parts: list[str] = []
    for s in sections:
        prefix = prefix_map.get(s.level, "") if not s.is_table else ""
        parts.append(prefix + s.text)
    return "\n\n".join(parts)


def convert(
    doc: PDFDocument,
    source_filename: str,
    enable_wikilinks: bool = True,
    enable_callouts: bool = True,
    enable_toc: bool = True,
) -> str:
    frontmatter = build_frontmatter(doc, source_filename)
    toc = build_toc(doc.sections) if enable_toc else ""
    body = build_body(doc.sections)

    if enable_callouts:
        body = detect_callouts(body)

    parts = [frontmatter]
    if toc:
        parts.append(toc)
    parts.append(body)
    full_text = "\n\n".join(parts)

    if enable_wikilinks:
        bold_phrases = {
            s.text.strip()
            for s in doc.sections
            if s.is_bold and s.level == 0 and len(s.text) < 80
        }
        full_text = add_wikilinks(full_text, bold_phrases)

    return full_text
