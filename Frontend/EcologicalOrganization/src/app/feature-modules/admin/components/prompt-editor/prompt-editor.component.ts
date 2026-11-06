import { Component, EventEmitter, Input, Output } from '@angular/core';
import { DocumentType } from 'src/app/api/document-type/document-type.model';
import { NewPromptVersion } from 'src/app/api/prompt/prompt-version-api.service';
import { Prompt, PromptVersion } from 'src/app/api/prompt/prompt.model';
import {
  DRAFT_ID,
  NewPrompt,
  PromptVersionBasicInfo,
  PromptVersionText,
} from '../../models/prompt-management.model';

@Component({
  selector: 'admin-prompt-editor',
  templateUrl: './prompt-editor.component.html',
  styleUrls: ['../../admin.styles.css', './prompt-editor.component.css'],
})
export class PromptEditorComponent {
  @Input({ required: true }) prompt!: Prompt;
  @Input() selectedVersion: PromptVersion | null = null;
  @Input() documentTypes: DocumentType[] = [];

  @Output() renamePromptRequested = new EventEmitter<string>();
  @Output() deletePromptRequested = new EventEmitter<number>();
  @Output() saveNewPromptRequested = new EventEmitter<NewPrompt>();
  @Output() createVersionRequested = new EventEmitter<void>();
  @Output() saveNewVersionRequested = new EventEmitter<NewPromptVersion>();
  @Output() saveVersionBasicInfoRequested = new EventEmitter<PromptVersionBasicInfo>();
  @Output() saveVersionPromptTextRequested = new EventEmitter<PromptVersionText>();
  @Output() activateVersionRequested = new EventEmitter<number>();
  @Output() deleteVersionRequested = new EventEmitter<number>();
  @Output() testVersionRequested = new EventEmitter<number>();

  get isNewPrompt(): boolean {
    return this.prompt.id === DRAFT_ID;
  }
}
