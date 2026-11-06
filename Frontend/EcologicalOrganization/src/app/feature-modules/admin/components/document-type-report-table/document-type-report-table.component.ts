import { Component, EventEmitter, Input, Output } from '@angular/core';
import { SortDirection } from 'src/app/api/analytics/analytics-api.service';
import { DocumentTypeReportRow } from 'src/app/api/analytics/analytics.model';
import { DocumentTypeReportColumn } from '../../models/system-analytics.model';

@Component({
  selector: 'admin-document-type-report-table',
  templateUrl: './document-type-report-table.component.html',
  styleUrls: ['./document-type-report-table.component.css'],
})
export class DocumentTypeReportTableComponent {
  @Input() rows: DocumentTypeReportRow[] = [];
  @Input() sortColumn: DocumentTypeReportColumn = 'documentTypeName';
  @Input() sortDirection: SortDirection = 'asc';

  @Output() sortRequested = new EventEmitter<DocumentTypeReportColumn>();

  readonly columns: { key: DocumentTypeReportColumn; label: string }[] = [
    { key: 'documentTypeName', label: 'Tip dokumenta' },
    { key: 'numExecutions', label: '# Izvršavanja' },
    { key: 'avgDurationMs', label: 'Prosečno trajanje (ms)' },
    { key: 'avgInputTokens', label: 'Avg input tok.' },
    { key: 'avgOutputTokens', label: 'Avg output tok.' },
    { key: 'totalCostUsd', label: 'Ukupan trošak ($)' },
    { key: 'avgCostUsd', label: 'Trošak/izv. ($)' },
    { key: 'errorRate', label: 'Greške (%)' },
    { key: 'ratingCount', label: '# Ocena' },
    { key: 'ratingAvg', label: 'Avg ocena' },
    { key: 'ratingMedian', label: 'Medijan' },
  ];

  ariaSort(column: DocumentTypeReportColumn): string {
    if (column !== this.sortColumn) return 'none';
    return this.sortDirection === 'asc' ? 'ascending' : 'descending';
  }
}
