from app.schema.analytics.analytics_schema import AnalyticsOut
from app.repository.analytics.analytics_repository import AnalyticsRepository
from app.services.prompt.prompt_version_service import PromptVersionService
from typing import Optional, List, Dict, Any
from datetime import datetime


class AnalyticsService:
    def __init__(
        self,
        analytics_repository: AnalyticsRepository,
        prompt_version_service: PromptVersionService,
    ):
        self.analytics_repository = analytics_repository
        self.prompt_version_service = prompt_version_service

    @staticmethod
    def _to_metrics(values: dict) -> dict:
        executions = int(values["num_executions"] or 0)
        avg_input_tokens = values["avg_input_tokens"]
        avg_output_tokens = values["avg_output_tokens"]
        avg_tokens = (
            avg_input_tokens + avg_output_tokens
            if avg_input_tokens is not None and avg_output_tokens is not None
            else None
        )
        return {
            "num_executions": executions,
            "avg_duration_ms": values["avg_duration_ms"],
            "avg_input_tokens": avg_input_tokens,
            "avg_output_tokens": avg_output_tokens,
            "avg_tokens": avg_tokens,
            "total_tokens": round(avg_tokens * executions) if avg_tokens is not None else 0,
            "cost_per_execution": values["avg_cost"],
            "total_cost_usd": float(values["total_cost_usd"] or 0),
            "error_rate": values["error_rate"],
            "rating_count": int(values["rating_count"] or 0),
            "rating_avg": values["rating_avg"],
            "rating_median": values["rating_median"],
            **{f"rating_c{stars}": int(values[f"rating_c{stars}"] or 0) for stars in range(1, 6)},
            "failed_execution_count": int(values["failed_exec_count"] or 0),
        }

    def get_version_analytics(self, version_id: int, bayes_prior_weight: int = 10) -> AnalyticsOut:
        prompt_version = self.prompt_version_service.get_details(version_id)
        active_version = self.prompt_version_service.find_active_for_document_type(prompt_version.document_type_id)

        if active_version and active_version.id == prompt_version.id:
            metric_values = self.analytics_repository.get_version_metrics_live(version_id)
        else:
            # stats saved on the version when it stopped being active
            metric_values = prompt_version.model_dump()

        return AnalyticsOut(
            scope="version",
            prompt_version_id=version_id,
            **self._to_metrics(metric_values),
            bayes_score=self.analytics_repository.get_bayes_for_version(version_id, bayes_prior_weight),
        )

    def get_prompt_analytics(self, prompt_id: int, bayes_prior_weight: int = 10) -> AnalyticsOut:
        return AnalyticsOut(
            scope="prompt",
            prompt_id=prompt_id,
            **self._to_metrics(self.analytics_repository.get_prompt_analytics(prompt_id)),
            bayes_score=self.analytics_repository.get_bayes_for_prompt(prompt_id, bayes_prior_weight),
        )

    def get_document_type_report(
        self, from_ts: datetime, to_ts: datetime, document_type_id: Optional[int], include_total: bool = True
    ) -> List[Dict[str, Any]]:
        return self.analytics_repository.get_document_type_report(from_ts, to_ts, document_type_id, include_total)
