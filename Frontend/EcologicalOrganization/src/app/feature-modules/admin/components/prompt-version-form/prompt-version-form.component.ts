import {
  AfterViewInit,
  Component,
  ElementRef,
  EventEmitter,
  Input,
  OnChanges,
  OnDestroy,
  Output,
  SimpleChanges,
  ViewChild,
} from '@angular/core';
import { NewPromptVersion } from 'src/app/api/prompt/prompt-version-api.service';
import { PromptVersion } from 'src/app/api/prompt/prompt.model';
import { DRAFT_ID, PromptVersionBasicInfo, PromptVersionText } from '../../models/prompt-management.model';

type SaveStatus = 'unsaved' | 'saved';

const SAVE_STATUS_MESSAGES: Record<SaveStatus, string> = {
  unsaved: 'Promene nisu sačuvane',
  saved: 'Promene uspešno sačuvane',
};

const SAVED_MESSAGE_DURATION_MS = 2000;

@Component({
  selector: 'admin-prompt-version-form',
  templateUrl: './prompt-version-form.component.html',
  styleUrls: ['../../admin.styles.css', './prompt-version-form.component.css'],
})
export class PromptVersionFormComponent implements OnChanges, AfterViewInit, OnDestroy {
  @Input({ required: true }) version!: PromptVersion;

  @Output() saveBasicInfoRequested = new EventEmitter<PromptVersionBasicInfo>();
  @Output() savePromptTextRequested = new EventEmitter<PromptVersionText>();
  @Output() activateRequested = new EventEmitter<number>();
  @Output() deleteRequested = new EventEmitter<number>();
  @Output() saveNewVersionRequested = new EventEmitter<NewPromptVersion>();
  @Output() testRequested = new EventEmitter<number>();

  @ViewChild('promptTextArea') promptTextArea?: ElementRef<HTMLTextAreaElement>;

  readonly saveStatusMessages = SAVE_STATUS_MESSAGES;

  nameDraft = '';
  descriptionDraft = '';
  promptTextDraft = '';
  basicInfoStatus: SaveStatus | null = null;
  promptTextStatus: SaveStatus | null = null;

  private basicInfoStatusTimer: ReturnType<typeof setTimeout> | null = null;
  private promptTextStatusTimer: ReturnType<typeof setTimeout> | null = null;

  ngOnChanges(changes: SimpleChanges): void {
    const versionChange = changes['version'];
    if (!versionChange || versionChange.previousValue?.id === versionChange.currentValue?.id) return;

    this.nameDraft = this.version.name ?? '';
    this.descriptionDraft = this.version.description ?? '';
    this.promptTextDraft = this.version.promptText ?? '';
    this.clearStatusTimers();
    this.basicInfoStatus = null;
    this.promptTextStatus = null;
    setTimeout(() => this.resizePromptTextArea(), 0);
  }

  ngAfterViewInit(): void {
    setTimeout(() => this.resizePromptTextArea(), 0);
  }

  ngOnDestroy(): void {
    this.clearStatusTimers();
  }

  get isActive(): boolean {
    return !!this.version.isActive;
  }

  get isNew(): boolean {
    return !!this.version.isNew || this.version.id === DRAFT_ID;
  }

  onBasicInfoChange(): void {
    if (this.isNew) return;
    const isChanged =
      this.nameDraft.trim() !== (this.version.name ?? '') ||
      this.descriptionDraft.trim() !== (this.version.description ?? '');
    if (isChanged) this.clearBasicInfoStatusTimer();
    this.basicInfoStatus = isChanged ? 'unsaved' : null;
  }

  onPromptTextChange(): void {
    this.resizePromptTextArea();
    if (this.isNew) return;
    const isChanged = this.promptTextDraft.trim() !== (this.version.promptText ?? '');
    if (isChanged) this.clearPromptTextStatusTimer();
    this.promptTextStatus = isChanged ? 'unsaved' : null;
  }

  saveBasicInfo(): void {
    this.saveBasicInfoRequested.emit({
      versionId: this.version.id,
      name: this.nameDraft.trim(),
      description: this.descriptionDraft.trim(),
    });
    this.basicInfoStatus = 'saved';
    this.clearBasicInfoStatusTimer();
    this.basicInfoStatusTimer = setTimeout(() => {
      if (this.basicInfoStatus === 'saved') this.basicInfoStatus = null;
    }, SAVED_MESSAGE_DURATION_MS);
  }

  savePromptText(): void {
    this.savePromptTextRequested.emit({
      versionId: this.version.id,
      promptText: this.promptTextDraft.trim(),
    });
    this.promptTextStatus = 'saved';
    this.clearPromptTextStatusTimer();
    this.promptTextStatusTimer = setTimeout(() => {
      if (this.promptTextStatus === 'saved') this.promptTextStatus = null;
    }, SAVED_MESSAGE_DURATION_MS);
  }

  saveNewVersion(): void {
    this.saveNewVersionRequested.emit({
      promptId: this.version.promptId,
      name: this.nameDraft.trim(),
      description: this.descriptionDraft.trim(),
      promptText: this.promptTextDraft.trim(),
    });
  }

  private resizePromptTextArea(): void {
    const textArea = this.promptTextArea?.nativeElement;
    if (!textArea) return;
    textArea.style.height = 'auto';
    textArea.style.overflowY = 'hidden';
    textArea.style.height = textArea.scrollHeight + 'px';
  }

  private clearBasicInfoStatusTimer(): void {
    if (this.basicInfoStatusTimer) clearTimeout(this.basicInfoStatusTimer);
    this.basicInfoStatusTimer = null;
  }

  private clearPromptTextStatusTimer(): void {
    if (this.promptTextStatusTimer) clearTimeout(this.promptTextStatusTimer);
    this.promptTextStatusTimer = null;
  }

  private clearStatusTimers(): void {
    this.clearBasicInfoStatusTimer();
    this.clearPromptTextStatusTimer();
  }
}
