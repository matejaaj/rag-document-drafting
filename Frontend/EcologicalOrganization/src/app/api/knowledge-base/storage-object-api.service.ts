import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { WRITING_ASSISTANT_API_URL } from '../common/api-url';
import { Page, PageDto, toPage } from '../common/page.model';
import { StorageObject, StorageObjectDto, toStorageObject } from './knowledge-base.model';

@Injectable({ providedIn: 'root' })
export class StorageObjectApiService {
  private readonly url = `${WRITING_ASSISTANT_API_URL}/storage-objects`;

  constructor(private http: HttpClient) {}

  list(repoFolderId: number | null = null, page = 1, perPage = 100): Observable<Page<StorageObject>> {
    const params: Record<string, number> = { page, per_page: perPage };
    if (repoFolderId !== null) params['repo_folder_id'] = repoFolderId;
    return this.http
      .get<PageDto<StorageObjectDto>>(this.url, { params })
      .pipe(map((dto) => toPage(dto, toStorageObject)));
  }

  upload(file: File, repoFolderId: number | null = null, documentTypeId: number | null = null): Observable<StorageObject> {
    const form = new FormData();
    form.append('file', file);
    if (repoFolderId !== null) form.append('repo_folder_id', String(repoFolderId));
    if (documentTypeId !== null) form.append('document_type_id', String(documentTypeId));
    return this.http.post<StorageObjectDto>(this.url, form).pipe(map(toStorageObject));
  }

  rename(id: number, newName: string): Observable<StorageObject> {
    return this.http
      .patch<StorageObjectDto>(`${this.url}/${id}`, { original_name: newName })
      .pipe(map(toStorageObject));
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.url}/${id}`);
  }

  getSummary(objectId: number): Observable<string> {
    return this.http
      .get<{ summary_text: string }>(`${this.url}/${objectId}/summary`)
      .pipe(map((response) => response.summary_text));
  }
}
