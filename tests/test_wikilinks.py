from wikilinks import add_wikilinks, _is_proper_noun_candidate, STOP_LIST

def test_stop_list_words_rejected():
    assert not _is_proper_noun_candidate("Le")
    assert not _is_proper_noun_candidate("La")
    assert not _is_proper_noun_candidate("The")
    assert not _is_proper_noun_candidate("Ces")

def test_proper_noun_accepted():
    assert _is_proper_noun_candidate("Paris")
    assert _is_proper_noun_candidate("Dupont")
    assert _is_proper_noun_candidate("Microsoft")

def test_allcaps_rejected():
    assert not _is_proper_noun_candidate("NATO")
    assert not _is_proper_noun_candidate("PDF")

def test_proper_noun_linked():
    text = "---\ntitle: test\n---\n\nLe rapport concerne Paris et Lyon."
    result = add_wikilinks(text, set())
    assert "[[Paris]]" in result
    assert "[[Lyon]]" in result

def test_bold_phrase_linked():
    text = "---\ntitle: test\n---\n\nLe rapport de Jean Dupont est disponible."
    result = add_wikilinks(text, {"Jean Dupont"})
    assert "[[Jean Dupont]]" in result

def test_frontmatter_untouched():
    text = "---\ntitle: Paris\nauthor: Jean\n---\n\nContenu."
    result = add_wikilinks(text, set())
    fm_end = result.index("---", 3) + 3
    frontmatter = result[:fm_end]
    assert "[[" not in frontmatter

def test_code_block_untouched():
    text = "---\ntitle: test\n---\n\n```python\nParis = 'city'\n```"
    result = add_wikilinks(text, set())
    assert "[[Paris]]" not in result

def test_no_double_wrapping():
    text = "---\ntitle: test\n---\n\n[[Paris]] est une ville."
    result = add_wikilinks(text, set())
    assert "[[[[Paris]]]]" not in result
    assert result.count("[[Paris]]") == 1

def test_toc_line_untouched():
    text = "---\ntitle: t\n---\n\n- [[#Introduction]]\n"
    result = add_wikilinks(text, set())
    assert "[[[[#Introduction]]]]" not in result

def test_no_text_means_no_change():
    text = "---\ntitle: t\n---\n\naucun nom propre ici."
    result = add_wikilinks(text, set())
    assert "[[" not in result.split("---\n\n", 1)[1]
