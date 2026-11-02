from pathlib import Path

from docx import Document


def parse_docx(path: Path) -> tuple[str, dict]:
    document = Document(path)
    parts: list[str] = []
    paragraph_number = 0
    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue
        paragraph_number += 1
        style = paragraph.style.name if paragraph.style else ""
        if style and style.lower().startswith("heading"):
            parts.append(f"[Section: {text}] [Paragraph: {paragraph_number}]")
        else:
            parts.append(f"[Paragraph: {paragraph_number}] {text}")

    for table_index, table in enumerate(document.tables, start=1):
        rows: list[str] = []
        for row in table.rows:
            rows.append(" | ".join(cell.text.strip() for cell in row.cells))
        if rows:
            parts.append(f"[Table {table_index}]\n" + "\n".join(rows))

    text = "\n\n".join(parts).strip()
    if not text:
        raise ValueError("The DOCX does not contain readable text.")

    return text, {"paragraph_count": paragraph_number, "table_count": len(document.tables)}
