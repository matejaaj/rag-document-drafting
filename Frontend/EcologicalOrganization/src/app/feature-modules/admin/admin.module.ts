import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SharedModule } from 'src/app/shared/shared.module';
import { DocumentTypeReportFiltersComponent } from './components/document-type-report-filters/document-type-report-filters.component';
import { DocumentTypeReportTableComponent } from './components/document-type-report-table/document-type-report-table.component';
import { DocumentTypeTableComponent } from './components/document-type-table/document-type-table.component';
import { KnowledgeBaseFolderContentsComponent } from './components/knowledge-base-folder-contents/knowledge-base-folder-contents.component';
import { KnowledgeBaseToolbarComponent } from './components/knowledge-base-toolbar/knowledge-base-toolbar.component';
import { PromptAnalyticsComponent } from './components/prompt-analytics/prompt-analytics.component';
import { PromptDetailsFormComponent } from './components/prompt-details-form/prompt-details-form.component';
import { PromptEditorComponent } from './components/prompt-editor/prompt-editor.component';
import { PromptEvaluationComponent } from './components/prompt-evaluation/prompt-evaluation.component';
import { PromptFeedbackListComponent } from './components/prompt-feedback-list/prompt-feedback-list.component';
import { PromptSidebarComponent } from './components/prompt-sidebar/prompt-sidebar.component';
import { PromptVersionFormComponent } from './components/prompt-version-form/prompt-version-form.component';
import { PromptVersionSidebarComponent } from './components/prompt-version-sidebar/prompt-version-sidebar.component';
import { RatingSummaryComponent } from './components/rating-summary/rating-summary.component';
import { SystemAnalyticsComponent } from './components/system-analytics/system-analytics.component';
import { DocumentTypeManagementPageComponent } from './pages/document-type-management-page/document-type-management-page.component';
import { KnowledgeBaseManagementPageComponent } from './pages/knowledge-base-management-page/knowledge-base-management-page.component';
import { PromptManagementPageComponent } from './pages/prompt-management-page/prompt-management-page.component';

@NgModule({
  declarations: [
    PromptManagementPageComponent,
    DocumentTypeManagementPageComponent,
    KnowledgeBaseManagementPageComponent,
    PromptSidebarComponent,
    PromptVersionSidebarComponent,
    PromptEditorComponent,
    PromptDetailsFormComponent,
    PromptVersionFormComponent,
    PromptEvaluationComponent,
    PromptAnalyticsComponent,
    PromptFeedbackListComponent,
    RatingSummaryComponent,
    SystemAnalyticsComponent,
    DocumentTypeReportFiltersComponent,
    DocumentTypeReportTableComponent,
    DocumentTypeTableComponent,
    KnowledgeBaseToolbarComponent,
    KnowledgeBaseFolderContentsComponent,
  ],
  imports: [CommonModule, FormsModule, SharedModule],
})
export class AdminModule {}
