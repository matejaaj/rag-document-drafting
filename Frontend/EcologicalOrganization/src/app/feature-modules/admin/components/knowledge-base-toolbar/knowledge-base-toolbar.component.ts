import { Component, ElementRef, EventEmitter, Input, OnChanges, Output, SimpleChanges, ViewChild } from '@angular/core';
import { DocumentType } from 'src/app/api/document-type/document-type.model';
import { FolderBreadcrumb } from '../../models/knowledge-base-management.model';

@Component({
  selector: 'admin-knowledge-base-toolbar',
  templateUrl: './knowledge-base-toolbar.component.html',
  styleUrls: ['./knowledge-base-toolbar.component.css'],
})
export class KnowledgeBaseToolbarComponent implements OnChanges {
  @Input() breadcrumbs: FolderBreadcrumb[] = [];
  @Input() newFolderName = '';
  @Input() creatingFolder = false;
  @Input() documentTypes: DocumentType[] = [];
  @Input() loadingDocumentTypes = false;
  @Input() selectedDocumentTypeId: number | null = null;
  @Input() selectedFile: File | null = null;
  @Input() uploading = false;

  @Output() openBreadcrumbRequested = new EventEmitter<number>();
  @Output() newFolderNameChange = new EventEmitter<string>();
  @Output() createFolderRequested = new EventEmitter<void>();
  @Output() selectedDocumentTypeIdChange = new EventEmitter<number | null>();
  @Output() selectedFileChange = new EventEmitter<File>();
  @Output() uploadRequested = new EventEmitter<void>();
  @Output() refreshRequested = new EventEmitter<void>();

  @ViewChild('fileInput') fileInput?: ElementRef<HTMLInputElement>;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['selectedFile'] && !this.selectedFile && this.fileInput) {
      this.fileInput.nativeElement.value = '';
    }
  }

  pickFile(event: Event): void {
    const files = (event.target as HTMLInputElement).files;
    if (files && files.length > 0) this.selectedFileChange.emit(files[0]);
  }
}
