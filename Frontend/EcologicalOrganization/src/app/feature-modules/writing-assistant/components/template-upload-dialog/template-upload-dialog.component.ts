import { Component, EventEmitter, HostListener, Input, OnInit, Output } from '@angular/core';
import { DocumentType } from 'src/app/api/document-type/document-type.model';
import { TemplateUpload } from '../../models/template-upload.model';

@Component({
  selector: 'wa-template-upload-dialog',
  templateUrl: './template-upload-dialog.component.html',
  styleUrls: ['./template-upload-dialog.component.css', '../../writing-assistant.styles.css'],
})
export class TemplateUploadDialogComponent implements OnInit {
  @Input() documentTypes: DocumentType[] = [];
  @Input() uploading = false;

  @Output() closeRequested = new EventEmitter<void>();
  @Output() uploadRequested = new EventEmitter<TemplateUpload>();

  form = {
    name: '',
    documentTypeId: null as number | null,
    file: null as File | null,
  };

  nameEdited = false;

  ngOnInit(): void {
    const defaultDocumentType = this.documentTypes.find((documentType) => documentType.name === 'Default');
    if (defaultDocumentType) this.form.documentTypeId = defaultDocumentType.id;
  }

  selectFile(event: Event): void {
    const file = (event.target as HTMLInputElement).files?.[0] || null;
    this.form.file = file;
    if (file && !this.nameEdited && !this.form.name) {
      this.form.name = file.name.replace(/\.[^.]+$/, '');
    }
  }

  clearFile(fileInput: HTMLInputElement): void {
    this.form.file = null;
    if (!this.nameEdited) this.form.name = '';
    fileInput.value = '';
  }

  isValid(): boolean {
    return !!(this.form.file && this.form.name.trim() && this.form.documentTypeId);
  }

  upload(): void {
    const { name, documentTypeId, file } = this.form;
    if (!file || !name.trim() || !documentTypeId || this.uploading) return;
    this.uploadRequested.emit({ name: name.trim(), documentTypeId, file });
  }

  @HostListener('document:keydown.escape')
  cancel(): void {
    if (!this.uploading) this.closeRequested.emit();
  }
}
