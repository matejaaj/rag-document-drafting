import { Component, EventEmitter, Input, OnChanges, Output, SimpleChanges } from '@angular/core';
import { DocumentType } from 'src/app/api/document-type/document-type.model';
import { NewPrompt } from '../../models/prompt-management.model';

@Component({
  selector: 'admin-prompt-details-form',
  templateUrl: './prompt-details-form.component.html',
  styleUrls: ['../../admin.styles.css', './prompt-details-form.component.css'],
})
export class PromptDetailsFormComponent implements OnChanges {
  @Input() title = '';
  @Input() documentTypes: DocumentType[] = [];
  @Input() documentTypeId: number | null = null;
  @Input() isNewPrompt = false;

  @Output() renameRequested = new EventEmitter<string>();
  @Output() deleteRequested = new EventEmitter<void>();
  @Output() createVersionRequested = new EventEmitter<void>();
  @Output() saveNewPromptRequested = new EventEmitter<NewPrompt>();

  titleDraft = '';
  documentTypeIdDraft: number | null = null;
  isEditingTitle = false;
  isTitleInvalid = false;

  ngOnChanges(changes: SimpleChanges): void {
    if (changes['title']) this.titleDraft = this.title;
    if (changes['documentTypeId']) this.documentTypeIdDraft = this.documentTypeId;
    if (changes['isNewPrompt'] && this.isNewPrompt) this.startEditingTitle();
  }

  get documentTypeName(): string {
    const documentType = this.documentTypes.find((type) => type.id === this.documentTypeId);
    return documentType?.name ?? 'Ovaj tip dokumenta je obrisan';
  }

  startEditingTitle(): void {
    this.isEditingTitle = true;
    this.isTitleInvalid = false;
  }

  saveTitle(): void {
    const title = this.titleDraft.trim();
    if (!title) {
      this.isTitleInvalid = true;
      return;
    }
    this.isTitleInvalid = false;
    this.isEditingTitle = false;
    this.renameRequested.emit(title);
  }

  cancelEditingTitle(): void {
    this.isEditingTitle = false;
    this.isTitleInvalid = false;
    this.titleDraft = this.title;
  }

  changeDocumentType(documentTypeId: string): void {
    this.documentTypeIdDraft = +documentTypeId;
  }

  saveNewPrompt(): void {
    const title = this.titleDraft.trim();
    if (!title) {
      this.isTitleInvalid = true;
      return;
    }
    if (this.documentTypeIdDraft === null) return;
    this.isTitleInvalid = false;
    this.saveNewPromptRequested.emit({ title, documentTypeId: this.documentTypeIdDraft });
  }
}
