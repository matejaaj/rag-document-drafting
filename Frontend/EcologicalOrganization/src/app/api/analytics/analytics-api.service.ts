import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { WRITING_ASSISTANT_API_URL } from '../common/api-url';
import {
  DocumentReportSectionSelection,
  DocumentTypeReportRow,
  DocumentTypeReportRowDto,
  PromptAnalytics,
  PromptAnalyticsDto,
  toDocumentTypeReportRow,
  toPromptAnalytics,
} from './analytics.model';

export type SortDirection = 'asc' | 'desc';

@Injectable({ providedIn: 'root' })
export class AnalyticsApiService {
  private readonly url = `${WRITING_ASSISTANT_API_URL}/analytics`;

  constructor(private http: HttpClient) {}

  getPromptAnalytics(promptId: number): Observable<PromptAnalytics> {
    return this.http
      .get<PromptAnalyticsDto>(`${this.url}/prompts/${promptId}`)
      .pipe(map(toPromptAnalytics));
  }

  getVersionAnalytics(versionId: number): Observable<PromptAnalytics> {
    return this.http
      .get<PromptAnalyticsDto>(`${this.url}/prompt-versions/${versionId}`)
      .pipe(map(toPromptAnalytics));
  }

  getDocumentTypeReport(
    fromIso: string,
    toIso: string,
    documentTypeId: number | null = null,
    includeTotal = true
  ): Observable<DocumentTypeReportRow[]> {
    let params = new HttpParams()
      .set('from_ts', fromIso)
      .set('to_ts', toIso)
      .set('include_total', String(includeTotal));
    if (documentTypeId !== null && documentTypeId !== undefined) {
      params = params.set('document_type_id', String(documentTypeId));
    }
    return this.http
      .get<DocumentTypeReportRowDto[]>(`${this.url}/document-type-report`, { params })
      .pipe(map((rows) => rows.map(toDocumentTypeReportRow)));
  }

  downloadDocumentTypeReportPdf(
    fromIso: string,
    toIso: string,
    documentTypeId: number | null,
    includeTotal: boolean,
    sortKey: string,
    sortDirection: SortDirection,
    timezone?: string
  ): Observable<Blob> {
    let params = new HttpParams()
      .set('from_ts', fromIso)
      .set('to_ts', toIso)
      .set('include_total', String(includeTotal))
      .set('sort_key', sortKey)
      .set('sort_direction', sortDirection);
    if (timezone) params = params.set('timezone', timezone);
    if (documentTypeId !== null && documentTypeId !== undefined) {
      params = params.set('document_type_id', String(documentTypeId));
    }
    return this.http.get(`${this.url}/document-type-report.pdf`, { params, responseType: 'blob' });
  }

  downloadDocumentReportPdf(
    sessionId: number,
    title: string | null,
    selections: DocumentReportSectionSelection[]
  ): Observable<Blob> {
    const body = {
      title: title && title.trim() ? title.trim() : null,
      selections: (selections || []).map((selection) => ({
        section_id: selection.sectionId,
        seq_no: selection.seqNo,
      })),
    };
    return this.http.post(`${this.url}/document-report.pdf`, body, {
      params: { session_id: String(sessionId) },
      responseType: 'blob',
    });
  }
}
