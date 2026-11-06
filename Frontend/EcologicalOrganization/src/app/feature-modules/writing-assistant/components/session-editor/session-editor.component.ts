import { Component, EventEmitter, Input, Output } from '@angular/core';
import { ChatSession } from 'src/app/api/chat/chat.model';
import { DocumentType } from 'src/app/api/document-type/document-type.model';
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
} from '../../models/editable-section.model';

@Component({
  selector: 'wa-session-editor',
  templateUrl: './session-editor.component.html',
  styleUrls: ['../../writing-assistant.styles.css', './session-editor.component.css'],
})
export class SessionEditorComponent {
  @Input() session!: ChatSession;
  @Input() overview!: EditableSessionOverview;
  @Input() documentTypes: DocumentType[] = [];

  @Output() saveTitleRequested = new EventEmitter<string>();
  @Output() documentTypeChange = new EventEmitter<number>();
  @Output() globalInstructionChange = new EventEmitter<string>();
  @Output() addSectionRequested = new EventEmitter<void>();
  @Output() openPreviewRequested = new EventEmitter<void>();
  @Output() saveSectionNameRequested = new EventEmitter<SectionNameSave>();
  @Output() deleteSectionRequested = new EventEmitter<EditableSection>();
  @Output() generateSectionRequested = new EventEmitter<SectionGeneration>();
  @Output() loadSectionIterationRequested = new EventEmitter<SectionIterationSelection>();
  @Output() saveSectionDraftRequested = new EventEmitter<SectionDraftSave>();
  @Output() feedbackDialogOpenChange = new EventEmitter<SectionFeedbackDialogChange>();
  @Output() submitFeedbackRequested = new EventEmitter<SectionFeedbackSubmit>();

  trackBySectionKey = (_index: number, section: EditableSection) => getSectionKey(section);
}
