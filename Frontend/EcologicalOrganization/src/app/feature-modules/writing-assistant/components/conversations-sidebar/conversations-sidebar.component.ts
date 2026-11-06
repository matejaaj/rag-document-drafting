import {
  Component,
  ElementRef,
  EventEmitter,
  HostListener,
  Input,
  OnChanges,
  Output,
  SimpleChanges,
  ViewChild,
} from '@angular/core';
import { ChatSession } from 'src/app/api/chat/chat.model';

@Component({
  selector: 'wa-conversations-sidebar',
  templateUrl: './conversations-sidebar.component.html',
  styleUrls: ['../../../../shared/sidebar.css', './conversations-sidebar.component.css'],
})
export class ConversationsSidebarComponent implements OnChanges {
  @Input() conversations: ChatSession[] = [];
  @Input() loading = false;
  @Input() loadingMore = false;
  @Input() selectedConversationId?: number;
  @Input() showAdminLink = false;

  @Output() createRequested = new EventEmitter<void>();
  @Output() openRequested = new EventEmitter<ChatSession>();
  @Output() deleteRequested = new EventEmitter<ChatSession>();
  @Output() searchTermChange = new EventEmitter<string>();
  @Output() loadMoreRequested = new EventEmitter<void>();
  @Output() homeRequested = new EventEmitter<void>();
  @Output() logoutRequested = new EventEmitter<void>();

  @ViewChild('scrollArea') scrollArea?: ElementRef<HTMLDivElement>;

  openMenuConversationId: number | null = null;

  ngOnChanges(changes: SimpleChanges): void {
    const previous: ChatSession[] | undefined = changes['conversations']?.previousValue;
    const current: ChatSession[] | undefined = changes['conversations']?.currentValue;
    if (previous && current && current.length <= 20 && current.length < previous.length) {
      this.scrollToTop();
    }
  }

  toggleMenu(conversationId: number): void {
    this.openMenuConversationId = this.openMenuConversationId === conversationId ? null : conversationId;
  }

  deleteConversation(conversation: ChatSession): void {
    this.deleteRequested.emit(conversation);
    this.openMenuConversationId = null;
  }

  @HostListener('document:click', ['$event'])
  closeMenuOnOutsideClick(event: Event): void {
    if (!(event.target as HTMLElement).closest('.menu-wrap')) {
      this.openMenuConversationId = null;
    }
  }

  search(term: string): void {
    this.scrollToTop();
    this.searchTermChange.emit(term);
  }

  private scrollToTop(): void {
    if (this.scrollArea) this.scrollArea.nativeElement.scrollTop = 0;
  }
}
