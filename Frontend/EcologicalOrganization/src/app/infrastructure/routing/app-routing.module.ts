import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { HomeComponent } from 'src/app/feature-modules/layout/home/home.component';
import { LoginComponent } from '../auth/login/login.component';
import { AuthGuard } from '../auth/auth.guard';
import { RegistrationComponent } from '../auth/registration/registration.component';
import { WritingAssistantPageComponent } from 'src/app/feature-modules/writing-assistant/pages/writing-assistant-page/writing-assistant-page.component';
import { PromptManagementPageComponent } from 'src/app/feature-modules/admin/pages/prompt-management-page/prompt-management-page.component';
import { DocumentTypeManagementPageComponent } from 'src/app/feature-modules/admin/pages/document-type-management-page/document-type-management-page.component';
import { KnowledgeBaseManagementPageComponent } from 'src/app/feature-modules/admin/pages/knowledge-base-management-page/knowledge-base-management-page.component';
const routes: Routes = [
  { path: '', component: HomeComponent, canActivate: [AuthGuard] },
  { path: 'login', component: LoginComponent },
  {
    path: 'register',
    component: RegistrationComponent,
    canActivate: [AuthGuard],
    data: { roles: ['ADMIN'] },
  },

  { path: 'writing-assistant', component: WritingAssistantPageComponent },
  {
    path: 'writing-assistant/:sessionId',
    component: WritingAssistantPageComponent,
    canActivate: [AuthGuard],
  },
  {
    path: 'dashboard',
    component: PromptManagementPageComponent,
    canActivate: [AuthGuard],
    data: { roles: ['ADMIN'] },
  },
  {
    path: 'document-type-management',
    component: DocumentTypeManagementPageComponent,
    canActivate: [AuthGuard],
    data: { roles: ['ADMIN'] },
  },
  {
    path: 'document-management',
    component: KnowledgeBaseManagementPageComponent,
    canActivate: [AuthGuard],
    data: { roles: ['ADMIN'] },
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes)],
  exports: [RouterModule],
})
export class AppRoutingModule {}
