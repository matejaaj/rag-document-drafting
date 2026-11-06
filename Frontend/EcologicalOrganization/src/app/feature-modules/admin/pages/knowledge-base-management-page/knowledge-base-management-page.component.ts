import { Component, OnInit } from '@angular/core';
import { KnowledgeBaseManagementStore } from '../../state/knowledge-base-management.store';

@Component({
  selector: 'admin-knowledge-base-management-page',
  templateUrl: './knowledge-base-management-page.component.html',
  styleUrls: ['./knowledge-base-management-page.component.css'],
  providers: [KnowledgeBaseManagementStore],
})
export class KnowledgeBaseManagementPageComponent implements OnInit {
  constructor(readonly knowledgeBase: KnowledgeBaseManagementStore) {}

  ngOnInit(): void {
    this.knowledgeBase.load();
  }
}
