import { ChangeDetectionStrategy, Component, EventEmitter, Input, Output } from '@angular/core';
import { SessionSectionWithLatestIteration } from 'src/app/api/chat/chat.model';

@Component({
  selector: 'wa-document-preview',
  templateUrl: './document-preview.component.html',
  styleUrls: ['./document-preview.component.css'],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DocumentPreviewComponent {
  @Input() title = '';
  @Input() sections: SessionSectionWithLatestIteration[] = [];
  @Input() downloading = false;

  @Output() closeRequested = new EventEmitter<void>();
  @Output() downloadPdfRequested = new EventEmitter<void>();

  get sectionsInOrder(): SessionSectionWithLatestIteration[] {
    return [...this.sections].sort((first, second) => (first.position ?? 0) - (second.position ?? 0));
  }

  getSectionText(section: SessionSectionWithLatestIteration): string {
    const iteration = section.latestIteration;
    return iteration?.sectionDraft?.content ?? iteration?.modelOutput?.generatedText ?? '';
  }

  trackById = (_index: number, section: SessionSectionWithLatestIteration) => section.id;
}
