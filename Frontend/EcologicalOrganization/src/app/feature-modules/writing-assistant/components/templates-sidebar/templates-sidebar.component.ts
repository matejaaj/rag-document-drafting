import { Component, ElementRef, EventEmitter, HostListener, Input, Output, ViewChild } from '@angular/core';
import { DocumentType } from 'src/app/api/document-type/document-type.model';
import { Template } from 'src/app/api/template/template.model';
import { TemplateUpload } from '../../models/template-upload.model';

@Component({
  selector: 'wa-templates-sidebar',
  templateUrl: './templates-sidebar.component.html',
  styleUrls: ['../../../../shared/sidebar.css', './templates-sidebar.component.css'],
})
export class TemplatesSidebarComponent {
  @Input() templates: Template[] = [];
  @Input() documentTypes: DocumentType[] = [];
  @Input() loading = false;
  @Input() loadingMore = false;
  @Input() creatingConversation = false;
  @Input() deletingTemplateId: number | null = null;
  @Input() uploadDialogOpen = false;
  @Input() uploading = false;

  @Output() closeRequested = new EventEmitter<void>();
  @Output() createConversationRequested = new EventEmitter<Template>();
  @Output() deleteRequested = new EventEmitter<Template>();
  @Output() searchTermChange = new EventEmitter<string>();
  @Output() loadMoreRequested = new EventEmitter<void>();
  @Output() uploadDialogOpenChange = new EventEmitter<boolean>();
  @Output() uploadRequested = new EventEmitter<TemplateUpload>();

  @ViewChild('scrollArea') scrollArea?: ElementRef<HTMLDivElement>;

  openMenuTemplateId: number | null = null;

  @HostListener('document:click', ['$event'])
  closeMenuOnOutsideClick(event: Event): void {
    if (!(event.target as HTMLElement).closest('.menu-wrap')) {
      this.openMenuTemplateId = null;
    }
  }

  toggleMenu(templateId: number): void {
    this.openMenuTemplateId = this.openMenuTemplateId === templateId ? null : templateId;
  }

  selectTemplate(template: Template): void {
    if (this.openMenuTemplateId === template.id) return;
    this.createConversationRequested.emit(template);
  }

  deleteTemplate(template: Template): void {
    this.openMenuTemplateId = null;
    this.deleteRequested.emit(template);
  }

  search(term: string): void {
    this.scrollToTop();
    this.searchTermChange.emit(term);
  }

  private scrollToTop(): void {
    if (this.scrollArea) this.scrollArea.nativeElement.scrollTop = 0;
  }
}
