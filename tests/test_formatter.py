import tempfile
from pathlib import Path
from formatter import sanitize_filename, save_markdown


def test_sanitize_basic():
    assert sanitize_filename("Mon Document") == "Mon_Document"

def test_sanitize_removes_special():
    result = sanitize_filename("Rapport: 2024!")
    assert ":" not in result
    assert "!" not in result

def test_sanitize_empty_returns_document():
    assert sanitize_filename("") == "document"

def test_sanitize_truncates_at_80():
    result = sanitize_filename("A" * 100)
    assert len(result) <= 80

def test_save_creates_file():
    with tempfile.TemporaryDirectory() as d:
        result = save_markdown("# Hello", "Test Doc", d)
        assert Path(result["output_path"]).exists()

def test_save_filename_ends_with_md():
    with tempfile.TemporaryDirectory() as d:
        result = save_markdown("# Hello", "Test", d)
        assert result["filename"].endswith(".md")

def test_save_returns_stats():
    with tempfile.TemporaryDirectory() as d:
        result = save_markdown("# Hello\nWorld", "Test", d)
        assert result["chars"] > 0
        assert result["lines"] > 0

def test_save_vault_missing_returns_warning(tmp_path):
    result = save_markdown("# Hello", "Test", str(tmp_path), "/nonexistent/vault")
    assert result["vault_path"] is None
    assert "vault_warning" in result

def test_save_vault_exists_copies_file(tmp_path):
    vault = tmp_path / "vault"
    vault.mkdir()
    out = tmp_path / "output"
    result = save_markdown("# Hello", "Test", str(out), str(vault))
    assert result["vault_path"] is not None
    assert Path(result["vault_path"]).exists()
