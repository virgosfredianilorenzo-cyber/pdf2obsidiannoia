from __future__ import annotations
import re
import shutil
from pathlib import Path


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\s\-àâäéèêëîïôùûüç]", "", name, flags=re.UNICODE)
    name = re.sub(r"\s+", "_", name.strip())
    return name[:80] or "document"


def save_markdown(
    md_text: str,
    title: str,
    output_dir: str | Path,
    vault_path: str | Path | None = None,
) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = sanitize_filename(title) + ".md"
    output_path = output_dir / filename
    output_path.write_text(md_text, encoding="utf-8")

    result: dict = {
        "filename": filename,
        "output_path": str(output_path),
        "vault_path": None,
        "chars": len(md_text),
        "lines": md_text.count("\n"),
    }

    if vault_path:
        vault = Path(vault_path).expanduser()
        if vault.exists():
            dest = vault / filename
            shutil.copy2(output_path, dest)
            result["vault_path"] = str(dest)
        else:
            result["vault_warning"] = f"Vault introuvable : {vault_path}"

    return result
