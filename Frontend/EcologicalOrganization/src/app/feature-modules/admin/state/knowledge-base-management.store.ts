import { Injectable } from '@angular/core';
import { finalize } from 'rxjs/operators';
import { DocumentTypeApiService } from 'src/app/api/document-type/document-type-api.service';
import { DocumentType } from 'src/app/api/document-type/document-type.model';
import { RepoFolder, StorageObject } from 'src/app/api/knowledge-base/knowledge-base.model';
import { RepoFolderApiService } from 'src/app/api/knowledge-base/repo-folder-api.service';
import { StorageObjectApiService } from 'src/app/api/knowledge-base/storage-object-api.service';
import { FolderBreadcrumb } from '../models/knowledge-base-management.model';

@Injectable()
export class KnowledgeBaseManagementStore {
  breadcrumbs: FolderBreadcrumb[] = [{ folderId: null, name: 'Root' }];
  folders: RepoFolder[] = [];
  files: StorageObject[] = [];
  loading = false;

  newFolderName = '';
  creatingFolder = false;
  deletingFolderIds = new Set<number>();

  documentTypes: DocumentType[] = [];
  loadingDocumentTypes = false;
  selectedDocumentTypeId: number | null = null;
  selectedFile: File | null = null;
  uploading = false;
  deletingFileIds = new Set<number>();

  summaryText: string | null = null;
  loadingSummary = false;

  private currentFolderId: number | null = null;

  constructor(
    private repoFolderApi: RepoFolderApiService,
    private storageObjectApi: StorageObjectApiService,
    private documentTypeApi: DocumentTypeApiService
  ) {}

  load(): void {
    this.loadingDocumentTypes = true;
    this.documentTypeApi
      .list(1, 500, 'name')
      .pipe(finalize(() => (this.loadingDocumentTypes = false)))
      .subscribe((page) => (this.documentTypes = page.items));
    this.loadCurrentFolder();
  }

  refresh(): void {
    this.loadCurrentFolder();
  }

  openFolder(folder: RepoFolder): void {
    this.currentFolderId = folder.id;
    this.breadcrumbs = [...this.breadcrumbs, { folderId: folder.id, name: folder.name }];
    this.summaryText = null;
    this.loadCurrentFolder();
  }

  openBreadcrumb(index: number): void {
    this.breadcrumbs = this.breadcrumbs.slice(0, index + 1);
    this.currentFolderId = this.breadcrumbs[index].folderId;
    this.loadCurrentFolder();
  }

  changeNewFolderName(name: string): void {
    this.newFolderName = name;
  }

  createFolder(): void {
    const name = this.newFolderName.trim();
    if (!name) return;

    this.creatingFolder = true;
    this.repoFolderApi
      .create(name, this.currentFolderId)
      .pipe(finalize(() => (this.creatingFolder = false)))
      .subscribe(() => {
        this.newFolderName = '';
        this.loadCurrentFolder();
      });
  }

  deleteFolder(folder: RepoFolder): void {
    if (!confirm(`Obrisati folder "${folder.name}" i sve njegove podfoldere i fajlove?`)) return;

    this.deletingFolderIds.add(folder.id);
    this.repoFolderApi
      .delete(folder.id)
      .pipe(finalize(() => this.deletingFolderIds.delete(folder.id)))
      .subscribe(() => this.reloadAfterDelete());
  }

  selectDocumentType(documentTypeId: number | null): void {
    this.selectedDocumentTypeId = documentTypeId;
  }

  selectFile(file: File): void {
    this.selectedFile = file;
  }

  uploadSelectedFile(): void {
    if (!this.selectedFile || this.selectedDocumentTypeId === null) return;

    this.uploading = true;
    this.storageObjectApi
      .upload(this.selectedFile, this.currentFolderId, this.selectedDocumentTypeId)
      .pipe(finalize(() => (this.uploading = false)))
      .subscribe(() => {
        this.selectedFile = null;
        this.loadCurrentFolder();
      });
  }

  deleteFile(file: StorageObject): void {
    if (!confirm(`Obrisati fajl "${file.originalName}"?`)) return;

    this.deletingFileIds.add(file.id);
    this.storageObjectApi
      .delete(file.id)
      .pipe(finalize(() => this.deletingFileIds.delete(file.id)))
      .subscribe(() => this.reloadAfterDelete());
  }

  showSummary(file: StorageObject): void {
    this.summaryText = null;
    this.loadingSummary = true;
    this.storageObjectApi
      .getSummary(file.id)
      .pipe(finalize(() => (this.loadingSummary = false)))
      .subscribe((summary) => (this.summaryText = summary || ''));
  }

  private loadCurrentFolder(): void {
    this.loading = true;
    const isRoot = this.currentFolderId === null;

    this.repoFolderApi
      .list(this.currentFolderId)
      .pipe(finalize(() => (this.loading = false)))
      .subscribe((page) => {
        this.folders = isRoot ? page.items.filter((folder) => folder.parentId === null) : page.items;
      });

    this.storageObjectApi.list(this.currentFolderId).subscribe((page) => {
      this.files = isRoot ? page.items.filter((file) => file.repoFolderId === null) : page.items;
    });
  }

  private reloadAfterDelete(): void {
    this.loadCurrentFolder();
    this.summaryText = null;
    this.loadingSummary = false;
  }
}
