export interface ChatSession {
  id: number;
  templateId: number;
  documentTypeId: number;
  createdBy: number;
  title?: string;
  updatedAt?: string;
  isTestSession?: boolean;
  testPromptVersionId?: number | null;
}

export interface SessionSection {
  id: number;
  sessionId: number;
  templateSectionId?: number | null;
  name: string;
  position: number;
}

export interface ModelOutput {
  id: number;
  generatedText?: string | null;
}

export interface SectionInstruction {
  id: number;
  text: string;
  createdAt?: string | null;
}

export interface SectionDraft {
  id: number;
  content?: string | null;
}

export interface SectionIteration {
  id: number;
  seqNo: number;
  sessionSectionId: number;
  sectionInstruction?: SectionInstruction | null;
  modelOutput?: ModelOutput | null;
  sectionDraft?: SectionDraft | null;
}

export interface SessionSectionWithLatestIteration {
  id: number;
  sessionId: number;
  name?: string | null;
  position?: number | null;
  latestIteration?: SectionIteration | null;
  maxSeqNo?: number | null;
}

export interface SessionOverview {
  documentTypeId: number;
  title: string;
  latestGlobalInstructionText: string;
  sections: SessionSectionWithLatestIteration[];
}

export interface ChatSessionDto {
  id: number;
  template_id: number;
  document_type_id?: number | null;
  created_by: number;
  title?: string;
  updated_at?: string;
  is_test_session?: number;
  test_prompt_version_id?: number | null;
}

export interface SessionSectionDto {
  id: number;
  session_id: number;
  template_section_id?: number | null;
  name: string;
  position: number;
}

export interface SectionIterationDto {
  id: number;
  seq_no: number;
  session_section_id: number;
  section_instruction?: { id: number; text_?: string; text?: string; created_at?: string | null } | null;
  model_output?: { id: number; generated_text?: string | null } | null;
  section_draft?: { id: number; content?: string | null } | null;
}

export interface SessionOverviewDto {
  document_type_id: number;
  title: string;
  latest_global_instruction_text?: string | null;
  sections?: {
    id: number;
    session_id: number;
    name?: string | null;
    position?: number | null;
    latest_iteration?: SectionIterationDto | null;
  }[];
}

export function toChatSession(dto: ChatSessionDto): ChatSession {
  return {
    id: dto.id,
    templateId: dto.template_id,
    documentTypeId: dto.document_type_id ?? (null as unknown as number),
    createdBy: dto.created_by,
    title: dto.title,
    updatedAt: dto.updated_at,
    isTestSession: dto.is_test_session === 1,
    testPromptVersionId: dto.test_prompt_version_id ?? null,
  };
}

export function toSessionSection(dto: SessionSectionDto): SessionSection {
  return {
    id: dto.id,
    sessionId: dto.session_id,
    templateSectionId: dto.template_section_id ?? null,
    name: dto.name,
    position: dto.position,
  };
}

export function toSectionIteration(dto: SectionIterationDto): SectionIteration {
  return {
    id: dto.id,
    seqNo: dto.seq_no,
    sessionSectionId: dto.session_section_id,
    sectionInstruction: dto.section_instruction
      ? {
          id: dto.section_instruction.id,
          text: (dto.section_instruction.text_ ?? dto.section_instruction.text) as string,
          createdAt: dto.section_instruction.created_at ?? null,
        }
      : null,
    modelOutput: dto.model_output
      ? { id: dto.model_output.id, generatedText: dto.model_output.generated_text ?? null }
      : null,
    sectionDraft: dto.section_draft
      ? { id: dto.section_draft.id, content: dto.section_draft.content ?? null }
      : null,
  };
}

export function toSessionOverview(dto: SessionOverviewDto): SessionOverview {
  return {
    documentTypeId: dto.document_type_id,
    title: dto.title,
    latestGlobalInstructionText: dto.latest_global_instruction_text ?? '',
    sections: (dto.sections || []).map((section): SessionSectionWithLatestIteration => {
      const latestIteration = section.latest_iteration ? toSectionIteration(section.latest_iteration) : null;
      return {
        id: section.id,
        sessionId: section.session_id,
        name: section.name ?? null,
        position: section.position ?? null,
        latestIteration,
        maxSeqNo: latestIteration?.seqNo ?? 0,
      };
    }),
  };
}
