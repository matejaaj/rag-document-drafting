from __future__ import annotations
import re
from statistics import median
from typing import List

import pymupdf

from .protocol import DocumentParser, ParsedDocument, DocSection

_HEADING_HINTS = r"(sadržaj|uvod|sažetak|metodologija|ciljevi|rezultati|diskusija|zaključak|prilog|bibliografija)"
_HEADING_REGEX = re.compile(rf"^(\d+(\.\d+)*)\s+|^{_HEADING_HINTS}\b", re.I)

def _clean_line(line_text: str) -> str:
    line_text = line_text.replace("\xa0", " ").strip()
    line_text = re.sub(r"-\n", "", line_text)
    line_text = re.sub(r"[ \t]+", " ", line_text)
    return line_text

class PdfDocumentParser(DocumentParser):
    def can_handle(self, filename: str, mime_type: str) -> bool:
        extension = (filename.rsplit(".", 1)[-1] or "").lower()
        return extension == "pdf" or ("pdf" in (mime_type or "").lower())

    def parse(self, content: bytes, filename: str) -> ParsedDocument:
        pdf_document = pymupdf.open(stream=content, filetype="pdf")
        sections: List[DocSection] = []
        current_section_name = "Opšte"
        current_section_lines: List[str] = []
        body_font_sizes: List[float] = []

        def flush_current_section():
            nonlocal current_section_lines
            section_text = "\n".join(current_section_lines).strip()
            if section_text:
                sections.append(DocSection(current_section_name, section_text))
            current_section_lines = []

        for page in pdf_document:
            page_layout = page.get_text("dict")
            for block in page_layout.get("blocks", []):
                for line in block.get("lines", []):
                    spans = line.get("spans", [])
                    if not spans:
                        continue
                    line_text = _clean_line("".join(span.get("text", "") for span in spans))
                    if not line_text:
                        continue
                    font_size = max(float(span.get("size", 0.0)) for span in spans)

                    if 6.0 < font_size < 22.0 and len(line_text) > 30:
                        body_font_sizes.append(font_size)
                    baseline_font_size = median(body_font_sizes) if body_font_sizes else 10.0

                    looks_like_heading = (
                        font_size >= baseline_font_size * 1.25
                        or (line_text.isupper() and 3 <= len(line_text) <= 80)
                        or bool(_HEADING_REGEX.match(line_text))
                    )

                    if looks_like_heading:
                        flush_current_section()
                        current_section_name = line_text[:120]
                    else:
                        current_section_lines.append(line_text)

        flush_current_section()

        if not sections:
            plain_text = "\n".join(page.get_text("text").strip() for page in pdf_document).strip()
            if plain_text:
                sections.append(DocSection("Opšte", plain_text))
            else:
                sections.append(DocSection("Opšte", ""))

        metadata = {
            "pages": len(pdf_document),
            "title": pdf_document.metadata.get("title") if pdf_document.metadata else None,
        }
        pdf_document.close()
        return ParsedDocument(sections=sections, metadata=metadata)
