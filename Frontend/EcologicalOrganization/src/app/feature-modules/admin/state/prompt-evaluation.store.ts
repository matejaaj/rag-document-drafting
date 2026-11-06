import { Injectable } from '@angular/core';
import { Subscription } from 'rxjs';
import { finalize } from 'rxjs/operators';
import { AnalyticsApiService } from 'src/app/api/analytics/analytics-api.service';
import { PromptAnalytics } from 'src/app/api/analytics/analytics.model';
import { OutputFeedbackApiService } from 'src/app/api/feedback/output-feedback-api.service';
import { EvaluationScope, EvaluationTab, FeedbackListEntry } from '../models/prompt-evaluation.model';

const FEEDBACK_PER_PAGE = 5;

@Injectable()
export class PromptEvaluationStore {
  isVisible = false;
  activeTab: EvaluationTab = 'analytics';
  scope: EvaluationScope = 'prompt';
  loading = false;
  error: string | null = null;

  analytics: PromptAnalytics | null = null;

  feedbackEntries: FeedbackListEntry[] = [];
  feedbackPage = 1;
  feedbackPageCount = 1;

  private promptId = 0;
  private versionId = 0;
  private loadedAnalyticsKey: string | null = null;
  private loadedFeedbackKey: string | null = null;
  private analyticsRequest?: Subscription;
  private feedbackRequest?: Subscription;

  constructor(
    private analyticsApi: AnalyticsApiService,
    private outputFeedbackApi: OutputFeedbackApiService
  ) {}

  showFor(promptId: number | null, versionId: number | null): void {
    const isSavedVersion = promptId !== null && promptId > 0 && versionId !== null && versionId > 0;
    if (!isSavedVersion) {
      this.isVisible = false;
      return;
    }
    if (this.isVisible && promptId === this.promptId && versionId === this.versionId) return;

    if (!this.isVisible) this.reset();
    this.isVisible = true;
    this.promptId = promptId;
    this.versionId = versionId;
    this.feedbackPage = 1;
    this.loadAnalytics();
    this.loadFeedback();
  }

  switchTab(tab: EvaluationTab): void {
    if (this.activeTab === tab) return;
    this.activeTab = tab;
    if (tab === 'analytics') this.loadAnalytics();
    else this.loadFeedback();
  }

  switchScope(scope: EvaluationScope): void {
    if (this.scope === scope) return;
    this.scope = scope;
    this.feedbackPage = 1;
    this.loadAnalytics();
    this.loadFeedback();
  }

  showPreviousFeedbackPage(): void {
    if (this.feedbackPage <= 1) return;
    this.feedbackPage--;
    this.loadFeedback();
  }

  showNextFeedbackPage(): void {
    if (this.feedbackPage >= this.feedbackPageCount) return;
    this.feedbackPage++;
    this.loadFeedback();
  }

  toggleFeedbackDetails(entry: FeedbackListEntry): void {
    entry.isExpanded = !entry.isExpanded;
    if (!entry.isExpanded || entry.feedback.details || entry.isLoadingDetails) return;

    entry.isLoadingDetails = true;
    this.outputFeedbackApi.get(entry.feedback.id).subscribe({
      next: (feedback) => {
        entry.feedback = { ...entry.feedback, details: feedback.details ?? null };
        entry.isLoadingDetails = false;
      },
      error: () => (entry.isLoadingDetails = false),
    });
  }

  private loadAnalytics(): void {
    const key = `${this.scope}:${this.promptId}:${this.versionId}`;
    if (this.loadedAnalyticsKey === key) return;

    this.analyticsRequest?.unsubscribe();
    this.loading = this.activeTab === 'analytics';
    this.error = null;
    const request =
      this.scope === 'prompt'
        ? this.analyticsApi.getPromptAnalytics(this.promptId)
        : this.analyticsApi.getVersionAnalytics(this.versionId);

    this.analyticsRequest = request.pipe(finalize(() => (this.loading = false))).subscribe({
      next: (analytics) => {
        this.analytics = analytics;
        this.loadedAnalyticsKey = key;
      },
      error: () => {
        if (this.activeTab === 'analytics') this.error = 'Učitavanje nije uspelo.';
        this.analytics = null;
      },
    });
  }

  private loadFeedback(): void {
    if (this.activeTab !== 'feedback') return;
    const key = `${this.scope}:${this.promptId}:${this.versionId}:${this.feedbackPage}`;
    if (this.loadedFeedbackKey === key) return;

    this.feedbackRequest?.unsubscribe();
    this.loading = true;
    this.error = null;
    const request =
      this.scope === 'prompt'
        ? this.outputFeedbackApi.listForPrompt(this.promptId, this.feedbackPage, FEEDBACK_PER_PAGE)
        : this.outputFeedbackApi.listForVersion(this.versionId, this.feedbackPage, FEEDBACK_PER_PAGE);

    this.feedbackRequest = request.pipe(finalize(() => (this.loading = false))).subscribe({
      next: (page) => {
        this.feedbackEntries = page.items.map((feedback) => ({
          feedback,
          isExpanded: false,
          isLoadingDetails: false,
        }));
        this.feedbackPageCount = Math.max(1, Math.ceil(page.meta.totalCount / FEEDBACK_PER_PAGE));
        this.loadedFeedbackKey = key;
      },
      error: () => {
        this.error = 'Učitavanje ocena nije uspelo.';
        this.feedbackEntries = [];
        this.feedbackPageCount = 1;
      },
    });
  }

  private reset(): void {
    this.analyticsRequest?.unsubscribe();
    this.feedbackRequest?.unsubscribe();
    this.activeTab = 'analytics';
    this.scope = 'prompt';
    this.loading = false;
    this.error = null;
    this.analytics = null;
    this.loadedAnalyticsKey = null;
    this.feedbackEntries = [];
    this.feedbackPageCount = 1;
    this.loadedFeedbackKey = null;
  }
}
