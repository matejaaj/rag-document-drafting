import { SessionOverview, SessionSectionWithLatestIteration } from 'src/app/api/chat/chat.model';
import { NewOutputFeedback } from 'src/app/api/feedback/output-feedback.model';

export interface EditableSection extends SessionSectionWithLatestIteration {
  isUnsaved?: boolean;
  temporaryKey?: string;
  generating?: boolean;
  loadingIteration?: boolean;
  savingDraft?: boolean;
  feedbackDialogOpen?: boolean;
  submittingFeedback?: boolean;
}

export interface EditableSessionOverview extends SessionOverview {
  sections: EditableSection[];
}

export function getSectionKey(section: EditableSection): string {
  return section.temporaryKey ?? String(section.id);
}

export interface SectionNameSave {
  section: EditableSection;
  name: string;
}

export interface SectionGeneration {
  section: EditableSection;
  instructionText: string;
}

export interface SectionIterationSelection {
  section: EditableSection;
  seqNo: number;
}

export interface SectionDraftSave {
  section: EditableSection;
  seqNo: number;
  text: string;
}

export interface SectionFeedbackDialogChange {
  section: EditableSection;
  open: boolean;
}

export interface SectionFeedbackSubmit {
  section: EditableSection;
  feedback: NewOutputFeedback;
}
