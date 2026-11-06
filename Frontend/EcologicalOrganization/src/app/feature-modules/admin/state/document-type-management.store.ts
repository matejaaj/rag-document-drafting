import { Injectable } from '@angular/core';
import { Observable } from 'rxjs';
import { DocumentTypeApiService } from 'src/app/api/document-type/document-type-api.service';
import { DocumentType } from 'src/app/api/document-type/document-type.model';
import { DocumentTypeDraft } from '../models/document-type-management.model';

@Injectable()
export class DocumentTypeManagementStore {
  documentTypes: DocumentType[] = [];
  loading = false;
  ordering = '-updated_at';
  editedDocumentTypeId: number | null = null;

  private isAddingNew = false;

  constructor(private documentTypeApi: DocumentTypeApiService) {}

  load(): void {
    this.loading = true;
    this.documentTypeApi.list(1, 20, this.ordering).subscribe({
      next: (page) => {
        this.documentTypes = page.items;
        this.loading = false;
      },
      error: () => (this.loading = false),
    });
  }

  sortBy(column: string): void {
    this.ordering = this.ordering === column ? `-${column}` : column;
    this.load();
  }

  addDocumentType(): void {
    const newDocumentType: DocumentType = {
      id: -Date.now(),
      name: '',
      description: '',
      deleted: 0,
      createdAt: undefined,
      updatedAt: undefined,
    };
    this.documentTypes = [newDocumentType, ...this.documentTypes];
    this.editedDocumentTypeId = newDocumentType.id;
    this.isAddingNew = true;
  }

  editDocumentType(documentType: DocumentType): void {
    this.editedDocumentTypeId = documentType.id;
    this.isAddingNew = false;
  }

  cancelEditing(): void {
    if (this.isAddingNew) {
      this.documentTypes = this.documentTypes.filter((documentType) => documentType.id !== this.editedDocumentTypeId);
      this.isAddingNew = false;
    }
    this.editedDocumentTypeId = null;
  }

  saveDocumentType(draft: DocumentTypeDraft): void {
    const name = draft.name.trim();
    if (!name || this.editedDocumentTypeId === null) return;

    const request: Observable<unknown> = this.isAddingNew
      ? this.documentTypeApi.create(name, draft.description)
      : this.documentTypeApi.update(this.editedDocumentTypeId, name, draft.description);

    request.subscribe(() => {
      this.isAddingNew = false;
      this.cancelEditing();
      this.load();
    });
  }

  deleteDocumentType(documentTypeId: number): void {
    if (!confirm('Da li si siguran da želiš da obrišeš ovaj tip dokumenta?')) return;
    this.documentTypeApi.delete(documentTypeId).subscribe(() => this.load());
  }
}
