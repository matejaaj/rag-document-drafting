import { OutputFeedbackListItem } from 'src/app/api/feedback/output-feedback.model';

export type EvaluationTab = 'analytics' | 'feedback';

export type EvaluationScope = 'prompt' | 'version';

export interface FeedbackListEntry {
  feedback: OutputFeedbackListItem;
  isExpanded: boolean;
  isLoadingDetails: boolean;
}
