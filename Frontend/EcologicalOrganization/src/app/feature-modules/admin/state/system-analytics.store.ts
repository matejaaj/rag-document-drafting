import { Injectable } from '@angular/core';
import { AnalyticsApiService, SortDirection } from 'src/app/api/analytics/analytics-api.service';
import { DocumentTypeReportRow } from 'src/app/api/analytics/analytics.model';
import { DocumentTypeApiService } from 'src/app/api/document-type/document-type-api.service';
import { DocumentType } from 'src/app/api/document-type/document-type.model';
import { DocumentTypeReportColumn, DocumentTypeReportFilters } from '../models/system-analytics.model';

const PDF_SORT_KEYS: Record<DocumentTypeReportColumn, string> = {
  documentTypeName: 'document_type_name',
  numExecutions: 'num_executions',
  avgDurationMs: 'avg_duration_ms',
  avgInputTokens: 'avg_input_tokens',
  avgOutputTokens: 'avg_output_tokens',
  totalCostUsd: 'total_cost_usd',
  avgCostUsd: 'avg_cost_usd',
  errorRate: 'error_rate',
  ratingCount: 'rating_count',
  ratingAvg: 'rating_avg',
  ratingMedian: 'rating_median',
};

@Injectable()
export class SystemAnalyticsStore {
  filters = defaultFilters();
  documentTypes: DocumentType[] = [];
  dateRangeError: string | null = null;
  rows: DocumentTypeReportRow[] = [];
  sortColumn: DocumentTypeReportColumn = 'documentTypeName';
  sortDirection: SortDirection = 'asc';
  loading = false;
  error: string | null = null;
  downloadingPdf = false;

  constructor(
    private analyticsApi: AnalyticsApiService,
    private documentTypeApi: DocumentTypeApiService
  ) {}

  open(): void {
    this.filters = defaultFilters();
    this.documentTypes = [];
    this.rows = [];
    this.sortColumn = 'documentTypeName';
    this.sortDirection = 'asc';
    this.error = null;
    this.downloadingPdf = false;
    this.documentTypeApi.list().subscribe((page) => (this.documentTypes = page.items));
    this.applyFilters();
  }

  changeFilters(filters: DocumentTypeReportFilters): void {
    this.filters = filters;
    this.validateDateRange();
  }

  applyFilters(): void {
    this.validateDateRange();
    if (this.dateRangeError) return;

    this.loading = true;
    this.error = null;
    const { fromDate, toDate, documentTypeId, includeTotal } = this.filters;
    this.analyticsApi
      .getDocumentTypeReport(startOfDay(fromDate), endOfDay(toDate), documentTypeId, includeTotal)
      .subscribe({
        next: (rows) => {
          this.rows = this.sortRows(rows);
          this.loading = false;
        },
        error: () => {
          this.error = 'Učitavanje izveštaja nije uspelo.';
          this.rows = [];
          this.loading = false;
        },
      });
  }

  resetFilters(): void {
    this.filters = defaultFilters();
    this.applyFilters();
  }

  sortBy(column: DocumentTypeReportColumn): void {
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'asc';
    }
    this.rows = this.sortRows(this.rows);
  }

  downloadPdf(): void {
    this.validateDateRange();
    if (this.dateRangeError) return;

    this.downloadingPdf = true;
    const { fromDate, toDate, documentTypeId, includeTotal } = this.filters;
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || undefined;
    this.analyticsApi
      .downloadDocumentTypeReportPdf(
        startOfDay(fromDate),
        endOfDay(toDate),
        documentTypeId,
        includeTotal,
        PDF_SORT_KEYS[this.sortColumn],
        this.sortDirection,
        timezone
      )
      .subscribe({
        next: (pdf) => {
          saveFile(pdf, `doc-type-report_${fromDate}_to_${toDate}.pdf`);
          this.downloadingPdf = false;
        },
        error: () => {
          this.error = 'Preuzimanje PDF izveštaja nije uspelo.';
          this.downloadingPdf = false;
        },
      });
  }

  private validateDateRange(): void {
    const { fromDate, toDate } = this.filters;
    const isInvalid = !!fromDate && !!toDate && new Date(fromDate) > new Date(toDate);
    this.dateRangeError = isInvalid ? 'Datum od ne sme biti posle datuma do.' : null;
  }

  private sortRows(rows: DocumentTypeReportRow[]): DocumentTypeReportRow[] {
    const totalRow = rows.find((row) => row.documentTypeId === null);
    const direction = this.sortDirection === 'asc' ? 1 : -1;
    const sortedRows = rows
      .filter((row) => row.documentTypeId !== null)
      .sort((left, right) => {
        const leftValue = left[this.sortColumn];
        const rightValue = right[this.sortColumn];
        if (leftValue == null && rightValue == null) return 0;
        if (leftValue == null) return 1;
        if (rightValue == null) return -1;
        if (typeof leftValue === 'string' && typeof rightValue === 'string') {
          return leftValue.localeCompare(rightValue) * direction;
        }
        return (Number(leftValue) - Number(rightValue)) * direction;
      });
    return totalRow ? [...sortedRows, totalRow] : sortedRows;
  }
}

function defaultFilters(): DocumentTypeReportFilters {
  const today = new Date();
  const weekAgo = new Date(today);
  weekAgo.setDate(weekAgo.getDate() - 7);
  return { fromDate: toDateInputValue(weekAgo), toDate: toDateInputValue(today), documentTypeId: null, includeTotal: true };
}

function toDateInputValue(date: Date): string {
  const twoDigits = (value: number) => String(value).padStart(2, '0');
  return `${date.getFullYear()}-${twoDigits(date.getMonth() + 1)}-${twoDigits(date.getDate())}`;
}

function startOfDay(date: string): string {
  return `${date}T00:00:00${timezoneOffset()}`;
}

function endOfDay(date: string): string {
  return `${date}T23:59:59${timezoneOffset()}`;
}

function timezoneOffset(): string {
  const offsetMinutes = -new Date().getTimezoneOffset();
  const sign = offsetMinutes >= 0 ? '+' : '-';
  const hours = String(Math.floor(Math.abs(offsetMinutes) / 60)).padStart(2, '0');
  const minutes = String(Math.abs(offsetMinutes) % 60).padStart(2, '0');
  return `${sign}${hours}:${minutes}`;
}

function saveFile(file: Blob, fileName: string): void {
  const url = window.URL.createObjectURL(file);
  const link = document.createElement('a');
  link.href = url;
  link.download = fileName;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
