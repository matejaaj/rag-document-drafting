import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { WRITING_ASSISTANT_API_URL } from '../common/api-url';
import {
  SectionIteration,
  SectionIterationDto,
  SessionSection,
  SessionSectionDto,
  toSectionIteration,
  toSessionSection,
} from './chat.model';

export interface NewSessionSection {
  sessionId: number;
  name: string;
  position: number;
  templateSectionId?: number | null;
}

export interface GenerationInstructions {
  sectionInstruction?: string;
  globalInstruction?: string;
}

@Injectable({ providedIn: 'root' })
export class SessionSectionApiService {
  private readonly url = `${WRITING_ASSISTANT_API_URL}/session-sections`;

  constructor(private http: HttpClient) {}

  create(section: NewSessionSection): Observable<SessionSection> {
    const body: Record<string, unknown> = {
      session_id: section.sessionId,
      name: section.name,
      position: section.position,
    };
    if (section.templateSectionId !== undefined) {
      body['template_section_id'] = section.templateSectionId;
    }
    return this.http.post<SessionSectionDto>(this.url, body).pipe(map(toSessionSection));
  }

  updateTitle(sectionId: number, name: string): Observable<SessionSection> {
    return this.http
      .patch<SessionSectionDto>(`${this.url}/${sectionId}/title`, { name })
      .pipe(map(toSessionSection));
  }

  delete(sectionId: number): Observable<void> {
    return this.http.delete<void>(`${this.url}/${sectionId}`);
  }

  generateIteration(sectionId: number, instructions: GenerationInstructions): Observable<SectionIteration> {
    const body = {
      section_instruction: instructions.sectionInstruction ?? null,
      global_instruction: instructions.globalInstruction ?? null,
    };
    return this.http
      .post<SectionIterationDto>(`${this.url}/${sectionId}/iterations`, body)
      .pipe(map(toSectionIteration));
  }

  getIteration(sectionId: number, seqNo: number): Observable<SectionIteration> {
    return this.http
      .get<SectionIterationDto>(`${this.url}/${sectionId}/iterations/${seqNo}`)
      .pipe(map(toSectionIteration));
  }

  saveDraft(sectionId: number, seqNo: number, content: string): Observable<SectionIteration> {
    return this.http
      .put<SectionIterationDto>(`${this.url}/${sectionId}/iterations/${seqNo}/draft`, { content })
      .pipe(map(toSectionIteration));
  }
}
