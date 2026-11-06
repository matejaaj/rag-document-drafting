export interface DocumentType {
  id: number;
  name: string;
  description?: string | null;
  deleted: number;
  createdAt?: string | null;
  updatedAt?: string | null;
}

export interface DocumentTypeDto {
  id: number;
  name: string;
  description?: string | null;
  deleted: number;
  created_at?: string | null;
  updated_at?: string | null;
}

export function toDocumentType(dto: DocumentTypeDto): DocumentType {
  return {
    id: dto.id,
    name: dto.name,
    description: dto.description ?? null,
    deleted: dto.deleted,
    createdAt: dto.created_at ?? null,
    updatedAt: dto.updated_at ?? null,
  };
}
