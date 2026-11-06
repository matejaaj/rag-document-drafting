import { Component, Input } from '@angular/core';
import { PromptAnalytics } from 'src/app/api/analytics/analytics.model';

@Component({
  selector: 'admin-prompt-analytics',
  templateUrl: './prompt-analytics.component.html',
  styleUrls: ['./prompt-analytics.component.css'],
})
export class PromptAnalyticsComponent {
  @Input() analytics: PromptAnalytics | null = null;

  millisecondsToSeconds(milliseconds: number | null): number | null {
    if (milliseconds == null) return null;
    return Math.round((milliseconds / 1000) * 100) / 100;
  }
}
