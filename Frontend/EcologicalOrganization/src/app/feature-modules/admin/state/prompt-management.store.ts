import { Injectable } from '@angular/core';
import { MatSnackBar } from '@angular/material/snack-bar';
import { Router } from '@angular/router';
import { ChatSessionApiService } from 'src/app/api/chat/chat-session-api.service';
import { DocumentTypeApiService } from 'src/app/api/document-type/document-type-api.service';
import { DocumentType } from 'src/app/api/document-type/document-type.model';
import { PromptApiService } from 'src/app/api/prompt/prompt-api.service';
import { NewPromptVersion, PromptVersionApiService } from 'src/app/api/prompt/prompt-version-api.service';
import { Prompt, PromptVersion } from 'src/app/api/prompt/prompt.model';
import { AuthService } from 'src/app/infrastructure/auth/auth.service';
import {
  DRAFT_ID,
  NewPrompt,
  PROMPTS_PER_PAGE,
  PromptVersionBasicInfo,
  PromptVersionText,
} from '../models/prompt-management.model';
import { PromptEvaluationStore } from './prompt-evaluation.store';

@Injectable()
export class PromptManagementStore {
  prompts: Prompt[] = [];
  loadingPrompts = true;
  loadingMorePrompts = false;
  hasMorePrompts = false;
  selectedPrompt: Prompt | null = null;

  versions: PromptVersion[] = [];
  loadingVersions = false;
  selectedVersion: PromptVersion | null = null;

  documentTypes: DocumentType[] = [];
  showSystemAnalytics = false;

  private page = 1;
  private searchTerm?: string;

  constructor(
    private promptApi: PromptApiService,
    private promptVersionApi: PromptVersionApiService,
    private documentTypeApi: DocumentTypeApiService,
    private chatSessionApi: ChatSessionApiService,
    private authService: AuthService,
    private router: Router,
    private evaluation: PromptEvaluationStore,
    private snackBar: MatSnackBar
  ) {}

  get showVersionsSidebar(): boolean {
    return this.selectedPrompt !== null;
  }

  load(): void {
    this.documentTypeApi.list().subscribe((page) => (this.documentTypes = page.items));
    this.loadPrompts();
  }

  search(searchTerm?: string): void {
    this.searchTerm = (searchTerm ?? '').trim() || undefined;
    this.loadPrompts();
  }

  loadMorePrompts(): void {
    if (!this.hasMorePrompts || this.loadingPrompts || this.loadingMorePrompts) return;
    this.loadingMorePrompts = true;
    this.page += 1;

    this.promptApi.list(this.page, PROMPTS_PER_PAGE, this.searchTerm).subscribe({
      next: (page) => {
        this.prompts = [...this.prompts, ...page.items];
        this.loadingMorePrompts = false;
        this.hasMorePrompts = this.prompts.length < page.meta.totalCount;
      },
      error: () => (this.loadingMorePrompts = false),
    });
  }

  selectPrompt(prompt: Prompt): void {
    this.showSystemAnalytics = false;
    this.selectedPrompt = prompt;
    this.setSelectedVersion(prompt.activeVersion ?? null);
    this.loadVersions(prompt.id);
  }

  createDraftPrompt(): void {
    this.showSystemAnalytics = false;
    const documentTypeId = this.defaultDocumentTypeId();
    if (documentTypeId === null) {
      this.snackBar.open('Nije učitan nijedan tip dokumenta. Pokušaj ponovo.', 'Zatvori', { duration: 5000 });
      return;
    }

    this.selectedPrompt = {
      id: DRAFT_ID,
      title: '',
      documentTypeId,
      isActive: false,
      activeVersion: null,
      updatedAt: null,
    };
    this.versions = [];
    this.setSelectedVersion(null);
  }

  saveNewPrompt(newPrompt: NewPrompt): void {
    this.promptApi.create(newPrompt.title, newPrompt.documentTypeId).subscribe((created) => {
      this.prompts = [created, ...this.prompts];
      this.selectedPrompt = created;
      this.setSelectedVersion(null);
    });
  }

  renamePrompt(title: string): void {
    const prompt = this.selectedPrompt;
    if (!prompt || prompt.id === DRAFT_ID) return;

    this.selectedPrompt = { ...prompt, title };
    this.prompts = this.prompts.map((listedPrompt) =>
      listedPrompt.id === prompt.id ? { ...listedPrompt, title } : listedPrompt
    );
    this.promptApi.updateTitle(prompt.id, title).subscribe();
  }

  deletePrompt(promptId: number): void {
    if (!promptId) return;
    if (!window.confirm('Da li sigurno želiš da obrišeš ovaj prompt?')) return;

    this.promptApi.delete(promptId).subscribe(() => {
      this.prompts = this.prompts.filter((prompt) => prompt.id !== promptId);
      if (this.selectedPrompt?.id !== promptId) return;

      const nextPrompt = this.prompts[0];
      if (nextPrompt) {
        this.selectPrompt(nextPrompt);
      } else {
        this.selectedPrompt = null;
        this.versions = [];
        this.setSelectedVersion(null);
        this.router.navigate(['/dashboard']);
      }
    });
  }

  openSystemAnalytics(): void {
    this.showSystemAnalytics = true;
    this.selectedPrompt = null;
    this.versions = [];
    this.setSelectedVersion(null);
  }

  logOut(): void {
    this.authService.logout();
  }

  selectVersion(version: PromptVersion): void {
    if (!this.selectedPrompt) return;
    this.setSelectedVersion(version);
  }

  createDraftVersion(): void {
    if (!this.selectedPrompt) return;

    const draft: PromptVersion = {
      id: DRAFT_ID,
      promptId: this.selectedPrompt.id,
      name: draftVersionName(new Date()),
      description: '',
      promptText: '',
      isActive: false,
      createdAt: null,
      updatedAt: null,
      isNew: true,
    };
    this.versions = [draft, ...this.versions];
    this.setSelectedVersion(draft);
  }

  saveNewVersion(newVersion: NewPromptVersion): void {
    this.promptVersionApi.create(newVersion).subscribe((created) => {
      if (!this.selectedPrompt) return;
      this.versions = [created, ...this.versions.filter((version) => !version.isNew)];
      this.setSelectedVersion(created);
    });
  }

  saveVersionBasicInfo({ versionId, name, description }: PromptVersionBasicInfo): void {
    if (!this.selectedVersion) return;
    this.promptVersionApi.updateBasicInfo(versionId, name, description).subscribe((saved) =>
      this.mergeSavedVersion(versionId, {
        name: saved.name,
        description: saved.description,
        updatedAt: saved.updatedAt,
      })
    );
  }

  saveVersionPromptText({ versionId, promptText }: PromptVersionText): void {
    if (!this.selectedVersion) return;
    this.promptVersionApi.updatePromptText(versionId, promptText).subscribe((saved) =>
      this.mergeSavedVersion(versionId, { promptText: saved.promptText, updatedAt: saved.updatedAt })
    );
  }

  activateVersion(versionId: number): void {
    const prompt = this.selectedPrompt;
    if (!prompt) return;

    this.promptVersionApi.activate(versionId).subscribe((activated) => {
      const activeVersion = {
        ...(this.versions.find((version) => version.id === activated.id) ?? activated),
        isActive: true,
      };
      // Only one prompt per document type can be active.
      this.prompts = this.prompts.map((listedPrompt) => {
        if (listedPrompt.documentTypeId !== prompt.documentTypeId) return listedPrompt;
        return listedPrompt.id === prompt.id
          ? { ...listedPrompt, isActive: true, activeVersion }
          : { ...listedPrompt, isActive: false, activeVersion: null };
      });

      if (this.selectedPrompt?.id !== prompt.id) return;
      this.versions = this.versions.map((version) => ({ ...version, isActive: version.id === activated.id }));
      this.selectedPrompt = { ...this.selectedPrompt, isActive: true, activeVersion };
      this.setSelectedVersion(activeVersion);
    });
  }

  deleteVersion(versionId: number): void {
    if (!versionId || !this.selectedPrompt) return;
    if (!window.confirm('Da li sigurno želiš da obrišeš ovu verziju?')) return;

    this.promptVersionApi.delete(versionId).subscribe(() => {
      if (this.selectedVersion?.id === versionId) this.setSelectedVersion(null);
      if (this.selectedPrompt) this.loadVersions(this.selectedPrompt.id);
    });
  }

  testVersion(versionId: number): void {
    const promptTitle = this.selectedPrompt?.title || 'Prompt';
    const versionName = this.selectedVersion?.name || 'Verzija';
    const title = `Test - ${promptTitle} ${versionName} - ${new Date().toLocaleString('sr-RS')}`;

    this.chatSessionApi
      .createTestSession(versionId, title)
      .subscribe((session) => this.router.navigate(['/writing-assistant', session.id]));
  }

  private loadPrompts(): void {
    this.loadingPrompts = true;
    this.page = 1;

    this.promptApi.list(this.page, PROMPTS_PER_PAGE, this.searchTerm).subscribe({
      next: (page) => {
        this.prompts = page.items;
        this.loadingPrompts = false;
        this.loadingMorePrompts = false;
        this.hasMorePrompts = this.prompts.length < page.meta.totalCount;

        const promptToOpen = this.prompts.find((prompt) => prompt.isActive) ?? this.prompts[0];
        if (promptToOpen && !this.selectedPrompt && !this.showSystemAnalytics) {
          this.selectPrompt(promptToOpen);
        }
      },
      error: () => {
        this.loadingPrompts = false;
        this.loadingMorePrompts = false;
      },
    });
  }

  private loadVersions(promptId: number): void {
    this.loadingVersions = true;
    this.promptVersionApi.listForPrompt(promptId).subscribe({
      next: (versions) => {
        this.versions = versions;
        this.loadingVersions = false;
        const versionToSelect = versions.find((version) => version.isActive) ?? versions[0];
        if (versionToSelect) this.selectVersion(versionToSelect);
      },
      error: () => {
        this.versions = [];
        this.loadingVersions = false;
      },
    });
  }

  private mergeSavedVersion(versionId: number, savedFields: Partial<PromptVersion>): void {
    this.versions = this.versions.map((version) =>
      version.id === versionId ? { ...version, ...savedFields } : version
    );
    if (this.selectedVersion?.id === versionId) {
      this.selectedVersion = { ...this.selectedVersion, ...savedFields };
    }
  }

  private setSelectedVersion(version: PromptVersion | null): void {
    this.selectedVersion = version;
    this.evaluation.showFor(this.selectedPrompt?.id ?? null, version?.id ?? null);
  }

  private defaultDocumentTypeId(): number | null {
    const defaultType = this.documentTypes.find((documentType) => documentType.name === 'Default');
    return defaultType?.id ?? this.documentTypes[0]?.id ?? null;
  }
}

function draftVersionName(date: Date): string {
  const twoDigits = (value: number) => String(value).padStart(2, '0');
  const day = `${date.getFullYear()}/${twoDigits(date.getMonth() + 1)}/${twoDigits(date.getDate())}`;
  const time = `${twoDigits(date.getHours())}:${twoDigits(date.getMinutes())}:${twoDigits(date.getSeconds())}`;
  const milliseconds = String(date.getMilliseconds()).padStart(3, '0');
  return `v - ${day} ${time}.${milliseconds}`;
}
