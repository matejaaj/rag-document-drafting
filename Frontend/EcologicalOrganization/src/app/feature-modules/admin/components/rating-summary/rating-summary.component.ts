import { Component, Input } from '@angular/core';
import { PromptAnalytics } from 'src/app/api/analytics/analytics.model';

@Component({
  selector: 'admin-rating-summary',
  templateUrl: './rating-summary.component.html',
  styleUrls: ['./rating-summary.component.css'],
})
export class RatingSummaryComponent {
  @Input() analytics: PromptAnalytics | null = null;

  readonly stars = [1, 2, 3, 4, 5];

  get ratingBars(): { rating: number; count: number; widthPercent: number }[] {
    const counts = [
      { rating: 5, count: this.analytics?.ratingC5 ?? 0 },
      { rating: 4, count: this.analytics?.ratingC4 ?? 0 },
      { rating: 3, count: this.analytics?.ratingC3 ?? 0 },
      { rating: 2, count: this.analytics?.ratingC2 ?? 0 },
      { rating: 1, count: this.analytics?.ratingC1 ?? 0 },
    ];
    const highestCount = Math.max(1, ...counts.map((bar) => bar.count));
    return counts.map((bar) => ({ ...bar, widthPercent: (bar.count / highestCount) * 100 }));
  }

  filledStarCount(rating: number | null | undefined): number {
    const clamped = typeof rating === 'number' ? Math.max(0, Math.min(5, rating)) : 0;
    return Math.round(clamped);
  }
}
