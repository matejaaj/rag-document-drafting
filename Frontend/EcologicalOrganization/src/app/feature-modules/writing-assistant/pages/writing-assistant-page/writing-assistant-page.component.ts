import { Component, DestroyRef, OnInit } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { ActivatedRoute, Router } from '@angular/router';
import { distinctUntilChanged, filter, map } from 'rxjs/operators';
import { ChatSession } from 'src/app/api/chat/chat.model';
import { Template } from 'src/app/api/template/template.model';
import { AuthService } from 'src/app/infrastructure/auth/auth.service';
import { ConversationsStore } from '../../state/conversations.store';
import { SessionEditorStore } from '../../state/session-editor.store';
import { TemplatesStore } from '../../state/templates.store';

@Component({
  selector: 'wa-writing-assistant-page',
  templateUrl: './writing-assistant-page.component.html',
  styleUrls: ['./writing-assistant-page.component.css'],
  providers: [ConversationsStore, TemplatesStore, SessionEditorStore],
})
export class WritingAssistantPageComponent implements OnInit {
  showAdminLink = false;
  templatesSidebarVisible = false;
  previewVisible = false;

  constructor(
    public conversationsStore: ConversationsStore,
    public templatesStore: TemplatesStore,
    public sessionEditorStore: SessionEditorStore,
    private route: ActivatedRoute,
    private router: Router,
    private authService: AuthService,
    private destroyRef: DestroyRef
  ) {}

  ngOnInit(): void {
    this.authService.user$
      .pipe(takeUntilDestroyed(this.destroyRef))
      .subscribe((user) => (this.showAdminLink = user.role === 'ADMIN'));

    this.conversationsStore.loadConversations();
    this.templatesStore.loadDocumentTypes();

    this.route.paramMap
      .pipe(
        map((params) => params.get('sessionId')),
        filter((sessionId): sessionId is string => !!sessionId),
        map(Number),
        distinctUntilChanged(),
        takeUntilDestroyed(this.destroyRef)
      )
      .subscribe((sessionId) => this.openSession(sessionId));
  }

  openTemplatesSidebar(): void {
    this.previewVisible = false;
    if (this.templatesSidebarVisible) return;
    this.templatesSidebarVisible = true;
    this.templatesStore.loadTemplates();
  }

  createConversation(template: Template): void {
    this.conversationsStore.createConversation(template.id, (conversation) => {
      this.templatesSidebarVisible = false;
      this.router.navigate(['/writing-assistant', conversation.id]);
    });
  }

  openConversation(conversation: ChatSession): void {
    this.templatesSidebarVisible = false;
    this.previewVisible = false;
    if (this.sessionEditorStore.activeSession?.id !== conversation.id) {
      this.router.navigate(['/writing-assistant', conversation.id]);
    }
  }

  deleteConversation(conversation: ChatSession): void {
    this.conversationsStore.deleteConversation(conversation, () => {
      // Navigating away recreates the page, which clears the editor.
      if (this.sessionEditorStore.activeSession?.id === conversation.id) {
        this.router.navigate(['/writing-assistant']);
      }
    });
  }

  renameSession(title: string): void {
    this.sessionEditorStore.renameSession(title, (sessionId, newTitle) =>
      this.conversationsStore.updateConversationTitle(sessionId, newTitle)
    );
  }

  goHome(): void {
    this.router.navigate(['/writing-assistant']);
  }

  logout(): void {
    this.authService.logout();
  }

  private openSession(sessionId: number): void {
    this.previewVisible = false;
    const conversation = this.conversationsStore.conversations.find((item) => item.id === sessionId);
    this.sessionEditorStore.openSession(sessionId, conversation, () => this.router.navigate(['/writing-assistant']));
  }
}
