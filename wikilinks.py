from __future__ import annotations
import re

STOP_LIST: frozenset[str] = frozenset({
    "le", "la", "les", "l", "un", "une", "des", "du", "the", "a", "an",
    "de", "en", "au", "aux", "et", "ou", "mais", "donc", "or", "ni",
    "car", "ce", "cet", "cette", "ces", "il", "elle", "ils", "elles",
    "je", "tu", "nous", "vous", "on", "que", "qui", "quand", "où",
    "comme", "par", "pour", "avec", "sans", "sur", "sous", "dans",
    "entre", "vers", "chez", "se", "si", "ne", "pas", "plus", "très",
    "bien", "aussi", "même", "tout", "tous", "toute", "toutes",
    "son", "sa", "ses", "mon", "ma", "mes", "ton", "ta", "tes",
    "leur", "leurs", "its", "his", "her", "our", "your", "their",
    "this", "that", "these", "those", "is", "are", "was", "were",
    "be", "been", "being", "have", "has", "had", "do", "does", "did",
    "will", "would", "could", "should", "may", "might", "shall", "can",
    "not", "no", "nor", "also", "from", "with", "into", "then", "than",
    "when", "dont", "lequel", "laquelle", "lesquels",
    "lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche",
    "janvier", "février", "mars", "avril", "mai", "juin", "juillet",
    "août", "septembre", "octobre", "novembre", "décembre",
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "june", "july", "august",
    "september", "october", "november", "december",
})

_PROPER_NOUN_RE = re.compile(r"(?<!\[)\b([A-ZÀÂÄÉÈÊËÎÏÔÙÛÜÇ][a-zà-ÿ]{1,})\b(?!\])")
_CODE_BLOCK_RE = re.compile(r"(```[\s\S]*?```)", re.DOTALL)


def _is_proper_noun_candidate(word: str) -> bool:
    return (
        len(word) >= 2
        and word[0].isupper()
        and not word.isupper()
        and word.lower() not in STOP_LIST
    )


def _split_frontmatter(text: str) -> tuple[str, str]:
    if not text.startswith("---"):
        return "", text
    end = text.find("\n---", 3)
    if end == -1:
        return "", text
    return text[: end + 4], text[end + 4:]


def add_wikilinks(text: str, bold_phrases: set[str]) -> str:
    """Adds [[wikilinks]] to body text. Frontmatter and code blocks are untouched."""
    frontmatter, body = _split_frontmatter(text)
    parts = _CODE_BLOCK_RE.split(body)

    processed: list[str] = []
    for part in parts:
        if part.startswith("```"):
            processed.append(part)
            continue

        for phrase in sorted(bold_phrases, key=len, reverse=True):
            phrase = phrase.strip()
            if not phrase or len(phrase) >= 80:
                continue
            escaped = re.escape(phrase)
            part = re.sub(rf"(?<!\[)\b{escaped}\b(?!\])", f"[[{phrase}]]", part)

        result_lines: list[str] = []
        for line in part.split("\n"):
            if re.match(r"^#+\s", line) or re.match(r"\s*-\s+\[\[#", line) or line.startswith(">"):
                result_lines.append(line)
                continue
            line = _PROPER_NOUN_RE.sub(
                lambda m: f"[[{m.group(0)}]]" if _is_proper_noun_candidate(m.group(0)) else m.group(0),
                line,
            )
            result_lines.append(line)

        processed.append("\n".join(result_lines))

    return frontmatter + "".join(processed)
