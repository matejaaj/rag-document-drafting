from __future__ import annotations
from typing import Protocol
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Tuple


@dataclass
class DocumentTypeReportParams:
    from_ts: datetime
    to_ts: datetime
    document_type_id: Optional[int]
    include_total: bool
    sort_key: str = "document_type_name"
    sort_direction: str = "asc"
    timezone_name: Optional[str] = None
    locale: str = "sr-RS"


@dataclass
class DocumentReportSelection:
    section_id: int
    seq_no: Optional[int] = None


# (row key, column header), in display order
DOCUMENT_TYPE_REPORT_COLUMNS: Tuple[Tuple[str, str], ...] = (
    ("document_type_name", "Tip dokumenta"),
    ("num_executions", "Broj Izvršavanja"),
    ("avg_duration_ms", "Prosecno trajanje (ms)"),
    ("avg_input_tokens", "Prosecan broj  input tokena"),
    ("avg_output_tokens", "Prosecan broj output tokena"),
    ("total_cost_usd", "Ukupan trošak ($)"),
    ("avg_cost_usd", "Trošak po izvrsenju. ($)"),
    ("error_rate", "Greške (%)"),
    ("rating_count", "Broj Ocena"),
    ("rating_avg", "Prosecna ocena"),
    ("rating_median", "Medijan ocena"),
)


class PdfEngine(Protocol):

    def html_to_pdf(self, html: str) -> bytes:
        ...
