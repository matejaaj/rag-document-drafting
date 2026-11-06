export interface UsageMetrics {
  numExecutions: number;
  avgDurationMs: number | null;
  avgInputTokens: number | null;
  avgOutputTokens: number | null;
  totalCostUsd: number;
  errorRate: number | null;
  ratingCount: number;
  ratingAvg: number | null;
  ratingMedian: number | null;
  ratingC1: number;
  ratingC2: number;
  ratingC3: number;
  ratingC4: number;
  ratingC5: number;
}

export interface PromptAnalytics extends UsageMetrics {
  scope: 'version' | 'prompt';
  promptId?: number | null;
  promptVersionId?: number | null;
  avgTokens: number | null;
  totalTokens: number;
  costPerExecution: number | null;
  failedExecutionCount?: number | null;
  bayesScore?: number | null;
}

export interface DocumentTypeReportRow extends UsageMetrics {
  documentTypeId: number | null;
  documentTypeName: string;
  avgCostUsd: number | null;
  failedExecutions: number;
}

export interface DocumentReportSectionSelection {
  sectionId: number;
  seqNo?: number;
}

interface UsageMetricsDto {
  num_executions: number;
  avg_duration_ms: number | null;
  avg_input_tokens: number | null;
  avg_output_tokens: number | null;
  total_cost_usd: number;
  error_rate: number | null;
  rating_count: number;
  rating_avg: number | null;
  rating_median: number | null;
  rating_c1: number;
  rating_c2: number;
  rating_c3: number;
  rating_c4: number;
  rating_c5: number;
}

export interface PromptAnalyticsDto extends UsageMetricsDto {
  scope: 'version' | 'prompt';
  prompt_id?: number | null;
  prompt_version_id?: number | null;
  avg_tokens: number | null;
  total_tokens: number;
  cost_per_execution: number | null;
  failed_execution_count?: number | null;
  bayes_score?: number | null;
}

export interface DocumentTypeReportRowDto extends UsageMetricsDto {
  document_type_id: number | null;
  document_type_name: string;
  avg_cost_usd: number | null;
  failed_execs: number;
}

function toUsageMetrics(dto: UsageMetricsDto): UsageMetrics {
  return {
    numExecutions: dto.num_executions,
    avgDurationMs: dto.avg_duration_ms,
    avgInputTokens: dto.avg_input_tokens,
    avgOutputTokens: dto.avg_output_tokens,
    totalCostUsd: dto.total_cost_usd,
    errorRate: dto.error_rate,
    ratingCount: dto.rating_count,
    ratingAvg: dto.rating_avg,
    ratingMedian: dto.rating_median,
    ratingC1: dto.rating_c1,
    ratingC2: dto.rating_c2,
    ratingC3: dto.rating_c3,
    ratingC4: dto.rating_c4,
    ratingC5: dto.rating_c5,
  };
}

export function toPromptAnalytics(dto: PromptAnalyticsDto): PromptAnalytics {
  return {
    ...toUsageMetrics(dto),
    scope: dto.scope,
    promptId: dto.prompt_id ?? null,
    promptVersionId: dto.prompt_version_id ?? null,
    avgTokens: dto.avg_tokens,
    totalTokens: dto.total_tokens,
    costPerExecution: dto.cost_per_execution,
    failedExecutionCount: dto.failed_execution_count ?? null,
    bayesScore: dto.bayes_score ?? null,
  };
}

export function toDocumentTypeReportRow(dto: DocumentTypeReportRowDto): DocumentTypeReportRow {
  return {
    ...toUsageMetrics(dto),
    documentTypeId: dto.document_type_id,
    documentTypeName: dto.document_type_name,
    avgCostUsd: dto.avg_cost_usd,
    failedExecutions: dto.failed_execs,
  };
}
