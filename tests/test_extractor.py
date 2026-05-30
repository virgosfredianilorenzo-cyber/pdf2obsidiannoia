from extractor import _clean, _detect_level, _table_to_md

def test_clean_multiple_spaces():
    assert _clean("hello   world") == "hello world"

def test_clean_strips():
    assert _clean("  hello  ") == "hello"

def test_detect_level_largest():
    assert _detect_level(18.0, [18.0, 14.0, 12.0]) == 1

def test_detect_level_second():
    assert _detect_level(14.0, [18.0, 14.0, 12.0]) == 2

def test_detect_level_third():
    assert _detect_level(12.0, [18.0, 14.0, 12.0]) == 3

def test_detect_level_body():
    assert _detect_level(10.0, [18.0, 14.0, 12.0]) == 0

def test_detect_level_empty_sizes():
    assert _detect_level(12.0, []) == 0

def test_table_to_md_basic():
    table = [["Col1", "Col2"], ["A", "B"]]
    result = _table_to_md(table)
    assert "| Col1 | Col2 |" in result
    assert "|---|---|" in result
    assert "| A | B |" in result

def test_table_to_md_empty():
    assert _table_to_md([]) == ""

def test_table_to_md_none_cells():
    table = [["A", None], ["B", "C"]]
    result = _table_to_md(table)
    assert "|" in result
