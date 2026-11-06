import { Injectable } from '@angular/core';
import { DocumentTypeApiService } from 'src/app/api/document-type/document-type-api.service';
import { DocumentType } from 'src/app/api/document-type/document-type.model';
import { TemplateApiService } from 'src/app/api/template/template-api.service';
import { Template } from 'src/app/api/template/template.model';
import { TemplateUpload } from '../models/template-upload.model';

const PAGE_SIZE = 20;

@Injectable()
export class TemplatesStore {
  templates: Template[] = [];
  documentTypes: DocumentType[] = [];
  loading = true;
  loadingMore = false;
  hasMore = false;
  deletingTemplateId: number | null = null;
  uploadDialogOpen = false;
  uploading = false;

  private page = 1;
  private totalCount = 0;
  private searchTerm?: string;

  constructor(private templateApi: TemplateApiService, private documentTypeApi: DocumentTypeApiService) {}

  loadDocumentTypes(): void {
    this.documentTypeApi.list().subscribe((result) => (this.documentTypes = result.items));
  }

  loadTemplates(): void {
    this.templates = [];
    this.searchTemplates('');
  }

  searchTemplates(searchTerm: string): void {
    this.searchTerm = searchTerm.trim() || undefined;
    this.loading = true;
    this.page = 1;
    this.loadPage();
  }

  loadMoreTemplates(): void {
    if (!this.hasMore || this.loading || this.loadingMore) return;
    this.loadingMore = true;
    this.page += 1;
    this.loadPage();
  }

  deleteTemplate(template: Template): void {
    if (this.deletingTemplateId) return;
    this.deletingTemplateId = template.id;
    this.templateApi.delete(template.id).subscribe({
      next: () => {
        this.setTemplates(this.templates.filter((item) => item.id !== template.id));
        if (this.hasMore && this.templates.length < this.totalCount) {
          this.loadMoreTemplates();
        }
        this.deletingTemplateId = null;
      },
      error: () => (this.deletingTemplateId = null),
    });
  }

  uploadTemplate(upload: TemplateUpload): void {
    this.uploading = true;
    this.templateApi.upload(upload.name, upload.documentTypeId, upload.file).subscribe({
      next: (template) => {
        const documentType = this.documentTypes.find((type) => type.id === template.documentTypeId);
        this.setTemplates([{ ...template, documentTypeName: documentType?.name ?? '' }, ...this.templates]);
        this.uploading = false;
        this.uploadDialogOpen = false;
      },
      error: () => (this.uploading = false),
    });
  }

  private loadPage(): void {
    const append = this.page > 1;
    this.templateApi.list(this.page, PAGE_SIZE, this.searchTerm).subscribe({
      next: (result) => {
        this.totalCount = result.meta.totalCount;
        this.setTemplates(append ? [...this.templates, ...result.items] : result.items);
        this.hasMore = this.templates.length < this.totalCount;
        this.loading = false;
        this.loadingMore = false;
      },
      error: () => {
        this.loading = false;
        this.loadingMore = false;
      },
    });
  }

  private setTemplates(templates: Template[]): void {
    const labeledTemplates = templates.map((template) => {
      const typeName = (template.documentTypeName ?? '').trim().toLowerCase();
      return typeName === 'default' || typeName === 'ostali' ? { ...template, documentTypeName: 'Opšti' } : template;
    });
    const emptyTemplateIndex = labeledTemplates.findIndex((template) => (template.name ?? '').trim().toLowerCase() === 'prazan');
    if (emptyTemplateIndex > 0) {
      labeledTemplates.unshift(...labeledTemplates.splice(emptyTemplateIndex, 1));
    }
    this.templates = labeledTemplates;
  }
}
