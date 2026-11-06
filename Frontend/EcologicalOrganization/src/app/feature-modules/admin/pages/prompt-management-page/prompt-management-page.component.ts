import { Component, OnInit } from '@angular/core';
import { PromptEvaluationStore } from '../../state/prompt-evaluation.store';
import { PromptManagementStore } from '../../state/prompt-management.store';
import { SystemAnalyticsStore } from '../../state/system-analytics.store';

@Component({
  selector: 'admin-prompt-management-page',
  templateUrl: './prompt-management-page.component.html',
  styleUrls: ['./prompt-management-page.component.css'],
  providers: [PromptManagementStore, PromptEvaluationStore, SystemAnalyticsStore],
})
export class PromptManagementPageComponent implements OnInit {
  constructor(
    readonly promptManagement: PromptManagementStore,
    readonly evaluation: PromptEvaluationStore,
    readonly systemAnalytics: SystemAnalyticsStore
  ) {}

  ngOnInit(): void {
    this.promptManagement.load();
  }

  openSystemAnalytics(): void {
    if (this.promptManagement.showSystemAnalytics) return;
    this.promptManagement.openSystemAnalytics();
    this.systemAnalytics.open();
  }
}
