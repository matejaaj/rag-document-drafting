from __future__ import annotations
from typing import Any, Dict, List
from datetime import datetime
from zoneinfo import ZoneInfo

from app.services.analytics.report.report_models import DOCUMENT_TYPE_REPORT_COLUMNS, DocumentTypeReportParams

EMPTY_CELL = "—"


class DocumentTypeReportHtmlRenderer:
    CSS = """
    @page { size: A4 landscape; margin: 20mm 16mm; }
    body { font-family: Helvetica, Arial, sans-serif; color: #111; }
    h1 { font-size: 18px; margin: 0 0 6px 0; }
    .meta { font-size: 11px; color: #555; margin-bottom: 16px; }
    .meta .period { font-weight: 600; }
    .meta .filters { margin-top: 2px; }
    table { width: 100%; border-collapse: collapse; }
    th, td { font-size: 12px; padding: 8px 10px; border-bottom: 1px solid #e6e6e9; text-align: left; white-space: nowrap; }
    thead th { font-weight: 700; color: #555; background: #fafafc; }
    tr.total td { font-weight: 700; background: #f5f6fb; }
    .chip { display: inline-block; padding: 2px 10px; border: 1px solid #dadbe3; border-radius: 999px; background: #d3d3d9; }
    .footer { font-size: 10px; color: #666; margin-top: 12px; }
    """

    def render(self, rows: List[Dict[str, Any]], params: DocumentTypeReportParams) -> str:
        generated_at = datetime.now(tz=ZoneInfo(params.timezone_name)) if params.timezone_name else datetime.now()
        generated_at_text = generated_at.strftime("%d/%m/%Y %H:%M")
        period = f"{params.from_ts.strftime('%d/%m/%Y')} – {params.to_ts.strftime('%d/%m/%Y')}"

        filters = []
        if params.document_type_id is not None:
            filters.append(f"Tip dokumenta ID: {params.document_type_id}")

        header_cells = "".join(
            f'<th class="col-{key}">{label}</th>' for key, label in DOCUMENT_TYPE_REPORT_COLUMNS
        )

        table_rows = []
        for row in rows:
            cells = "".join(
                f'<td class="col-{key}">{self._format_cell(key, row.get(key))}</td>'
                for key, _ in DOCUMENT_TYPE_REPORT_COLUMNS
            )
            row_class = ' class="total"' if row.get("document_type_id") is None else ""
            table_rows.append(f"<tr{row_class}>{cells}</tr>")
        table_body = "\n".join(table_rows)

        return f"""
        <!doctype html>
        <html>
          <head>
            <meta charset="utf-8"/>
            <title>Izveštaj po tipovima dokumenata</title>
            <style>{self.CSS}</style>
          </head>
          <body>
            <h1>Izveštaj po tipovima dokumenata</h1>
            <div class="meta">
              <div class="period">Period: {period}</div>
              <div class="filters">{' • '.join(filters)}</div>
              <div class="filters">Generisano: {generated_at_text}</div>
            </div>
            <table>
              <thead><tr>{header_cells}</tr></thead>
              <tbody>{table_body}</tbody>
            </table>
            <div class="footer">© EcoLink 2025</div>
          </body>
        </html>
        """

    def _format_cell(self, key: str, value: Any) -> str:
        if key == "document_type_name":
            return str(value) if value is not None else '<span class="chip">Svi</span>'
        if value is None:
            return EMPTY_CELL
        if key in ("num_executions", "rating_count", "rating_median", "avg_input_tokens", "avg_output_tokens"):
            return f"{int(value):,}".replace(",", " ")
        if key == "avg_duration_ms":
            return f"{round(float(value)):,}".replace(",", " ")
        if key in ("total_cost_usd", "avg_cost_usd"):
            return f"${float(value):,.2f}".replace(",", " ")
        if key == "error_rate":
            return f"{float(value) * 100:.1f}%"
        if key == "rating_avg":
            return f"{float(value):.2f}"
        return str(value)
