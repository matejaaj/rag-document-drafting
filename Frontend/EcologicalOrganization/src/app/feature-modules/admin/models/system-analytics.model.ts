export interface DocumentTypeReportFilters {
  fromDate: string;
  toDate: string;
  documentTypeId: number | null;
  includeTotal: boolean;
}

export type DocumentTypeReportColumn =
  | 'documentTypeName'
  | 'numExecutions'
  | 'avgDurationMs'
  | 'avgInputTokens'
  | 'avgOutputTokens'
  | 'totalCostUsd'
  | 'avgCostUsd'
  | 'errorRate'
  | 'ratingCount'
  | 'ratingAvg'
  | 'ratingMedian';
