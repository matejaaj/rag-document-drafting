import { Component, OnInit } from '@angular/core';
import { Location } from '@angular/common';
import { DocumentTypeManagementStore } from '../../state/document-type-management.store';

@Component({
  selector: 'admin-document-type-management-page',
  templateUrl: './document-type-management-page.component.html',
  styleUrls: ['./document-type-management-page.component.css', '../../admin.styles.css'],
  providers: [DocumentTypeManagementStore],
})
export class DocumentTypeManagementPageComponent implements OnInit {
  constructor(
    readonly documentTypeManagement: DocumentTypeManagementStore,
    private location: Location
  ) {}

  ngOnInit(): void {
    this.documentTypeManagement.load();
  }

  goBack(): void {
    this.location.back();
  }
}
