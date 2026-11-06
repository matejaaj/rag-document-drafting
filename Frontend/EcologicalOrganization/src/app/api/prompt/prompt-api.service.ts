import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { WRITING_ASSISTANT_API_URL } from '../common/api-url';
import { Page, PageDto, toPage } from '../common/page.model';
import { Prompt, PromptDto, toPrompt } from './prompt.model';

@Injectable({ providedIn: 'root' })
export class PromptApiService {
  private readonly url = `${WRITING_ASSISTANT_API_URL}/prompts`;

  constructor(private http: HttpClient) {}

  list(page = 1, perPage = 20, searchTerm?: string): Observable<Page<Prompt>> {
    const params: Record<string, string | number> = { page, per_page: perPage };
    if ((searchTerm ?? '').trim()) params['search_term'] = searchTerm!.trim();

    return this.http
      .get<PageDto<PromptDto>>(this.url, { params })
      .pipe(map((dto) => toPage(dto, toPrompt)));
  }

  create(title: string, documentTypeId: number): Observable<Prompt> {
    return this.http
      .post<PromptDto>(this.url, { title, document_type_id: documentTypeId })
      .pipe(map((dto) => ({ ...toPrompt(dto), activeVersion: null })));
  }

  updateTitle(id: number, title: string): Observable<void> {
    return this.http.patch<void>(`${this.url}/${id}/title`, { title });
  }

  delete(id: number): Observable<void> {
    return this.http.delete<void>(`${this.url}/${id}`);
  }
}
