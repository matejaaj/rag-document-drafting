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
import { Prompt } from 'src/app/api/prompt/prompt.model';
import { PROMPTS_PER_PAGE } from '../../models/prompt-management.model';

@Component({
  selector: 'admin-prompt-sidebar',
  templateUrl: './prompt-sidebar.component.html',
  styleUrls: ['../../../../shared/sidebar.css', './prompt-sidebar.component.css'],
})
export class PromptSidebarComponent implements OnChanges {
  @Input() prompts: Prompt[] = [];
  @Input() loading = false;
  @Input() loadingMore = false;
  @Input() selectedPromptId: number | null = null;

  @Output() createPromptRequested = new EventEmitter<void>();
  @Output() selectedPromptChange = new EventEmitter<Prompt>();
  @Output() deletePromptRequested = new EventEmitter<number>();
  @Output() openSystemAnalyticsRequested = new EventEmitter<void>();
  @Output() searchTermChange = new EventEmitter<string>();
  @Output() loadMoreRequested = new EventEmitter<void>();
  @Output() logoutRequested = new EventEmitter<void>();

  @ViewChild('scrollArea') scrollArea?: ElementRef<HTMLDivElement>;

  openMenuPromptId: number | null = null;

  ngOnChanges(changes: SimpleChanges): void {
    const promptsChange = changes['prompts'];
    if (!promptsChange?.previousValue) return;
    const previousCount = (promptsChange.previousValue as Prompt[]).length;
    const currentCount = (promptsChange.currentValue as Prompt[]).length;
    // Reloaded from the first page (e.g. a new search): scroll to top.
    if (currentCount <= PROMPTS_PER_PAGE && currentCount < previousCount) this.scrollToTop();
  }

  toggleMenu(promptId: number): void {
    this.openMenuPromptId = this.openMenuPromptId === promptId ? null : promptId;
  }

  requestDelete(promptId: number): void {
    this.deletePromptRequested.emit(promptId);
    this.openMenuPromptId = null;
  }

  @HostListener('document:click', ['$event'])
  closeMenuOnOutsideClick(event: Event): void {
    if (!(event.target as HTMLElement).closest('.menu-wrap')) this.openMenuPromptId = null;
  }

  search(term: string): void {
    this.scrollToTop();
    this.searchTermChange.emit(term);
  }

  private scrollToTop(): void {
    if (this.scrollArea) this.scrollArea.nativeElement.scrollTop = 0;
  }
}
