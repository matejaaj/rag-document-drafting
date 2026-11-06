import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { WRITING_ASSISTANT_API_URL } from '../common/api-url';
import { PageDto } from '../common/page.model';
import { PromptVersion, PromptVersionDto, toPromptVersion } from './prompt.model';

export interface NewPromptVersion {
  promptId: number;
  name: string;
  description: string;
  promptText: string;
}

@Injectable({ providedIn: 'root' })
export class PromptVersionApiService {
  private readonly url = `${WRITING_ASSISTANT_API_URL}/prompt-versions`;

  constructor(private http: HttpClient) {}

  listForPrompt(promptId: number, page = 1, perPage = 50): Observable<PromptVersion[]> {
    return this.http
      .get<PageDto<PromptVersionDto>>(this.url, { params: { prompt_id: promptId, page, per_page: perPage } })
      .pipe(map((dto) => (dto.items || []).map(toPromptVersion)));
  }

  create(version: NewPromptVersion): Observable<PromptVersion> {
    const body = {
      prompt_id: version.promptId,
      name: version.name,
      description: version.description,
      prompt_text: version.promptText,
    };
    return this.http.post<PromptVersionDto>(this.url, body).pipe(map(toPromptVersion));
  }

  updateBasicInfo(versionId: number, name: string, description: string): Observable<PromptVersion> {
    return this.http
      .patch<PromptVersionDto>(`${this.url}/${versionId}/basic-info`, { name, description })
      .pipe(map(toPromptVersion));
  }

  updatePromptText(versionId: number, promptText: string): Observable<PromptVersion> {
    return this.http
      .patch<PromptVersionDto>(`${this.url}/${versionId}/prompt-text`, { prompt_text: promptText })
      .pipe(map(toPromptVersion));
  }

  activate(versionId: number): Observable<PromptVersion> {
    return this.http
      .post<PromptVersionDto>(`${this.url}/${versionId}/activate`, {})
      .pipe(map(toPromptVersion));
  }

  delete(versionId: number): Observable<void> {
    return this.http.delete<void>(`${this.url}/${versionId}`);
  }
}
