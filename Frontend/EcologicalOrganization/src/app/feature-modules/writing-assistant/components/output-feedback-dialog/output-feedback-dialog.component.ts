import { Component, EventEmitter, HostListener, Input, Output } from '@angular/core';
import { NewOutputFeedback } from 'src/app/api/feedback/output-feedback.model';

@Component({
  selector: 'wa-output-feedback-dialog',
  templateUrl: './output-feedback-dialog.component.html',
  styleUrls: ['./output-feedback-dialog.component.css', '../../writing-assistant.styles.css'],
})
export class OutputFeedbackDialogComponent {
  @Input() modelOutputId = 0;
  @Input() submitting = false;

  @Output() closeRequested = new EventEmitter<void>();
  @Output() submitRequested = new EventEmitter<NewOutputFeedback>();

  readonly ratings = [1, 2, 3, 4, 5];
  ratingValue: number | null = null;
  hoverRating = 0;
  commentText = '';

  @HostListener('document:keydown.escape')
  cancel(): void {
    if (!this.submitting) this.closeRequested.emit();
  }

  submit(): void {
    if (!this.modelOutputId || !this.ratingValue) return;
    this.submitRequested.emit({
      modelOutputId: this.modelOutputId,
      ratingValue: this.ratingValue,
      commentText: this.commentText.trim() || null,
    });
  }

  autoGrow(event: Event): void {
    const textarea = event.target as HTMLTextAreaElement;
    textarea.style.height = 'auto';
    textarea.style.overflowY = 'hidden';
    textarea.style.height = textarea.scrollHeight + 'px';
  }
}
