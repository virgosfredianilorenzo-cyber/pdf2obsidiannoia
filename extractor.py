from __future__ import annotations
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
import fitz
import pdfplumber


@dataclass
class PDFSection:
    level: int        # 1=H1, 2=H2, 3=H3, 0=paragraphe
    text: str
    page: int
    is_table: bool = False
    is_bold: bool = False


@dataclass
class PDFDocument:
    title: str
    author: str
    subject: str
    pages: int
    sections: list[PDFSection] = field(default_factory=list)
    raw_text: str = ""


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _detect_level(span_size: float, sizes: list[float]) -> int:
    if not sizes:
        return 0
    sorted_sizes = sorted(set(sizes), reverse=True)
    if span_size >= sorted_sizes[0] * 0.95:
        return 1
    if len(sorted_sizes) > 1 and span_size >= sorted_sizes[1] * 0.95:
        return 2
    if len(sorted_sizes) > 2 and span_size >= sorted_sizes[2] * 0.95:
        return 3
    return 0


def _table_to_md(table: list[list[Optional[str]]]) -> str:
    if not table:
        return ""
    rows = []
    for i, row in enumerate(table):
        cells = [str(c or "").replace("\n", " ").strip() for c in row]
        rows.append("| " + " | ".join(cells) + " |")
        if i == 0:
            rows.append("|" + "|".join(["---"] * len(cells)) + "|")
    return "\n".join(rows)


def extract(pdf_path: str | Path) -> PDFDocument:
    pdf_path = Path(pdf_path)
    doc_fitz = fitz.open(str(pdf_path))
    meta = doc_fitz.metadata or {}
    pdf_doc = PDFDocument(
        title=meta.get("title") or pdf_path.stem,
        author=meta.get("author") or "",
        subject=meta.get("subject") or "",
        pages=len(doc_fitz),
    )

    all_sizes: list[float] = []
    for page in doc_fitz:
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    if span.get("flags", 0) & 16 or span.get("size", 0) > 11:
                        all_sizes.append(round(span["size"], 1))

    size_freq = Counter(all_sizes)
    top_sizes = [s for s, _ in size_freq.most_common(4)]

    raw_parts: list[str] = []
    for page_num, page in enumerate(doc_fitz, start=1):
        for block in page.get_text("dict")["blocks"]:
            if block.get("type") != 0:
                continue
            for line in block.get("lines", []):
                line_text = ""
                line_size = 0.0
                is_bold = False
                for span in line.get("spans", []):
                    t = _clean(span.get("text", ""))
                    if not t:
                        continue
                    line_text += t + " "
                    line_size = max(line_size, span.get("size", 0))
                    if span.get("flags", 0) & 16:
                        is_bold = True
                line_text = line_text.strip()
                if not line_text or len(line_text) < 2:
                    continue
                raw_parts.append(line_text)
                level = _detect_level(line_size, top_sizes)
                if is_bold and level == 0 and len(line_text) < 120:
                    level = 3
                pdf_doc.sections.append(
                    PDFSection(level=level, text=line_text, page=page_num, is_bold=is_bold)
                )

    doc_fitz.close()

    with pdfplumber.open(str(pdf_path)) as plumb:
        for page_num, page in enumerate(plumb.pages, start=1):
            for table in page.extract_tables():
                if not table:
                    continue
                pdf_doc.sections.append(
                    PDFSection(level=0, text=_table_to_md(table), page=page_num, is_table=True)
                )

    pdf_doc.raw_text = "\n".join(raw_parts)
    return pdf_doc
