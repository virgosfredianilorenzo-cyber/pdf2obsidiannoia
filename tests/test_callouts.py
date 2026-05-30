from callouts import detect_callouts

def test_note_callout():
    result = detect_callouts("Note: Ce point est important.")
    assert "> [!NOTE] Note" in result
    assert "> Ce point est important." in result

def test_remarque_callout():
    result = detect_callouts("Remarque: À ne pas oublier.")
    assert "> [!NOTE] Remarque" in result

def test_warning_callout():
    result = detect_callouts("Attention: Procédure irréversible.")
    assert "> [!WARNING] Attention" in result

def test_danger_callout():
    result = detect_callouts("Danger: Risque élevé.")
    assert "> [!WARNING] Danger" in result

def test_important_callout():
    result = detect_callouts("Important: Lire attentivement.")
    assert "> [!IMPORTANT] Important" in result

def test_example_callout():
    result = detect_callouts("Exemple: Voici un cas pratique.")
    assert "> [!EXAMPLE] Exemple" in result

def test_tip_callout():
    result = detect_callouts("Conseil: Utiliser un bon outil.")
    assert "> [!TIP] Conseil" in result

def test_case_insensitive():
    result = detect_callouts("NOTE: Texte.")
    assert "> [!NOTE]" in result

def test_no_callout_unchanged():
    text = "Ceci est un paragraphe normal sans callout."
    assert detect_callouts(text) == text

def test_heading_not_converted():
    text = "## Note sur la méthode"
    assert detect_callouts(text) == text

def test_multiline_callout_continuation():
    text = "Note: Première ligne.\nSuite du texte.\n\nParagraphe suivant."
    result = detect_callouts(text)
    assert "> Suite du texte." in result
    assert "Paragraphe suivant." in result
    assert "> [!NOTE]" in result

def test_multiple_callouts():
    text = "Note: Premier.\n\nAttention: Deuxième."
    result = detect_callouts(text)
    assert "> [!NOTE]" in result
    assert "> [!WARNING]" in result
