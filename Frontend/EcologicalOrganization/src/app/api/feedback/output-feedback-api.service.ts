import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { WRITING_ASSISTANT_API_URL } from '../common/api-url';
import { Page, PageDto, toPage } from '../common/page.model';
import {
  NewOutputFeedback,
  OutputFeedback,
  OutputFeedbackDto,
  OutputFeedbackListItem,
  OutputFeedbackListItemDto,
  toOutputFeedback,
  toOutputFeedbackListItem,
} from './output-feedback.model';

@Injectable({ providedIn: 'root' })
export class OutputFeedbackApiService {
  private readonly url = `${WRITING_ASSISTANT_API_URL}/output-feedback`;

  constructor(private http: HttpClient) {}

  create(feedback: NewOutputFeedback): Observable<OutputFeedback> {
    const body: Record<string, unknown> = {
      model_output_id: feedback.modelOutputId,
      rating_value: feedback.ratingValue,
    };
    if (feedback.commentText && feedback.commentText.trim()) {
      body['comment_text'] = feedback.commentText.trim();
    }
    return this.http.post<OutputFeedbackDto>(this.url, body).pipe(map(toOutputFeedback));
  }

  listForPrompt(promptId: number, page = 1, perPage = 5): Observable<Page<OutputFeedbackListItem>> {
    const params = new HttpParams().set('page', page).set('per_page', perPage);
    return this.http
      .get<PageDto<OutputFeedbackListItemDto>>(`${this.url}/by-prompt/${promptId}`, { params })
      .pipe(map((dto) => toPage(dto, toOutputFeedbackListItem)));
  }

  listForVersion(versionId: number, page = 1, perPage = 5): Observable<Page<OutputFeedbackListItem>> {
    const params = new HttpParams().set('page', page).set('per_page', perPage);
    return this.http
      .get<PageDto<OutputFeedbackListItemDto>>(`${this.url}/by-version/${versionId}`, { params })
      .pipe(map((dto) => toPage(dto, toOutputFeedbackListItem)));
  }

  get(feedbackId: number): Observable<OutputFeedbackListItem> {
    return this.http
      .get<OutputFeedbackListItemDto>(`${this.url}/${feedbackId}`)
      .pipe(map(toOutputFeedbackListItem));
  }
}
