import { Component, EventEmitter, Input, Output } from '@angular/core';
import { PromptAnalytics } from 'src/app/api/analytics/analytics.model';
import { FeedbackListEntry } from '../../models/prompt-evaluation.model';

@Component({
  selector: 'admin-prompt-feedback-list',
  templateUrl: './prompt-feedback-list.component.html',
  styleUrls: ['./prompt-feedback-list.component.css'],
})
export class PromptFeedbackListComponent {
  @Input() analytics: PromptAnalytics | null = null;
  @Input() entries: FeedbackListEntry[] = [];
  @Input() page = 1;
  @Input() pageCount = 1;

  @Output() previousPageRequested = new EventEmitter<void>();
  @Output() nextPageRequested = new EventEmitter<void>();
  @Output() toggleDetailsRequested = new EventEmitter<FeedbackListEntry>();

  readonly starValues = [1, 2, 3, 4, 5];
}
