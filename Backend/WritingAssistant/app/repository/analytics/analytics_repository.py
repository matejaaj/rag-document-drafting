from contextlib import AbstractContextManager
from typing import Any, Callable, Dict, Optional

from sqlalchemy.orm import Session
from sqlalchemy import text


METRIC_COLUMNS = (
    "num_executions", "avg_duration_ms", "avg_input_tokens", "avg_output_tokens", "avg_cost",
    "total_cost_usd", "failed_exec_count", "error_rate", "rating_count", "rating_avg",
    "rating_median", "rating_c1", "rating_c2", "rating_c3", "rating_c4", "rating_c5",
)


class AnalyticsRepository:
    """Calls Oracle PL/SQL packages; not ported to SQLite yet."""

    def __init__(self, session_factory: Callable[..., AbstractContextManager[Session]]):
        self.session_factory = session_factory

    def _call_ref_cursor_function(self, session: Session, function_name: str, *args):
        database_api = session.bind.dialect.dbapi
        raw_connection = session.connection().connection
        cursor = raw_connection.cursor()
        cursor_type = getattr(database_api, "CURSOR", database_api.Cursor)
        return cursor.callfunc(function_name, cursor_type, list(args))

    def get_version_metrics_live(self, version_id: int) -> Dict[str, Any]:
        with self.session_factory() as session:
            result_cursor = self._call_ref_cursor_function(session, "prompt_metrics_pkg.get_pv_metrics", version_id)
            return dict(zip(METRIC_COLUMNS, result_cursor.fetchone()))

    def get_prompt_analytics(self, prompt_id: int) -> Dict[str, Any]:
        with self.session_factory() as session:
            result_cursor = self._call_ref_cursor_function(session, "prompt_metrics_pkg.get_prompt_metrics", prompt_id)
            return dict(zip(METRIC_COLUMNS, result_cursor.fetchone()))

    def get_bayes_for_version(self, version_id: int, prior_weight: int = 10) -> Optional[float]:
        with self.session_factory() as session:
            score = session.execute(text("SELECT calc_bayes_score(:version_id, :prior_weight) FROM dual"),
                                    {"version_id": version_id, "prior_weight": prior_weight}).scalar()
            return float(score) if score is not None else None

    def get_bayes_for_prompt(self, prompt_id: int, prior_weight: int = 10) -> Optional[float]:
        with self.session_factory() as session:
            score = session.execute(text("SELECT calc_bayes_score_for_prompt(:prompt_id, :prior_weight) FROM dual"),
                                    {"prompt_id": prompt_id, "prior_weight": prior_weight}).scalar()
            return float(score) if score is not None else None

    def get_document_type_report(self, from_ts, to_ts, document_type_id, include_total=True):
        report_query = text("""
            SELECT *
            FROM TABLE(
            report_pkg.get_doc_type_report(
                :from_ts, :to_ts, :document_type_id, :include_total
            )
            )
        """)
        with self.session_factory() as session:
            result = session.execute(report_query, {
                "from_ts": from_ts,
                "to_ts": to_ts,
                "document_type_id": document_type_id,
                "include_total": 1 if include_total else 0
            })
            return [dict(row) for row in result.mappings().all()]
