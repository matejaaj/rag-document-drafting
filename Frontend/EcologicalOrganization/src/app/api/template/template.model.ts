export interface Template {
  id: number;
  name: string;
  documentTypeId: number;
  documentTypeName?: string;
  updatedAt?: string;
}

export interface TemplateDto {
  id: number;
  name: string;
  document_type_id: number;
  document_type_name?: string;
  updated_at?: string;
}

export function toTemplate(dto: TemplateDto): Template {
  return {
    id: dto.id,
    name: dto.name,
    documentTypeId: dto.document_type_id,
    updatedAt: dto.updated_at,
    documentTypeName: dto.document_type_name,
  };
}
