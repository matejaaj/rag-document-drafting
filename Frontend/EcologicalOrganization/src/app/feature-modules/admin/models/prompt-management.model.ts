export const DRAFT_ID = -1;

export const PROMPTS_PER_PAGE = 20;

export interface NewPrompt {
  title: string;
  documentTypeId: number;
}

export interface PromptVersionBasicInfo {
  versionId: number;
  name: string;
  description: string;
}

export interface PromptVersionText {
  versionId: number;
  promptText: string;
}
