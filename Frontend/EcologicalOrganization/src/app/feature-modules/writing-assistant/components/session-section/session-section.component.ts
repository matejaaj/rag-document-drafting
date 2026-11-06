import { Component, ElementRef, EventEmitter, Input, OnChanges, Output, SimpleChanges, ViewChild } from '@angular/core';
import { NewOutputFeedback } from 'src/app/api/feedback/output-feedback.model';
import {
  EditableSection,
  SectionDraftSave,
  SectionFeedbackDialogChange,
  SectionFeedbackSubmit,
  SectionGeneration,
  SectionIterationSelection,
  SectionNameSave,
} from '../../models/editable-section.model';

@Component({
  selector: 'wa-session-section',
  templateUrl: './session-section.component.html',
  styleUrls: ['../../writing-assistant.styles.css', './session-section.component.css'],
})
export class SessionSectionComponent implements OnChanges {
  @Input() section!: EditableSection;

  @Output() saveNameRequested = new EventEmitter<SectionNameSave>();
  @Output() deleteRequested = new EventEmitter<EditableSection>();
  @Output() generateRequested = new EventEmitter<SectionGeneration>();
  @Output() loadIterationRequested = new EventEmitter<SectionIterationSelection>();
  @Output() saveDraftRequested = new EventEmitter<SectionDraftSave>();
  @Output() feedbackDialogOpenChange = new EventEmitter<SectionFeedbackDialogChange>();
  @Output() submitFeedbackRequested = new EventEmitter<SectionFeedbackSubmit>();

  @ViewChild('resultTextarea') resultTextarea?: ElementRef<HTMLTextAreaElement>;

  instructionText = '';
  editingTitle = false;
  titleDraft = '';
  invalidTitle = false;

  currentSeqNo = 0;
  maxSeqNo = 0;

  resultDraft = '';
  resultStatus: 'unsaved' | 'saved' | null = null;
  private resultStatusTimer: ReturnType<typeof setTimeout> | null = null;

  ngOnChanges(changes: SimpleChanges): void {
    const previous: EditableSection | undefined = changes['section'].previousValue;

    // Only a new iteration replaces the text; other updates keep unsaved edits.
    if (!previous || previous.latestIteration !== this.section.latestIteration) {
      this.showLatestIteration();
    }
    if (previous?.savingDraft && !this.section.savingDraft && !this.hasUnsavedResult) {
      this.showSavedStatus();
    }
  }

  get showIterationNav(): boolean {
    return !!this.currentSeqNo && this.maxSeqNo > 1 && !this.section.isUnsaved;
  }

  get hasUnsavedResult(): boolean {
    return this.resultDraft.trim() !== this.latestResultText.trim();
  }

  startTitleEdit(): void {
    this.editingTitle = true;
    this.titleDraft = this.section.name ?? '';
    this.invalidTitle = false;
  }

  saveTitle(): void {
    const name = this.titleDraft.trim();
    if (!name) {
      this.invalidTitle = true;
      return;
    }
    this.invalidTitle = false;
    this.saveNameRequested.emit({ section: this.section, name });
    this.editingTitle = false;
  }

  cancelTitleEdit(): void {
    if (this.section.isUnsaved && !this.section.name) {
      this.titleDraft = 'Sekcija';
      this.saveTitle();
      return;
    }
    this.editingTitle = false;
    this.invalidTitle = false;
    this.titleDraft = this.section.name ?? '';
  }

  generate(): void {
    if (this.section.generating || this.section.loadingIteration) return;
    this.generateRequested.emit({ section: this.section, instructionText: this.instructionText });
  }

  onResultChange(): void {
    this.autoGrowResult();
    if (this.currentSeqNo === 0) return;
    this.clearResultStatus();
    if (this.hasUnsavedResult) this.resultStatus = 'unsaved';
  }

  saveDraft(): void {
    if (this.currentSeqNo === 0 || !this.hasUnsavedResult) return;
    this.saveDraftRequested.emit({ section: this.section, seqNo: this.currentSeqNo, text: this.resultDraft.trim() });
  }

  showPreviousIteration(): void {
    if (this.currentSeqNo > 1) {
      this.loadIterationRequested.emit({ section: this.section, seqNo: this.currentSeqNo - 1 });
    }
  }

  showNextIteration(): void {
    if (this.currentSeqNo < this.maxSeqNo) {
      this.loadIterationRequested.emit({ section: this.section, seqNo: this.currentSeqNo + 1 });
    }
  }

  openFeedbackDialog(): void {
    if (!this.section.latestIteration?.modelOutput?.id) return;
    this.feedbackDialogOpenChange.emit({ section: this.section, open: true });
  }

  closeFeedbackDialog(): void {
    this.feedbackDialogOpenChange.emit({ section: this.section, open: false });
  }

  submitFeedback(feedback: NewOutputFeedback): void {
    this.submitFeedbackRequested.emit({ section: this.section, feedback });
  }

  private get latestResultText(): string {
    const iteration = this.section.latestIteration;
    return iteration?.sectionDraft?.content ?? iteration?.modelOutput?.generatedText ?? '';
  }

  private showLatestIteration(): void {
    const iteration = this.section.latestIteration;
    this.instructionText = iteration?.sectionInstruction?.text ?? '';
    this.editingTitle = !!this.section.isUnsaved;
    this.titleDraft = this.section.name ?? '';
    this.currentSeqNo = iteration?.seqNo ?? 0;
    this.maxSeqNo = this.section.maxSeqNo ?? iteration?.seqNo ?? 0;
    this.resultDraft = this.latestResultText;
    this.clearResultStatus();
    setTimeout(() => this.autoGrowResult(), 0);
  }

  private showSavedStatus(): void {
    this.clearResultStatus();
    this.resultStatus = 'saved';
    this.resultStatusTimer = setTimeout(() => (this.resultStatus = null), 2000);
  }

  private clearResultStatus(): void {
    if (this.resultStatusTimer) clearTimeout(this.resultStatusTimer);
    this.resultStatusTimer = null;
    this.resultStatus = null;
  }

  private autoGrowResult(): void {
    const textarea = this.resultTextarea?.nativeElement;
    if (!textarea) return;
    textarea.style.height = 'auto';
    textarea.style.overflowY = 'hidden';
    textarea.style.height = textarea.scrollHeight + 'px';
  }
}
