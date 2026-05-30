from extractor import PDFDocument, PDFSection
from converter import build_frontmatter, build_toc, build_body, convert


def _doc():
    doc = PDFDocument(title="Rapport Test", author="Jean Dupont", subject="", pages=5)
    doc.sections = [
        PDFSection(level=1, text="Introduction", page=1),
        PDFSection(level=2, text="Contexte", page=1),
        PDFSection(level=0, text="Note: Ce point est crucial.", page=1),
        PDFSection(level=0, text="Texte normal ici.", page=2, is_bold=False),
        PDFSection(level=0, text="Tableau ci-dessous.", page=2, is_table=True),
    ]
    return doc


def test_frontmatter_has_title():
    fm = build_frontmatter(_doc(), "test.pdf")
    assert 'title: "Rapport Test"' in fm

def test_frontmatter_has_source():
    fm = build_frontmatter(_doc(), "test.pdf")
    assert "source: test.pdf" in fm

def test_frontmatter_has_pages():
    fm = build_frontmatter(_doc(), "test.pdf")
    assert "pages: 5" in fm

def test_frontmatter_has_mode():
    fm = build_frontmatter(_doc(), "test.pdf")
    assert "mode: obsidian-noia" in fm

def test_frontmatter_wrapped_in_dashes():
    fm = build_frontmatter(_doc(), "test.pdf")
    assert fm.startswith("---")
    assert fm.endswith("---")

def test_toc_has_table_header():
    toc = build_toc(_doc().sections)
    assert "## Table des matières" in toc

def test_toc_h1_present():
    toc = build_toc(_doc().sections)
    assert "[[#Introduction]]" in toc

def test_toc_h2_indented():
    toc = build_toc(_doc().sections)
    lines = toc.split("\n")
    h2_line = next(l for l in lines if "Contexte" in l)
    assert h2_line.startswith("  ")

def test_toc_empty_when_no_headings():
    doc = PDFDocument(title="T", author="", subject="", pages=1)
    doc.sections = [PDFSection(level=0, text="Texte.", page=1)]
    assert build_toc(doc.sections) == ""

def test_build_body_has_h1_prefix():
    body = build_body(_doc().sections)
    assert "# Introduction" in body

def test_build_body_has_h2_prefix():
    body = build_body(_doc().sections)
    assert "## Contexte" in body

def test_convert_starts_with_frontmatter():
    result = convert(_doc(), "test.pdf")
    assert result.startswith("---")

def test_convert_callouts_on():
    result = convert(_doc(), "test.pdf", enable_callouts=True)
    assert "> [!NOTE]" in result

def test_convert_callouts_off():
    result = convert(_doc(), "test.pdf", enable_callouts=False)
    assert "> [!NOTE]" not in result

def test_convert_toc_on():
    result = convert(_doc(), "test.pdf", enable_toc=True)
    assert "## Table des matières" in result

def test_convert_toc_off():
    result = convert(_doc(), "test.pdf", enable_toc=False)
    assert "## Table des matières" not in result

def test_convert_wikilinks_off():
    result = convert(_doc(), "test.pdf", enable_wikilinks=False)
    body = result.split("---\n\n", 1)[-1]
    assert "[[Jean" not in body
