import { Component, EventEmitter, Input, Output } from '@angular/core';
import { DocumentType } from 'src/app/api/document-type/document-type.model';
import { DocumentTypeReportFilters } from '../../models/system-analytics.model';

@Component({
  selector: 'admin-document-type-report-filters',
  templateUrl: './document-type-report-filters.component.html',
  styleUrls: ['./document-type-report-filters.component.css'],
})
export class DocumentTypeReportFiltersComponent {
  @Input({ required: true }) filters!: DocumentTypeReportFilters;
  @Input() documentTypes: DocumentType[] = [];
  @Input() dateRangeError: string | null = null;

  @Output() filtersChange = new EventEmitter<DocumentTypeReportFilters>();
  @Output() applyRequested = new EventEmitter<void>();
  @Output() resetRequested = new EventEmitter<void>();

  changeFilters(change: Partial<DocumentTypeReportFilters>): void {
    this.filtersChange.emit({ ...this.filters, ...change });
  }
}
