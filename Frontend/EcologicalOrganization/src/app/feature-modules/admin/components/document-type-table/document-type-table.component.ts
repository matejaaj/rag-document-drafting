import { Component, ElementRef, EventEmitter, Input, OnChanges, Output, SimpleChanges, ViewChild } from '@angular/core';
import { DocumentType } from 'src/app/api/document-type/document-type.model';
import { DocumentTypeDraft } from '../../models/document-type-management.model';

@Component({
  selector: 'admin-document-type-table',
  templateUrl: './document-type-table.component.html',
  styleUrls: ['./document-type-table.component.css', '../../admin.styles.css'],
})
export class DocumentTypeTableComponent implements OnChanges {
  @Input() documentTypes: DocumentType[] = [];
  @Input() loading = false;
  @Input() ordering = '';
  @Input() editedDocumentTypeId: number | null = null;

  @Output() sortRequested = new EventEmitter<string>();
  @Output() editRequested = new EventEmitter<DocumentType>();
  @Output() deleteRequested = new EventEmitter<number>();
  @Output() saveRequested = new EventEmitter<DocumentTypeDraft>();
  @Output() cancelEditRequested = new EventEmitter<void>();

  @ViewChild('descriptionTextArea') descriptionTextArea?: ElementRef<HTMLTextAreaElement>;

  nameDraft = '';
  descriptionDraft = '';

  ngOnChanges(changes: SimpleChanges): void {
    if (!changes['editedDocumentTypeId']) return;
    const edited = this.documentTypes.find((documentType) => documentType.id === this.editedDocumentTypeId);
    this.nameDraft = edited?.name ?? '';
    this.descriptionDraft = edited?.description || '';
    if (edited) setTimeout(() => this.resizeDescriptionTextArea());
  }

  sortArrow(column: string): string {
    if (this.ordering === column) return '▲';
    if (this.ordering === `-${column}`) return '▼';
    return '';
  }

  isDefaultDocumentType(documentType: DocumentType): boolean {
    return documentType.name?.toLowerCase() === 'default';
  }

  resizeDescriptionTextArea(): void {
    const textArea = this.descriptionTextArea?.nativeElement;
    if (!textArea) return;
    textArea.style.height = 'auto';
    textArea.style.height = textArea.scrollHeight + 'px';
  }
}
