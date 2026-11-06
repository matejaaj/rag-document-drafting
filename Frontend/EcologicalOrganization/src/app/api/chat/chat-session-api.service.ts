import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { WRITING_ASSISTANT_API_URL } from '../common/api-url';
import { Page, PageDto, toPage } from '../common/page.model';
import {
  ChatSession,
  ChatSessionDto,
  SessionOverview,
  SessionOverviewDto,
  toChatSession,
  toSessionOverview,
} from './chat.model';

@Injectable({ providedIn: 'root' })
export class ChatSessionApiService {
  private readonly url = `${WRITING_ASSISTANT_API_URL}/chat-sessions`;

  constructor(private http: HttpClient) {}

  list(page = 1, perPage = 20, searchTerm?: string): Observable<Page<ChatSession>> {
    let params = new HttpParams().set('page', String(page)).set('per_page', String(perPage));
    if ((searchTerm ?? '').trim()) {
      params = params.set('search_term', (searchTerm as string).trim());
    }
    return this.http
      .get<PageDto<ChatSessionDto>>(this.url, { params })
      .pipe(map((dto) => toPage(dto, toChatSession)));
  }

  create(templateId: number, title?: string): Observable<ChatSession> {
    const body: { template_id: number; title?: string } = { template_id: templateId };
    if (title && title.trim()) body.title = title.trim();
    return this.http.post<ChatSessionDto>(this.url, body).pipe(map(toChatSession));
  }

  createTestSession(testPromptVersionId: number, title: string): Observable<ChatSession> {
    return this.http
      .post<ChatSessionDto>(`${this.url}/test`, { test_prompt_version_id: testPromptVersionId, title })
      .pipe(map(toChatSession));
  }

  updateTitle(sessionId: number, title: string): Observable<ChatSession> {
    return this.http
      .patch<ChatSessionDto>(`${this.url}/${sessionId}/title`, { title })
      .pipe(map(toChatSession));
  }

  updateDocumentType(sessionId: number, documentTypeId: number): Observable<void> {
    return this.http.patch<void>(`${this.url}/${sessionId}/document-type`, {
      document_type_id: documentTypeId,
      updated_at: new Date().toISOString(),
    });
  }

  getOverview(sessionId: number): Observable<SessionOverview> {
    return this.http
      .get<SessionOverviewDto>(`${this.url}/${sessionId}/overview`)
      .pipe(map(toSessionOverview));
  }

  delete(sessionId: number): Observable<void> {
    return this.http.delete<void>(`${this.url}/${sessionId}`);
  }
}
