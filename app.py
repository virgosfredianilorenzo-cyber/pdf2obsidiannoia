from __future__ import annotations
import logging
import re
import tempfile
from pathlib import Path

import fitz
import uvicorn
import yaml
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from converter import convert
from extractor import extract
from formatter import save_markdown

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

CONFIG_PATH = Path(__file__).parent / "config.yaml"
with open(CONFIG_PATH, encoding="utf-8") as _f:
    CONFIG = yaml.safe_load(_f)

app = FastAPI(title="pdf2obsidiannoia", version="1.0.0")

static_dir = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTMLResponse(content=(static_dir / "index.html").read_text(encoding="utf-8"))


@app.post("/api/convert")
async def convert_pdf(
    file: UploadFile = File(...),
    language: str = Form("fr"),
    enable_wikilinks: bool = Form(True),
    enable_callouts: bool = Form(True),
    enable_toc: bool = Form(True),
    vault_path: str = Form(""),
):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Fichier PDF requis")

    output_dir = CONFIG.get("output_dir", "./output")
    vault = vault_path.strip() or CONFIG.get("vault_path") or None

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        doc_check = fitz.open(tmp_path)
        if doc_check.needs_pass:
            doc_check.close()
            raise HTTPException(status_code=400, detail="PDF protégé par mot de passe")
        is_scanned = all(not page.get_text().strip() for page in doc_check)
        doc_check.close()

        pdf_doc = extract(tmp_path)
        warnings: list[str] = []
        if is_scanned:
            warnings.append("PDF scanné détecté — contenu texte limité ou absent")

        md_text = convert(
            pdf_doc,
            source_filename=file.filename,
            enable_wikilinks=enable_wikilinks,
            enable_callouts=enable_callouts,
            enable_toc=enable_toc,
        )

        save_info = save_markdown(md_text, title=pdf_doc.title, output_dir=output_dir, vault_path=vault)
        if "vault_warning" in save_info:
            warnings.append(save_info["vault_warning"])

        wikilink_count = len(re.findall(r"\[\[(?!#)[^\]]+\]\]", md_text))
        callout_count = len(re.findall(r"^> \[!", md_text, re.MULTILINE))

        return JSONResponse({
            "success": True,
            "filename": save_info["filename"],
            "output_path": save_info["output_path"],
            "vault_path": save_info.get("vault_path"),
            "markdown": md_text,
            "warnings": warnings,
            "stats": {
                "pages": pdf_doc.pages,
                "sections": len(pdf_doc.sections),
                "wikilinks": wikilink_count,
                "callouts": callout_count,
                "chars": save_info["chars"],
                "lines": save_info["lines"],
            },
        })

    except HTTPException:
        raise
    except Exception:
        logging.exception("Erreur conversion")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")
    finally:
        Path(tmp_path).unlink(missing_ok=True)


@app.get("/api/download/{filename}")
async def download(filename: str):
    output_dir = Path(CONFIG.get("output_dir", "./output")).resolve()
    file_path = (output_dir / filename).resolve()
    if not str(file_path).startswith(str(output_dir) + "/"):
        raise HTTPException(status_code=400, detail="Accès refusé")
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Fichier introuvable")
    return FileResponse(str(file_path), media_type="text/markdown", filename=file_path.name)


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", CONFIG.get("port", 8001)))
    print(f"\n  pdf2obsidiannoia — http://localhost:{port}\n")
    uvicorn.run(app, host="127.0.0.1", port=port, reload=False)
