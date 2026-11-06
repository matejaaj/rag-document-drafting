export interface OutputFeedback {
  id: number;
  modelOutputId: number;
  ratingValue: number;
  commentText?: string | null;
  createdBy: number;
  createdAt: string;
}

export interface NewOutputFeedback {
  modelOutputId: number;
  ratingValue: number;
  commentText?: string | null;
}

export interface OutputFeedbackDetails {
  finalPrompt?: string | null;
  generatedText?: string | null;
}

export interface OutputFeedbackListItem {
  id: number;
  ratingValue: number | null;
  commentText: string | null;
  createdAt: string | null;
  createdBy: number;
  createdByEmail?: string | null;
  details?: OutputFeedbackDetails | null;
}

export interface OutputFeedbackDto {
  id: number;
  model_output_id: number;
  rating_value: number;
  comment_text?: string | null;
  created_by: number;
  created_at: string;
}

export interface OutputFeedbackListItemDto {
  id: number;
  rating_value: number | null;
  comment_text: string | null;
  created_at: string | null;
  created_by: number;
  created_by_email?: string | null;
  details?: { final_prompt?: string | null; generated_text?: string | null } | null;
}

export function toOutputFeedback(dto: OutputFeedbackDto): OutputFeedback {
  return {
    id: dto.id,
    modelOutputId: dto.model_output_id,
    ratingValue: dto.rating_value,
    commentText: dto.comment_text ?? null,
    createdBy: dto.created_by,
    createdAt: dto.created_at,
  };
}

export function toOutputFeedbackListItem(dto: OutputFeedbackListItemDto): OutputFeedbackListItem {
  return {
    id: dto.id,
    ratingValue: dto.rating_value,
    commentText: dto.comment_text,
    createdAt: dto.created_at,
    createdBy: dto.created_by,
    createdByEmail: dto.created_by_email ?? null,
    details: dto.details
      ? { finalPrompt: dto.details.final_prompt ?? null, generatedText: dto.details.generated_text ?? null }
      : null,
  };
}
