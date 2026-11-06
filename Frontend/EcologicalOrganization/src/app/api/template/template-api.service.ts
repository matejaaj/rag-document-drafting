import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { WRITING_ASSISTANT_API_URL } from '../common/api-url';
import { Page, PageDto, toPage } from '../common/page.model';
import { Template, TemplateDto, toTemplate } from './template.model';

@Injectable({ providedIn: 'root' })
export class TemplateApiService {
  private readonly url = `${WRITING_ASSISTANT_API_URL}/templates`;

  constructor(private http: HttpClient) {}

  list(page = 1, perPage = 20, searchTerm?: string): Observable<Page<Template>> {
    const params: Record<string, string | number> = { page, per_page: perPage };
    if ((searchTerm ?? '').trim()) params['search_term'] = searchTerm!.trim();

    return this.http
      .get<PageDto<TemplateDto>>(this.url, { params })
      .pipe(map((dto) => toPage(dto, toTemplate)));
  }

  upload(name: string, documentTypeId: number, file: File): Observable<Template> {
    const formData = new FormData();
    formData.append('name', name);
    formData.append('document_type_id', String(documentTypeId));
    formData.append('file', file);
    return this.http.post<TemplateDto>(this.url, formData).pipe(map(toTemplate));
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.url}/${id}`);
  }
}
