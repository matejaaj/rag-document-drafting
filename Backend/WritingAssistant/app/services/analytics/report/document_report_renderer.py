from __future__ import annotations
from typing import List, Optional, Tuple
from html import escape
import os

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

APP_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
FONT_PATH = os.path.join(APP_DIR, "assets", "fonts", "DejaVuSans.ttf")

pdfmetrics.registerFont(TTFont("DejaVuSans", FONT_PATH))


SERBIAN_LATIN_TO_ASCII = str.maketrans({
    "č": "c", "ć": "c", "š": "s", "ž": "z", "đ": "dj",
    "Č": "C", "Ć": "C", "Š": "S", "Ž": "Z", "Đ": "Dj",
})
def _transliterate_to_ascii(text: Optional[str]) -> str:
    if not text:
        return ""
    return text.translate(SERBIAN_LATIN_TO_ASCII)


def _newlines_to_html_breaks(text: str) -> str:
    if text is None:
        return ""
    return "<br/>".join(escape(text).splitlines())


class DocumentReportHtmlRenderer:
    PAGE_SIZE = "A4"
    ORIENTATION = "portrait"

    def render(self, title: str, sections: List[Tuple[str, str]]) -> str:
        page_css = f"@page {{ size: {self.PAGE_SIZE} {self.ORIENTATION}; margin: 18mm 16mm; }}"

        ascii_title = _transliterate_to_ascii(title)

        sections_html = "\n".join(
            f"""
            <section class="doc-section">
              <h2 class="doc-section-title">{escape(_transliterate_to_ascii(section_title))}</h2>
              <div class="doc-text">{_newlines_to_html_breaks(_transliterate_to_ascii(section_text)) or "—"}</div>
            </section>
            """
            for section_title, section_text in sections
        )

        css = f"""
        {page_css}
        body {{ font-family: "DejaVuSans", sans-serif; color: #111; }}
        h1 {{ font-size: 20px; margin: 0 0 10px 0; }}
        .meta {{ font-size: 11px; color: #666; margin: 0 0 18px 0; }}
        .doc-section {{ page-break-inside: avoid; margin-bottom: 16px; }}
        .doc-section-title {{ font-size: 16px; margin: 0 0 6px 0; }}
        .doc-text {{ font-size: 12px; line-height: 1.45; white-space: normal; }}
        .footer {{ font-size: 10px; color: #666; margin-top: 20px; }}
        """

        return f"""
        <!doctype html>
        <html>
          <head>
            <meta charset="utf-8"/>
            <title>{escape(ascii_title)}</title>
            <style>{css}</style>
          </head>
          <body>
            <h1>{escape(ascii_title)}</h1>
            {sections_html}
            <div class="footer">© EcoLink 2025</div>
          </body>
        </html>
        """
