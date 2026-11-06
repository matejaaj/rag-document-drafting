export interface RepoFolder {
  id: number;
  name: string;
  parentId: number | null;
  createdBy: number | null;
  createdAt: string | null;
}

export interface StorageObject {
  id: number;
  originalName: string;
  mimeType: string | null;
  sizeBytes: number;
  repoFolderId: number | null;
  path: string | null;
  createdBy: number | null;
  createdAt: string | null;
}

export interface RepoFolderDto {
  id: number;
  name: string;
  parent_id?: number | null;
  created_by?: number | null;
  created_at?: string | null;
}

export interface StorageObjectDto {
  id: number;
  original_name: string;
  mime_type?: string | null;
  size_bytes?: number | null;
  repo_folder_id?: number | null;
  path?: string | null;
  created_by?: number | null;
  created_at?: string | null;
}

export function toRepoFolder(dto: RepoFolderDto): RepoFolder {
  return {
    id: dto.id,
    name: dto.name,
    parentId: dto.parent_id ?? null,
    createdBy: dto.created_by ?? null,
    createdAt: dto.created_at ?? null,
  };
}

export function toStorageObject(dto: StorageObjectDto): StorageObject {
  return {
    id: dto.id,
    originalName: dto.original_name,
    mimeType: dto.mime_type ?? null,
    sizeBytes: dto.size_bytes ?? 0,
    repoFolderId: dto.repo_folder_id ?? null,
    path: dto.path ?? null,
    createdBy: dto.created_by ?? null,
    createdAt: dto.created_at ?? null,
  };
}
