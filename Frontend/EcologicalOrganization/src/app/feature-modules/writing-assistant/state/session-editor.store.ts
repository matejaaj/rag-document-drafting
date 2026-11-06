import { Injectable } from '@angular/core';
import { AnalyticsApiService } from 'src/app/api/analytics/analytics-api.service';
import { ChatSessionApiService } from 'src/app/api/chat/chat-session-api.service';
import { ChatSession } from 'src/app/api/chat/chat.model';
import { SessionSectionApiService } from 'src/app/api/chat/session-section-api.service';
import { OutputFeedbackApiService } from 'src/app/api/feedback/output-feedback-api.service';
import {
  EditableSection,
  EditableSessionOverview,
  getSectionKey,
  SectionDraftSave,
  SectionFeedbackDialogChange,
  SectionFeedbackSubmit,
  SectionGeneration,
  SectionIterationSelection,
  SectionNameSave,
} from '../models/editable-section.model';

@Injectable()
export class SessionEditorStore {
  activeSession: ChatSession | null = null;
  overview: EditableSessionOverview | null = null;
  downloadingPdf = false;

  constructor(
    private chatSessionApi: ChatSessionApiService,
    private sessionSectionApi: SessionSectionApiService,
    private outputFeedbackApi: OutputFeedbackApiService,
    private analyticsApi: AnalyticsApiService
  ) {}

  get documentTitle(): string {
    return this.overview?.title || this.activeSession?.title || 'Dokument';
  }

  openSession(sessionId: number, knownSession: ChatSession | undefined, onLoadFailed: () => void): void {
    this.activeSession = knownSession ?? { id: sessionId, templateId: 0, createdBy: 0, documentTypeId: 0, title: '' };
    this.chatSessionApi.getOverview(sessionId).subscribe({
      next: (overview) => {
        this.overview = overview;
        if (this.activeSession) {
          this.activeSession = { ...this.activeSession, documentTypeId: overview.documentTypeId };
        }
      },
      error: () => onLoadFailed(),
    });
  }

  renameSession(title: string, onRenamed: (sessionId: number, title: string) => void): void {
    const session = this.activeSession;
    if (!session) return;
    this.chatSessionApi.updateTitle(session.id, title).subscribe((updated) => {
      const newTitle = updated.title ?? '';
      this.activeSession = { ...session, title: newTitle };
      if (this.overview) {
        this.overview = { ...this.overview, title: newTitle };
      }
      onRenamed(session.id, newTitle);
    });
  }

  changeDocumentType(documentTypeId: number): void {
    const session = this.activeSession;
    if (!session) return;
    this.activeSession = { ...session, documentTypeId };
    this.chatSessionApi.updateDocumentType(session.id, documentTypeId).subscribe({
      error: () => {
        if (this.activeSession) {
          this.activeSession = { ...this.activeSession, documentTypeId: session.documentTypeId };
        }
      },
    });
  }

  changeGlobalInstruction(text: string): void {
    if (!this.overview) return;
    this.overview = { ...this.overview, latestGlobalInstructionText: text };
  }

  addSection(): void {
    if (!this.overview || !this.activeSession) return;
    const lastPosition = this.overview.sections.reduce((max, section) => Math.max(max, section.position ?? 0), 0);
    const newSection: EditableSection = {
      id: 0,
      sessionId: this.activeSession.id,
      name: '',
      position: lastPosition + 1,
      latestIteration: null,
      isUnsaved: true,
      temporaryKey: 'unsaved-' + Math.random().toString(36).slice(2),
    };
    this.overview = { ...this.overview, sections: [...this.overview.sections, newSection] };
  }

  saveSectionName({ section, name }: SectionNameSave): void {
    if (!this.activeSession) return;

    if (section.isUnsaved || !section.id) {
      const position = section.position ?? 1;
      this.sessionSectionApi.create({ sessionId: this.activeSession.id, name, position }).subscribe((created) =>
        this.updateSection(section, {
          id: created.id,
          sessionId: created.sessionId,
          name: created.name,
          position: created.position,
          isUnsaved: undefined,
          temporaryKey: undefined,
        })
      );
      return;
    }

    this.sessionSectionApi
      .updateTitle(section.id, name)
      .subscribe((updated) => this.updateSection(section, { name: updated.name }));
  }

  deleteSection(section: EditableSection): void {
    if (section.isUnsaved || !section.id) {
      this.removeSection(section);
      return;
    }
    this.sessionSectionApi.delete(section.id).subscribe(() => this.removeSection(section));
  }

  generateSectionText({ section, instructionText }: SectionGeneration): void {
    if (!this.overview) return;
    const instructions = {
      sectionInstruction: instructionText,
      globalInstruction: this.overview.latestGlobalInstructionText,
    };
    this.updateSection(section, { generating: true });
    this.sessionSectionApi.generateIteration(section.id, instructions).subscribe({
      next: (iteration) =>
        this.updateSection(section, {
          latestIteration: iteration,
          maxSeqNo: Math.max(section.maxSeqNo ?? 0, iteration.seqNo),
          generating: false,
        }),
      error: () => this.updateSection(section, { generating: false }),
    });
  }

  loadSectionIteration({ section, seqNo }: SectionIterationSelection): void {
    this.updateSection(section, { loadingIteration: true });
    this.sessionSectionApi.getIteration(section.id, seqNo).subscribe({
      next: (iteration) => this.updateSection(section, { latestIteration: iteration, loadingIteration: false }),
      error: () => this.updateSection(section, { loadingIteration: false }),
    });
  }

  saveSectionDraft({ section, seqNo, text }: SectionDraftSave): void {
    this.updateSection(section, { savingDraft: true });
    this.sessionSectionApi.saveDraft(section.id, seqNo, text).subscribe({
      next: (iteration) => this.updateSection(section, { latestIteration: iteration, savingDraft: false }),
      error: () => this.updateSection(section, { savingDraft: false }),
    });
  }

  setFeedbackDialogOpen({ section, open }: SectionFeedbackDialogChange): void {
    this.updateSection(section, { feedbackDialogOpen: open });
  }

  submitFeedback({ section, feedback }: SectionFeedbackSubmit): void {
    this.updateSection(section, { submittingFeedback: true });
    this.outputFeedbackApi.create(feedback).subscribe({
      next: () => this.updateSection(section, { submittingFeedback: false, feedbackDialogOpen: false }),
      error: () => this.updateSection(section, { submittingFeedback: false }),
    });
  }

  downloadPdf(): void {
    if (!this.activeSession || !this.overview || this.downloadingPdf) return;

    const title = this.documentTitle;
    const selections = this.overview.sections
      .filter((section) => !!section.id)
      .map((section) => ({ sectionId: section.id, seqNo: section.latestIteration?.seqNo }));

    this.downloadingPdf = true;
    this.analyticsApi.downloadDocumentReportPdf(this.activeSession.id, title, selections).subscribe({
      next: (pdf) => {
        const url = window.URL.createObjectURL(pdf);
        const link = document.createElement('a');
        link.href = url;
        link.download = title + '.pdf';
        link.click();
        window.URL.revokeObjectURL(url);
        this.downloadingPdf = false;
      },
      error: () => (this.downloadingPdf = false),
    });
  }

  private updateSection(section: EditableSection, changes: Partial<EditableSection>): void {
    if (!this.overview) return;
    const key = getSectionKey(section);
    this.overview = {
      ...this.overview,
      sections: this.overview.sections.map((item) => (getSectionKey(item) === key ? { ...item, ...changes } : item)),
    };
  }

  private removeSection(section: EditableSection): void {
    if (!this.overview) return;
    const key = getSectionKey(section);
    this.overview = {
      ...this.overview,
      sections: this.overview.sections.filter((item) => getSectionKey(item) !== key),
    };
  }
}
