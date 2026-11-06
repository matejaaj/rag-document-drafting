import { Component, EventEmitter, Input, Output } from '@angular/core';
import { DocumentType } from 'src/app/api/document-type/document-type.model';

@Component({
  selector: 'wa-session-header',
  templateUrl: './session-header.component.html',
  styleUrls: ['../../writing-assistant.styles.css', './session-header.component.css'],
})
export class SessionHeaderComponent {
  @Input() title = '';
  @Input() globalInstruction = '';
  @Input() documentTypes: DocumentType[] = [];
  @Input() documentTypeId: number | null = null;
  @Input() isTestSession = false;

  @Output() saveTitleRequested = new EventEmitter<string>();
  @Output() addSectionRequested = new EventEmitter<void>();
  @Output() globalInstructionChange = new EventEmitter<string>();
  @Output() documentTypeChange = new EventEmitter<number>();
  @Output() openPreviewRequested = new EventEmitter<void>();

  editingTitle = false;
  titleDraft = '';
  invalidTitle = false;

  get selectedDocumentType(): DocumentType | null {
    return this.documentTypes.find((documentType) => documentType.id === this.documentTypeId) ?? null;
  }

  startTitleEdit(): void {
    this.editingTitle = true;
    this.titleDraft = this.title;
    this.invalidTitle = false;
  }

  saveTitle(): void {
    const newTitle = this.titleDraft.trim();
    if (!newTitle) {
      this.invalidTitle = true;
      return;
    }
    this.invalidTitle = false;
    this.saveTitleRequested.emit(newTitle);
    this.editingTitle = false;
  }

  cancelTitleEdit(): void {
    this.editingTitle = false;
    this.invalidTitle = false;
    this.titleDraft = this.title;
  }

  changeDocumentType(value: string | number): void {
    this.documentTypeChange.emit(+value);
  }
}
