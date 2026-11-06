import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { SharedModule } from 'src/app/shared/shared.module';
import { WritingAssistantPageComponent } from './pages/writing-assistant-page/writing-assistant-page.component';
import { ConversationsSidebarComponent } from './components/conversations-sidebar/conversations-sidebar.component';
import { TemplatesSidebarComponent } from './components/templates-sidebar/templates-sidebar.component';
import { TemplateUploadDialogComponent } from './components/template-upload-dialog/template-upload-dialog.component';
import { WelcomeScreenComponent } from './components/welcome-screen/welcome-screen.component';
import { SessionEditorComponent } from './components/session-editor/session-editor.component';
import { SessionHeaderComponent } from './components/session-header/session-header.component';
import { SessionSectionComponent } from './components/session-section/session-section.component';
import { OutputFeedbackDialogComponent } from './components/output-feedback-dialog/output-feedback-dialog.component';
import { DocumentPreviewComponent } from './components/document-preview/document-preview.component';

@NgModule({
  declarations: [
    WritingAssistantPageComponent,
    ConversationsSidebarComponent,
    TemplatesSidebarComponent,
    TemplateUploadDialogComponent,
    WelcomeScreenComponent,
    SessionEditorComponent,
    SessionHeaderComponent,
    SessionSectionComponent,
    OutputFeedbackDialogComponent,
    DocumentPreviewComponent,
  ],
  imports: [CommonModule, FormsModule, SharedModule],
})
export class WritingAssistantModule {}
