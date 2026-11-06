import { Component, EventEmitter, Input, Output } from '@angular/core';
import { SortDirection } from 'src/app/api/analytics/analytics-api.service';
import { DocumentTypeReportRow } from 'src/app/api/analytics/analytics.model';
import { DocumentType } from 'src/app/api/document-type/document-type.model';
import { DocumentTypeReportColumn, DocumentTypeReportFilters } from '../../models/system-analytics.model';

@Component({
  selector: 'admin-system-analytics',
  templateUrl: './system-analytics.component.html',
  styleUrls: ['./system-analytics.component.css'],
})
export class SystemAnalyticsComponent {
  @Input({ required: true }) filters!: DocumentTypeReportFilters;
  @Input() documentTypes: DocumentType[] = [];
  @Input() dateRangeError: string | null = null;
  @Input() loading = false;
  @Input() error: string | null = null;
  @Input() rows: DocumentTypeReportRow[] = [];
  @Input() sortColumn: DocumentTypeReportColumn = 'documentTypeName';
  @Input() sortDirection: SortDirection = 'asc';
  @Input() downloadingPdf = false;

  @Output() filtersChange = new EventEmitter<DocumentTypeReportFilters>();
  @Output() applyRequested = new EventEmitter<void>();
  @Output() resetRequested = new EventEmitter<void>();
  @Output() sortRequested = new EventEmitter<DocumentTypeReportColumn>();
  @Output() downloadPdfRequested = new EventEmitter<void>();
}
