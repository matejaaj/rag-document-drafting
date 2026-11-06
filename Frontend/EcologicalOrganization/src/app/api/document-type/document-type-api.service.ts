import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { WRITING_ASSISTANT_API_URL } from '../common/api-url';
import { Page, PageDto, toPage } from '../common/page.model';
import { DocumentType, DocumentTypeDto, toDocumentType } from './document-type.model';

@Injectable({ providedIn: 'root' })
export class DocumentTypeApiService {
  private readonly url = `${WRITING_ASSISTANT_API_URL}/document-types`;

  constructor(private http: HttpClient) {}

  list(page = 1, perPage = 20, ordering = '-updated_at'): Observable<Page<DocumentType>> {
    return this.http
      .get<PageDto<DocumentTypeDto>>(this.url, { params: { page, per_page: perPage, ordering } })
      .pipe(map((dto) => toPage(dto, toDocumentType)));
  }

  create(name: string, description: string | null): Observable<DocumentType> {
    return this.http
      .post<DocumentTypeDto>(this.url, { name, description })
      .pipe(map(toDocumentType));
  }

  update(id: number, name: string, description: string | null): Observable<void> {
    return this.http.patch<void>(`${this.url}/${id}`, { name, description });
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.url}/${id}`);
  }
}
