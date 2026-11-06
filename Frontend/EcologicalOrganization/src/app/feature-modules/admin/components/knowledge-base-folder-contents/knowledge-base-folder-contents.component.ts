import { Component, EventEmitter, Input, Output } from '@angular/core';
import { RepoFolder, StorageObject } from 'src/app/api/knowledge-base/knowledge-base.model';

const FILE_SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB'];

@Component({
  selector: 'admin-knowledge-base-folder-contents',
  templateUrl: './knowledge-base-folder-contents.component.html',
  styleUrls: ['./knowledge-base-folder-contents.component.css'],
})
export class KnowledgeBaseFolderContentsComponent {
  @Input() folders: RepoFolder[] = [];
  @Input() files: StorageObject[] = [];
  @Input() loading = false;
  @Input() deletingFolderIds = new Set<number>();
  @Input() deletingFileIds = new Set<number>();

  @Output() openFolderRequested = new EventEmitter<RepoFolder>();
  @Output() deleteFolderRequested = new EventEmitter<RepoFolder>();
  @Output() showSummaryRequested = new EventEmitter<StorageObject>();
  @Output() deleteFileRequested = new EventEmitter<StorageObject>();

  formatFileSize(sizeBytes: number): string {
    let size = sizeBytes;
    let unitIndex = 0;
    while (size >= 1024 && unitIndex < FILE_SIZE_UNITS.length - 1) {
      size = size / 1024;
      unitIndex++;
    }
    return `${size.toFixed(size < 10 && unitIndex > 0 ? 1 : 0)} ${FILE_SIZE_UNITS[unitIndex]}`;
  }
}
