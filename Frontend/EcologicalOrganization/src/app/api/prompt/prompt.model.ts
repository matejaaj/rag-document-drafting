export interface PromptVersion {
  id: number;
  promptId: number;
  name: string | null;
  description: string | null;
  promptText: string | null;
  isActive?: boolean;
  createdAt?: string | null;
  updatedAt?: string | null;
  isNew?: boolean;
}

export interface Prompt {
  id: number;
  title: string;
  documentTypeId: number | null;
  isActive: boolean;
  activeVersion?: PromptVersion | null;
  updatedAt?: string | null;
}

export interface PromptVersionDto {
  id: number;
  prompt_id: number;
  name?: string | null;
  description?: string | null;
  prompt_text?: string | null;
  is_active?: boolean;
  created_at?: string | null;
  updated_at?: string | null;
}

export interface PromptDto {
  id: number;
  title: string;
  document_type_id: number;
  is_active?: boolean;
  active_version?: PromptVersionDto | null;
  updated_at?: string | null;
}

export function toPromptVersion(dto: PromptVersionDto): PromptVersion {
  return {
    id: dto.id,
    promptId: dto.prompt_id,
    name: dto.name ?? null,
    description: dto.description ?? null,
    promptText: dto.prompt_text ?? null,
    isActive: !!dto.is_active,
    createdAt: dto.created_at ?? null,
    updatedAt: dto.updated_at ?? null,
  };
}

export function toPrompt(dto: PromptDto): Prompt {
  return {
    id: dto.id,
    title: dto.title,
    documentTypeId: dto.document_type_id,
    isActive: !!dto.is_active,
    activeVersion: dto.active_version ? toPromptVersion(dto.active_version) : null,
    updatedAt: dto.updated_at ?? null,
  };
}
