import { Component, EventEmitter, Input, Output } from '@angular/core';
import { PromptAnalytics } from 'src/app/api/analytics/analytics.model';
import { EvaluationScope, EvaluationTab, FeedbackListEntry } from '../../models/prompt-evaluation.model';

@Component({
  selector: 'admin-prompt-evaluation',
  templateUrl: './prompt-evaluation.component.html',
  styleUrls: ['./prompt-evaluation.component.css'],
})
export class PromptEvaluationComponent {
  @Input() activeTab: EvaluationTab = 'analytics';
  @Input() scope: EvaluationScope = 'prompt';
  @Input() loading = false;
  @Input() error: string | null = null;
  @Input() analytics: PromptAnalytics | null = null;
  @Input() feedbackEntries: FeedbackListEntry[] = [];
  @Input() feedbackPage = 1;
  @Input() feedbackPageCount = 1;

  @Output() activeTabChange = new EventEmitter<EvaluationTab>();
  @Output() scopeChange = new EventEmitter<EvaluationScope>();
  @Output() previousFeedbackPageRequested = new EventEmitter<void>();
  @Output() nextFeedbackPageRequested = new EventEmitter<void>();
  @Output() toggleFeedbackDetailsRequested = new EventEmitter<FeedbackListEntry>();
}
