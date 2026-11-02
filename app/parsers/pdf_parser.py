from pathlib import Path

import fitz


def extract_pdf_text(path: Path) -> tuple[str, dict]:
    """Best-effort local text extraction for storage/provenance.

    The original PDF is still sent directly to Gemini; this local extraction
    must not prevent Gemini from analyzing scanned/image-heavy PDFs.
    """
    doc = fitz.open(path)
    pages: list[str] = []
    for index, page in enumerate(doc, start=1):
        text = page.get_text("text").strip()
        if text:
            pages.append(f"[Page {index}]\n{text}")
    metadata = {
        "page_count": len(doc),
        "text_pages": len(pages),
        "scan_or_image_only": len(pages) == 0,
        "pdf_metadata": doc.metadata or {},
    }
    doc.close()
    text = "\n\n".join(pages).strip()
    if not text:
        text = "[Local text extraction produced no text. The original PDF was sent directly to Gemini for multimodal analysis.]"
    return text, metadata
