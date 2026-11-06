import { Component, EventEmitter, Input, Output } from '@angular/core';
import { PromptVersion } from 'src/app/api/prompt/prompt.model';

@Component({
  selector: 'admin-prompt-version-sidebar',
  templateUrl: './prompt-version-sidebar.component.html',
  styleUrls: ['./prompt-version-sidebar.component.css'],
})
export class PromptVersionSidebarComponent {
  @Input() versions: PromptVersion[] = [];
  @Input() loading = false;
  @Input() selectedVersionId: number | null = null;

  @Output() selectedVersionChange = new EventEmitter<PromptVersion>();
  @Output() createVersionRequested = new EventEmitter<void>();
}
