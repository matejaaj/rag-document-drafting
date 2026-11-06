import { Component, ElementRef, EventEmitter, HostListener, Input, Output, ViewChild } from '@angular/core';
import { takeUntilDestroyed } from '@angular/core/rxjs-interop';
import { Subject } from 'rxjs';
import { debounceTime, distinctUntilChanged, map } from 'rxjs/operators';

@Component({
  selector: 'app-search-box',
  templateUrl: './search-box.component.html',
  styleUrls: ['./search-box.component.css'],
})
export class SearchBoxComponent {
  @Input() placeholder = '';
  @Input() inputId?: string;
  @Input() collapsible = false;
  @Output() searchTermChange = new EventEmitter<string>();

  @ViewChild('input') input?: ElementRef<HTMLInputElement>;

  open = false;
  searchTerm = '';

  private readonly typedSearchTerms$ = new Subject<string>();

  constructor() {
    this.typedSearchTerms$
      .pipe(
        map((term) => term.trim()),
        debounceTime(300),
        distinctUntilChanged(),
        takeUntilDestroyed()
      )
      .subscribe((term) => this.searchTermChange.emit(term));
  }

  toggle(): void {
    if (this.open) {
      this.clear();
      return;
    }
    this.open = true;
    setTimeout(() => this.input?.nativeElement.focus());
  }

  changeSearchTerm(term: string): void {
    this.searchTerm = term;
    this.typedSearchTerms$.next(term);
  }

  @HostListener('document:keydown.escape')
  closeOnEscape(): void {
    if (this.open) this.clear();
  }

  clear(): void {
    if (this.searchTerm) this.searchTermChange.emit('');
    this.searchTerm = '';
    this.open = false;
  }
}
