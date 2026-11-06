import { Injectable } from '@angular/core';
import { ChatSessionApiService } from 'src/app/api/chat/chat-session-api.service';
import { ChatSession } from 'src/app/api/chat/chat.model';

const PAGE_SIZE = 20;

@Injectable()
export class ConversationsStore {
  conversations: ChatSession[] = [];
  loading = true;
  loadingMore = false;
  hasMore = false;
  creatingConversation = false;

  private page = 1;
  private searchTerm?: string;

  constructor(private chatSessionApi: ChatSessionApiService) {}

  loadConversations(): void {
    this.loading = true;
    this.page = 1;
    this.loadPage();
  }

  searchConversations(searchTerm: string): void {
    this.searchTerm = searchTerm.trim() || undefined;
    this.loadConversations();
  }

  loadMoreConversations(): void {
    if (!this.hasMore || this.loading || this.loadingMore) return;
    this.loadingMore = true;
    this.page += 1;
    this.loadPage();
  }

  createConversation(templateId: number, onCreated: (conversation: ChatSession) => void): void {
    this.creatingConversation = true;
    this.chatSessionApi.create(templateId).subscribe({
      next: (conversation) => {
        this.conversations = [conversation, ...this.conversations];
        this.creatingConversation = false;
        onCreated(conversation);
      },
      error: () => (this.creatingConversation = false),
    });
  }

  deleteConversation(conversation: ChatSession, onDeleted: () => void): void {
    this.chatSessionApi.delete(conversation.id).subscribe(() => {
      this.conversations = this.conversations.filter((item) => item.id !== conversation.id);
      onDeleted();
    });
  }

  updateConversationTitle(conversationId: number, title: string): void {
    this.conversations = this.conversations.map((conversation) =>
      conversation.id === conversationId ? { ...conversation, title } : conversation
    );
  }

  private loadPage(): void {
    const append = this.page > 1;
    this.chatSessionApi.list(this.page, PAGE_SIZE, this.searchTerm).subscribe({
      next: (result) => {
        this.conversations = append ? [...this.conversations, ...result.items] : result.items;
        this.hasMore = this.conversations.length < result.meta.totalCount;
        this.loading = false;
        this.loadingMore = false;
      },
      error: () => {
        this.loading = false;
        this.loadingMore = false;
      },
    });
  }
}
